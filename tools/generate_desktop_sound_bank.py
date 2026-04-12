from __future__ import annotations

import math
import random
import struct
import wave
from pathlib import Path

SAMPLE_RATE = 22_050
OUTPUT_DIR = Path(__file__).resolve().parents[1] / "assets" / "sounds" / "desktop"
PEAK_TARGET = 0.9


def make_buffer(duration_seconds: float) -> list[float]:
    return [0.0] * max(1, int(duration_seconds * SAMPLE_RATE))


def clamp(value: float, low: float, high: float) -> float:
    return max(low, min(high, value))


def oscillator(phase: float, waveform: str) -> float:
    cycle = (phase / (2.0 * math.pi)) % 1.0
    if waveform == "sine":
        return math.sin(phase)
    if waveform == "square":
        return 1.0 if cycle < 0.5 else -1.0
    if waveform == "triangle":
        return 2.0 * abs(2.0 * cycle - 1.0) - 1.0
    if waveform == "saw":
        return 2.0 * cycle - 1.0
    raise ValueError(f"Unsupported waveform: {waveform}")


def envelope(progress: float, attack: float = 0.08, sustain: float = 0.82, release: float = 0.18) -> float:
    progress = clamp(progress, 0.0, 1.0)
    if progress < attack:
        return progress / max(attack, 0.0001)
    if progress > 1.0 - release:
        return max(0.0, (1.0 - progress) / max(release, 0.0001))
    return sustain


def add_tone(
    buffer: list[float],
    start: float,
    duration: float,
    frequency: float,
    *,
    waveform: str = "triangle",
    volume: float = 0.4,
    sweep: float = 0.0,
    vibrato: float = 0.0,
    vibrato_rate: float = 6.0,
) -> None:
    start_index = max(0, int(start * SAMPLE_RATE))
    sample_count = max(1, int(duration * SAMPLE_RATE))
    phase = 0.0
    for offset in range(sample_count):
        index = start_index + offset
        if index >= len(buffer):
            break
        progress = offset / sample_count
        current_frequency = frequency * (1.0 + sweep * progress)
        if vibrato:
            current_frequency *= 1.0 + math.sin(progress * duration * math.tau * vibrato_rate) * vibrato
        phase += math.tau * current_frequency / SAMPLE_RATE
        amp = volume * envelope(progress)
        buffer[index] += oscillator(phase, waveform) * amp


def add_chord(
    buffer: list[float],
    start: float,
    duration: float,
    frequencies: list[float],
    *,
    waveform: str = "triangle",
    volume: float = 0.32,
    sweep: float = 0.0,
) -> None:
    if not frequencies:
        return
    per_voice = volume / max(1, len(frequencies))
    for frequency in frequencies:
        add_tone(buffer, start, duration, frequency, waveform=waveform, volume=per_voice, sweep=sweep)


def add_noise(buffer: list[float], start: float, duration: float, *, volume: float = 0.18) -> None:
    start_index = max(0, int(start * SAMPLE_RATE))
    sample_count = max(1, int(duration * SAMPLE_RATE))
    low_pass = 0.0
    for offset in range(sample_count):
        index = start_index + offset
        if index >= len(buffer):
            break
        progress = offset / sample_count
        raw = random.uniform(-1.0, 1.0)
        low_pass = low_pass * 0.82 + raw * 0.18
        high = raw - low_pass
        amp = volume * envelope(progress, attack=0.02, sustain=0.5, release=0.4)
        buffer[index] += high * amp


def add_kick(buffer: list[float], start: float, *, volume: float = 0.4) -> None:
    start_index = max(0, int(start * SAMPLE_RATE))
    sample_count = max(1, int(0.16 * SAMPLE_RATE))
    phase = 0.0
    for offset in range(sample_count):
        index = start_index + offset
        if index >= len(buffer):
            break
        progress = offset / sample_count
        current_frequency = 140.0 - 90.0 * progress
        phase += math.tau * current_frequency / SAMPLE_RATE
        amp = volume * envelope(progress, attack=0.01, sustain=0.9, release=0.7)
        buffer[index] += math.sin(phase) * amp


