from magicgui import magicgui, widgets
from napari.types import ImageData, LabelsData, LayerDataTuple
from napari_plugin_engine import (
    HookImplementationMarker,
    HookSpecificationMarker,
    PluginManager,
    HookCaller,
)
from skimage import filters, feature
from typing_extensions import Annotated


specification = HookSpecificationMarker("napari_workflow")
implementation = HookImplementationMarker("napari_workflow")


class Specs:
    @specification
    def threshold(image: ImageData, **kwargs) -> LabelsData:
        ...

    @specification
    def detect_blobs(image: ImageData, **kwargs) -> LayerDataTuple:
        ...





def _blob(func):
    def _wrapped(image, **kwargs):
        blobs = func(image, **kwargs)
        centers = blobs[:, : image.ndim]
        kwargs = dict(
            size=blobs[:, -1],
            opacity=0.5,
            edge_color="yellow",
            face_color="transparent",
        )
        return (centers, kwargs, "points")

    return _wrapped


class Blobs:
    @implementation(specname="detect_blobs")
    def laplacian_of_gaussian(
        image: ImageData,
        min_sigma: Annotated[float, {"min": 0.5, "max": 15, "step": 0.5}] = 2,
        max_sigma: Annotated[float, {"min": 1, "max": 100, "step": 0.5}] = 10,
        num_sigma: Annotated[int, {"min": 1, "max": 20}] = 10,
        threshold: Annotated[float, {"min": 0, "max": 1000, "step": 0.1}] = 100,
        overlap: Annotated[float, {"min": 0, "max": 1, "step": 0.01}] = 0.5,
        log_scale: bool = False,
        exclude_border: bool = False,
    ) -> LayerDataTuple:
        kwargs = locals()
        kwargs.pop("image")
        return _blob(feature.blob_log)(image, **kwargs)

    @implementation(specname="detect_blobs")
    def difference_of_gaussian(
        image: ImageData,
        min_sigma: Annotated[float, {"min": 0.5, "max": 15, "step": 0.5}] = 5,
        max_sigma: Annotated[float, {"min": 1, "max": 100, "step": 0.5}] = 30,
        sigma_ratio: Annotated[float, {"min": 1, "max": 10}] = 1.6,
        threshold: Annotated[float, {"min": 0, "max": 1000, "step": 0.1}] = 1,
        overlap: Annotated[float, {"min": 0, "max": 1, "step": 0.01}] = 0.5,
        exclude_border: bool = False,
    ) -> LayerDataTuple:
        kwargs = locals()
        kwargs.pop("image")
        return _blob(feature.blob_dog)(image, **kwargs)

    @implementation(specname="detect_blobs")
    def determinant_of_hessian(
        image: ImageData,
        min_sigma: Annotated[float, {"min": 0.5, "max": 15, "step": 0.5}] = 1,
        max_sigma: Annotated[float, {"min": 1, "max": 100, "step": 0.5}] = 30,
        num_sigma: Annotated[int, {"min": 1, "max": 20}] = 10,
        threshold: Annotated[float, {"min": 0.1, "max": 100, "step": 0.1}] = 1,
        overlap: Annotated[float, {"min": 0, "max": 1, "step": 0.01}] = 0.5,
        log_scale: bool = False,
    ) -> LayerDataTuple:
        kwargs = locals()
        kwargs.pop("image")
        return _blob(feature.blob_doh)(image, **kwargs)


def _thresh(func):
    # convert global threshold func into one that returns a binary image
    def _wrapped(image, dark_background=True, **kwargs) -> LabelsData:
        thresh = func(image, **kwargs)
        return image >= thresh if dark_background else image <= thresh

    return _wrapped

    
