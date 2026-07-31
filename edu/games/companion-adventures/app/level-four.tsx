"use client";

import { CSSProperties, FormEvent, ReactNode, useEffect, useLayoutEffect, useRef, useState } from "react";
import LevelPrelude, { PreludeLine } from "./level-prelude";
import { startNarration, stopNarration } from "./narration-controller.mjs";
import {
  LEVEL_FOUR_NARRATION,
  LEVEL_FOUR_PICTURE_LABELS,
  levelFourRoundForRound,
  nextLevelFourRound,
  pendingLevelFourResolution,
  readLevelFourIntroSeen,
  readLevelFourResolution,
} from "./level-four-state.mjs";
import useLevelMusic from "./use-level-music";

type Character = "mira" | "tavi" | "sol" | "ivo";
type Activity = "search" | "build" | "memory" | "difference" | "trace" | "measure" | "friend" | "height" | "checkpoint";
type Resolution = "finish" | null;
type Line = { speaker: string; text: string; audio: string };
type Scene = {
  id: string;
  title: string;
  gameTitle: string;
  gameIcon: string;
  background: string;
  cast: Character[];
  journey: string;
  activity: Activity;
  lines: [Line, Line];
  prompt: string;
  success: Line;
};

const lineByAudio = new Map(LEVEL_FOUR_NARRATION.map((entry) => [entry.audio, entry]));
function authored(audio: string): Line {
  const entry = lineByAudio.get(audio);
  if (!entry) throw new Error(`Missing Level Four narration line: ${audio}`);
  return { speaker: entry.speaker, text: entry.text, audio: entry.audio };
}

export const LEVEL_FOUR_AUDIO_DIRECTORY = "/audio/e04-v1.0.1";
export const LEVEL_FOUR_MUSIC = "/audio/music/level-four.mp3";
export const LEVEL_FOUR_ASSETS = Object.freeze({
  search: "/art/stages/e04-stage-01-look-and-point-v2.png",
  build: "/art/stages/e04-stage-02-build-the-board-v1.png",
  memory: "/art/stages/e04-stage-03-curtain-memory-v1.png",
  difference: "/art/stages/e04-stage-04-difference-finder-v1.png",
  trace: "/art/stages/e04-stage-05-placement-record-v2.png",
  measure: "/art/stages/e04-stage-06-measuring-ribbon-v1.png",
  friend: "/art/stages/e04-stage-07-friend-check-v1.png",
  height: "/art/stages/e04-stage-08-height-check-v2.png",
  checkpoint: "/art/stages/e04-stage-09-record-checkpoint-v2.png",
  ivo: "/art/characters/individual/ivo.png",
});

const scenes: Scene[] = [
  {
    id: "search", title: "Look at the picture plan", gameTitle: "Find It With the Lens", gameIcon: "🔎", background: LEVEL_FOUR_ASSETS.search, cast: ["mira", "tavi", "sol", "ivo"], journey: "The friends step through the Sunrise Arch. The gate is shut. A picture plan and an empty Welcome Sign stand beside it.", activity: "search",
    lines: [authored("01a-narrator-gate"), authored("01b-mia-find")],
    prompt: "Tap the MOON corner. Tap Use the lens. Then choose the picture you see. You have three try lights. A wrong answer turns one off.",
    success: authored("01c-narrator-observation"),
  },
  {
    id: "build", title: "Build the Welcome Sign", gameTitle: "Welcome Sign Builder", gameIcon: "🧩", background: LEVEL_FOUR_ASSETS.build, cast: ["mira", "tavi", "sol", "ivo"], journey: "Ivo puts four picture cards beside the empty sign. The picture plan stays where everyone can see it.", activity: "build",
    lines: [authored("02a-narrator-ivo-arrives"), authored("02b-ivo-build")],
    prompt: "Choose a picture card. Then tap the corner where the plan shows that picture. Put all four pictures on the sign.",
    success: authored("02c-narrator-build-check"),
  },
  {
    id: "memory", title: "Build it again", gameTitle: "Curtain Copy", gameIcon: "🎭", background: LEVEL_FOUR_ASSETS.memory, cast: ["mira", "tavi", "sol", "ivo"], journey: "A playful gust pulls a curtain over the picture plan. You will build on one sign. Sol will build on another sign behind the curtain.", activity: "memory",
    lines: [authored("03a-narrator-curtain"), authored("03b-tavi-memory")],
    prompt: "Look at all four pictures. When the curtain closes, put one picture in every corner. Then tap Check my sign.",
    success: authored("03c-narrator-memory-check"),
  },
  {
    id: "difference", title: "What changed on Sol's sign?", gameTitle: "Difference Finder", gameIcon: "👀", background: LEVEL_FOUR_ASSETS.difference, cast: ["mira", "tavi", "sol", "ivo"], journey: "The team's sign matches. Sol uncovers the sign he made behind the curtain. Something on his sign is different.", activity: "difference",
    lines: [authored("04a-narrator-first-try"), authored("04b-sol-compare")],
    prompt: "Look at the picture plan and Sol's sign. Tap the two corners on Sol's sign that are different. A matching corner will get a tick.",
    success: authored("04c-narrator-retained-try"),
  },
  {
    id: "trace", title: "Follow Sol's four moves", gameTitle: "Sol's Step Cards", gameIcon: "🗂️", background: LEVEL_FOUR_ASSETS.trace, cast: ["mira", "tavi", "sol", "ivo"], journey: "Ivo opens four little cards. While Sol built, Ivo wrote down Move 1, Move 2, Move 3 and Move 4.", activity: "trace",
    lines: [authored("05a-narrator-footprints"), authored("05b-mia-trace")],
    prompt: "Tap the move cards in order. Start with Move 1. Find the first move that puts a picture in the wrong corner.",
    success: authored("05c-narrator-trace"),
  },
  {
    id: "measure", title: "Will it fit side to side?", gameTitle: "Measuring Ribbon", gameIcon: "📏", background: LEVEL_FOUR_ASSETS.measure, cast: ["mira", "tavi", "sol", "ivo"], journey: "Mia has fixed the two mixed-up pictures. She lifts the sign towards two hooks on the gate. Will it fit from the left hook to the right hook?", activity: "measure",
    lines: [authored("06a-narrator-frame"), authored("06b-ivo-measure")],
    prompt: "Use Shorter and Longer. Make the ribbon touch the left hook and the right hook. Then tap Test this width.",
    success: authored("06c-narrator-boundary"),
  },
  {
    id: "friend", title: "Ivo checks without peeking", gameTitle: "Ivo Makes His Own Sign", gameIcon: "🔍", background: LEVEL_FOUR_ASSETS.friend, cast: ["mira", "tavi", "sol", "ivo"], journey: "Before the sign is hung, the team hides it behind a cloth. Ivo takes the picture plan, four unused cards and an empty sign.", activity: "friend",
    lines: [authored("07a-narrator-friend-check"), authored("07b-tavi-scan")],
    prompt: "Find the next corner shown on Ivo's card. Move his lens there, then put that picture on Ivo's sign. Finish all four before lifting the cloth.",
    success: authored("07c-narrator-independent"),
  },
  {
    id: "height", title: "Did we check the height?", gameTitle: "Does It Fit Bottom to Top?", gameIcon: "↕️", background: LEVEL_FOUR_ASSETS.height, cast: ["mira", "tavi", "sol", "ivo"], journey: "The width fits. Mia thinks the sign may be ready. Ivo points to its bottom and top edges. They have not checked that way yet.", activity: "height",
    lines: [authored("08a-narrator-disagreement"), authored("08b-ivo-outcomes")],
    prompt: "Tap USE A HEIGHT TOOL. Then tap Taller until the blue tool touches the bottom and top edges. Tap Does it touch both edges?",
    success: authored("08c-narrator-outcomes"),
  },
  {
    id: "checkpoint", title: "Four checks for the gate", gameTitle: "Match the Answer Cards", gameIcon: "✅", background: LEVEL_FOUR_ASSETS.checkpoint, cast: ["mira", "tavi", "sol", "ivo"], journey: "The morning visitors wait beyond the gate. Four empty locks light up, and four answer cards wait on the table.", activity: "checkpoint",
    lines: [authored("09a-narrator-checkpoint"), authored("09b-mia-final")],
    prompt: "Choose an answer card. Then tap the gate question that the card answers. Put all four cards by their questions to open the gate.",
    success: authored("09c-narrator-final-check"),
  },
];

