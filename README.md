# Swarmbreaker

Retro arcade trench defence inspired by the segmented-enemy chaos of `Centipede`.

The current demo slice now includes:

- title, mode select, records, help, options, pause, and game-over screens
- persistent presentation settings plus a local profile for unlocks and run history
- a combo multiplier and clearer score-chasing feedback
- challenge modes: `Classic Defence`, `Time Attack`, `Toxic Gauntlet`, and `Boss Rush`
- boss waves with a Hive Matriarch event and mode-specific escalation rules
- a guided first-run objective card layered over the opening waves
- adaptive synth-backed menu, run, and boss music states
- stronger visual feedback using hit, muzzle, and explosion effects
- extra-life thresholds, run summaries, unlock notices, and local leaderboard-ready records
- poisoned mushrooms that force centipede heads into dive attacks

## Requirements

- Python 3.10+
- `pygame-ce`

Install the dependency with:

```bash
python -m pip install pygame-ce
```

## Run locally

```bash
python main.py
```

## Controls

- Left / Right: strafe in-game and change records pages
- Up / Down: move through menus and advance or fall back within the trench
- Hold `Space`: fire
- `Enter`: confirm menu selections or deploy a wave immediately
- `P`: pause or resume the run
- `H`: open the help card during a run
- `M`: mute or restore audio
- `R`: open records from the mode select screen
- `Esc`: back out of menus or end the current run

## Smoke test

```bash
set SDL_VIDEODRIVER=dummy
set SDL_AUDIODRIVER=dummy
set SWARMBREAKER_HEADLESS_SMOKE_TEST=1
python main.py
```

The legacy `BUGBLASTER_HEADLESS_SMOKE_TEST=1` flag still works for backwards compatibility.

## Desktop validation

For the full deterministic desktop regression lane, run:

```bash
python tools/validate_desktop_demo.py
```

This validates the authored sound bank, late-wave surge tuning, Matriarch Prime escalation, and the shared desktop review-pack evidence.
It also writes a dated validation report into `../LOCAL-ONLY/captures/swarmbreaker`.

## Desktop review pack

Swarmbreaker remains a desktop-first pygame game.

To generate the shared desktop evidence pack used by the manager hub:

```bash
python tools/generate_review_pack.py
```

This writes deterministic review screenshots and metadata to `../LOCAL-ONLY/captures/swarmbreaker`.

## Desktop sound bank

The desktop build now supports an authored sound-bank override at `assets/sounds/desktop`.
To regenerate the shipped retro cue pack:

```bash
python tools/generate_desktop_sound_bank.py
```

Any `.wav` or `.ogg` placed in that folder with the same cue name as the runtime sound key will override the procedural fallback.

## Experimental browser review prototype

There is now a lightweight pygbag-based review URL for manager capture and browser-feasibility checks. It is not the primary shipping runtime.

Build the staged prototype:

```bash
python tools/build_browser_prototype.py
```

Serve the generated web root:

```bash
cd build/browser-prototype-source/build/web
python -m http.server 8000
```

Open the fast-entry review URL:

```text
http://127.0.0.1:8000/?autostart=1&review=1&mode=classic
```

Review mode uses deterministic startup and lightweight procedural browser assets so the URL reaches a stable reviewable state quickly.

If you already captured browser screenshots through Playwright or another browser automation pass, publish them into the shared manager pack with:

```bash
python tools/generate_browser_review_pack.py
```

## Local save data

High score, settings, unlocks, and local run records are now written to your local user data folder instead of the repo root.
Legacy repo-root high score and settings files are still read if they already exist.
