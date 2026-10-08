from __future__ import annotations

from functools import lru_cache
from typing import Iterable, Sequence, Tuple

from cacho import CATEGORIAS, combinaciones_dados, puntuacion


class ExpectiminimaxAgent:
    """Agente que combina decisiones MAX/MIN con nodos CHANCE de los dados.

    El nodo MIN representa la presion del rival: estima la mejor categoria que
    el rival podria aprovechar y la resta de la utilidad de nuestra jugada.
    """

    def __init__(self, profundidad: int = 2):
        self.profundidad = max(1, profundidad)
        self.nodos_explorados = 0
        self._max_cache = {}
        self._min_cache = {}

    def elegir_turno(self, dados: Sequence[int], lanzamientos: int, disponibles: Sequence[str]) -> Tuple[Tuple[int, ...], str]:
        self.nodos_explorados = 0
        dados = tuple(dados)
        restantes = 3 - lanzamientos
        if restantes <= 0:
            return dados, self.elegir_categoria(dados, disponibles)

        mejores = self._acciones_reducidas(dados)
        mejor_valor = float("-inf")
        mejor_dados = dados
        for indices in mejores:
            valor = self._chance(dados, indices, restantes, tuple(disponibles), self.profundidad)
            if valor > mejor_valor:
                mejor_valor, mejor_dados = valor, dados
                mejor_dados = max(
                    combinaciones_dados(dados, indices),
                    key=lambda candidato: self._valor_categoria(candidato, disponibles),
                )
        return mejor_dados, self.elegir_categoria(mejor_dados, disponibles)

    def elegir_indices_relanzamiento(self, dados: Sequence[int], disponibles: Sequence[str], lanzamientos_restantes: int) -> Tuple[int, ...]:
        """Elige que dados conservar entre lanzamientos en la interfaz."""
        if lanzamientos_restantes <= 0:
            return ()
        opciones = self._acciones_reducidas(tuple(dados))
        return max(
            opciones,
            key=lambda indices: self._chance(tuple(dados), indices, lanzamientos_restantes, tuple(disponibles), self.profundidad),
        )

    def elegir_categoria(self, dados: Sequence[int], disponibles: Sequence[str]) -> str:
        return max(disponibles, key=lambda categoria: self._min_value(tuple(dados), categoria, tuple(disponibles)))

    def _chance(self, dados: Tuple[int, ...], indices: Iterable[int], restantes: int, disponibles: Tuple[str, ...], profundidad: int) -> float:
        indices = tuple(indices)
        resultados = self._resultados_chance(dados, indices)
        if not resultados:
            return self._max_value(dados, disponibles)
        return sum(self._max_value(resultado, disponibles) if restantes == 1 or profundidad <= 1 else self._chance_siguiente(resultado, disponibles, restantes - 1, profundidad - 1) for resultado in resultados) / len(resultados)

    def _chance_siguiente(self, dados: Tuple[int, ...], disponibles: Tuple[str, ...], restantes: int, profundidad: int) -> float:
        return max(self._chance(dados, indices, restantes, disponibles, profundidad) for indices in self._acciones_reducidas(dados))

    def _max_value(self, dados: Tuple[int, ...], disponibles: Tuple[str, ...]) -> float:
        clave = (dados, disponibles)
        if clave in self._max_cache:
            return self._max_cache[clave]
        self.nodos_explorados += 1
        valor = max(self._min_value(dados, categoria, disponibles) for categoria in disponibles)
        self._max_cache[clave] = valor
        return valor

    def _min_value(self, dados: Tuple[int, ...], categoria: str, disponibles: Tuple[str, ...]) -> float:
        clave = (dados, categoria, disponibles)
        if clave in self._min_cache:
            return self._min_cache[clave]
        propio = puntuacion(categoria, dados)
        respuestas_rival = [puntuacion(otra, dados) for otra in disponibles if otra != categoria]
        presion = max(respuestas_rival, default=0)
        valor = propio - presion * 0.35
        self._min_cache[clave] = valor
        return valor

    @staticmethod
    def _resultados_chance(dados: Tuple[int, ...], indices: Tuple[int, ...]) -> Tuple[Tuple[int, ...], ...]:
        resultados = tuple(combinaciones_dados(dados, indices))
        limite = 72
        if len(resultados) <= limite:
            return resultados
        paso = len(resultados) / limite
        return tuple(resultados[int(posicion * paso)] for posicion in range(limite))

    def _valor_categoria(self, dados: Sequence[int], disponibles: Sequence[str]) -> int:
        return max((puntuacion(categoria, dados) for categoria in disponibles), default=0)

    @staticmethod
    @lru_cache(maxsize=4096)
    def _acciones_reducidas(dados: Tuple[int, ...]) -> Tuple[Tuple[int, ...], ...]:
        """Reduce el branching conservando grupos y dados unicos prometedores."""
        candidatos = {()}
        for valor in set(dados):
            candidatos.add(tuple(indice for indice, dado in enumerate(dados) if dado != valor))
        candidatos.add((0, 1, 2, 3, 4))
        return tuple(sorted(candidatos, key=lambda indices: (len(indices), indices)))
