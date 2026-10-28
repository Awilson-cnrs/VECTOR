from pathlib import Path

import matplotlib.pyplot as plt

from .merge import mergeOnGDS, mergeOnGC, DEFAULT_DATA_PATH
from .calc import calcConv, calcSelect
from .samples import sampleDict


def OverviewPlot(sample, cataFolder=DEFAULT_DATA_PATH, sampleDict=sampleDict):
    """Plot an overview of a single sample: temperature, gas concentrations, and flows."""
    if sample not in sampleDict:
        available = ', '.join(sorted(sampleDict.keys()))
        raise KeyError(
            f"Sample '{sample}' not found in sampleDict.\n"
            f"Available samples: {available}"
        )
    
    df = mergeOnGDS(cataFolder, sampleDict[sample])
    fig, axs = plt.subplots(3, 1, sharex=True)  # this plots the three plots together, with shared x axis!!

    df['Temperature'].plot(ax=axs[0])
    ax0_twin = axs[0].twinx()  # second y axis for power output
    df['POutput'].plot(ax=ax0_twin, alpha=0.3, color='red')  # alpha is just for colour shade, semi-transparent
    ax0_twin.set_ylabel('Power output (%)', color='red')
    ax0_twin.tick_params(axis='y', labelcolor='red')
    ax0_twin.legend(fontsize='small', loc='upper right')
    axs[0].legend(fontsize='small', loc='upper left')
    axs[0].set_ylabel('Temperature (°C)')
    axs[0].set_title(sampleDict[sample]['label'])

    df['C_H2'].plot(ax=axs[1])
    df['C_CO2'].plot(ax=axs[1])
    # df['NC_N2'].plot(ax=axs[1])
    df['C_CH4'].plot(ax=axs[1])
    df['C_CO'].plot(ax=axs[1])
    axs[1].legend(fontsize='small')
    axs[1].set_ylabel('Compound Concentration (% mol)')

    df['H2'].plot(ax=axs[2])
    df['CO2'].plot(ax=axs[2])
    df['N2'].plot(ax=axs[2])
    ax2_twin = axs[2].twinx()
    # df['React_Pressure'].plot(ax=ax2_twin, alpha=0.3, color='red')
    # ax2_twin.set_ylabel('Reactor Pressure (bar)', color='red')
    df['BFC_Pressure'].plot(ax=ax2_twin, alpha=0.3, color='red')
    ax2_twin.set_ylabel('BFC Pressure (bar)', color='red')
    ax2_twin.tick_params(axis='y', labelcolor='red')
    ax2_twin.legend(fontsize='small', loc='upper right')
    axs[2].legend(fontsize='small', loc='upper left')
    axs[2].set_ylabel('Flow (ml/min)')

    axs[2].set_xlabel('Time (h)')
    plt.tight_layout()


def triPlot(samples, vlines=False, cataFolder=DEFAULT_DATA_PATH, sampleDict=sampleDict):
    """Compare multiple samples: CO2 conversion, CH4 selectivity, and CO selectivity."""
    # --- Validate all samples exist ---
    missing_samples = [s for s in samples if s not in sampleDict]
    if missing_samples:
        available = ', '.join(sorted(sampleDict.keys()))
        raise KeyError(
            f"Sample(s) not found in sampleDict: {missing_samples}\n"
            f"Available samples: {available}"
        )
    
    # --- Validate TPrange is present for all samples ---
    for sample in samples:
        if 'TPrange' not in sampleDict[sample]:
            raise ValueError(
                f"Sample '{sample}' is missing 'TPrange' in sampleDict.\n"
                "TPrange is required for triPlot — it defines the time range to extract.\n"
                "Add 'TPrange': [start, end, offset] to the sample configuration."
            )

    fig, axs = plt.subplots(3, 1, sharex=True, figsize=(7, 4))

    for sample in samples:
        df = mergeOnGC(cataFolder, sampleDict[sample]).iloc[sampleDict[sample]['TPrange'][0]:sampleDict[sample]['TPrange'][1]]
        df.index = df.index - df.index[0] + sampleDict[sample]['TPrange'][2]
        df, _ = calcConv(df)
        df, C_CO2_max, normFact = calcSelect(df)
        axs[0].plot(df['Conversion'], label=sampleDict[sample]['label'])
        axs[1].plot(df['S_CH4'] * 100)
        axs[2].plot(df['S_CO'] * 100)

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


