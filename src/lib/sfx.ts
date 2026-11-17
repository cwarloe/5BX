type OscKind = OscillatorType;

let ctx: AudioContext | null = null;
let master: GainNode | null = null;
let enabled = true;

function ctor(): typeof AudioContext {
  const w = window as Window & { webkitAudioContext?: typeof AudioContext };
  return window.AudioContext ?? w.webkitAudioContext!;
}

export function setSfxEnabled(on: boolean) {
  enabled = on;
  if (ctx && master) {
    master.gain.setTargetAtTime(on ? 0.22 : 0, ctx.currentTime, 0.02);
  }
}

export function sfxEnabled() {
  return enabled;
}

/** Create and resume inside a user gesture. Synchronous resume call. */
export function unlockAudio() {
  if (!ctx) {
    ctx = new (ctor())({ latencyHint: "interactive" });
    master = ctx.createGain();
    master.gain.value = enabled ? 0.22 : 0;
    master.connect(ctx.destination);
  }
  if (ctx.state === "suspended") {
    void ctx.resume();
  }
}

export function resumeAudio() {
  if (ctx && ctx.state === "suspended") void ctx.resume();
}

function tone(freq: number, when: number, dur: number, type: OscKind, gain: number) {
  if (!ctx || !master || !enabled) return;
  const osc = ctx.createOscillator();
  const amp = ctx.createGain();
  osc.type = type;
  osc.frequency.setValueAtTime(freq, when);
  amp.gain.setValueAtTime(0.0001, when);
  amp.gain.exponentialRampToValueAtTime(Math.max(0.001, gain), when + 0.012);
  amp.gain.exponentialRampToValueAtTime(0.0001, when + dur);
  osc.connect(amp);
  amp.connect(master);
  osc.start(when);
  osc.stop(when + dur + 0.03);
  osc.onended = () => {
    osc.disconnect();
    amp.disconnect();
  };
}

const COUNT_FREQ = [0, 880, 740, 659, 587, 494];

export function beepCountdown(n: number) {
  if (!ctx) return;
  const now = ctx.currentTime;
  const freq = COUNT_FREQ[n] ?? 523;
  tone(freq, now, n === 1 ? 0.16 : 0.08, "square", n === 1 ? 0.7 : 0.5);
}

export function chimeStart() {
  if (!ctx) return;
  const now = ctx.currentTime;
  [523, 659, 784, 1046].forEach((freq, i) => {
    tone(freq, now + i * 0.07, 0.11, "square", 0.42);
  });
}

export function chimeMinute() {
  if (!ctx) return;
  const now = ctx.currentTime;
  tone(880, now, 0.09, "triangle", 0.32);
  tone(1175, now + 0.08, 0.14, "triangle", 0.26);
}

export function fanfare() {
  if (!ctx) return;
  const now = ctx.currentTime;
  const notes = [523, 659, 784, 1046, 784, 1046, 1319, 1568];
  notes.forEach((freq, i) => {
    tone(freq, now + i * 0.11, 0.18, "square", 0.38);
    tone(freq / 2, now + i * 0.11, 0.2, "triangle", 0.22);
  });
}
