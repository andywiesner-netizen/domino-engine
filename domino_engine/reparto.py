"""Reparto de fichas y sorteo de salida."""

from __future__ import annotations

import random

from .ficha import Ficha, juego_completo

JUGADORES = 4
FICHAS_POR_JUGADOR = 7


def repartir(rng: random.Random | None = None) -> list[list[Ficha]]:
    """Baraja las 28 fichas y reparte 7 a cada uno de los 4 jugadores.

    No queda pozo: todas las fichas se reparten.

    El generador se recibe por parámetro para que los tests puedan fijar
    una semilla y reproducir manos exactas. El servidor debe pasar un
    random.SystemRandom().
    """
    rng = rng or random.Random()
    fichas = juego_completo()
    rng.shuffle(fichas)
    return [
        fichas[i * FICHAS_POR_JUGADOR : (i + 1) * FICHAS_POR_JUGADOR]
        for i in range(JUGADORES)
    ]


def sortear_salida(rng: random.Random | None = None) -> int:
    """Escoge al azar quién sale en la primera mano de la partida.

    Sorteo puro entre los cuatro: no interviene el doble 6 ni ningún
    otro criterio (REGLAS.md §3).
    """
    rng = rng or random.Random()
    return rng.randrange(JUGADORES)


def siguiente_salida(salida_anterior: int) -> int:
    """Quién sale en la mano siguiente.

    Rota a la derecha desde quien salió antes, sin importar quién ganó
    la mano (REGLAS.md §3).
    """
    return (salida_anterior + 1) % JUGADORES
