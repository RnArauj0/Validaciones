import pandas as pd
from datetime import datetime
import warnings
from src.app.repository.configuration_repository import get_rimac_file
from src.app.repository.mapping_repository import MAPEO

def preparar_rimac():
    # ---------------------------------------------------------
    # 1️⃣ Obtener el archivo más reciente
    # ---------------------------------------------------------

    try:
        file_path = get_rimac_file()
        print(f"[OK] Archivo localizado: {file_path}")
    except Exception as e:
        print(f"No se pudo obtener el archivo: {e}")
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
            sheet_candidates = [s for s in xls.sheet_names if any(k in s.lower() for k in ["pagosvencidos", "pagos", "rimac"])]
            target_sheet = sheet_candidates[0] if sheet_candidates else xls.sheet_names[0]

        print(f"[INFO] Hoja detectada: '{target_sheet}'")

        # lEER HOJA SELECCIONADA
        df = pd.read_excel(file_path, sheet_name=target_sheet, dtype=str, engine=engine)
        df.columns = df.columns.map(str).str.strip()
        print(f"[OK] Archivo leído correctamente ({len(df)} filas, {len(df.columns)} columnas)")

    except Exception as e:
        print(f"Error al leer el archivo Excel: {e}")
        return
    # ---------------------------------------------------------
    # 3️⃣ Validación de columnas esperadas
    # ---------------------------------------------------------
    columnas_esperadas = MAPEO.get("Tablero_RIMAC", [])
    columnas_faltantes = [c for c in columnas_esperadas if c not in df.columns]

    if columnas_faltantes:
        print(f"[ERROR] Faltan columnas esperadas: {columnas_faltantes}")

    else:
        print(f"[OK] Todas las columnas esperadas fueron detectadas.")

    # ---------------------------------------------------------
    # 4️⃣ Limpieza y normalización de datos
    # ---------------------------------------------------------
    try:
        # Mantener solo columnas clave (si existen)
        columnas_principales = [c for c in ["RESPONSABLE DE PAGO", "NRO. POLIZA", "CATEGORÍA", "VENCIMIENTO"] if
                                c in df.columns]
        df_base = df[columnas_principales].copy()

        # Convertir 'VENCIMIENTO' a datetime para poder ordenar correctamente
        if "VENCIMIENTO" in df_base.columns:
            df_base["VENCIMIENTO"] = pd.to_datetime(df_base["VENCIMIENTO"], errors="coerce")

        # Normalizar nro de póliza (espacios)
        if "NRO. POLIZA" in df_base.columns:
            df_base["NRO. POLIZA"] = df_base["NRO. POLIZA"].astype(str).str.strip()

        # Eliminar duplicados por número de póliza: conservar la más antigua
        if "NRO. POLIZA" in df_base.columns:
            before = len(df_base)
            # Ordenar por póliza y vencimiento ascendente (NaT al final) para que 'first' sea la más antigua
            sort_cols = ["NRO. POLIZA"]
            if "VENCIMIENTO" in df_base.columns:
                sort_cols.append("VENCIMIENTO")
                df_base = df_base.sort_values(by=sort_cols, ascending=[True, True], na_position="last")
            else:
                df_base = df_base.sort_values(by="NRO. POLIZA", ascending=True)

            df_base = df_base.drop_duplicates(subset=["NRO. POLIZA"], keep="first")
            removed = before - len(df_base)
            if removed > 0:
                print(
                    f"[INFO] Eliminados {removed} registros duplicados por 'NRO. POLIZA' (se conserva la más antigua).")

        # Ordenar por vencimiento para salida si existe
        if "VENCIMIENTO" in df_base.columns:
            df_base = df_base.sort_values(by="VENCIMIENTO", ascending=True, na_position="last")
            # Formatear fecha para escritura/export
            df_base["VENCIMIENTO"] = df_base["VENCIMIENTO"].dt.strftime("%Y-%m-%d")

        print(f"[OK] Datos limpiados y ordenados. Total final: {len(df_base)} filas.")

    except Exception as e:
        print(f"[ERROR] Error durante la limpieza o normalización: {e}")
        return

    # ---------------------------------------------------------
    # 5️⃣ Guardar los cambios en el mismo archivo
    # ---------------------------------------------------------
    try:
        print(f"[INFO] Guardando los cambios en: {file_path.resolve()}")
        with pd.ExcelWriter(file_path, engine="openpyxl", mode="a", if_sheet_exists="replace") as writer:
            # ⬅️ aquí usamos la misma hoja desde la que leímos
            df_base.to_excel(writer, index=False, sheet_name=target_sheet)

        print(f"✅ Archivo actualizado correctamente en: {file_path.resolve()}")

        # Verificación post-escritura
        check_df = pd.read_excel(file_path, sheet_name=target_sheet, engine="openpyxl")
        print(f"[VERIFICACIÓN] Hoja '{target_sheet}' guardada correctamente con {len(check_df)} filas y {len(check_df.columns)} columnas.")

    except Exception as e:
        print(f"❌ Error al guardar los cambios en el archivo: {e}")
        return

    # ---------------------------------------------------------
    # 6️⃣ Resumen del proceso
    # ---------------------------------------------------------
    print("\n📋 Resumen del proceso Rimac:")
    print(f"   Total de filas procesadas: {len(df_base)}")
    print(f"   Columnas finales: {list(df_base.columns)}")
    print(f"   Última modificación: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("--------------------------------------------------------------")
    print("✅ Proceso de preparación Rimac finalizado correctamente.\n")


# Punto de ejecución directa
if __name__ == "__main__":
    preparar_rimac()
























