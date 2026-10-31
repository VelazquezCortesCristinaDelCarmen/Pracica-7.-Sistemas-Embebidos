# Ejercicio_3_PR6
from flask import Flask, send_file
import matplotlib
# CAMBIO: Usar backend 'Agg' para generar imágenes en segundo plano sin requerir interfaz gráfica
matplotlib.use('Agg') 
import matplotlib.pyplot as plt
import datetime
import io

app = Flask(__name__)
LOG_FILE = './temp.log'

@app.route('/')
def index():
    # CAMBIO: HTML servido por la página web donde se observa la gráfica [5pt]
    return '''
    <html>
        <head>
            <title>Monitor de Temperatura</title>
            <meta http-equiv="refresh" content="60"> <!-- CAMBIO: Resolución / auto-refresh de 1 minuto -->
        </head>
        <body style="font-family: Arial, sans-serif; text-align: center;">
            <h1>Histórico de Temperaturas (Bitácora)</h1>
            <img src="/grafica" alt="Grafica de Temperaturas" style="max-width: 90%; border: 1px solid #ccc;">
            <br><br>
            <button onclick="location.reload()" style="padding: 10px 20px; font-size: 16px;">Actualizar Manualmente</button>
        </body>
    </html>
    '''

@app.route('/grafica')
def grafica():
    tiempos = []
    temperaturas = []
    
    try:
        # CAMBIO: Extraemos datos de la bitácora
        with open(LOG_FILE, 'r') as fp:
            for linea in fp:
                partes = linea.strip().split(',')
                if len(partes) == 2:
                    t = float(partes[0])
                    temp = float(partes[1])
                    tiempos.append(datetime.datetime.fromtimestamp(t))
                    temperaturas.append(temp)
                    
        # Generar figura
        fig, ax = plt.subplots(figsize=(10, 5))
        ax.plot(tiempos, temperaturas, marker='o', linestyle='-', color='r')
        ax.set_title('Temperatura Registrada')
        ax.set_xlabel('Tiempo')
        ax.set_ylabel('Temperatura (°C)')
        ax.grid(True)
        fig.autofmt_xdate()
        
        # CAMBIO: Guardar la gráfica en un buffer de memoria virtual para servirla HTTP sin escribir en disco duro
        buf = io.BytesIO()
        plt.savefig(buf, format='png')
        buf.seek(0)
        plt.close(fig)
        
        return send_file(buf, mimetype='image/png')
    except Exception as e:
        return f"Error leyendo histórico: {e}"

if __name__ == '__main__':
    # CAMBIO: Arrancar servidor en todas las interfaces de red, puerto 5000.
    # Podrás acceder desde el navegador en: http://<IP_DE_LA_RASPBERRY>:5000
    app.run(host='0.0.0.0', port=5000)