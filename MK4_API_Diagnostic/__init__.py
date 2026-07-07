from __future__ import absolute_import, print_function, unicode_literals

import inspect
import os
import traceback

_HERE = os.path.dirname(os.path.abspath(__file__))
_OUT_PATH = os.path.join(_HERE, os.pardir, "mk4_api_dump.txt")

_MODULES = (
    "ableton.v2.base",
    "ableton.v3.base",
    "ableton.v2.control_surface",
    "ableton.v2.control_surface.capabilities",
    "ableton.v2.control_surface.control",
    "ableton.v2.control_surface.mode",
    "ableton.v2.control_surface.elements",
    "ableton.v2.control_surface.midi",
    "ableton.v3.control_surface",
    "ableton.v3.control_surface.capabilities",
    "ableton.v3.control_surface.components",
    "ableton.v3.control_surface.controls",
    "ableton.v3.control_surface.mode",
    "ableton.v3.control_surface.display",
    "ableton.v3.control_surface.elements",
    "ableton.v3.control_surface.midi",
)

# (module, class name) pairs for every ableton class this script constructs directly.
# We dump the real constructor signature for each instead of guessing again.
_SIGNATURES = (
    ("ableton.v3.control_surface.display", "DisplaySpecification"),
    ("ableton.v3.control_surface.display", "Renderable"),
    ("ableton.v3.control_surface", "ControlSurfaceSpecification"),
    ("ableton.v3.control_surface", "Skin"),
    ("ableton.v3.control_surface", "LiveObjSkinEntry"),
    ("ableton.v3.control_surface", "ElementsBase"),
    ("ableton.v2.control_surface", "InternalParameter"),
    ("ableton.v2.control_surface.control", "StepEncoderControl"),
)


def _names_of(mod):
    names = getattr(mod, "__all__", None)
    if names:
        return sorted(names)
    return sorted(n for n in dir(mod) if not n.startswith("_"))


def _check(lines, modname):
    try:
        mod = __import__(modname, fromlist=["*"])
        lines.append("=== {} ===".format(modname))
        lines.append(", ".join(_names_of(mod)))
    except Exception:
        lines.append("=== {} (IMPORT FAILED) ===".format(modname))
        lines.append(traceback.format_exc())
    lines.append("")


def _signature_of(lines, modname, clsname):
    label = "{}.{}".format(modname, clsname)
    try:
        mod = __import__(modname, fromlist=["*"])
        cls = getattr(mod, clsname)
        lines.append("=== SIGNATURE {} ===".format(label))
        lines.append("type: {!r}".format(type(cls)))
        fields = getattr(cls, "_fields", None)
        if fields:
            lines.append("_fields: {}".format(fields))
            defaults = getattr(cls, "_field_defaults", None)
            if defaults:
                lines.append("_field_defaults: {}".format(defaults))
        try:
            sig = inspect.signature(cls)
            lines.append("signature: {}".format(sig))
        except (TypeError, ValueError):
            try:
                sig = inspect.signature(cls.__init__)
                lines.append("__init__ signature: {}".format(sig))
            except (TypeError, ValueError) as e:
                lines.append("signature unavailable: {!r}".format(e))
    except Exception:
        lines.append("=== SIGNATURE {} (FAILED) ===".format(label))
        lines.append(traceback.format_exc())
    lines.append("")


def _version_info(lines):
    lines.append("=== Live version ===")
    try:
        import Live
        app = Live.Application.get_application()
        v = app.get_major_version(), app.get_minor_version(), app.get_bugfix_version()
        lines.append("Live version: {}.{}.{}".format(*v))
    except Exception:
        lines.append("Could not read Live version:")
        lines.append(traceback.format_exc())
    lines.append("")


def _run_diagnostic():
    lines = []
    _version_info(lines)
    for m in _MODULES:
        _check(lines, m)
    for modname, clsname in _SIGNATURES:
        _signature_of(lines, modname, clsname)

    text = "\n".join(lines)
    for path in (_OUT_PATH, os.path.join(_HERE, "mk4_api_dump.txt")):
        try:
            with open(path, "w") as f:
                f.write(text)
            break
        except Exception:
            continue


_run_diagnostic()


def get_capabilities():
    return {}


def create_instance(c_instance):
    return None
