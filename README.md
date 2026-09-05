# domino-engine

Motor de reglas de dominó doble 6 por parejas. Lógica pura: sin red, sin base de datos, sin interfaz.

Se instala como paquete en las apps que lo necesiten, de modo que las reglas existan **una sola vez**:

```bash
pip install git+https://github.com/USUARIO/domino-engine.git
```

La especificación que implementa está en [REGLAS.md](REGLAS.md). Cada test referencia la sección que verifica.

## Estado

**Rebanada 1 — completa.** Fichas, mesa, validación de jugada, reparto y rotación de salida. 22 tests en verde.

Falta: turnos, tranca, conteo de puntos, partida. Ver *Próximo* abajo.

## Uso

```python
from domino_engine import Mesa, Ficha, Lado, repartir, sortear_salida

manos = repartir()
turno = sortear_salida()

mesa = Mesa()
mesa.colocar(Ficha(6, 4))
mesa.extremos                      # (6, 4)

mesa.jugadas_posibles(manos[0])    # [(Ficha, Lado), ...]
mesa.colocar(Ficha(4, 2), Lado.DERECHA)
mesa.extremos                      # (6, 2)
print(mesa)                        # [6|4] [4|2]
```

Una ficha que encaja por ambos lados aparece dos veces en `jugadas_posibles`: son jugadas distintas y el jugador debe escoger.

## Desarrollo

```bash
pip install -e ".[dev]"
pytest
python ejemplo_mano.py 42      # juega una mano en la terminal
```

`ejemplo_mano.py` no es parte del paquete. Es una demostración: implementa turnos y tranca de forma provisional para probar que las piezas encajan. Esa lógica se muda a `domino_engine/mano.py` en la rebanada 2.

## Decisiones de diseño

**`Ficha` es inmutable y se normaliza.** `Ficha(4, 6)` y `Ficha(6, 4)` son la misma. Es hashable, así que sirve en conjuntos y como clave.

**La mesa guarda la orientación, no solo las fichas.** Cada `FichaColocada` conserva cómo quedó de izquierda a derecha. El frontend lo necesita para dibujar la cadena en SVG y recalcularlo después sería frágil.

**El generador aleatorio se inyecta.** `repartir(random.Random(42))` reproduce la misma mano siempre. Los tests dependen de eso. El servidor debe pasar `random.SystemRandom()`.

**El motor no sabe de jugadores ni de red.** Recibe fichas y devuelve fichas. Quién está conectado, quién se pasó de tiempo y quién es un bot es problema del servidor.

## Verificación

Además de los 22 tests, se simularon 500 manos completas verificando dos invariantes: que la cadena encaje en cada unión, y que ninguna ficha se pierda ni se duplique entre la mesa y las manos. Cero fallas.

## Próximo

- `mano.py` — turnos, paso obligado, detección de tranca
- `conteo.py` — `ConteoLatino` y `ConteoInternacional` tras una interfaz común
- `partida.py` — acumulación de puntos, rotación entre manos, fin de partida
- `bot.py` — el jugador automático, hoy provisional en `ejemplo_mano.py`
