from ableton.v3.base import task
from ableton.v3.control_surface.components import PlayableComponent
class KeyboardComponent(PlayableComponent):
    pass
    is_polyphonic = True
    def __init__(self, *a, **k):
        super().__init__(*a, matrix_always_listenable=True, **k)
        self.pitches = [36]
        self._chord_detection_task = self._tasks.add(task.wait(0.3))
        self._chord_detection_task.kill()
    def _on_matrix_pressed(self, button):
        pitch = button.index
        if self._chord_detection_task.is_running:
            self.pitches.append(pitch)
        else:
            self.pitches = [pitch]
            self._chord_detection_task.restart()
    def _update_led_feedback(self):
        return None