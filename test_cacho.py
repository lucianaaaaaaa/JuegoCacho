import unittest

from cacho import CATEGORIAS, JuegoCacho, puntuacion
from agente_cacho import ExpectiminimaxAgent


class ReglasCachoTest(unittest.TestCase):
    def test_categorias_especiales(self):
        self.assertEqual(puntuacion("generala", (6, 6, 6, 6, 6)), 50)
        self.assertEqual(puntuacion("poker", (4, 4, 4, 4, 2)), 40)
        self.assertEqual(puntuacion("full", (2, 2, 5, 5, 5)), 25)
        self.assertEqual(puntuacion("escalera", (2, 3, 4, 5, 6)), 30)

    def test_no_se_repite_categoria(self):
        juego = JuegoCacho(semilla=7)
        juego.lanzar()
        juego.anotar("chance")
        self.assertIn("chance", juego.jugadores[0].puntajes)
        juego.turno = 0
        self.assertNotIn("chance", juego.categorias_disponibles)

    def test_agente_devuelve_accion_valida(self):
        agente = ExpectiminimaxAgent()
        dados, categoria = agente.elegir_turno((1, 2, 3, 4, 5), 1, CATEGORIAS)
        self.assertEqual(len(dados), 5)
        self.assertIn(categoria, CATEGORIAS)


if __name__ == "__main__":
    unittest.main()
