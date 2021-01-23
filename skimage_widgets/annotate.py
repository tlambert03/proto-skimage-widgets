import builtins
import inspect
from types import FunctionType
from typing_extensions import Annotated
import re
from docstring_parser import parse
from ast import literal_eval


def gather_functions(module):

    functions = {
        n: getattr(module, n)
        for n in dir(module)
        if not n.startswith("_")
        if isinstance(getattr(module, n), FunctionType)
    }
    return functions


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


def guess_type(param: inspect.Parameter, doc_type):
    if param.annotation is not param.empty:
        return param.annotation
    if param.name in ("image", "data"):
        return "napari.types.ImageData"
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


def annotate_function(function):
    sig = inspect.signature(function)
    doc_params = {p.arg_name: p.type_name for p in parse(function.__doc__).params}
    for k, v in list(doc_params.items()):
        if "," in k:
            for split_key in k.split(","):
                doc_params[split_key.strip()] = v
            del doc_params[k]
    for p in sig.parameters.values():
        function.__annotations__[p.name] = guess_type(p, doc_params.get(p.name))


def annotate_module(module):
    functions = gather_functions(module).values()
    for func in functions:
        annotate_function(func)
    return functions
