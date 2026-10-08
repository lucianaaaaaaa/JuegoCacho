from __future__ import annotations

from agente_cacho import ExpectiminimaxAgent
from cacho import CATEGORIAS, JuegoCacho, puntuacion


def mostrar_puntajes(juego: JuegoCacho) -> None:
    print("\nPUNTUACIONES")
    for jugador in juego.jugadores:
        print(f"{jugador.nombre}: {jugador.total} puntos")
        if jugador.puntajes:
            print("  " + " | ".join(f"{categoria}: {puntos}" for categoria, puntos in jugador.puntajes.items()))


def pedir_indices() -> tuple[int, ...]:
    respuesta = input("Dados a relanzar (1-5, separados por espacios; Enter para ninguno): ").strip()
    if not respuesta:
        return ()
    try:
        indices = tuple(int(valor) - 1 for valor in respuesta.split())
    except ValueError as error:
        raise ValueError("Escribe solo numeros del 1 al 5") from error
    if len(set(indices)) != len(indices) or any(indice not in range(5) for indice in indices):
        raise ValueError("Cada dado debe aparecer una sola vez y estar entre 1 y 5")
    return indices


def turno_humano(juego: JuegoCacho) -> None:
    juego.lanzar()
    print(f"\nTus dados: {juego.dados}")
    while juego.lanzamientos < 3:
        try:
            indices = pedir_indices()
        except ValueError as error:
            print(f"Entrada invalida: {error}")
            continue
        if not indices:
            break
        juego.lanzar(indices)
        print(f"Resultado: {juego.dados}")
    print("Categorias disponibles:")
    for numero, categoria in enumerate(juego.categorias_disponibles, 1):
        print(f"  {numero}. {categoria}: {puntuacion(categoria, juego.dados)}")
    while True:
        respuesta = input("Elige el numero de categoria: ").strip()
        try:
            categoria = juego.categorias_disponibles[int(respuesta) - 1]
            break
        except (ValueError, IndexError):
            print("Seleccion invalida.")
    puntos = juego.anotar(categoria)
    print(f"Anotaste {puntos} puntos en {categoria}.")


def turno_ia(juego: JuegoCacho, agente: ExpectiminimaxAgent) -> None:
    juego.lanzar()
    while juego.lanzamientos < 3:
        indices = agente.elegir_indices_relanzamiento(juego.dados, juego.categorias_disponibles, 3 - juego.lanzamientos)
        if not indices:
            break
        juego.lanzar(indices)
    categoria = agente.elegir_categoria(juego.dados, juego.categorias_disponibles)
    puntos = juego.anotar(categoria)
    print(f"\nLa IA obtuvo {juego.dados}, eligio {categoria} y anoto {puntos} puntos.")
    print(f"Nodos explorados: {agente.nodos_explorados}")


def main() -> None:
    print("=== CACHO: humano contra agente expectiminimax ===")
    print("Cada turno permite hasta tres lanzamientos. Puedes relanzar solo los dados que indiques.")
    juego = JuegoCacho()
    agente = ExpectiminimaxAgent(profundidad=2)
    while not juego.terminado:
        if juego.jugador_actual.es_humano:
            turno_humano(juego)
        else:
            turno_ia(juego, agente)
        mostrar_puntajes(juego)
    print("\n=== PARTIDA TERMINADA ===")
    mostrar_puntajes(juego)
    humano, ia = juego.jugadores
    if humano.total > ia.total:
        print("Ganaste la partida.")
    elif ia.total > humano.total:
        print("La IA gano la partida.")
    else:
        print("La partida termino en empate.")


if __name__ == "__main__":
    main()
