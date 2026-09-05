"""Motor de reglas de dominó doble 6 por parejas.

Lógica pura: sin red, sin base de datos, sin interfaz.
Ver REGLAS.md para la especificación que implementa.
"""

from .ficha import VALOR_MAXIMO, Ficha, juego_completo, sumar
from .mesa import FichaColocada, JugadaInvalida, Lado, Mesa
from .reparto import (
    FICHAS_POR_JUGADOR,
    JUGADORES,
    repartir,
    siguiente_salida,
    sortear_salida,
)

__version__ = "0.1.0"

__all__ = [
    "VALOR_MAXIMO",
    "Ficha",
    "juego_completo",
    "sumar",
    "Mesa",
    "FichaColocada",
    "Lado",
    "JugadaInvalida",
    "repartir",
    "sortear_salida",
    "siguiente_salida",
    "JUGADORES",
    "FICHAS_POR_JUGADOR",
]
