# Launchkey MK4 — Live 11.3.11 Compatibility Patch (unofficial, unstable)

> **TL;DR: if you can, just use Ableton Live 12 with the Launchkey MK4.** Novation's
> official MIDI Remote Script is written against the Live 12 `ableton.v3` framework,
> and that's what the hardware is actually supported on. This repo exists only because
> the author is stuck on Live 11.3.11 and wanted *some* of the MK4's functionality
> back. It is a patched, partially-working port, not a substitute for the real thing.

## What this is

Novation's stock Launchkey MK4 MIDI Remote Script imports names from the
`ableton.v3` control-surface framework that simply don't exist in the copy of that
framework shipped with Live 11.3.11 (it's written for Live 12). Loading it as-is
crashes the script at import time before anything on the hardware works.

This repo is a hand-patched copy of that script (`Launchkey_MK4_patched/`), fixed up
import-by-import against the *real* Live 11.3.11 API surface, so it loads and the
core hardware functionality (pads, encoders, faders, session/clip launching,
transport, drum group, scale, mixer) works.

## Methodology

Ableton doesn't publish an API diff between point releases, and generic decompiled
references of "Live 11" turned out to be unreliable — more than once a fix based on
a decompiled snapshot was proven wrong by what the real, installed framework
actually does. So this repo does not trust any reference documentation or decompiled
source. Every fix here is driven by ground truth captured directly from the user's
own Ableton Live 11.3.11 installation:

1. **`MK4_API_Diagnostic/`** — a throwaway MIDI Remote Script that, on load, imports
   every `ableton.v2`/`ableton.v3` submodule this script depends on and dumps:
   - every importable name in each module (`dir()`/`__all__`)
   - the real constructor signature (`inspect.signature`), `_fields` (for
     `NamedTuple`-based classes), docstring, and public attributes of every
     `ableton.*` class this script constructs directly (`DisplaySpecification`,
     `ControlSurfaceSpecification`, `Skin`, `View`, etc.)
   to `mk4_api_dump.txt`.
2. That dump gets pasted into **`notes.txt`** alongside the actual Ableton crash log
   (`RemoteScriptError` tracebacks from Live's own log) for the current failure.
3. Every fix is cross-checked against that dump before being written — if a name
   isn't in the dump, it does not exist in this Live 11.3.11 install, full stop, no
   matter what any design doc/plan/decompiled reference claims.
4. Fix, commit, push, reload in Live, repeat.

This is why `notes.txt` is deliberately kept and committed: it's the accumulated
ground-truth record for this specific Live 11.3.11 install, not scratch space.

## What was actually changed vs. the Live 12 script

- **Import path fixes**: several names the stock script imports from
  `ableton.v3.base` (`liveobj_valid`, `move_current_song_time`) only exist in
  `ableton.v2.base` in Live 11.3.11. Fixed in `colors.py`, `drum_group.py`,
  `internal_parameter.py`, `session.py`, `session_navigation.py`, `transport.py`,
  `display.py`.
- **Local replacements for names that don't exist anywhere in Live 11.3.11**
  (confirmed absent from both `ableton.v2.base` and `ableton.v3.base`):
  - `song()` (module-level accessor) — `session_navigation.py`'s `select()` helper
    now takes `song` as a parameter instead, called with the component's own
    `self.song`.
  - `round_to_multiple()` — reimplemented locally in `transport.py` (floors to the
    nearest multiple, used for bar-quantized transport scrubbing).
  - `find_parent_track()` — reimplemented locally in `display.py` (walks
    `canonical_parent` up the Live Object Model until it finds an object with
    `.clip_slots`, i.e. a Track).
  - `parameter_display_name()` — reimplemented locally in `display.py` as a thin
    wrapper around a device `Parameter`'s `.name`.
  - `liveobj_color_to_value_from_palette()` — reimplemented locally in `colors.py`
    (palette dict lookup with a nearest-RGB-distance fallback).
- **LCD screen content is disabled.** This is the big one. The stock script's
  `display.py` builds its `DisplaySpecification` with a `render(state)` /
  `protocol(elements)` pair. The real Live 11.3.11 `DisplaySpecification` doesn't
  accept those arguments at all — its actual signature is
  `DisplaySpecification(create_root_view, protocol, notifications)`, where
  `create_root_view` returns a tree of `View` objects (composed via `CompoundView`
  / `NotificationView` / `DisconnectedView`) from a completely different, more
  complex DSL than the `render(state) -> DisplayContent` pattern the stock script
  uses. No official Ableton script using this exact DSL was available on this
  machine to use as a working reference, and guessing at an unfamiliar, deeply
  nested API was judged too likely to produce more broken-script cycles. Per an
  explicit decision made while working through this, the LCD is left inert for now
  (`DisplaySpecification()` with no arguments) so everything else can load and
  work. The old `render()`/`protocol()` functions are still in `display.py`,
  unused, so restoring real LCD content is a scoped, self-contained follow-up
  rather than something that has to be rediscovered from scratch.
- Miscellaneous defensive-coding wrapping (`try`/`except` + logging) added around
  a few call sites that touch the now-disabled display system, so failures there
  degrade gracefully instead of crashing the whole control surface.

## Known limitations

- **The LCD screen shows nothing.** No track/device names, no transport readout,
  no mode labels. This is the single biggest functional gap vs. the real Live 12
  script.
- **Only this script's own use cases have been exercised.** Fixes were made
  reactively, against whatever `RemoteScriptError` actually showed up next in Live's
  log. Code paths that haven't been hit yet (edge cases in modes, device banking,
  drum racks with nested chains, etc.) may still crash — `find_parent_track()` in
  particular is a best-effort reimplementation and may not handle deeply nested
  rack/chain hierarchies correctly.
- **This has only been verified against one specific installation**: Ableton Live
  11.3.11, whatever exact build of the `ableton.v3`/`ableton.v2` frameworks ships
  with it. It is not guaranteed to work on any other Live 11.x point release —
  point releases are assumed not to change the scripting framework, but that
  assumption hasn't been verified beyond this one install.
- **No automated tests.** Verification is entirely "does it crash in the real Live
  log," there is no test harness and no way to run this outside a real Ableton
  install.
- This is a **living, reactive patch**, not a finished product. Expect to find and
  fix more crashes as more of the hardware's functionality gets exercised.

## Recommendation

If you have any option to run **Ableton Live 12** with your Launchkey MK4, do
that instead and use Novation's official, supported script. This repo is a
stopgap for being stuck on Live 11, not a recommended way to run this hardware.
If you're reading this because you found yourself in the same situation — stuck
on Live 11.3.x with a Launchkey MK4 and a script that won't load — the
methodology above (build a diagnostic script, get ground truth from your own
install, fix only what the ground truth contradicts) is the approach that
actually worked here, as opposed to guessing from generic Live 11 references.

## Repo layout

- `Launchkey_MK4_patched/` — the patched control surface script. Copy/symlink this
  folder into `.../Ableton/Resources/MIDI Remote Scripts/` to use it.
- `MK4_API_Diagnostic/` — throwaway diagnostic script (see Methodology above).
  Not needed once you're not actively debugging a new crash.
- `notes.txt` — accumulated ground-truth log: real API dumps + real crash logs
  from this Live 11.3.11 install. Consult this before "fixing" anything based on
  outside references.
