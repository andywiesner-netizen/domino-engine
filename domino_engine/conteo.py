"""Reglas de conteo de puntos (REGLAS.md §6).

La diferencia entre latino e internacional está únicamente en QUÉ fichas
se cuentan. En ambos modos los puntos van íntegros a la pareja ganadora.

Se aísla aquí para que agregar un modo nuevo no obligue a tocar la
lógica de juego.
"""

from __future__ import annotations

from typing import Protocol, runtime_checkable

from .ficha import Ficha, sumar

PAREJAS = 2


def pareja_de(jugador: int) -> int:
    """Pareja a la que pertenece un jugador.

    Las posiciones 0 y 2 son la pareja 0; las posiciones 1 y 3, la pareja 1.
    Los compañeros quedan enfrentados y el turno alterna entre parejas.
    """
    return jugador % PAREJAS


@runtime_checkable
class ReglaConteo(Protocol):
    nombre: str

    def puntos(
        self, manos: list[list[Ficha]], pareja_ganadora: int
    ) -> int:
        """Puntos que anota la pareja ganadora al cerrarse la mano.

        `manos` son las fichas que quedaron sin jugar, indexadas por
        posición del jugador (0 a 3).
        """
        ...


class ConteoLatino:
    """Solo cuentan las fichas de la pareja rival."""

    nombre = "latino"

    def puntos(self, manos: list[list[Ficha]], pareja_ganadora: int) -> int:
        return sum(
            sumar(mano)
            for jugador, mano in enumerate(manos)
            if pareja_de(jugador) != pareja_ganadora
        )


class ConteoInternacional:
    """Cuentan todas las fichas no jugadas, incluidas las de la propia pareja.

    En dominó limpio el que cerró tiene cero fichas, así que en la
    práctica se suman las del compañero y las de los dos rivales. En
    tranca se suman las cuatro manos.
    """

    nombre = "internacional"

    def puntos(self, manos: list[list[Ficha]], pareja_ganadora: int) -> int:
        return sum(sumar(mano) for mano in manos)


REGLAS: dict[str, type] = {
    "latino": ConteoLatino,
    "internacional": ConteoInternacional,
}


def regla(nombre: str) -> ReglaConteo:
    """Devuelve la regla de conteo por nombre."""
    try:
        return REGLAS[nombre]()
    except KeyError:
        raise ValueError(
            f"Modo de conteo desconocido: {nombre!r}. "
            f"Opciones: {', '.join(REGLAS)}"
        ) from None
