import numpy as np


def calcConv(df):
    """Calculate CO2 conversion from merged data."""
    C_CO2_max = df.loc[df['C_CO2'] >= df['C_CO2'].quantile(0.95), 'C_CO2'].mean()  # mean of 5% greatest CO2 area values i.e. CO2_in
    # C_CO2_max = df['C_CO2'].max()
    df = df.copy()
    df['Conversion'] = 100 * (C_CO2_max - df['C_CO2']) / C_CO2_max

    return df, C_CO2_max


def calcSelect(df):
    """Calculate CH4 and CO selectivity from merged data."""
    C_CO2_max = df['C_CO2'].max()
    
    df = df.copy()
    denominator = df['C_CO'] + df['C_CH4']
    # Protect against division by zero
    df['S_CH4'] = np.where(denominator > 0, df['C_CH4'] / denominator, 0.0)
    df['S_CO'] = np.where(denominator > 0, df['C_CO'] / denominator, 0.0)
    normFact = (df['S_CO'] + df['S_CH4']).max()

    return df, C_CO2_max, normFact