def tempPlot(samples, cataFolder=DEFAULT_DATA_PATH, sampleDict=sampleDict):
    """Plot temperature curves for multiple samples."""
    missing_samples = [s for s in samples if s not in sampleDict]
    if missing_samples:
        available = ', '.join(sorted(sampleDict.keys()))
        raise KeyError(
            f"Sample(s) not found in sampleDict: {missing_samples}\n"
            f"Available samples: {available}"
        )
    
    for sample in samples:
        if 'TPrange' not in sampleDict[sample]:
            raise ValueError(
                f"Sample '{sample}' is missing 'TPrange' in sampleDict.\n"
                "TPrange is required for tempPlot."
            )

    for sample in samples:
        df = mergeOnGC(cataFolder, sampleDict[sample]).iloc[sampleDict[sample]['TPrange'][0]:sampleDict[sample]['TPrange'][1]]
        df.index = df.index - df.index[0] + sampleDict[sample]['TPrange'][2]
        plt.plot(df['Temperature'], label=sampleDict[sample]['label'])

    vlines = [2.95, 5.84, 6.25, 9.13, 9.56, 12.35]
    for vline in vlines:
        plt.axvline(x=vline, color='red', linestyle='--', linewidth=1)

    plt.legend(fontsize='small')
    plt.xlabel('Time (hour)')
    plt.ylabel('Temperature (°C)')


def tweakTimeOffset(sample, tweak, sampleRef='DR60-26', cataFolder=DEFAULT_DATA_PATH, sampleDict=sampleDict):
    """Compare temperature timing between a sample and a reference sample."""
    if sample not in sampleDict:
        available = ', '.join(sorted(sampleDict.keys()))
        raise KeyError(
            f"Sample '{sample}' not found in sampleDict.\n"
            f"Available samples: {available}"
        )
    if sampleRef not in sampleDict:
        available = ', '.join(sorted(sampleDict.keys()))
        raise KeyError(
            f"Reference sample '{sampleRef}' not found in sampleDict.\n"
            f"Available samples: {available}"
        )

    df = mergeOnGC(cataFolder, sampleDict[sampleRef]).iloc[sampleDict[sampleRef]['TPrange'][0]:sampleDict[sampleRef]['TPrange'][1]]
    df.index = df.index - df.index[0]
    plt.plot(df['Temperature'].loc[5:7], label='ref')
    vlines = [5.84, 6.25]
    for vline in vlines:
        plt.axvline(x=vline, color='red', linestyle='--', linewidth=1)

    df = mergeOnGC(cataFolder, sampleDict[sample]).iloc[sampleDict[sample]['TPrange'][0]:sampleDict[sample]['TPrange'][1]]
    df.index = df.index - df.index[0] + tweak
    plt.plot(df['Temperature'].loc[5:7], label=sampleDict[sample]['label'])

    plt.text(x=0.05, y=0.2, s=f'{sample} : {tweak}', fontsize=16, transform=plt.gca().transAxes)
    plt.legend(fontsize='small')
    plt.xlabel('Time (hour)')
    plt.ylabel('Temperature (°C)')


def carbonBalance(sample, cataFolder=DEFAULT_DATA_PATH, sampleDict=sampleDict):
    """Plot gas concentrations and carbon balance for a single sample."""
    if sample not in sampleDict:
        available = ', '.join(sorted(sampleDict.keys()))
        raise KeyError(
            f"Sample '{sample}' not found in sampleDict.\n"
            f"Available samples: {available}"
        )
    if 'TPrange' not in sampleDict[sample]:
        raise ValueError(
            f"Sample '{sample}' is missing 'TPrange' in sampleDict.\n"
            "TPrange is required for carbonBalance."
        )

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
             label=r'$CO_{2,\mathrm{in}} = CO_{2,\mathrm{out}} + CH_{4,\mathrm{out}} + CO_{\mathrm{out}}$')
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
