import warnings

import pandas as pd
from datetime import datetime
from src.app.repository.configuration_repository import get_sharepoint_file
from src.app.repository.mapping_repository import MAPEO

def preparar_sharepoint():

    try:
        file_path = get_sharepoint_file()
        print(f"[OK] Archivo localizado: {file_path.name}")
    except Exception as e:
        print(f"❌ No se encontró archivo de entrada en la carpeta SharePoint: {e}")
        return

    # ---------------------------------------------------------
    # 2️⃣ Detección de hoja correcta
    # ---------------------------------------------------------
    try:
        ext = file_path.suffix.lower()
        engine = "xlrd" if ext == ".xls" else "openpyxl"

        with warnings.catch_warnings():
            warnings.simplefilter("ignore")
            xls = pd.ExcelFile(file_path, engine=engine)
            sheet_candidates = [s for s in xls.sheet_names if
                                any(k in s.lower() for k in ["tablero", "renovaciones", "poliza"])]
            target_sheet = sheet_candidates[0] if sheet_candidates else xls.sheet_names[0]

        print(f"[INFO] Hoja detectada: '{target_sheet}'")

        # Leer hoja seleccionada
        df = pd.read_excel(file_path, sheet_name=target_sheet, dtype=str, engine=engine)
        df.columns = df.columns.map(str).str.strip()
        print(f"[OK] Archivo leído correctamente ({len(df)} filas, {len(df.columns)} columnas)")

    except Exception as e:
        print(f"❌ Error al leer el archivo SharePoint: {e}")
        return
    # ---------------------------------------------------------
    # 3️⃣ Validación de columnas esperadas
    # ---------------------------------------------------------
    columnas_esperadas = MAPEO.get("Tablero_sharepoint", [])
    columnas_faltantes = [c for c in columnas_esperadas if c not in df.columns]

    if columnas_faltantes:
        print(f"Advertencia: faltan columnas esperadas: {columnas_faltantes}")
    else:
        print("[OK] Todas las columnas esperadas fueron detectadas.")

    # ---------------------------------------------------------
    # 4️⃣ Creación / actualización de columnas derivadas
    # ---------------------------------------------------------
    try:
        if "Pólizafinal" not in df.columns:
            print("No se encontró columna 'Pólizafinal'. No se puede generar pacifico/rimac.")
            return

        df["Pólizafinal"] = df["Pólizafinal"].astype(str).str.strip()

        # Eliminar versiones viejas de columnas
        for col in ["Pacifico", "Rimac"]:
            if col in df.columns:
                df.drop(columns=[col], inplace=True)

        # Pacifico
        # Copia directa de 'Polizafinal'
        df["Pacifico"] = df["Pólizafinal"]

        # Rimac
        # Reemplazo de prefijos
        df["Rimac"] = df["Pólizafinal"].apply(
            lambda x: x.split("-")[-1] if "-" in x else x
        )

        print("[OK] columnas derivadas creadas/actualizadas correctamente: Pacifico, Rimac")

    except Exception as e:
        print(f"[ERROR] Error durante la creación de columnas derivadas: {e}")
        return
    # ---------------------------------------------------------
    # 5️⃣ Guardar los cambios en el mismo archivo
    # ---------------------------------------------------------
    try:
        print(f"[INFO] Guardando los cambios en: {file_path.resolve()}")
        with pd.ExcelWriter(file_path, engine="openpyxl", mode="w") as writer:
            df.to_excel(writer, index=False, sheet_name=target_sheet)
        print(f"Archivo actualizado correctamente en: {file_path.resolve()}")


        # Verificacion post - escritura
        check_df = pd.read_excel(file_path, sheet_name=target_sheet, engine="openpyxl")
        added_cols = [c for c in ["Pacifico", "Rimac"] if c in check_df.columns]
        print(f"[VERIFICACIÓN] Columnas en el archivo guardado: {added_cols}")

    except Exception as e:
        print(f"Error al guardar los cambios en el archivo SharePoint: {e}")
        return

    # ---------------------------------------------------------
    # 6️⃣ Resumen del proceso
    # ---------------------------------------------------------
    print("\n📋 Resumen del proceso SharePoint:")
    print(f"   Total de filas: {len(df)}")
    print(f"   Columnas totales: {len(df.columns)}")
    print(f"   Columnas creadas o actualizadas: ['Pacifico', 'Rimac']")
    print(f"   Última modificación: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("--------------------------------------------------------------")
    print("✅ Proceso de preparación SharePoint finalizado correctamente.\n")


# Punto de ejecución directa
if __name__ == "__main__":
    preparar_sharepoint()




















