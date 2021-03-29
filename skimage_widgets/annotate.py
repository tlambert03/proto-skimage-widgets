import builtins
import inspect
from types import FunctionType
from typing_extensions import Annotated
import re
from docstring_parser import parse
from ast import literal_eval

HIDDEN = {"skimage.filters._median.median": {"behavior"}}

BIND_DEFAULT = {"output", "out", "cval", "selem"}
NAME_MAP = {
    "data": "napari.types.ImageData",
    "image": "napari.types.ImageData",
    "mask": "napari.types.LabelsData",
}
DOC_TYPE_MAP = {
    "array of bool": "napari.types.ImageData",
    "array": "napari.types.ImageData",
    "ndarray": "napari.types.ImageData",
}


def gather_functions(module):

    return {
        n: getattr(module, n)
        for n in dir(module)
        if not n.startswith("_")
        if isinstance(getattr(module, n), FunctionType)
    }


def from_builtins(word):
    aliases = {
        "string": "str",
        "boolean": "bool",
        "integer": "int",
        "scalar": "float",
    }
    word = aliases.get(word, word)
    if word in dir(builtins):
        return getattr(builtins, word)


def bound_default(param):
    return Annotated[type(param.default), {"bind": param.default}]


def guess_type(param: inspect.Parameter, doc_type):
    if param.annotation is not param.empty:
        return param.annotation

    if param.name in BIND_DEFAULT:
        return bound_default(param)

    if param.name in NAME_MAP:
        return NAME_MAP[param.name]
    if not doc_type:
        return type(param.default)

    # a couple manual corrections that should be fixed with PRs
    doc_type = doc_type.replace("‘", "")  # filters.median
    doc_type = doc_type.replace("{int, function}", "int or callable")

    _builtin = from_builtins(doc_type.split("or")[0].strip())
    if not _builtin:
        _builtin = from_builtins(doc_type.split(",")[0].strip())
    if _builtin:
        return _builtin

    of_match = re.match(r"(iterable|tuple|sequence|list) of ([^\s]+)", doc_type)
    if of_match:
        import typing

        a, b = of_match.groups()
        container = getattr(typing, a.title())
        type_ = from_builtins(b.rstrip("s"))
        return container[type_]

    if doc_type in DOC_TYPE_MAP:
        return DOC_TYPE_MAP[doc_type]

    if "mask" in param.name:
        return "napari.types.LabelsData"
    if "array of bool" in doc_type:
        return "napari.types.LabelsData"
    if "array" in doc_type:
        return "napari.types.ImageData"

    try:
        val = literal_eval(doc_type)
        if isinstance(val, set):
            return Annotated[str, {"choices": list(val)}]
    except Exception:
        pass

    if param.default is not param.empty:
        return type(param.default)


def guess_return_type(doc):

    if "array of bool" in doc.type_name:
        return "napari.types.LabelsData"
    if doc.type_name in DOC_TYPE_MAP:
        return DOC_TYPE_MAP[doc.type_name]
    if "image" in doc.description:
        return "napari.types.ImageData"
    if "array" in doc.type_name:
        return "napari.types.ImageData"


def annotate_function(function):
    sig = inspect.signature(function)
    doc_params = {p.arg_name: p.type_name for p in parse(function.__doc__).params}
    for k, v in list(doc_params.items()):
        if "," in k:
            for split_key in k.split(","):
                doc_params[split_key.strip()] = v
            del doc_params[k]

    hidden = HIDDEN.get(f"{function.__module__}.{function.__name__}", {})
    for p in sig.parameters.values():
        if p.name in hidden:
            annotation = bound_default(p)
        else:
            annotation = guess_type(p, doc_params.get(p.name))
        function.__annotations__[p.name] = annotation

    doc_returns = parse(function.__doc__).returns
    # Note skimage.filters.inverse has no return doc string
    # Note skimage.filters.threshold should be a different type ....
    if doc_returns is not None:
        function.__annotations__["return"] = guess_return_type(doc_returns)


def annotate_module(module):
    if isinstance(module, str):
        import importlib

        module = importlib.import_module(module)

    functions = gather_functions(module)
    for func in functions.values():
        annotate_function(func)
    return functions
