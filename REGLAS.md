# Especificación de reglas — Dominó doble 6 por parejas

Documento base para `domino-engine`. Toda función del motor debe poder rastrearse hasta una regla de aquí. Lo que no esté especificado se marca como **PENDIENTE** y no se implementa.

Versión 0.2 — completa. Implementada en `domino_engine`, sin puntos abiertos que bloqueen el motor.

---

## 1. Elementos del juego

**Fichas:** juego doble 6, 28 fichas. Cada ficha tiene dos extremos con valores de 0 a 6. Los dobles tienen ambos extremos iguales.

**Valor de una ficha:** la suma de sus dos extremos. El 6-4 vale 10, el doble 6 vale 12, el 0-0 vale 0.

**Jugadores:** cuatro, en dos parejas fijas. Los compañeros se sientan enfrentados, de modo que el turno siempre alterna entre parejas.

Posiciones en la mesa: `0`, `1`, `2`, `3`. Pareja A = posiciones `0` y `2`. Pareja B = posiciones `1` y `3`.

**Mano:** una ronda completa, desde el reparto hasta que se cierra por dominó limpio o tranca. Al terminar se anotan puntos.

**Partida:** sucesión de manos hasta que una pareja alcanza el puntaje meta.

---

## 2. Parámetros configurables

| Parámetro | Descripción | Valor por defecto |
|---|---|---|
| `puntos_meta` | Puntos para ganar la partida | 100 |
| `modo_conteo` | `latino` o `internacional` | `latino` |
| `segundos_por_jugada` | Tiempo por turno | 30 |
| `segundos_reconexion` | Espera antes de que el bot tome el control | **PENDIENTE** |

`puntos_meta` y `modo_conteo` no son independientes en la práctica: a la
misma meta, una partida internacional dura cerca de un 35% menos manos
que una latina, porque cada mano anota más. Medido sobre 1000 partidas
por modo: 12.9 manos en latino contra 8.2 en internacional, a 100 puntos.
Conviene que el valor por defecto de la meta dependa del modo.

---

## 3. Reparto y salida

Las 28 fichas se barajan y se reparten 7 a cada jugador. No queda pozo: todas las fichas están en manos de los jugadores.

**Primera mano de la partida:** el jugador que sale se escoge al azar entre los cuatro. No se usa el doble 6 ni ningún otro criterio.

**Manos siguientes:** sale el jugador a la derecha del que salió en la mano anterior. La rotación depende únicamente de quién salió antes, **no de quién ganó**.

Esto significa que en cuatro manos consecutivas sale cada jugador una vez, sin importar los resultados.

**Nueva partida:** se vuelve a sortear al azar.

---

## 4. Desarrollo de la mano

El jugador que sale coloca cualquier ficha de su mano. No hay restricción sobre cuál.

A partir de ahí, el turno avanza a la derecha, en el mismo sentido en que rota la salida. En cada turno el jugador debe colocar una ficha que tenga un extremo coincidente con alguno de los dos extremos libres de la mesa.

Si no tiene ninguna ficha jugable, **pasa**. El paso es obligatorio: un jugador con ficha válida no puede pasar.

**El paso es información pública.** Todos los jugadores ven que alguien pasó y en qué extremos estaban los números. Es información central del juego y el motor debe registrarla en el historial de la mano.

---

## 5. Fin de la mano

Una mano termina de dos maneras.

### 5.1 Dominó limpio

Un jugador coloca su última ficha. Su pareja gana la mano.

### 5.2 Tranca

Ningún jugador puede jugar: los cuatro pasan consecutivamente y quedan fichas en mano.

Se suman los puntos de cada pareja. **Gana la pareja con menor suma.** La comparación es entre totales de pareja, no entre jugadores individuales.

Si ambas parejas suman igual, la mano queda en **empate**: ninguna pareja anota, se registra la mano y se continúa con la rotación normal de salida.

---

## 6. Puntuación

La diferencia entre los dos modos está únicamente en **qué fichas se cuentan**. En ambos, los puntos van íntegros a la pareja ganadora.

