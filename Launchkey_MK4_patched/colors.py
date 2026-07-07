from ableton.v2.base import liveobj_valid, memoize
from ableton.v3.control_surface import STANDARD_COLOR_PALETTE, STANDARD_FALLBACK_COLOR_TABLE
from ableton.v3.control_surface.elements import ColorPart, ComplexColor, SimpleColor
BLINK_CHANNEL = 1
PULSE_CHANNEL = 2
def _find_nearest_color(rgb_table, src_hex_color):
    def hex_to_channels(color_in_hex):
        return ((color_in_hex & 16711680) >> 16, (color_in_hex & 65280) >> 8, color_in_hex & 255)
    def squared_distance(color):
        return sum((a - b) ** 2 for a, b in zip(hex_to_channels(src_hex_color), hex_to_channels(color[1])))
    return min(rgb_table, key=squared_distance)[0]
def liveobj_color_to_value_from_palette(obj, palette, fallback_table=None):
    if not liveobj_valid(obj):
        return 0
    color = obj.color
    try:
        return palette[color]
    except (KeyError, IndexError):
        if fallback_table is not None:
            return _find_nearest_color(fallback_table, color)
        return 0
@memoize
def make_simple_color(value):
    return SimpleColor(value)
def make_color_for_liveobj(obj):
    color = make_simple_color(liveobj_color_to_value_from_palette(obj, palette=STANDARD_COLOR_PALETTE, fallback_table=STANDARD_FALLBACK_COLOR_TABLE))
    if liveobj_valid(obj) and (not color.midi_value):
        return Rgb.WHITE_HALF
    else:
        return color
def make_animated_color(value, animation_channel):
    return ComplexColor((ColorPart(0), ColorPart(value, animation_channel)))
class Mono:
    OFF = SimpleColor(0)
    DIM = SimpleColor(32)
    ON = SimpleColor(127)
    BLINK = make_animated_color(127, BLINK_CHANNEL)
class Rgb:
    OFF = SimpleColor(0)
    WHITE = SimpleColor(3)
    WHITE_HALF = SimpleColor(1)
    RED = SimpleColor(5)
    RED_HALF = SimpleColor(7)
    RED_BLINK = make_animated_color(5, BLINK_CHANNEL)
    RED_PULSE = make_animated_color(5, PULSE_CHANNEL)
    GREEN = SimpleColor(21)
    GREEN_BLINK = make_animated_color(21, BLINK_CHANNEL)
    GREEN_PULSE = make_animated_color(21, PULSE_CHANNEL)
    BLUE = SimpleColor(41)
    BLUE_HALF = SimpleColor(43)
    LIGHT_BLUE = SimpleColor(37)
    DARK_BLUE = SimpleColor(49)
    ORANGE = SimpleColor(96)
    ORANGE_HALF = SimpleColor(83)