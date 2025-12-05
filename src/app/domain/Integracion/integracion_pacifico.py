# integracion_pacifico.py

import sys
import warnings
from datetime import datetime, timedelta
from pathlib import Path

import pandas as pd

# -------------------------------------------------------------------
# Ajustar sys.path para poder importar desde la raíz del proyecto
# -------------------------------------------------------------------
project_root = Path(__file__).resolve().parents[2]
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))

from src.app.repository.configuration_repository import (
    get_sics_file,
    get_sharepoint_file,
    get_pacifico_file,
    OUTPUT_PACIFICO_INTEGRADO,
    OUTPUT_PACIFICO_ANULADO,    # carpeta donde deja el anulados limpio
    get_latest_file             # para leer el último anulados preparado
)
from src.app.repository.mapping_repository import MAPEO

from src.app.domain.Basicos.sics import preparar_sics
from src.app.domain.Basicos.sharepoint import preparar_sharepoint
from src.app.domain.Basicos.pacifico import preparar_pacifico
from src.app.domain.Basicos.anulados import preparar_anulados


# ===================================================================
# 1. Utilidades
# ===================================================================

def leer_excel(path: Path) -> pd.DataFrame:
    """Lee un Excel con engine según extensión, retornando todo como texto."""
    ext = path.suffix.lower()
    with warnings.catch_warnings():
        warnings.simplefilter("ignore")
        if ext == ".xls":
            return pd.read_excel(path, dtype=str, engine="xlrd")
        else:
            return pd.read_excel(path, dtype=str, engine="openpyxl")


# ---------- Asignación de responsable Pacífico ----------

_RESP_PAC_ENTRIES = MAPEO.get("Responsables_Pacifico", [])

_RESP_PAC_MAP = {
    (
        str(item.get("Linea", "")).strip().upper(),
        str(item.get("Producto", "")).strip().upper(),
    ): str(item.get("Responsable", "")).strip()
    for item in _RESP_PAC_ENTRIES
}


def asignar_responsable_pacifico(linea: str, producto: str) -> str:
    """Devuelve el responsable según (Linea de Negocio, Producto)."""
    key = (str(linea).strip().upper(), str(producto).strip().upper())
    return _RESP_PAC_MAP.get(key, "")


# ---------- Cálculo de OBS Pacífico ----------

def calc_obs_pacifico(fin_vigencia, sics_val, tablero_val) -> int:
    """
    Lógica OBS Pacífico:

      1 -> SICS y Tablero = 'No Encontrado' (o vacío/nan)
      3 -> SICS(YYYY-MM) >= FinVigencia(YYYY-MM)
      2 -> resto de casos

    Se inspira en la fórmula de Excel:
        =SI(G30>=TEXTO(M30;"YYYY-MM");3;2)
    con el caso especial 1 igual que en Rimac.
    """
    s = str(sics_val).strip() if pd.notna(sics_val) else ""
    t = str(tablero_val).strip() if pd.notna(tablero_val) else ""
    fv = str(fin_vigencia).strip() if pd.notna(fin_vigencia) else ""

    def es_no_encontrado(x: str) -> bool:
        xl = x.lower()
        return xl in ("", "no encontrado", "nan")

    # 1️⃣ No está en SICS ni en Tablero
    if es_no_encontrado(s) and es_no_encontrado(t):
        return 1

    # 2️⃣ Si no hay SICS, no se puede comparar: se considera 2
    if es_no_encontrado(s):
        return 2

    # 3️⃣ Comparar YYYY-MM entre SICS y Fin de Vigencia
    s_ym = s[:7]  # asume 'YYYY-MM' o 'YYYY-MM-DD'
    fv_ym = fv[:7]

    try:
        if s_ym and fv_ym and s_ym >= fv_ym:
            return 3
        return 2
    except Exception:
        return 2


# ===================================================================
# 2. Proceso principal de integración Pacífico
# ===================================================================

