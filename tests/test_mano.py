"""Tests de la rebanada 2: turnos, tranca, conteo y partida.

Cada test referencia la sección de REGLAS.md que verifica.

Nota: los tests usan manos cortas (2 o 3 fichas) en vez de 7. El motor no
exige 7 —eso lo impone `repartir`— y con manos cortas los escenarios de
tranca y conteo quedan explícitos en vez de depender de una semilla.
"""

import random

import pytest

from domino_engine import (
    ConteoInternacional,
    ConteoLatino,
    Ficha,
    FinDeMano,
    Lado,
    Mano,
    Mesa,
    MovimientoInvalido,
    Partida,
    bot,
    pareja_de,
    regla,
)

# Escenario base: el jugador 0 abre con el 6-6 y nadie más tiene un 6,
# así que los tres pasan y el turno vuelve al 0.
SEIS_DOBLE = Ficha(6, 6)


def mano_tranca(conteo=None):
    """p0 juega 6-6 y le queda 1-1; nadie tiene 6.

    Pareja 0 = 2 + 4 = 6 · Pareja 1 = 5 + 6 = 11 → gana la pareja 0.
    """
    return Mano(
        manos=[
            [SEIS_DOBLE, Ficha(1, 1)],  # queda  2
            [Ficha(3, 2)],              # queda  5
            [Ficha(4, 0)],              # queda  4
            [Ficha(5, 1)],              # queda  6
        ],
        turno=0,
        conteo=conteo or ConteoLatino(),
    )


def mano_domino(conteo=None):
    """p0 tiene una sola ficha: al jugarla cierra por dominó limpio.

    Rivales = 5 + 6 = 11 · compañero = 4.
    """
    return Mano(
        manos=[
            [SEIS_DOBLE],
            [Ficha(3, 2)],  # 5
            [Ficha(4, 0)],  # 4
            [Ficha(5, 1)],  # 6
        ],
        turno=0,
        conteo=conteo or ConteoLatino(),
    )


def llevar_a_tranca(mano):
    mano.jugar(SEIS_DOBLE)
    for _ in range(3):
        mano.pasar()
    return mano.pasar()


# --- Parejas (REGLAS.md §1) ---


def test_los_companeros_estan_enfrentados():
    assert pareja_de(0) == pareja_de(2) == 0
    assert pareja_de(1) == pareja_de(3) == 1


# --- Turnos (REGLAS.md §4, caso 4) ---


def test_el_turno_avanza_a_la_derecha():
    mano = mano_domino()
    mano.manos[0] = [SEIS_DOBLE, Ficha(0, 0)]
    mano.jugar(SEIS_DOBLE)
    assert mano.turno == 1


def test_un_jugador_con_ficha_valida_no_puede_pasar():
    mano = mano_tranca()
    with pytest.raises(MovimientoInvalido):
        mano.pasar()


def test_no_se_puede_jugar_una_ficha_que_no_se_tiene():
    mano = mano_tranca()
    with pytest.raises(MovimientoInvalido):
        mano.jugar(Ficha(0, 0))


def test_no_se_puede_jugar_por_un_lado_que_no_encaja():
    mano = mano_tranca()
    mano.jugar(SEIS_DOBLE)
    mano.pasar()
    mano.pasar()
    with pytest.raises(MovimientoInvalido):
        mano.jugar(Ficha(5, 1), Lado.DERECHA)


def test_no_se_puede_jugar_despues_de_cerrada():
    mano = mano_domino()
    mano.jugar(SEIS_DOBLE)
    assert mano.terminada
    with pytest.raises(MovimientoInvalido):
        mano.pasar()


def test_el_paso_queda_en_el_historial_con_los_extremos():
    mano = mano_tranca()
    mano.jugar(SEIS_DOBLE)
    mano.pasar()
    evento = mano.historial[-1]
    assert evento.tipo == "paso"
    assert evento.jugador == 1
    assert evento.extremos == (6, 6)


# --- Tranca (caso 5, 6 y 7) ---


def test_cuatro_pasos_seguidos_disparan_la_tranca():
    resultado = llevar_a_tranca(mano_tranca())
    assert resultado.tipo is FinDeMano.TRANCA


def test_tranca_gana_la_pareja_de_menor_suma():
    resultado = llevar_a_tranca(mano_tranca())
    assert resultado.puntos_por_pareja == (6, 11)
    assert resultado.pareja_ganadora == 0


def test_tranca_empatada_no_anota_y_no_tiene_ganador():
    mano = Mano(
        manos=[
            [SEIS_DOBLE, Ficha(1, 1)],  # 2
            [Ficha(3, 2)],              # 5
            [Ficha(4, 1)],              # 5
            [Ficha(2, 0)],              # 2
        ],
        turno=0,
    )
    resultado = llevar_a_tranca(mano)
    assert resultado.tipo is FinDeMano.EMPATE
    assert resultado.puntos_por_pareja == (7, 7)
    assert resultado.pareja_ganadora is None
    assert resultado.puntos == 0


# --- Conteo (REGLAS.md §6, casos 8, 9 y 10) ---


