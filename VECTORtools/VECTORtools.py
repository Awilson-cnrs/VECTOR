from pathlib import Path
from sampleDictFile import sampleDict
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np

def loadGDS(file):
    df = pd.read_csv(file, sep=';', skiprows=[1], encoding='cp1252') #encoding allows to deal with é character in the file
    df['datetime'] = pd.to_datetime(df['Date Heure']) # converts Date Heure column into datetime
    df.drop(columns=['Date Heure'], inplace=True) #deletes columns Date Heure / inplace=True Modifies df directly, instead of returning a new DataFrame
    df.set_index('datetime', inplace=True) #datetime is now the row label (index), you can plot with datetime slices
    df.index = df.index.floor('s') #rounds down everything to the nearest second
    df = df.loc[:, ~df.columns.str.contains('^Unnamed')] #removes all unnamed columns from dataframe
    df = df[~df.index.duplicated(keep='first')] #whenever there are two rows associated with the same time, keep only the first
    df.rename(columns={'M_1FTC01': 'N2', 'M_2FTC01': 'CO2', 'M_3FTC01': 'H2', 'M_6FTC01' : 'Calibration Mix', '1PT01':'React_Pressure',
                       'M_4PTC01' : 'BFC_Pressure'}, inplace=True) #renames columns for better formatting
    #print('GDS', df.shape) #This gives GDS, number of rows and columns
    
    return df

def loadOPC(file):
    df = pd.read_csv(file, delimiter=',', decimal='.') #, error_bad_lines=False)
    df['datetime'] = df['Date/Time'].astype(str).str.replace(',', '.') #new column called datetime, transforms cells in strings, dots replace commas
    df['datetime'] = pd.to_datetime('1899-12-30') + pd.to_timedelta(df['datetime'].astype(float), unit='d') #converts an excel number associated to a datetime into datetime
    df.drop(columns=df.columns[0], inplace=True) #removes previous Date/Time column
    df.set_index('datetime', inplace=True)
    df.index = df.index.floor('s')
    df = df[~df.index.duplicated(keep='first')] #arranging datetime data to match GDS !!
    df['Temperature'] = df['Temperature'].astype(float) #transforms T data in floating-point numbers
    #print('OPC', df.shape)
    
    return df

def loadGC(file):
    df = pd.read_csv(file, skiprows=5)
    df = df.rename(columns={df.columns[0]: 'datetime'})
    df = df[df['datetime'].str.match(r'^\d')] #all this ignores rows in datetime that do not start with a number, thus keeping only datetime data!
    df['datetime'] = pd.to_datetime(df['datetime']) #python now knows this is datetime data
    df = df.set_index('datetime')
    df = df.drop(df.columns[0], axis=1) #this drops a column just like above but he used different syntax
    df.sort_index(inplace=True) #very important step, data was not in chronological order, now it is
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
    #print('GC', df.shape)
    
    return df

def loadMS(file): #data only for DR60-1
    
    df = pd.read_csv(file, sep="\t", decimal=",", skiprows=6, index_col=0) #MS data is in asc, which works just like csv
    df = df.iloc[1:]
    df = df.loc[:, ~df.columns.str.contains("^Unnamed")]
    #df.index = pd.to_datetime(df.index, dayfirst=True)
    #df = df.set_index('datetime')
    df = df.apply(lambda x: x.str.replace(',', '.').astype(float) if x.dtype == 'object' else x)
    
    return df

    
def mergeOnGDS(cataFolder, sampleDict):

    df_gds = loadGDS(cataFolder  / sampleDict['GDS'])
    df_opc = loadOPC(cataFolder  / sampleDict['OPC'])
    df_gc = loadGC(cataFolder  / sampleDict['GC'])

    # Reset index to make 'datetime' a column again
    df_gds = df_gds.reset_index()
    df_opc = df_opc.reset_index()
    df_gc = df_gc.reset_index()

    # Ensure all datetime columns have the same precision
    df_gds['datetime'] = df_gds['datetime'].astype('datetime64[ns]')
    df_opc['datetime'] = df_opc['datetime'].astype('datetime64[ns]')
    df_gc['datetime'] = df_gc['datetime'].astype('datetime64[ns]')
    
    df = pd.merge_asof(df_gds, df_opc, on='datetime', direction='nearest') #here we match the closest gaps of GDS and OPC !
    #merge_asof align experimental data without creating so many NaNs
    df = pd.merge_asof(df, df_gc, on='datetime', direction='nearest') #then GC is added

    # Set the index back to 'datetime'
    df.set_index('datetime', inplace=True)
    
    df.sort_index(inplace=True)
    df.interpolate(method='linear', inplace=True) #still needs to interpolate
    df.index = (df.index - df.index[0]).total_seconds() / 3600 #in hours
    
    return df

