# anulados.py

import sys
import warnings
from pathlib import Path
import pandas as pd

# -------------------------------------------------------------------
# Ajustar sys.path para poder importar desde la raíz del proyecto
# -------------------------------------------------------------------
project_root = Path(__file__).resolve().parents[3]
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))

from src.app.repository.configuration_repository import INPUT_ANULADOS, OUTPUT_PACIFICO_ANULADO


def leer_excel_anulados(path: Path) -> pd.DataFrame:
    """Lee un Excel de anulados con el engine adecuado."""
    ext = path.suffix.lower()
    with warnings.catch_warnings():
        warnings.simplefilter("ignore")
        if ext == ".xls":
            return pd.read_excel(path, dtype=str, engine="xlrd")
        else:
            return pd.read_excel(path, dtype=str, engine="openpyxl")


def preparar_anulados():
    """
    Prepara el archivo de Anulados:
      - Lee desde INPUT_ANULADOS (Anulados.xlsx)
      - Elimina duplicados (cada póliza solo una vez, mantiene el último registro)
      - Guarda el resultado en OUTPUT_PACIFICO_ANULADO
    """
    print("\n[INICIO] Preparación de Anulados")
    print("-" * 70)

    # 1. Verificar que existe el archivo de entrada
    if not INPUT_ANULADOS.exists():
        print(f"[ERROR] No se encontró el archivo de Anulados: {INPUT_ANULADOS}")
        return

    print(f"[OK] Archivo Localizado: {INPUT_ANULADOS.name}")

    # 2. Leer el archivo
    try:
        df = leer_excel_anulados(INPUT_ANULADOS)
    except Exception as e:
        print(f"[ERROR] No se pudo leer el archivo de Anulados: {e}")
        return

    print(f"[INFO] Filas leídas: {len(df)}")

    # 3. Normalizar columnas
    df.columns = df.columns.map(str).str.strip()

    # 4. Verificar que existan las columnas necesarias
    if "Nro de Poliza/Contrato" not in df.columns:
        print("[ERROR] El archivo no contiene la columna 'Nro de Poliza/Contrato'")
        return

    # 5. Eliminar duplicados - cada póliza solo una vez (mantener el último registro)
    filas_antes = len(df)
    df_limpio = df.drop_duplicates(subset=["Nro de Poliza/Contrato"], keep="last")
    filas_despues = len(df_limpio)
    duplicados_eliminados = filas_antes - filas_despues

    print(f"[INFO] Pólizas únicas: {filas_despues}")
    print(f"[INFO] Duplicados eliminados: {duplicados_eliminados}")

    # 6. Guardar en OUTPUT_PACIFICO_ANULADO
    OUTPUT_PACIFICO_ANULADO.mkdir(parents=True, exist_ok=True)
    output_path = OUTPUT_PACIFICO_ANULADO / "Anulados_preparado.xlsx"

    try:
        with warnings.catch_warnings():
            warnings.simplefilter("ignore")
            with pd.ExcelWriter(output_path, engine="openpyxl") as writer:
                df_limpio.to_excel(writer, index=False, sheet_name="Anulados")
        print(f"[OK] Archivo preparado guardado: {output_path}")
    except Exception as e:
        print(f"[ERROR] No se pudo guardar el archivo preparado: {e}")
        return

    print("[OK] Preparación de Anulados completada")
    print("-" * 70)


if __name__ == "__main__":
    preparar_anulados()