def test_domino_limpio_latino_solo_cuenta_a_los_rivales():
    resultado = mano_domino(ConteoLatino()).jugar(SEIS_DOBLE)
    assert resultado.tipo is FinDeMano.DOMINO
    assert resultado.jugador_que_cerro == 0
    assert resultado.puntos == 11


def test_domino_limpio_internacional_cuenta_tambien_al_companero():
    resultado = mano_domino(ConteoInternacional()).jugar(SEIS_DOBLE)
    assert resultado.puntos == 15


def test_tranca_latino_solo_cuenta_a_los_rivales():
    assert llevar_a_tranca(mano_tranca(ConteoLatino())).puntos == 11


def test_tranca_internacional_cuenta_las_cuatro_manos():
    assert llevar_a_tranca(mano_tranca(ConteoInternacional())).puntos == 17


def test_regla_por_nombre():
    assert isinstance(regla("latino"), ConteoLatino)
    assert isinstance(regla("internacional"), ConteoInternacional)
    with pytest.raises(ValueError):
        regla("caribeño")


# --- Bot (REGLAS.md §8, casos 14 y 15) ---


def test_el_bot_escoge_la_ficha_valida_de_mayor_valor():
    mesa = Mesa()
    mesa.colocar(Ficha(6, 4))
    ficha, _ = bot.escoger(mesa, [Ficha(6, 0), Ficha(6, 5), Ficha(4, 1)])
    assert ficha == Ficha(6, 5)


def test_el_bot_pasa_si_no_tiene_ficha_valida():
    mesa = Mesa()
    mesa.colocar(SEIS_DOBLE)
    assert bot.escoger(mesa, [Ficha(3, 2), Ficha(1, 0)]) is None


def test_el_bot_es_determinista_sin_importar_el_orden_de_la_mano():
    mesa = Mesa()
    mesa.colocar(Ficha(6, 4))
    mano = [Ficha(6, 0), Ficha(4, 2), Ficha(6, 1), Ficha(4, 3)]
    esperado = bot.escoger(mesa, mano)
    for semilla in range(20):
        barajada = list(mano)
        random.Random(semilla).shuffle(barajada)
        assert bot.escoger(mesa, barajada) == esperado


# --- Partida (REGLAS.md §7, casos 11, 12 y 13) ---


def test_la_partida_acumula_puntos():
    partida = Partida(puntos_meta=50)
    partida.registrar(llevar_a_tranca(mano_tranca()))
    assert partida.marcador == [11, 0]
    assert partida.manos_jugadas == 1


def test_la_partida_termina_al_alcanzar_o_superar_la_meta():
    partida = Partida(puntos_meta=20)
    assert not partida.terminada
    for _ in range(2):
        partida.registrar(llevar_a_tranca(mano_tranca()))
    assert partida.marcador == [22, 0]
    assert partida.terminada
    assert partida.ganadora == 0


def test_la_salida_rota_sin_importar_quien_gano():
    partida = Partida()
    partida.nueva_mano(random.Random(1))
    primera = partida.salida
    for esperado in range(1, 5):
        partida.nueva_mano(random.Random(esperado))
        assert partida.salida == (primera + esperado) % 4


def test_nueva_partida_vuelve_a_sortear():
    salidas = set()
    for semilla in range(40):
        p = Partida()
        p.nueva_mano(random.Random(semilla))
        salidas.add(p.salida)
    assert len(salidas) > 1


def test_no_se_reparte_una_mano_con_la_partida_terminada():
    partida = Partida(puntos_meta=5)
    partida.registrar(llevar_a_tranca(mano_tranca()))
    with pytest.raises(RuntimeError):
        partida.nueva_mano()


def test_puntos_meta_invalido():
    with pytest.raises(ValueError):
        Partida(puntos_meta=0)


def test_el_empate_no_mueve_el_marcador_pero_cuenta_como_mano():
    partida = Partida()
    mano = Mano(
        manos=[[SEIS_DOBLE, Ficha(1, 1)], [Ficha(3, 2)], [Ficha(4, 1)], [Ficha(2, 0)]],
        turno=0,
    )
    partida.registrar(llevar_a_tranca(mano))
    assert partida.marcador == [0, 0]
    assert partida.manos_jugadas == 1


# --- Integración: partidas completas con bots ---


@pytest.mark.parametrize("modo", ["latino", "internacional"])
def test_partidas_completas_con_bots(modo):
    """200 partidas de punta a punta, verificando invariantes."""
    for semilla in range(200):
        rng = random.Random(semilla)
        partida = Partida(puntos_meta=100, modo_conteo=modo)
        while not partida.terminada:
            mano = partida.nueva_mano(rng)
            while not mano.terminada:
                jugada = bot.escoger(mano.mesa, mano.manos[mano.turno])
                resultado = (
                    mano.pasar() if jugada is None else mano.jugar(*jugada)
                )
            partida.registrar(resultado)

            # Ninguna ficha se pierde ni se duplica
            todas = mano.mesa.fichas_jugadas + [
                f for m in mano.manos for f in m
            ]
            assert len(set(todas)) == 28

            # El empate no anota; lo demás sí
            if resultado.tipo is FinDeMano.EMPATE:
                assert resultado.puntos == 0

        assert max(partida.marcador) >= 100
        assert partida.ganadora in (0, 1)
        assert partida.manos_jugadas > 0
