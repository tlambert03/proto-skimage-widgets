from skimage import feature as _skf
from napari.types import ImageData, LabelsData, LayerDataTuple, PointsData
from typing_extensions import Annotated
import numpy as np


def blob_log(
    image: ImageData,
    min_sigma: Annotated[float, {"min": 0.5, "max": 15, "step": 0.5}] = 1.5,
    max_sigma: Annotated[float, {"min": 1, "max": 100, "step": 0.5}] = 4,
    num_sigma: Annotated[int, {"min": 1, "max": 20}] = 6,
    threshold: Annotated[float, {"min": 0, "max": 1000, "step": 0.1}] = 150,
    overlap: Annotated[float, {"min": 0, "max": 1, "step": 0.01}] = 0.5,
    log_scale: bool = False,
) -> LayerDataTuple:
    blobs = _skf.blob_log(
        image,
        min_sigma=min_sigma,
        max_sigma=max_sigma,
        num_sigma=num_sigma,
        threshold=threshold,
        overlap=overlap,
        log_scale=log_scale,
    )
    centers = blobs[:, : image.ndim]
    kwargs = dict(
        size=blobs[:, -1], opacity=0.5, edge_color="yellow", face_color="transparent"
    )
    return (centers, kwargs, "points")
