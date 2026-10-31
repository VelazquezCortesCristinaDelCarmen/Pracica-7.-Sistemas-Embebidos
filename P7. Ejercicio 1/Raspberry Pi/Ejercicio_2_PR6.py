# Ejercicio_2_PR6
import matplotlib.pyplot as plt
import datetime

LOG_FILE = './temp.log'

def graficar_historico():
    tiempos = []
    temperaturas = []
    
    try:
        # CAMBIO: Leyendo los valores almacenados en la bitácora para graficar [4pt]
        with open(LOG_FILE, 'r') as fp:
            for linea in fp:
                partes = linea.strip().split(',')
                if len(partes) == 2:
                    t = float(partes[0])
                    temp = float(partes[1])
                    # Convertimos el timestamp UNIX a formato legible
                    tiempos.append(datetime.datetime.fromtimestamp(t))
                    temperaturas.append(temp)
        
        # CAMBIO: Configuración de la gráfica del histórico de temperaturas
        plt.figure(figsize=(10, 5))
        plt.plot(tiempos, temperaturas, marker='o', linestyle='-', color='b')
        plt.title('Histórico de Temperaturas')
        plt.xlabel('Tiempo')
        plt.ylabel('Temperatura (°C)')
        plt.grid(True)
        plt.xticks(rotation=45)
        plt.tight_layout()
        
        # Mostrar gráfica en pantalla
        plt.show()
    except Exception as e:
        print("Error al generar la gráfica. Verifica que temp.log exista y tenga datos.", e)

if __name__ == '__main__':
    graficar_historico()