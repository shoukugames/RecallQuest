#!/usr/bin/env python3
"""Synthesise every sound in RecallQuest into assets/audio/*.wav.

Run this only when the sound design changes (needs numpy; the game itself does not).
All music is original and generated here: slow ambient pads, soft bells and a
synthetic reverb, rendered as seamless loops.
"""
import os
import wave

import numpy as np

ROOT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..")
OUT = os.path.join(ROOT, "assets", "audio")
RNG = np.random.default_rng(20261107)


def midi_hz(m):
    return 440.0 * 2 ** ((m - 69) / 12)


def save(name, data, rate):
    """data: float array, mono (n,) or stereo (n, 2), range about -1..1"""
    data = np.asarray(data, dtype=np.float64)
    if data.ndim == 1:
        data = data[:, None]
    peak = np.max(np.abs(data)) or 1.0
    data = data / peak * 0.89
    pcm = (data * 32767).astype("<i2")
    with wave.open(os.path.join(OUT, name), "wb") as handle:
        handle.setnchannels(pcm.shape[1])
        handle.setsampwidth(2)
        handle.setframerate(rate)
        handle.writeframes(pcm.tobytes())
    print(f"{name}: {len(pcm) / rate:.1f}s")


def lowpass(signal, rate, cutoff):
    spec = np.fft.rfft(signal, axis=0)
    freqs = np.fft.rfftfreq(signal.shape[0], 1 / rate)
    curve = 1 / (1 + (freqs / cutoff) ** 4)
    if signal.ndim == 2:
        curve = curve[:, None]
    return np.fft.irfft(spec * curve, n=signal.shape[0], axis=0)


def circular_reverb(signal, rate, seconds=4.0, mix=0.55, seed=1):
    """Convolve with decaying noise, wrapping the tail so the loop stays seamless."""
    rng = np.random.default_rng(seed)
    n = signal.shape[0]
    out = np.zeros((n, 2))
    length = int(seconds * rate)
    t = np.arange(length) / rate
    for ch in range(2):
        ir = rng.standard_normal(length) * np.exp(-t * 6.9 / seconds)
        ir = lowpass(ir, rate, 3500)
        ir[: int(0.012 * rate)] *= np.linspace(0, 1, int(0.012 * rate))
        ir /= np.sqrt(np.sum(ir ** 2))
        size = n  # circular convolution over exactly one loop length
        wet = np.fft.irfft(np.fft.rfft(signal[:, ch], size) * np.fft.rfft(ir, size), size)
        out[:, ch] = signal[:, ch] * (1 - mix) + wet * mix * 1.6
    return out


def envelope(n, rate, attack, release):
    env = np.ones(n)
    a = min(n, max(1, int(attack * rate)))
    r = min(n - a, max(1, int(release * rate)))
    env[:a] = np.linspace(0, 1, a) ** 2
    env[n - r:] *= np.linspace(1, 0, r) ** 2
    return env


def pad_voice(m, seconds, rate, bright=1.0):
    n = int(seconds * rate)
    t = np.arange(n) / rate
    out = np.zeros(n)
    for detune in (-0.07, 0.0, 0.08):
        f = midi_hz(m + detune)
        phase = RNG.uniform(0, 2 * np.pi)
        # soft saw from a few harmonics
        for h, amp in ((1, 1.0), (2, 0.42 * bright), (3, 0.2 * bright), (4, 0.09 * bright), (5, 0.05 * bright)):
            out += amp * np.sin(2 * np.pi * f * h * t + phase * h)
    lfo = 1 + 0.18 * np.sin(2 * np.pi * RNG.uniform(0.07, 0.15) * t + RNG.uniform(0, 6))
    return out * lfo * envelope(n, rate, seconds * 0.35, seconds * 0.45) / 3


