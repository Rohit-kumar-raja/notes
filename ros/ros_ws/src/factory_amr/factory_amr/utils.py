import math
import os
import shutil
import struct
import subprocess
import tempfile
import wave

_WAV_PATH = os.path.join(tempfile.gettempdir(), "fire_alarm.wav")
_proc = None
_cmd = None


def _make_wav(path, rate=44100, freq=3000.0, vol=0.8):
    """3 pulses at ~3 kHz, then a pause (fire alarm pattern)."""
    frames = bytearray()
    for _ in range(3):
        for i in range(int(rate * 0.4)):
            t = i / rate
            s = math.sin(2 * math.pi * freq * t) + 0.33 * math.sin(2 * math.pi * 3 * freq * t)
            frames.extend(struct.pack("<h", int(max(-1, min(1, s * vol)) * 32767)))
        frames.extend(b"\x00\x00" * int(rate * 0.15))
    frames.extend(b"\x00\x00" * int(rate * 0.6))

    with wave.open(path, "wb") as w:
        w.setnchannels(1)
        w.setsampwidth(2)
        w.setframerate(rate)
        w.writeframes(bytes(frames))


def _find_player(wav):
    if shutil.which("paplay"):
        return ["paplay", wav]
    if shutil.which("aplay"):
        return ["aplay", "-q", wav]
    if shutil.which("play"):  # sox
        return ["play", "-q", wav]
    return None


def _init():
    global _cmd
    if _cmd is None:
        if not os.path.exists(_WAV_PATH):
            _make_wav(_WAV_PATH)
        _cmd = _find_player(_WAV_PATH) or []
    return _cmd


def is_playing():
    return _proc is not None and _proc.poll() is None


def play_alarm():
    """Non-blocking. Safe to call every scan; won't overlap itself."""
    global _proc
    if is_playing():
        return
    cmd = _init()
    if cmd:
        _proc = subprocess.Popen(cmd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    else:
        print("\a", end="", flush=True)  # terminal bell fallback


def stop_alarm():
    global _proc
    if is_playing():
        _proc.terminate()
    _proc = None