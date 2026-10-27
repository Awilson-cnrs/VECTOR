import pandas as pd


def loadGDS(file):
    df = pd.read_csv(file, sep=';', skiprows=[1], encoding='cp1252')  # encoding allows to deal with é character in the file
    df['datetime'] = pd.to_datetime(df['Date Heure'])  # converts Date Heure column into datetime
    df = df.drop(columns=['Date Heure'])  # deletes columns Date Heure
    df = df.set_index('datetime')  # datetime is now the row label (index), you can plot with datetime slices
    df.index = df.index.floor('s')  # rounds down everything to the nearest second
    df = df.loc[:, ~df.columns.str.contains('^Unnamed')]  # removes all unnamed columns from dataframe
    df = df[~df.index.duplicated(keep='first')]  # whenever there are two rows associated with the same time, keep only the first
    df = df.rename(columns={'M_1FTC01': 'N2', 'M_2FTC01': 'CO2', 'M_3FTC01': 'H2', 'M_6FTC01': 'Calibration Mix', '1PT01': 'React_Pressure',
                       'M_4PTC01': 'BFC_Pressure'})  # renames columns for better formatting
    # print('GDS', df.shape)  # This gives GDS, number of rows and columns

    return df


def loadOPC(file):
    df = pd.read_csv(file, delimiter=',', decimal='.')  # , error_bad_lines=False)
    df['datetime'] = df['Date/Time'].astype(str).str.replace(',', '.')  # new column called datetime, transforms cells in strings, dots replace commas
    df['datetime'] = pd.to_datetime('1899-12-30') + pd.to_timedelta(df['datetime'].astype(float), unit='d')  # converts an excel number associated to a datetime into datetime
    df = df.drop(columns=df.columns[0])  # removes previous Date/Time column
    df = df.set_index('datetime')
    df.index = df.index.floor('s')
    df = df[~df.index.duplicated(keep='first')]  # arranging datetime data to match GDS !!
    df['Temperature'] = df['Temperature'].astype(float)  # transforms T data in floating-point numbers
    # print('OPC', df.shape)

    return df


def loadGC(file):
    df = pd.read_csv(file, skiprows=5)
    df = df.rename(columns={df.columns[0]: 'datetime'})
    df = df[df['datetime'].str.match(r'^\d')]  # all this ignores rows in datetime that do not start with a number, thus keeping only datetime data!
    df['datetime'] = pd.to_datetime(df['datetime'])  # python now knows this is datetime data
    df = df.set_index('datetime')
    df = df.drop(df.columns[0], axis=1)  # this drops a column just like above but he used different syntax
    df = df.sort_index()  # very important step, data was not in chronological order, now it is
    df.index = df.index.floor('s')
    df = df[~df.index.duplicated(keep='first')]
    # print(df.head(5)) run this to see why the loop below is necessary !
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
    # print('GC', df.shape)

    return df


def loadMS(file):  # data only for DR60-1
    df = pd.read_csv(file, sep="\t", decimal=",", skiprows=6, index_col=0)  # MS data is in asc, which works just like csv
    df = df.iloc[1:]
    df = df.loc[:, ~df.columns.str.contains("^Unnamed")]
    # df.index = pd.to_datetime(df.index, dayfirst=True)
    # df = df.set_index('datetime')
    df = df.apply(lambda x: x.str.replace(',', '.').astype(float) if x.dtype == 'object' else x)

    return df
