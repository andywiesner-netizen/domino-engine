"""Jugador automático (REGLAS.md §8).

Criterio versión 1: la ficha válida de mayor valor. Deliberadamente
simple y predecible, para que ningún jugador sienta que la máquina
decidió la partida por él.

Cualquier mejora futura debe entrar detrás de esta misma firma.
"""

from __future__ import annotations

from .ficha import Ficha
from .mesa import Lado, Mesa


def escoger(mesa: Mesa, mano: list[Ficha]) -> tuple[Ficha, Lado] | None:
    """Jugada que haría el bot, o None si debe pasar.

    El desempate es determinista y no depende del orden en que estén las
    fichas en la mano: primero mayor valor, luego orden canónico de la
    ficha, luego izquierda antes que derecha. Así una misma situación
    produce siempre la misma jugada, que es lo que hace reproducible un
    bug reportado.
    """
    jugadas = mesa.jugadas_posibles(mano)
    if not jugadas:
        return None
    return min(
        jugadas,
        key=lambda j: (-j[0].valor, j[0], j[1] is Lado.DERECHA),
    )
