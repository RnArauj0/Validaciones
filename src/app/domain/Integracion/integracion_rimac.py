# Integración de Rimac
import pandas as pd
from datetime import datetime, timedelta
import warnings
from pathlib import Path
import sys

from src.app.repository.configuration_repository import (
    get_sics_file,
    get_sharepoint_file,
    get_rimac_file,
    OUTPUT_RIMAC
)
from src.app.repository.mapping_repository import MAPEO

# Importar funciones de preparación
from src.app.domain.Basicos.sics import preparar_sics
from src.app.domain.Basicos.sharepoint import preparar_sharepoint
from src.app.domain.Basicos.rimac import preparar_rimac

# Añadir la raíz del proyecto al sys.path (ajusta parents[n] si la estructura cambia)
project_root = Path(__file__).resolve().parents[2]
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))

# ============================================================
# Funciones auxiliares
# ============================================================

def asignar_responsable(categoria: str) -> str:
    """Devuelve el responsable según la categoría usando el mapeo de responsables."""
    categoria = str(categoria).strip().upper()
    for responsable, categorias in MAPEO.get("Responsables", {}).items():
        if categoria in [c.upper() for c in categorias]:
            return responsable
    return ""


def calc_obs(vencimiento, sics_val, tablero_val):
    """
    Reglas del OBS:
      1 -> sics no encontrado y tablero no encontrado
      2 -> sics(YYYY-MM) <= vencimiento(YYYY-MM)
      6 -> resto de casos
    """
    # Normalizar valores
    s = str(sics_val).strip() if pd.notna(sics_val) else ""
    t = str(tablero_val).strip() if pd.notna(tablero_val) else ""

    def es_no_encontrado(x: str) -> bool:
        xl = x.strip().lower()
        return xl in ("", "no encontrado", "nan")

    # 1️⃣ Caso OBS = 1
    if es_no_encontrado(s) and es_no_encontrado(t):
        return 1

    # 2️⃣ Si SICS está vacío → OBS = 6
    if es_no_encontrado(s):
        return 6

    # Preparar YYYY-MM
    v_ym = str(vencimiento)[:7] if pd.notna(vencimiento) else ""
    s_ym = s[:7]

    # 3️⃣ Condición exacta:
    #     sics <= vencimiento
    try:
        return 2 if s_ym and s_ym <= v_ym else 6
    except:
        return 6


# ============================================================
# Proceso principal de integración
# ============================================================

