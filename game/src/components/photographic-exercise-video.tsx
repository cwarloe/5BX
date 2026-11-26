import { useCallback, useEffect, useRef, useState } from "react";
import {
  matchesReviewedDuration,
  photoMayAutoPlay,
  resolvePhotoClip,
  type ApprovedPhotoClip,
  type ApprovedPhotoRegistry,
  type PhotoPlaybackSlot,
} from "@/lib/photo-video";

type Props = {
  registry: ApprovedPhotoRegistry;
  slot: PhotoPlaybackSlot | null;
  playing: boolean;
  label: string;
  buildBase: string;
};

type ValidatedProps = {
  clip: ApprovedPhotoClip;
  slot: PhotoPlaybackSlot;
  playing: boolean;
  label: string;
  onFailure: () => void;
};

function clockTarget(slot: PhotoPlaybackSlot, clip: ApprovedPhotoClip): number {
  return slot.elapsedSeconds % clip.durationSeconds;
}

/**
 * Mount only after registry validation. Fetch metadata invisibly; never
 * autoPlay. Its separate keyed lifecycle guarantees that reducing motion or
 * switching intervals tears down the *actual* mounted video element.
 */
function ValidatedPhotoElement({ clip, slot, playing, label, onFailure }: ValidatedProps) {
  const videoRef = useRef<HTMLVideoElement | null>(null);
  const validated = useRef(false);
  const failed = useRef(false);
  const disposed = useRef(false);
  const [visible, setVisible] = useState(false);

  const release = useCallback((player: HTMLVideoElement) => {
    try { player.pause(); } catch { /* already detached or media failure */ }
    player.removeAttribute("src");
    try { player.load(); } catch { /* source is already discarded */ }
  }, []);

  const fail = useCallback(() => {
    if (disposed.current || failed.current) return;
    failed.current = true;
    validated.current = false;
    setVisible(false);
    if (videoRef.current) release(videoRef.current);
    onFailure();
  }, [onFailure, release]);

  useEffect(() => {
    const actualPlayer = videoRef.current;
    disposed.current = false;
    return () => {
      disposed.current = true;
      validated.current = false;
      if (actualPlayer) release(actualPlayer);
    };
  }, [release]);

  const frameTolerance = 1 / clip.fps;

  const revealIfAligned = (player: HTMLVideoElement) => {
    if (!validated.current || failed.current || disposed.current || player.readyState < 2) return;
    if (Math.abs(player.currentTime - clockTarget(slot, clip)) <= frameTolerance) {
      setVisible(true);
    }
  };

  // The game simulation is the clock; decoder delay must never extend a beat.
  useEffect(() => {
    const player = videoRef.current;
    if (!player || !validated.current || failed.current || disposed.current) return;
    const target = clockTarget(slot, clip);
    // A newer simulation tick can overtake an earlier invisible seek. Keep
    // the pending media aligned; never reveal a stale frame to catch up.
    if (!visible) {
      if (!player.seeking && Math.abs(player.currentTime - target) > frameTolerance) {
        try {
          player.currentTime = target;
        } catch {
          fail();
        }
      }
      return;
    }
    if (Math.abs(player.currentTime - target) > frameTolerance) {
      player.pause();
      setVisible(false);
      try {
        player.currentTime = target;
      } catch {
        fail();
      }
      return;
    }
    if (!playing) {
      player.pause();
      return;
    }
    if (!player.paused) return;
    try {
      // A rejected browser gesture policy is a HOLD, not a sprite fallback.
      void Promise.resolve(player.play()).catch(fail);
    } catch {
      fail();
    }
  }, [clip, fail, frameTolerance, playing, slot, visible]);

  return (
    <video
      ref={videoRef}
      className="photo-exercise-video"
      src={clip.url}
      style={{ visibility: visible ? "visible" : "hidden" }}
      aria-hidden={!visible}
      aria-label={`Photographic demonstration: ${label}`}
      muted
      loop
      playsInline
      preload="metadata"
      onLoadedMetadata={(event) => {
        const player = event.currentTarget;
        if (!matchesReviewedDuration(player.duration, clip, slot.slotSeconds)) {
          fail();
          return;
        }
        validated.current = true;
        const target = clockTarget(slot, clip);
        if (Math.abs(player.currentTime - target) > 0.001) {
          try {
            player.currentTime = target;
          } catch {
            fail();
          }
        } else {
          revealIfAligned(player);
        }
      }}
      onLoadedData={(event) => revealIfAligned(event.currentTarget)}
      onSeeked={(event) => revealIfAligned(event.currentTarget)}
      onError={fail}
    />
  );
}

/** Video-first only: there is no sprite import, rendering, or media fallback. */
export function PhotographicExerciseVideo({ registry, slot, playing, label, buildBase }: Props) {
  const [failedKey, setFailedKey] = useState<string | null>(null);
  const [prefersReducedMotion, setPrefersReducedMotion] = useState(() =>
    typeof window !== "undefined" &&
    typeof window.matchMedia === "function" &&
    window.matchMedia("(prefers-reduced-motion: reduce)").matches,
  );
  const [motionOptIn, setMotionOptIn] = useState(false);

  useEffect(() => {
    const query = window.matchMedia?.("(prefers-reduced-motion: reduce)");
    if (!query) return;
    const update = () => {
      setPrefersReducedMotion(query.matches);
      if (query.matches) setMotionOptIn(false);
    };
    query.addEventListener("change", update);
    return () => query.removeEventListener("change", update);
  }, []);

  // A new workout must not silently inherit a prior opt-in session.
  useEffect(() => {
    if (!slot) setMotionOptIn(false);
  }, [slot]);

  const result = slot ? resolvePhotoClip(registry, slot, buildBase) : { status: "missing" as const };
  const clip = result.status === "ready" ? result.clip : null;
  const key = clip && slot
    ? `${slot.registryKey}:${slot.segmentKey}:${clip.revision}:${clip.sha256}`
    : null;
  const failed = key !== null && failedKey === key;
  const motionHeld = prefersReducedMotion && !motionOptIn;
  const permittedToPlay = photoMayAutoPlay(playing, prefersReducedMotion, motionOptIn);

  if (!slot || !clip || failed) {
    const reason = failed ? "playback failed" : result.status.replaceAll("-", " ");
    return (
      <div className="photo-video-unavailable" role="status" aria-live="polite">
        <strong>{label}</strong>
        <span>Photographic video unavailable ({reason}).</span>
        <span>Awaiting release-approved MP4; no substitute animation is shown.</span>
      </div>
    );
  }

  if (motionHeld) {
    return (
      <div className="photo-video-unavailable" role="status">
        <strong>{label}</strong>
        <span>Demonstration held to respect your reduced-motion preference.</span>
        <button type="button" className="photo-motion-opt-in" onClick={() => setMotionOptIn(true)}>
          Play photographic demonstration
        </button>
      </div>
    );
  }

  return (
    <ValidatedPhotoElement
      key={key}
      clip={clip}
      slot={slot}
      playing={permittedToPlay}
      label={label}
      onFailure={() => setFailedKey(key)}
    />
  );
}
