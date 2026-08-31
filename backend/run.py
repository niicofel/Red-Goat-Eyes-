from app import create_app
from app.config import Config

app = create_app()

if __name__ == "__main__":
    faltantes = Config.validar()
    if faltantes:
        print()
        print("AVISO: faltan variables en backend/.env ->", ", ".join(faltantes))
        print()

    print()
    print("=" * 60)
    print("  RED GOAT EYES")
    print("=" * 60)
    print(f"  Sitio : http://{Config.FLASK_HOST}:{Config.FLASK_PUERTO}/")
    print(f"  API   : http://{Config.FLASK_HOST}:{Config.FLASK_PUERTO}/api/salud")
    print(f"  Base  : {Config.resumen()['base_de_datos']}")
    print("=" * 60)
    print()

    app.run(host=Config.FLASK_HOST, port=Config.FLASK_PUERTO,
            debug=Config.DEBUG, use_reloader=Config.DEBUG)