def mergeOnGC(cataFolder, sampleDict): #same as above, but everything is aligned with GC instead of GDS data
    
    df_opc = loadOPC(cataFolder  / sampleDict['OPC'])
    df_gc = loadGC(cataFolder  / sampleDict['GC'])
    df_gds = loadGDS(cataFolder  / sampleDict['GDS'])
    

    # Reset index to make 'datetime' a column again
    df_gds = df_gds.reset_index()
    df_opc = df_opc.reset_index()
    df_gc = df_gc.reset_index()

    # Ensure all datetime columns have the same precision
    df_gds['datetime'] = df_gds['datetime'].astype('datetime64[ns]')
    df_opc['datetime'] = df_opc['datetime'].astype('datetime64[ns]')
    df_gc['datetime'] = df_gc['datetime'].astype('datetime64[ns]')

    df = pd.merge_asof(df_gc, df_gds, on='datetime', direction='nearest')
    df = pd.merge_asof(df, df_opc, on='datetime', direction='nearest')

    # Set the index back to 'datetime'
    df.set_index('datetime', inplace=True)
    df.index = (df.index - df.index[0]).total_seconds() / 3600

    return df

def OverviewPlot(sample, cataFolder = Path(r"Z:\RawData\TestCata"), sampleDict = sampleDict):
    
    df = mergeOnGDS(cataFolder, sampleDict[sample])
    fig, axs = plt.subplots(3, 1, sharex=True) #this plots the three plots together, with shared x axis!! 
    
    df['Temperature'].plot(ax=axs[0])
    ax0_twin = axs[0].twinx() #second y axis for power output
    df['POutput'].plot(ax=ax0_twin, alpha=0.3, color='red') #alpha is just for colour shade, semi-transparent
    ax0_twin.set_ylabel('Power output (%)', color='red')
    ax0_twin.tick_params(axis='y', labelcolor='red')
    ax0_twin.legend(fontsize='small', loc='upper right')
    axs[0].legend(fontsize='small', loc='upper left')
    axs[0].set_ylabel('Temperature (°C)')
    axs[0].set_title(sampleDict[sample]['label'])
    
    df['C_H2'].plot(ax=axs[1])
    df['C_CO2'].plot(ax=axs[1])
    #df['NC_N2'].plot(ax=axs[1])
    df['C_CH4'].plot(ax=axs[1])
    df['C_CO'].plot(ax=axs[1])
    axs[1].legend(fontsize='small')
    axs[1].set_ylabel('Compound Concentration (% mol)')
    
    df['H2'].plot(ax=axs[2])
    df['CO2'].plot(ax=axs[2])
    df['N2'].plot(ax=axs[2])
    ax2_twin = axs[2].twinx()
    #df['React_Pressure'].plot(ax=ax2_twin, alpha=0.3, color='red')
    #ax2_twin.set_ylabel('Reactor Pressure (bar)', color='red')
    df['BFC_Pressure'].plot(ax=ax2_twin, alpha=0.3, color='red')
    ax2_twin.set_ylabel('BFC Pressure (bar)', color='red')
    ax2_twin.tick_params(axis='y', labelcolor='red')
    ax2_twin.legend(fontsize='small', loc='upper right')
    axs[2].legend(fontsize='small', loc='upper left')
    axs[2].set_ylabel('Flow (ml/min)')
    
    axs[2].set_xlabel('Time (h)')
    plt.tight_layout()

def calcConv(df):
    
    C_CO2_max = df.loc[df['C_CO2'] >= df['C_CO2'].quantile(0.95),'C_CO2'].mean() #mean of 5% greatest CO2 area values i.e. CO2_in
    #C_CO2_max = df['C_CO2'].max()
    df['Conversion'] = 100 * (C_CO2_max - df['C_CO2']) / C_CO2_max

    return df, C_CO2_max

def calcSelect(df):
    
    C_CO2_max = df['C_CO2'].max()
    
    df['S_CH4'] = (df['C_CH4']) / (df['C_CO'] + df['C_CH4'])
    df['S_CO'] = (df['C_CO']) / (df['C_CO'] + df['C_CH4'])
    normFact = (df['S_CO']+df['S_CH4']).max()

    return df, C_CO2_max, normFact

def triPlot(samples, vlines = False, cataFolder = Path(r"Z:\RawData\TestCata"), sampleDict = sampleDict):

    fig, axs = plt.subplots(3, 1, sharex=True, figsize=(7, 4))

    for sample in samples:
        df = mergeOnGC(cataFolder, sampleDict[sample]).iloc[sampleDict[sample]['TPrange'][0]:sampleDict[sample]['TPrange'][1]]
        df.index = df.index - df.index[0] + sampleDict[sample]['TPrange'][2]
        df, _ = calcConv(df)
        df, C_CO2_max, normFact = calcSelect(df)
        axs[0].plot(df['Conversion'], label = sampleDict[sample]['label'])
        axs[1].plot(df['S_CH4']*100)
        axs[2].plot(df['S_CO']*100)

    T_times = [2.678, 2.949, 5.86, 6.21, 9.13, 9.52, 12.4]
    T_labels = ['T = 200 °C', '', 'T = 300 °C', '', 'T = 400 °C', '', 'T = 500 °C']

    for t, label in zip(T_times, T_labels):
    	for ax in axs:
            ax.axvline(t, linestyle='--', alpha=0.4)

    	axs[0].text(
            t, 1.02, label,
            transform=axs[0].get_xaxis_transform(),
            ha='center', va='bottom',
            fontsize='x-small'
    	)    

    axs[0].set_ylabel('CO$_2$ conversion (%)', fontsize='small')
    axs[0].legend(fontsize='x-small')

    axs[1].set_ylabel('CH$_4$ selectivity (%)', fontsize='small')

    axs[2].set_ylabel('CO selectivity (%)', fontsize='small')
    axs[2].set_xlabel('Time (hour)')
    axs[0].set_ylim(-5, 80)
    axs[1].set_ylim(-5, 110)
    axs[2].set_ylim(-5, 110)

    
    if vlines:
        vlines = [2.95, 5.84, 6.25, 9.13, 9.56, 12.35]
        for vline in vlines:
            axs[0].axvline(x=vline, color='red', linestyle='--', linewidth=1)
            axs[1].axvline(x=vline, color='red', linestyle='--', linewidth=1)
            axs[2].axvline(x=vline, color='red', linestyle='--', linewidth=1)
    plt.tight_layout()
    
