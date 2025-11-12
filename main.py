import sys
from pathlib import Path

try:
    import pandas as pd
except ImportError:
    print("Error: pandas no está instalado. Añade 'pandas' a requirements.txt o instálalo con pip.", file=sys.stderr)
    sys.exit(1)

DATA_DIR = Path(__file__).resolve().parent / "data"

def find_first_dataset(data_dir: Path):
    patterns = ["*.csv", "*.tsv", "*.parquet", "*.xlsx", "*.xls"]
    for pat in patterns:
        files = sorted(data_dir.glob(pat))
        if files:
            return files[0]
    return None

def read_dataset(path: Path):
    suffix = path.suffix.lower()
    if suffix in [".csv", ".tsv"]:
        sep = "\t" if suffix == ".tsv" else ","
        return pd.read_csv(path, sep=sep, low_memory=False)
    if suffix == ".parquet":
        return pd.read_parquet(path)
    if suffix in [".xlsx", ".xls"]:
        return pd.read_excel(path)
    raise ValueError(f"Formato no soportado: {suffix}")

def clean_dataframe(df: pd.DataFrame) -> pd.DataFrame:
    # Normalizar nombres de columnas
    df = df.rename(columns=lambda c: str(c).strip().lower().replace(" ", "_"))

    # Eliminar filas duplicadas completas
    df = df.drop_duplicates()

    # Reemplazar cadenas vacías por NA
    df = df.replace(r'^\s*$', pd.NA, regex=True)

    # Recortar espacios en columnas tipo object / string
    obj_cols = df.select_dtypes(include=["object", "string"]).columns
    for col in obj_cols:
        df[col] = df[col].astype("string").str.strip()

    # Intentar convertir columnas tipo object a numéricas cuando tenga sentido
    for col in df.columns:
        if df[col].dtype == "object" or pd.api.types.is_string_dtype(df[col]):
            coerced = pd.to_numeric(df[col], errors="coerce")
            if coerced.notna().sum() / max(1, len(df)) > 0.5:
                df[col] = coerced

    # Detectar y parsear fechas por nombre o por muestra
    for col in df.columns:
        col_l = str(col).lower()
        if "date" in col_l or "fecha" in col_l:
            df[col] = pd.to_datetime(df[col], errors="coerce", infer_datetime_format=True)
        elif df[col].dtype == "object" or pd.api.types.is_string_dtype(df[col]):
            sample = df[col].dropna().astype(str).head(50)
            if len(sample) > 0:
                parsed = pd.to_datetime(sample, errors="coerce", infer_datetime_format=True)
                if parsed.notna().sum() / len(sample) > 0.6:
                    df[col] = pd.to_datetime(df[col], errors="coerce", infer_datetime_format=True)

    # Eliminar columnas con más del 95% de valores faltantes
    thresh = int(0.05 * len(df))
    if thresh > 0:
        df = df.dropna(axis=1, thresh=thresh)

    return df.reset_index(drop=True)

def main():
    if not DATA_DIR.exists():
        print(f"No se encontró la carpeta de datos en: {DATA_DIR}", file=sys.stderr)
        sys.exit(1)

    ds_path = find_first_dataset(DATA_DIR)
    if ds_path is None:
        print(f"No se encontró ningún dataset en {DATA_DIR}. Formatos buscados: csv, tsv, parquet, xlsx, xls", file=sys.stderr)
        sys.exit(1)

    print(f"Lectura del dataset: {ds_path}")
    try:
        df = read_dataset(ds_path)
    except Exception as e:
        print(f"Error leyendo el dataset: {e}", file=sys.stderr)
        sys.exit(1)

    print("Ejecutando proceso ETL (limpieza)...")
    cleaned = clean_dataframe(df)

    # Mostrar resumen y los primeros registros del dataset limpio
    print("\n--- Resumen del dataset limpio ---")
    print(f"Filas: {len(cleaned)}, Columnas: {len(cleaned.columns)}")
    cleaned_info_buf = []
    try:
        # Mostrar info en consola (sin imprimir None)
        cleaned.info(buf=None)
    except Exception:
        # fallback sencillo
        print(cleaned.dtypes)

    print("\n--- Primeras 20 filas ---")
    pd.set_option("display.max_rows", 200, "display.max_columns", None, "display.width", 150)
    print(cleaned.head(20).to_string(index=False))

    # Guardar dataset limpio para uso posterior
    out_path = DATA_DIR / "cleaned_dataset.csv"
    try:
        cleaned.to_csv(out_path, index=False)
        print(f"\nDataset limpio guardado en: {out_path}")
    except Exception as e:
        print(f"No se pudo guardar el dataset limpio: {e}", file=sys.stderr)

if __name__ == "__main__":
    main()