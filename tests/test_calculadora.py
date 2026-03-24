import unittest

from config.settings import DEFAULT_DATA
from core.calculadora import calcular_todo


class CalculadoraTests(unittest.TestCase):
    def test_calcula_valores_principales_con_data_base(self):
        resultado = calcular_todo(DEFAULT_DATA)

        self.assertEqual(resultado["capital_total"], 72300)
        self.assertEqual(resultado["total_cuotas_mes"], 1620)
        self.assertAlmostEqual(resultado["ganancia_tc"], 907.5)
        self.assertAlmostEqual(resultado["fondo_disponible"], 28227.0)
        self.assertEqual(resultado["ventas_finales"], 12006.0)
        self.assertEqual(resultado["utilidad_bruta"], 1863.0)

    def test_sin_operacion_de_cambio_devuelve_ceros_relacionados(self):
        data = {
            **DEFAULT_DATA,
            "operaciones_cambio": [],
        }

        resultado = calcular_todo(data)

        self.assertEqual(resultado["soles_usados"], 0)
        self.assertEqual(resultado["usd_comprados"], 0)
        self.assertEqual(resultado["ganancia_tc"], 0)
        self.assertEqual(resultado["soles_libres"], resultado["capital_total"])


if __name__ == "__main__":
    unittest.main()
