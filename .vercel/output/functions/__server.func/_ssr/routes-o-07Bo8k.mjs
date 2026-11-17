import { i as __toESM } from "../_runtime.mjs";
import { K as require_react, b as require_jsx_runtime } from "../_libs/@tanstack/react-router+[...].mjs";
//#region node_modules/.nitro/vite/services/ssr/assets/routes-o-07Bo8k.js
var import_react = /* @__PURE__ */ __toESM(require_react());
var import_jsx_runtime = require_jsx_runtime();
var RUN_NOTE = "10 SCISSOR JUMPS EVERY 75 STEPS";
function chart(goals) {
	return [
		{
			name: "TOE TOUCHES",
			seconds: 120,
			goal: goals[0],
			unit: "REPS",
			action: "toe"
		},
		{
			name: "SIT-UPS",
			seconds: 60,
			goal: goals[1],
			unit: "REPS",
			action: "situp"
		},
		{
			name: "BACK EXTENSIONS",
			seconds: 60,
			goal: goals[2],
			unit: "REPS",
			action: "back"
		},
		{
			name: "KNEE PUSH-UPS",
			seconds: 60,
			goal: goals[3],
			unit: "REPS",
			action: "pushup"
		},
		{
			name: "STATIONARY RUN",
			seconds: 360,
			goal: goals[4],
			unit: "STEPS",
			action: "run",
			note: RUN_NOTE
		}
	];
}
var LEVELS = {
	"D-": {
		id: "D-",
		label: "Chart 1: D-",
		exercises: chart([
			2,
			3,
			4,
			2,
			100
		])
	},
	D: {
		id: "D",
		label: "Chart 1: D",
		exercises: chart([
			3,
			4,
			5,
			3,
			145
		])
	},
	"D+": {
		id: "D+",
		label: "Chart 1: D+",
		exercises: chart([
			4,
			5,
			6,
			3,
			175
		])
	}
};
var LEVEL_ORDER = [
	"D-",
	"D",
	"D+"
];
function isLevelId(value) {
	return value === "D-" || value === "D" || value === "D+";
}
var RUN_BANNERS = [
	{
		at: 60,
		text: "5 MINUTES LEFT"
	},
	{
		at: 120,
		text: "4 MINUTES LEFT"
	},
	{
		at: 180,
		text: "3 MINUTES LEFT"
	},
	{
		at: 240,
		text: "2 MINUTES LEFT"
	},
	{
		at: 300,
		text: "1 MINUTE LEFT"
	}
];
var FRAME_COUNTS = {
	idle: 4,
	toe: 4,
	situp: 4,
	back: 4,
	pushup: 4,
	run: 4,
	scissor: 4,
	crash: 1
};
function spriteSrc(action, frame) {
	return `/sprites/${action}/${frame}.png`;
}
function formatRemain(seconds) {
	const s = Math.max(0, Math.ceil(seconds - 1e-6));
	return `${Math.floor(s / 60)}:${(s % 60).toString().padStart(2, "0")}`;
}
function formatClock(seconds) {
	const s = Math.max(0, Math.floor(seconds + 1e-6));
	const h = Math.floor(s / 3600);
	const m = Math.floor(s % 3600 / 60);
	const r = s % 60;
	const pad = (n) => n.toString().padStart(2, "0");
	return `${pad(h)}:${pad(m)}:${pad(r)}`;
}
function exerciseCue(exercise) {
	const unit = exercise.unit === "STEPS" ? "steps" : "reps";
	return `${exercise.name.toLowerCase()}. ${exercise.goal} ${unit}.`;
}
function createSim() {
	return {
		phase: "idle",
		levelId: "D-",
		index: 0,
		phaseElapsed: 0,
		workoutBase: 0,
		running: false,
		banner: null,
		firedMarks: 0,
		lastPop: 0,
		wall: 0
	};
}
function snapshot(sim) {
	return {
		...sim,
		banner: sim.banner ? { ...sim.banner } : null
	};
}
function resetFields(sim) {
	sim.phase = "idle";
	sim.index = 0;
	sim.phaseElapsed = 0;
	sim.workoutBase = 0;
	sim.running = false;
	sim.banner = null;
	sim.firedMarks = 0;
	sim.lastPop = 0;
}
function resetSim(sim) {
	const levelId = sim.levelId;
	resetFields(sim);
	sim.levelId = levelId;
}
function popFor(remain) {
	if (remain <= 0 || remain > 5) return 0;
	return Math.ceil(remain - 1e-9);
}
function syncPop(sim, duration, speakIt, hooks) {
	const pop = popFor(duration - sim.phaseElapsed);
	if (pop === sim.lastPop) return;
	if (pop > 0) hooks.onCountdown(pop, speakIt);
	sim.lastPop = pop;
}
function enterWork(sim, level, index, hooks) {
	sim.phase = "work";
	sim.index = index;
	sim.phaseElapsed = 0;
	sim.banner = null;
	sim.firedMarks = 0;
	sim.lastPop = 0;
	sim.running = true;
	hooks.onIntervalStart(level.exercises[index]);
}
function enterOutro(sim, hooks) {
	sim.phase = "outro";
	sim.phaseElapsed = 0;
	sim.banner = null;
	sim.lastPop = 0;
	sim.running = true;
	hooks.onComplete();
}
function completeInterval(sim, level, hooks) {
	const exercise = level.exercises[sim.index];
	sim.workoutBase += exercise.seconds;
	if (sim.index < level.exercises.length - 1) enterWork(sim, level, sim.index + 1, hooks);
	else enterOutro(sim, hooks);
}
function beginIntro(sim, hooks) {
	if (sim.phase === "done") resetFields(sim);
	sim.phase = "intro";
	sim.index = 0;
	sim.phaseElapsed = 0;
	sim.workoutBase = 0;
	sim.banner = null;
	sim.firedMarks = 0;
	sim.running = true;
	sim.lastPop = 5;
	hooks.onCountdown(5, false);
}
function pauseSim(sim) {
	sim.running = false;
}
function resumeSim(sim) {
	if (sim.phase === "idle" || sim.phase === "done") return;
	sim.running = true;
}
function skipSim(sim, level, hooks) {
	if (sim.phase === "done") resetFields(sim);
	if (sim.phase === "idle" || sim.phase === "intro") {
		sim.workoutBase = 0;
		enterWork(sim, level, 0, hooks);
		return;
	}
	if (sim.phase === "work") {
		completeInterval(sim, level, hooks);
		return;
	}
	if (sim.phase === "outro") {
		sim.phase = "done";
		sim.running = false;
		sim.phaseElapsed = 10;
		hooks.onOutroDone();
	}
}
function advance(sim, dt, level, hooks) {
	sim.wall += dt;
	if (!sim.running) return;
	if (sim.phase === "intro") {
		sim.phaseElapsed += dt;
		if (sim.phaseElapsed >= 5) {
			enterWork(sim, level, 0, hooks);
			return;
		}
		syncPop(sim, 5, false, hooks);
		return;
	}
	if (sim.phase === "work") {
		const prev = sim.phaseElapsed;
		sim.phaseElapsed += dt;
		const exercise = level.exercises[sim.index];
		if (sim.index === 4) RUN_BANNERS.forEach((mark, bit) => {
			const flag = 1 << bit;
			if (prev < mark.at && sim.phaseElapsed >= mark.at && (sim.firedMarks & flag) === 0) {
				sim.firedMarks |= flag;
				sim.banner = {
					text: mark.text,
					until: sim.phaseElapsed + 2.6
				};
				hooks.onMinute();
			}
		});
		if (sim.banner && sim.phaseElapsed >= sim.banner.until) sim.banner = null;
		if (sim.phaseElapsed >= exercise.seconds) {
			completeInterval(sim, level, hooks);
			return;
		}
		syncPop(sim, exercise.seconds, true, hooks);
		return;
	}
	if (sim.phase === "outro") {
		sim.phaseElapsed += dt;
		if (sim.phaseElapsed >= 10) {
			sim.phaseElapsed = 10;
			sim.phase = "done";
			sim.running = false;
			hooks.onOutroDone();
		}
	}
}
var ctx = null;
var master = null;
var enabled = true;
function ctor() {
	const w = window;
	return window.AudioContext ?? w.webkitAudioContext;
}
function setSfxEnabled(on) {
	enabled = on;
	if (ctx && master) master.gain.setTargetAtTime(on ? .22 : 0, ctx.currentTime, .02);
}
/** Create and resume inside a user gesture. Synchronous resume call. */
function unlockAudio() {
	if (!ctx) {
		ctx = new (ctor())({ latencyHint: "interactive" });
		master = ctx.createGain();
		master.gain.value = enabled ? .22 : 0;
		master.connect(ctx.destination);
	}
	if (ctx.state === "suspended") ctx.resume();
}
function resumeAudio() {
	if (ctx && ctx.state === "suspended") ctx.resume();
}
function tone(freq, when, dur, type, gain) {
	if (!ctx || !master || !enabled) return;
	const osc = ctx.createOscillator();
	const amp = ctx.createGain();
	osc.type = type;
	osc.frequency.setValueAtTime(freq, when);
	amp.gain.setValueAtTime(1e-4, when);
	amp.gain.exponentialRampToValueAtTime(Math.max(.001, gain), when + .012);
	amp.gain.exponentialRampToValueAtTime(1e-4, when + dur);
	osc.connect(amp);
	amp.connect(master);
	osc.start(when);
	osc.stop(when + dur + .03);
	osc.onended = () => {
		osc.disconnect();
		amp.disconnect();
	};
}
var COUNT_FREQ = [
	0,
	880,
	740,
	659,
	587,
	494
];
function beepCountdown(n) {
	if (!ctx) return;
	const now = ctx.currentTime;
	tone(COUNT_FREQ[n] ?? 523, now, n === 1 ? .16 : .08, "square", n === 1 ? .7 : .5);
}
function chimeStart() {
	if (!ctx) return;
	const now = ctx.currentTime;
	[
		523,
		659,
		784,
		1046
	].forEach((freq, i) => {
		tone(freq, now + i * .07, .11, "square", .42);
	});
}
function chimeMinute() {
	if (!ctx) return;
	const now = ctx.currentTime;
	tone(880, now, .09, "triangle", .32);
	tone(1175, now + .08, .14, "triangle", .26);
}
function fanfare() {
	if (!ctx) return;
	const now = ctx.currentTime;
	[
		523,
		659,
		784,
		1046,
		784,
		1046,
		1319,
		1568
	].forEach((freq, i) => {
		tone(freq, now + i * .11, .18, "square", .38);
		tone(freq / 2, now + i * .11, .2, "triangle", .22);
	});
}
var COUNT_WORDS = {
	5: "Five",
	4: "four",
	3: "three",
	2: "two",
	1: "one"
};
var voiceOn = true;
var pending = 0;
function setVoiceEnabled(on) {
	voiceOn = on;
	if (!on) stopSpeech();
}
function stopSpeech() {
	window.clearTimeout(pending);
	window.speechSynthesis?.cancel();
}
function resumeSpeech() {
	if (window.speechSynthesis?.paused) window.speechSynthesis.resume();
}
function pickVoice() {
	const voices = window.speechSynthesis?.getVoices() ?? [];
	return voices.find((v) => /en-US/i.test(v.lang) && /samantha|daniel|google us english/i.test(v.name)) ?? voices.find((v) => v.lang.toLowerCase().startsWith("en"));
}
function speak(text) {
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
function speakCount(n) {
	const word = COUNT_WORDS[n];
	if (word) speak(word);
}
if (typeof window !== "undefined") window.speechSynthesis?.addEventListener("voiceschanged", () => {
	pickVoice();
});
var VICTORY_LINES = [
	{
		at: .4,
		text: "CHART 1 COMPLETE!"
	},
	{
		at: 2.15,
		text: "YOU WIN!"
	},
	{
		at: 4.05,
		text: "PERFECT!"
	}
];
var TREE_SLOTS = [
	"tree-a",
	"tree-b",
	"tree-c",
	"tree-d",
	"tree-e",
	"tree-f"
];
function frameOf(sim) {
	const level = LEVELS[sim.levelId];
	if (sim.phase === "outro" || sim.phase === "done") return "red";
	if (sim.phase === "work" && sim.index === 4) return level.exercises[4].seconds - sim.phaseElapsed <= 10 ? "red" : "gold";
	return "teal";
}
function actionOf(sim, level) {
	if (sim.phase === "idle" || sim.phase === "intro") return "idle";
	const t = sim.phase === "done" ? 10 : sim.phaseElapsed;
	if (sim.phase === "outro" || sim.phase === "done") return t >= 2.62 ? "crash" : "run";
	if (sim.index === 4 && sim.phaseElapsed % 45 >= 40) return "scissor";
	return level.exercises[sim.index].action;
}
function popOf(sim, level) {
	const duration = sim.phase === "intro" ? 5 : sim.phase === "work" ? level.exercises[sim.index].seconds : 0;
	if (!duration) return null;
	const remain = duration - sim.phaseElapsed;
	if (remain <= 0 || remain > 5) return null;
	return Math.ceil(remain - 1e-9);
}
function remainOf(sim, level) {
	if (sim.phase === "idle") return 5;
	if (sim.phase === "intro") return Math.max(0, 5 - sim.phaseElapsed);
	if (sim.phase === "work") return Math.max(0, level.exercises[sim.index].seconds - sim.phaseElapsed);
	if (sim.phase === "outro") return Math.max(0, 10 - sim.phaseElapsed);
	return 0;
}
function clockOf(sim) {
	if (sim.phase === "work") return sim.workoutBase + sim.phaseElapsed;
	if (sim.phase === "outro" || sim.phase === "done") return sim.workoutBase;
	return 0;
}
function nextOf(sim, level) {
	if (sim.phase === "idle" || sim.phase === "intro") return level.exercises[0];
	if (sim.phase === "work" && sim.index < level.exercises.length - 1) return level.exercises[sim.index + 1];
	return null;
}
function athleteMotion(phase, elapsed) {
	if (phase !== "outro" && phase !== "done") return "none";
	const t = phase === "done" ? 10 : elapsed;
	if (t < 1.15) {
		const eased = (t / 1.15) ** 2;
		return `translateY(${(-eased * 155).toFixed(1)}%) rotate(${(-eased * 18).toFixed(1)}deg)`;
	}
	if (t < 2.15) return "translateY(-160%) rotate(-18deg)";
	if (t < 2.7) {
		const p = (t - 2.15) / .55;
		return `translateY(${(-160 * (1 - p)).toFixed(1)}%) rotate(${(-18 * (1 - p)).toFixed(1)}deg)`;
	}
	if (t < 3.15) {
		const squash = Math.sin(Math.min(1, (t - 2.7) / .45) * Math.PI);
		return `translateY(${(squash * 6).toFixed(1)}%) scale(${(1 + squash * .42).toFixed(3)}, ${(1 - squash * .5).toFixed(3)})`;
	}
	return "none";
}
function shadowAmount(phase, elapsed) {
	if (phase !== "outro" && phase !== "done") return 1;
	const t = phase === "done" ? 10 : elapsed;
	if (t < 1.15) return 1 - t / 1.15 * .82;
	if (t < 2.15) return .16;
	if (t < 2.7) return .16 + (t - 2.15) / .55 * .9;
	return 1;
}
function frameIndex(action, sim) {
	const count = FRAME_COUNTS[action];
	if (count <= 1) return 0;
	const time = sim.phase === "idle" ? sim.wall : sim.phaseElapsed;
	return Math.floor(time * (action === "idle" ? 4 : 8)) % count;
}
function Pines() {
	return /* @__PURE__ */ (0, import_jsx_runtime.jsx)(import_jsx_runtime.Fragment, { children: TREE_SLOTS.map((slot) => /* @__PURE__ */ (0, import_jsx_runtime.jsx)("div", {
		className: `tree ${slot}`,
		"aria-hidden": true,
		children: /* @__PURE__ */ (0, import_jsx_runtime.jsxs)("svg", {
			viewBox: "0 0 40 70",
			children: [
				/* @__PURE__ */ (0, import_jsx_runtime.jsx)("polygon", {
					points: "20,2 37,30 31,30 39,50 1,50 9,30 3,30",
					fill: "var(--color-pine)"
				}),
				/* @__PURE__ */ (0, import_jsx_runtime.jsx)("polygon", {
					points: "20,16 31,36 9,36",
					fill: "var(--color-pine-dark)"
				}),
				/* @__PURE__ */ (0, import_jsx_runtime.jsx)("rect", {
					x: "16",
					y: "50",
					width: "8",
					height: "16",
					fill: "var(--color-trunk)"
				})
			]
		})
	}, slot)) });
}
function WorkoutApp() {
	const sim = (0, import_react.useRef)(createSim());
	const [view, setView] = (0, import_react.useState)(() => snapshot(sim.current));
	const [sfxOn, setSfxOn] = (0, import_react.useState)(true);
	const [voiceOn, setVoiceOn] = (0, import_react.useState)(true);
	const wakeRef = (0, import_react.useRef)(null);
	const hooksRef = (0, import_react.useRef)(null);
	const apiRef = (0, import_react.useRef)({
		start: () => {},
		skip: () => {},
		reset: () => {}
	});
	const acquireWake = (0, import_react.useCallback)(async () => {
		try {
			if (!("wakeLock" in navigator)) return;
			wakeRef.current = await navigator.wakeLock.request("screen");
		} catch {}
	}, []);
	const releaseWake = (0, import_react.useCallback)(() => {
		const lock = wakeRef.current;
		wakeRef.current = null;
		lock?.release().catch(() => {});
	}, []);
	hooksRef.current = {
		onCountdown(n, speakIt) {
			beepCountdown(n);
			if (speakIt) speakCount(n);
		},
		onIntervalStart(exercise) {
			chimeStart();
			speak(exerciseCue(exercise));
		},
		onMinute() {
			chimeMinute();
		},
		onComplete() {
			stopSpeech();
			fanfare();
		},
		onOutroDone() {
			releaseWake();
		}
	};
	const publish = (0, import_react.useCallback)(() => {
		setView(snapshot(sim.current));
	}, []);
	const onStart = (0, import_react.useCallback)(() => {
		unlockAudio();
		const current = sim.current;
		const hooks = hooksRef.current;
		if (current.phase === "idle" || current.phase === "done") {
			beginIntro(current, hooks);
			acquireWake();
			speak("Ready, go!");
			publish();
			return;
		}
		if (current.running) {
			pauseSim(current);
			releaseWake();
			stopSpeech();
			publish();
			return;
		}
		resumeSim(current);
		acquireWake();
		publish();
	}, [
		acquireWake,
		publish,
		releaseWake
	]);
	const onSkip = (0, import_react.useCallback)(() => {
		unlockAudio();
		const current = sim.current;
		skipSim(current, LEVELS[current.levelId], hooksRef.current);
		if (current.running) acquireWake();
		else releaseWake();
		publish();
	}, [
		acquireWake,
		publish,
		releaseWake
	]);
	const onReset = (0, import_react.useCallback)(() => {
		resetSim(sim.current);
		releaseWake();
		stopSpeech();
		publish();
	}, [publish, releaseWake]);
	apiRef.current.start = onStart;
	apiRef.current.skip = onSkip;
	apiRef.current.reset = onReset;
	(0, import_react.useEffect)(() => {
		const storedLevel = localStorage.getItem("5bx-level");
		if (storedLevel && isLevelId(storedLevel)) sim.current.levelId = storedLevel;
		if (localStorage.getItem("5bx-sfx") === "0") {
			setSfxEnabled(false);
			setSfxOn(false);
		}
		if (localStorage.getItem("5bx-voice") === "0") {
			setVoiceEnabled(false);
			setVoiceOn(false);
		}
		publish();
	}, [publish]);
	(0, import_react.useEffect)(() => {
		let raf = 0;
		let last = performance.now();
		let published = 0;
		let dead = false;
		const loop = (now) => {
			if (dead) return;
			const dt = Math.min(.05, (now - last) / 1e3);
			last = now;
			const current = sim.current;
			const mark = `${current.phase}|${current.index}|${current.running}|${current.banner?.text ?? ""}`;
			advance(current, dt, LEVELS[current.levelId], hooksRef.current);
			if (`${current.phase}|${current.index}|${current.running}|${current.banner?.text ?? ""}` !== mark || now - published > 50) {
				published = now;
				setView(snapshot(current));
			}
			raf = requestAnimationFrame(loop);
		};
		raf = requestAnimationFrame(loop);
		return () => {
			dead = true;
			cancelAnimationFrame(raf);
		};
	}, []);
	(0, import_react.useEffect)(() => {
		const onVis = () => {
			if (document.visibilityState !== "visible") return;
			resumeAudio();
			resumeSpeech();
			const current = sim.current;
			if (current.running && current.phase !== "idle" && current.phase !== "done") acquireWake();
		};
		document.addEventListener("visibilitychange", onVis);
		return () => document.removeEventListener("visibilitychange", onVis);
	}, [acquireWake]);
	(0, import_react.useEffect)(() => {
		const onKey = (event) => {
			const tag = event.target?.tagName;
			if (tag === "SELECT" || tag === "INPUT" || tag === "TEXTAREA") return;
			if (event.code === "Space") {
				event.preventDefault();
				apiRef.current.start();
			} else if (event.key === "s" || event.key === "S") apiRef.current.skip();
			else if (event.key === "r" || event.key === "R") apiRef.current.reset();
		};
		window.addEventListener("keydown", onKey);
		return () => window.removeEventListener("keydown", onKey);
	}, []);
	(0, import_react.useEffect)(() => {
		const actions = Object.keys(FRAME_COUNTS);
		for (const action of actions) for (let frame = 0; frame < FRAME_COUNTS[action]; frame += 1) {
			const img = new Image();
			img.src = spriteSrc(action, frame);
		}
		return () => {
			releaseWake();
		};
	}, [releaseWake]);
	const level = LEVELS[view.levelId];
	const action = actionOf(view, level);
	const pop = popOf(view, level);
	const exercise = view.phase === "work" ? level.exercises[view.index] : null;
	const scissoring = action === "scissor";
	const outroTime = view.phase === "done" ? 10 : view.phaseElapsed;
	const showVictory = view.phase === "outro" || view.phase === "done";
	const impact = view.phase === "outro" && view.phaseElapsed >= 2.62 && view.phaseElapsed < 2.95;
	const shaking = view.phase === "outro" && view.phaseElapsed >= 2.62 && view.phaseElapsed < 3.15;
	const shadow = shadowAmount(view.phase, view.phaseElapsed);
	const upcoming = nextOf(view, level);
	const paused = !view.running && (view.phase === "intro" || view.phase === "work" || view.phase === "outro");
	const status = view.phase === "work" && exercise ? `${exercise.name}. Goal ${exercise.goal} ${exercise.unit}.` : view.phase === "intro" || view.phase === "idle" ? `5BX workout, ${level.label}. Get ready.` : "Chart 1 complete.";
	const onLevel = (id) => {
		if (id === sim.current.levelId && sim.current.phase === "idle") return;
		sim.current.levelId = id;
		resetSim(sim.current);
		localStorage.setItem("5bx-level", id);
		releaseWake();
		stopSpeech();
		publish();
	};
	return /* @__PURE__ */ (0, import_jsx_runtime.jsxs)("main", {
		className: "shell",
		"data-frame": frameOf(view),
		"data-phase": view.phase,
		"data-interval": view.index + 1,
		children: [
			/* @__PURE__ */ (0, import_jsx_runtime.jsx)("p", {
				className: "sr-only",
				"aria-live": "polite",
				children: status
			}),
			/* @__PURE__ */ (0, import_jsx_runtime.jsxs)("section", {
				className: shaking ? "stage shake" : "stage",
				"aria-label": "Workout stage",
				children: [
					/* @__PURE__ */ (0, import_jsx_runtime.jsx)("div", { className: "sky" }),
					/* @__PURE__ */ (0, import_jsx_runtime.jsx)("div", {
						className: "sun",
						"aria-hidden": true
					}),
					/* @__PURE__ */ (0, import_jsx_runtime.jsx)("div", { className: "ground" }),
					/* @__PURE__ */ (0, import_jsx_runtime.jsx)(Pines, {}),
					/* @__PURE__ */ (0, import_jsx_runtime.jsx)("div", {
						className: "contact-shadow",
						style: {
							transform: `translateX(-50%) scaleX(${shadow.toFixed(3)})`,
							opacity: Math.max(.12, shadow)
						},
						"aria-hidden": true
					}),
					/* @__PURE__ */ (0, import_jsx_runtime.jsx)("div", {
						className: action === "crash" ? "athlete splat" : "athlete",
						children: /* @__PURE__ */ (0, import_jsx_runtime.jsx)("div", {
							className: "athlete-motion",
							style: { transform: athleteMotion(view.phase, view.phaseElapsed) },
							children: /* @__PURE__ */ (0, import_jsx_runtime.jsx)("img", {
								src: spriteSrc(action, frameIndex(action, view)),
								alt: "",
								className: view.phase === "idle" || view.phase === "intro" ? "ghost" : void 0,
								draggable: false
							})
						})
					}),
					/* @__PURE__ */ (0, import_jsx_runtime.jsx)("header", {
						className: "hud-top",
						children: view.phase === "idle" || view.phase === "intro" ? /* @__PURE__ */ (0, import_jsx_runtime.jsxs)(import_jsx_runtime.Fragment, { children: [
							/* @__PURE__ */ (0, import_jsx_runtime.jsx)("p", {
								className: "kicker",
								children: "— CHART 1 —"
							}),
							/* @__PURE__ */ (0, import_jsx_runtime.jsxs)("h1", {
								className: "title",
								children: ["5BX WORKOUT — ", level.id]
							}),
							/* @__PURE__ */ (0, import_jsx_runtime.jsx)("p", {
								className: "ready-line",
								children: "GET READY"
							}),
							view.phase === "idle" ? /* @__PURE__ */ (0, import_jsx_runtime.jsx)("p", {
								className: "press-start",
								children: "PRESS START"
							}) : null
						] }) : showVictory ? /* @__PURE__ */ (0, import_jsx_runtime.jsxs)(import_jsx_runtime.Fragment, { children: [
							/* @__PURE__ */ (0, import_jsx_runtime.jsx)("p", {
								className: "kicker",
								children: "— FINISH —"
							}),
							/* @__PURE__ */ (0, import_jsx_runtime.jsx)("h1", {
								className: "title",
								children: "CHART 1"
							}),
							/* @__PURE__ */ (0, import_jsx_runtime.jsx)("p", {
								className: "goal",
								children: "COMPLETE"
							})
						] }) : /* @__PURE__ */ (0, import_jsx_runtime.jsxs)(import_jsx_runtime.Fragment, { children: [
							/* @__PURE__ */ (0, import_jsx_runtime.jsxs)("p", {
								className: "kicker",
								children: [
									"— No. ",
									view.index + 1,
									"/5 —"
								]
							}),
							/* @__PURE__ */ (0, import_jsx_runtime.jsx)("h1", {
								className: "title",
								children: exercise?.name
							}),
							/* @__PURE__ */ (0, import_jsx_runtime.jsxs)("p", {
								className: "goal",
								children: [
									"GOAL: ",
									exercise?.goal,
									" ",
									exercise?.unit
								]
							}),
							exercise?.note ? /* @__PURE__ */ (0, import_jsx_runtime.jsx)("p", {
								className: "note",
								children: exercise.note
							}) : null
						] })
					}),
					paused ? /* @__PURE__ */ (0, import_jsx_runtime.jsx)("p", {
						className: "paused-flag",
						children: "PAUSED"
					}) : null,
					pop ? /* @__PURE__ */ (0, import_jsx_runtime.jsx)("div", {
						className: "countdown",
						children: /* @__PURE__ */ (0, import_jsx_runtime.jsx)("span", {
							className: "countdown-num",
							children: pop
						})
					}) : null,
					view.banner && view.phase === "work" ? /* @__PURE__ */ (0, import_jsx_runtime.jsx)("div", {
						className: "milestone",
						children: view.banner.text
					}) : null,
					scissoring && !pop ? /* @__PURE__ */ (0, import_jsx_runtime.jsx)("div", {
						className: "alert-badge",
						children: "10 SCISSOR JUMPS!"
					}) : null,
					impact ? /* @__PURE__ */ (0, import_jsx_runtime.jsx)("div", { className: "impact-flash" }) : null,
					showVictory ? /* @__PURE__ */ (0, import_jsx_runtime.jsx)("div", {
						className: "victory",
						children: VICTORY_LINES.filter((line) => outroTime >= line.at).map((line) => /* @__PURE__ */ (0, import_jsx_runtime.jsx)("p", {
							className: "victory-line slam",
							children: line.text
						}, line.text))
					}) : null,
					/* @__PURE__ */ (0, import_jsx_runtime.jsxs)("footer", {
						className: "ground-hud",
						children: [
							/* @__PURE__ */ (0, import_jsx_runtime.jsxs)("div", {
								className: "hud-cell",
								children: [/* @__PURE__ */ (0, import_jsx_runtime.jsx)("span", {
									className: "hud-label",
									children: "TIME REMAINING"
								}), /* @__PURE__ */ (0, import_jsx_runtime.jsx)("span", {
									className: "hud-time",
									children: formatRemain(remainOf(view, level))
								})]
							}),
							/* @__PURE__ */ (0, import_jsx_runtime.jsx)("div", {
								className: "hud-cell",
								children: /* @__PURE__ */ (0, import_jsx_runtime.jsx)("span", {
									className: "clock",
									children: formatClock(clockOf(view))
								})
							}),
							/* @__PURE__ */ (0, import_jsx_runtime.jsxs)("div", {
								className: "hud-cell hud-next",
								children: [/* @__PURE__ */ (0, import_jsx_runtime.jsx)("span", {
									className: "hud-label",
									children: "NEXT"
								}), upcoming ? /* @__PURE__ */ (0, import_jsx_runtime.jsxs)("div", {
									className: "mini",
									children: [/* @__PURE__ */ (0, import_jsx_runtime.jsx)("img", {
										src: spriteSrc(upcoming.action, 0),
										alt: ""
									}), /* @__PURE__ */ (0, import_jsx_runtime.jsx)("span", { children: upcoming.name })]
								}) : /* @__PURE__ */ (0, import_jsx_runtime.jsx)("span", {
									className: "mini-finish",
									children: "FINISH"
								})]
							})
						]
					})
				]
			}),
			/* @__PURE__ */ (0, import_jsx_runtime.jsxs)("nav", {
				className: "controls",
				"aria-label": "Workout controls",
				children: [
					/* @__PURE__ */ (0, import_jsx_runtime.jsx)("select", {
						"aria-label": "Level",
						value: view.levelId,
						onChange: (event) => {
							const id = event.target.value;
							if (isLevelId(id)) onLevel(id);
						},
						children: LEVEL_ORDER.map((id) => /* @__PURE__ */ (0, import_jsx_runtime.jsx)("option", {
							value: id,
							children: LEVELS[id].label
						}, id))
					}),
					/* @__PURE__ */ (0, import_jsx_runtime.jsx)("button", {
						type: "button",
						className: view.running ? void 0 : "primary",
						onClick: onStart,
						children: view.running ? "Pause" : "Start"
					}),
					/* @__PURE__ */ (0, import_jsx_runtime.jsx)("button", {
						type: "button",
						onClick: onReset,
						children: "Reset"
					}),
					/* @__PURE__ */ (0, import_jsx_runtime.jsx)("button", {
						type: "button",
						"aria-label": "Skip interval",
						onClick: onSkip,
						children: "Skip"
					}),
					/* @__PURE__ */ (0, import_jsx_runtime.jsxs)("button", {
						type: "button",
						"aria-pressed": sfxOn,
						onClick: () => {
							const next = !sfxOn;
							setSfxOn(next);
							setSfxEnabled(next);
							localStorage.setItem("5bx-sfx", next ? "1" : "0");
							if (next) unlockAudio();
						},
						children: ["SFX: ", sfxOn ? "ON" : "OFF"]
					}),
					/* @__PURE__ */ (0, import_jsx_runtime.jsxs)("button", {
						type: "button",
						"aria-pressed": voiceOn,
						onClick: () => {
							const next = !voiceOn;
							setVoiceOn(next);
							setVoiceEnabled(next);
							localStorage.setItem("5bx-voice", next ? "1" : "0");
						},
						children: ["Voice: ", voiceOn ? "ON" : "OFF"]
					})
				]
			})
		]
	});
}
function Home() {
	return /* @__PURE__ */ (0, import_jsx_runtime.jsx)(WorkoutApp, {});
}
//#endregion
export { Home as component };
