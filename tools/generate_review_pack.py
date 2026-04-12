from __future__ import annotations

import json
import os
import random
import sys
import tempfile
from datetime import date
from pathlib import Path


def configure_environment() -> None:
    os.environ.setdefault("SDL_VIDEODRIVER", "dummy")
    os.environ.setdefault("SDL_AUDIODRIVER", "dummy")
    staging_root = Path(tempfile.gettempdir()) / "swarmbreaker-review-profile"
    staging_root.mkdir(parents=True, exist_ok=True)
    os.environ["LOCALAPPDATA"] = str(staging_root)
    os.environ["XDG_DATA_HOME"] = str(staging_root)


configure_environment()

REPO_ROOT = Path(__file__).resolve().parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

import pygame

import main


WORKSPACE_ROOT = REPO_ROOT.parent
CAPTURE_DIR = WORKSPACE_ROOT / "LOCAL-ONLY" / "captures" / "swarmbreaker"
DATE_TAG = date.today().isoformat()


def ensure_capture_dir() -> None:
    CAPTURE_DIR.mkdir(parents=True, exist_ok=True)


def relative_capture_path(path: Path) -> str:
    return str(path.relative_to(WORKSPACE_ROOT)).replace("\\", "/")


def save_current_frame(game: main.Game, filename: str) -> Path:
    output_path = CAPTURE_DIR / filename
    pygame.image.save(game.screen, output_path)
    return output_path


def build_records_state(game: main.Game) -> None:
    game.start_run(mode_id="time_attack", skip_briefing=True)
    game.begin_wave(2)
    game.deploy_current_wave()
    game.score = 8420
    game.best_multiplier = 4
    game.multiplier = 3
    game.combo_timer = 150
    game.combo_charge = 2
    game.lives = 2
    game.play_frames = 128 * 60
    game.mode_timer_frames = 64 * 60
    game.stats["waves_cleared"] = 2
    game.stats["segments_destroyed"] = 31
    game.stats["mushrooms_cleared"] = 5
    game.stats["specials_destroyed"] = 4
    game.render()

    game.score = 9215
    game.best_multiplier = 4
    game.level = 5
    game.play_frames = 165 * 60
    game.stats["waves_cleared"] = 4
    game.stats["bosses_destroyed"] = 1
    game.enter_game_over("timeout")

    game.start_run(mode_id="classic", skip_briefing=True)
    game.begin_wave(4)
    game.deploy_current_wave()
    game.score = 13640
    game.best_multiplier = 5
    game.level = 7
    game.play_frames = 224 * 60
    game.stats["waves_cleared"] = 6
    game.stats["segments_destroyed"] = 44
    game.stats["mushrooms_cleared"] = 8
    game.stats["specials_destroyed"] = 7
    game.stats["bosses_destroyed"] = 3
    game.enter_game_over("destroyed")

    game.records_mode_index = game.mode_ids.index("boss_rush")
    game.menu_return_phase = "title"
    game.game_phase = "records"


