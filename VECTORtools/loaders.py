import pandas as pd


def loadGDS(file):
    """Load GDS (Gas Delivery System) data from CSV.
    
    Expects columns: Date Heure, M_1FTC01, M_2FTC01, M_3FTC01, M_6FTC01, 1PT01, M_4PTC01
    These correspond to: timestamp, N2, CO2, H2, Calibration Mix, Reactor Pressure, BFC Pressure.
    """
    df = pd.read_csv(file, sep=';', skiprows=[1], encoding='cp1252')

    # --- Validate expected columns are present ---
    if 'Date Heure' not in df.columns:
        raise ValueError(
            f"GDS file missing expected column 'Date Heure'.\n"
            f"File: {file}\n"
            f"Found columns: {list(df.columns)}\n"
            f"This usually means the GDS instrument export format changed."
        )
    expected_flow_cols = ['M_1FTC01', 'M_2FTC01', 'M_3FTC01', 'M_6FTC01', '1PT01', 'M_4PTC01']
    missing = [c for c in expected_flow_cols if c not in df.columns]
    if missing:
        raise ValueError(
            f"GDS file missing expected columns: {missing}\n"
            f"File: {file}\n"
            f"Found columns: {list(df.columns)}\n"
            f"This usually means the GDS instrument channel names changed (hardware or firmware update)."
        )

    df['datetime'] = pd.to_datetime(df['Date Heure'])
    df = df.drop(columns=['Date Heure'])
    df = df.set_index('datetime')
    df.index = df.index.floor('s')
    df = df.loc[:, ~df.columns.str.contains('^Unnamed')]
    df = df[~df.index.duplicated(keep='first')]

    if df.empty:
        raise ValueError(f"GDS file is empty after parsing: {file}")

    df = df.rename(columns={'M_1FTC01': 'N2', 'M_2FTC01': 'CO2', 'M_3FTC01': 'H2', 'M_6FTC01': 'Calibration Mix', '1PT01': 'React_Pressure',
                       'M_4PTC01': 'BFC_Pressure'})

    return df


def loadOPC(file):
    """Load OPC (Temperature Controller) data from CSV.
    
    Expects columns: Date/Time (Excel serial datetime), Temperature
    """
    df = pd.read_csv(file, delimiter=',', decimal='.')

    # --- Validate expected columns are present ---
    if 'Date/Time' not in df.columns:
        raise ValueError(
            f"OPC file missing expected column 'Date/Time'.\n"
            f"File: {file}\n"
            f"Found columns: {list(df.columns)}\n"
            f"This usually means the OPC temperature controller export format changed."
        )
    if 'Temperature' not in df.columns:
        raise ValueError(
            f"OPC file missing expected column 'Temperature'.\n"
            f"File: {file}\n"
            f"Found columns: {list(df.columns)}\n"
            f"This usually means the OPC temperature controller channel name changed."
        )

    df['datetime'] = df['Date/Time'].astype(str).str.replace(',', '.')
    df['datetime'] = pd.to_datetime('1899-12-30') + pd.to_timedelta(df['datetime'].astype(float), unit='d')
    df = df.drop(columns=df.columns[0])
    df = df.set_index('datetime')
    df.index = df.index.floor('s')
    df = df[~df.index.duplicated(keep='first')]
    df['Temperature'] = df['Temperature'].astype(float)

    if df.empty:
        raise ValueError(f"OPC file is empty after parsing: {file}")

    return df


def loadGC(file):
    """Load GC (Gas Chromatograph) data from CSV.
    
    Expects: first 5 rows are headers/metadata, then datetime followed by concentration columns.
    Column names use a dot notation (e.g. 'CO2.1', 'CH4.2', 'CO.3') to distinguish
    normalized concentration (NC_), area (A_), retention time (RT_), and concentration (C_).
    
    Critical columns for analysis: C_CO2, C_CO, C_CH4
    """
    df = pd.read_csv(file, skiprows=5)
    df = df.rename(columns={df.columns[0]: 'datetime'})
    df = df[df['datetime'].str.match(r'^\d')]
    df['datetime'] = pd.to_datetime(df['datetime'])
    df = df.set_index('datetime')
    df = df.drop(df.columns[0], axis=1)
    df = df.sort_index()
    df.index = df.index.floor('s')
    df = df[~df.index.duplicated(keep='first')]

    if df.empty:
        raise ValueError(
            f"GC file is empty after parsing: {file}\n"
            f"This may mean the GC export format changed (e.g. different number of header rows)."
        )

    # Rename columns based on dot notation: CO2.1 -> NC_CO2, CH4.2 -> A_CH4, CO.3 -> RT_CO, CO2 -> C_CO2
    new_column_names = []
    for col in df.columns:
        if col.split('.')[-1] == '1':
            new_column_names.append('NC_{}'.format(col.split('.')[0]))
        elif col.split('.')[-1] == '2':
            new_column_names.append('A_{}'.format(col.split('.')[0]))
        elif col.split('.')[-1] == '3':
            new_column_names.append('RT_{}'.format(col.split('.')[0]))
        else:
            new_column_names.append('C_{}'.format(col.split('.')[0]))
    df.columns = new_column_names

    # --- Validate critical concentration columns exist ---
    required_gc_cols = ['C_CO2', 'C_CO', 'C_CH4']
    missing = [c for c in required_gc_cols if c not in df.columns]
    if missing:
        raise ValueError(
            f"GC file missing required concentration columns: {missing}\n"
            f"File: {file}\n"
            f"Found columns: {list(df.columns)}\n"
            f"This usually means the GC instrument detected different compounds or the column naming changed."
        )

    return df


def loadMS(file):
    """Load MS (Mass Spectrometer) data from .asc tab-separated file.
    
    Note: This function is incomplete — datetime parsing is not finalized.
    MS data is only available for sample DR60-1 and is not used in the main merge pipeline.
    """
    df = pd.read_csv(file, sep="\t", decimal=",", skiprows=6, index_col=0)
    df = df.iloc[1:]
    df = df.loc[:, ~df.columns.str.contains("^Unnamed")]
    # df.index = pd.to_datetime(df.index, dayfirst=True)
    # df = df.set_index('datetime')
    df = df.apply(lambda x: x.str.replace(',', '.').astype(float) if x.dtype == 'object' else x)

    return df
