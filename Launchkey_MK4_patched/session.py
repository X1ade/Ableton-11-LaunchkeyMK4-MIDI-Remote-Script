from ableton.v3.base import liveobj_valid
from ableton.v3.control_surface.components import ClipSlotComponent as ClipSlotComponentBase
from ableton.v3.control_surface.components import SessionComponent as SessionComponentBase

from .mk4_log import get_logger
_logger = get_logger("session")


class ClipSlotComponent(ClipSlotComponentBase):
    def _on_launch_button_pressed(self):
        session = getattr(getattr(self, "parent", None), "parent", None)  # Scene -> Session
        slot = getattr(self, "_clip_slot", None)

        # Delete modifier: delete the real clip in this slot (if any), swallow launch.
        if getattr(session, "is_delete_modifier", False):
            if liveobj_valid(slot):
                has_clip = bool(getattr(slot, "has_clip", False))
                can_delete = hasattr(slot, "delete_clip")

                if has_clip and can_delete:
                    try:
                        slot.delete_clip()
                    except Exception as e:
                        _logger.exception("Exception during delete_clip(): %r", e)

            return

        super()._on_launch_button_pressed()

    def _feedback_value(self, track, slot_or_clip):
        value = super()._feedback_value(track, slot_or_clip)

        # Check if we're in delete mode
        session = getattr(getattr(self, "parent", None), "parent", None)  # Scene -> Session
        is_delete_mode = getattr(session, "is_delete_modifier", False)

        if is_delete_mode:
            # In delete mode: show red for clips that can be deleted, OFF for empty slots
            slot = getattr(self, "_clip_slot", None)
            if liveobj_valid(slot):
                has_clip = bool(getattr(slot, "has_clip", False))
                can_delete = hasattr(slot, "delete_clip")
                if has_clip and can_delete:
                    return "Session.StopClip"  # Red, non-blinking
                else:
                    # Empty slot or can't delete - show OFF
                    return "Session.NoScene"  # OFF

        return value


class SessionComponent(SessionComponentBase):
    def __init__(self, *a, **k):
        super().__init__(*a, clip_slot_component_type=ClipSlotComponent, **k)

        # Long-press Scene button arms this; pads delete while True.
        self.is_delete_modifier = False

    def set_delete_modifier(self, enabled: bool):
        self.is_delete_modifier = bool(enabled)
        # Update colors for all clip slots when delete mode changes
        self._update_clip_slot_colors()

    def _update_clip_slot_colors(self):
        """Update colors for all clip slots when delete mode changes."""
        # Get the buttons from control surface elements and call set_clip_launch_buttons
        try:
            # Access control surface through canonical_parent
            control_surface = getattr(self, "canonical_parent", None)
            if control_surface and hasattr(control_surface, "elements"):
                elements = control_surface.elements
                if hasattr(elements, "main_pads"):
                    main_pads = elements.main_pads
                    # Call set_clip_launch_buttons with the buttons to trigger framework refresh
                    super().set_clip_launch_buttons(main_pads)
        except Exception as e:
            _logger.exception("SessionComponent._update_clip_slot_colors: exception: %r", e)
