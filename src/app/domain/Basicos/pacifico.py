import warnings
import pandas as pd
from pathlib import Path

from src.app.repository.configuration_repository import (
    get_pacifico_files,
    OUTPUT_PACIFICO
)


# ====================================================================================
# UTILIDADES
# ====================================================================================

def normalizar_fecha(serie: pd.Series):
    """Convierte valores a fecha estándar YYYY-MM-DD."""
    try:
        return pd.to_datetime(serie, errors="coerce").dt.strftime("%Y-%m-%d")
    except:
        return serie


def limpiar_monto(serie: pd.Series):
    """Normaliza montos tipo 1,234.56 o '--' a float."""
    return (
        serie.astype(str)
        .str.replace(",", "", regex=False)
        .str.replace("—", "0")
        .str.replace("--", "0")
        .str.replace("-", "0")
        .astype(float)
    )


def limpiar_encabezado(df: pd.DataFrame) -> pd.DataFrame:
    """
    Detecta la fila real del encabezado en los archivos Pacífico,
    la establece como encabezado del DataFrame y elimina filas/columnas basura.
    """
    header_row = None

    # Buscar la fila donde aparece "Contratante" (encabezado real)
    for i in range(min(10, len(df))):
        row = df.iloc[i].astype(str).str.lower().tolist()
        if "contratante" in row:
            header_row = i
            break

    if header_row is None:
        print("[WARN] No se pudo detectar el encabezado real. Se deja tal cual.")
        return df

    # Redefinir encabezados
    df.columns = df.iloc[header_row]

    # Eliminar filas anteriores al encabezado
    df = df.drop(index=range(0, header_row + 1))

    # Quitar columnas basura (Unnamed)
    df = df.loc[:, ~df.columns.astype(str).str.contains("unnamed", case=False)]

    # Eliminar filas basura como "TipoReporte"
    first_col = df.columns[0]
    df = df[df[first_col].astype(str).str.lower() != "tiporeporte"]

    df = df.reset_index(drop=True)
    return df


# ====================================================================================
# PROCESO PRINCIPAL: PREPARACIÓN PACÍFICO
# ====================================================================================

def preparar_pacifico():
    """
    Une los archivos Pacífico (vigente y no vigente), normaliza los datos,
    limpia encabezados y genera un archivo base listo para la integración.
    """
    print("\n" + "=" * 80)
    print(" INICIO DEL PROCESO DE PREPARACIÓN PACÍFICO")
    print("=" * 80)

    try:
        archivos = get_pacifico_files()
    except FileNotFoundError as e:
        print(f"[ERROR] {e}")
        return pd.DataFrame()

    frames = []

    for file in archivos:
        print(f"[OK] Leyendo archivo: {file.name}")

        try:
            raw_df = pd.read_excel(file, header=None, dtype=str, engine="openpyxl")
        except Exception as e:
            print(f"[ERROR] No se pudo leer {file.name}: {e}")
            continue

        # Limpieza de encabezado
        df = limpiar_encabezado(raw_df)

        # Clasificar tipo de reporte según el nombre del archivo
        f = file.name.lower()
        if "vig" in f and not "no" in f:
            tipo = "VIGENTE"
        elif "no" in f:
            tipo = "NO VIGENTE"
        else:
            tipo = "DESCONOCIDO"

        df["TipoReporte"] = tipo

        frames.append(df)

    if not frames:
        print("[ERROR] No hay archivos Pacífico válidos para procesar.")
        return pd.DataFrame()

    # Unir documentos
    df = pd.concat(frames, ignore_index=True)
    print(f"[INFO] Total registros unificados: {len(df)}")

    # ====================================================================================
    # LIMPIEZA Y NORMALIZACIÓN FINAL
    # ====================================================================================

    columnas_fecha = ["Inicio de Vigencia", "Fin de Vigencia"]
    columnas_monto = ["Prima Bruta Dolares", "Prima Bruta Soles"]

    # Normalizar fechas
    for col in columnas_fecha:
        if col in df.columns:
            df[col] = normalizar_fecha(df[col])

    # Normalizar montos
    for col in columnas_monto:
        if col in df.columns:
            df[col] = limpiar_monto(df[col])

    # Limpiar espacios solo en columnas de texto
    for col in df.columns:
        if df[col].dtype == object:
            df[col] = df[col].map(lambda x: x.strip() if isinstance(x, str) else x)

    # Asegurar limpieza de póliza
    if "Nro de Poliza/Contrato" in df.columns:
        df["Nro de Poliza/Contrato"] = df["Nro de Poliza/Contrato"].astype(str).str.strip()

    # ====================================================================================
    # GUARDAR ARCHIVO BASE
    # ====================================================================================

    OUTPUT_PACIFICO.mkdir(parents=True, exist_ok=True)
    output_path = OUTPUT_PACIFICO / "Base_Pacifico.xlsx"

    with warnings.catch_warnings():
        warnings.simplefilter("ignore")
        df.to_excel(output_path, index=False)

    print(f"\n[OK] Archivo unificado y limpio guardado en:")
    print(f"     {output_path.resolve()}")
    print("[OK] Preparación Pacífico completada exitosamente.\n")

    return df


# ====================================================================================
# EJECUCIÓN DIRECTA
# ====================================================================================

if __name__ == "__main__":
    preparar_pacifico()
