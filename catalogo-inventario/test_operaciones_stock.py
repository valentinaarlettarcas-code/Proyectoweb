
import unittest
from unittest.mock import MagicMock

from reservas_stock import reservar_stock
from operaciones_stock import consolidar_stock, liberar_stock


class TestInventario(unittest.TestCase):

    def setUp(self):
        self.db = MagicMock()

        self.session = (
            self.db.client.start_session
            .return_value.__enter__.return_value
        )

        self.session.with_transaction.side_effect = (
            lambda funcion, **kwargs: funcion(self.session)
        )

        self.db.productos.update_one.return_value.modified_count = 1
        self.db.reservas.update_one.return_value.modified_count = 1

    def test_reservar_stock(self):
        self.db.reservas.find_one.return_value = None

        resultado = reservar_stock(
            self.db,
            "RES-001",
            "ORD-001",
            [{"producto_id": 1, "cantidad": 2}]
        )

        self.assertEqual(resultado["estado"], "RESERVADA")
        self.assertEqual(
            resultado["productos"][0]["cantidad"], 2
        )

    def test_rechazar_cantidad_invalida(self):
        with self.assertRaises(ValueError):
            reservar_stock(
                self.db,
                "RES-002",
                "ORD-002",
                [{"producto_id": 1, "cantidad": -2}]
            )

    def test_consolidar_stock(self):
        self.db.reservas.find_one.return_value = {
            "_id": "RES-003",
            "orden_id": "ORD-003",
            "estado": "RESERVADA",
            "productos": [
                {"producto_id": 1, "cantidad": 2}
            ]
        }

        resultado = consolidar_stock(self.db, "RES-003")

        self.assertEqual(resultado["estado"], "CONSOLIDADA")
        self.db.productos.update_one.assert_called_once()

    def test_liberar_stock(self):
        self.db.reservas.find_one.return_value = {
            "_id": "RES-004",
            "orden_id": "ORD-004",
            "estado": "RESERVADA",
            "productos": [
                {"producto_id": 1, "cantidad": 2}
            ]
        }

        resultado = liberar_stock(
            self.db,
            "RES-004",
            "PAGO_RECHAZADO"
        )

        self.assertEqual(resultado["estado"], "LIBERADA")
        self.db.productos.update_one.assert_called_once()

    def test_no_consolidar_dos_veces(self):
        self.db.reservas.find_one.return_value = {
            "_id": "RES-005",
            "estado": "CONSOLIDADA"
        }

        resultado = consolidar_stock(self.db, "RES-005")

        self.assertTrue(resultado["ya_procesada"])
        self.db.productos.update_one.assert_not_called()


    def test_stock_insuficiente(self):
        self.db.reservas.find_one.return_value = None
        self.db.productos.update_one.return_value.modified_count = 0

        with self.assertRaises(ValueError):
            reservar_stock(
                self.db,
                "RES-006",
                "ORD-006",
                [{"producto_id": 1, "cantidad": 100}]
            )

        self.db.reservas.insert_one.assert_not_called()

    def test_no_liberar_reserva_consolidada(self):
        self.db.reservas.find_one.return_value = {
            "_id": "RES-007",
            "estado": "CONSOLIDADA"
        }

        with self.assertRaises(ValueError):
            liberar_stock(
                self.db,
                "RES-007",
                "PAGO_RECHAZADO"
            )

        self.db.productos.update_one.assert_not_called()

    def test_liberacion_no_modifica_stock_fisico(self):
        self.db.reservas.find_one.return_value = {
            "_id": "RES-008",
            "orden_id": "ORD-008",
            "estado": "RESERVADA",
            "productos": [
                {"producto_id": 1, "cantidad": 2}
            ]
        }

        liberar_stock(self.db, "RES-008", "PAGO_RECHAZADO")

        cambios = self.db.productos.update_one.call_args.args[1]

        self.assertEqual(
            cambios["$inc"],
            {"stock_reservado": -2}
        )

    def test_consolidacion_descuenta_ambos_stocks(self):
        self.db.reservas.find_one.return_value = {
            "_id": "RES-009",
            "orden_id": "ORD-009",
            "estado": "RESERVADA",
            "productos": [
                {"producto_id": 1, "cantidad": 2}
            ]
        }

        consolidar_stock(self.db, "RES-009")

        cambios = self.db.productos.update_one.call_args.args[1]

        self.assertEqual(
            cambios["$inc"],
            {
                "stock_fisico": -2,
                "stock_reservado": -2
            }
        )


    def test_reserva_repetida_no_duplica_stock(self):
        productos = [
            {"producto_id": 1, "cantidad": 2}
        ]

        self.db.reservas.find_one.return_value = {
            "_id": "RES-010",
            "orden_id": "ORD-010",
            "productos": productos,
            "estado": "RESERVADA"
        }

        resultado = reservar_stock(
            self.db,
            "RES-010",
            "ORD-010",
            productos
        )

        self.assertEqual(resultado["estado"], "RESERVADA")
        self.db.productos.update_one.assert_not_called()
        self.db.reservas.insert_one.assert_not_called()

    def test_reserva_duplicada_con_datos_distintos(self):
        self.db.reservas.find_one.return_value = {
            "_id": "RES-011",
            "orden_id": "ORD-011",
            "productos": [
                {"producto_id": 1, "cantidad": 2}
            ],
            "estado": "RESERVADA"
        }

        with self.assertRaises(ValueError):
            reservar_stock(
                self.db,
                "RES-011",
                "ORD-011",
                [{"producto_id": 1, "cantidad": 5}]
            )

        self.db.productos.update_one.assert_not_called()

    def test_liberacion_repetida_no_duplica_movimiento(self):
        self.db.reservas.find_one.return_value = {
            "_id": "RES-012",
            "orden_id": "ORD-012",
            "estado": "LIBERADA",
            "motivo_liberacion": "PAGO_RECHAZADO"
        }

        resultado = liberar_stock(
            self.db,
            "RES-012",
            "PAGO_RECHAZADO"
        )

        self.assertTrue(resultado["ya_procesada"])
        self.db.productos.update_one.assert_not_called()
        self.db.movimientos_inventario.insert_one.assert_not_called()

    def test_no_consolidar_reserva_liberada(self):
        self.db.reservas.find_one.return_value = {
            "_id": "RES-013",
            "estado": "LIBERADA"
        }

        with self.assertRaises(ValueError):
            consolidar_stock(self.db, "RES-013")

        self.db.productos.update_one.assert_not_called()


if __name__ == "__main__":
    unittest.main()
