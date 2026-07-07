from __future__ import annotations

import logging
import os
import sys
import traceback

from ableton.v3.control_surface import MOMENTARY_DELAY
from ableton.v3.control_surface.mode import ImmediateBehaviour, make_reenter_behaviour

from .launchkey_modes import LaunchkeyModesComponent
from .midi import SET_RELATIVE_ENCODER_MODE


from .mk4_log import get_logger
_logger = get_logger("mappings")


def set_relative_encoder_mode(control_surface):
    try:
        def _send():
            try:
                control_surface.send_midi(SET_RELATIVE_ENCODER_MODE)
            except Exception:
                _logger.exception("Exception in set_relative_encoder_mode._send")
                raise

        return _send

    except Exception:
        _logger.exception("Exception in set_relative_encoder_mode")
        raise


def make_relative_encoder_mode_behavior(control_surface):
    try:
        behavior = make_reenter_behaviour(
            ImmediateBehaviour,
            on_reenter=set_relative_encoder_mode(control_surface),
        )
        return behavior

    except Exception:
        _logger.exception("Exception in make_relative_encoder_mode_behavior")
        raise


def create_launchkey_common_mappings(control_surface):
    try:
        mappings = {}

        mappings["View_Based_Recording"] = dict(record_button="record_button")

        mappings["Scale"] = dict(
            scale_type_control="scale_type_element",
            root_note_control="root_note_element",
        )

        mappings["Keyboard"] = dict(matrix="keyboard")

        mappings["Encoder_Touch"] = dict(touch_controls="encoder_touch_elements")

        mappings["Lower_Pad_Modes"] = dict(
            enable=False,
            is_private=True,
            support_momentary_mode_cycling=False,
            cycle_mode_button="pad_function_button",
            clip_launch=None,
            stop=dict(component="Session", stop_track_clip_buttons="lower_pads"),
            mute=dict(component="Mixer", mute_buttons="lower_pads"),
            solo=dict(component="Mixer", solo_buttons="lower_pads"),
        )

        mappings["Daw_Pad_Modes"] = dict(
            enable=False,
            is_private=True,
            clip=dict(
                modes=[
                    dict(
                        component="Session",
                        clip_launch_buttons="main_pads",
                        #scene_0_launch_button="scene_launch_button",
                    ),
                    dict(component="Scene_Launch_Hold"),
                    dict(
                        component="Session_Navigation",
                        up_button="pad_up_button",
                        down_button="pad_down_button",
                    ),
                    dict(component="Lower_Pad_Modes"),
                ]
            ),
        )

        mappings["Scene_Launch_Hold"] = dict(
            scene_launch_button="scene_launch_button",
        )

        def _cycle_daw_pad_modes():
            try:
                control_surface.component_map["Daw_Pad_Modes"].cycle_mode()
            except Exception:
                _logger.exception("Exception in _cycle_daw_pad_modes")
                raise

        mappings["Main_Pad_Modes"] = dict(
            modes_component_type=LaunchkeyModesComponent,
            enable=False,
            is_private=True,
            mode_selection_control="pad_mode_element",
            null_0=None,
            null_1=None,
            daw=dict(
                component="Daw_Pad_Modes",
                behaviour=make_reenter_behaviour(
                    ImmediateBehaviour,
                    on_reenter=_cycle_daw_pad_modes,
                ),
            ),
            null_3=None,
            chord=None,
            custom_1=None,
            custom_2=None,
            custom_3=None,
            custom_4=None,
            null_9=None,
            null_10=None,
            null_11=None,
            null_12=None,
            arp=None,
            chord_map=None,
            drum=dict(
                component="Drum_Group",
                matrix="drum_pads",
                scroll_page_up_button="pad_up_button",
                scroll_page_down_button="pad_down_button",
            ),
        )

        mappings["Mixer_Encoder_Modes"] = dict(
            enable=False,
            is_private=True,
            level_button="encoder_up_button",
            pan_button="encoder_down_button",
            level=dict(component="Mixer", volume_controls="encoders"),
            pan=dict(component="Mixer", pan_controls="encoders"),
        )

        mappings["Main_Encoder_Modes"] = dict(
            modes_component_type=LaunchkeyModesComponent,
            enable=False,
            is_private=True,
            mode_selection_control="encoder_mode_element",
            null_0=None,
            mixer=dict(
                modes=[
                    dict(component="Mixer_Encoder_Modes"),
                    set_relative_encoder_mode(control_surface),
                ],
                behaviour=make_relative_encoder_mode_behavior(control_surface),
            ),
            plugin=dict(
                modes=[
                    dict(
                        component="Device",
                        parameter_controls="encoders",
                        prev_bank_button="encoder_up_button",
                        next_bank_button="encoder_down_button",
                    ),
                    set_relative_encoder_mode(control_surface),
                ],
                behaviour=make_relative_encoder_mode_behavior(control_surface),
            ),
            null_3=None,
            sends=dict(
                modes=[
                    dict(
                        component="Mixer",
                        send_controls="encoders",
                        prev_send_index_button="encoder_up_button",
                        next_send_index_button="encoder_down_button",
                    ),
                    set_relative_encoder_mode(control_surface),
                ],
                behaviour=make_relative_encoder_mode_behavior(control_surface),
            ),
            transport=dict(
                modes=[
                    dict(
                        component="Transport",
                        arrangement_position_encoder="encoders_raw[0]",
                        loop_start_encoder="encoders_raw[3]",
                        loop_length_encoder="encoders_raw[4]",
                        tempo_coarse_encoder="encoders_raw[7]",
                        set_cue_button="encoder_up_button",
                    ),
                    dict(component="Cue_Point", encoder="encoders_raw[5]"),
                ]
            ),
            custom_1=None,
            custom_2=None,
            custom_3=None,
            custom_4=None,
        )
        _logger.debug("Configured mappings['Main_Encoder_Modes']")

        return mappings

    except Exception:
        _logger.exception("Exception in create_launchkey_common_mappings")
        raise


def create_mappings(control_surface):
    try:
        mappings = create_launchkey_common_mappings(control_surface)

        mappings["Transport"] = dict(
            play_toggle_button="play_button",
            play_pause_button="play_button_with_shift",
            stop_button="stop_button",
            loop_button="loop_button",
            metronome_button="metronome_button",
            capture_midi_button="capture_button",
        )

        mappings["Undo_Redo"] = dict(
            undo_button="undo_button",
            redo_button="undo_button_with_shift",
        )

        mappings["View_Control"] = dict(
            prev_track_button="track_left_button",
            next_track_button="track_right_button",
        )

        mappings["Session_Navigation"] = dict(
            page_left_button="shifted_track_left_button",
            page_right_button="shifted_track_right_button",
        )

        mappings["Volume_Mixer"] = dict(
            enable=False,
            volume_controls="faders",
            master_track_volume_control="master_fader",
        )

        mappings["Fader_Button_Modes"] = dict(
            enable=False,
            is_private=True,
            support_momentary_mode_cycling=False,
            cycle_mode_button="fader_button_mode_button",
            arm=dict(component="Mixer", arm_buttons="fader_buttons"),
            select=dict(component="Mixer", track_select_buttons="fader_buttons"),
        )

        return mappings

    except Exception:
        _logger.exception("Exception in create_mappings")
        raise