def lay_notes(
    buffer: list[float],
    notes: list[float | None],
    *,
    start: float,
    step: float,
    duration: float,
    waveform: str = "triangle",
    volume: float = 0.35,
    sweep: float = 0.0,
    vibrato: float = 0.0,
) -> None:
    cursor = start
    for frequency in notes:
        if frequency is not None:
            add_tone(
                buffer,
                cursor,
                duration,
                frequency,
                waveform=waveform,
                volume=volume,
                sweep=sweep,
                vibrato=vibrato,
            )
        cursor += step


def normalize(buffer: list[float]) -> list[float]:
    peak = max((abs(sample) for sample in buffer), default=0.0)
    if peak <= 0.0:
        return buffer
    scale = PEAK_TARGET / peak
    return [clamp(sample * scale, -1.0, 1.0) for sample in buffer]


def write_wav(path: Path, buffer: list[float]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with wave.open(str(path), "wb") as wav_file:
        wav_file.setnchannels(1)
        wav_file.setsampwidth(2)
        wav_file.setframerate(SAMPLE_RATE)
        frames = bytearray()
        for sample in normalize(buffer):
            frames.extend(struct.pack("<h", int(sample * 32767)))
        wav_file.writeframes(frames)


def build_shoot() -> list[float]:
    buffer = make_buffer(0.16)
    add_tone(buffer, 0.0, 0.1, 780.0, waveform="square", volume=0.34, sweep=-0.32)
    add_tone(buffer, 0.01, 0.08, 1174.0, waveform="triangle", volume=0.16, sweep=-0.18)
    return buffer


def build_enemy_hit() -> list[float]:
    buffer = make_buffer(0.18)
    add_noise(buffer, 0.0, 0.08, volume=0.22)
    add_tone(buffer, 0.0, 0.12, 280.0, waveform="triangle", volume=0.24, sweep=-0.45)
    return buffer


def build_player_die() -> list[float]:
    buffer = make_buffer(0.9)
    add_tone(buffer, 0.0, 0.26, 220.0, waveform="triangle", volume=0.3, sweep=-0.28)
    add_tone(buffer, 0.18, 0.34, 165.0, waveform="saw", volume=0.24, sweep=-0.36)
    add_noise(buffer, 0.22, 0.24, volume=0.12)
    add_kick(buffer, 0.3, volume=0.18)
    return buffer


def build_warning() -> list[float]:
    buffer = make_buffer(0.66)
    for start, freq in ((0.0, 220.0), (0.18, 165.0), (0.36, 220.0)):
        add_tone(buffer, start, 0.16, freq, waveform="triangle", volume=0.28, vibrato=0.02)
    return buffer


def build_combo() -> list[float]:
    buffer = make_buffer(0.34)
    lay_notes(buffer, [440.0, 554.37, 659.25], start=0.0, step=0.08, duration=0.1, waveform="square", volume=0.26)
    return buffer


def build_bonus() -> list[float]:
    buffer = make_buffer(0.56)
    lay_notes(buffer, [392.0, 523.25, 784.0], start=0.0, step=0.12, duration=0.16, waveform="triangle", volume=0.24)
    add_noise(buffer, 0.2, 0.12, volume=0.08)
    return buffer


def build_wave() -> list[float]:
    buffer = make_buffer(0.44)
    lay_notes(buffer, [261.63, 329.63, 392.0], start=0.0, step=0.1, duration=0.14, waveform="triangle", volume=0.22)
    return buffer


def build_surge() -> list[float]:
    buffer = make_buffer(0.9)
    add_kick(buffer, 0.0, volume=0.22)
    add_kick(buffer, 0.34, volume=0.16)
    add_tone(buffer, 0.0, 0.28, 196.0, waveform="square", volume=0.24, sweep=0.22, vibrato=0.015)
    add_tone(buffer, 0.28, 0.28, 247.0, waveform="triangle", volume=0.26, sweep=0.18, vibrato=0.015)
    add_tone(buffer, 0.56, 0.26, 294.0, waveform="triangle", volume=0.22, sweep=-0.14, vibrato=0.015)
    add_noise(buffer, 0.1, 0.18, volume=0.08)
    return buffer


def build_boss_shot() -> list[float]:
    buffer = make_buffer(0.22)
    add_tone(buffer, 0.0, 0.16, 185.0, waveform="square", volume=0.28, sweep=-0.22)
    add_tone(buffer, 0.02, 0.12, 147.0, waveform="square", volume=0.2, sweep=-0.28)
    return buffer


def build_boss_hit() -> list[float]:
    buffer = make_buffer(0.26)
    add_noise(buffer, 0.0, 0.08, volume=0.18)
    add_tone(buffer, 0.0, 0.2, 620.0, waveform="triangle", volume=0.22, sweep=-0.42)
    return buffer


def build_boss_die() -> list[float]:
    buffer = make_buffer(1.12)
    add_kick(buffer, 0.0, volume=0.22)
    lay_notes(buffer, [220.0, 185.0, 147.0, 110.0], start=0.0, step=0.18, duration=0.22, waveform="triangle", volume=0.22, sweep=-0.12)
    add_noise(buffer, 0.16, 0.22, volume=0.1)
    add_noise(buffer, 0.48, 0.24, volume=0.07)
    return buffer


def build_boss_phase() -> list[float]:
    buffer = make_buffer(0.92)
    add_kick(buffer, 0.0, volume=0.18)
    lay_notes(buffer, [220.0, 277.18, 185.0, 110.0], start=0.0, step=0.18, duration=0.18, waveform="square", volume=0.2, sweep=-0.08)
    add_tone(buffer, 0.5, 0.28, 98.0, waveform="triangle", volume=0.18, vibrato=0.02)
    return buffer


def build_menu() -> list[float]:
    buffer = make_buffer(0.12)
    add_tone(buffer, 0.0, 0.08, 440.0, waveform="triangle", volume=0.14)
    return buffer


def build_menu_confirm() -> list[float]:
    buffer = make_buffer(0.36)
    lay_notes(buffer, [392.0, 523.25, 659.25], start=0.0, step=0.08, duration=0.1, waveform="triangle", volume=0.22)
    return buffer


def build_record() -> list[float]:
    buffer = make_buffer(0.52)
    lay_notes(buffer, [523.25, 659.25, 784.0], start=0.0, step=0.12, duration=0.14, waveform="triangle", volume=0.22)
    return buffer


def build_record_break() -> list[float]:
    buffer = make_buffer(0.82)
    lay_notes(buffer, [587.33, 784.0, 987.77, 1174.66], start=0.0, step=0.12, duration=0.16, waveform="triangle", volume=0.22)
    add_noise(buffer, 0.34, 0.18, volume=0.06)
    return buffer


def build_rank_up() -> list[float]:
    buffer = make_buffer(0.46)
    lay_notes(buffer, [392.0, 523.25, 659.25], start=0.0, step=0.1, duration=0.12, waveform="triangle", volume=0.22)
    return buffer


def build_deploy() -> list[float]:
    buffer = make_buffer(0.58)
    add_kick(buffer, 0.0, volume=0.2)
    add_chord(buffer, 0.04, 0.18, [196.0, 246.94, 329.63], waveform="triangle", volume=0.28)
    add_chord(buffer, 0.24, 0.22, [220.0, 277.18, 369.99], waveform="triangle", volume=0.3)
    return buffer


def build_unlock() -> list[float]:
    buffer = make_buffer(0.84)
    lay_notes(buffer, [330.0, 392.0, 523.25, 659.25], start=0.0, step=0.14, duration=0.18, waveform="triangle", volume=0.22)
    return buffer


def build_last_life() -> list[float]:
    buffer = make_buffer(0.92)
    add_tone(buffer, 0.0, 0.24, 196.0, waveform="triangle", volume=0.28, vibrato=0.02)
    add_tone(buffer, 0.3, 0.24, 165.0, waveform="triangle", volume=0.28, vibrato=0.02)
    add_tone(buffer, 0.6, 0.18, 147.0, waveform="triangle", volume=0.22, sweep=-0.08)
    return buffer


def build_title_theme() -> list[float]:
    buffer = make_buffer(2.4)
    lay_notes(buffer, [261.63, 329.63, 392.0, 523.25, 392.0, 329.63, 261.63, 196.0], start=0.0, step=0.28, duration=0.2, waveform="triangle", volume=0.16)
    lay_notes(buffer, [130.81, None, 146.83, None, 174.61, None, 130.81, None], start=0.0, step=0.28, duration=0.24, waveform="sine", volume=0.12)
    for beat in (0.0, 0.56, 1.12, 1.68):
        add_noise(buffer, beat + 0.18, 0.06, volume=0.02)
    return buffer


def build_mode_select_theme() -> list[float]:
    buffer = make_buffer(2.4)
    lay_notes(buffer, [220.0, 277.18, 329.63, 440.0, 329.63, 277.18, 220.0, 261.63], start=0.0, step=0.28, duration=0.18, waveform="triangle", volume=0.15)
    lay_notes(buffer, [110.0, None, 123.47, None, 130.81, None, 110.0, None], start=0.0, step=0.28, duration=0.22, waveform="square", volume=0.08)
    return buffer


def build_briefing_theme() -> list[float]:
    buffer = make_buffer(2.6)
    lay_notes(buffer, [196.0, 246.94, 293.66, 329.63, 293.66, 246.94, 196.0, 220.0], start=0.0, step=0.3, duration=0.22, waveform="triangle", volume=0.14)
    lay_notes(buffer, [98.0, None, 110.0, None, 123.47, None, 98.0, None], start=0.0, step=0.3, duration=0.28, waveform="sine", volume=0.08)
    return buffer


def build_run_theme() -> list[float]:
    buffer = make_buffer(2.08)
    lay_notes(buffer, [220.0, 220.0, 329.63, 392.0, 220.0, 220.0, 329.63, 440.0], start=0.0, step=0.16, duration=0.11, waveform="square", volume=0.14)
    lay_notes(buffer, [261.63, 261.63, 349.23, 392.0, 261.63, 261.63, 349.23, 493.88], start=1.04, step=0.16, duration=0.11, waveform="square", volume=0.14)
    lay_notes(buffer, [440.0, None, 523.25, None, 587.33, None, 523.25, None], start=0.0, step=0.26, duration=0.16, waveform="triangle", volume=0.1)
    return buffer


def build_boss_theme() -> list[float]:
    buffer = make_buffer(2.24)
    lay_notes(buffer, [147.0, 147.0, 175.0, 196.0, 147.0, 147.0, 131.0, 165.0], start=0.0, step=0.18, duration=0.14, waveform="square", volume=0.15)
    lay_notes(buffer, [98.0, None, 110.0, None, 87.31, None, 98.0, None], start=0.0, step=0.28, duration=0.22, waveform="sine", volume=0.08)
    add_kick(buffer, 0.0, volume=0.12)
    add_kick(buffer, 0.72, volume=0.1)
    add_kick(buffer, 1.44, volume=0.1)
    return buffer


def build_surge_theme() -> list[float]:
    buffer = make_buffer(2.08)
    lay_notes(buffer, [131.0, 165.0, 196.0, 247.0, 147.0, 196.0, 262.0, 294.0], start=0.0, step=0.18, duration=0.14, waveform="square", volume=0.14)
    lay_notes(buffer, [98.0, None, 110.0, None, 123.47, None, 130.81, None], start=0.0, step=0.26, duration=0.2, waveform="triangle", volume=0.08)
    add_kick(buffer, 0.0, volume=0.14)
    add_kick(buffer, 0.52, volume=0.12)
    add_kick(buffer, 1.04, volume=0.12)
    add_kick(buffer, 1.56, volume=0.12)
    return buffer


BUILDERS = {
    "shoot": build_shoot,
    "enemy_hit": build_enemy_hit,
    "player_die": build_player_die,
    "warning": build_warning,
    "combo": build_combo,
    "bonus": build_bonus,
    "wave": build_wave,
    "surge": build_surge,
    "boss_shot": build_boss_shot,
    "boss_hit": build_boss_hit,
    "boss_die": build_boss_die,
    "boss_phase": build_boss_phase,
    "menu": build_menu,
    "menu_confirm": build_menu_confirm,
    "record": build_record,
    "record_break": build_record_break,
    "rank_up": build_rank_up,
    "deploy": build_deploy,
    "unlock": build_unlock,
    "last_life": build_last_life,
    "title_theme": build_title_theme,
    "mode_select_theme": build_mode_select_theme,
    "briefing_theme": build_briefing_theme,
    "run_theme": build_run_theme,
    "boss_theme": build_boss_theme,
    "surge_theme": build_surge_theme,
}


def main() -> None:
    random.seed(7)
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    for name, builder in BUILDERS.items():
        write_wav(OUTPUT_DIR / f"{name}.wav", builder())
    print(f"Generated {len(BUILDERS)} desktop sound-bank files in {OUTPUT_DIR}")


if __name__ == "__main__":
    main()
