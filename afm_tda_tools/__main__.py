"""
Command line interface for the AFM data analysis pipeline.

This script provides a CLI entry point for preprocessing raw AFM
``.txt`` files, running a sequence of analyses (autocorrelation,
persistence homology, min–max and diagram distances), and saving
results to the specified directory.  The CLI preserves the argument
structure of the original project for backwards compatibility.

Example
-------
```
python -m afm_tda_tools \
    --data-path /path/to/raw_txt \
    --save-path /path/to/output_dir \
    --width-line 0.02 \
    --max-edge-length 100 \
    --matrix-size 3 \
    --delta-bottleneck 0.01 \
    --order-wasserstein 1.0 \
    --multiply-const 1e9
```
"""

from __future__ import annotations

import argparse

from afm_tda_tools.pipeline import AnalysisPipeline


def main() -> None:
    """
    Parse CLI arguments and execute the AFM analysis pipeline.

    The pipeline will:
      1. Preprocess raw ``.txt`` files into CSV.
      2. Run autocorrelation analysis.
      3. Compute persistence homology diagrams and plots.
      4. Perform min–max block‑wise analysis.
      5. Compute bottleneck and Wasserstein distance matrices.
      6. Save all results under the specified output directory.
    """
    parser = argparse.ArgumentParser(description="Run the full AFM data analysis pipeline.")
    parser.add_argument(
        "--data-path", "-d", required=True, help="Path to directory with raw .txt files."
    )
    parser.add_argument(
        "--save-path", "-s", required=True, help="Path to directory where results will be saved."
    )
    parser.add_argument(
        "--width-line",
        "-w",
        type=float,
        default=0.0196,
        help="Sampling interval for autocorrelation lag axis.",
    )
    parser.add_argument(
        "--max-edge-length",
        "-e",
        type=float,
        default=100.0,
        help="Maximum edge length threshold for Rips complex.",
    )
    parser.add_argument(
        "--matrix-size", "-m", type=int, default=3, help="Block size (n) for n×n min–max analysis."
    )
    parser.add_argument(
        "--delta-bottleneck",
        "-b",
        type=float,
        default=0.01,
        help="Tolerance parameter for bottleneck distance.",
    )
    parser.add_argument(
        "--order-wasserstein",
        "-o",
        type=float,
        default=1.0,
        help="Order parameter for Wasserstein distance.",
    )
    parser.add_argument(
        "--multiply-const",
        "-c",
        type=float,
        default=1e9,
        help="Scaling factor to apply to raw data values.",
    )
    parser.add_argument(
        "--exclude",
        "-x",
        nargs="*",
        default=["(3x3).csv", "_auto.csv", "output.csv"],
        help="Filename suffixes to exclude from analysis.",
    )
    args = parser.parse_args()
    pipeline = AnalysisPipeline(
        data_path=args.data_path,
        save_path=args.save_path,
        exclude_patterns=args.exclude,
        width_line=args.width_line,
        max_edge_length=args.max_edge_length,
        matrix_size=args.matrix_size,
        delta=args.delta_bottleneck,
        order=args.order_wasserstein,
        multiply_const=args.multiply_const,
    )
    pipeline.run()


if __name__ == "__main__":
    main()