from __future__ import absolute_import, print_function, unicode_literals

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
