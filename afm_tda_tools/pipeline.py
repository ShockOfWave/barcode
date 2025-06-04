"""
Module defining the analysis pipeline for AFM data processing.

This pipeline handles preprocessing of raw `.txt` files into CSV,
followed by sequential execution of:
  - autocorrelation analysis
  - persistence homology analysis
  - min–max analysis
  - bottleneck and Wasserstein distance computation

Results are stored in a shared AnalysisData container and exported
to the specified save directory.
"""

import os
import shutil
from typing import Optional

try:
    import boto3
except Exception:  # pragma: no cover - boto3 is optional
    boto3 = None

from afm_tda_tools.analyzers import (
    AutocorrelationAnalyzer,
    BottleneckAnalyzer,
    MinMaxAnalyzer,
    PersistenceAnalyzer,
)
from afm_tda_tools.data import AnalysisData, txt_to_csv_folder


def package_results(save_dir: str) -> str:
    """Compress the output directory into a ``.zip`` archive.

    Parameters
    ----------
    save_dir : str
        Directory containing pipeline results.

    Returns
    -------
    str
        Path to the created archive.
    """
    archive_path = shutil.make_archive(save_dir, "zip", root_dir=save_dir)
    return archive_path


def upload_results_to_s3(
    save_dir: str,
    bucket: str,
    prefix: str = "results",
    client: Optional["boto3.client"] = None,
) -> str:
    """Upload zipped results to an S3 bucket.

    Parameters
    ----------
    save_dir : str
        Directory to compress and upload.
    bucket : str
        Target S3 bucket name.
    prefix : str, optional
        Key prefix in the bucket.
    client : boto3.client, optional
        Pre-configured boto3 client. One will be created if ``None``.

    Returns
    -------
    str
        ``s3://`` URL of the uploaded archive.
    """
    if boto3 is None:
        raise RuntimeError("boto3 is required for S3 uploads")

    archive = package_results(save_dir)
    if client is None:
        client = boto3.client("s3")

    key = f"{prefix}/{os.path.basename(archive)}"
    client.upload_file(archive, bucket, key)
    return f"s3://{bucket}/{key}"


class AnalysisPipeline:
    """
    Orchestrates the full analysis workflow on AFM datasets.

    This class runs a sequence of analyzers on raw AFM data:
      1. Convert raw `.txt` files to CSV.
      2. Autocorrelation analysis.
      3. Persistence homology analysis.
      4. Min–max block-wise analysis.
      5. Pairwise bottleneck and Wasserstein distance computation.

    Parameters
    ----------
    data_path : str
        Path to the directory containing raw `.txt` files.
    save_path : str
        Path to the directory where processed CSV files and results
        will be saved.
    exclude_patterns : list of str, optional
        Filename suffixes to exclude from analysis (default:
        ["(3x3).csv", "_auto.csv", "output.csv"]).
    width_line : float, default 0.1
        Sampling interval (µm) for autocorrelation lag scaling.
    max_edge_length : float, default 1.0
        Maximum edge length for Rips complex construction.
    matrix_size : int, default 3
        Block size for min–max analysis.
    delta : float, default 0.01
        Tolerance for bottleneck distance computation.
    order : float, default 1.0
        Order for Wasserstein distance computation.
    """

    def __init__(
        self,
        data_path,
        save_path,
        exclude_patterns=None,
        width_line=0.1,
        max_edge_length=1.0,
        matrix_size=3,
        delta=0.01,
        order=1.0,
    ):
        self.data_path = data_path
        self.save_path = save_path
        self.exclude_patterns = (
            exclude_patterns
            if exclude_patterns is not None
            else ["(3x3).csv", "_auto.csv", "output.csv"]
        )

        # Shared container for intermediate and final results
        self.data_container = AnalysisData()

        # Initialize analyzers with the shared data container
        self.acf_analyzer = AutocorrelationAnalyzer(self.data_container)
        self.persistence_analyzer = PersistenceAnalyzer(self.data_container)
        self.minmax_analyzer = MinMaxAnalyzer(self.data_container)
        self.bottleneck_analyzer = BottleneckAnalyzer(self.data_container)

        # Default parameters for each analysis step
        self.width_line = width_line
        self.max_edge_length = max_edge_length
        self.matrix_size = matrix_size
        self.delta = delta
        self.order = order

    def run(
        self,
        *,
        package: bool = False,
        upload_s3: bool = False,
        s3_bucket: str | None = None,
        s3_prefix: str = "results",
    ) -> str:
        """
        Execute the full analysis pipeline.

        This method performs the following steps in order:
          1. Preprocess raw `.txt` files into CSV.
          2. Collect processed CSV files, excluding any matching
             `exclude_patterns`.
          3. Run autocorrelation analysis.
          4. Run persistence homology analysis.
          5. Run min–max block-wise analysis.
          6. Compute and save bottleneck and Wasserstein distances.

        Parameters
        ----------
        package : bool, default False
            If ``True``, the output directory is zipped and the path to the
            archive is returned.
        upload_s3 : bool, default False
            When ``True``, results are uploaded to the S3 bucket specified by
            ``s3_bucket`` and the ``s3://`` URL is returned.
        s3_bucket : str, optional
            Target S3 bucket for uploads.
        s3_prefix : str, default "results"
            Key prefix used when uploading to S3.

        Returns
        -------
        str
            Path to the results directory, the created archive, or the uploaded
            ``s3://`` URL depending on the provided options.
        """
        # Step 0: preprocess raw text files
        txt_to_csv_folder(self.data_path, self.save_path)

        # Step 1: collect CSV files for analysis
        files = self.acf_analyzer.get_files(self.save_path, exclude_patterns=self.exclude_patterns)

        # Step 2: autocorrelation
        self.acf_analyzer.analyze(files, width_line=self.width_line)

        # Step 3: persistence diagrams and plots
        self.persistence_analyzer.analyze(files, max_edge_length=self.max_edge_length)

        # Step 4: min–max block-wise analysis
        self.minmax_analyzer.analyze(files, matrix_size=self.matrix_size)

        # Step 5: bottleneck and Wasserstein distances
        self.bottleneck_analyzer.analyze(
            files,
            persistence_analyzer=self.persistence_analyzer,
            delta=self.delta,
            order=self.order,
        )

        # Step 6: save bottleneck analysis results
        save_dir = os.path.join(self.save_path)
        self.bottleneck_analyzer.save_results(save_dir)

        print("Pipeline finished successfully.")

        if upload_s3:
            if not s3_bucket:
                raise ValueError("'s3_bucket' must be provided when 'upload_s3' is True")
            return upload_results_to_s3(save_dir, bucket=s3_bucket, prefix=s3_prefix)
        if package:
            return package_results(save_dir)
        return save_dir