const preludeLines: PreludeLine[] = ["00a-narrator-recap", "00b-narrator-mission", "00c-narrator-discover", "00d-narrator-ivo"].map((audio) => {
  const entry = lineByAudio.get(audio);
  if (!entry?.heading) throw new Error(`Missing Level Four prelude heading: ${audio}`);
  return { speaker: entry.speaker, heading: entry.heading, text: entry.text, audio: entry.audio };
});

const names: Record<Character, string> = { mira: "Mia", tavi: "Tavi", sol: "Sol", ivo: "Ivo" };
const pictureIcons: Record<string, string> = { sunflower: "🌻", bee: "🐝", "watering-can": "🪣💧", boot: "🥾" };
const symbolIcons: Record<string, string> = { sun: "☀️", moon: "🌙", leaf: "🍃", star: "⭐" };
const endingLesson = authored("10-narrator-to-you");
const pictureLabels = LEVEL_FOUR_PICTURE_LABELS as Record<string, string>;

const bookCodes: Record<string, string> = {
  LOOKCLOSE: "Ivo's lens draws a harmless sparkling circle around the sign.",
  SIGNMAKER: "The four sign spaces glow in a gentle garden pattern.",
  KEEPFIRST: "Sol pins a copy of his first try into the team scrapbook.",
  SPOTCHANGE: "Two tiny leaf markers dance beside the two signs.",
  FOLLOWSTEPS: "Sol's step cards give a soft leaf-rustle celebration.",
  WIDTHONLY: "A ribbon stretches from one glowing side edge to the other.",
  FRIENDCHECK: "Ivo's four check marks play a gentle four-note tune.",
  MOREWORK: "Ivo opens one extra pocket in his satchel.",
  ALLCHECKED: "The Garden Welcome Sign sparkles after every check is complete.",
};

function image(name: Character) {
  if (name === "mira") return "/art/characters/individual/mira-v1.png";
  if (name === "ivo") return LEVEL_FOUR_ASSETS.ivo;
  return `/art/characters/individual/${name}.png`;
}

function CharacterSprite({ name, speaking, index }: { name: Character; speaking: boolean; index: number }) {
  return <div className={`actor actor-${name} ${speaking ? "speaking" : ""}`} style={{ "--actor-index": index } as CSSProperties}>
    <img src={image(name)} alt="" draggable={false} /><span>{names[name]}</span>
  </div>;
}

function Portrait({ speaker }: { speaker: string }) {
  const id = (speaker.toLowerCase() === "mia" ? "mira" : speaker.toLowerCase()) as Character;
  if (!(id in names)) return <span className="narrator-portrait" aria-hidden="true">📖</span>;
  return <img className={`portrait-${id}`} src={image(id)} alt="" aria-hidden="true" />;
}

function MiniGame({ title, icon, progress, children }: { title: string; icon: string; progress: string; children: ReactNode }) {
  return <section className="e03-mini-game e04-mini-game" aria-label={`${title} mini-game`}>
    <header className="mini-game-header"><span aria-hidden="true">{icon}</span><div><small>MINI-GAME</small><strong>{title}</strong></div><b>{progress}</b></header>
    {children}
  </section>;
}

function TryLights({ mistakes }: { mistakes: number }) {
  return <div className="try-lights" aria-label={`${3 - mistakes} of 3 try lights left`}><b>TRY LIGHTS</b>{[0, 1, 2].map((value) => <span key={value} className={value < 3 - mistakes ? "on" : "off"}>◆</span>)}</div>;
}

function entriesToPlacements(entries: string[]) {
  const placements: Record<number, string> = {};
  for (const entry of entries) {
    const [slot, picture] = entry.split(":");
    const index = Number(slot);
    if (Number.isInteger(index) && picture) placements[index] = picture;
  }
  return placements;
}

export type LevelFourProps = { onExit: () => void; onNext?: () => void };

