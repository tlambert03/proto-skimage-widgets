from napari_plugin_engine import napari_hook_implementation


@napari_hook_implementation
def napari_experimental_provide_dock_widget():
    from .annotate import annotate_module
    from skimage import filters
    from magicgui import magic_factory

    return [
        magic_factory(f, layout="vertical", auto_call=True)
        for f in annotate_module(filters).values()
    ]
