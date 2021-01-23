from skimage import filters
import pytest
from skimage_widgets.annotate import annotate_module
from magicgui import magicgui


@pytest.mark.parametrize("function", list(annotate_module(filters).values()))
def test_widgets(function):
    magicgui(function)
