from __future__ import annotations

import json
import os
import sys
import tempfile
from datetime import date
from pathlib import Path


def configure_environment() -> None:
    os.environ.setdefault("SDL_VIDEODRIVER", "dummy")
    os.environ.setdefault("SDL_AUDIODRIVER", "dummy")
    staging_root = Path(tempfile.gettempdir()) / "swarmbreaker-validate-profile"
    staging_root.mkdir(parents=True, exist_ok=True)
    os.environ["LOCALAPPDATA"] = str(staging_root)
    os.environ["XDG_DATA_HOME"] = str(staging_root)


configure_environment()

REPO_ROOT = Path(__file__).resolve().parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

import pygame

import main
from tools.generate_review_pack import CAPTURE_DIR, generate_review_pack


DATE_TAG = date.today().isoformat()
EXPECTED_SOUND_KEYS = [
    "bonus",
    "boss_die",
    "boss_hit",
    "boss_phase",
    "boss_shot",
    "boss_theme",
    "briefing_theme",
    "combo",
    "deploy",
    "enemy_hit",
    "last_life",
    "menu",
    "menu_confirm",
    "mode_select_theme",
    "player_die",
    "rank_up",
    "record",
    "record_break",
    "run_theme",
    "shoot",
    "surge",
    "surge_theme",
    "title_theme",
    "unlock",
    "warning",
    "wave",
]


def expect(condition: bool, message: str) -> None:
    if not condition:
        raise AssertionError(message)


def validate_sound_bank() -> dict:
    desktop_dir = REPO_ROOT / "assets" / "sounds" / "desktop"
    missing = [key for key in EXPECTED_SOUND_KEYS if not (desktop_dir / f"{key}.wav").exists()]
    expect(not missing, f"Missing desktop sound-bank files: {', '.join(missing)}")

    resolved = {}
    for key in ("deploy", "surge", "boss_phase", "record_break", "mode_select_theme"):
        path = main.find_optional_sound(key)
        expect(path is not None, f"Optional sound lookup did not resolve for {key}")
        resolved[key] = str(Path(path))
    return {
        "soundBankFileCount": len(list(desktop_dir.glob("*.wav"))),
        "resolvedExamples": resolved,
    }


def validate_late_wave_profiles() -> dict:
    game = main.Game()
    game.sound_enabled = False

    wave10 = game.build_wave_profile(10)
    wave15 = game.build_wave_profile(15)
    wave12 = game.build_wave_profile(12)

    expect(wave10["kind"] == "surge", "Wave 10 should be the first Overrun Surge")
    expect(wave10["secondary_wave_count"] == 1, "Wave 10 surge should ramp cleanly with one secondary wave")
    expect(wave10["spider_limit"] <= 3, "Wave 10 surge should not overfill the lane with spiders")
    expect(wave10["surge_bonus"] >= 2000, "Wave 10 surge payout regressed unexpectedly")

    expect(wave15["kind"] == "surge", "Wave 15 should remain an Overrun Surge")
    expect(wave15["secondary_wave_count"] >= 2, "Late surges should still escalate beyond Wave 10")
    expect(wave15["surge_bonus"] > wave10["surge_bonus"], "Late surge payout should outgrow the first surge")

    expect(wave12["kind"] == "boss", "Wave 12 should be a boss wave")
    expect(wave12.get("prime") is True, "Wave 12 boss should be flagged as Matriarch Prime")
    expect(wave12["boss_prime_bonus"] >= 1500, "Prime bonus regressed unexpectedly")

    boss = main.HiveMatriarch(game, wave12)
    boss.health = int(boss.max_health * 0.3)
    boss.update_phase()
    expect(boss.phase == 3, "Prime boss should enter phase 3 at low health")
    expect(boss.prime_burst_used is True, "Prime burst should trigger on phase 3 escalation")
    expect(len(game.enemy_projectiles) == 7, "Prime burst should spawn a seven-bolt spread")
    expect(game.status_message == "Matriarch Prime is breaking the trench.", "Prime status message changed unexpectedly")

    return {
        "wave10": {
            "secondaryWaveCount": wave10["secondary_wave_count"],
            "spiderLimit": wave10["spider_limit"],
            "surgeBonus": wave10["surge_bonus"],
        },
        "wave15": {
            "secondaryWaveCount": wave15["secondary_wave_count"],
            "spiderLimit": wave15["spider_limit"],
            "surgeBonus": wave15["surge_bonus"],
        },
        "wave12": {
            "bossName": wave12["boss_name"],
            "bossPrimeBonus": wave12["boss_prime_bonus"],
            "primeBurstProjectiles": len(game.enemy_projectiles),
        },
    }


def validate_review_pack() -> dict:
    summary = generate_review_pack()
    evidence_paths = []
    for evidence in summary["evidencePaths"]:
        absolute_path = REPO_ROOT.parent / evidence["path"]
        expect(absolute_path.exists(), f"Review-pack evidence missing: {absolute_path}")
        evidence_paths.append(str(absolute_path))
    review_pack_json = CAPTURE_DIR / "review-pack.json"
    expect(review_pack_json.exists(), "Review-pack JSON summary was not written")
    return {
        "reviewPackJson": str(review_pack_json),
        "evidenceCount": len(evidence_paths),
        "firstEvidence": evidence_paths[0] if evidence_paths else None,
        "verifiedAt": summary["verifiedAt"],
    }


def main_cli() -> None:
    try:
        results = {
            "date": DATE_TAG,
            "soundBank": validate_sound_bank(),
            "lateWaveProfiles": validate_late_wave_profiles(),
            "reviewPack": validate_review_pack(),
        }
        CAPTURE_DIR.mkdir(parents=True, exist_ok=True)
        report_path = CAPTURE_DIR / f"desktop-validation-{DATE_TAG}.json"
        report_path.write_text(json.dumps(results, indent=2) + "\n", encoding="utf-8")
        results["validationReportPath"] = str(report_path)
        print(json.dumps(results, indent=2))
    finally:
        pygame.quit()


if __name__ == "__main__":
    main_cli()
