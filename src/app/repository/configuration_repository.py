"""
configuration_repository.py
----------------------------
Define las rutas base y funciones para localizar los archivos más recientes
de cada fuente (SICS, SharePoint, Rimac, Pacífico) sin depender de nombres específicos.

FLUJO DE PROCESAMIENTO:
  1. PreparaciónPacífico/ (INPUT)   → preparar_pacifico() → OUTPUT_PACIFICO/Base_Pacifico.xlsx
  2. PreparaciónSics/ (INPUT)       → preparar_sics()     → output/
  3. PreparaciónSharepoint/ (INPUT) → preparar_sharepoint() → output/
  4. OUTPUT_PACIFICO/Base_Pacifico.xlsx + otros → integracion_pacifico() → OUTPUT_PACIFICO_INTEGRADO/
"""

from pathlib import Path

# === RUTAS BASE ===
BASE_DIR = Path(__file__).resolve().parents[3]  # Ajusta el nivel hasta llegar a GestorDeValidaciones
DATA_DIR = BASE_DIR / "src" / "app" / "data"
INPUT_DIR = DATA_DIR / "input"
OUTPUT_DIR = DATA_DIR / "output"

# === RUTAS DE ENTRADA (Preparación) ===
PATH_SICS_INPUT = INPUT_DIR / "PreparaciónSics"
PATH_SHAREPOINT_INPUT = INPUT_DIR / "PreparaciónSharepoint"
PATH_RIMAC_INPUT = INPUT_DIR / "PreparaciónRimac"
PATH_PACIFICO_INPUT = INPUT_DIR / "PreparaciónPacífico"
INPUT_ANULADOS = PATH_PACIFICO_INPUT / "Anulados" / "Anulados.xlsx"

# === RUTAS DE SALIDA ===
OUTPUT_RIMAC = OUTPUT_DIR / "Rimac"
OUTPUT_PACIFICO = OUTPUT_DIR / "Pacífico"
OUTPUT_PACIFICO_INTEGRADO = OUTPUT_DIR / "PacíficoIntegrado"
OUTPUT_PACIFICO_ANULADO = OUTPUT_PACIFICO / "PacificoAnulado"


def get_pacifico_file() -> Path:
    """Obtiene el archivo preparado de Pacífico (Base_Pacifico.xlsx) desde OUTPUT_PACIFICO."""
    return get_latest_file(OUTPUT_PACIFICO)

def get_latest_file(folder: Path, extensions: tuple = (".xlsx", ".xls")) -> Path:
    """
    Devuelve el archivo más reciente dentro de la carpeta especificada.
    Si no encuentra archivos compatibles, lanza FileNotFoundError.
    """
    files = []
    for ext in extensions:
        files.extend(Path(folder).glob(f"*{ext}"))

    if not files:
        raise FileNotFoundError(f"No se encontró ningún archivo en {folder}")

    latest = max(files, key=lambda f: f.stat().st_mtime)
    return latest


# === ACCESOS PARA ARCHIVOS DE ENTRADA (Preparación) ===

def get_sics_file() -> Path:
    """Obtiene el archivo más reciente en la carpeta de entrada SICS."""
    return get_latest_file(PATH_SICS_INPUT)


def get_sharepoint_file() -> Path:
    """Obtiene el archivo más reciente en la carpeta de entrada SharePoint."""
    return get_latest_file(PATH_SHAREPOINT_INPUT)


def get_rimac_file() -> Path:
    """Obtiene el archivo más reciente en la carpeta de entrada Rimac."""
    return get_latest_file(PATH_RIMAC_INPUT)


def get_pacifico_files() -> list[Path]:
    """Obtiene todos los archivos Pacífico encontrados en la carpeta de entrada (vigente y no vigente)."""
    files = list(PATH_PACIFICO_INPUT.glob("*.xlsx"))
    if not files:
        raise FileNotFoundError(f"No se encontraron archivos Pacífico en {PATH_PACIFICO_INPUT}")
    return files