class Thresholds:

    @implementation(specname="threshold")
    def li(image: ImageData, dark_background: bool = True) -> LabelsData:
        return _thresh(filters.threshold_li)(image, dark_background)


    @implementation(specname="threshold")
    def otsu(
        image: ImageData, nbins: int = 256, dark_background: bool = True
    ) -> LabelsData:
        return _thresh(filters.threshold_otsu)(image, dark_background, nbins=nbins)


    @implementation(specname="threshold")
    def isodata(
        image: ImageData, nbins: int = 256, dark_background: bool = True
    ) -> LabelsData:
        return _thresh(filters.threshold_isodata)(image, dark_background, nbins=nbins)


    @implementation(specname="threshold")
    def mean(image: ImageData, dark_background: bool = True) -> LabelsData:
        return _thresh(filters.threshold_mean)(image, dark_background)

    @implementation(specname="threshold")
    def minimum(
        image: ImageData,
        nbins: int = 256,
        max_iter: int = 500,
        dark_background: bool = True,
    ) -> LabelsData:
        return _thresh(filters.threshold_minimum)(
            image, dark_background, nbins=nbins, max_iter=max_iter
        )

    @implementation(specname="threshold")
    def triangle(
        image: ImageData,
        nbins: int = 256,
        dark_background: bool = True,
    ) -> LabelsData:
        return _thresh(filters.threshold_triangle)(image, dark_background, nbins=nbins)

    @implementation(specname="threshold")
    def yen(
        image: ImageData, nbins: int = 256, dark_background: bool = True
    ) -> LabelsData:
        return _thresh(filters.threshold_yen)(image, dark_background, nbins=nbins)

    @implementation(specname="threshold")
    def local(
        image: ImageData,
        block_size: Annotated[int, {"step": 2}] = 5,
        method: Annotated[
            str, {"choices": ("gaussian", "mean", "median")}
        ] = "gaussian",
        offset: float = 0,
    ) -> LabelsData:
        return image > filters.threshold_local(
            image, block_size=block_size, method=method, offset=offset
        )

    @implementation(specname="threshold")
    def niblack(
        image: ImageData,
        window_size: Annotated[int, {"step": 2, "min": 3}] = 15,
        k: Annotated[
            float, {"widget_type": "FloatSlider", "max": 1, "step": 0.01}
        ] = 0.2,
    ) -> LabelsData:
        return image > filters.threshold_niblack(image, window_size=window_size, k=k)

    @implementation(specname="threshold")
    def sauvola(
        image: ImageData,
        window_size: Annotated[int, {"step": 2, "min": 3}] = 15,
        k: Annotated[
            float, {"widget_type": "FloatSlider", "max": 1, "step": 0.01}
        ] = 0.2,
    ) -> LabelsData:
        return image > filters.threshold_sauvola(image, window_size=window_size, k=k)

    @implementation(specname="threshold")
    def hysteresis(
        image: ImageData,
        low: Annotated[
            float, {"widget_type": "FloatSlider", "max": 1000, "step": 1}
        ] = 1,
        high: Annotated[
            float, {"widget_type": "FloatSlider", "max": 1000, "step": 1}
        ] = 500,
    ) -> LabelsData:
        return filters.apply_hysteresis_threshold(image, low, high)

    @implementation(specname="threshold")
    def multiotsu(image: ImageData, classes: int = 3, nbins: int = 256) -> LabelsData:
        import numpy as np

        threshes = filters.threshold_multiotsu(image, classes=classes, nbins=nbins)
        labels = np.zeros_like(image)
        # probably a better way
        for n, thresh in enumerate(threshes):
            labels[image > thresh] = n + 1
        return labels


pm = PluginManager("napari_workflow")
pm.add_hookspecs(Specs)
pm.register(Thresholds, name="Thresholds")
pm.register(Blobs, name="Blobs")


def spec_widget(caller: HookCaller):

    # dict of {func_name: func} for all hook implementations
    methods = {x.function.__name__: x.function for x in caller.get_hookimpls()}

    # make a widget function that will select from the methods
    method = widgets.ComboBox(choices=tuple(methods), name="method")
    container = widgets.Container(widgets=[method], labels=False)
    container.native.layout().addStretch()

    # when the method changes, populate the container with the correct widget
    @method.changed.connect
    def _add_subwidget(event):
        if len(container) > 1:
            container.pop(-1).native.close()
        subwidget = magicgui(methods[event.value], auto_call=True)
        subwidget.margins = (0, 0, 0, 0)
        container.append(subwidget)

    return container


if __name__ == "__main__":
    import napari
    from skimage import data

    viewer = napari.Viewer()
    viewer.add_image(data.coins())
    viewer.window.add_dock_widget(
        spec_widget(pm.hook.detect_blobs), area="right", name="blobs"
    )
    viewer.window.add_dock_widget(
        spec_widget(pm.hook.threshold), area="right", name="threshold"
    )

    napari.run()