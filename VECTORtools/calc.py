import numpy as np
import pandas as pd


def calcConv(df):
    """Calculate CO2 conversion from merged data.
    
    Expects the merged DataFrame to have column 'C_CO2' (CO2 concentration from GC).
    
    Returns:
        Tuple of (DataFrame with 'Conversion' column, C_CO2_max reference value).
    """
    if 'C_CO2' not in df.columns:
        raise ValueError(
            "Merged data missing column 'C_CO2'.\n"
            "This column comes from the GC (Gas Chromatograph) data.\n"
            "Possible causes:\n"
            "  - GC file format changed (column naming)\n"
            "  - GC data failed to merge with GDS/OPC data\n"
            "  - The GC instrument was not running during this experiment."
        )
    
    C_CO2_max = df.loc[df['C_CO2'] >= df['C_CO2'].quantile(0.95), 'C_CO2'].mean()
    
    if C_CO2_max == 0 or pd.isna(C_CO2_max):
        raise ValueError(
            f"C_CO2_max is {C_CO2_max} — cannot calculate conversion.\n"
            "This means CO2 concentration data is all zeros or empty.\n"
            "Check if the GC instrument was recording correctly."
        )
    
    df = df.copy()
    df['Conversion'] = 100 * (C_CO2_max - df['C_CO2']) / C_CO2_max

    return df, C_CO2_max


def calcSelect(df):
    """Calculate CH4 and CO selectivity from merged data.
    
    Expects the merged DataFrame to have columns: C_CO2, C_CO, C_CH4.
    
    Returns:
        Tuple of (DataFrame with 'S_CH4' and 'S_CO' columns, C_CO2_max, normFact).
    """
    required_cols = ['C_CO2', 'C_CO', 'C_CH4']
    missing = [c for c in required_cols if c not in df.columns]
    if missing:
        raise ValueError(
            f"Merged data missing required columns: {missing}\n"
            f"These columns come from the GC (Gas Chromatograph) data.\n"
            "Possible causes:\n"
            "  - GC file format changed (column naming)\n"
            "  - GC data failed to merge with GDS/OPC data\n"
            "  - The GC instrument detected different compounds than expected."
        )
    
    C_CO2_max = df['C_CO2'].max()
    
    df = df.copy()
    denominator = df['C_CO'] + df['C_CH4']
    # Protect against division by zero — when no products are detected, selectivity is 0
    df['S_CH4'] = np.where(denominator > 0, df['C_CH4'] / denominator, 0.0)
    df['S_CO'] = np.where(denominator > 0, df['C_CO'] / denominator, 0.0)
    normFact = (df['S_CO'] + df['S_CH4']).max()
    
    if pd.isna(normFact) or normFact == 0:
        raise ValueError(
            "Selectivity normalization factor is 0 — no CH4 or CO detected.\n"
            "This means the reaction produced no measurable products.\n"
            "Check if the GC calibration is correct or if the reaction conditions were appropriate."
        )

    return df, C_CO2_max, normFact
