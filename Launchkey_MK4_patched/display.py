from dataclasses import dataclass
from enum import IntEnum
from typing import Optional, Tuple

from ableton.v2.base import liveobj_valid
from ableton.v3.base import as_ascii
from ableton.v3.control_surface.display import DisplaySpecification

DISPLAY_WIDTH = 16


def display_text_bytes(line):
    return as_ascii((line or '')[:DISPLAY_WIDTH])


def liveobj_name(obj):
    return obj.name if liveobj_valid(obj) else None


def find_parent_track(obj):
    while liveobj_valid(obj) and not hasattr(obj, 'clip_slots'):
        obj = obj.canonical_parent
    return obj if liveobj_valid(obj) else None


def parameter_display_name(parameter):
    return parameter.name if liveobj_valid(parameter) else '-'


class Config(IntEnum):
    two_line = 97
    three_line = 98
    two_by_four = 99


@dataclass
class TargetContent:
    config: Optional[Config] = Config.two_line
    lines: Optional[Tuple[str, ...]] = ()
    trigger: Optional[bool] = False


@dataclass
class DisplayContent:
    static: Optional[TargetContent] = None
    daw_label: Optional[TargetContent] = None
    mixer_label: Optional[TargetContent] = None
    encoders: Tuple[Optional[Tuple[TargetContent, TargetContent]], ...] = ()
    faders: Tuple[Optional[Tuple[TargetContent, TargetContent]], ...] = ()

    @classmethod
    def with_parameters(cls, state, released_encoder_index=None, **k):
        def parameter_header(element, is_encoder):
            if is_encoder and state.main_encoder_modes.selected_mode == 'transport':
                return 'Transport'
            if (not is_encoder or state.main_encoder_modes.selected_mode != 'plugin') and liveobj_valid(element.mapped_object.canonical_parent):
                return liveobj_name(find_parent_track(element.mapped_object))
            return liveobj_name(state.target_track.target_track)

        def parameter_content(elements, is_encoders=False):
            return tuple(
                TargetContent(
                    config=Config.three_line,
                    lines=(parameter_header(element, is_encoders), parameter_display_name(element.mapped_object), str(element.mapped_object))
                    if liveobj_valid(element.mapped_object) else ('-', '-', '-'),
                    trigger=is_encoders and i == released_encoder_index,
                )
                for i, element in enumerate(elements)
            )

        return cls(
            encoders=parameter_content(state.elements.encoders, is_encoders=True),
            faders=parameter_content(state.elements.faders + [state.elements.master_fader]) if hasattr(state.elements, 'faders') else (),
            **k,
        )


def default_label_content():
    return DisplayContent(daw_label=TargetContent(lines=('Clip 1/2',)), mixer_label=TargetContent(lines=('Level',)))


def track_and_device_names(state):
    return TargetContent(lines=(liveobj_name(state.target_track.target_track), liveobj_name(state.device.device) or '-'))


def transport_static_content():
    return TargetContent(config=Config.two_by_four, lines=('Transport', 'Scrb', '', '', 'LPS', 'LPE', 'Mark', '', 'BPM'))


def mode_label_content(state):
    mixer_mode = getattr(state.mixer_encoder_modes, 'selected_mode', None)
    return (
        TargetContent(lines=('Clip 1/2',)),
        TargetContent(lines=(mixer_mode.title() if mixer_mode else 'Level',)),
    )


def render(state):
    daw_label, mixer_label = mode_label_content(state)
    if state.encoder_touch.last_released_index is not None:
        return DisplayContent.with_parameters(
            state,
            released_encoder_index=state.encoder_touch.last_released_index,
            daw_label=daw_label,
            mixer_label=mixer_label,
        )
    if state.main_encoder_modes.selected_mode == 'transport':
        return DisplayContent(static=transport_static_content(), daw_label=daw_label, mixer_label=mixer_label)
    return DisplayContent(static=track_and_device_names(state), daw_label=daw_label, mixer_label=mixer_label)


def protocol(elements):
    def display(content: DisplayContent):
        if content:
            display_content('static', content.static, show_immediately=True)
            display_content('daw_label', content.daw_label)
            display_content('mixer_label', content.mixer_label)
            for i, encoder in enumerate(content.encoders):
                display_content('encoder_{}'.format(i), encoder)
            for i, fader in enumerate(content.faders):
                display_content('fader_{}'.format(i), fader)

    def display_content(name, content: TargetContent, show_immediately=False):
        if content and content.lines:
            command = getattr(elements, '{}_display_command'.format(name))
            command.send_data(
                content.config,
                tuple(display_text_bytes(line) for line in content.lines),
                show_immediately=show_immediately,
                trigger=content.trigger,
            )

    return display


# NOTE: the real Live 11.3.11 DisplaySpecification uses a View-based DSL
# (create_root_view / CompoundView / NotificationView) that is fundamentally
# different from the render()/protocol() pattern this file was built around
# (confirmed via MK4_API_Diagnostic - see notes.txt). Reconstructing that DSL
# blind risks more broken-script restart cycles, and no stock reference script
# is available on this machine to copy the real usage from. Until that DSL is
# implemented properly, the LCD screen is left inert (no track/device/transport
# text) so the rest of the control surface (pads, encoders, faders, session,
# transport) can load and work. `render`/`protocol` above are kept, unused, so
# this is a one-line change to restore once the View DSL is implemented.
display_specification = DisplaySpecification()
