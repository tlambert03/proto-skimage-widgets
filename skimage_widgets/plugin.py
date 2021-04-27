from magicgui import magic_factory
from napari_plugin_engine import napari_hook_implementation
from .manual import _filters, _feature

# @napari_hook_implementation
# def napari_experimental_provide_dock_widget():
#     from .annotate import annotate_module

#     opts = dict(auto_call=True)
#     return [
#         magic_factory(x, **opts) for x in annotate_module("skimage.filters").values()
#     ]


# @napari_hook_implementation
# def napari_experimental_provide_dock_widget():
#     return [
#         magic_factory(x, auto_call=False)
#         for x in [
#             _filters.threshold,
#             _filters.edges,
#             _filters.ridges,
#             _filters.denoise,
#             _filters.wiener,
#             _feature.blob_log,
#         ]
#     ]

@napari_hook_implementation
def napari_experimental_provide_dock_widget():
    return [
        magic_factory(x, auto_call=True)
        for x in [
            _filters.threshold, 
            _filters.edges,
            _filters.ridges,
            _filters.denoise,
            _filters.wiener,
            _feature.blob_log,
        ]
    ]
