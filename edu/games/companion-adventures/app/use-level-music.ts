"use client";

import { useCallback, useEffect, useRef, useState } from "react";

const NORMAL_VOLUME = 0.12;
const DUCKED_VOLUME = 0.035;

export default function useLevelMusic(track: "level-one" | "level-two" | "level-three") {
  const [enabled, setEnabled] = useState(true);
  const audioRef = useRef<HTMLAudioElement | null>(null);
  const enabledRef = useRef(true);
  const duckedRef = useRef(false);
  const wantedRef = useRef(false);

  const ensureAudio = useCallback(() => {
    if (!audioRef.current) {
      const audio = new Audio(`/audio/music/${track}.mp3?v=story-music-20260731a`);
      audio.loop = true;
      audio.preload = "auto";
      audio.volume = duckedRef.current ? DUCKED_VOLUME : NORMAL_VOLUME;
      audioRef.current = audio;
    }
    return audioRef.current;
  }, [track]);

  const start = useCallback(() => {
    wantedRef.current = true;
    if (!enabledRef.current || document.visibilityState !== "visible") return;
    const audio = ensureAudio();
    audio.play().catch(() => undefined);
  }, [ensureAudio]);

  const stop = useCallback(() => {
    wantedRef.current = false;
    audioRef.current?.pause();
    if (audioRef.current) audioRef.current.currentTime = 0;
  }, []);

  const duck = useCallback((value: boolean) => {
    duckedRef.current = value;
    if (audioRef.current) audioRef.current.volume = value ? DUCKED_VOLUME : NORMAL_VOLUME;
  }, []);

  const toggle = useCallback(() => {
    const next = !enabledRef.current;
    enabledRef.current = next;
    setEnabled(next);
    try { localStorage.setItem("sft-background-music-v1", next ? "on" : "off"); } catch { /* optional */ }
    if (!next) audioRef.current?.pause();
    else if (wantedRef.current && document.visibilityState === "visible") ensureAudio().play().catch(() => undefined);
  }, [ensureAudio]);

  useEffect(() => {
    const timeout = window.setTimeout(() => {
      try {
        const next = localStorage.getItem("sft-background-music-v1") !== "off";
        enabledRef.current = next;
        setEnabled(next);
        if (!next) audioRef.current?.pause();
        else if (wantedRef.current && document.visibilityState === "visible") ensureAudio().play().catch(() => undefined);
      } catch { /* optional */ }
    }, 0);
    return () => window.clearTimeout(timeout);
  }, [ensureAudio]);

  useEffect(() => {
    const visibility = () => {
      if (document.visibilityState === "hidden") {
        audioRef.current?.pause();
        return;
      }
      if (enabledRef.current && wantedRef.current) ensureAudio().play().catch(() => undefined);
    };
    const pageHide = () => audioRef.current?.pause();
    const pageShow = () => {
      if (enabledRef.current && wantedRef.current && document.visibilityState === "visible") ensureAudio().play().catch(() => undefined);
    };
    document.addEventListener("visibilitychange", visibility);
    window.addEventListener("pagehide", pageHide);
    window.addEventListener("pageshow", pageShow);
    return () => {
      document.removeEventListener("visibilitychange", visibility);
      window.removeEventListener("pagehide", pageHide);
      window.removeEventListener("pageshow", pageShow);
      audioRef.current?.pause();
      audioRef.current = null;
    };
  }, [ensureAudio]);

  return { enabled, start, stop, toggle, duck };
}
