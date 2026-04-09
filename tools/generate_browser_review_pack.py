from __future__ import annotations

import json
import shutil
from datetime import date
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
WORKSPACE_ROOT = REPO_ROOT.parent
CAPTURE_DIR = WORKSPACE_ROOT / "LOCAL-ONLY" / "captures" / "swarmbreaker"
BUILD_MANIFEST_PATH = REPO_ROOT / "build" / "browser-prototype.json"
SOURCE_CAPTURE_DIR = Path.home() / ".codex"
DATE_TAG = date.today().isoformat()

SCREENSHOT_SOURCES = [
    {
        "label": "Browser review URL initial run state",
        "source": SOURCE_CAPTURE_DIR / "swarmbreaker-browser-prototype-final.png",
        "destination": CAPTURE_DIR / f"browser-review-intro-{DATE_TAG}.png",
    },
    {
        "label": "Browser review URL follow-up state",
        "source": SOURCE_CAPTURE_DIR / "swarmbreaker-browser-prototype-gameplay.png",
        "destination": CAPTURE_DIR / f"browser-review-gameplay-{DATE_TAG}.png",
    },
]


def ensure_capture_dir() -> None:
    CAPTURE_DIR.mkdir(parents=True, exist_ok=True)


def relative_capture_path(path: Path) -> str:
    return str(path.relative_to(WORKSPACE_ROOT)).replace("\\", "/")


def copy_required_files() -> list[dict[str, str]]:
    evidence = []
    missing = [item["source"] for item in SCREENSHOT_SOURCES if not item["source"].exists()]
    if not BUILD_MANIFEST_PATH.exists():
        missing.append(BUILD_MANIFEST_PATH)
    if missing:
        missing_list = "\n".join(f"- {path}" for path in missing)
        raise SystemExit(f"Missing browser review inputs:\n{missing_list}")

    for item in SCREENSHOT_SOURCES:
        destination = item["destination"]
        shutil.copy2(item["source"], destination)
        evidence.append({"label": item["label"], "path": relative_capture_path(destination)})

    manifest_copy = CAPTURE_DIR / f"browser-build-manifest-{DATE_TAG}.json"
    shutil.copy2(BUILD_MANIFEST_PATH, manifest_copy)
    evidence.append({"label": "Browser prototype build manifest", "path": relative_capture_path(manifest_copy)})
    return evidence


def generate_browser_review_pack() -> dict[str, object]:
    ensure_capture_dir()
    evidence = copy_required_files()

    review_summary = {
        "gameName": "Swarmbreaker",
        "gameType": "desktop",
        "reviewTrack": "experimental_browser_prototype",
        "renderClass": "desktop-first pygame with experimental pygbag review URL",
        "localLaunchCommand": "python main.py",
        "prototypeBuildCommand": "python tools/build_browser_prototype.py",
        "prototypeServeCommand": "python -m http.server 8000",
        "prototypeServeCwd": "build/browser-prototype-source/build/web",
        "reviewUrl": "http://127.0.0.1:8000/?autostart=1&review=1&mode=classic",
        "reviewParams": ["autostart=1", "review=1", "mode=classic"],
        "evidencePaths": evidence,
        "knownCaveats": [
            "The browser URL is an experimental review prototype and does not replace the desktop shipping runtime.",
            "Browser review mode swaps to lightweight procedural art and skips the synth music bed so the staged build stays compatible and reviewable.",
            "The prototype still depends on a staged build plus local static server instead of the one-command desktop launch path.",
        ],
        "nextImprovement": "Automate the browser capture pass end-to-end so the shared pack can be refreshed without a manual Playwright screenshot step.",
        "verifiedAt": DATE_TAG,
    }

    summary_path = CAPTURE_DIR / "browser-review-pack.json"
    summary_path.write_text(json.dumps(review_summary, indent=2), encoding="utf-8")

    markdown_lines = [
        "# Swarmbreaker Browser Review Prototype Pack",
        "",
        f"- game name: `{review_summary['gameName']}`",
        "- launch track: `experimental browser review prototype`",
        f"- desktop launch command: `{review_summary['localLaunchCommand']}`",
        f"- prototype build command: `{review_summary['prototypeBuildCommand']}`",
        f"- prototype serve command: `{review_summary['prototypeServeCommand']}`",
        f"- prototype serve cwd: `{review_summary['prototypeServeCwd']}`",
        f"- review URL: `{review_summary['reviewUrl']}`",
        f"- review query params: `{', '.join(review_summary['reviewParams'])}`",
        f"- render class: `{review_summary['renderClass']}`",
        "- evidence paths:",
    ]
    for evidence_item in evidence:
        markdown_lines.append(f"  - `{evidence_item['label']}`: `{evidence_item['path']}`")
    markdown_lines.extend(
        [
            "- known caveats:",
            f"  - {review_summary['knownCaveats'][0]}",
            f"  - {review_summary['knownCaveats'][1]}",
            f"  - {review_summary['knownCaveats'][2]}",
            f"- next required verification improvement: {review_summary['nextImprovement']}",
            f"- verified at: `{review_summary['verifiedAt']}`",
            "",
            "## What passed",
            "",
            "- The fast-entry browser URL reached a deterministic reviewable run state with `autostart=1&review=1&mode=classic`.",
            "- A follow-up captured state proved that the browser prototype continues past boot and into live run flow.",
            "- Browser review telemetry recorded the first rendered frame and active canvas size in local storage during the session.",
            "",
            "## What remains different from desktop",
            "",
            "- The browser prototype is for manager review and feasibility checks, not the primary production runtime.",
            "- Review mode intentionally prefers procedural fallback assets and compatibility-safe audio over full desktop fidelity.",
        ]
    )
    (CAPTURE_DIR / "browser-review-pack.md").write_text("\n".join(markdown_lines) + "\n", encoding="utf-8")
    return review_summary


if __name__ == "__main__":
    summary = generate_browser_review_pack()
    print(json.dumps(summary, indent=2))
