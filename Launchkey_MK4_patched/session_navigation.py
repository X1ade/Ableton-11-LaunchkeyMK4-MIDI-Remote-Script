from ableton.v3.base import depends, liveobj_valid, song
from ableton.v3.control_surface.components import SessionNavigationComponent as SessionNavigationComponentBase


def select(track):
    try:
        if liveobj_valid(track):
            song().view.selected_track = track
            return True
    except RuntimeError:
        pass
    return False


class SessionNavigationComponent(SessionNavigationComponentBase):
    pass
    @depends(session_ring=None)
    def __init__(self, session_ring=None, *a, **k):
        super().__init__(*a, session_ring=session_ring, **k)
        self._session_ring = session_ring
        self.register_slot(self._page_horizontal.scrollable, self._on_tracks_scrolled, 'scrolled')
    def _on_tracks_scrolled(self):
        if self._session_ring.track_offset in range(len(self.song.tracks)):
            select(self.song.tracks[self._session_ring.track_offset])