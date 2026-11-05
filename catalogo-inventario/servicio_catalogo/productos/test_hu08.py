
from django.test import SimpleTestCase

from .validaciones_producto import (
    validar_precio,
    validar_stock,
    validar_imagenes
)


class ValidacionesProductoTests(SimpleTestCase):

    def test_precio_positivo(self):
        self.assertEqual(validar_precio(15000), 15000)

    def test_precio_cero_o_negativo(self):
        for precio in [0, -100, -0.5]:
            with self.subTest(precio=precio):
                with self.assertRaises(ValueError):
                    validar_precio(precio)

    def test_precio_no_numerico(self):
        with self.assertRaises(ValueError):
            validar_precio("precio-invalido")

    def test_precio_no_finito(self):
        for precio in ["NaN", "Infinity", "-Infinity"]:
            with self.subTest(precio=precio):
                with self.assertRaises(ValueError):
                    validar_precio(precio)

    def test_stock_cero(self):
        self.assertEqual(validar_stock(0), 0)

    def test_stock_negativo(self):
        with self.assertRaises(ValueError):
            validar_stock(-5)

    def test_stock_no_entero(self):
        for stock in [2.5, True, "10"]:
            with self.subTest(stock=stock):
                with self.assertRaises(ValueError):
                    validar_stock(stock)

    def test_imagenes_validas(self):
        for cantidad in [4, 5, 6]:
            with self.subTest(cantidad=cantidad):
                imagenes = ["imagen"] * cantidad
                self.assertEqual(
                    validar_imagenes(imagenes),
                    imagenes
                )

    def test_imagenes_invalidas(self):
        for cantidad in [0, 3, 7]:
            with self.subTest(cantidad=cantidad):
                with self.assertRaises(ValueError):
                    validar_imagenes(["imagen"] * cantidad)