def generate_review_pack() -> dict:
    ensure_capture_dir()
    random.seed(7)
    game = main.Game()
    game.sound_enabled = False
    captures = []

    game.game_phase = "title"
    game.render()
    captures.append(
        {
            "label": "Desktop title",
            "path": relative_capture_path(save_current_frame(game, f"title-{DATE_TAG}.png")),
        }
    )

    game.mode_select_index = game.mode_ids.index("boss_rush")
    game.game_phase = "mode_select"
    game.render()
    captures.append(
        {
            "label": "Mode select",
            "path": relative_capture_path(save_current_frame(game, f"mode-select-{DATE_TAG}.png")),
        }
    )

    game.start_run(mode_id="time_attack", skip_briefing=True)
    game.begin_wave(2)
    game.deploy_current_wave()
    game.score = 7850
    game.mode_best_score = 12040
    game.best_multiplier = 4
    game.multiplier = 3
    game.combo_timer = 190
    game.combo_charge = 2
    game.lives = 2
    game.play_frames = 94 * 60
    game.mode_timer_frames = 73 * 60
    game.status_message = "Clock extended by 12 seconds."
    game.status_timer = 120
    for _ in range(12):
        game.update()
    game.render()
    captures.append(
        {
            "label": "Gameplay review state",
            "path": relative_capture_path(save_current_frame(game, f"gameplay-{DATE_TAG}.png")),
        }
    )

    build_records_state(game)
    game.render()
    captures.append(
        {
            "label": "Records review state",
            "path": relative_capture_path(save_current_frame(game, f"records-{DATE_TAG}.png")),
        }
    )

    review_summary = {
        "gameName": "Swarmbreaker",
        "gameType": "desktop",
        "renderClass": "desktop",
        "localLaunchCommand": "python main.py",
        "reviewUrl": None,
        "reviewParams": [],
        "reviewEquivalent": "python tools/generate_review_pack.py",
        "validationEquivalent": "python tools/validate_desktop_demo.py",
        "browserPrototypeEquivalent": "python tools/build_browser_prototype.py",
        "evidencePaths": captures,
        "knownCaveats": [
            "Swarmbreaker remains a desktop-first pygame runtime even though an experimental browser review prototype now exists.",
            "The evidence pack uses SDL dummy drivers for deterministic screenshots, so it proves render states rather than live input latency.",
        ],
        "nextImprovement": "Run a native desktop playtest and ear-test on real audio hardware so the generated sound bank and Matriarch Prime burst spacing are tuned from hands-on feel as well as deterministic validation.",
        "verifiedAt": DATE_TAG,
    }

    summary_path = CAPTURE_DIR / "review-pack.json"
    with summary_path.open("w", encoding="utf-8") as handle:
        json.dump(review_summary, handle, indent=2)

    markdown_lines = [
        "# Swarmbreaker Desktop Review Pack",
        "",
        f"- game name: `{review_summary['gameName']}`",
        "- current local launch URL: `n/a (desktop)`",
        "- current public URL: `n/a`",
        "- review URL and query params: `n/a for the desktop pack; experimental browser review URL lives in the browser prototype pack`",
        f"- launch command or script used: `{review_summary['localLaunchCommand']}`",
        f"- review capture command: `{review_summary['reviewEquivalent']}`",
        f"- validation command: `{review_summary['validationEquivalent']}`",
        f"- browser prototype build command: `{review_summary['browserPrototypeEquivalent']}`",
        f"- render class: `{review_summary['renderClass']}`",
        "- browser flags used: `none`",
        "- evidence paths:",
    ]
    for evidence in captures:
        markdown_lines.append(f"  - `{evidence['label']}`: `{evidence['path']}`")
    markdown_lines.extend(
        [
            "- known caveats:",
            f"  - {review_summary['knownCaveats'][0]}",
            f"  - {review_summary['knownCaveats'][1]}",
            f"- next required verification improvement: {review_summary['nextImprovement']}",
            f"- verified at: `{review_summary['verifiedAt']}`",
            "",
            "## What passed",
            "",
            "- Deterministic desktop title, mode select, gameplay, and records states were captured successfully.",
            "- The capture flow uses isolated local save data so it does not mutate the operator's normal profile.",
            "- The desktop validation lane can now verify the sound bank, late-wave tuning, and review-pack evidence together.",
            "",
            "## What failed",
            "",
            "- The desktop capture flow does not itself generate the browser prototype screenshots or a native live-input feel check.",
            "",
            "## Workaround",
            "",
            "- Use the desktop review-pack command for pygame-native evidence and the separate browser prototype pack when the manager needs a fast-entry URL.",
        ]
    )
    (CAPTURE_DIR / "review-pack.md").write_text("\n".join(markdown_lines) + "\n", encoding="utf-8")

    pygame.quit()
    return review_summary


if __name__ == "__main__":
    summary = generate_review_pack()
    print(json.dumps(summary, indent=2))
