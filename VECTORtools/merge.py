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
    # Ensure all datetime columns have the same precision
    base_df[base_time_col] = base_df[base_time_col].astype('datetime64[ns]')
    for other_df in other_dfs:
        other_df[base_time_col] = other_df[base_time_col].astype('datetime64[ns]')
    
    df = base_df
    for other_df in other_dfs:
        df = pd.merge_asof(df, other_df, on=base_time_col, direction='nearest')
    
    df = df.set_index(base_time_col)
    df = df.sort_index()
    df = df.interpolate(method='linear')
    return df


def mergeOnGDS(cataFolder, sampleDict):
    """Merge all instruments aligned to GDS timestamps."""
    df_gds = loadGDS(cataFolder / sampleDict['GDS'])
    df_opc = loadOPC(cataFolder / sampleDict['OPC'])
    df_gc = loadGC(cataFolder / sampleDict['GC'])

    # Reset index to make 'datetime' a column again
    df_gds = df_gds.reset_index()
    df_opc = df_opc.reset_index()
    df_gc = df_gc.reset_index()

    df = _merge_instruments(df_gds, [df_opc, df_gc])
    df.index = (df.index - df.index[0]).total_seconds() / 3600  # in hours

    return df


def mergeOnGC(cataFolder, sampleDict):
    """Merge all instruments aligned to GC timestamps."""
    df_opc = loadOPC(cataFolder / sampleDict['OPC'])
    df_gc = loadGC(cataFolder / sampleDict['GC'])
    df_gds = loadGDS(cataFolder / sampleDict['GDS'])

    # Reset index to make 'datetime' a column again
    df_gds = df_gds.reset_index()
    df_opc = df_opc.reset_index()
    df_gc = df_gc.reset_index()

    df = _merge_instruments(df_gc, [df_gds, df_opc])
    df.index = (df.index - df.index[0]).total_seconds() / 3600  # in hours

    return df
