# Cacho: agente con expectiminimax

Ejercicio de juego de dados para dos jugadores. Cada turno tiene hasta tres lanzamientos y termina anotando una categoria disponible. La IA calcula sus relanzamientos con nodos:

- **MAX**: la IA escoge el relanzamiento o la categoria que maximiza su utilidad.
- **CHANCE**: se promedian los resultados posibles de los dados.
- **MIN**: se descuenta la mejor categoria que el rival podria aprovechar como presion competitiva.

La interfaz es de consola para que el juego sea facil de ejecutar sin instalar dependencias externas.

## Ejecutar

Desde esta carpeta:

```bash
python main.py
```

En el turno humano, escribe los numeros de los dados que quieres relanzar, por ejemplo `1 4 5`. Pulsa Enter sin numeros para conservar todos los dados y pasar a elegir categoria.

## Validar

```bash
python -m unittest -v
```
