"""Motor de reglas de dominó doble 6 por parejas.

Lógica pura: sin red, sin base de datos, sin interfaz.
Ver REGLAS.md para la especificación que implementa.
"""

from . import bot
from .conteo import (
    ConteoInternacional,
    ConteoLatino,
    ReglaConteo,
    pareja_de,
    regla,
)
from .ficha import VALOR_MAXIMO, Ficha, juego_completo, sumar
from .mano import Evento, FinDeMano, Mano, MovimientoInvalido, ResultadoMano
from .mesa import FichaColocada, JugadaInvalida, Lado, Mesa
from .partida import Partida
from .reparto import (
    FICHAS_POR_JUGADOR,
    JUGADORES,
    repartir,
    siguiente_salida,
    sortear_salida,
)

__version__ = "0.2.0"

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
    "Mano",
    "ResultadoMano",
    "FinDeMano",
    "Evento",
    "MovimientoInvalido",
    "ReglaConteo",
    "ConteoLatino",
    "ConteoInternacional",
    "regla",
    "pareja_de",
    "Partida",
    "bot",
]
