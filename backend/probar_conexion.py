import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app.config import Config
from app.database import probar_conexion, consultar_todos, consultar_valor

print()
print("=" * 60)
print("  RED GOAT EYES - Prueba de conexion")
print("=" * 60)
print()

print("Configuracion:")
for clave, valor in Config.resumen().items():
    print(f"  {clave:20} {valor}")

faltantes = Config.validar()
if faltantes:
    print()
    print("  AVISO - faltan variables en .env:", ", ".join(faltantes))

print()
estado = probar_conexion()
print("Conexion:", estado)

if not estado["conectado"]:
    print()
    print("Revisa DB_USUARIO y DB_CLAVE en backend/.env")
    sys.exit(1)

print()
print("Productos disponibles:", consultar_valor(
    "SELECT COUNT(*) FROM v_catalogo_publico WHERE disponible"))
print()

for fila in consultar_todos(
        "SELECT codigo, nombre, categoria, precio_final, stock "
        "FROM v_catalogo_publico WHERE disponible ORDER BY codigo LIMIT 5"):
    print(f"  {fila['codigo']}  {fila['nombre'][:30]:30} "
          f"{fila['categoria']:11} ${fila['precio_final']:>6}  stock={fila['stock']}")

print()
print("Ciudades cargadas:", consultar_valor("SELECT COUNT(*) FROM ciudad"))
print()
print("Todo correcto.")
print()