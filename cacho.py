from __future__ import annotations

from dataclasses import dataclass, field
from itertools import product
from random import Random
from typing import Dict, Iterable, List, Optional, Sequence, Tuple


CATEGORIAS = (
    "unos",
    "doses",
    "treses",
    "cuatros",
    "cincos",
    "seises",
    "tercia",
    "full",
    "escalera",
    "poker",
    "generala",
    "chance",
)

PUNTOS_CARAS = {categoria: indice for indice, categoria in enumerate(CATEGORIAS[:6], 1)}


def combinaciones_dados(dados: Sequence[int], indices: Iterable[int]) -> Iterable[Tuple[int, ...]]:
    indices = tuple(indices)
    for valores in product(range(1, 7), repeat=len(indices)):
        nuevo = list(dados)
        for indice, valor in zip(indices, valores):
            nuevo[indice] = valor
        yield tuple(nuevo)


def puntuacion(categoria: str, dados: Sequence[int]) -> int:
    """Calcula la puntuacion de una categoria para cinco dados."""
    if categoria not in CATEGORIAS:
        raise ValueError(f"Categoria desconocida: {categoria}")
    dados = tuple(dados)
    conteos = {valor: dados.count(valor) for valor in range(1, 7)}
    suma = sum(dados)

    if categoria in PUNTOS_CARAS:
        valor = PUNTOS_CARAS[categoria]
        return valor * conteos[valor]
    return puntuacion_combinacion(categoria, dados, conteos, suma)


def puntuacion_combinacion(categoria: str, dados: Sequence[int], conteos: Dict[int, int], suma: int) -> int:
    valores = set(dados)
    patrones = {
        "tercia": (max(conteos.values()) >= 3, suma),
        "full": (sorted(conteos.values()) == [0, 0, 0, 0, 2, 3], 25),
        "escalera": (valores in ({1, 2, 3, 4, 5}, {2, 3, 4, 5, 6}), 30),
        "poker": (max(conteos.values()) >= 4, 40),
        "generala": (max(conteos.values()) == 5, 50),
        "chance": (True, suma),
    }
    valido, puntos = patrones[categoria]
    return puntos if valido else 0


def es_categoria_valida(categoria: str, disponibles: Sequence[str]) -> bool:
    return categoria in disponibles


@dataclass
class Jugador:
    nombre: str
    es_humano: bool
    puntajes: Dict[str, int] = field(default_factory=dict)

    @property
    def total(self) -> int:
        return sum(self.puntajes.values())


class JuegoCacho:
    """Motor de una partida de cinco dados con tres lanzamientos por turno."""

    def __init__(self, jugador_humano: str = "Tu", jugador_ia: str = "IA", semilla: Optional[int] = None):
        self.rng = Random(semilla)
        self.jugadores = [Jugador(jugador_humano, True), Jugador(jugador_ia, False)]
        self.turno = 0
        self.dados = (0, 0, 0, 0, 0)
        self.lanzamientos = 0
        self.terminado = False

    @property
    def jugador_actual(self) -> Jugador:
        return self.jugadores[self.turno]

    @property
    def categorias_disponibles(self) -> List[str]:
        usadas = set(self.jugador_actual.puntajes)
        return [categoria for categoria in CATEGORIAS if categoria not in usadas]

    def lanzar(self, indices: Optional[Iterable[int]] = None) -> Tuple[int, ...]:
        if self.lanzamientos >= 3:
            raise RuntimeError("Ya no quedan lanzamientos en este turno")
        indices = range(5) if indices is None else tuple(indices)
        if any(indice not in range(5) for indice in indices):
            raise ValueError("Los indices de dados deben estar entre 0 y 4")
        dados = list(self.dados)
        for indice in indices:
            dados[indice] = self.rng.randint(1, 6)
        self.dados = tuple(dados)
        self.lanzamientos += 1
        return self.dados

    def anotar(self, categoria: str) -> int:
        if self.lanzamientos == 0:
            raise RuntimeError("Debes lanzar los dados antes de anotar")
        if categoria not in self.categorias_disponibles:
            raise ValueError("Esa categoria no esta disponible")
        puntos = puntuacion(categoria, self.dados)
        self.jugador_actual.puntajes[categoria] = puntos
        if all(len(jugador.puntajes) == len(CATEGORIAS) for jugador in self.jugadores):
            self.terminado = True
        else:
            self.turno = 1 - self.turno
            self.dados = (0, 0, 0, 0, 0)
            self.lanzamientos = 0
        return puntos

    def estado(self) -> str:
        jugador = self.jugador_actual
        categorias = ", ".join(self.categorias_disponibles)
        return f"Turno de {jugador.nombre} | dados: {self.dados} | lanzamiento: {self.lanzamientos}/3 | categorias: {categorias}"
