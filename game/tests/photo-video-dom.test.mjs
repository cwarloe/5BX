/** React DOM lifecycle tests use synthetic metadata, never an actual exercise MP4. */
import { afterEach, beforeEach, describe, it } from "node:test";
import assert from "node:assert/strict";
import React from "react";
import { JSDOM } from "jsdom";

const dom = new JSDOM("<!doctype html><html><body></body></html>", {
  url: "https://example.invalid/5BX/game/",
});
Object.defineProperty(globalThis, "window", { configurable: true, value: dom.window });
Object.defineProperty(globalThis, "document", { configurable: true, value: dom.window.document });
Object.defineProperty(globalThis, "navigator", { configurable: true, value: dom.window.navigator });
Object.defineProperty(globalThis, "HTMLElement", { configurable: true, value: dom.window.HTMLElement });
Object.defineProperty(globalThis, "HTMLMediaElement", { configurable: true, value: dom.window.HTMLMediaElement });
Object.defineProperty(globalThis, "IS_REACT_ACT_ENVIRONMENT", { configurable: true, writable: true, value: true });

const mediaQueries = new Set();
const query = {
  matches: false,
  addEventListener(_type, listener) { mediaQueries.add(listener); },
  removeEventListener(_type, listener) { mediaQueries.delete(listener); },
};
window.matchMedia = () => query;

const calls = [];
HTMLMediaElement.prototype.play = function () {
  calls.push({ op: "play", video: this });
  return Promise.resolve();
};
HTMLMediaElement.prototype.pause = function () {
  calls.push({ op: "pause", video: this });
};
HTMLMediaElement.prototype.load = function () {
  calls.push({ op: "load", video: this });
};

// Dynamic import follows DOM initialization, so React testing-library and the
// component see an actual document at module setup time.
const { act, cleanup, fireEvent, render, waitFor } = await import("@testing-library/react");
const { PhotographicExerciseVideo } = await import("../src/components/photographic-exercise-video.tsx");
const { approvedMediaPath, photoWorkSlot } = await import("../src/lib/photo-video.ts");

const sha = "a".repeat(64);
const clip = {
  chart: 1, exercise: 5, action: "scissor", exerciseId: "chart1-scissor-jump",
  revision: "synthetic-unreleased-dom-test", sha256: sha, url: approvedMediaPath(sha),
  mediaType: "video/mp4", codec: "h264", durationSeconds: 5,
  frameCount: 120, fps: 24,
};
const validRegistry = { schemaVersion: 1, clips: { "c1-e5-scissor": clip } };
const emptyRegistry = { schemaVersion: 1, clips: {} };
const slot = photoWorkSlot("scissor", 1, 4, 40, 360);

function mount({ registry = validRegistry, slotValue = slot, playing = true } = {}) {
  return render(React.createElement(PhotographicExerciseVideo, {
    registry, slot: slotValue, playing, label: "Scissor jumps", buildBase: "/5BX/game/",
  }));
}

function setMetadata(video, duration = 5, readyState = 2, currentTime = 0) {
  Object.defineProperties(video, {
    duration: { configurable: true, value: duration },
    readyState: { configurable: true, value: readyState },
    currentTime: { configurable: true, writable: true, value: currentTime },
    seeking: { configurable: true, value: false },
  });
}

function count(op, video) {
  return calls.filter((item) => item.op === op && (!video || item.video === video)).length;
}

beforeEach(() => {
  calls.length = 0;
  query.matches = false;
});
afterEach(() => {
  cleanup();
  mediaQueries.clear();
});

