from __future__ import annotations

import argparse
import json
import shutil
import subprocess
import sys
import urllib.request
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
BUILD_ROOT = REPO_ROOT / "build"
STAGE_ROOT = BUILD_ROOT / "browser-prototype-source"
ASSET_ROOT = REPO_ROOT / "assets"
MANIFEST_PATH = BUILD_ROOT / "browser-prototype.json"
COPY_ROOTS = ["main.py", "README.md", "assets"]
SKIP_FILE_NAMES = {"desktop.ini"}
BROWSERFS_URL = "https://cdn.jsdelivr.net/npm/browserfs@1.4.3/dist/browserfs.min.js"
BROWSERFS_SCRIPT_NAME = "browserfs.min.js"
CANVAS_BOOT_FIX = """
    function syncReviewCanvas(targetWidth, targetHeight) {
        const reviewCanvas = document.getElementById("canvas");
        if (!reviewCanvas) {
            return;
        }
        const width = Number.parseInt(targetWidth || config.fb_width, 10) || 1280;
        const height = Number.parseInt(targetHeight || config.fb_height, 10) || 720;
        reviewCanvas.width = width;
        reviewCanvas.height = height;
        reviewCanvas.hidden = false;
        reviewCanvas.style.visibility = "visible";
        reviewCanvas.style.display = "block";
    }
"""


def reset_stage() -> None:
    if STAGE_ROOT.exists():
        shutil.rmtree(STAGE_ROOT)
    STAGE_ROOT.mkdir(parents=True, exist_ok=True)


def copy_project_subset() -> None:
    for relative_name in COPY_ROOTS:
        source = REPO_ROOT / relative_name
        destination = STAGE_ROOT / relative_name
        if source.is_dir():
            shutil.copytree(
                source,
                destination,
                ignore=shutil.ignore_patterns("__pycache__", "*.pyc", "*.pyo", "desktop.ini"),
            )
        else:
            shutil.copy2(source, destination)


def clean_stage() -> None:
    for path in STAGE_ROOT.rglob("*"):
        if path.is_file() and path.name in SKIP_FILE_NAMES:
            path.unlink()


def prune_review_only_assets() -> list[str]:
    pruned_paths: list[str] = []
    review_effect_root = STAGE_ROOT / "assets" / "sounds" / "images"
    if review_effect_root.exists():
        shutil.rmtree(review_effect_root)
        pruned_paths.append(str(review_effect_root.relative_to(STAGE_ROOT)).replace("\\", "/"))
    return pruned_paths


def convert_wav_assets() -> list[dict[str, str]]:
    conversions: list[dict[str, str]] = []
    for wav_path in (STAGE_ROOT / "assets" / "sounds").glob("*.wav"):
        ogg_path = wav_path.with_suffix(".ogg")
        command = [
            "ffmpeg",
            "-y",
            "-i",
            str(wav_path),
            "-c:a",
            "libvorbis",
            "-q:a",
            "5",
            str(ogg_path),
        ]
        subprocess.run(command, check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
        wav_path.unlink()
        conversions.append(
            {
                "source": str(wav_path.relative_to(STAGE_ROOT)).replace("\\", "/"),
                "converted": str(ogg_path.relative_to(STAGE_ROOT)).replace("\\", "/"),
            }
        )
    return conversions


def run_pygbag_build() -> Path:
    command = [
        sys.executable,
        "-m",
        "pygbag",
        "--build",
        "--ume_block",
        "0",
        "--disable-sound-format-error",
        str(STAGE_ROOT),
    ]
    subprocess.run(command, check=True)
    return STAGE_ROOT / "build" / "web"


def vendor_browserfs(web_root: Path) -> str:
    web_root.mkdir(parents=True, exist_ok=True)
    browserfs_path = web_root / BROWSERFS_SCRIPT_NAME
    with urllib.request.urlopen(BROWSERFS_URL) as response:
        browserfs_path.write_bytes(response.read())
    return BROWSERFS_URL


def patch_browserfs_reference(web_root: Path) -> None:
    index_path = web_root / "index.html"
    if not index_path.exists():
        return

    content = index_path.read_text(encoding="utf-8")
    patched = content.replace(
        '<script src="https://pygame-web.github.io/cdn/0.9.3//browserfs.min.js"></script>',
        f'<script src="{BROWSERFS_SCRIPT_NAME}"></script>',
    )
    patched = patched.replace(
        'width="1px"\nheight="1px"',
        'width="1280px"\nheight="720px"',
    )
    patched = patched.replace(
        """globalThis.__canvas_resized = (self, ecw, ech) => {
        console.warn("TODO: panda3d canvas monitor", self, ecw, ech)
    }""",
        f"""{CANVAS_BOOT_FIX}
    globalThis.__canvas_resized = (self, ecw, ech) => {{
        syncReviewCanvas(ecw, ech)
        console.warn("browser review canvas resized", self, ecw, ech)
    }}""",
    )
    patched = patched.replace(
        '        console.log(__FILE__, "custom_onload")',
        '        console.log(__FILE__, "custom_onload")\n        syncReviewCanvas()',
    )
    patched = patched.replace(
        '        console.log(__FILE__, "custom_prerun")',
        '        console.log(__FILE__, "custom_prerun")\n        syncReviewCanvas()',
    )

    if patched != content:
        index_path.write_text(patched, encoding="utf-8")


def write_manifest(web_root: Path, conversions: list[dict[str, str]], pruned_paths: list[str]) -> dict[str, object]:
    manifest = {
        "buildRoot": str(BUILD_ROOT),
        "stageRoot": str(STAGE_ROOT),
        "webRoot": str(web_root),
        "reviewUrlExample": "http://127.0.0.1:8000/?autostart=1&review=1&mode=classic",
        "convertedAudio": conversions,
        "prunedReviewOnlyAssets": pruned_paths,
        "vendoredBrowserFs": str(web_root / BROWSERFS_SCRIPT_NAME) if web_root.exists() else None,
        "notes": [
            "Serve the generated web root with any static server for local browser review.",
            "The staged browser review build strips file-based effect atlases because review mode now uses procedural browser-safe feedback assets.",
            "The browser prototype is experimental and should not replace the desktop release path.",
        ],
    }
    MANIFEST_PATH.write_text(json.dumps(manifest, indent=2), encoding="utf-8")
    return manifest


def build_browser_prototype(skip_build: bool) -> dict[str, object]:
    BUILD_ROOT.mkdir(parents=True, exist_ok=True)
    reset_stage()
    copy_project_subset()
    clean_stage()
    pruned_paths = prune_review_only_assets()
    conversions = convert_wav_assets()
    web_root = STAGE_ROOT / "build" / "web"
    if not skip_build:
        web_root = run_pygbag_build()
        vendor_browserfs(web_root)
        patch_browserfs_reference(web_root)
    return write_manifest(web_root, conversions, pruned_paths)


def main() -> None:
    parser = argparse.ArgumentParser(description="Stage and optionally build a Pygbag browser prototype for Swarmbreaker.")
    parser.add_argument("--skip-build", action="store_true", help="Prepare the staging directory without invoking pygbag.")
    args = parser.parse_args()

    manifest = build_browser_prototype(skip_build=args.skip_build)
    print(json.dumps(manifest, indent=2))


if __name__ == "__main__":
    main()
