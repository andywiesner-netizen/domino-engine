"""La partida: sucesión de manos hasta alcanzar el puntaje meta (REGLAS.md §7)."""

from __future__ import annotations

import random
from dataclasses import dataclass, field

from .conteo import ReglaConteo, regla
from .mano import Mano, ResultadoMano
from .reparto import repartir, siguiente_salida, sortear_salida

PUNTOS_META_POR_DEFECTO = 100


@dataclass
class Partida:
    """Marcador y rotación de salida entre manos.

    No juega: crea manos y registra sus resultados. Quién juega cada
    mano —personas, bots, o una mezcla— es problema de quien lo use.
    """

    puntos_meta: int = PUNTOS_META_POR_DEFECTO
    modo_conteo: str = "latino"
    marcador: list[int] = field(default_factory=lambda: [0, 0])
    salida: int | None = None
    manos_jugadas: int = 0
    historial: list[ResultadoMano] = field(default_factory=list)

    def __post_init__(self) -> None:
        if self.puntos_meta <= 0:
            raise ValueError("puntos_meta debe ser positivo")
        self._conteo: ReglaConteo = regla(self.modo_conteo)

    @property
    def conteo(self) -> ReglaConteo:
        return self._conteo

    @property
    def terminada(self) -> bool:
        return max(self.marcador) >= self.puntos_meta

    @property
    def ganadora(self) -> int | None:
        """Pareja que ganó la partida, o None si sigue en curso."""
        if not self.terminada:
            return None
        return 0 if self.marcador[0] >= self.puntos_meta else 1

    def nueva_mano(self, rng: random.Random | None = None) -> Mano:
        """Reparte y devuelve la mano siguiente.

        La primera se sortea al azar; las demás rotan a la derecha desde
        quien salió antes, sin importar quién ganó (REGLAS.md §3).
        """
        if self.terminada:
            raise RuntimeError("La partida ya terminó")
        rng = rng or random.Random()
        self.salida = (
            sortear_salida(rng) if self.salida is None
            else siguiente_salida(self.salida)
        )
        return Mano(manos=repartir(rng), turno=self.salida, conteo=self._conteo)

    def registrar(self, resultado: ResultadoMano) -> None:
        """Anota el resultado de una mano en el marcador."""
        if resultado.pareja_ganadora is not None:
            self.marcador[resultado.pareja_ganadora] += resultado.puntos
        self.historial.append(resultado)
        self.manos_jugadas += 1
