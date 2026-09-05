"""Una mano: desde el reparto hasta que se cierra (REGLAS.md §4 y §5)."""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum

from .conteo import ConteoLatino, ReglaConteo, pareja_de
from .ficha import Ficha, sumar
from .mesa import Lado, Mesa
from .reparto import JUGADORES


class FinDeMano(str, Enum):
    DOMINO = "domino"
    TRANCA = "tranca"
    EMPATE = "empate"


class MovimientoInvalido(Exception):
    """El jugador intentó algo que las reglas no permiten."""


@dataclass(frozen=True)
class Evento:
    """Un movimiento del historial.

    El paso se registra con los extremos que había en ese momento: es
    información pública que los jugadores usan para deducir manos, y sin
    ella no se puede reconstruir la partida.
    """

    jugador: int
    tipo: str  # "jugada" | "paso"
    ficha: Ficha | None = None
    lado: Lado | None = None
    extremos: tuple[int, int] | None = None


@dataclass(frozen=True)
class ResultadoMano:
    tipo: FinDeMano
    pareja_ganadora: int | None
    puntos: int
    jugador_que_cerro: int | None
    puntos_por_pareja: tuple[int, int]
    fichas_restantes: list[list[Ficha]]


@dataclass
class Mano:
    """Estado de una mano en curso.

    El motor no sabe de red ni de jugadores conectados. Recibe jugadas y
    responde si son legales. Quién las origina —una persona o un bot— es
    problema de quien lo use.
    """

    manos: list[list[Ficha]]
    turno: int
    conteo: ReglaConteo = field(default_factory=ConteoLatino)
    mesa: Mesa = field(default_factory=Mesa)
    historial: list[Evento] = field(default_factory=list)
    pasos_seguidos: int = 0
    resultado: ResultadoMano | None = None

    @property
    def terminada(self) -> bool:
        return self.resultado is not None

    def mano_de(self, jugador: int) -> list[Ficha]:
        return list(self.manos[jugador])

    def jugadas_posibles(self, jugador: int | None = None):
        """Jugadas legales del jugador indicado (por defecto, el del turno)."""
        j = self.turno if jugador is None else jugador
        return self.mesa.jugadas_posibles(self.manos[j])

    def debe_pasar(self, jugador: int | None = None) -> bool:
        return not self.jugadas_posibles(jugador)

    def jugar(self, ficha: Ficha, lado: Lado = Lado.DERECHA) -> ResultadoMano | None:
        """Coloca una ficha del jugador en turno.

        Devuelve el resultado si la mano se cerró, o None si sigue.
        """
        self._exigir_en_curso()
        if ficha not in self.manos[self.turno]:
            raise MovimientoInvalido(
                f"El jugador {self.turno} no tiene la ficha {ficha}"
            )
        if lado not in self.mesa.lados_validos(ficha):
            raise MovimientoInvalido(
                f"{ficha} no encaja por la {lado.value} "
                f"(extremos: {self.mesa.extremos})"
            )

        self.manos[self.turno].remove(ficha)
        self.mesa.colocar(ficha, lado)
        self.historial.append(
            Evento(self.turno, "jugada", ficha, lado, self.mesa.extremos)
        )
        self.pasos_seguidos = 0

        if not self.manos[self.turno]:
            return self._cerrar_por_domino()

        self._avanzar()
        return None

    def pasar(self) -> ResultadoMano | None:
        """El jugador en turno pasa.

        El paso es obligatorio, no opcional: si tiene ficha jugable, se
        rechaza (REGLAS.md §4).
        """
        self._exigir_en_curso()
        if not self.debe_pasar():
            raise MovimientoInvalido(
                f"El jugador {self.turno} tiene jugada válida y no puede pasar"
            )

        self.historial.append(
            Evento(self.turno, "paso", extremos=self.mesa.extremos)
        )
        self.pasos_seguidos += 1

        if self.pasos_seguidos == JUGADORES:
            return self._cerrar_por_tranca()

        self._avanzar()
        return None

    # --- interno ---

    def _exigir_en_curso(self) -> None:
        if self.terminada:
            raise MovimientoInvalido("La mano ya terminó")

    def _avanzar(self) -> None:
        """El turno avanza a la derecha (REGLAS.md §4)."""
        self.turno = (self.turno + 1) % JUGADORES

    def _puntos_por_pareja(self) -> tuple[int, int]:
        return (
            sum(sumar(m) for j, m in enumerate(self.manos) if pareja_de(j) == 0),
            sum(sumar(m) for j, m in enumerate(self.manos) if pareja_de(j) == 1),
        )

    def _cerrar_por_domino(self) -> ResultadoMano:
        ganadora = pareja_de(self.turno)
        self.resultado = ResultadoMano(
            tipo=FinDeMano.DOMINO,
            pareja_ganadora=ganadora,
            puntos=self.conteo.puntos(self.manos, ganadora),
            jugador_que_cerro=self.turno,
            puntos_por_pareja=self._puntos_por_pareja(),
            fichas_restantes=[list(m) for m in self.manos],
        )
        return self.resultado

    def _cerrar_por_tranca(self) -> ResultadoMano:
        a, b = self._puntos_por_pareja()

        if a == b:
            # Empate: nadie anota (REGLAS.md §5.2)
            self.resultado = ResultadoMano(
                tipo=FinDeMano.EMPATE,
                pareja_ganadora=None,
                puntos=0,
                jugador_que_cerro=None,
                puntos_por_pareja=(a, b),
                fichas_restantes=[list(m) for m in self.manos],
            )
            return self.resultado

        ganadora = 0 if a < b else 1
        self.resultado = ResultadoMano(
            tipo=FinDeMano.TRANCA,
            pareja_ganadora=ganadora,
            puntos=self.conteo.puntos(self.manos, ganadora),
            jugador_que_cerro=None,
            puntos_por_pareja=(a, b),
            fichas_restantes=[list(m) for m in self.manos],
        )
        return self.resultado
