const COUNT_WORDS: Record<number, string> = {
  5: "Five",
  4: "four",
  3: "three",
  2: "two",
  1: "one",
};

let voiceOn = true;
let pending = 0;

export function setVoiceEnabled(on: boolean) {
  voiceOn = on;
  if (!on) stopSpeech();
}

export function voiceEnabled() {
  return voiceOn;
}

export function stopSpeech() {
  window.clearTimeout(pending);
  window.speechSynthesis?.cancel();
}

export function resumeSpeech() {
  if (window.speechSynthesis?.paused) window.speechSynthesis.resume();
}

function pickVoice(): SpeechSynthesisVoice | undefined {
  const voices = window.speechSynthesis?.getVoices() ?? [];
  return (
    voices.find((v) => /en-US/i.test(v.lang) && /samantha|daniel|google us english/i.test(v.name)) ??
    voices.find((v) => v.lang.toLowerCase().startsWith("en"))
  );
}

export function speak(text: string) {
  if (!voiceOn || typeof window === "undefined" || !window.speechSynthesis) return;
  const synth = window.speechSynthesis;
  synth.cancel();
  window.clearTimeout(pending);
  pending = window.setTimeout(() => {
    if (!voiceOn) return;
    const utter = new SpeechSynthesisUtterance(text);
    utter.lang = "en-US";
    utter.rate = 1.04;
    utter.pitch = 1;
    const voice = pickVoice();
    if (voice) utter.voice = voice;
    synth.speak(utter);
  }, 40);
}

export function speakCount(n: number) {
  const word = COUNT_WORDS[n];
  if (word) speak(word);
}

if (typeof window !== "undefined") {
  window.speechSynthesis?.addEventListener("voiceschanged", () => {
    pickVoice();
  });
}
