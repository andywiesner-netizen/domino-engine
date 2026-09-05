"""Demostración: juega una partida completa en la terminal.

Ya no implementa reglas: todo sale del motor. Sirve para ver el juego
funcionando y como ejemplo de cómo se usa la API desde el servidor.

Uso:  python ejemplo_mano.py [semilla] [latino|internacional] [puntos]
"""

import random
import sys

from domino_engine import FinDeMano, Partida, bot

PAREJA = "ABAB"


def jugar_mano(mano, verboso=True):
    """Juega una mano completa con bots y devuelve el resultado."""
    while not mano.terminada:
        turno = mano.turno
        jugada = bot.escoger(mano.mesa, mano.manos[turno])
        if jugada is None:
            resultado = mano.pasar()
            if verboso:
                print(f"    jugador {turno} pasa")
        else:
            resultado = mano.jugar(*jugada)
            if verboso:
                ficha, lado = jugada
                print(f"    jugador {turno} juega {ficha} por la {lado.value}")
                print(f"        {mano.mesa}")
    return resultado


def main(semilla, modo, meta):
    rng = random.Random(semilla)
    partida = Partida(puntos_meta=meta, modo_conteo=modo)

    print(f"semilla {semilla} - modo {modo} - a {meta} puntos\n")

    while not partida.terminada:
        mano = partida.nueva_mano(rng)
        print(f"  mano {partida.manos_jugadas + 1} - sale el jugador {mano.turno}")
        resultado = jugar_mano(mano)
        partida.registrar(resultado)

        a, b = resultado.puntos_por_pareja
        if resultado.tipo is FinDeMano.EMPATE:
            print(f"    TRANCA EMPATADA ({a} y {b}) - nadie anota")
        elif resultado.tipo is FinDeMano.TRANCA:
            gana = PAREJA[resultado.pareja_ganadora]
            print(f"    TRANCA (A:{a} B:{b}) - pareja {gana} anota {resultado.puntos}")
        else:
            gana = PAREJA[resultado.pareja_ganadora]
            print(
                f"    DOMINO del jugador {resultado.jugador_que_cerro} - "
                f"pareja {gana} anota {resultado.puntos}"
            )
        print(f"    marcador  A:{partida.marcador[0]}  B:{partida.marcador[1]}\n")

    print(f"*** GANA LA PAREJA {PAREJA[partida.ganadora]} "
          f"en {partida.manos_jugadas} manos ***")


if __name__ == "__main__":
    args = sys.argv[1:]
    main(
        int(args[0]) if len(args) > 0 else random.randrange(10000),
        args[1] if len(args) > 1 else "latino",
        int(args[2]) if len(args) > 2 else 100,
    )