def bell(m, seconds, rate, decay=2.2):
    n = int(seconds * rate)
    t = np.arange(n) / rate
    f = midi_hz(m)
    out = (np.sin(2 * np.pi * f * t) + 0.35 * np.sin(2 * np.pi * f * 2.76 * t) * np.exp(-t * 3)
           + 0.18 * np.sin(2 * np.pi * f * 5.4 * t) * np.exp(-t * 6))
    env = np.exp(-t * decay)
    env[: int(0.004 * rate)] *= np.linspace(0, 1, int(0.004 * rate))
    return out * env


def place(buffer, sound, start, gain=1.0, pan=0.0):
    """Add a mono sound into a stereo loop buffer, wrapping around the end."""
    n = buffer.shape[0]
    left = gain * np.sqrt((1 - pan) / 2)
    right = gain * np.sqrt((1 + pan) / 2)
    idx = (np.arange(len(sound)) + start) % n
    np.add.at(buffer[:, 0], idx, sound * left)
    np.add.at(buffer[:, 1], idx, sound * right)


def ambient_track(rate, chords, chord_seconds, scale, bells_per_chord, root_bass, seed, bright):
    global RNG
    RNG = np.random.default_rng(seed)
    total = len(chords) * chord_seconds
    n = int(total * rate)
    buf = np.zeros((n, 2))
    overlap = 2.5
    for i, chord in enumerate(chords):
        start = int((i * chord_seconds - overlap / 2) * rate)
        for j, m in enumerate(chord):
            voice = pad_voice(m, chord_seconds + overlap, rate, bright)
            place(buf, voice, start, 0.16, pan=(j / max(1, len(chord) - 1)) * 1.2 - 0.6)
        bass = pad_voice(root_bass[i], chord_seconds + overlap, rate, 0.3)
        place(buf, bass, start, 0.22, 0.0)
        # gentle bells drawn from the scale, never crowded
        times = np.sort(RNG.uniform(0.3, chord_seconds - 0.5, bells_per_chord))
        for k, tm in enumerate(times):
            note = int(RNG.choice(scale))
            place(buf, bell(note, 4.5, rate, decay=RNG.uniform(1.2, 2.0)),
                  int((i * chord_seconds + tm) * rate), RNG.uniform(0.05, 0.09), RNG.uniform(-0.7, 0.7))
    # a soft wind-like noise bed
    noise = lowpass(RNG.standard_normal((n, 2)), rate, 500)
    swell = 0.5 + 0.5 * np.sin(2 * np.pi * np.arange(n) / n * 3)[:, None]
    buf += noise * 0.012 * swell
    buf = lowpass(buf, rate, 5200)
    return circular_reverb(buf, rate, seconds=5.0, mix=0.5, seed=seed)


def music():
    rate = 22050
    # Title: warm F major, music-box bells over soft pads
    chords = [[65, 69, 72, 76], [62, 65, 69, 72], [58, 62, 65, 69, 72], [60, 64, 67, 70],
              [57, 60, 64, 69], [62, 65, 69, 74], [58, 62, 65, 70], [60, 65, 67, 72]]
    bass = [41, 38, 34, 36, 33, 38, 34, 36]
    scale = [77, 79, 81, 84, 86, 88, 89, 91]
    save("bgm_title.wav", ambient_track(rate, chords, 6, scale, 3, bass, 31, 0.85), rate)
    # Reading and questions: slow, very calm A-flat lydian colours that stay out of the way
    chords = [[56, 60, 63, 67], [58, 62, 65, 70], [53, 56, 60, 63, 67], [51, 55, 58, 62],
              [56, 60, 63, 70], [55, 58, 62, 65], [53, 58, 60, 65], [51, 55, 60, 63]]
    bass = [32, 34, 29, 27, 32, 31, 29, 27]
    scale = [72, 74, 75, 79, 80, 82, 84, 87]
    save("bgm_game.wav", ambient_track(rate, chords, 8, scale, 2, bass, 47, 0.6), rate)


