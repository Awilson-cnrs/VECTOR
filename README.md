# VECTORtools

Catalysis data analysis: loads GDS (gas flows), OPC (temperature), and GC (gas concentrations) instrument data, merges by timestamp, and produces conversion/selectivity plots.

## Setup

Install dependencies with Conda:

    conda env create -f environment.yml
    conda activate vector

No installation step is required — just run the Jupyter notebook or import `VECTORtools` directly.

## Usage

```python
from VECTORtools import mergeOnGDS, triPlot, carbonBalance, sampleDict

# Single sample overview
carbonBalance('DR60-40')

# Compare multiple samples
triPlot(['DR60-40', 'DR58-3_2', 'DR60-26_2'])
```

Set `DATA_PATH` environment variable to override the default data directory (`Z:/RawData/TestCata`).
