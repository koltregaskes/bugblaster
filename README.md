# Swarmbreaker

Retro arcade shooter inspired by the segmented-enemy chaos of Centipede.

Poisoned mushrooms now matter: if a centipede head hits one, it dives straight down toward the player zone before recovering into its side-to-side pattern.

Runs now also support pause and extra-life score thresholds, so longer sessions feel closer to a proper arcade climb instead of a bare survival loop.

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

- Left / Right: move
- Space: fire
- `P`: pause or resume the run
- `M`: mute or restore audio
- Enter: start or restart
- Esc: exit or end the current run

## Smoke test

```bash
set SDL_VIDEODRIVER=dummy
set SDL_AUDIODRIVER=dummy
set BUGBLASTER_HEADLESS_SMOKE_TEST=1
python main.py
```
