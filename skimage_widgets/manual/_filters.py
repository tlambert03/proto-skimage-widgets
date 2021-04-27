from skimage import filters as _skf
from napari.types import ImageData, LabelsData
from typing_extensions import Annotated
import numpy as np

_THRESHOLDS = ("isodata", "li", "mean", "minimum", "otsu", "triangle", "yen")
_EDGES = (
    "farid",
    "farid_h",
    "farid_v",
    "laplace",
    "prewitt",
    "prewitt_h",
    "prewitt_v",
    "roberts",
    "roberts_neg_diag",
    "roberts_pos_diag",
    "scharr",
    "scharr_h",
    "scharr_v",
    "sobel",
    "sobel_h",
    "sobel_v",
)
_RIDGES = ("frangi", "hessian", "meijering", "sato")
_DENOISE = ("gaussian", "median", "unsharp_mask")


def threshold(
    method: Annotated[str, {"choices": _THRESHOLDS}],
    image: ImageData,
    dark_background=True,
) -> LabelsData:
    thresh = getattr(_skf, f"threshold_{method}")(image)
    return image >= thresh if dark_background else image <= thresh



def edges(method: Annotated[str, {"choices": (_EDGES)}], image: ImageData) -> ImageData:
    return getattr(_skf, method)(image)


def ridges(method: Annotated[str, {"choices": _RIDGES}], image: ImageData) -> ImageData:
    kwargs = {}
    if method in ("hessian", "sato"):
        # avoid warning
        kwargs["mode"] = "reflect"

    return getattr(_skf, method)(image, **kwargs)


def denoise(
    method: Annotated[str, {"choices": _DENOISE}], image: ImageData
) -> ImageData:
    kwargs = {}
    return getattr(_skf, method)(image, **kwargs)


def wiener(
    image: ImageData,
    K: Annotated[float, {"min": 0.001, "max": 1, "step": 0.01}] = 0.25,
    sigma: Annotated[float, {"widget_type": "FloatSlider", "min": 0.1, "max": 2}] = 1,
) -> ImageData:
    def _gauss_filter(r, c, sigma=1):
        return np.exp(-np.hypot(r, c) / sigma)

    return _skf.wiener(
        image, impulse_response=_gauss_filter, K=K, filter_params={"sigma": sigma}
    )
