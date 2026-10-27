"""VECTORtools — Catalysis data analysis and visualization.

Loads GDS (gas flows), OPC (temperature), and GC (gas concentrations) instrument
data, merges by timestamp, and produces conversion/selectivity plots.
"""

from .loaders import loadGDS, loadOPC, loadGC, loadMS
from .merge import mergeOnGDS, mergeOnGC
from .calc import calcConv, calcSelect
from .plots import OverviewPlot, triPlot, tempPlot, tweakTimeOffset, carbonBalance
from .samples import sampleDict, validate_sample

__all__ = [
    # Loaders
    'loadGDS', 'loadOPC', 'loadGC', 'loadMS',
    # Merge
    'mergeOnGDS', 'mergeOnGC',
    # Calculations
    'calcConv', 'calcSelect',
    # Plots
    'OverviewPlot', 'triPlot', 'tempPlot', 'tweakTimeOffset', 'carbonBalance',
    # Samples
    'sampleDict', 'validate_sample',
]
