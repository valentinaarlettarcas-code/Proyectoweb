// Seleccionar la base de datos
db = db.getSiblingDB('catalogo_db');

// Limpiar la colección por si se ejecuta más de una vez
db.productos.drop();

// Insertar los productos reales en la base de datos
db.productos.insertMany([
  {
    "id": 1,
    "nombre": "Silla ergonomica X-fire negra",
    "descripcion": "Silla ergonómica ideal para largas sesiones de juego o trabajo.",
    "precio": 150000,
    "categoria": "Muebles",
    "stock": { "reservado": 0, "disponible": 10 },
    "activo": true
  },
  {
    "id": 2,
    "nombre": "Teclado mecanico Redragon K552 Kumara",
    "descripcion": "Teclado mecanico con switches rojos para una experiencia de escritura óptima.",
    "precio": 80000,
    "categoria": "Perifericos",
    "stock": { "reservado": 2, "disponible": 8 },
    "activo": true
  },
  {
    "id": 3,
    "nombre": "mouse gamer Logitech G502 HERO",
    "descripcion": "Mouse gaming con sensor de alta precisión y botones programables.",
    "precio": 450000,
    "categoria": "Perifericos",
    "stock": { "reservado": 1, "disponible": 9 },
    "activo": true
  }
]);

print(" Base de datos poblada exitosamente.");