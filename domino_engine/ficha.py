"""Fichas de dominó doble 6."""

from __future__ import annotations

from dataclasses import dataclass

VALOR_MAXIMO = 6


@dataclass(frozen=True, order=True)
class Ficha:
    """Una ficha de dominó.

    Se normaliza siempre a (mayor, menor), de modo que Ficha(4, 6) y
    Ficha(6, 4) son la misma ficha y comparan iguales. Es inmutable y
    hashable: se puede usar en conjuntos y como clave de diccionario.
    """

    mayor: int
    menor: int

    def __post_init__(self) -> None:
        a, b = self.mayor, self.menor
        for v in (a, b):
            if not isinstance(v, int) or not 0 <= v <= VALOR_MAXIMO:
                raise ValueError(f"Extremo inválido: {v!r}")
        if a < b:
            object.__setattr__(self, "mayor", b)
            object.__setattr__(self, "menor", a)

    @property
    def valor(self) -> int:
        """Suma de los dos extremos. Es lo que se anota al contar puntos."""
        return self.mayor + self.menor

    @property
    def es_doble(self) -> bool:
        return self.mayor == self.menor

    @property
    def extremos(self) -> tuple[int, int]:
        return (self.mayor, self.menor)

    def tiene(self, numero: int) -> bool:
        return numero in (self.mayor, self.menor)

    def otro_extremo(self, numero: int) -> int:
        """Dado un extremo, devuelve el otro.

        En un doble devuelve el mismo número.
        """
        if numero == self.mayor:
            return self.menor
        if numero == self.menor:
            return self.mayor
        raise ValueError(f"La ficha {self} no tiene el extremo {numero}")

    def __str__(self) -> str:
        return f"{self.mayor}-{self.menor}"

    def __repr__(self) -> str:
        return f"Ficha({self.mayor}, {self.menor})"


def juego_completo() -> list[Ficha]:
    """Las 28 fichas del doble 6, en orden canónico."""
    return [
        Ficha(mayor, menor)
        for mayor in range(VALOR_MAXIMO + 1)
        for menor in range(mayor + 1)
    ]


def sumar(fichas: list[Ficha]) -> int:
    """Puntos totales de un conjunto de fichas."""
    return sum(f.valor for f in fichas)
