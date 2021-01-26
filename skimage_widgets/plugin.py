from napari_plugin_engine import napari_hook_implementation


@napari_hook_implementation
def napari_experimental_provide_function_widget():
    from .annotate import annotate_module
    from skimage import filters

    return list(annotate_module(filters).values())
