"""FastAPI server exposing the AFM analysis pipeline."""

from fastapi import FastAPI
from pydantic import BaseModel

from afm_tda_tools.pipeline import AnalysisPipeline

app = FastAPI()


class PipelineRequest(BaseModel):
    """Request body for :func:`run_pipeline`."""

    data_path: str
    save_path: str
    package_results: bool = False
    upload_to_s3: bool = False
    s3_bucket: str | None = None
    s3_prefix: str = "results"
    exclude_patterns: list[str] | None = None
    width_line: float = 0.1
    max_edge_length: float = 1.0
    matrix_size: int = 3
    delta: float = 0.01
    order: float = 1.0


@app.post("/run")
def run_pipeline(req: PipelineRequest):
    """Execute :class:`AnalysisPipeline` and package results."""
    pipeline = AnalysisPipeline(
        data_path=req.data_path,
        save_path=req.save_path,
        exclude_patterns=req.exclude_patterns,
        width_line=req.width_line,
        max_edge_length=req.max_edge_length,
        matrix_size=req.matrix_size,
        delta=req.delta,
        order=req.order,
    )
    result_location = pipeline.run(
        package=req.package_results,
        upload_s3=req.upload_to_s3,
        s3_bucket=req.s3_bucket,
        s3_prefix=req.s3_prefix,
    )
    return {"result_location": result_location}
