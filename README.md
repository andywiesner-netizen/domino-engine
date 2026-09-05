# domino-engine

Motor de reglas de dominó doble 6 por parejas. Lógica pura: sin red, sin base de datos, sin interfaz.

Se instala como paquete en las apps que lo necesiten, de modo que las reglas existan **una sola vez**:

```bash
pip install git+https://github.com/andywiesner-netizen/domino-engine.git
```

La especificación que implementa está en [REGLAS.md](REGLAS.md). Cada test referencia la sección que verifica.

## Estado

**Motor completo.** Fichas, mesa, reparto, turnos, paso obligado, tranca, los dos modos de conteo, bot y partida. 49 tests en verde y los 15 casos obligatorios de la especificación cubiertos.

Falta solo la política de reconexión, que es decisión del servidor y no del motor.

## Uso

```python
import random
from domino_engine import Partida, FinDeMano, bot

rng = random.Random()
partida = Partida(puntos_meta=100, modo_conteo="latino")

while not partida.terminada:
    mano = partida.nueva_mano(rng)

    while not mano.terminada:
        if mano.debe_pasar():
            resultado = mano.pasar()
        else:
            ficha, lado = bot.escoger(mano.mesa, mano.manos[mano.turno])
            resultado = mano.jugar(ficha, lado)

    partida.registrar(resultado)

print(f"Gana la pareja {partida.ganadora} en {partida.manos_jugadas} manos")
```

`jugar()` y `pasar()` devuelven el `ResultadoMano` cuando la mano se cierra, y `None` mientras siga. Cualquier movimiento ilegal levanta `MovimientoInvalido`: el motor nunca acepta una jugada inválida en silencio.

```python
mano.jugadas_posibles()      # [(Ficha, Lado), ...] del jugador en turno
mano.debe_pasar()            # True si no tiene ninguna
mano.mesa.extremos           # (6, 2)
mano.historial               # eventos, incluidos los pasos con sus extremos
```

## Desarrollo

```bash
pip install -e ".[dev]"
pytest
python ejemplo_mano.py 7 latino 100     # juega una partida en la terminal
```

## Decisiones de diseño

**`Ficha` es inmutable y se normaliza.** `Ficha(4, 6)` y `Ficha(6, 4)` son la misma. Es hashable, así que sirve en conjuntos y como clave.

**La mesa guarda la orientación, no solo las fichas.** Cada `FichaColocada` conserva cómo quedó de izquierda a derecha. El frontend lo necesita para dibujar la cadena en SVG y recalcularlo después sería frágil.

**El paso se registra con los extremos del momento.** Es información pública que los jugadores usan para deducir manos. Sin ella no se puede reconstruir una partida.

**El conteo está aislado tras una interfaz.** `ConteoLatino` y `ConteoInternacional` implementan `ReglaConteo`. Un modo nuevo no obliga a tocar la lógica de juego.

**El generador aleatorio se inyecta.** `repartir(random.Random(42))` da siempre la misma mano. El servidor debe pasar `random.SystemRandom()`.

**El motor no sabe de jugadores ni de red.** Recibe fichas y devuelve fichas. Quién está conectado, quién se pasó de tiempo y quién es un bot es problema del servidor.

**El bot es determinista.** Ante la misma mesa y la misma mano escoge siempre igual, sin importar el orden de las fichas. Eso hace reproducible un bug reportado.

## Verificación

49 tests, más 2000 partidas completas simuladas con bots (1000 por modo) verificando tres invariantes: que la cadena encaje en cada unión, que ninguna ficha se pierda ni se duplique, y que toda partida termine. Cero fallas.

Medición sobre esas partidas, útil para calibrar la meta por defecto:

| | latino | internacional |
|---|---|---|
| dominó limpio | 71.9% | 72.1% |
| tranca | 25.8% | 25.8% |
| tranca empatada | 2.3% | 2.1% |
| manos por partida a 100 pts | 12.9 | 8.2 |
| puntos por mano | 13.0 | 20.3 |

## Próximo

El motor está listo para que lo use un servidor. Lo que sigue vive fuera de este repo:

- `domino-online` — FastAPI + WebSockets, salas, reconexión
- `domino-web` — React + Vite, mesa en SVG