def tone(freq, seconds, rate, wave_kind="sine", decay=8.0, attack=0.003):
    n = int(seconds * rate)
    t = np.arange(n) / rate
    f = np.asarray(freq) if np.ndim(freq) else np.full(n, freq)
    phase = 2 * np.pi * np.cumsum(f) / rate
    if wave_kind == "sine":
        s = np.sin(phase)
    elif wave_kind == "tri":
        s = 2 / np.pi * np.arcsin(np.sin(phase))
    elif wave_kind == "square":
        s = np.tanh(np.sin(phase) * 4)
    else:
        s = np.sin(phase) + 0.3 * np.sin(2 * phase)
    env = np.exp(-t * decay)
    a = max(1, int(attack * rate))
    env[:a] *= np.linspace(0, 1, a)
    return s * env


def effects():
    rate = 44100

    def cat(*parts):
        return np.concatenate(parts)

    def silence(s):
        return np.zeros(int(s * rate))

    def mix(*sounds):
        n = max(len(s) for s in sounds)
        out = np.zeros(n)
        for s in sounds:
            out[: len(s)] += s
        return out

    def stereo(mono, verb=0.25):
        pad = np.concatenate([mono, np.zeros(int(0.6 * rate))])
        rng = np.random.default_rng(5)
        length = int(0.5 * rate)
        t = np.arange(length) / rate
        out = np.zeros((len(pad), 2))
        for ch in range(2):
            ir = rng.standard_normal(length) * np.exp(-t * 12)
            ir /= np.sqrt(np.sum(ir ** 2))
            wet = np.convolve(pad, ir)[: len(pad)]
            out[:, ch] = pad * (1 - verb) + wet * verb
        return out

    def arp(notes, step, length, kind="bell", decay=4):
        return mix(*[cat(silence(i * step), tone(midi_hz(m), length, rate, kind, decay=decay))
                     for i, m in enumerate(notes)])

    save("click.wav", stereo(tone(1100, 0.07, rate, "tri", decay=55) * 0.6, 0.1), rate)
    save("hover.wav", tone(2000, 0.03, rate, decay=120) * 0.3, rate)
    save("type.wav", tone(1500, 0.03, rate, "tri", decay=110) * 0.4, rate)
    save("tick.wav", tone(1700, 0.05, rate, "sine", decay=70) * 0.7, rate)
    save("count.wav", tone(midi_hz(88), 0.12, rate, "bell", decay=30) * 0.6, rate)
    # a soft paper rustle for turning the page
    n = int(0.35 * rate)
    noise = np.random.default_rng(2).standard_normal(n)
    env = np.sin(np.linspace(0, np.pi, n)) ** 2
    rustle = lowpass(noise * env, rate, 3000) - lowpass(noise * env, rate, 600)
    save("page.wav", stereo(rustle * 0.8, 0.2), rate)
    save("correct.wav", stereo(arp([76, 79, 84, 88], 0.08, 0.8), 0.35), rate)
    save("wrong.wav", stereo(cat(tone(330, 0.14, rate, "tri", decay=7), tone(262, 0.3, rate, "tri", decay=6))), rate)
    save("reveal.wav", stereo(arp([72, 71, 69], 0.12, 0.7, "tri", 4), 0.35), rate)
    save("start.wav", stereo(arp([67, 72, 76], 0.09, 0.8), 0.35), rate)
    save("level_clear.wav", stereo(mix(arp([67, 72, 76, 79, 84, 88], 0.11, 1.4, "bell", 3),
                                       cat(silence(0.55), tone(midi_hz(60), 1.6, rate, "tri", decay=2) * 0.5)), 0.4), rate)
    save("fanfare.wav", stereo(mix(arp([60, 64, 67, 72, 67, 72, 76, 79, 84], 0.12, 1.6, "bell", 2.5),
                                   cat(silence(0.95), arp([48, 55, 60], 0.0, 2.2, "tri", 1.5) * 0.5)), 0.45), rate)
    save("time_up.wav", stereo(arp([67, 63, 60, 55], 0.22, 0.6, "tri", 4), 0.4), rate)
    save("new_record.wav", stereo(arp([72, 79, 84, 88, 91], 0.08, 0.9), 0.4), rate)


if __name__ == "__main__":
    os.makedirs(OUT, exist_ok=True)
    effects()
    music()
