"""Tests de la primera rebanada: fichas, mesa y reparto.

Cada test referencia la sección de REGLAS.md que verifica.
"""

import random

import pytest

from domino_engine import (
    Ficha,
    JugadaInvalida,
    Lado,
    Mesa,
    juego_completo,
    repartir,
    siguiente_salida,
    sortear_salida,
    sumar,
)


# --- Fichas (REGLAS.md §1) ---


def test_ficha_se_normaliza():
    assert Ficha(4, 6) == Ficha(6, 4)
    assert Ficha(4, 6).mayor == 6


def test_ficha_es_hashable():
    assert len({Ficha(4, 6), Ficha(6, 4)}) == 1


def test_valor_es_la_suma():
    assert Ficha(6, 4).valor == 10
    assert Ficha(6, 6).valor == 12
    assert Ficha(0, 0).valor == 0


def test_dobles():
    assert Ficha(3, 3).es_doble
    assert not Ficha(3, 2).es_doble


def test_otro_extremo():
    assert Ficha(6, 4).otro_extremo(6) == 4
    assert Ficha(6, 4).otro_extremo(4) == 6
    assert Ficha(3, 3).otro_extremo(3) == 3
    with pytest.raises(ValueError):
        Ficha(6, 4).otro_extremo(2)


def test_extremos_fuera_de_rango():
    for par in ((7, 3), (-1, 2), (3, 9)):
        with pytest.raises(ValueError):
            Ficha(*par)


def test_juego_completo_son_28_distintas():
    juego = juego_completo()
    assert len(juego) == 28
    assert len(set(juego)) == 28
    assert sumar(juego) == 168


# --- Reparto (caso 1 de la especificación) ---


def test_reparto_28_fichas_7_por_jugador_sin_pozo():
    manos = repartir(random.Random(42))
    assert len(manos) == 4
    assert all(len(m) == 7 for m in manos)
    todas = [f for m in manos for f in m]
    assert len(set(todas)) == 28


def test_reparto_es_reproducible_con_semilla():
    assert repartir(random.Random(7)) == repartir(random.Random(7))


def test_sorteo_de_salida_en_rango():
    assert all(0 <= sortear_salida(random.Random(s)) < 4 for s in range(50))


# --- Rotación de salida (caso 11) ---


def test_la_salida_rota_a_la_derecha():
    assert [siguiente_salida(i) for i in range(4)] == [1, 2, 3, 0]


def test_cuatro_manos_dan_la_vuelta_completa():
    salida = 2
    vistos = []
    for _ in range(4):
        vistos.append(salida)
        salida = siguiente_salida(salida)
    assert sorted(vistos) == [0, 1, 2, 3]
    assert salida == 2


# --- Mesa (casos 2 y 3) ---


def test_mesa_vacia():
    mesa = Mesa()
    assert mesa.vacia
    assert mesa.extremos is None


def test_la_primera_ficha_siempre_es_valida():
    for ficha in juego_completo():
        mesa = Mesa()
        assert mesa.es_jugable(ficha)
        mesa.colocar(ficha)
        assert mesa.extremos == (ficha.mayor, ficha.menor)


def test_ficha_sin_extremo_coincidente_es_rechazada():
    mesa = Mesa()
    mesa.colocar(Ficha(6, 4))
    assert not mesa.es_jugable(Ficha(3, 2))
    with pytest.raises(JugadaInvalida):
        mesa.colocar(Ficha(3, 2), Lado.DERECHA)


def test_colocar_en_el_lado_equivocado_es_rechazado():
    mesa = Mesa()
    mesa.colocar(Ficha(6, 4))  # extremos 6 y 4
    with pytest.raises(JugadaInvalida):
        mesa.colocar(Ficha(6, 1), Lado.DERECHA)  # el 6 está a la izquierda


def test_extremos_se_actualizan_por_ambos_lados():
    mesa = Mesa()
    mesa.colocar(Ficha(6, 4))
    assert mesa.extremos == (6, 4)
    mesa.colocar(Ficha(4, 2), Lado.DERECHA)
    assert mesa.extremos == (6, 2)
    mesa.colocar(Ficha(6, 1), Lado.IZQUIERDA)
    assert mesa.extremos == (1, 2)


def test_la_orientacion_queda_registrada_para_dibujar():
    mesa = Mesa()
    mesa.colocar(Ficha(6, 4))
    mesa.colocar(Ficha(2, 4), Lado.DERECHA)
    assert str(mesa) == "[6|4] [4|2]"


def test_doble_no_rompe_la_cadena():
    mesa = Mesa()
    mesa.colocar(Ficha(6, 4))
    mesa.colocar(Ficha(4, 4), Lado.DERECHA)
    assert mesa.extremos == (6, 4)


def test_ficha_que_encaja_por_ambos_lados():
    mesa = Mesa()
    mesa.colocar(Ficha(6, 4))
    assert mesa.lados_validos(Ficha(6, 4)) == frozenset(
        {Lado.IZQUIERDA, Lado.DERECHA}
    )


def test_jugadas_posibles_lista_ambas_opciones():
    mesa = Mesa()
    mesa.colocar(Ficha(5, 3))  # extremos 5 y 3
    mano = [Ficha(5, 3), Ficha(5, 0), Ficha(1, 1)]
    jugadas = mesa.jugadas_posibles(mano)
    assert (Ficha(5, 3), Lado.IZQUIERDA) in jugadas
    assert (Ficha(5, 3), Lado.DERECHA) in jugadas
    assert (Ficha(5, 0), Lado.IZQUIERDA) in jugadas
    assert not any(f == Ficha(1, 1) for f, _ in jugadas)


def test_mano_sin_jugadas_posibles():
    mesa = Mesa()
    mesa.colocar(Ficha(6, 6))
    assert mesa.jugadas_posibles([Ficha(3, 2), Ficha(1, 0)]) == []