describe("photographic React video lifecycle (synthetic DOM)", () => {
  it("never mounts media or a sprite when registry is empty", () => {
    const { container } = mount({ registry: emptyRegistry });
    assert.equal(container.querySelector("video"), null);
    assert.equal(container.querySelector("img"), null);
    assert.match(container.textContent, /unavailable.*missing/i);
    assert.equal(count("play"), 0);
  });

  it("never plays or displays a frame before checked metadata", async () => {
    const { container } = mount();
    const player = container.querySelector("video");
    assert.ok(player);
    assert.equal(player.hasAttribute("autoplay"), false);
    assert.equal(player.style.visibility, "hidden");
    assert.equal(player.getAttribute("aria-hidden"), "true");
    assert.equal(count("play"), 0);
    setMetadata(player, 5);
    fireEvent.loadedMetadata(player);
    await waitFor(() => assert.equal(player.style.visibility, "visible"));
    assert.equal(player.getAttribute("aria-hidden"), "false");
    await waitFor(() => assert.ok(count("play", player) >= 1));
  });

  it("restores admitted source after React StrictMode effect rehearsal", async () => {
    const { container, unmount } = render(React.createElement(React.StrictMode, null,
      React.createElement(PhotographicExerciseVideo, {
        registry: validRegistry, slot, playing: true,
        label: "Scissor jumps", buildBase: "/5BX/game/",
      }),
    ));
    const player = container.querySelector("video");
    assert.ok(player);
    assert.equal(player.getAttribute("src"), clip.url);
    assert.equal(player.style.visibility, "hidden");
    assert.equal(count("play", player), 0);
    setMetadata(player);
    fireEvent.loadedMetadata(player);
    await waitFor(() => assert.equal(player.style.visibility, "visible"));
    await waitFor(() => assert.ok(count("play", player) >= 1));
    unmount();
    assert.equal(player.hasAttribute("src"), false);
  });

  it("rejects overlong metadata before showing or playing anything", () => {
    const { container } = mount();
    const player = container.querySelector("video");
    setMetadata(player, 5.05);
    fireEvent.loadedMetadata(player);
    assert.equal(count("play", player), 0);
    assert.equal(player.hasAttribute("src"), false);
    assert.equal(container.querySelector("video"), null);
    assert.match(container.textContent, /unavailable.*playback failed/i);
    assert.equal(container.querySelector("img"), null);
  });

  it("waits for the simulation-aligned seek before revealing an in-progress interval", async () => {
    const late = photoWorkSlot("scissor", 1, 4, 42, 360);
    const { container } = mount({ slotValue: late });
    const player = container.querySelector("video");
    setMetadata(player, 5, 2, 0);
    fireEvent.loadedMetadata(player);
    assert.equal(player.currentTime, 2);
    assert.equal(player.style.visibility, "hidden");
    assert.equal(count("play", player), 0);
    fireEvent.seeked(player);
    await waitFor(() => assert.equal(player.style.visibility, "visible"));
    await waitFor(() => assert.ok(count("play", player) >= 1));
  });

  it("pauses on workout pause and tears down an old clip on segment switch", async () => {
    const props = (slotValue, playing) => React.createElement(PhotographicExerciseVideo, {
      registry: validRegistry, slot: slotValue, playing,
      label: "Scissor jumps", buildBase: "/5BX/game/",
    });
    const { container, rerender } = render(props(slot, true));
    const player = container.querySelector("video");
    setMetadata(player);
    fireEvent.loadedMetadata(player);
    await waitFor(() => assert.ok(count("play", player) >= 1));
    const pausedBefore = count("pause", player);
    rerender(props(slot, false));
    await waitFor(() => assert.ok(count("pause", player) > pausedBefore));
    const nextJump = photoWorkSlot("scissor", 1, 4, 85, 360);
    rerender(props(nextJump, false));
    assert.ok(count("pause", player) > pausedBefore);
    assert.ok(count("load", player) >= 1);
    assert.equal(player.hasAttribute("src"), false);
    const replacement = container.querySelector("video");
    assert.ok(replacement && replacement !== player);
    assert.equal(replacement.style.visibility, "hidden");
    assert.equal(count("play", replacement), 0);
  });

  it("holds reduced-motion media until explicit opt-in and resets after workout", async () => {
    query.matches = true;
    const { container, rerender } = mount();
    assert.equal(container.querySelector("video"), null);
    const button = container.querySelector("button");
    assert.ok(button);
    fireEvent.click(button);
    const player = container.querySelector("video");
    assert.ok(player);
    assert.equal(player.style.visibility, "hidden");
    setMetadata(player);
    fireEvent.loadedMetadata(player);
    await waitFor(() => assert.ok(count("play", player) >= 1));
    rerender(React.createElement(PhotographicExerciseVideo, {
      registry: validRegistry, slot: null, playing: false,
      label: "5BX", buildBase: "/5BX/game/",
    }));
    assert.equal(player.hasAttribute("src"), false);
    rerender(React.createElement(PhotographicExerciseVideo, {
      registry: validRegistry, slot, playing: true,
      label: "Scissor jumps", buildBase: "/5BX/game/",
    }));
    assert.equal(container.querySelector("video"), null);
    assert.ok(container.querySelector("button"));
  });

  it("removes playing video immediately when reduced-motion preference changes", async () => {
    const { container } = mount();
    const player = container.querySelector("video");
    setMetadata(player);
    fireEvent.loadedMetadata(player);
    await waitFor(() => assert.ok(count("play", player) >= 1));
    query.matches = true;
    await act(async () => {
      for (const listener of mediaQueries) listener();
    });
    assert.equal(container.querySelector("video"), null);
    assert.ok(container.querySelector("button"));
    assert.equal(player.hasAttribute("src"), false);
    assert.ok(count("pause", player) >= 1);
  });

  it("treats browser play rejection as HOLD and discards the source", async () => {
    const original = HTMLMediaElement.prototype.play;
    HTMLMediaElement.prototype.play = function () {
      calls.push({ op: "play", video: this });
      return Promise.reject(new Error("browser prevented autoplay"));
    };
    try {
      const { container } = mount();
      const player = container.querySelector("video");
      setMetadata(player);
      fireEvent.loadedMetadata(player);
      await waitFor(() => assert.match(container.textContent, /playback failed/));
      assert.equal(player.hasAttribute("src"), false);
      assert.equal(container.querySelector("img"), null);
    } finally {
      HTMLMediaElement.prototype.play = original;
    }
  });

  it("ignores an interrupted pending play promise after pause, then can resume", async () => {
    const original = HTMLMediaElement.prototype.play;
    let rejectPending;
    HTMLMediaElement.prototype.play = function () {
      calls.push({ op: "play", video: this });
      return new Promise((_resolve, reject) => { rejectPending = reject; });
    };
    const props = (playing) => React.createElement(PhotographicExerciseVideo, {
      registry: validRegistry, slot, playing,
      label: "Scissor jumps", buildBase: "/5BX/game/",
    });
    try {
      const { container, rerender } = render(props(true));
      const player = container.querySelector("video");
      setMetadata(player);
      fireEvent.loadedMetadata(player);
      await waitFor(() => assert.equal(count("play", player), 1));
      rerender(props(false));
      await act(async () => {
        rejectPending(Object.assign(new Error("play interrupted by pause"), { name: "AbortError" }));
      });
      assert.equal(container.querySelector("video"), player);
      assert.equal(player.getAttribute("src"), clip.url);
      assert.doesNotMatch(container.textContent, /playback failed/i);
      rerender(props(true));
      await waitFor(() => assert.equal(count("play", player), 2));
    } finally {
      HTMLMediaElement.prototype.play = original;
    }
  });

  it("fails closed on media error and releases source on unmount", async () => {
    const { container, unmount } = mount();
    const player = container.querySelector("video");
    fireEvent.error(player);
    assert.equal(count("play", player), 0);
    assert.equal(player.hasAttribute("src"), false);
    assert.match(container.textContent, /playback failed/);
    const { container: second, unmount: secondUnmount } = mount();
    const secondVideo = second.querySelector("video");
    unmount();
    secondUnmount();
    assert.equal(secondVideo.hasAttribute("src"), false);
    assert.ok(count("pause", secondVideo) >= 1);
  });
});
