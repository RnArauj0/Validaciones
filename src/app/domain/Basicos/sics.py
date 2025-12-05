import pandas as pd
from datetime import datetime
import warnings
from src.app.repository.configuration_repository import get_sics_file
from src.app.repository.mapping_repository import MAPEO

def preparar_sics():

    try:
        file_path = get_sics_file()
        print(f"[OK] Archivo Localizado: {file_path.name}")
    except Exception as e:
        print(f"[ERROR] No se pudo localizar el archivo de SICS: {e}")
        return

    try:
        ext = file_path.suffix.lower()
        engine = "xlrd" if ext == ".xls" else "openpyxl"

        with warnings.catch_warnings():
            warnings.simplefilter("ignore")
            # Leer sin dtype=str para que las fechas se lean correctamente
            df = pd.read_excel(file_path, engine=engine)

        df.columns = df.columns.map(str).str.strip()
        print(f"[OK] Archivo leído correctamente ({len(df)} filas, {len(df.columns)} columnas)")

    except Exception as e:
        print(f"[ERROR] No se pudo leer el archivo de SICS: {e}")
        return

    # Obtener columnas esperadas del mapeo (sin incluir las columnas derivadas)
    columnas_esperadas = [c for c in MAPEO["Tablero_SICS"] if c not in ["Pacifico", "Rimac", "Fin Vig"]]
    columnas_faltantes = [c for c in columnas_esperadas if c not in df.columns]

    if columnas_faltantes:
        print(f"⚠️  Advertencia: faltan columnas esperadas: {columnas_faltantes}")
    else:
        print("[OK] Todas las columnas base están completas.")

    try:
        # Normalizar campo base "Póliza"
        if "Póliza" not in df.columns:
            print("❌ No se encontró la columna base 'Póliza'. No se puede generar Pacifico/Rimac.")
            return

        df["Póliza"] = df["Póliza"].astype(str).str.strip()

        # Eliminar versiones viejas de las columnas (para evitar conflictos)
        for col in ["Pacifico", "Rimac", "Fin Vig"]:
            if col in df.columns:
                df.drop(columns=[col], inplace=True)

        # --- Pacifico ---
        # Copia directa de 'Póliza' (sin alteraciones)
        df["Pacifico"] = df["Póliza"]

        # --- Rimac ---
        # Toma la parte después del guion (-), si no lo tiene quedaría igual
        df["Rimac"] = df["Póliza"].apply(
            lambda x: x.split("-")[-1] if "-" in x else x
        )

        # --- Fin Vig ---
        # Convierte el formato de fecha de "01/09/2025" a "2025-09"
        if "Vig Hasta Póliza" in df.columns:
            # Convertir a datetime con diferentes formatos posibles
            fecha_convertida = pd.to_datetime(df["Vig Hasta Póliza"], errors="coerce", dayfirst=True)

            # Verificar cuántas fechas se convirtieron exitosamente
            fechas_validas = fecha_convertida.notna().sum()
            fechas_totales = len(df)
            print(f"[INFO] Fechas válidas convertidas: {fechas_validas}/{fechas_totales}")

            # Formatear a "YYYY-MM"
            df["Fin Vig"] = fecha_convertida.dt.strftime("%Y-%m").fillna("")

            # Mostrar muestra de conversión
            if fechas_validas < fechas_totales:
                print(f"⚠️  {fechas_totales - fechas_validas} fechas no pudieron ser convertidas")
        else:
            print("⚠️  No se encontró la columna 'Vig Hasta Póliza'. No se generará 'Fin Vig'.")

        print("[OK] Columnas derivadas creadas/actualizadas: Pacifico, Rimac, Fin Vig")

    except Exception as e:
        print(f"[ERROR] Error durante la creación de columnas derivadas: {e}")
        return

    try:
        print(f"[INFO] Guardando los cambios en: {file_path.resolve()}")
        with pd.ExcelWriter(file_path, engine="openpyxl", mode="w") as writer:
            df.to_excel(writer, index=False)
        print(f"✅ Archivo actualizado correctamente en: {file_path.resolve()}")

        # Verificación post-escritura
        check_df = pd.read_excel(file_path, engine="openpyxl")
        added_cols = [c for c in ["Pacifico", "Rimac", "Fin Vig"] if c in check_df.columns]
        print(f"[VERIFICACIÓN] Columnas en el archivo guardado: {added_cols}")

    except Exception as e:
        print(f"❌ Error al guardar los cambios en el archivo: {e}")
        return

    print("\n📋 Resumen del proceso SICS:")
    print(f"   Total de filas: {len(df)}")
    print(f"   Columnas totales: {len(df.columns)}")
    print(f"   Columnas creadas o actualizadas: ['Pacifico', 'Rimac', 'Fin Vig']")
    print(f"   Última modificación: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("--------------------------------------------------------------")
    print("✅ Proceso de preparación SICS finalizado correctamente.\n")


if __name__ == "__main__":
    preparar_sics()




















