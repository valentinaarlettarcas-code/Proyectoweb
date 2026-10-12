db = db.getSiblingDB('catalogo_db');
db.productos.createIndex({ "id": 1 }, { unique: true });
db.productos.createIndex({ "categoria": 1 });
print(" Índices de optimización creados.");