export default function LevelFour({ onExit, onNext }: LevelFourProps) {
  const [sceneIndex, setSceneIndex] = useState(0);
  const [introSeen, setIntroSeen] = useState(false);
  const [preludeStep, setPreludeStep] = useState(-1);
  const [beat, setBeat] = useState(0);
  const [complete, setComplete] = useState(false);
  const [finished, setFinished] = useState(false);
  const [muted, setMuted] = useState(false);
  const [codesOpen, setCodesOpen] = useState(false);
  const [code, setCode] = useState("");
  const [codeMessage, setCodeMessage] = useState("");
  const [activityStep, setActivityStep] = useState(0);
  const [chosen, setChosen] = useState<string[]>([]);
  const [tried, setTried] = useState<string[]>([]);
  const [memoryAttempts, setMemoryAttempts] = useState<string[][]>([]);
  const [selected, setSelected] = useState("");
  const [meter, setMeter] = useState(0);
  const [wrong, setWrong] = useState("");
  const [mistakes, setMistakes] = useState(0);
  const [roundLost, setRoundLost] = useState(false);
  const [round, setRound] = useState(0);
  const [resolution, setResolution] = useState<Resolution>(null);
  const [storageReady, setStorageReady] = useState(false);
  const audioRef = useRef<HTMLAudioElement | null>(null);
  const soundRef = useRef<AudioContext | null>(null);
  const lastLineRef = useRef("");
  const narrationGenerationRef = useRef(0);
  const endingLessonPlayedRef = useRef(false);
  const progressRef = useRef<Record<string, unknown>>({});
  const { enabled: musicOn, start: startMusic, stop: stopMusic, toggle: toggleMusic, duck: duckMusic } = useLevelMusic("level-four");

  const scene = scenes[sceneIndex];
  const config = levelFourRoundForRound(round);
  const introOpen = !introSeen;
  const dialogueDone = beat >= scene.lines.length;
  const currentLine = complete ? scene.success : scene.lines[Math.min(beat, scene.lines.length - 1)];
  const speaking = (!dialogueDone || complete) ? (currentLine?.speaker.toLowerCase() === "mia" ? "mira" : currentLine?.speaker.toLowerCase()) : "";
  const inferredResolution = complete ? null : pendingLevelFourResolution(scene.activity, chosen);
  const pendingResolution: Resolution = resolution ?? inferredResolution;
  const resolving = pendingResolution !== null;

  useEffect(() => {
    try { localStorage.setItem("sft-active-level-v1", "e04"); } catch { /* optional */ }
  }, []);

  useEffect(() => { if (storageReady) startMusic(); }, [storageReady, startMusic]);

  useEffect(() => {
    const hide = () => {
      if (document.visibilityState === "hidden") stopNarration(audioRef, narrationGenerationRef, duckMusic);
    };
    const pageHide = () => stopNarration(audioRef, narrationGenerationRef, duckMusic);
    document.addEventListener("visibilitychange", hide);
    window.addEventListener("pagehide", pageHide);
    return () => {
      document.removeEventListener("visibilitychange", hide);
      window.removeEventListener("pagehide", pageHide);
    };
  }, [duckMusic]);

  useLayoutEffect(() => {
    progressRef.current = { introSeen, preludeStep, sceneIndex, beat, complete, finished, activityStep, chosen, tried, memoryAttempts, selected, meter, wrong, mistakes, roundLost, round, resolution };
  }, [introSeen, preludeStep, sceneIndex, beat, complete, finished, activityStep, chosen, tried, memoryAttempts, selected, meter, wrong, mistakes, roundLost, round, resolution]);

  useEffect(() => {
    const timeout = window.setTimeout(() => {
      try {
        const stored = localStorage.getItem("sft-e04-garden-check-v1");
        const saved = JSON.parse(stored ?? "{}");
        const restoredIntroSeen = readLevelFourIntroSeen(saved, stored !== null);
        const restoredSceneIndex = typeof saved.sceneIndex === "number" ? Math.min(Math.max(saved.sceneIndex, 0), scenes.length - 1) : 0;
        const restoredBeat = typeof saved.beat === "number" ? Math.max(saved.beat, 0) : 0;
        const restoredComplete = saved.complete === true;
        const restoredFinished = saved.finished === true;
        setIntroSeen(restoredIntroSeen);
        setPreludeStep(typeof saved.preludeStep === "number" ? Math.min(3, Math.max(-1, saved.preludeStep)) : -1);
        setSceneIndex(restoredSceneIndex);
        setBeat(restoredBeat);
        setComplete(restoredComplete);
        setFinished(restoredFinished);
        setActivityStep(typeof saved.activityStep === "number" ? Math.max(0, saved.activityStep) : 0);
        setChosen(Array.isArray(saved.chosen) ? saved.chosen.filter((value: unknown) => typeof value === "string") : []);
        setTried(Array.isArray(saved.tried) ? saved.tried.filter((value: unknown) => typeof value === "string") : []);
        setMemoryAttempts(Array.isArray(saved.memoryAttempts) ? saved.memoryAttempts.filter((attempt: unknown) => Array.isArray(attempt)).map((attempt: unknown[]) => attempt.filter((value) => typeof value === "string") as string[]) : []);
        setSelected(typeof saved.selected === "string" ? saved.selected : "");
        setMeter(typeof saved.meter === "number" ? Math.min(4, Math.max(0, saved.meter)) : 0);
        setWrong(typeof saved.wrong === "string" ? saved.wrong : "");
        setMistakes(typeof saved.mistakes === "number" ? Math.min(3, Math.max(0, saved.mistakes)) : 0);
        setRoundLost(saved.roundLost === true);
        setRound(typeof saved.round === "number" ? Math.max(0, saved.round) : 0);
        setResolution(readLevelFourResolution(saved.resolution));
        lastLineRef.current = restoredIntroSeen && !restoredFinished ? `${restoredSceneIndex}:${restoredComplete ? "success" : restoredBeat}` : "";
        endingLessonPlayedRef.current = restoredFinished;
      } catch {
        setRound(0);
      }
      setStorageReady(true);
    }, 0);
    return () => window.clearTimeout(timeout);
  }, []);

  useEffect(() => {
    if (!storageReady) return;
    const save = () => {
      try {
        localStorage.setItem("sft-e04-garden-check-v1", JSON.stringify(progressRef.current));
        localStorage.setItem("sft-active-level-v1", "e04");
      } catch { /* optional */ }
    };
    save();
    const hidden = () => { if (document.visibilityState === "hidden") save(); };
    window.addEventListener("pagehide", save);
    document.addEventListener("visibilitychange", hidden);
    return () => {
      window.removeEventListener("pagehide", save);
      document.removeEventListener("visibilitychange", hidden);
    };
  }, [storageReady, introSeen, preludeStep, sceneIndex, beat, complete, finished, activityStep, chosen, tried, memoryAttempts, selected, meter, wrong, mistakes, roundLost, round, resolution]);

  useEffect(() => {
    if (!storageReady || !finished || muted || endingLessonPlayedRef.current) return;
    endingLessonPlayedRef.current = true;
    const generation = narrationGenerationRef.current;
    const timeout = window.setTimeout(() => {
      if (document.visibilityState !== "visible" || narrationGenerationRef.current !== generation) return;
      if (audioRef.current && !audioRef.current.paused) return;
      playLine(endingLesson);
    }, 120);
    return () => window.clearTimeout(timeout);
    // playLine intentionally uses the latest audio settings.
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [storageReady, finished, muted]);

  useEffect(() => () => {
    stopNarration(audioRef, narrationGenerationRef, duckMusic);
    stopMusic();
  }, [duckMusic, stopMusic]);

  function playLine(entry = currentLine) {
    if (!entry || muted) return;
    startNarration({
      src: `${LEVEL_FOUR_AUDIO_DIRECTORY}/${entry.audio}.mp3?v=e04-review-20260731a`,
      audioRef,
      generationRef: narrationGenerationRef,
      duckMusic,
    });
  }

  function sound(kind: "tap" | "good" | "wrong" | "step") {
    if (muted) return;
    const context = soundRef.current ?? new AudioContext();
    soundRef.current = context;
    const now = context.currentTime;
    const tones = kind === "good" ? [392, 523, 659] : kind === "wrong" ? [170, 125] : kind === "step" ? [220, 294] : [330, 440];
    tones.forEach((frequency, index) => {
      const oscillator = context.createOscillator();
      const gain = context.createGain();
      oscillator.type = kind === "wrong" ? "triangle" : "sine";
      oscillator.frequency.value = frequency;
      gain.gain.setValueAtTime(0.0001, now + index * 0.07);
      gain.gain.exponentialRampToValueAtTime(0.065, now + index * 0.07 + 0.01);
      gain.gain.exponentialRampToValueAtTime(0.0001, now + index * 0.07 + 0.2);
      oscillator.connect(gain).connect(context.destination);
      oscillator.start(now + index * 0.07);
      oscillator.stop(now + index * 0.07 + 0.22);
    });
  }

  useEffect(() => {
    if (finished) return;
    if (introOpen || !currentLine || (dialogueDone && !complete)) {
      stopNarration(audioRef, narrationGenerationRef, duckMusic);
      return;
    }
    const key = `${sceneIndex}:${complete ? "success" : beat}`;
    const generation = narrationGenerationRef.current;
    const timeout = window.setTimeout(() => {
      if (document.visibilityState !== "visible" || narrationGenerationRef.current !== generation || lastLineRef.current === key) return;
      lastLineRef.current = key;
      playLine(currentLine);
    }, 25);
    return () => {
      window.clearTimeout(timeout);
      stopNarration(audioRef, narrationGenerationRef, duckMusic);
    };
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [finished, introOpen, sceneIndex, beat, complete, muted]);

  useEffect(() => {
    if (scene.activity !== "memory" || !dialogueDone || complete || roundLost || activityStep !== 0) return;
    const timeout = window.setTimeout(() => setActivityStep(1), 3500);
    return () => window.clearTimeout(timeout);
  }, [scene.activity, dialogueDone, complete, roundLost, activityStep, round]);

  function finishRound() {
    if (complete || roundLost) return;
    sound("good");
    setResolution(null);
    setWrong("");
    setMistakes(0);
    setRoundLost(false);
    setComplete(true);
  }

  useEffect(() => {
    if (!pendingResolution || complete || roundLost) return;
    const timeout = window.setTimeout(() => finishRound(), 0);
    return () => window.clearTimeout(timeout);
    // The timeout is a restore-only fallback; live winning inputs finish in
    // their own event so a correct final move is a synchronous one-shot win.
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [pendingResolution, complete, roundLost]);

  function wrongTry(message: string, token?: string) {
    if (roundLost || resolving || complete) return;
    sound("wrong");
    if (token) setTried((values) => values.includes(token) ? values : [...values, token]);
    const next = mistakes + 1;
    setMistakes(next);
    setWrong(message);
    if (next >= 3) setRoundLost(true);
    else window.setTimeout(() => setWrong(""), 2300);
  }

  function learningTry(message: string, token?: string) {
    if (roundLost || resolving || complete) return;
    sound("wrong");
    if (token) setTried((values) => values.includes(token) ? values : [...values, token]);
    setWrong(message);
    window.setTimeout(() => setWrong(""), 2300);
  }

  function resetActivity(nextRound: number) {
    setResolution(null);
    setRound(nextRound);
    setMistakes(0);
    setRoundLost(false);
    setWrong("");
    setActivityStep(0);
    setChosen([]);
    setTried([]);
    setMemoryAttempts([]);
    setSelected("");
    setMeter(0);
  }

  function retryRound() { sound("step"); resetActivity(nextLevelFourRound(round)); }
  function nextBeat() { sound("tap"); if (beat < scene.lines.length) setBeat((value) => value + 1); }
  function nextScene() {
    sound("step");
    if (sceneIndex === scenes.length - 1) {
      stopNarration(audioRef, narrationGenerationRef, duckMusic);
      endingLessonPlayedRef.current = false;
      setResolution(null);
      setFinished(true);
      return;
    }
    setSceneIndex((value) => value + 1);
    setBeat(0);
    setComplete(false);
    resetActivity(round);
    lastLineRef.current = "";
  }
  function replay() {
    stopNarration(audioRef, narrationGenerationRef, duckMusic);
    setComplete(false);
    resetActivity(nextLevelFourRound(round));
    lastLineRef.current = "";
  }
  function restart() {
    stopNarration(audioRef, narrationGenerationRef, duckMusic);
    setIntroSeen(false);
    setPreludeStep(-1);
    setSceneIndex(0);
    setBeat(0);
    setComplete(false);
    setFinished(false);
    resetActivity(0);
    lastLineRef.current = "";
    endingLessonPlayedRef.current = false;
    try {
      localStorage.removeItem("sft-e04-garden-check-v1");
      localStorage.setItem("sft-active-level-v1", "e04");
    } catch { /* optional */ }
  }
  function exitLevel() {
    stopNarration(audioRef, narrationGenerationRef, duckMusic);
    stopMusic();
    onExit();
  }
  function toggleNarration() {
    const next = !muted;
    setMuted(next);
    if (next) stopNarration(audioRef, narrationGenerationRef, duckMusic);
  }
  function submitCode(event: FormEvent) {
    event.preventDefault();
    const clean = code.toUpperCase().replace(/[^A-Z]/g, "");
    setCodeMessage(bookCodes[clean] ?? "That code is hiding on another book page. Keep looking.");
    if (bookCodes[clean]) { setCode(""); sound("good"); }
  }

  function pictureCard(picture: string, small = false) {
    return <><span className={small ? "small-picture" : ""} aria-hidden="true">{pictureIcons[picture]}</span><b>{pictureLabels[picture] ?? picture}</b></>;
  }

  function activity() {
    if (complete) return null;

    if (scene.activity === "search") {
      const lensIndex = Math.min(3, Math.max(0, meter));
      const look = () => {
        const corner = config.source[lensIndex];
        if (lensIndex !== config.requestIndex) {
          wrongTry(`You are looking at the ${corner.symbolLabel} corner. We need the ${config.source[config.requestIndex].symbolLabel} corner. This mark will stay so you remember where you looked. Try another corner.`, `search:${corner.symbol}`);
          return;
        }
        setSelected("lens-ready");
        sound("good");
      };
      const choosePicture = (picture: string) => {
        if (picture !== config.requestPicture) {
          wrongTry(`You chose the ${pictureLabels[picture]}. Look inside the ${config.source[config.requestIndex].symbolLabel} corner again. Which picture is there?`, `search-picture:${picture}`);
          return;
        }
        setChosen([config.requestPicture]);
        finishRound();
      };
      return <MiniGame title={scene.gameTitle} icon={scene.gameIcon} progress={`Find ${config.source[config.requestIndex].symbolLabel}`}>
        <div className="e04-search-game">
          <p className="e04-question-card">Which picture is at <strong>{config.source[config.requestIndex].symbolLabel}</strong>?</p>
          <div className="e04-reference-plan e04-source-lens" aria-label="The four-corner picture plan">
            <strong>PICTURE PLAN</strong>
            {config.source.map((entry: { symbol: string; symbolLabel: string; picture: string }, index: number) => <span key={entry.symbol} className={`${lensIndex === index ? "under-lens" : ""} ${tried.includes(`search:${entry.symbol}`) ? "kept-wrong" : ""}`}><small>{symbolIcons[entry.symbol]} {entry.symbolLabel}</small>{pictureCard(entry.picture, true)}{lensIndex === index && <i aria-hidden="true">🔍</i>}</span>)}
          </div>
          <label className="e04-lens-control"><strong>Choose a corner</strong><input aria-label="Move the looking lens" type="range" min="0" max="3" step="1" value={lensIndex} onChange={(event) => { setMeter(Number(event.currentTarget.value)); setSelected(""); sound("step"); }} /></label>
          <div className="e04-step-controls e04-corner-controls" aria-label="Choose a picture-plan corner">{config.source.map((entry: { symbol: string; symbolLabel: string }, index: number) => <button key={entry.symbol} type="button" className={lensIndex === index ? "active" : ""} aria-pressed={lensIndex === index} onClick={() => { setMeter(index); setSelected(""); sound("step"); }}>{symbolIcons[entry.symbol]} {entry.symbolLabel}</button>)}</div>
          {selected !== "lens-ready" ? <button className="primary" onClick={look}>Use the lens on {config.source[lensIndex].symbolLabel}</button> : <section className="e04-lens-answer"><strong>What picture can you see through the lens?</strong><div className="e04-card-tray">{config.cardTray.map((picture: string) => <button key={picture} className={tried.includes(`search-picture:${picture}`) ? "kept-wrong" : ""} onClick={() => choosePicture(picture)}>{pictureCard(picture)}</button>)}</div></section>}
          {tried.some((value) => value.startsWith("search:")) && <p className="kept-attempts">The corners you tried stay marked. Move the lens and look at the picture plan.</p>}
        </div>
      </MiniGame>;
    }

    if (scene.activity === "build") {
      const placements = entriesToPlacements(chosen);
      const placedPictures = new Set(Object.values(placements));
      const place = (picture: string, slot: number) => {
        if (!picture) { setWrong("Choose a picture card first, then choose a space on the sign."); return; }
        if (config.plan[slot] !== picture) {
          wrongTry(`The plan shows the ${pictureLabels[config.plan[slot]]} in this corner. Your try will stay marked. Look at the plan and try again.`, `build:${slot}:${picture}`);
          return;
        }
        const next = chosen.filter((entry) => !entry.startsWith(`${slot}:`) && !entry.endsWith(`:${picture}`));
        next.push(`${slot}:${picture}`);
        setChosen(next);
        setSelected("");
        if (new Set(next.map((entry) => entry.split(":")[0])).size === 4) finishRound(); else sound("good");
      };
      return <MiniGame title={scene.gameTitle} icon={scene.gameIcon} progress={`${Object.keys(placements).length}/4 pictures placed`}>
        <div className="e04-build-game">
          <div className="e04-reference-plan"><strong>PICTURE PLAN</strong>{config.source.map((entry: { symbol: string; symbolLabel: string; picture: string }) => <span key={entry.symbol}><small>{symbolIcons[entry.symbol]} {entry.symbolLabel}</small>{pictureCard(entry.picture, true)}</span>)}</div>
          <div className="e04-sign-board">{config.source.map((entry: { symbol: string; symbolLabel: string }, slot: number) => <button key={entry.symbol} className={placements[slot] ? "filled" : ""} onClick={() => place(selected, slot)} onDragOver={(event) => event.preventDefault()} onDrop={(event) => place(event.dataTransfer.getData("text/plain"), slot)}><small>{symbolIcons[entry.symbol]} {entry.symbolLabel}</small>{placements[slot] ? pictureCard(placements[slot]) : <span>?</span>}</button>)}</div>
          <div className="e04-card-tray">{config.cardTray.map((picture) => <button key={picture} className={selected === picture ? "selected" : ""} disabled={placedPictures.has(picture)} draggable={!placedPictures.has(picture)} onDragStart={(event) => event.dataTransfer.setData("text/plain", picture)} onClick={() => { setSelected(picture); sound("tap"); }}>{pictureCard(picture)}</button>)}</div>
          {tried.some((value) => value.startsWith("build:")) && <p className="kept-attempts">PLACES YOU TRIED: {tried.filter((value) => value.startsWith("build:")).length}</p>}
        </div>
      </MiniGame>;
    }

    if (scene.activity === "memory") {
      const curtainOpen = activityStep === 0;
      const choose = (picture: string) => {
        if (chosen.includes(picture) || chosen.length >= 4) return;
        const next = [...chosen, picture];
        setChosen(next);
        sound("tap");
      };
      const checkRebuild = () => {
        if (chosen.length !== 4) { setWrong("Put one picture in every corner before you check."); return; }
        if (chosen.every((picture, index) => picture === config.memoryPlan[index])) { finishRound(); return; }
        setMemoryAttempts((attempts) => attempts.some((attempt) => attempt.join(":") === chosen.join(":")) ? attempts : [...attempts, [...chosen]]);
        wrongTry("This sign does not match the picture plan yet. It will stay below so you can see your try. Show the plan again, then make a new sign.", `memory:${chosen.join("-")}`);
        setChosen([]);
        setActivityStep(0);
      };
      return <MiniGame title={scene.gameTitle} icon={scene.gameIcon} progress={curtainOpen ? "Look now — the curtain will close" : `${chosen.length}/4 pictures placed`}>
        <div className="e04-memory-game">
          <div className={`e04-memory-window ${curtainOpen ? "open" : "closed"}`}>
            {curtainOpen ? config.source.map((entry: { symbol: string; symbolLabel: string; picture: string }) => <span key={entry.symbol}><small>{symbolIcons[entry.symbol]} {entry.symbolLabel}</small>{pictureCard(entry.picture)}</span>) : <><strong>PICTURE PLAN HIDDEN</strong><span aria-hidden="true">🎭</span></>}
          </div>
          {!curtainOpen && <><div className="e04-memory-answer">{config.source.map((entry: { symbol: string; symbolLabel: string }, index: number) => <span key={entry.symbol}><small>{symbolIcons[entry.symbol]} {entry.symbolLabel}</small>{chosen[index] ? pictureCard(chosen[index], true) : <b>?</b>}</span>)}</div><div className="e04-card-tray">{config.cardTray.map((picture) => <button key={picture} disabled={chosen.includes(picture)} onClick={() => choose(picture)}>{pictureCard(picture)}</button>)}</div><div className="e04-memory-actions"><button className="primary" onClick={checkRebuild} disabled={chosen.length !== 4}>Check my sign</button><button className="secondary e04-look-again" onClick={() => { setActivityStep(0); setChosen([]); setWrong(""); sound("step"); }}>Show the plan again</button></div></>}
          {memoryAttempts.length > 0 && <section className="e04-memory-attempts" aria-label="Earlier signs kept visible"><strong>MY EARLIER SIGNS</strong>{memoryAttempts.map((attempt, attemptIndex) => <div key={`${attempt.join("-")}-${attemptIndex}`}><small>TRY {attemptIndex + 1}</small>{attempt.map((picture, index) => <span key={`${picture}-${index}`}><i>{symbolIcons[config.source[index].symbol]}</i>{pictureIcons[picture]}</span>)}</div>)}</section>}
        </div>
      </MiniGame>;
    }

    if (scene.activity === "difference") {
      const check = (index: number) => {
        if (!config.differenceIndexes.includes(index)) {
          wrongTry("This picture is in the same corner on both signs. It gets a tick. Look at another corner.", `difference:${index}`);
          return;
        }
        if (chosen.includes(String(index))) return;
        const next = [...chosen, String(index)];
        setChosen(next);
        if (next.length === 2) finishRound(); else sound("good");
      };
      return <MiniGame title={scene.gameTitle} icon={scene.gameIcon} progress={`${chosen.length}/2 changed corners found`}>
        <div className="e04-difference-game">
          <div className="e04-compare-row"><section><strong>PICTURE PLAN</strong>{config.source.map((entry: { symbol: string; symbolLabel: string; picture: string }) => <span key={entry.symbol}><small>{symbolIcons[entry.symbol]} {entry.symbolLabel}</small>{pictureCard(entry.picture, true)}</span>)}</section><section><strong>SOL&apos;S FIRST SIGN — KEEP IT HERE</strong>{config.firstTry.map((picture, index) => <button key={index} className={`${tried.includes(`difference:${index}`) ? "checked" : ""} ${chosen.includes(String(index)) ? "changed" : ""}`} onClick={() => check(index)}><small>{symbolIcons[config.source[index].symbol]} {config.source[index].symbolLabel}</small>{pictureCard(picture, true)}{tried.includes(`difference:${index}`) && <i>✓ SAME</i>}{chosen.includes(String(index)) && <i>↔ DIFFERENT</i>}</button>)}</section></div>
        </div>
      </MiniGame>;
    }

    if (scene.activity === "trace") {
      const checkStep = (index: number) => {
        const expectedIndex = chosen.length;
        if (index !== expectedIndex) {
          wrongTry(`You tapped Move ${index + 1}. We are checking Move ${expectedIndex + 1} now. Start there, then go one card at a time.`, `trace-order:${expectedIndex}:${index}`);
          return;
        }
        const step = config.trace[index];
        const expectedSymbol = config.source.find((entry: { picture: string }) => entry.picture === step.picture)?.symbol;
        const next = [...chosen, String(index)];
        setChosen(next);
        if (step.symbol !== expectedSymbol) finishRound(); else sound("good");
      };
      return <MiniGame title={scene.gameTitle} icon={scene.gameIcon} progress={`${chosen.length} moves checked`}>
        <div className="e04-trace-game e04-placement-trace">
          <div className="e04-reference-plan"><strong>PICTURE PLAN</strong>{config.source.map((entry: { symbol: string; symbolLabel: string; picture: string }) => <span key={entry.symbol}><small>{symbolIcons[entry.symbol]} {entry.symbolLabel}</small>{pictureCard(entry.picture, true)}</span>)}</div>
          <div className="e04-placement-cards">{config.trace.map((step: { picture: string; symbol: string }, index: number) => {
            const sourceSymbol = config.source.find((entry: { picture: string }) => entry.picture === step.picture)?.symbol;
            const checked = chosen.includes(String(index));
            const departure = checked && step.symbol !== sourceSymbol;
            const outOfOrder = tried.some((value) => value === `trace-order:${chosen.length}:${index}` || value.endsWith(`:${index}`));
            return <button key={`${step.picture}-${index}`} className={`${checked ? "checked" : ""} ${departure ? "departure" : ""} ${outOfOrder ? "kept-wrong" : ""}`} onClick={() => checkStep(index)}><small>MOVE {index + 1}</small><span>{pictureIcons[step.picture]} <b>{pictureLabels[step.picture]}</b></span><i aria-hidden="true">→</i><span>{symbolIcons[step.symbol]} <b>{step.symbol.toUpperCase()}</b></span>{checked && <em>{departure ? "FIRST MOVE THAT CHANGED" : "SAME AS PLAN"}</em>}</button>;
          })}</div>
          {tried.some((value) => value.startsWith("trace-order:")) && <p className="kept-attempts">Moves tapped too soon stay marked. Continue with Move {chosen.length + 1}.</p>}
        </div>
      </MiniGame>;
    }

    if (scene.activity === "measure") {
      const widthValue = Math.min(4, Math.max(1, meter || 1));
      const test = () => {
        if (widthValue !== config.measureWidth) {
          learningTry(widthValue < config.measureWidth ? "The ribbon does not reach the right hook yet. Tap Longer and try again." : "The ribbon goes past the right hook. Tap Shorter and try again.", `measure:${widthValue}`);
          return;
        }
        finishRound();
      };
      return <MiniGame title={scene.gameTitle} icon={scene.gameIcon} progress="Make the ribbon touch both hooks">
        <div className="e04-measure-game">
          <div className="e04-boundary-records"><span className="done">PICTURES ✓</span><span className="active">WIDTH ?</span><span>HEIGHT NOT CHECKED</span></div>
          <div className={`e04-gate-frame width-${config.measureWidth}`} aria-label="Gate frame with a clearly marked left hook and right hook"><i>LEFT HOOK</i><div className={`e04-ribbon width-${widthValue}`}><span>←</span><b>WIDTH RIBBON</b><span>→</span></div><i>RIGHT HOOK</i></div>
          <label><strong>Make the width ribbon touch both hooks</strong><input type="range" min="1" max="4" step="1" value={widthValue} onChange={(event) => { setMeter(Number(event.currentTarget.value)); sound("step"); }} /></label>
          <div className="e04-step-controls" aria-label="Change the width ribbon"><button type="button" disabled={widthValue <= 1} onClick={() => { setMeter(widthValue - 1); sound("step"); }}>← Shorter</button><button type="button" disabled={widthValue >= 4} onClick={() => { setMeter(widthValue + 1); sound("step"); }}>Longer →</button></div>
          <button className="primary" onClick={test}>Test this width</button>
          {tried.some((value) => value.startsWith("measure:")) && <div className="e04-measure-tries"><strong>YOUR EARLIER RIBBONS</strong>{tried.filter((value) => value.startsWith("measure:")).map((value) => { const triedWidth = Number(value.split(":")[1]); return <span key={value}>{triedWidth < config.measureWidth ? "Stopped short" : "Went past"} ×</span>; })}</div>}
        </div>
      </MiniGame>;
    }

    if (scene.activity === "friend") {
      const lensIndex = Math.min(3, Math.max(0, meter));
      const placements = entriesToPlacements(chosen);
      const nextSymbol = config.friendOrder[chosen.length];
      const record = () => {
        if (chosen.length >= 4) return;
        const corner = config.source[lensIndex];
        if (corner.symbol !== nextSymbol) {
          wrongTry(`Ivo's card says ${nextSymbol.toUpperCase()} next. You are looking at ${corner.symbolLabel}. This try will stay marked. Move the lens to ${nextSymbol.toUpperCase()}.`, `friend:${chosen.length}:${corner.symbol}`);
          return;
        }
        const next = [...chosen, `${lensIndex}:${corner.picture}`];
        setChosen(next);
        sound("good");
      };
      const uncover = () => { setSelected("uncovered"); sound("step"); };
      return <MiniGame title={scene.gameTitle} icon={scene.gameIcon} progress={`${chosen.length}/4 pictures on Ivo's sign`}>
        <div className="e04-friend-game">
          <div className="e04-reference-plan e04-source-lens"><strong>PICTURE PLAN</strong>{config.source.map((entry: { symbol: string; symbolLabel: string; picture: string }, index: number) => <span key={entry.symbol} className={lensIndex === index ? "under-lens" : ""}><small>{symbolIcons[entry.symbol]} {entry.symbolLabel}</small>{pictureCard(entry.picture, true)}{lensIndex === index && <i aria-hidden="true">🔍</i>}</span>)}</div>
          <div className="e04-fresh-check-row"><section><strong>IVO&apos;S SIGN</strong><div className="e04-sign-board">{config.source.map((entry: { symbol: string; symbolLabel: string }, index: number) => <span key={entry.symbol}><small>{symbolIcons[entry.symbol]} {entry.symbolLabel}</small>{placements[index] ? pictureCard(placements[index], true) : <b>?</b>}</span>)}</div></section><section className={selected === "uncovered" ? "uncovered" : "covered"}><strong>OUR SIGN</strong>{selected === "uncovered" ? <div className="e04-sign-board">{config.source.map((entry: { symbol: string; symbolLabel: string; picture: string }) => <span key={entry.symbol}><small>{symbolIcons[entry.symbol]} {entry.symbolLabel}</small>{pictureCard(entry.picture, true)}</span>)}</div> : <div className="e04-team-screen">OUR SIGN IS HIDDEN<br />NO PEEKING</div>}</section></div>
          {chosen.length < 4 ? <><p className="e04-next-corner">IVO&apos;S NEXT CORNER: find <strong>{nextSymbol.toUpperCase()}</strong></p><label className="e04-lens-control"><strong>Move Ivo&apos;s lens</strong><input type="range" min="0" max="3" step="1" value={lensIndex} onChange={(event) => setMeter(Number(event.currentTarget.value))} /></label><div className="e04-step-controls e04-corner-controls" aria-label="Choose Ivo's picture-plan corner">{config.source.map((entry: { symbol: string; symbolLabel: string }, index: number) => <button key={entry.symbol} type="button" className={lensIndex === index ? "active" : ""} aria-pressed={lensIndex === index} onClick={() => { setMeter(index); sound("step"); }}>{symbolIcons[entry.symbol]} {entry.symbolLabel}</button>)}</div><button className="secondary" onClick={record}>Put this picture on Ivo&apos;s sign</button></> : selected !== "uncovered" ? <button className="primary" onClick={uncover}>Lift the cloth</button> : <button className="primary" onClick={finishRound}>Do the two signs match?</button>}
        </div>
      </MiniGame>;
    }

    if (scene.activity === "height") {
      const heightValue = Math.min(4, Math.max(1, meter || 1));
      const chooseQuestion = (choice: "height" | "guess" | "vote") => {
        if (choice !== "height") {
          learningTry(choice === "guess" ? "A guess is an answer without checking. It cannot tell us how tall the sign is. Choose the height tool." : "A vote tells us what people choose. It does not tell us how tall the sign is. Choose the height tool.", `height-choice:${choice}`);
          return;
        }
        setSelected("height");
        setMeter(1);
        sound("good");
      };
      const testHeight = () => {
        if (heightValue !== config.heightTarget) {
          learningTry(heightValue < config.heightTarget ? "The blue tool does not touch the top edge yet. Tap Taller and try again." : "The blue tool goes past the top edge. Tap Shorter and try again.", `height:${heightValue}`);
          return;
        }
        finishRound();
      };
      return <MiniGame title={scene.gameTitle} icon={scene.gameIcon} progress={selected === "height" ? "Make the tool touch bottom and top" : "How can we check bottom to top?"}>
        <div className="e04-height-game">
          <div className="e04-disagreement-people"><section><strong>MIA ASKS</strong><p>“The width fits. Are we finished?”</p></section><section><strong>IVO NOTICES</strong><p>“We still need to check bottom to top.”</p></section></div>
          {selected !== "height" ? <div className="e04-height-choices"><strong>WHAT SHOULD THE TEAM DO?</strong><button onClick={() => chooseQuestion("height")}>↕ USE A HEIGHT TOOL</button><button className={tried.includes("height-choice:guess") ? "kept-wrong" : ""} onClick={() => chooseQuestion("guess")}>? GUESS</button><button className={tried.includes("height-choice:vote") ? "kept-wrong" : ""} onClick={() => chooseQuestion("vote")}>✋ VOTE</button></div> : <><div className="e04-height-boundaries"><i>TOP EDGE</i><div className={`e04-height-tool height-${heightValue}`}><span>↑</span><b>HEIGHT TOOL</b><span>↓</span></div><i>BOTTOM EDGE</i></div><label><strong>Grow the tool from the bottom edge to the top edge</strong><input type="range" min="1" max="4" step="1" value={heightValue} onChange={(event) => { setMeter(Number(event.currentTarget.value)); sound("step"); }} /></label><div className="e04-step-controls" aria-label="Change the height tool"><button type="button" disabled={heightValue <= 1} onClick={() => { setMeter(heightValue - 1); sound("step"); }}>↓ Shorter</button><button type="button" disabled={heightValue >= 4} onClick={() => { setMeter(heightValue + 1); sound("step"); }}>Taller ↑</button></div><button className="primary" onClick={testHeight}>Does it touch both edges?</button></>}
          {tried.some((value) => /^height:\d/.test(value)) && <div className="e04-measure-tries"><strong>HEIGHTS YOU TRIED</strong>{tried.filter((value) => /^height:\d/.test(value)).map((value) => <span key={value}>Stopped short ×</span>)}</div>}
        </div>
      </MiniGame>;
    }

    if (scene.activity === "checkpoint") {
      const recordDetails: Record<string, { title: string; detail: string; icon: string }> = {
        pictures: { title: "PICTURE CHECK", detail: "All four pictures match the plan", icon: "🖼️" },
        width: { title: "WIDTH CHECK", detail: "The ribbon touched both side hooks", icon: "↔️" },
        height: { title: "HEIGHT CHECK", detail: "The tool touched the bottom and top", icon: "↕️" },
        friend: { title: "IVO'S CHECK", detail: "Ivo's sign matched ours", icon: "🔍" },
      };
      const questionLabels: Record<string, string> = { pictures: "Do the pictures match?", width: "Is the width right?", height: "Is the height right?", friend: "Did Ivo's sign match?" };
      const matchedQuestions = new Set(chosen.map((entry) => entry.split(":")[0]));
      const matchedRecords = new Set(chosen.map((entry) => entry.split(":")[1]));
      const match = (question: string) => {
        if (!selected) { setWrong("Choose one answer card first. Then choose the gate question it answers."); return; }
        if (selected !== question) {
          wrongTry(`This is the ${recordDetails[selected].title} card, but you tapped ${questionLabels[question]} This card answers a different question. Leave this try here and try again.`, `checkpoint:${question}:${selected}`);
          return;
        }
        const next = [...chosen, `${question}:${selected}`];
        setChosen(next);
        setSelected("");
        if (next.length === 4) finishRound(); else sound("good");
      };
      return <MiniGame title={scene.gameTitle} icon={scene.gameIcon} progress={`${chosen.length}/4 answer cards placed`}>
        <div className="e04-checkpoint-game">
          <section className="e04-record-tray"><strong>FOUR ANSWER CARDS</strong>{config.checkpointRecords.map((record: string) => <button key={record} disabled={matchedRecords.has(record)} className={selected === record ? "selected" : ""} onClick={() => { setSelected(record); sound("tap"); }}><span>{recordDetails[record].icon}</span><b>{recordDetails[record].title}</b><small>{recordDetails[record].detail}</small></button>)}</section>
          <section className="e04-gate-questions"><strong>FOUR GATE QUESTIONS</strong>{config.checkpointQuestions.map((question: string) => <button key={question} disabled={matchedQuestions.has(question)} className={matchedQuestions.has(question) ? "matched" : ""} onClick={() => match(question)}><b>{questionLabels[question]}</b>{matchedQuestions.has(question) && <span>✓ {recordDetails[question].title}</span>}</button>)}</section>
          {tried.some((value) => value.startsWith("checkpoint:")) && <section className="e04-checking-rail"><strong>TRIES TO LOOK AT AGAIN</strong>{tried.filter((value) => value.startsWith("checkpoint:")).map((value) => { const [, question, record] = value.split(":"); return <span key={value}>{recordDetails[record].title} → {questionLabels[question]} ×</span>; })}</section>}
        </div>
      </MiniGame>;
    }

    return null;
  }

  if (!storageReady) return <main className="restore-screen"><p>Returning to your garden adventure…</p></main>;

  if (introOpen) return <LevelPrelude
    levelClass="level-four-prelude"
    eyebrow="LEVEL FOUR · THE GARDEN GATE"
    title="The Garden Gate Check"
    subtitle="A blank Welcome Sign is waiting by a closed garden gate. Help the friends copy its pictures, find a mistake and make sure it fits."
    background={LEVEL_FOUR_ASSETS.search}
    lines={preludeLines}
    characters={[
      { id: "mia", name: "Mia", image: image("mira") },
      { id: "tavi", name: "Tavi", image: image("tavi") },
      { id: "sol", name: "Sol", image: image("sol") },
      { id: "ivo", name: "Ivo", image: image("ivo") },
    ]}
    discoveries={[<>🔎 Find what changed</>, <>📏 Check side to side and bottom to top</>, <>🧑‍🤝‍🧑 Let Ivo check without peeking</>]}
    initialStep={preludeStep}
    onStepChange={setPreludeStep}
    onSpeak={(entry) => { startMusic(); playLine(entry); }}
    onBegin={() => { stopNarration(audioRef, narrationGenerationRef, duckMusic); setIntroSeen(true); setPreludeStep(3); lastLineRef.current = ""; }}
    onExit={exitLevel}
    musicOn={musicOn}
    onToggleMusic={toggleMusic}
  />;

  if (finished) return <main className="ending-screen e04-ending">
    <div className="ending-art" style={{ backgroundImage: `url('${LEVEL_FOUR_ASSETS.checkpoint}')` }} />
    <button className="ending-home" onClick={exitLevel} aria-label="Choose a level">⌂ Levels</button>
    <section>
      <p className="eyebrow">LEVEL FOUR COMPLETE</p>
      <div className="e03-progress e04-progress" aria-label="9 of 9 story steps complete">{scenes.map((_, index) => <span className="done" key={index}>●</span>)}</div>
      <h1>The garden gate opens.</h1>
      <p>Mia, Sol, Tavi and Ivo finished the Welcome Sign. Its pictures matched the plan. The width ribbon touched both side hooks. The height tool touched the bottom and top edges. Ivo&apos;s sign matched too. All four checks were complete, so the gate opened for the morning visitors.</p>
      <blockquote>One check answers one question. Four questions needed four checks.</blockquote>
      <div className="ending-lesson"><span aria-hidden="true">📖</span><div><strong>NARRATOR TO YOU</strong><p>{endingLesson.text}</p></div><button onClick={() => playLine(endingLesson)}>Hear the lesson again</button></div>
      <div className="ending-controls">
        {onNext ? <button className="primary" onClick={onNext}>Next level</button> : <button className="primary" disabled>Next level · coming soon</button>}
        <button className="secondary" onClick={restart}>Play Level 4 again</button>
        <button className="secondary" onClick={exitLevel}>Choose a level</button>
        <button className="secondary" onClick={toggleMusic}>{musicOn ? "Turn music off" : "Turn music on"}</button>
      </div>
    </section>
  </main>;

  return <main className="game-shell level-four-shell">
    <header className="game-hud e04-hud">
      <div><span className="eyebrow">THE GARDEN GATE CHECK</span><strong>{scene.title}</strong></div>
      <div className="e03-progress e04-progress" aria-label={`${sceneIndex + (complete ? 1 : 0)} of 9 story steps complete`}>{scenes.map((_, index) => <span key={index} className={index < sceneIndex || (index === sceneIndex && complete) ? "done" : index === sceneIndex ? "now" : ""}>●</span>)}</div>
      <nav><button onClick={exitLevel} aria-label="Choose a level">⌂ <span>Levels</span></button><button onClick={() => playLine()} aria-label="Replay narration">↻ <span>Hear again</span></button><button onClick={toggleNarration} aria-pressed={muted}>{muted ? "🔇" : "🔊"} <span>{muted ? "Narration off" : "Narration on"}</span></button><button onClick={toggleMusic} aria-pressed={musicOn}>{musicOn ? "♫" : "♩"} <span>{musicOn ? "Music on" : "Music off"}</span></button><button onClick={restart} aria-label="Restart Level Four">↺ <span>Start over</span></button><button onClick={() => setCodesOpen(true)}>⌨ <span>Book code</span></button></nav>
    </header>
    <section key={scene.id} className={`play-stage e04-stage scene-e04-${scene.id}`} style={{ backgroundImage: `url('${scene.background}')` }} aria-label={`${scene.title}, an animated garden checking story scene`}>
      <div className="stage-light" />
      {beat === 0 && <div className="journey-banner"><span aria-hidden="true">→</span><strong>{scene.journey}</strong></div>}
      <div className="walking-cast" aria-hidden="true">{scene.cast.map((name, index) => <CharacterSprite key={name} name={name} index={index} speaking={speaking === name} />)}</div>
      {dialogueDone && !complete && <div className="activity-layer">{scene.activity === "measure" || scene.activity === "height" ? <div className="e04-practice-badge">TRY AS MANY LENGTHS AS YOU NEED</div> : <TryLights mistakes={mistakes} />}{!roundLost && <fieldset className="resolution-lock" disabled={resolving} aria-busy={resolving}>{activity()}</fieldset>}{wrong && <p className="e03-feedback e04-feedback" role="status">{wrong}</p>}{roundLost && <section className="round-lost" role="alert"><span aria-hidden="true">◆ ◆ ◆</span><h2>Try lights are dark</h2><p>All three try lights are dark. Your tries are still here, and the story can continue. Tap Try a new puzzle to get three new lights.</p><button onClick={retryRound}>Try a new puzzle</button></section>}</div>}
      <aside className={`speech-panel ${dialogueDone && !complete ? "prompting" : ""} ${complete ? "completed" : ""}`} aria-live="polite">
        {!dialogueDone || complete ? <><div className="speaker-portrait"><Portrait speaker={currentLine.speaker} /></div><span className="speaker">{complete ? "NARRATOR · WHAT THIS GAME TAUGHT" : currentLine.speaker}</span><p>{currentLine.text}</p>{complete ? <div className="completion-controls"><button className="replay-control" onClick={replay}><span aria-hidden="true">↻</span> Play again</button><button className="next-control" onClick={nextScene}>{sceneIndex === scenes.length - 1 ? "Open the garden" : "Go to the next game"} <span aria-hidden="true">→</span></button></div> : <button className="next-control" onClick={nextBeat}>Next <span aria-hidden="true">→</span></button>}</> : <><div className="speaker-portrait prompt-portrait" aria-hidden="true">☝️</div><span className="speaker">YOUR TURN</span><p>{scene.prompt}</p><span className="action-nudge" aria-hidden="true">↑ Try it in the scene</span></>}
      </aside>
    </section>
    {codesOpen && <div className="modal-backdrop" role="presentation" onMouseDown={() => setCodesOpen(false)}><section className="code-modal" role="dialog" aria-modal="true" aria-labelledby="e04-code-title" onMouseDown={(event) => event.stopPropagation()}><button className="close-modal" onClick={() => setCodesOpen(false)} aria-label="Close">×</button><p className="eyebrow">OPTIONAL BOOK SECRET</p><h2 id="e04-code-title">Mia&apos;s code pocket</h2><p>Codes unlock small surprises. They never give an answer or skip a checking lesson.</p><form onSubmit={submitCode}><label htmlFor="e04-book-code">Code from Book Four</label><div><input id="e04-book-code" value={code} onChange={(event) => setCode(event.target.value)} autoComplete="off" /><button>Open</button></div></form><p className="code-result" aria-live="polite">{codeMessage}</p></section></div>}
  </main>;
}