def tempPlot(samples, cataFolder = Path(r"Z:\RawData\TestCata"), sampleDict = sampleDict):

    for sample in samples:
        df = mergeOnGC(cataFolder, sampleDict[sample]).iloc[sampleDict[sample]['TPrange'][0]:sampleDict[sample]['TPrange'][1]]
        df.index = df.index - df.index[0] + sampleDict[sample]['TPrange'][2]
        plt.plot(df['Temperature'], label = sampleDict[sample]['label'])
    
    vlines = [2.95, 5.84, 6.25, 9.13, 9.56, 12.35]
    for vline in vlines:
        plt.axvline(x=vline, color='red', linestyle='--', linewidth=1)
    
    plt.legend(fontsize='small')
    plt.xlabel('Time (hour)')
    plt.ylabel('Temperature (°C)')
    
def tweakTimeOffset(sample, tweak, sampleRef = 'DR60-26', cataFolder = Path(r"Z:\RawData\TestCata"), sampleDict = sampleDict):

    df = mergeOnGC(cataFolder, sampleDict[sampleRef]).iloc[sampleDict[sampleRef]['TPrange'][0]:sampleDict[sampleRef]['TPrange'][1]]
    df.index = df.index - df.index[0]
    plt.plot(df['Temperature'].loc[5:7], label = 'ref')
    vlines = [5.84, 6.25]
    for vline in vlines:
        plt.axvline(x=vline, color='red', linestyle='--', linewidth=1)

    df = mergeOnGC(cataFolder, sampleDict[sample]).iloc[sampleDict[sample]['TPrange'][0]:sampleDict[sample]['TPrange'][1]]

    df.index = df.index - df.index[0] + tweak
    plt.plot(df['Temperature'].loc[5:7], label = sampleDict[sample]['label'])

    plt.text(x=0.05, y=0.2, s=f'{sample} : {tweak}', fontsize=16, transform=plt.gca().transAxes)
    plt.legend(fontsize='small')
    plt.xlabel('Time (hour)')
    plt.ylabel('Temperature (°C)')

def carbonBalance(sample, cataFolder = Path(r"Z:\RawData\TestCata"), sampleDict = sampleDict):

    df = mergeOnGC(cataFolder, sampleDict[sample]).iloc[
        sampleDict[sample]['TPrange'][0]:sampleDict[sample]['TPrange'][1]
    ]
    df.index = df.index - df.index[0]
    df, _ = calcConv(df)
    
    CO2_in = df['C_CO2'].max()
    
    # Carbon balance (%)
    carbon_balance = CO2_in - df['C_CO2'] - df['C_CH4'] - df['C_CO']
    
    fig, (ax1, ax2) = plt.subplots(
        2, 1,
        figsize=(7, 7),
        sharex=True,
        gridspec_kw={'height_ratios': [3, 1]}
    )
    
    # Top panel: Gas concentrations
    
    ax1.plot(df['Temperature'], df['C_CO2'],
             color='forestgreen', lw=2, label='CO$_2$')
    
    ax1.plot(df['Temperature'], df['C_CO'],
             color='darkorange', lw=2, label='CO')
    
    ax1.plot(df['Temperature'], df['C_CH4'],
             color='royalblue', lw=2, label='CH$_4$')
    
    ax1.set_ylabel('Concentration (%mol)')
    ax1.legend()
    ax1.grid(alpha=0.3)
    
    # Bottom panel: Carbon balance
    
    ax2.plot(df['Temperature'],
             carbon_balance,
             color='red',
             lw=2,
             label = r'$CO_{2,\mathrm{in}} = CO_{2,\mathrm{out}} + CH_{4,\mathrm{out}} + CO_{\mathrm{out}}$')
    
    ax2.axhline(0,
                color='k',
                linestyle='--',
                lw=1)
    
    ax2.set_xlabel('Temperature (°C)')
    ax2.set_ylabel('Balance (%mol)')
    ax2.legend()
    ax2.set_ylim(-10, 5)
    ax2.grid(alpha=0.3)
    
    fig.suptitle(sampleDict[sample]['label'])
    plt.tight_layout()



