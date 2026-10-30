db = db.getSiblingDB('catalogo_db');

// Limpiamos la colección para evitar duplicados 
db.productos.drop();

const productosPrincipales = [
  { "id": 1, "nombre": "Silla ergonomica X-fire negra", "descripcion": "Silla ergonómica ideal para largas sesiones de juego o trabajo.", "precio": 150000, "categoria": "Muebles", "stock": { "reservado": 0, "disponible": 10 }, "activo": true, "imagenes": ["silla1.jpg", "silla2.jpg", "silla3.jpg"] },
  { "id": 2, "nombre": "Teclado mecanico Redragon K552 Kumara", "descripcion": "Teclado mecanico con switches rojos para una experiencia de escritura óptima.", "precio": 80000, "categoria": "Perifericos", "stock": { "reservado": 2, "disponible": 8 }, "activo": true, "imagenes": ["tec1.jpg", "tec2.jpg", "tec3.jpg"] },
  { "id": 3, "nombre": "mouse gamer Logitech G502 HERO", "descripcion": "Mouse gaming con sensor de alta precisión y botones programables.", "precio": 450000, "categoria": "Perifericos", "stock": { "reservado": 1, "disponible": 9 }, "activo": true, "imagenes": ["m1.jpg", "m2.jpg", "m3.jpg"] },
  { "id": 4, "nombre": "Monitor Gamer 144Hz IPS 24\"", "precio": 150000, "stock": { "disponible": 15, "reservado": 0 }, "activo": true, "imagenes": ["mon1.jpg", "mon2.jpg", "mon3.jpg"] },
  { "id": 5, "nombre": "Monitor Ultrawide 34\"", "precio": 320000, "stock": { "disponible": 5, "reservado": 1 }, "activo": true, "imagenes": ["uw1.jpg", "uw2.jpg", "uw3.jpg"] },
  { "id": 6, "nombre": "Audífonos Inalámbricos", "precio": 85000, "stock": { "disponible": 20, "reservado": 2 }, "activo": true, "imagenes": ["aud1.jpg", "aud2.jpg", "aud3.jpg"] },
  { "id": 7, "nombre": "Mousepad XXL RGB", "precio": 25000, "stock": { "disponible": 50, "reservado": 0 }, "activo": true, "imagenes": ["mp1.jpg", "mp2.jpg", "mp3.jpg"] },
  { "id": 8, "nombre": "Escritorio Regulable", "precio": 210000, "stock": { "disponible": 8, "reservado": 0 }, "activo": true, "imagenes": ["esc1.jpg", "esc2.jpg", "esc3.jpg"] },
  { "id": 9, "nombre": "Micrófono Condensador USB", "precio": 65000, "stock": { "disponible": 12, "reservado": 0 }, "activo": true, "imagenes": ["mic1.jpg", "mic2.jpg", "mic3.jpg"] },
  { "id": 10, "nombre": "Brazo Articulado", "precio": 18000, "stock": { "disponible": 30, "reservado": 0 }, "activo": true, "imagenes": ["brazo1.jpg", "brazo2.jpg", "brazo3.jpg"] },
  { "id": 11, "nombre": "Webcam 1080p 60fps", "precio": 55000, "stock": { "disponible": 0, "reservado": 0 }, "activo": true, "imagenes": ["cam1.jpg", "cam2.jpg", "cam3.jpg"] }, 
  { "id": 12, "nombre": "Aro de Luz LED", "precio": 15000, "stock": { "disponible": 25, "reservado": 0 }, "activo": true, "imagenes": ["aro1.jpg", "aro2.jpg", "aro3.jpg"] },
  { "id": 13, "nombre": "Soporte Doble Monitores", "precio": 45000, "stock": { "disponible": 10, "reservado": 0 }, "activo": true, "imagenes": ["sop1.jpg", "sop2.jpg", "sop3.jpg"] },
  { "id": 14, "nombre": "Silla Mesh Oficina", "precio": 130000, "stock": { "disponible": 6, "reservado": 0 }, "activo": true, "imagenes": ["sillam1.jpg", "sillam2.jpg", "sillam3.jpg"] },
  { "id": 15, "nombre": "Teclado Mecánico TKL Red", "precio": 60000, "stock": { "disponible": 18, "reservado": 3 }, "activo": true, "imagenes": ["tecl2_1.jpg", "tecl2_2.jpg", "tecl2_3.jpg"] },
  { "id": 16, "nombre": "Mouse Superligero 60g", "precio": 45000, "stock": { "disponible": 22, "reservado": 0 }, "activo": true, "imagenes": ["mous2_1.jpg", "mous2_2.jpg", "mous2_3.jpg"] },
  { "id": 17, "nombre": "Cable Extensión Sleeved PC", "precio": 22000, "stock": { "disponible": 40, "reservado": 0 }, "activo": true, "imagenes": ["cab1.jpg", "cab2.jpg", "cab3.jpg"] },
  { "id": 18, "nombre": "Gabinete ATX Flujo de Aire", "precio": 75000, "stock": { "disponible": 0, "reservado": 0 }, "activo": true, "imagenes": ["gab1.jpg", "gab2.jpg", "gab3.jpg"] }, 
  { "id": 19, "nombre": "Kit Ventiladores ARGB", "precio": 35000, "stock": { "disponible": 15, "reservado": 0 }, "activo": true, "imagenes": ["vent1.jpg", "vent2.jpg", "vent3.jpg"] },
  { "id": 20, "nombre": "Hub USB-C 7 en 1", "precio": 28000, "stock": { "disponible": 35, "reservado": 0 }, "activo": false, "imagenes": ["hub1.jpg", "hub2.jpg", "hub3.jpg"] }
];

db.productos.insertMany(productosPrincipales);
print("Base de datos poblada exitosamente  .");