# main_integraciones.py

import sys
from pathlib import Path

# ---------------------------------------------------------
# Ajustar sys.path para poder importar usando "src.app."
# ---------------------------------------------------------
project_root = Path(__file__).resolve().parents[2]
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))

# Importar los procesos de integración
from src.app.domain.Integracion.integracion_rimac import integracion_rimac
from src.app.domain.Integracion.integracion_pacifico import integracion_pacifico


def main():
    print("\n" + "=" * 80)
    print("   INICIO DEL PROCESO DE INTEGRACIÓN (RIMAC + PACÍFICO)")
    print("=" * 80)

    # -----------------------------------------------------
    # 1) Integración Rimac
    # -----------------------------------------------------
    try:
        print("\n[ BLOQUE 1/2 ] Integración Rimac")
        print("-" * 80)
        integracion_rimac()
    except Exception as e:
        print(f"\n[ERROR] Ocurrió un error en la integración de Rimac: {e}")

    # -----------------------------------------------------
    # 2) Integración Pacífico
    # -----------------------------------------------------
    try:
        print("\n[ BLOQUE 2/2 ] Integración Pacífico")
        print("-" * 80)
        integracion_pacifico()
    except Exception as e:
        print(f"\n[ERROR] Ocurrió un error en la integración de Pacífico: {e}")

    print("\n" + "=" * 80)
    print("   FIN DEL PROCESO DE INTEGRACIÓN (RIMAC + PACÍFICO)")
    print("=" * 80 + "\n")


if __name__ == "__main__":
    main()
