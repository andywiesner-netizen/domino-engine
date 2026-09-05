"""La mesa: la cadena de fichas jugadas y sus extremos libres."""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum

from .ficha import Ficha


class Lado(str, Enum):
    IZQUIERDA = "izquierda"
    DERECHA = "derecha"


class JugadaInvalida(Exception):
    """Se intentó colocar una ficha que no encaja en el lado pedido."""


@dataclass(frozen=True)
class FichaColocada:
    """Una ficha ya en la mesa, con su orientación.

    `izq` y `der` son los valores tal como quedan de izquierda a derecha.
    El frontend necesita esta orientación para dibujar la cadena, así que
    se guarda aquí en vez de recalcularse.
    """

    ficha: Ficha
    izq: int
    der: int


@dataclass
class Mesa:
    cadena: list[FichaColocada] = field(default_factory=list)

    @property
    def vacia(self) -> bool:
        return not self.cadena

    @property
    def izquierda(self) -> int | None:
        """Extremo libre del lado izquierdo."""
        return None if self.vacia else self.cadena[0].izq

    @property
    def derecha(self) -> int | None:
        """Extremo libre del lado derecho."""
        return None if self.vacia else self.cadena[-1].der

    @property
    def extremos(self) -> tuple[int, int] | None:
        if self.vacia:
            return None
        return (self.izquierda, self.derecha)

    @property
    def fichas_jugadas(self) -> list[Ficha]:
        return [fc.ficha for fc in self.cadena]

    def lados_validos(self, ficha: Ficha) -> frozenset[Lado]:
        """Lados donde esta ficha puede colocarse.

        Vacío si no es jugable. En mesa vacía cualquier ficha vale por
        ambos lados: la primera jugada no tiene restricción.
        """
        if self.vacia:
            return frozenset({Lado.IZQUIERDA, Lado.DERECHA})
        lados = set()
        if ficha.tiene(self.izquierda):
            lados.add(Lado.IZQUIERDA)
        if ficha.tiene(self.derecha):
            lados.add(Lado.DERECHA)
        return frozenset(lados)

    def es_jugable(self, ficha: Ficha) -> bool:
        return bool(self.lados_validos(ficha))

    def jugadas_posibles(self, mano: list[Ficha]) -> list[tuple[Ficha, Lado]]:
        """Todas las jugadas legales de una mano, en orden canónico.

        Una misma ficha puede aparecer dos veces si encaja por ambos lados:
        son jugadas distintas y el jugador debe escoger.
        """
        return [
            (ficha, lado)
            for ficha in mano
            for lado in (Lado.IZQUIERDA, Lado.DERECHA)
            if lado in self.lados_validos(ficha)
        ]

    def colocar(self, ficha: Ficha, lado: Lado = Lado.DERECHA) -> FichaColocada:
        """Coloca una ficha y devuelve cómo quedó orientada.

        En mesa vacía el lado se ignora. Muta la mesa.
        """
        if self.vacia:
            colocada = FichaColocada(ficha, ficha.mayor, ficha.menor)
            self.cadena.append(colocada)
            return colocada

        if lado not in self.lados_validos(ficha):
            raise JugadaInvalida(
                f"{ficha} no encaja por la {lado.value} "
                f"(extremos: {self.izquierda} y {self.derecha})"
            )

        if lado is Lado.IZQUIERDA:
            punto = self.izquierda
            colocada = FichaColocada(ficha, ficha.otro_extremo(punto), punto)
            self.cadena.insert(0, colocada)
        else:
            punto = self.derecha
            colocada = FichaColocada(ficha, punto, ficha.otro_extremo(punto))
            self.cadena.append(colocada)
        return colocada

    def __str__(self) -> str:
        if self.vacia:
            return "[mesa vacía]"
        return " ".join(f"[{fc.izq}|{fc.der}]" for fc in self.cadena)
