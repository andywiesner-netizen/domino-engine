"""Demostración: juega una mano completa en la terminal.

NO es parte del paquete. La lógica de turnos, tranca y conteo vive aquí
provisionalmente solo para probar que las piezas de la rebanada 1
encajan. En la rebanada 2 se muda a domino_engine/mano.py con tests.

Uso:  python ejemplo_mano.py [semilla]
"""

import random
import sys

from domino_engine import Mesa, repartir, sortear_salida, sumar

PAREJA = {0: "A", 1: "B", 2: "A", 3: "B"}


def bot_escoge(mesa, mano):
    """Ficha válida de mayor valor (REGLAS.md §8)."""
    jugadas = mesa.jugadas_posibles(mano)
    if not jugadas:
        return None
    return max(jugadas, key=lambda j: j[0].valor)


def main(semilla):
    rng = random.Random(semilla)
    manos = repartir(rng)
    turno = sortear_salida(rng)
    mesa = Mesa()

    print(f"semilla {semilla} — sale el jugador {turno} (pareja {PAREJA[turno]})\n")
    for i, m in enumerate(manos):
        print(f"  jugador {i} ({PAREJA[i]}): {' '.join(str(f) for f in m)}")
    print()

    pasos_seguidos = 0
    while True:
        jugada = bot_escoge(mesa, manos[turno])

        if jugada is None:
            pasos_seguidos += 1
            print(f"  jugador {turno} PASA")
            if pasos_seguidos == 4:
                print("\n*** TRANCA ***")
                break
        else:
            pasos_seguidos = 0
            ficha, lado = jugada
            manos[turno].remove(ficha)
            mesa.colocar(ficha, lado)
            print(f"  jugador {turno} juega {ficha} por la {lado.value}")
            print(f"      mesa: {mesa}")
            if not manos[turno]:
                print(f"\n*** DOMINÓ LIMPIO — jugador {turno} (pareja {PAREJA[turno]}) ***")
                break

        turno = (turno + 1) % 4

    a = sumar(manos[0]) + sumar(manos[2])
    b = sumar(manos[1]) + sumar(manos[3])
    print(f"\nfichas en mano — pareja A: {a}   pareja B: {b}")
    print(f"jugadas en mesa: {len(mesa.cadena)} de 28")


if __name__ == "__main__":
    main(int(sys.argv[1]) if len(sys.argv) > 1 else random.randrange(10000))