| | Latino | Internacional |
|---|---|---|
| **Dominó limpio** | Fichas de la pareja rival | Todas las fichas no jugadas (rivales + compañero) |
| **Tranca con ganador** | Fichas de la pareja rival | Todas las fichas no jugadas (las cuatro manos) |
| **Tranca empatada** | 0 | 0 |

### Ejemplos numéricos

**Dominó limpio.** La posición `0` juega su última ficha. Quedan: compañero (`2`) con 7 puntos, rivales (`1` y `3`) con 12 y 9.

- Latino → Pareja A anota **21**
- Internacional → Pareja A anota **28**

**Tranca con ganador.** Pareja A suma 15, Pareja B suma 22. Gana A.

- Latino → A anota **22**
- Internacional → A anota **37**

**Tranca empatada.** Ambas parejas suman 18. Nadie anota. Sale el siguiente en la rotación.

---

## 7. Fin de la partida

Los puntos se acumulan mano tras mano. La partida termina cuando una pareja **alcanza o supera** `puntos_meta`.

Como solo una pareja anota por mano, es imposible que ambas crucen la meta simultáneamente.

---

## 8. Tiempo de jugada y jugador automático

Cada jugador dispone de `segundos_por_jugada` para colocar ficha. Al vencerse el tiempo, el sistema juega por él.

**Criterio del bot, versión 1:** juega la ficha válida de mayor valor. Si tiene varias con el mismo valor, escoge la primera en orden canónico. Si no tiene ficha válida, pasa.

Se escoge deliberadamente un criterio simple y predecible para que ningún jugador sienta que la máquina decidió la partida. Se refinará después, y cualquier mejora debe quedar detrás de la misma interfaz.

---

## 9. Desconexión y reconexión

**PENDIENTE.** Falta definir:

- Cuántos segundos se espera antes de que el bot tome el control
- Si el jugador retoma su puesto de inmediato al volver, aun a media mano
- Si se avisa al resto de la mesa que un jugador está siendo jugado por el sistema
- Qué pasa si el desconectado no vuelve nunca: ¿la partida termina, se abandona, o el bot la completa?

---

## 10. Puntos abiertos

- **Abandono voluntario.** Qué ocurre si un jugador se sale a propósito a mitad de partida. No bloquea el motor: es una decisión del servidor.

Resueltos: el turno avanza a la derecha igual que la rotación de salida (§4), y no existen puntos extra por zapato ni por capicúa.

---

## 11. Casos de prueba obligatorios

El motor no se considera terminado hasta que estos casos pasen:

1. Reparto: 28 fichas, 7 por jugador, sin repetidas y sin pozo
2. La primera ficha siempre es válida, sea cual sea
3. Una ficha sin extremo coincidente es rechazada
4. Un jugador con ficha válida no puede pasar
5. Cuatro pasos consecutivos disparan la tranca
6. Tranca: gana la pareja de menor suma
7. Tranca empatada: cero puntos y la rotación continúa normal
8. Dominó limpio latino: solo cuentan los rivales
9. Dominó limpio internacional: cuentan rivales y compañero
10. Tranca internacional: cuentan las cuatro manos
11. La salida rota a la derecha sin importar quién ganó
12. Nueva partida: la salida se sortea de nuevo
13. La partida termina al alcanzar o superar la meta
14. Bot: escoge la ficha válida de mayor valor
15. Bot sin ficha válida: pasa

---

## 12. Estado de implementación

Los 15 casos pasan. La puntuación vive aislada detrás de una interfaz:

```python
class ReglaConteo(Protocol):
    def puntos(self, manos: list[list[Ficha]],
               pareja_ganadora: int) -> int: ...
```

`ConteoLatino` y `ConteoInternacional` la implementan. Agregar un modo nuevo no requiere tocar la lógica de juego.

Además de los tests, se verificaron 2000 partidas completas jugadas por bots (1000 por modo) comprobando que ninguna ficha se pierda ni se duplique, que toda partida termine, y que el empate nunca anote.
