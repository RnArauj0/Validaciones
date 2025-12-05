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
        # Trabajar con TODAS las columnas del DataFrame original
        df_base = df.copy()

        # Convertir 'VENCIMIENTO' a datetime para poder ordenar correctamente
        if "VENCIMIENTO" in df_base.columns:
            # Solo aplicar el ordenamiento si existe la columna y al menos una fecha
            df_base["VENCIMIENTO"] = pd.to_datetime(df_base["VENCIMIENTO"], errors="coerce")
            if df_base["VENCIMIENTO"].notna().any():
                # Ordenar por fecha de más antiguo a más reciente ANTES de aplicar las siguientes condiciones
                df_base = df_base.sort_values(by="VENCIMIENTO", ascending=True, na_position="last")

        # Normalizar nro de póliza (espacios)
        if "NRO. POLIZA" in df_base.columns:
            df_base["NRO. POLIZA"] = df_base["NRO. POLIZA"].astype(str).str.strip()

        # Eliminar duplicados SOLO si los 3 campos son idénticos: RESPONSABLE DE PAGO, NRO. POLIZA y CATEGORÍA
        campos_duplicados = ["RESPONSABLE DE PAGO", "NRO. POLIZA", "CATEGORÍA"]
        campos_disponibles = [c for c in campos_duplicados if c in df_base.columns]

        # Aplicar eliminación de duplicados únicamente cuando LOS TRES campos estén presentes
        if set(campos_disponibles) == set(campos_duplicados):
            before = len(df_base)

            # No ordenar por VENCIMIENTO: conservar el orden original del archivo y mantener la primera aparición
            mask_duplicados = df_base.duplicated(subset=campos_duplicados, keep="first")
            removed = int(mask_duplicados.sum())

            # Conservar la primera ocurrencia (orden original) y eliminar el resto
            df_base = df_base.loc[~mask_duplicados].copy()

            if removed > 0:
                print(f"[INFO] Eliminados {removed} registros duplicados con 'RESPONSABLE DE PAGO', 'NRO. POLIZA' y 'CATEGORÍA' idénticos (se conserva la primera aparición).")
            else:
                print(f"[INFO] No se encontraron duplicados con los 3 campos idénticos.")
        else:
            # No tenemos los 3 campos; no eliminamos duplicados.
            print(f"[ADVERTENCIA] No se encontraron los 3 campos necesarios para eliminar duplicados. Campos disponibles: {campos_disponibles}")

        # Formatear fecha para escritura/export (si existen valores)
        if "VENCIMIENTO" in df_base.columns:
            # Asegurar que es datetime y luego formatear; no reordenamos aquí para evitar cambiar la prioridad original
            df_base["VENCIMIENTO"] = pd.to_datetime(df_base["VENCIMIENTO"], errors="coerce")
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
