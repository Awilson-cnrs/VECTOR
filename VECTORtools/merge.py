import os
from pathlib import Path

import pandas as pd

from .loaders import loadGDS, loadOPC, loadGC


# Default data path — override with DATA_PATH environment variable
DEFAULT_DATA_PATH = Path(os.getenv("DATA_PATH", "Z:/RawData/TestCata"))


def _merge_instruments(base_df, other_dfs, base_time_col='datetime'):
    """
    Shared helper to merge instrument data using merge_asof.
    
    Args:
        base_df: The base DataFrame (already loaded with datetime as a column)
        other_dfs: List of DataFrames to merge onto the base
        base_time_col: Column name for datetime (default 'datetime')
    
    Returns:
        Merged DataFrame with datetime as index
    """
    if base_time_col not in base_df.columns:
        raise ValueError(
            f"Base DataFrame missing time column '{base_time_col}'.\n"
            f"This should not happen — check the loader functions."
        )
    
    # Ensure all datetime columns have the same precision
    base_df[base_time_col] = base_df[base_time_col].astype('datetime64[ns]')
    for other_df in other_dfs:
        if base_time_col not in other_df.columns:
            raise ValueError(
                f"One of the instrument DataFrames is missing the '{base_time_col}' column.\n"
                f"This should not happen — check the loader functions."
            )
        other_df[base_time_col] = other_df[base_time_col].astype('datetime64[ns]')
    
    df = base_df
    for other_df in other_dfs:
        df = pd.merge_asof(df, other_df, on=base_time_col, direction='nearest')
    
    df = df.set_index(base_time_col)
    df = df.sort_index()
    df = df.interpolate(method='linear')
    return df


def mergeOnGDS(cataFolder, sampleDict):
    """Merge all instruments aligned to GDS timestamps.
    
    Args:
        cataFolder: Path to the data directory (e.g. Z:/RawData/TestCata)
        sampleDict: Dictionary with at least 'GDS', 'OPC', and 'GC' file paths
    
    Raises:
        ValueError: If required keys are missing from sampleDict or files don't exist.
    """
    # --- Validate sampleDict has required keys ---
    required_keys = ['GDS', 'OPC', 'GC']
    missing_keys = [k for k in required_keys if k not in sampleDict]
    if missing_keys:
        raise ValueError(
            f"Sample configuration missing required keys: {missing_keys}\n"
            f"Available keys: {list(sampleDict.keys())}\n"
            f"Each sample must have at least: {required_keys}"
        )

    # --- Check files exist before loading ---
    gds_path = cataFolder / sampleDict['GDS']
    opc_path = cataFolder / sampleDict['OPC']
    gc_path = cataFolder / sampleDict['GC']
    
    missing_files = []
    if not gds_path.exists():
        missing_files.append(f"  GDS: {gds_path}")
    if not opc_path.exists():
        missing_files.append(f"  OPC: {opc_path}")
    if not gc_path.exists():
        missing_files.append(f"  GC: {gc_path}")
    
    if missing_files:
        raise FileNotFoundError(
            f"One or more data files are missing:\n"
            f"{'\n'.join(missing_files)}\n\n"
            f"Check if the data path is correct (default: {cataFolder}).\n"
            f"Set the DATA_PATH environment variable to override."
        )

    df_gds = loadGDS(gds_path)
    df_opc = loadOPC(opc_path)
    df_gc = loadGC(gc_path)

    # Reset index to make 'datetime' a column again
    df_gds = df_gds.reset_index()
    df_opc = df_opc.reset_index()
    df_gc = df_gc.reset_index()

    df = _merge_instruments(df_gds, [df_opc, df_gc])
    df.index = (df.index - df.index[0]).total_seconds() / 3600  # in hours

    return df


def mergeOnGC(cataFolder, sampleDict):
    """Merge all instruments aligned to GC timestamps.
    
    Args:
        cataFolder: Path to the data directory (e.g. Z:/RawData/TestCata)
        sampleDict: Dictionary with at least 'GDS', 'OPC', and 'GC' file paths
    
    Raises:
        ValueError: If required keys are missing from sampleDict or files don't exist.
    """
    # --- Validate sampleDict has required keys ---
    required_keys = ['GDS', 'OPC', 'GC']
    missing_keys = [k for k in required_keys if k not in sampleDict]
    if missing_keys:
        raise ValueError(
            f"Sample configuration missing required keys: {missing_keys}\n"
            f"Available keys: {list(sampleDict.keys())}\n"
            f"Each sample must have at least: {required_keys}"
        )

    # --- Check files exist before loading ---
    gds_path = cataFolder / sampleDict['GDS']
    opc_path = cataFolder / sampleDict['OPC']
    gc_path = cataFolder / sampleDict['GC']
    
    missing_files = []
    if not gds_path.exists():
        missing_files.append(f"  GDS: {gds_path}")
    if not opc_path.exists():
        missing_files.append(f"  OPC: {opc_path}")
    if not gc_path.exists():
        missing_files.append(f"  GC: {gc_path}")
    
    if missing_files:
        raise FileNotFoundError(
            f"One or more data files are missing:\n"
            f"{'\n'.join(missing_files)}\n\n"
            f"Check if the data path is correct (default: {cataFolder}).\n"
            f"Set the DATA_PATH environment variable to override."
        )

    df_opc = loadOPC(opc_path)
    df_gc = loadGC(gc_path)
    df_gds = loadGDS(gds_path)

    # Reset index to make 'datetime' a column again
    df_gds = df_gds.reset_index()
    df_opc = df_opc.reset_index()
    df_gc = df_gc.reset_index()

    df = _merge_instruments(df_gc, [df_gds, df_opc])
    df.index = (df.index - df.index[0]).total_seconds() / 3600  # in hours

    return df
