# Demonstration of Quantum Speedup for Bernstein-Vazirani Algorithm
 
## `data`
Please visit the following Dropbox link (https://www.dropbox.com/sh/jkcun8d842w9p4e/AAAHDhB5j-8qlTv4TltMoZrpa?dl=) to access the data. Once you have cloned the GitHub repo, please add the files in the folder above to the `data/` folder.

Note that the data files are too large to be pushed back to GitHub, so please add `data/` to your .gitignore file.

Circuits and calibration are in the `data/` folder. Read `data/readme_data.ipynb` about how the data is organized and how to extract relevant information. 

## `results`
Raw values for the plotted results are in this folder. 

## `plots`
All the plots are in this folder

## `analysis`
`data` is converted to `results` and `plots` here. Suggested order of files:

`manipulating_bitstring.py` -> functions to analyze rawdata given as a dictionary of bitcounts

`simulation.py` -> simulation of ideal circuits 

`rawdata_to_rawdf.py` -> convert `rawdata` to `rawdf` (pandas DataFrame)

`ps_from_rawdf.py` -> compute success probabilities

`tts_from_rawdf.py` -> compute TTS

`bv-6_output_distribution`.ipynb -> Plotting output distributions

`circuit_duration_from_calibration_data.py` -> calculate circuit duration

`circuit_durations.ipynb` -> exemplifty `circuit_duration_from_calibration_data.py`

`tts_calculation_without_bootstrapping.ipynb` -> calculating TTS from `rawdf`

`bootstrapping.py` -> bootstrapping TTS data in order to compute error bars

`tts_calculation_with_bootstrapping.ipynb` -> calculating TTS from `rawdf` with bootstrapping

`generate_bootstrapped_linear_fits.nb` -> compute fits for TTS incorporating bootstrapping

`plots_with_fits.nb` -> generate plots for TTS and lambda
