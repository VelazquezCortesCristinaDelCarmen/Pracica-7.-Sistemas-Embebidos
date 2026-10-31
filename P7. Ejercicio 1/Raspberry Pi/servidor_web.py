import os,time,json,queue,threading
from datetime import datetime
from flask import Flask,Response,jsonify

LOG_FILE='./temp.log'
INTERVALO_LECTURA=.2
VENTANA_EN_VIVO=60

app=Flask(__name__)
datos=[]
clientes=[]
lock=threading.Lock()


def procesar_linea(linea):
    partes=linea.split()
    if len(partes)<2:return None
    try:
        timestamp=float(partes[0])
        temperatura=float(partes[1])
        return {'timestamp':timestamp,
                'fecha':datetime.fromtimestamp(timestamp).isoformat(),
                'temp_c':round(temperatura,2)}
    except (ValueError,OSError,OverflowError):
        return None


def cargar_datos_iniciales():
    global datos
    if not os.path.exists(LOG_FILE):
        with lock:datos=[]
        return 0,None

    nuevos=[]
    try:
        with open(LOG_FILE) as archivo:
            for linea in archivo:
                dato=procesar_linea(linea)
                if dato:nuevos.append(dato)
            posicion=archivo.tell()

        archivo_id=os.stat(LOG_FILE).st_ino
        with lock:datos=nuevos
        return posicion,archivo_id
    except OSError:
        with lock:datos=[]
        return 0,None


def enviar_a_clientes(dato):
    mensaje=f"data: {json.dumps(dato)}\n\n"
    eliminar=[]

    with lock:
        for cliente in clientes:
            try:cliente.put_nowait(mensaje)
            except queue.Full:eliminar.append(cliente)
        for cliente in eliminar:
            if cliente in clientes:clientes.remove(cliente)


def lector_temperatura(posicion_inicial=0,archivo_id_inicial=None):
    posicion=posicion_inicial
    archivo_id=archivo_id_inicial

    while True:
        try:
            if not os.path.exists(LOG_FILE):
                posicion=0
                archivo_id=None
                time.sleep(INTERVALO_LECTURA)
                continue

            nuevo_id=os.stat(LOG_FILE).st_ino
            if archivo_id!=nuevo_id:
                archivo_id=nuevo_id
                posicion=0

            if os.path.getsize(LOG_FILE)<posicion:
                posicion=0

            with open(LOG_FILE) as archivo:
                archivo.seek(posicion)

                while True:
                    linea=archivo.readline()
                    if not linea:break

                    posicion=archivo.tell()
                    dato=procesar_linea(linea)
                    if not dato:continue

                    with lock:
                        if datos:
                            ultimo=datos[-1]
                            if (ultimo['timestamp']==dato['timestamp'] and
                                ultimo['temp_c']==dato['temp_c']):
                                continue
                        datos.append(dato)

                    enviar_a_clientes(dato)

        except (OSError,ValueError):
            pass

        time.sleep(INTERVALO_LECTURA)


