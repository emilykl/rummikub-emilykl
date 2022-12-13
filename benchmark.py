# Benchmarking script for Rummikub solver
# Given an input file, runs solver on all prefixes of the input file,
# e.g. first tile only, then first two tiles, first 3 tiles, etc.
# Creates a dataframe of results, plots the results, and optionally
# outputs the results to a .csv file

import argparse
import os
import time

from collections_extended import bag
import pandas as pd
import plotly.express as px


from rummikub import read_input_file, solve


def main():

    # Parse command line args
    args = arg_parser().parse_args()

    # Read input file
    tiles_input_list = read_input_file(args.input_file_path)

    # Run benchmark
    results_df = solve_all_prefixes(tiles_input_list, max_tiles=args.max_tiles)

    # Print results
    print(f"Benchmark results:\n{results_df}")

    # Plot results
    plot_benchmark(results_df)

    # Output to results file (if given)
    if args.output:
        results_df.to_csv(args.output, index=False)
        print(f"\nWrote benchmark results to {args.output}\n")


def arg_parser():
    parser = argparse.ArgumentParser(
        description="\n".join([
            "Benchmarking script for Rummikub solver.",
            "For the given input file, runs the solver on the first tile,",
            "then the first 2 tiles, and so on up to the given max or the end of the file.",
            "Displays timing results as a graph, prints to command line and optionally saves",
            "results to an output file."
            ])
    )
    parser.add_argument(
        "input_file_path",
        type=str,
        help="Path to input file (required)",
    )
    parser.add_argument(
        "--output",
        "-o",
        type=str,
        help="Path to output results (optional)",
    )
    parser.add_argument(
        "--max-tiles",
        "-m",
        type=int,
        help="Maximum number of tiles to solve",
    )
    return parser


def solve_all_prefixes(tiles_input_list, max_tiles=None):

    results = []
    end_index = max_tiles if max_tiles else len(tiles_input_list)

    for i in range(1, end_index + 1):
        start = time.time()
        solve(bag(tiles_input_list[:i]))
        elapsed = time.time() - start
        results.append(
            {
                "n_tiles": len(tiles_input_list[:i]),
                "sec": elapsed,
            }
        )
    return pd.DataFrame(results)


def plot_benchmark(results_df):
    plot = px.bar(results_df, x="n_tiles", y="sec")
    plot.show()


if __name__ == "__main__":
    main()
