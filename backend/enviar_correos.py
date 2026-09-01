# ============================================================
# ENVIAR_CORREOS.PY
# Procesa la cola de correos pendientes.
# Se usa cuando un recibo no salio: python enviar_correos.py
# ============================================================
import sys

from app import create_app
from app.config import Config
from app.services.correo_service import CorreoService



# ---------------- Procesar la cola ----------------
# Comprueba la conexion con Gmail y manda los correos que estan pendientes
def main():
    create_app()
    servicio = CorreoService()

    print()
    print("=" * 62)
    print("  RED GOAT EYES - COLA DE CORREOS")
    print("=" * 62)
    print(f"  Servidor : {Config.SMTP_HOST}:{Config.SMTP_PUERTO}")
    print(f"  Remitente: {Config.SMTP_USUARIO}")
    print("=" * 62)
    print()

    if not servicio.configurado:
        print("  SMTP SIN CONFIGURAR")
        print("  Falta pegar la clave de aplicacion en SMTP_CLAVE de backend/.env")
        print()
        return 1

    prueba = servicio.probar_conexion()
    print(f"  Conexion: {prueba['mensaje']}")
    print()

    if not prueba.get("conectado"):
        return 1

    resumen = servicio.enviar_pendientes(limite=50)

    print(f"  Pendientes en la cola : {resumen['pendientes']}")
    print(f"  Enviados correctamente: {resumen['enviados']}")
    print(f"  Fallidos              : {resumen['fallidos']}")
    print()

    for detalle in resumen["detalles"]:
        print(f"    - {detalle}")

    print()
    return 0 if resumen["fallidos"] == 0 else 1


if __name__ == "__main__":
    sys.exit(main())