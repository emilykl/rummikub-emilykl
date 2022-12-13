# rummikub-emilykl

Rummikub solver. In beta.

## Usage

To run:

`pip install -r requirements.txt`

and then

`python rummikub.py input_file_path`

where `input_file_path` is the path to the input file. For example:

`python rummikub.py input/input4.txt`

## Benchmarking

The file `benchmark.py` provides a benchmark script for timing how long the solver takes for different input lengths. For a given input file, the script runs the solver on the first tile, then the first 2 tiles, and so on up to the specified max, or the end of the file, whichever comes first. Displays timing results as a graph, prints to command line and optionally saves results to an output file.

For usage info, run

`python benchmark.py --help`