def integracion_pacifico():
    print("\n" + "=" * 70)
    print("[INICIO] Proceso Completo de Integración Pacífico")
    print("=" * 70)

    # ---------------------------------------------------------------
    # Paso 0: Preparaciones (SICS, SharePoint, Pacífico)
    # ---------------------------------------------------------------
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

    print("\n[ETAPA 3/5] Preparación de datos Pacífico")
    print("-" * 70)
    try:
        preparar_pacifico()
    except Exception as e:
        print(f"[ERROR] Fallo en la preparación de Pacífico: {e}")
        return

    print("\n[ETAPA 4/5] Preparación de Anulados")
    print("-" * 70)
    try:
        preparar_anulados()
    except Exception as e:
        print(f"[ERROR] Fallo en la preparación de Anulados: {e}")
        return

    # ---------------------------------------------------------------
    # Paso 1: Localizar archivos preparados
    # ---------------------------------------------------------------
    print("\n[ETAPA 5/5] Integración y Match de datos Pacífico")
    print("-" * 70)

    try:
        path_sics = get_sics_file()
        path_sharepoint = get_sharepoint_file()
        path_pacifico = get_pacifico_file()
        print("[OK] Archivos detectados:")
        print(f"   SICS       → {path_sics.name}")
        print(f"   SharePoint → {path_sharepoint.name}")
        print(f"   Pacífico   → {path_pacifico.name}")
    except Exception as e:
        print(f"[ERROR] Localizando archivos: {e}")
        return

    # ---------------------------------------------------------------
    # Paso 2: Lectura de Excels
    # ---------------------------------------------------------------
    try:
        sics_df = leer_excel(path_sics)
        share_df = leer_excel(path_sharepoint)
        pac_df = leer_excel(path_pacifico)
    except Exception as e:
        print(f"[ERROR] Leyendo Excels: {e}")
        return

    print(f"[INFO] Filas: SICS={len(sics_df)} | SharePoint={len(share_df)} | Pacífico={len(pac_df)}")

    # Normalizar nombres de columnas
    for df in (sics_df, share_df, pac_df):
        df.columns = df.columns.map(str).str.strip()

    # ---------------------------------------------------------------
    # Paso 3: Validación mínima de columnas
    # ---------------------------------------------------------------
    req_sics = ["Pacifico", "Fin Vig"]
    req_share = ["Pacifico", "STATUS RENOVACION"]
    req_pac = [
        "Contratante",
        "Nro de Documento",
        "Linea de Negocio",
        "Producto",
        "Nro de Poliza/Contrato",
        "Fin de Vigencia",
        "Situacion",
    ]

    falt_sics = [c for c in req_sics if c not in sics_df.columns]
    falt_share = [c for c in req_share if c not in share_df.columns]
    falt_pac = [c for c in req_pac if c not in pac_df.columns]

    if falt_sics:
        print(f"[WARN] SICS: faltan columnas {falt_sics}")
    if falt_share:
        print(f"[WARN] SharePoint: faltan columnas {falt_share}")
    if falt_pac:
        print(f"[WARN] Base Pacífico: faltan columnas {falt_pac}")

    # ---------------------------------------------------------------
    # Paso 4: Normalización de llaves y columnas base
    # ---------------------------------------------------------------
    pac_df["Pacifico"] = pac_df["Nro de Poliza/Contrato"].astype(str).str.strip()

    if "Pacifico" in sics_df.columns:
        sics_df["Pacifico"] = sics_df["Pacifico"].astype(str).str.strip()
    if "Pacifico" in share_df.columns:
        share_df["Pacifico"] = share_df["Pacifico"].astype(str).str.strip()

    base_cols = [
        "Contratante",
        "Nro de Documento",
        "Linea de Negocio",
        "Producto",
        "Nro de Poliza/Contrato",
        "Fin de Vigencia",
        "Situacion",
        "Pacifico",
    ]
    base = pac_df[base_cols].copy()

    # ---------------------------------------------------------------
    # Paso 5: Match con SICS y SharePoint
    # ---------------------------------------------------------------
    print("[INFO] Realizando match Pacífico ↔ SICS/SharePoint...")

    if "Pacifico" in sics_df.columns and "Fin Vig" in sics_df.columns:
        sics_map = sics_df.dropna(subset=["Pacifico"]).drop_duplicates("Pacifico").set_index("Pacifico")["Fin Vig"]
        base["SICS"] = base["Pacifico"].map(sics_map).fillna("No Encontrado")
    else:
        base["SICS"] = "No Encontrado"

    if "Pacifico" in share_df.columns and "STATUS RENOVACION" in share_df.columns:
        shp_map = (
            share_df.dropna(subset=["Pacifico"])
            .drop_duplicates("Pacifico")
            .set_index("Pacifico")["STATUS RENOVACION"]
        )
        base["Tablero"] = base["Pacifico"].map(shp_map).fillna("No Encontrado")
    else:
        base["Tablero"] = "No Encontrado"

    print("[OK] Match completado")

    # ---------------------------------------------------------------
    # Paso 6: Responsable, OBS, Observaciones y DentroRango
    # ---------------------------------------------------------------
    base["Responsable"] = base.apply(
        lambda r: asignar_responsable_pacifico(r["Linea de Negocio"], r["Producto"]),
        axis=1,
    )

    base["OBS"] = base.apply(
        lambda r: calc_obs_pacifico(r["Fin de Vigencia"], r["SICS"], r["Tablero"]),
        axis=1,
    )

    comentarios_pac = MAPEO.get("Comentario_Pacifico", {})
    base["Observaciones"] = base["OBS"].map(comentarios_pac).fillna("")

    hoy = datetime.today()
    ano_actual = hoy.year
    ano_siguiente = ano_actual + 1
    mes_actual = hoy.strftime("%Y-%m")
    mes_anterior = (hoy - timedelta(days=30)).strftime("%Y-%m")
    mes_siguiente = (hoy + timedelta(days=30)).strftime("%Y-%m")

    def dentro_de_rango_pacifico(row) -> str:
        s = str(row["SICS"]).strip()
        t = str(row["Tablero"]).strip()
        responsable = str(row["Responsable"]).strip().upper()
        situacion = str(row["Situacion"]).strip().upper()
        fin_vig = str(row["Fin de Vigencia"]).strip()

        # 0️⃣ Filtrado por Situacion: anulada / no renovada / vigencia anterior → NO
        if situacion in {"ANULADA", "NO RENOVADA", "VIGENCIA ANTERIOR"}:
            return "No"

        # 0.1️⃣ Filtrado por año de Fin de Vigencia: solo año actual y siguiente
        try:
            ano_fv = int(fin_vig[:4])
            if ano_fv not in (ano_actual, ano_siguiente):
                return "No"
        except Exception:
            # si no se puede leer el año, juega a lo seguro
            return "No"

        # 1️⃣ Si SICS y Tablero son "No Encontrado" → Sí (se deben revisar)
        if s == "No Encontrado" and t == "No Encontrado":
            return "Sí"

        # 2️⃣ Si SICS vacío o "No Encontrado" → No
        if s in ("", "No Encontrado", "nan"):
            return "No"

        # 3️⃣ Rango por meses según responsable (igual que Rimac)
        s_ym = s[:7]

        if responsable == "JESUS":
            return "Sí" if s_ym in (mes_anterior, mes_actual) else "No"

        return "Sí" if s_ym in (mes_anterior, mes_actual, mes_siguiente) else "No"

    base["DentroRango"] = base.apply(dentro_de_rango_pacifico, axis=1)

    # ---------------------------------------------------------------
    # Paso 7: Integrar Anulados → Polizas Anulada
    # ---------------------------------------------------------------
    try:
        anulados_path = get_latest_file(OUTPUT_PACIFICO_ANULADO)
        print(f"[INFO] Integrando Anulados desde: {anulados_path.name}")
        anul_df = leer_excel(anulados_path)
        anul_df.columns = anul_df.columns.map(str).str.strip()

        if "Nro de Poliza/Contrato" in anul_df.columns and "Situacion" in anul_df.columns:
            anul_df["Nro de Poliza/Contrato"] = anul_df["Nro de Poliza/Contrato"].astype(str).str.strip()
            anul_df["Situacion"] = anul_df["Situacion"].astype(str).str.strip()

            anul_map = (
                anul_df.dropna(subset=["Nro de Poliza/Contrato"])
                .drop_duplicates("Nro de Poliza/Contrato", keep="last")
                .set_index("Nro de Poliza/Contrato")["Situacion"]
            )

            base["Polizas Anulada"] = base["Nro de Poliza/Contrato"].map(anul_map).fillna("")
        else:
            print("[WARN] El archivo de Anulados no contiene las columnas esperadas.")
            base["Polizas Anulada"] = base.get("Polizas Anulada", "")
    except FileNotFoundError:
        print("[WARN] No se encontró archivo de Anulados preparado. 'Polizas Anulada' quedará vacía.")
        base["Polizas Anulada"] = base.get("Polizas Anulada", "")
    except Exception as e:
        print(f"[WARN] Error integrando Anulados: {e}")
        base["Polizas Anulada"] = base.get("Polizas Anulada", "")

    # ---------------------------------------------------------------
    # Paso 8: Reglas adicionales sobre OBS y DentroRango (duplicados)
    # ---------------------------------------------------------------
    if (
        "Nro de Poliza/Contrato" in base.columns
        and "OBS" in base.columns
        and "DentroRango" in base.columns
    ):
        grupos = base.groupby("Nro de Poliza/Contrato", sort=False)

        for _, idx in grupos.groups.items():
            g = base.loc[idx]

            # Normalizar OBS a enteros (1, 2, 3)
            vals = []
            for o in g["OBS"]:
                try:
                    vals.append(int(str(o)))
                except ValueError:
                    pass
            obs_vals = set(vals)

            # 1️⃣ Si en la misma póliza hay OBS = 2 y OBS = 3:
            #     - prevalece el 2
            #     - los registros con OBS = 3 se marcan como "No" en DentroRango
            if 2 in obs_vals and 3 in obs_vals:
                mask_3 = (base.index.isin(idx)) & (base["OBS"].astype(str) == "3")
                base.loc[mask_3, "DentroRango"] = "No"

            # 2️⃣ Si la póliza está repetida y TODOS los OBS son 1:
            #     - solo actuamos si AL MENOS UNA ya estaba en "Sí"
            #       (para no revivir pólizas fuera de rango de año)
            if obs_vals == {1} and len(idx) > 1:
                dentro_si = base.loc[idx, "DentroRango"] == "Sí"

                # Si ninguna está en "Sí" (todas "No"), no tocamos nada
                if dentro_si.any():
                    # marcamos todas como "No"...
                    base.loc[idx, "DentroRango"] = "No"
                    # y dejamos solo UNA en "Sí" (la primera que ya tenía "Sí")
                    idx_si = list(idx[dentro_si.values])
                    primer_si = idx_si[0]
                    base.loc[primer_si, "DentroRango"] = "Sí"

    # ---------------------------------------------------------------
    # Paso 9: Reordenar columnas, eliminar Situacion / Cedidos y exportar
    # ---------------------------------------------------------------
    # Eliminamos las columnas que ya no deben aparecer en el Excel final
    for col_drop in ["Situacion", "Cedidos"]:
        if col_drop in base.columns:
            base = base.drop(columns=[col_drop])

    # Columnas finales (sin Situacion ni Cedidos)
    cols_final = [
        "Contratante",
        "Nro de Documento",
        "Linea de Negocio",
        "Producto",
        "Nro de Poliza/Contrato",
        "SICS",
        "Tablero",
        "Observaciones",
        "Responsable",
        "Fin de Vigencia",
        "OBS",
        "DentroRango",
        "Polizas Anulada",
    ]

    # Aseguramos que todas existan
    for col in cols_final:
        if col not in base.columns:
            base[col] = ""

    df_final = base.reindex(columns=cols_final)

    OUTPUT_PACIFICO_INTEGRADO.mkdir(parents=True, exist_ok=True)
    output_path = OUTPUT_PACIFICO_INTEGRADO / f"Reporte-polizas_Pacifico_{datetime.now().strftime('%Y-%m-%d')}.xlsx"

    try:
        with pd.ExcelWriter(output_path, engine="openpyxl") as writer:
            df_final.to_excel(writer, index=False, sheet_name="MatchPacifico")
        print(f"[OK] Archivo generado: {output_path}")
    except Exception as e:
        print(f"[ERROR] Guardando archivo final: {e}")
        return

    # ---------------------------------------------------------------
    # Paso 10: Resumen
    # ---------------------------------------------------------------
    total = len(df_final)
    en_rango = (df_final["DentroRango"] == "Sí").sum()
    print("\n" + "=" * 70)
    print("[RESUMEN FINAL] Integración Pacífico Completada")
    print("=" * 70)
    print(f"  Total de pólizas procesadas: {total}")
    print(f"  Pólizas en rango de vigencia: {en_rango}")
    print(f"  Pólizas fuera de rango: {total - en_rango}")
    print(f"  Archivo generado: {output_path.name}")
    print("=" * 70)
    print("✅ Proceso completo Pacífico finalizado exitosamente.\n")


if __name__ == "__main__":
    integracion_pacifico()