def integracion_rimac():
    """Ejecuta el proceso completo de integración Rimac."""
    print("\n" + "="*70)
    print("[INICIO] Proceso Completo de Integración Rimac")
    print("="*70)

    # ============================================================
    # PASO 0: Ejecutar scripts de preparación secuencialmente
    # ============================================================
    print("\n[ETAPA 1/4] Preparación de datos SICS")
    print("-" * 70)
    try:
        preparar_sics()
    except Exception as e:
        print(f"[ERROR] Fallo en la preparación de SICS: {e}")
        return

    print("\n[ETAPA 2/4] Preparación de datos SharePoint")
    print("-" * 70)
    try:
        preparar_sharepoint()
    except Exception as e:
        print(f"[ERROR] Fallo en la preparación de SharePoint: {e}")
        return

    print("\n[ETAPA 3/4] Preparación de datos Rimac")
    print("-" * 70)
    try:
        preparar_rimac()
    except Exception as e:
        print(f"[ERROR] Fallo en la preparación de Rimac: {e}")
        return

    # ============================================================
    # PASO 1: Integración de datos
    # ============================================================
    print("\n[ETAPA 4/4] Integración y Match de datos")
    print("-" * 70)

    # 1) Localizar archivos
    try:
        path_sics = get_sics_file()
        path_sharepoint = get_sharepoint_file()
        path_rimac = get_rimac_file()
        print("[OK] Archivos detectados:")
        print(f"   SICS       → {path_sics.name}")
        print(f"   SharePoint → {path_sharepoint.name}")
        print(f"   Rimac      → {path_rimac.name}")
    except Exception as e:
        print(f"[ERROR] Localizando archivos: {e}")
        return

    # 2) Lectura
    def leer_excel(path: Path):
        ext = path.suffix.lower()
        engine = "xlrd" if ext == ".xls" else "openpyxl"
        with warnings.catch_warnings():
            warnings.simplefilter("ignore")
            return pd.read_excel(path, dtype=str, engine=engine)

    try:
        sics_df = leer_excel(path_sics)
        share_df = leer_excel(path_sharepoint)
        rimac_df = leer_excel(path_rimac)
    except Exception as e:
        print(f"[ERROR] Leyendo Excels: {e}")
        return

    print(f"[INFO] Filas: SICS={len(sics_df)} | SharePoint={len(share_df)} | Rimac={len(rimac_df)}")

    # 3) Validación mínima
    checks = [
        ("SICS", sics_df, ["Rimac", "Fin Vig"]),
        ("SharePoint", share_df, ["Rimac", "STATUS RENOVACION"]),
        ("Rimac", rimac_df, ["RESPONSABLE DE PAGO", "NRO. POLIZA", "CATEGORÍA", "VENCIMIENTO"]),
    ]
    for name, df, req in checks:
        faltantes = [c for c in req if c not in df.columns]
        if faltantes:
            print(f"[WARN] {name}: faltan columnas {faltantes}")

    # 4) Normalización de llaves y columnas
    for df in (sics_df, share_df, rimac_df):
        df.columns = df.columns.map(str).str.strip()

    sics_df["Rimac"] = sics_df["Rimac"].astype(str).str.strip()
    share_df["Rimac"] = share_df["Rimac"].astype(str).str.strip()
    rimac_df["NRO. POLIZA"] = rimac_df["NRO. POLIZA"].astype(str).str.strip()

    # 5) Match
    print("[INFO] Match de datos...")
    base = rimac_df.copy()

    # SICS: NRO. POLIZA (Rimac) -> Fin Vig (YYYY-MM)
    sics_map = sics_df.drop_duplicates("Rimac").set_index("Rimac")["Fin Vig"]
    base["SICS"] = base["NRO. POLIZA"].map(sics_map).fillna("No Encontrado")

    # Tablero: NRO. POLIZA (Rimac) -> STATUS RENOVACION
    shp_map = share_df.drop_duplicates("Rimac").set_index("Rimac")["STATUS RENOVACION"]
    base["Tablero"] = base["NRO. POLIZA"].map(shp_map).fillna("No Encontrado")

    print("[OK] Match completado")

    # 6) Columnas calculadas
    # Responsable primero (para excepción de rango con Jesús)
    base["Responsable"] = base["CATEGORÍA"].apply(asignar_responsable)
    # Obs por regla de fechas
    base["Obs"] = base.apply(lambda r: calc_obs(r["VENCIMIENTO"], r["SICS"], r["Tablero"]), axis=1)
    # Observaciones según mapeo de Comentario (1, 2, 6 → texto)
    comentarios = MAPEO.get("Comentario", {})
    base["Observaciones"] = base["Obs"].map(comentarios).fillna("")

    # 7) Rango temporal (marcar, no filtrar)
    hoy = datetime.today()
    mes_actual = hoy.strftime("%Y-%m")
    mes_anterior = (hoy - timedelta(days=30)).strftime("%Y-%m")
    mes_siguiente = (hoy + timedelta(days=30)).strftime("%Y-%m")

    def dentro_de_rango(row):
        s = str(row["SICS"]).strip()
        t = str(row["Tablero"]).strip()

        # Si tanto SICS como Tablero son "No Encontrado", marcar como "Sí"
        if s == "No Encontrado" and t == "No Encontrado":
            return "Sí"

        # Si SICS está vacío o es "No Encontrado", marcar como "No"
        if s in ("", "No Encontrado", "nan"):
            return "No"

        # Tomar solo YYYY-MM de SICS
        s = s[:7]

        # Aplicar regla especial para Jesús (mes anterior y actual)
        if str(row["Responsable"]).strip().upper() == "JESUS":
            return "Sí" if s in (mes_anterior, mes_actual) else "No"

        # Para otros responsables (mes anterior, actual y siguiente)
        return "Sí" if s in (mes_anterior, mes_actual, mes_siguiente) else "No"

    base["DentroRango"] = base.apply(dentro_de_rango, axis=1)

    # 8) Reordenar y exportar
    columnas_finales = [
        "RESPONSABLE DE PAGO",
        "NRO. POLIZA",
        "CATEGORÍA",
        "VENCIMIENTO",
        "SICS",
        "Tablero",
        "Observaciones",
        "Responsable",
        "Obs",
        "DentroRango",
    ]
    df_final = base[columnas_finales].copy()

    OUTPUT_RIMAC.mkdir(parents=True, exist_ok=True)
    output_path = OUTPUT_RIMAC / f"Reporte-polizas_Rimac_{datetime.now().strftime('%Y-%m-%d')}.xlsx"

    try:
        with pd.ExcelWriter(output_path, engine="openpyxl") as writer:
            df_final.to_excel(writer, index=False, sheet_name="MatchRimac")
        print(f"[OK] Archivo generado: {output_path}")
    except Exception as e:
        print(f"[ERROR] Guardando archivo final: {e}")
        return

    # 9) Resumen
    total = len(df_final)
    en_rango = (df_final["DentroRango"] == "Sí").sum()
    print("\n" + "="*70)
    print("[RESUMEN FINAL] Integración Rimac Completada")
    print("="*70)
    print(f"  Total de pólizas procesadas: {total}")
    print(f"  Pólizas en rango de vigencia: {en_rango}")
    print(f"  Pólizas fuera de rango: {total - en_rango}")
    print(f"  Archivo generado: {output_path.name}")
    print("="*70)
    print("✅ Proceso completo finalizado exitosamente.\n")


# Ejecución directa
if __name__ == "__main__":
    integracion_rimac()