@app.route('/')
def inicio():
    return '''
<!DOCTYPE html>
<html lang="es">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width,initial-scale=1.0">
<title>Monitoreo de temperatura - LM35</title>
<style>
*{box-sizing:border-box}
body{margin:0;padding:30px;font-family:Arial;background:#f3f4f6;color:#222}
.contenedor{max-width:1400px;margin:auto;background:#fff;padding:25px;border-radius:12px;box-shadow:0 4px 18px rgba(0,0,0,.1)}
h1{text-align:center;margin:0 0 20px;font-size:28px}
.controles{display:flex;flex-wrap:wrap;align-items:center;gap:12px;margin-bottom:20px}
.controles label{font-weight:bold}
select{padding:9px 12px;border:1px solid #ccc;border-radius:6px;background:#fff;font-size:14px}
.estado{margin-left:auto;font-size:14px;font-weight:bold}
.conectado{color:#2e7d32}.desconectado{color:#c62828}
.grafica-contenedor{width:100%;height:600px;border:1px solid #ddd;border-radius:8px;background:#fff;overflow:hidden}
#grafica{width:100%;height:100%;display:block}
.informacion{display:flex;flex-wrap:wrap;gap:30px;margin-top:20px;padding:15px;background:#f8f9fa;border-radius:8px}
.dato{font-size:16px}.dato strong{color:#1565C0}
.enlace{margin-top:15px;text-align:right}.enlace a{color:#1565C0;text-decoration:none;font-weight:bold}
@media(max-width:700px){body{padding:10px}.contenedor{padding:15px}.grafica-contenedor{height:450px}.estado{margin-left:0;width:100%}}
</style>
</head>
<body>
<div class="contenedor">
<h1>Monitoreo de temperatura - LM35</h1>

<div class="controles">
<label for="periodo">Vista:</label>
<select id="periodo">
<option value="live" selected>En vivo - últimos 60 segundos</option>
<option value="all">Todo</option>
</select>
<div id="estado" class="estado desconectado">● Desconectado</div>
</div>

<div class="grafica-contenedor"><canvas id="grafica"></canvas></div>

<div class="informacion">
<div class="dato"><strong>Última temperatura:</strong>
<span id="ultimaTemperatura">--</span> °C</div>
<div class="dato"><strong>Fecha:</strong>
<span id="ultimaFecha">--</span></div>
<div class="dato"><strong>Mediciones:</strong>
<span id="numeroDatos">0</span></div>
</div>

<div class="enlace">
<a href="/datos.json" target="_blank">Ver datos JSON</a>
</div>
</div>

<script>
const canvas=document.getElementById('grafica'),
ctx=canvas.getContext('2d'),
periodo=document.getElementById('periodo'),
estado=document.getElementById('estado'),
ultimaTemperatura=document.getElementById('ultimaTemperatura'),
ultimaFecha=document.getElementById('ultimaFecha'),
numeroDatos=document.getElementById('numeroDatos');

const VENTANA_EN_VIVO=60;
let datos=[],vistaInicio=null,vistaObjetivo=null,animacionActiva=false;


function ajustarCanvas(){
    const r=canvas.getBoundingClientRect(),d=window.devicePixelRatio||1;
    canvas.width=r.width*d;
    canvas.height=r.height*d;
    ctx.setTransform(d,0,0,d,0,0);
    dibujarGrafica();
}


function actualizarInformacion(){
    numeroDatos.textContent=datos.length;

    if(!datos.length){
        ultimaTemperatura.textContent='--';
        ultimaFecha.textContent='--';
        return;
    }

    const u=datos[datos.length-1];
    ultimaTemperatura.textContent=Number(u.temp_c).toFixed(2);
    ultimaFecha.textContent=new Date(u.timestamp*1000).toLocaleString('es-MX');
}


function agregarDato(dato){
    dato.timestamp=Number(dato.timestamp);
    dato.temp_c=Number(dato.temp_c);

    if(!Number.isFinite(dato.timestamp)||!Number.isFinite(dato.temp_c))
        return;

    const u=datos.length?datos[datos.length-1]:null;

    if(u&&u.timestamp===dato.timestamp&&u.temp_c===dato.temp_c)
        return;

    datos.push(dato);
    datos.sort((a,b)=>a.timestamp-b.timestamp);
}


function prepararVista(){
    if(!datos.length){
        vistaInicio=vistaObjetivo=null;
        return;
    }

    const ultimo=datos[datos.length-1].timestamp;

    if(periodo.value==='live'){
        vistaInicio=ultimo-VENTANA_EN_VIVO;
    }else{
        vistaInicio=datos[0].timestamp;
    }

    vistaObjetivo=vistaInicio;
    dibujarGrafica();
}


function actualizarVentana(){
    if(!datos.length||periodo.value!=='live')return;

    const ultimo=datos[datos.length-1].timestamp;
    vistaObjetivo=ultimo-VENTANA_EN_VIVO;

    if(vistaInicio===null){
        vistaInicio=vistaObjetivo;
        dibujarGrafica();
        return;
    }

    iniciarAnimacion();
}


function animarVista(){
    if(vistaInicio===null||vistaObjetivo===null){
        animacionActiva=false;
        return;
    }

    const diferencia=vistaObjetivo-vistaInicio;

    if(Math.abs(diferencia)<.03){
        vistaInicio=vistaObjetivo;
        animacionActiva=false;
        dibujarGrafica();
        return;
    }

    vistaInicio+=diferencia*.15;
    dibujarGrafica();
    requestAnimationFrame(animarVista);
}


function iniciarAnimacion(){
    if(animacionActiva||vistaInicio===null||vistaObjetivo===null)return;
    animacionActiva=true;
    requestAnimationFrame(animarVista);
}


function dibujarGrafica(){
    const ancho=canvas.clientWidth,alto=canvas.clientHeight;

    if(ancho<=0||alto<=0)return;

    ctx.clearRect(0,0,ancho,alto);

    if(!datos.length){
        ctx.fillStyle='#555';
        ctx.font='16px Arial';
        ctx.textAlign='center';
        ctx.fillText('Esperando mediciones...',ancho/2,alto/2);
        return;
    }

    const x0=80,y0=65,x1=ancho-35,y1=alto-70,
          graficaAncho=x1-x0,graficaAlto=y1-y0;

    const ultimo=datos[datos.length-1].timestamp;
    let inicioTiempo,finTiempo;

    if(periodo.value==='live'){
        inicioTiempo= vistaInicio!==null?vistaInicio:ultimo-VENTANA_EN_VIVO;
        finTiempo=inicioTiempo+VENTANA_EN_VIVO;
    }else{
        inicioTiempo=datos[0].timestamp;
        finTiempo=ultimo;
        if(finTiempo<=inicioTiempo)finTiempo=inicioTiempo+1;
    }

    const rangoTiempo=finTiempo-inicioTiempo;
    const visibles=datos.filter(d=>d.timestamp>=inicioTiempo&&d.timestamp<=finTiempo);
    const temperaturas=(visibles.length?visibles:datos).map(d=>d.temp_c);

    let min=Math.min(...temperaturas),max=Math.max(...temperaturas);

    if(min===max){min--;max++;}

    const limiteMin=Math.floor(min-2),
          limiteMax=Math.ceil(max+2),
          rangoTemp=Math.max(limiteMax-limiteMin,1);

    const X=t=>x0+((t-inicioTiempo)/rangoTiempo)*graficaAncho;
    const Y=t=>y1-((t-limiteMin)/rangoTemp)*graficaAlto;

    ctx.fillStyle='#fff';
    ctx.fillRect(0,0,ancho,alto);

    ctx.fillStyle='#222';
    ctx.font='bold 18px Arial';
    ctx.textAlign='center';
    ctx.fillText('Monitoreo de temperatura - LM35',ancho/2,30);


    // Cuadrícula horizontal
    ctx.save();
    ctx.strokeStyle='rgba(0,0,0,.18)';
    ctx.lineWidth=.8;
    ctx.setLineDash([5,5]);

    for(let t=limiteMin;t<=limiteMax;t++){
        const y=Y(t);
        ctx.beginPath();
        ctx.moveTo(x0,y);
        ctx.lineTo(x1,y);
        ctx.stroke();
    }

    ctx.restore();


    // Intervalo del eje X
    let intervaloX;

    if(periodo.value==='live')intervaloX=10;
    else if(rangoTiempo<=60)intervaloX=5;
    else if(rangoTiempo<=300)intervaloX=30;
    else if(rangoTiempo<=1800)intervaloX=60;
    else intervaloX=300;

    const primerTick=Math.ceil(inicioTiempo/intervaloX)*intervaloX;


    // Cuadrícula vertical
    ctx.save();
    ctx.strokeStyle='rgba(0,0,0,.14)';
    ctx.lineWidth=.8;
    ctx.setLineDash([5,5]);

    for(let t=primerTick;t<=finTiempo;t+=intervaloX){
        const x=X(t);
        ctx.beginPath();
        ctx.moveTo(x,y0);
        ctx.lineTo(x,y1);
        ctx.stroke();
    }

    ctx.restore();


    // Ejes
    ctx.strokeStyle='#333';
    ctx.lineWidth=1.2;
    ctx.setLineDash([]);
    ctx.beginPath();
    ctx.moveTo(x0,y0);
    ctx.lineTo(x0,y1);
    ctx.lineTo(x1,y1);
    ctx.stroke();


    // Eje Y
    ctx.fillStyle='#333';
    ctx.font='12px Arial';
    ctx.textAlign='right';

    for(let t=limiteMin;t<=limiteMax;t++)
        ctx.fillText(t,x0-10,Y(t)+4);


    // Eje X
    ctx.textAlign='center';
    ctx.font='11px Arial';

    for(let t=primerTick;t<=finTiempo;t+=intervaloX){
        const texto=periodo.value==='live'
            ?Math.round(t-inicioTiempo)+' s'
            :new Date(t*1000).toLocaleTimeString(
                'es-MX',{hour:'2-digit',minute:'2-digit'}
            );

        ctx.fillText(texto,X(t),y1+22);
    }


    ctx.font='bold 12px Arial';
    ctx.fillText(
        periodo.value==='live'?'Tiempo transcurrido [s]':'Tiempo',
        (x0+x1)/2,alto-18
    );


    // Etiqueta Y
    ctx.save();
    ctx.translate(20,(y0+y1)/2);
    ctx.rotate(-Math.PI/2);
    ctx.fillText('Temperatura [°C]',0,0);
    ctx.restore();


    // Línea
    if(visibles.length){
        ctx.strokeStyle='#1565C0';
        ctx.lineWidth=2.2;
        ctx.beginPath();

        visibles.forEach((d,i)=>{
            const x=X(d.timestamp),y=Y(d.temp_c);
            i?ctx.lineTo(x,y):ctx.moveTo(x,y);
        });

        ctx.stroke();


        // Puntos
        visibles.forEach(d=>{
            const x=X(d.timestamp),y=Y(d.temp_c);

            ctx.beginPath();
            ctx.arc(x,y,7,0,Math.PI*2);
            ctx.fillStyle='#fff';
            ctx.fill();

            ctx.beginPath();
            ctx.arc(x,y,5,0,Math.PI*2);
            ctx.fillStyle='#FF6D00';
            ctx.fill();
        });
    }


    // Estadísticas
    if(visibles.length){
        const valores=visibles.map(d=>d.temp_c);
        const minima=Math.min(...valores);
        const maxima=Math.max(...valores);
        const promedio=valores.reduce((a,b)=>a+b,0)/valores.length;

        const cajaX=x1-180,cajaY=y0+10;

        ctx.fillStyle='rgba(255,255,255,.90)';
        ctx.fillRect(cajaX,cajaY,170,78);

        ctx.strokeStyle='#ccc';
        ctx.lineWidth=1;
        ctx.strokeRect(cajaX,cajaY,170,78);

        ctx.fillStyle='#222';
        ctx.font='12px Arial';
        ctx.textAlign='left';

        ctx.fillText('Mínima: '+minima.toFixed(2)+' °C',cajaX+10,cajaY+20);
        ctx.fillText('Máxima: '+maxima.toFixed(2)+' °C',cajaX+10,cajaY+40);
        ctx.fillText('Promedio: '+promedio.toFixed(2)+' °C',cajaX+10,cajaY+60);
    }


    // Leyenda
    ctx.beginPath();
    ctx.strokeStyle='#1565C0';
    ctx.lineWidth=2.2;
    ctx.moveTo(x1-135,alto-22);
    ctx.lineTo(x1-105,alto-22);
    ctx.stroke();

    ctx.beginPath();
    ctx.arc(x1-120,alto-22,5,0,Math.PI*2);
    ctx.fillStyle='#FF6D00';
    ctx.fill();

    ctx.fillStyle='#333';
    ctx.font='12px Arial';
    ctx.textAlign='left';
    ctx.fillText('Temperatura',x1-98,alto-18);
}


async function cargarDatosIniciales(){
    try{
        const respuesta=await fetch('/datos.json',{cache:'no-store'});
        if(!respuesta.ok)throw new Error('No se pudieron cargar los datos');

        datos=(await respuesta.json())
            .map(d=>({
                timestamp:Number(d.timestamp),
                temp_c:Number(d.temp_c),
                fecha:d.fecha
            }))
            .filter(d=>Number.isFinite(d.timestamp)&&Number.isFinite(d.temp_c))
            .sort((a,b)=>a.timestamp-b.timestamp);

        actualizarInformacion();
        prepararVista();
        dibujarGrafica();
    }catch(error){
        console.error('Error al cargar datos:',error);
    }
}


function conectarSSE(){
    const eventos=new EventSource('/stream');

    eventos.onopen=()=>{
        estado.textContent='● Conectado en tiempo real';
        estado.className='estado conectado';
    };

    eventos.onmessage=evento=>{
        try{
            agregarDato(JSON.parse(evento.data));
            actualizarInformacion();
            if(periodo.value==='live')actualizarVentana();
            dibujarGrafica();
        }catch(error){
            console.error('Error al procesar SSE:',error);
        }
    };

    eventos.onerror=()=>{
        estado.textContent='● Reconectando...';
        estado.className='estado desconectado';
    };
}


periodo.addEventListener('change',()=>{
    animacionActiva=false;
    vistaInicio=null;
    vistaObjetivo=null;
    prepararVista();
    dibujarGrafica();
});

window.addEventListener('resize',ajustarCanvas);
cargarDatosIniciales();
conectarSSE();
ajustarCanvas();
</script>
</body>
</html>
'''


@app.route('/datos.json')
def datos_json():
    with lock:
        datos_copia=list(datos)
    return jsonify(datos_copia)


@app.route('/stream')
def stream():
    def generar():
        cola=queue.Queue(maxsize=100)

        with lock:
            clientes.append(cola)

        try:
            while True:
                try:
                    yield cola.get(timeout=15)
                except queue.Empty:
                    yield ': ping\n\n'
        finally:
            with lock:
                if cola in clientes:
                    clientes.remove(cola)

    return Response(
        generar(),
        mimetype='text/event-stream',
        headers={
            'Cache-Control':'no-cache',
            'Connection':'keep-alive',
            'X-Accel-Buffering':'no'
        }
    )


posicion_inicial,archivo_id_inicial=cargar_datos_iniciales()

hilo_lector=threading.Thread(
    target=lector_temperatura,
    args=(posicion_inicial,archivo_id_inicial),
    daemon=True
)

hilo_lector.start()

if __name__=='__main__':
    app.run(host='0.0.0.0',port=5000,threaded=True)
