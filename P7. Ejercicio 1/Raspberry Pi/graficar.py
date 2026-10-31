import sys
from datetime import datetime

import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt


LOG_FILE = './temp.log'


def leer_bitacora(path=LOG_FILE):
    tiempos = []
    temps = []

    with open(path) as fp:
        for linea in fp:
            partes = linea.split()

            if len(partes) < 2:
                continue

            try:
                tiempos.append(
                    datetime.fromtimestamp(float(partes[0]))
                )

                temps.append(
                    float(partes[1])
                )

            except ValueError:
                continue

    return tiempos, temps


def main():

    # Nombre del archivo de salida
    salida = (
        sys.argv[1]
        if len(sys.argv) > 1
        else 'temperaturas.png'
    )

    # Leer datos
    tiempos, temps = leer_bitacora()

    if not temps:
        print('La bitácora está vacía')
        return

    # Calcular tiempo transcurrido desde la primera medición
    tiempo_segundos = [
        (t - tiempos[0]).total_seconds()
        for t in tiempos
    ]

    # Estadísticas
    temperatura_min = min(temps)
    temperatura_max = max(temps)
    temperatura_promedio = sum(temps) / len(temps)

    # ---------------------------------------------------------
    # CREAR GRÁFICA
    # ---------------------------------------------------------

    fig, ax = plt.subplots(
        figsize=(14, 7)
    )

    # Línea y puntos de temperatura
    ax.plot(
        tiempo_segundos,
        temps,
        color='#1565C0',
        linewidth=2.2,
        marker='o',
        markersize=7,
        markerfacecolor='#FF6D00',
        markeredgecolor='white',
        markeredgewidth=1.2,
        label='Temperatura'
    )

    # ---------------------------------------------------------
    # TÍTULO
    # ---------------------------------------------------------

    ax.set_title(
        'Monitoreo de temperatura - LM35',
        fontsize=18,
        fontweight='bold',
        pad=18
    )

    # ---------------------------------------------------------
    # ETIQUETAS
    # ---------------------------------------------------------

    ax.set_xlabel(
        'Tiempo transcurrido [s]',
        fontsize=12,
        fontweight='bold'
    )

    ax.set_ylabel(
        'Temperatura [°C]',
        fontsize=12,
        fontweight='bold'
    )

    # ---------------------------------------------------------
    # ESCALA DE TEMPERATURA
    # ---------------------------------------------------------

    # Agregar margen para que los puntos no queden pegados
    # a los límites de la gráfica.

    margen = 2

    limite_inferior = (
        int(temperatura_min - margen)
    )

    limite_superior = (
        int(temperatura_max + margen) + 1
    )

    ax.set_ylim(
        limite_inferior,
        limite_superior
    )

    # Marcas cada 1 °C
    ax.set_yticks(
        range(
            limite_inferior,
            limite_superior + 1,
            1
        )
    )

    # ---------------------------------------------------------
    # CUADRÍCULA
    # ---------------------------------------------------------

    ax.grid(
        True,
        linestyle='--',
        linewidth=0.8,
        alpha=0.35
    )

    # ---------------------------------------------------------
    # ESTADÍSTICAS
    # ---------------------------------------------------------

    texto_estadisticas = (
        f'Mínima:   {temperatura_min:.2f} °C\n'
        f'Máxima:   {temperatura_max:.2f} °C\n'
        f'Promedio: {temperatura_promedio:.2f} °C'
    )

    ax.text(
        0.02,
        0.97,
        texto_estadisticas,
        transform=ax.transAxes,
        verticalalignment='top',
        fontsize=11,
        fontweight='bold',
        bbox=dict(
            boxstyle='round,pad=0.6',
            facecolor='white',
            edgecolor='#1565C0',
            linewidth=1.5,
            alpha=0.95
        )
    )

    # ---------------------------------------------------------
    # EJE X
    # ---------------------------------------------------------

    duracion = tiempo_segundos[-1]

    if duracion <= 60:
        intervalo = 5

    elif duracion <= 300:
        intervalo = 30

    elif duracion <= 1800:
        intervalo = 60

    else:
        intervalo = 300

    marcas_x = list(
        range(
            0,
            int(duracion) + intervalo,
            intervalo
        )
    )

    ax.set_xticks(marcas_x)

    ax.set_xticklabels(
        [
            f'{x}s'
            for x in marcas_x
        ],
        fontsize=10
    )

    # ---------------------------------------------------------
    # APARIENCIA DE LOS EJES
    # ---------------------------------------------------------

    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)

    # ---------------------------------------------------------
    # LEYENDA
    # ---------------------------------------------------------

    ax.legend(
        loc='upper right',
        fontsize=10
    )

    # ---------------------------------------------------------
    # AJUSTAR Y GUARDAR
    # ---------------------------------------------------------

    fig.tight_layout()

    fig.savefig(
        salida,
        dpi=180,
        bbox_inches='tight'
    )

    plt.close(fig)

    print(
        'Gráfica guardada en',
        salida
    )


if __name__ == '__main__':
    main()