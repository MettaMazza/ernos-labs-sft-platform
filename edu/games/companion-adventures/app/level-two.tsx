"use client";
/* eslint-disable react-hooks/refs -- refs are read only inside event handlers and effects */

import { CSSProperties, FormEvent, ReactNode, useEffect, useLayoutEffect, useRef, useState } from "react";
import LevelPrelude, { PreludeLine } from "./level-prelude";
import {
  claimLevelTwoCompletion,
  levelTwoRoundSetup,
  restoreLevelTwoProgress,
  snapshotLevelTwoProgress,
} from "./level-two-state.mjs";
import useLevelMusic from "./use-level-music";

type Character = "mira" | "tavi" | "sol" | "pax";
type Activity = "parcel" | "whole" | "bridge" | "parts" | "rebuild" | "match" | "gap" | "count" | "sum";
type Line = { speaker: string; text: string; audio: string };
const LEVEL_TWO_STORAGE_KEY = "sft-e02-moving-stage-v1";
type Scene = {
  id: string;
  title: string;
  gameTitle: string;
  gameIcon: string;
  background: string;
  cast: Character[];
  journey?: string;
  introduces?: Character;
  activity: Activity;
  lines: Line[];
  prompt: string;
  success: Line;
};

const scenes: Scene[] = [
  {
    id: "parcel", title: "A parcel for the team", gameTitle: "Parcel Dash", gameIcon: "📦", background: "e01-stage-06-library-v1.png", cast: ["mira", "tavi", "sol"], activity: "parcel",
    lines: [
      { speaker: "Narrator", text: "The parcel that slid down the library ramp after the first mystery was waiting beside the five-star map.", audio: "01-narrator-new-parcel" },
      { speaker: "Mia", text: "There is the parcel, beside the map. The label says Mia, Sol and Tavi. It is for us! Help me move it along the glowing floor path to the yellow reading mat.", audio: "02-mira-open-parcel" },
    ],
    prompt: "The parcel starts at the bottom left. Use the arrows to move it along glowing squares to the yellow reading mat.",
    success: { speaker: "Narrator", text: "You moved the parcel one square at a time and followed the glowing path to its end. Following a route in order helps us reach the right place. Inside the parcel is a Moon Lantern, with a card asking the team to take it to the balcony.", audio: "03-tavi-reads-card" },
  },
  {
    id: "whole", title: "The small door", gameTitle: "Lantern Detective", gameIcon: "🔎", background: "e02-stage-02-whole-room-v1.png", cast: ["mira", "tavi", "sol", "pax"], journey: "Mission: get the whole lantern through the small door, then take it to the balcony.", introduces: "pax", activity: "whole",
    lines: [
      { speaker: "Narrator", text: "The friends followed the card towards the balcony. A small door blocked the way. The lantern was too wide to fit through it.", audio: "04-narrator-workshop-door" },
      { speaker: "Pax", text: "Hello! I’m Pax. We can take the lantern apart, carry every part through, and build the whole lantern again. First, tap the covered lantern. Each tap will uncover one part.", audio: "05-pax-meets" },
    ],
    prompt: "Tap the covered lantern four times. Each tap uncovers one part. When the whole lantern is visible, say what you found.",
    success: { speaker: "Narrator", text: "You uncovered all four parts and saw one whole Moon Lantern. A whole has every part it needs, with no missing part and no extra object. Now the team knows exactly what they must rebuild.", audio: "06-mira-whole" },
  },
  {
    id: "parts", title: "Choose the four-part plan", gameTitle: "Fit-the-Circle Lab", gameIcon: "🧩", background: "e02-stage-04-part-gate-v1.png", cast: ["mira", "tavi", "sol", "pax"], journey: "Step 1 of 4: choose parts that fill the whole lantern.", activity: "parts",
    lines: [
      { speaker: "Narrator", text: "Pax laid four lantern-picture cards beside a round plan frame.", audio: "10-narrator-next-door" },
      { speaker: "Pax", text: "Each card shows one same-size part. Match every curved part to its place. The four parts must fill the lantern plan with no gap and no part on top of another.", audio: "11-pax-find-parts" },
    ],
    prompt: "Tap a lantern-part card, then tap its matching place in the round plan. Fit all four parts with no gap or overlap.",
    success: { speaker: "Narrator", text: "You matched each lantern part to its place. All four parts meet with no gap and no overlap. The finished plan has matching sides; that is called symmetrical. The four separate parts now show one whole lantern.", audio: "12-pax-parts-fit" },
  },
  {
    id: "match", title: "Check the sizes", gameTitle: "Twin-Part Test", gameIcon: "📏", background: "e02-stage-06-match-table-v1.png", cast: ["mira", "tavi", "sol", "pax"], journey: "Step 1 continued: check what ‘same size’ looks like before Pax uses the plan.", activity: "match",
    lines: [
      { speaker: "Narrator", text: "Pax put two pairs of lantern-part pictures on the balance table.", audio: "16-narrator-two-pairs" },
      { speaker: "Tavi", text: "One pair shows lantern parts that are the same size. Look at both pairs before you choose.", audio: "17-tavi-check-pairs" },
    ],
    prompt: "Choose or drag a lantern-part pair onto the balance track. Release it and find the pair that stays level.",
    success: { speaker: "Narrator", text: "Pair A stayed level because its two lantern parts are the same size. Pair B tipped because one part is bigger. This check teaches us to compare sizes instead of guessing from a quick look.", audio: "18-tavi-same-size" },
  },
  {
    id: "bridge", title: "Carry every part", gameTitle: "Doorway Delivery", gameIcon: "🚪", background: "e02-stage-03-count-bridge-v1.png", cast: ["mira", "tavi", "sol", "pax"], journey: "Step 2 of 4: Pax separates the lantern. Carry all four parts through the small door.", activity: "bridge",
    lines: [
      { speaker: "Narrator", text: "The lantern came apart into four pieces. All four waited beside the small door.", audio: "07-narrator-four-tiles" },
      { speaker: "Sol", text: "The door is narrow, so we must carry one lantern part at a time. Let’s move all four through, and not carry any part twice.", audio: "08-sol-twice" },
    ],
    prompt: "Tap one lantern part. Then tap the small door to carry it through. Move all four parts once.",
    success: { speaker: "Narrator", text: "You carried all four lantern parts through the small door. Each part moved once: none was missed and none was carried twice. Keeping track lets us know the complete set reached the other side.", audio: "09-tavi-four-once" },
  },
  {
    id: "count", title: "Count what is held", gameTitle: "Count-and-Collect", gameIcon: "👐", background: "e02-stage-07-checking-room-v1.png", cast: ["mira", "tavi", "sol", "pax"], journey: "Step 3 of 4: check that all four parts are safely on the other side.", activity: "count",
    lines: [
      { speaker: "Narrator", text: "Pax held two lantern parts. The other two waited on the tray, so all four were still easy to see.", audio: "22-narrator-pax-holds" },
      { speaker: "Pax", text: "How many parts am I holding? Then tell me how many parts make the whole lantern.", audio: "23-pax-two-counts" },
    ],
    prompt: "Tap each visible lantern part once to count all four. Then answer how many Pax is holding and how many make the whole lantern.",
    success: { speaker: "Narrator", text: "You counted two parts in Pax's hands and two on the tray. Two and two make four altogether. Counting both groups tells us that all four parts of the whole lantern are still here.", audio: "24-sol-two-four" },
  },
  {
    id: "gap", title: "Check the practice frame", gameTitle: "Gap Repair", gameIcon: "🛠️", background: "e02-stage-07-checking-room-v1.png", cast: ["mira", "tavi", "sol", "pax"], journey: "Practice check: find the missing picture, then return all four real parts to the carrying tray.", activity: "gap",
    lines: [
      { speaker: "Narrator", text: "Pax placed three lantern-part pictures in a flat practice frame. One picture space was empty. Another lantern picture and a triangle were nearby.", audio: "19-narrator-gap" },
      { speaker: "Mia", text: "Which picture completes the practice frame? Choose it, turn its top upright, and fit it into the empty space.", audio: "20-mira-gap-extra" },
    ],
    prompt: "Choose the missing lantern picture. It starts sideways, so turn it until its top points up, then fit it into the practice frame.",
    success: { speaker: "Narrator", text: "You turned the lantern picture upright and fitted it into the empty space. It filled the gap; the triangle and square were extra shapes, so they stayed outside. This teaches us that a whole needs the right parts in the right places.", audio: "21-pax-gap-extra" },
  },
  {
    id: "sum", title: "Count every part together", gameTitle: "Lantern Sum Builder", gameIcon: "➕", background: "e02-stage-08-balcony-v1.png", cast: ["mira", "tavi", "sol", "pax"], journey: "Step 4 of 4: count the four separate parts at the balcony before rebuilding the lantern.", activity: "sum",
    lines: [
      { speaker: "Narrator", text: "The friends reached the balcony before the first evening star. All four lantern parts were still separate, ready to be counted together.", audio: "25-narrator-balcony" },
      { speaker: "Tavi", text: "Put one lantern part in each space. A plus sign means join the separate counts. The equals sign tells us the total on the other side must count the same parts.", audio: "26-tavi-remembers" },
    ],
    prompt: "Put one lantern part in each space. Choose the total that makes the equation true. Keep all four parts separate for the final rebuild.",
    success: { speaker: "Narrator", text: "One part plus one part plus one part plus one part equals four parts. Plus joins the separate counts. Equals tells us that both sides count the same four parts. The equation checks that every lantern part reached the balcony.", audio: "27-mira-ending" },
  },
  {
    id: "rebuild", title: "Build and light the whole", gameTitle: "Lantern Builder", gameIcon: "🌕", background: "e02-stage-08-balcony-v1.png", cast: ["mira", "tavi", "sol", "pax"], journey: "The equation checked all four parts. Now fit those same parts together to rebuild the whole lantern.", activity: "rebuild",
    lines: [
      { speaker: "Narrator", text: "Mia placed the empty round frame on the balcony. The four parts they had counted waited beside it.", audio: "13-narrator-four-parts" },
      { speaker: "Mia", text: "Our equation checked that all four parts are here. Now fit each part into the frame. Use every part once, and leave none behind.", audio: "14-mira-rebuild" },
    ],
    prompt: "Choose or drag each curved lantern part into its matching place. Use all four counted parts to rebuild one whole lantern.",
    success: { speaker: "Narrator", text: "You used each counted part once and rebuilt the whole Moon Lantern. The same four parts became one whole again. A blue moon lit up, then a gold sun. The two lights began to take turns, pointing towards the next adventure.", audio: "15-sol-whole-again" },
  },
];

const levelTwoPrelude: PreludeLine[] = [
  { speaker: "Narrator", heading: "What you learned before", text: "In the Star Door mystery, you learned that empty, quiet, blank and hidden do not mean the same as nothing. Careful words helped the team say exactly what they found.", audio: "00a-narrator-recap" },
  { speaker: "Narrator", heading: "The parcel returns", text: "At the end of that mystery, a hidden ramp delivered a parcel beside the five-star map. The same parcel is waiting in the library now, with Mia, Sol and Tavi written on its label.", audio: "00b-narrator-parcel-link" },
  { speaker: "Narrator", heading: "What you will discover", text: "Inside is a Moon Lantern. When it cannot fit through a small door, you will study the whole, separate its four parts, carry and count them, then build the same whole again.", audio: "00c-narrator-discover" },
  { speaker: "Narrator", heading: "A new friend will help", text: "Pax knows how things fit together. You do not need to know every new word yet. Try each puzzle, and after every game I will explain what your actions helped you learn.", audio: "00d-narrator-pax-tease" },
];

const codes: Record<string, string> = {
  WHOLELIGHT: "The Moon Lantern makes a smiling moon on the wall.",
  ONCEEACH: "Sol practises four funny one-step dances.",
  ONCEAROUND: "The four bridge tiles play four different notes.",
  FAIRFIT: "Pax shows a tiny round puzzle for another day.",
  PARTPAIR: "The lantern parts glow in four colours.",
  GAPCHECK: "A little triangle waves from outside the lantern.",
  HELDWHOLE: "The next light whispers: blue, gold, blue, gold.",
};

const names: Record<Character, string> = { mira: "Mia", tavi: "Tavi", sol: "Sol", pax: "Pax" };
const endingLesson: Line = { speaker: "Narrator", text: "Here is what you learned. One whole can be made from several exact parts. You kept track of all four lantern parts, counted them with addition, and used the equals sign to show that both sides named the same total. Then you fitted those four parts together to rebuild one whole. This matters because counting and a clear parts plan help us check that nothing has been missed or used twice.", audio: "28-narrator-to-you" };
const image = (name: Character) => name === "mira" || name === "pax"
  ? "/art/characters/individual/" + name + "-v1.png"
  : "/art/characters/individual/" + name + ".png";

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

function LanternDrawing() {
  return <g aria-hidden="true">
    <circle cx="100" cy="100" r="96" fill="#ffcf4f" />
    <circle cx="100" cy="100" r="88" fill="#ef553f" stroke="#7f2434" strokeWidth="5" />
    <circle cx="100" cy="100" r="70" fill="#f47642" stroke="#ffd45c" strokeWidth="6" />
    <circle cx="100" cy="100" r="48" fill="#e9433f" stroke="#8e2939" strokeWidth="5" />
    <path d="M12 100H188M100 12V188" stroke="#ffd45c" strokeWidth="8" />
    <circle cx="100" cy="100" r="13" fill="#fff0a2" stroke="#7f2434" strokeWidth="5" />
  </g>;
}

function WholeLantern({ label = "one whole Moon Lantern" }: { label?: string }) {
  return <span className="whole-lantern-art" role="img" aria-label={label}><svg viewBox="0 0 200 200"><LanternDrawing /></svg></span>;
}

function LanternQuarter({ part, turned = 0 }: { part: 1 | 2 | 3 | 4; turned?: number }) {
  const viewBoxes = { 1: "0 0 100 100", 2: "100 0 100 100", 3: "0 100 100 100", 4: "100 100 100 100" } as const;
  const positions = { 1: "top left", 2: "top right", 3: "bottom left", 4: "bottom right" } as const;
  return <span className={`lantern-quarter lantern-quarter-${part}`} style={{ transform: `rotate(${turned * 90}deg)` }} role="img" aria-label={`lantern part ${part}, the ${positions[part]} quarter of four same-size parts`}><svg viewBox={viewBoxes[part]} preserveAspectRatio="none" shapeRendering="geometricPrecision"><LanternDrawing /></svg></span>;
}

function MiniGame({ title, icon, progress, children }: { title: string; icon: string; progress: string; children: ReactNode }) {
  return <section className="e02-mini-game" aria-label={`${title} mini-game`}>
    <header className="mini-game-header"><span aria-hidden="true">{icon}</span><div><small>MINI-GAME</small><strong>{title}</strong></div><b>{progress}</b></header>
    {children}
  </section>;
}

function TryLights({ mistakes }: { mistakes: number }) {
  return <div className="try-lights" aria-label={`${3 - mistakes} of 3 try lights left`}><b>TRY LIGHTS</b>{[0,1,2].map((value) => <span key={value} className={value < 3 - mistakes ? "on" : "off"}>◆</span>)}</div>;
}

export default function LevelTwo({ onExit, onNext }: { onExit: () => void; onNext: () => void }) {
  const [sceneIndex, setSceneIndex] = useState(0);
  const [introOpen, setIntroOpen] = useState(true);
  const [preludeStep, setPreludeStep] = useState(-1);
  const [beat, setBeat] = useState(0);
  const [complete, setComplete] = useState(false);
  const [finished, setFinished] = useState(false);
  const [muted, setMuted] = useState(false);
  const [codesOpen, setCodesOpen] = useState(false);
  const [code, setCode] = useState("");
  const [codeMessage, setCodeMessage] = useState("");
  const [activityStep, setActivityStep] = useState(0);
  const [chosen, setChosen] = useState<number[]>([]);
  const [wrong, setWrong] = useState("");
  const [mistakes, setMistakes] = useState(0);
  const [round, setRound] = useState(0);
  const [storageReady, setStorageReady] = useState(false);
  const audioRef = useRef<HTMLAudioElement | null>(null);
  const soundRef = useRef<AudioContext | null>(null);
  const lastLineRef = useRef("");
  const progressRef = useRef<Record<string, unknown>>({});
  const feedbackTimerRef = useRef<number | null>(null);
  const completionLockRef = useRef(false);
  const { enabled: musicOn, start: startMusic, stop: stopMusic, toggle: toggleMusic, duck: duckMusic } = useLevelMusic("level-two");

  useEffect(() => {
    try { localStorage.setItem("sft-active-level-v1", "e02"); } catch { /* optional */ }
  }, []);
  const scene = scenes[sceneIndex];
  const roundLost = mistakes >= 3;
  const dialogueDone = beat >= scene.lines.length;
  const line = complete ? scene.success : scene.lines[Math.min(beat, scene.lines.length - 1)];
  const speaking = (!dialogueDone || complete) ? (line?.speaker.toLowerCase() === "mia" ? "mira" : line?.speaker.toLowerCase()) : "";

  useEffect(() => {
    const stopBackgroundAudio = () => {
      if (document.visibilityState !== "hidden") return;
      audioRef.current?.pause();
      audioRef.current = null;
      duckMusic(false);
    };
    const stopForPageHide = () => {
      audioRef.current?.pause();
      audioRef.current = null;
      duckMusic(false);
    };
    document.addEventListener("visibilitychange", stopBackgroundAudio);
    window.addEventListener("pagehide", stopForPageHide);
    return () => {
      document.removeEventListener("visibilitychange", stopBackgroundAudio);
      window.removeEventListener("pagehide", stopForPageHide);
    };
  }, [duckMusic]);

  useLayoutEffect(() => {
    completionLockRef.current = complete;
    progressRef.current = snapshotLevelTwoProgress({ introOpen, preludeStep, sceneIndex, beat, complete, finished, activityStep, chosen, mistakes, round });
  }, [introOpen, preludeStep, sceneIndex, beat, complete, finished, activityStep, chosen, mistakes, round]);

  useEffect(() => {
    const timeout = window.setTimeout(() => {
      try {
        const saved = restoreLevelTwoProgress(localStorage.getItem(LEVEL_TWO_STORAGE_KEY), scenes.length, levelTwoPrelude.length);
        setIntroOpen(saved.introOpen);
        setPreludeStep(saved.preludeStep);
        setSceneIndex(saved.sceneIndex);
        setBeat(saved.beat);
        setComplete(saved.complete);
        setFinished(saved.finished);
        setActivityStep(saved.activityStep);
        setChosen(saved.chosen);
        setWrong("");
        setMistakes(saved.mistakes);
        setRound(saved.round);
        completionLockRef.current = saved.complete;
      } catch { /* The level still works if device storage is unavailable. */ }
      setStorageReady(true);
    }, 0);
    return () => window.clearTimeout(timeout);
  }, []);

  useEffect(() => {
    if (!storageReady) return;
    const save = () => {
      try {
        const progress = progressRef.current;
        localStorage.setItem(LEVEL_TWO_STORAGE_KEY, JSON.stringify(progress));
        localStorage.setItem("sft-active-level-v1", "e02");
      } catch { /* optional */ }
    };
    save();
    const hidden = () => { if (document.visibilityState === "hidden") save(); };
    window.addEventListener("pagehide", save);
    document.addEventListener("visibilitychange", hidden);
    return () => { window.removeEventListener("pagehide", save); document.removeEventListener("visibilitychange", hidden); };
  }, [storageReady, introOpen, preludeStep, sceneIndex, beat, complete, finished, activityStep, chosen, mistakes, round]);

  useEffect(() => {
    if (!finished || muted) return;
    let lessonAudio: HTMLAudioElement | null = null;
    const timeout = window.setTimeout(() => {
      if (document.visibilityState !== "visible") return;
      if (audioRef.current && !audioRef.current.paused) return;
      audioRef.current?.pause();
      duckMusic(true);
      const audio = new Audio(`/audio/e02-v1.0.0/${endingLesson.audio}.mp3?v=e02-story-20260731f`);
      lessonAudio = audio;
      audioRef.current = audio;
      const restoreMusic = () => duckMusic(false);
      audio.addEventListener("ended", restoreMusic, { once: true });
      audio.addEventListener("error", restoreMusic, { once: true });
      audio.play().catch(restoreMusic);
    }, 120);
    return () => {
      window.clearTimeout(timeout);
      lessonAudio?.pause();
      duckMusic(false);
      if (audioRef.current === lessonAudio) audioRef.current = null;
    };
  }, [finished, muted, duckMusic]);

  useEffect(() => () => {
    audioRef.current?.pause();
    audioRef.current = null;
    if (feedbackTimerRef.current !== null) window.clearTimeout(feedbackTimerRef.current);
    stopMusic();
  }, [stopMusic]);

  function playLine(current = line) {
    if (!current || muted) return;
    audioRef.current?.pause();
    duckMusic(true);
    const audio = new Audio(`/audio/e02-v1.0.0/${current.audio}.mp3?v=e02-story-20260731f`);
    audioRef.current = audio;
    const restoreMusic = () => duckMusic(false);
    audio.addEventListener("ended", restoreMusic, { once: true });
    audio.addEventListener("error", restoreMusic, { once: true });
    audio.play().catch(restoreMusic);
  }

  function sound(kind: "tap" | "good" | "wrong" | "step") {
    if (muted) return;
    const context = soundRef.current ?? new AudioContext();
    soundRef.current = context;
    const now = context.currentTime;
    const tones = kind === "good" ? [440, 660, 880] : kind === "wrong" ? [180, 130] : kind === "step" ? [180, 240] : [340, 480];
    tones.forEach((frequency, index) => {
      const oscillator = context.createOscillator();
      const gain = context.createGain();
      oscillator.type = kind === "wrong" ? "square" : "sine";
      oscillator.frequency.value = frequency;
      gain.gain.setValueAtTime(.0001, now + index * .07);
      gain.gain.exponentialRampToValueAtTime(.07, now + index * .07 + .01);
      gain.gain.exponentialRampToValueAtTime(.0001, now + index * .07 + .2);
      oscillator.connect(gain).connect(context.destination);
      oscillator.start(now + index * .07); oscillator.stop(now + index * .07 + .22);
    });
  }

  useEffect(() => {
    if (introOpen || !line || (dialogueDone && !complete)) { audioRef.current?.pause(); duckMusic(false); return; }
    const key = `${sceneIndex}:${complete ? "success" : beat}`;
    const timeout = window.setTimeout(() => {
      if (document.visibilityState !== "visible") return;
      if (lastLineRef.current === key) return;
      lastLineRef.current = key;
      playLine(line);
    }, 25);
    return () => { window.clearTimeout(timeout); audioRef.current?.pause(); };
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [introOpen, sceneIndex, beat, complete, muted]);

  function clearFeedback() {
    if (feedbackTimerRef.current !== null) window.clearTimeout(feedbackTimerRef.current);
    feedbackTimerRef.current = null;
    setWrong("");
  }
  function showFeedback(message: string, duration = 2200) {
    if (feedbackTimerRef.current !== null) window.clearTimeout(feedbackTimerRef.current);
    setWrong(message);
    feedbackTimerRef.current = window.setTimeout(() => {
      feedbackTimerRef.current = null;
      setWrong("");
    }, duration);
  }
  function finish() {
    if (!claimLevelTwoCompletion(completionLockRef)) return;
    clearFeedback();
    sound("good");
    setMistakes(0);
    setComplete(true);
  }
  function wrongTry(message: string) {
    if (roundLost || completionLockRef.current) return;
    sound("wrong");
    setMistakes((value) => Math.min(3, value + 1));
    showFeedback(message);
  }
  function retryRound() { completionLockRef.current = false; clearFeedback(); sound("step"); setRound((value) => value + 1); setMistakes(0); setActivityStep(0); setChosen([]); }
  function nextBeat() { sound("tap"); if (beat < scene.lines.length) setBeat((value) => value + 1); }
  function nextScene() {
    sound("step");
    if (sceneIndex === scenes.length - 1) { audioRef.current?.pause(); audioRef.current = null; duckMusic(false); setFinished(true); return; }
    completionLockRef.current = false; clearFeedback(); setSceneIndex((value) => value + 1); setBeat(0); setComplete(false); setActivityStep(0); setChosen([]); setMistakes(0); lastLineRef.current = "";
  }
  function replay() { audioRef.current?.pause(); completionLockRef.current = false; clearFeedback(); setComplete(false); setActivityStep(0); setChosen([]); setMistakes(0); setRound((value) => value + 1); lastLineRef.current = ""; }
  function restart() {
    audioRef.current?.pause(); duckMusic(false); completionLockRef.current = false; clearFeedback(); setIntroOpen(true); setPreludeStep(-1); setSceneIndex(0); setBeat(0); setComplete(false); setFinished(false); setActivityStep(0); setChosen([]); setMistakes(0); setRound(0); lastLineRef.current = "";
    try {
      localStorage.removeItem(LEVEL_TWO_STORAGE_KEY);
      localStorage.setItem("sft-active-level-v1", "e02");
    } catch { /* optional */ }
  }
  function submitCode(event: FormEvent) {
    event.preventDefault(); const clean = code.toUpperCase().replace(/[^A-Z]/g, "");
    setCodeMessage(codes[clean] ?? "That code is hiding on another book page. Keep looking.");
    if (codes[clean]) setCode("");
  }
  function toggleNarration() { const next = !muted; setMuted(next); if (next) { audioRef.current?.pause(); audioRef.current = null; duckMusic(false); } }
  function exitLevel() { audioRef.current?.pause(); clearFeedback(); duckMusic(false); stopMusic(); onExit(); }
  function goToNextLevel() { audioRef.current?.pause(); duckMusic(false); stopMusic(); onNext(); }

  function activity() {
    if (complete) return null;
    const roundSetup = levelTwoRoundSetup(round);
    if (scene.activity === "parcel") {
      const open = roundSetup.parcelRoute;
      const current = activityStep || 10;
      const move = (delta: number) => {
        const column = current % 5; const next = current + delta;
        if ((delta === -1 && column === 0) || (delta === 1 && column === 4) || next < 0 || next > 14 || !open.includes(next)) { wrongTry("A book cart blocks that square. Keep the parcel on the glowing floor path."); return; }
        if (next === 10 || chosen.includes(next)) { wrongTry("That square is behind the parcel. Keep moving towards the yellow reading mat."); return; }
        const nextPath=[...chosen,next];clearFeedback();setChosen(nextPath);setActivityStep(next);sound("step");if(next===4)finish();
      };
      return <MiniGame title={scene.gameTitle} icon="📦" progress={`${chosen.length + 1}/${open.length} path squares`}><div className="parcel-path-game"><div className="parcel-path-grid">{Array.from({length:15},(_,cell)=><span key={cell} className={`${open.includes(cell)?"open":"cart"} ${chosen.includes(cell)?"used":""} ${cell===current?"parcel-here":""} ${cell===4?"reading-mat":""}`}>{cell===current?"📦":cell===4?"🟨":open.includes(cell)?"✨":"📚"}<b>{cell===10?"START":cell===4?"READING MAT":""}</b></span>)}</div><div className="parcel-arrows"><button onClick={()=>move(-5)}>↑</button><button onClick={()=>move(-1)}>←</button><button onClick={()=>move(1)}>→</button><button onClick={()=>move(5)}>↓</button></div></div></MiniGame>;
    }
    if (scene.activity === "whole") {
      const revealOrder = roundSetup.wholeRevealOrder;
      const inspect = () => { if(chosen.length<4){setChosen((parts)=>[...parts,revealOrder[parts.length]]);clearFeedback();sound("tap");} };
      return <MiniGame title={scene.gameTitle} icon="🔎" progress={`${chosen.length}/4 parts revealed`}><div className="lantern-inspector"><button className="whole-lantern-reveal" onClick={inspect} aria-label={`${chosen.length} of 4 lantern parts revealed. ${chosen.length<4?"Tap to uncover the next part.":"The whole lantern is visible."}`}><span className="lantern-reveal-window" aria-hidden="true"><WholeLantern />{[1,2,3,4].map((part)=><span key={part} className={`lantern-cover cover-${part} ${chosen.includes(part)?"revealed":""}`}>?</span>)}</span><b>{chosen.length<4?"Tap to uncover the next part":"The whole lantern is visible"}</b></button><div className="lantern-part-notebook"><strong>PARTS WE CAN SEE</strong>{[1,2,3,4].map((part)=><span key={part} className={chosen.includes(part)?"found":""}>{chosen.includes(part)?<LanternQuarter part={part as 1|2|3|4}/>:"?"}<b>PART {part}</b></span>)}</div><div className="whole-answer"><button disabled={chosen.length<4} onClick={finish}>Every part is here: the whole lantern</button><button disabled={chosen.length<4} onClick={()=>wrongTry("Look at the four notebook spaces. Is any lantern part missing?")}>A lantern part is missing</button><button disabled={chosen.length<4} onClick={()=>wrongTry("Only the four lantern parts are here. Is there an extra object?")}>An extra object is attached</button></div></div></MiniGame>;
    }
    if (scene.activity === "parts") {
      const cardOrder = roundSetup.partCardOrder;
      const selectedPart = activityStep;
      const placePart = (slot: number) => {
        if (!selectedPart) { showFeedback("Choose one lantern-part card first.", 1400); return; }
        if (selectedPart !== slot) { wrongTry("That curved edge does not match this place. Keep the card and try another place."); return; }
        const next = [...chosen,slot]; clearFeedback(); setChosen(next); setActivityStep(0); sound("step"); if(next.length===4)finish();
      };
      const positions = ["top left", "top right", "bottom left", "bottom right"];
      return <MiniGame title={scene.gameTitle} icon="🏮" progress={`${chosen.length}/4 plan parts placed`}><div className="plan-workbench"><div className="lantern-plan-frame" aria-label={`${chosen.length} of 4 lantern plan parts placed`}>{[1,2,3,4].map((slot)=><button key={slot} className={`plan-slot plan-slot-${slot} ${chosen.includes(slot)?"filled":""}`} onClick={()=>placePart(slot)} disabled={chosen.includes(slot)} aria-label={chosen.includes(slot)?`Lantern part ${slot} is placed in the ${positions[slot-1]}`:`Empty ${positions[slot-1]} place for part ${slot}`}>{chosen.includes(slot)?<LanternQuarter part={slot as 1|2|3|4}/>:<span>{slot}</span>}</button>)}</div><div className="plan-card-tray"><strong>FOUR SAME-SIZE LANTERN PARTS</strong>{cardOrder.map((part: number)=><button key={part} className={selectedPart===part?"selected":""} onClick={()=>{setActivityStep(part);sound("tap");}} disabled={chosen.includes(part)} aria-label={`Choose lantern part ${part}, ${positions[part-1]}`}><LanternQuarter part={part as 1|2|3|4}/><b>PART {part}<small>{positions[part-1]}</small></b></button>)}</div><p>{chosen.length===4?"The four parts meet in the middle. The finished lantern has matching sides.":selectedPart?`Part ${selectedPart} is ready. Match its curves and number to the same place.`:"Choose one lantern part. Its number and curves show where it fits."}</p></div></MiniGame>;
    }
    if (scene.activity === "match") {
      const pairOrder = roundSetup.match.pairOrder;
      const smallerSide = roundSetup.match.smallerSide;
      const selectedPair = activityStep;
      const pairPicture = (pair: number) => <><span className={pair===2&&smallerSide==="left"?"small-part":""}><LanternQuarter part={1}/></span><span className={pair===2&&smallerSide==="right"?"small-part":""}><LanternQuarter part={2}/></span></>;
      const test = () => {
        if (!selectedPair) {
          showFeedback("Choose or drag one pair onto the balance track.", 1600);
          return;
        }
        if (selectedPair === 1) finish();
        else wrongTry("The track tipped because one part reaches farther. Try the other pair.");
      };
      const trackState = selectedPair === 2 ? (smallerSide === "right" ? "tilted" : "tilted-opposite") : selectedPair === 1 ? "level" : "";
      return <MiniGame title={scene.gameTitle} icon="⚖️" progress={selectedPair ? "Ready to test" : "Choose a pair"}><div className="balance-puzzle"><div className={`balance-track ${trackState}`} onDragOver={(event) => event.preventDefault()} onDrop={(event) => { event.preventDefault(); clearFeedback(); setActivityStep(Number(event.dataTransfer.getData("text/plain"))); }}><div className="balance-lantern-load">{selectedPair?pairPicture(selectedPair):<WholeLantern label="whole lantern waiting for a pair test" />}</div><i/><b>{selectedPair ? `Lantern pair ${selectedPair === 1 ? "A" : "B"} on the track` : "Drop a lantern pair here"}</b></div><div className="balance-pairs">{pairOrder.map((pair: number) => <button key={pair} draggable onDragStart={(event) => event.dataTransfer.setData("text/plain",String(pair))} onClick={() => { clearFeedback(); setActivityStep(pair); }} className={selectedPair === pair ? "selected" : ""}><b>PAIR {pair === 1 ? "A" : "B"}</b><span className={`pair-lantern-parts ${pair === 1 ? "same" : "different"}`}>{pairPicture(pair)}</span></button>)}</div><button className="test-balance" onClick={test}>Release the lantern-part balance</button></div></MiniGame>;
    }
    if (scene.activity === "bridge") {
      const pieceOrder = roundSetup.bridgePieceOrder;
      const selectedPart = activityStep;
      const choosePart = (part: number) => {
        if (chosen.includes(part)) { wrongTry(`Lantern part ${part} is already through the door. Choose one still on this side.`); return; }
        clearFeedback(); setActivityStep(part); sound("tap");
      };
      const carryThrough = () => {
        if (!selectedPart) { showFeedback("Choose one lantern part beside the door first.", 1500); return; }
        const next=[...chosen,selectedPart];clearFeedback();setChosen(next);setActivityStep(0);sound("step");if(next.length===4)finish();
      };
      return <MiniGame title={scene.gameTitle} icon="🚪" progress={`${chosen.length}/4 lantern parts through`}><div className="doorway-delivery"><section className="delivery-side workshop-side"><strong>WORKSHOP SIDE</strong><div>{pieceOrder.map((part: number)=><button key={part} className={`${selectedPart===part?"selected":""} ${chosen.includes(part)?"carried":""}`} onClick={()=>choosePart(part)} aria-label={chosen.includes(part)?`Lantern part ${part} has already gone through`:`Choose lantern part ${part}`}><LanternQuarter part={part as 1|2|3|4}/><b>PART {part}</b></button>)}</div></section><button className={`delivery-door ${selectedPart?"ready":""}`} onClick={carryThrough}><span aria-hidden="true">🚪</span><b>{selectedPart ? `Carry part ${selectedPart} through` : "Choose a part"}</b></button><section className="delivery-side arrival-side"><strong>OTHER SIDE</strong><div>{[1,2,3,4].map((part)=><span key={part} className={chosen.includes(part)?"arrived":""}>{chosen.includes(part)?<LanternQuarter part={part as 1|2|3|4}/>:"?"}<b>PART {part}</b></span>)}</div></section></div></MiniGame>;
    }
    if (scene.activity === "count") {
      const heldOrder = roundSetup.count.held;
      const trayOrder = roundSetup.count.tray;
      const countPart = (part: number) => {
        if(chosen.includes(part)){wrongTry(`You already counted lantern part ${part}. Count a part without a number badge.`);return;}
        const next=[...chosen,part];clearFeedback();setChosen(next);sound("tap");if(next.length===4)setActivityStep(1);
      };
      const answerHeld = (answer:number) => answer===2 ? (clearFeedback(),setActivityStep(2),sound("good")) : wrongTry("Look only at Pax's hands. Tap and count the lantern parts he is holding.");
      const answerWhole = (answer:number) => answer===4 ? finish() : wrongTry("Count the two parts in Pax's hands and the two parts on the tray together.");
      return <MiniGame title={scene.gameTitle} icon="👐" progress={activityStep===0?`${chosen.length}/4 parts counted`:activityStep===1?"How many held?":"How many altogether?"}><div className="lantern-count-game"><div className="count-groups"><section><strong>PAX IS HOLDING</strong><div>{heldOrder.map((part: number)=><button key={part} onClick={()=>countPart(part)} className={chosen.includes(part)?"counted":""}><LanternQuarter part={part as 1|2}/>{chosen.includes(part)&&<i>{chosen.indexOf(part)+1}</i>}<b>LANTERN PART {part}</b></button>)}</div></section><section><strong>WAITING ON THE TRAY</strong><div>{trayOrder.map((part: number)=><button key={part} onClick={()=>countPart(part)} className={chosen.includes(part)?"counted":""}><LanternQuarter part={part as 3|4}/>{chosen.includes(part)&&<i>{chosen.indexOf(part)+1}</i>}<b>LANTERN PART {part}</b></button>)}</div></section></div>{activityStep===0?<p>Tap each lantern part once. The number badge shows your count.</p>:<div className="count-question"><strong>{activityStep===1?"How many lantern parts is Pax holding?":"How many lantern parts make the whole lantern?"}</strong><div>{[1,2,3,4].map(answer=><button key={answer} onClick={()=>activityStep===1?answerHeld(answer):answerWhole(answer)}>{answer}</button>)}</div></div>}</div></MiniGame>;
    }
    if (scene.activity === "gap") {
      const pieceOrder = roundSetup.gap.pieceOrder;
      const initialTurns = roundSetup.gap.initialTurns;
      const selected = activityStep; const orientation = chosen[0] ?? initialTurns; const turns = chosen[1] ?? 0;
      const fitPiece = () => {
        if (!selected) { showFeedback("Choose one loose piece first.", 1500); return; }
        if (selected !== 1 || orientation % 4 !== 1) { wrongTry("Choose the lantern picture, then turn it until its top points up like the pictures in the practice frame."); return; }
        finish();
      };
      return <MiniGame title={scene.gameTitle} icon="🛠️" progress={selected ? `${turns} turns` : "Choose picture"}><div className="gap-fit-puzzle"><div className="emoji-lantern-gap"><strong>PRACTICE FRAME</strong><div>{([1,2,3] as const).map(part=><LanternQuarter key={part} part={part}/>)}<span className="empty-quarter">?</span></div><b>One picture space is empty</b></div><div className="loose-shape-tray">{pieceOrder.map((piece: number)=><button key={piece} className={selected===piece?"selected":""} onClick={()=>{clearFeedback();setActivityStep(piece);setChosen([initialTurns,0]);sound("tap");}}>{piece===1?<LanternQuarter part={4} turned={selected===piece?orientation-1:initialTurns-1}/>:<span className="loose-shape">{piece===2?"🔺":"🟦"}</span>}<b>{piece===1?"Lantern picture":piece===2?"Triangle":"Blue square"}</b></button>)}</div><div className="gap-tools"><button onClick={()=>selected?(clearFeedback(),setChosen([(orientation+1)%4,turns+1]),sound("step")):showFeedback("Choose a picture before turning it.",1500)}>↻ Turn the chosen picture</button><button onClick={fitPiece}>Fit it into the practice frame</button></div></div></MiniGame>;
    }
    if (scene.activity === "rebuild") {
      const pieceOrder = roundSetup.rebuildPieceOrder;
      const place = (slot: number, piece = activityStep) => {
        if (!piece) { showFeedback("Choose or drag a lantern piece first.", 1600); return; }
        if (piece !== slot) { wrongTry("That curved edge does not meet this corner. Try a different slot or reset the board."); return; }
        if (chosen.includes(piece)) return;
        const next = [...chosen, piece]; clearFeedback(); setChosen(next); setActivityStep(0); sound("good");
        if (next.length === 4) finish();
      };
      return <MiniGame title={scene.gameTitle} icon={scene.gameIcon} progress={`${chosen.length}/4 fitted`}>
        <div className="lantern-jigsaw"><div className="lantern-frame" aria-label={`${chosen.length} of 4 lantern pieces fitted`}>{[1,2,3,4].map((slot) => <button key={slot} data-slot={slot} className={`jigsaw-slot slot-${slot} ${chosen.includes(slot) ? "filled" : ""}`} onClick={() => place(slot)} onDragOver={(event) => event.preventDefault()} onDrop={(event) => { event.preventDefault(); place(slot, Number(event.dataTransfer.getData("text/plain"))); }} aria-label={`Lantern slot ${slot}`}>{chosen.includes(slot) ? <LanternQuarter part={slot as 1|2|3|4}/> : <span>{slot}</span>}</button>)}</div><div className="jigsaw-tray"><strong>Choose or drag a lantern part</strong>{pieceOrder.map((piece: number) => <button key={piece} draggable={!chosen.includes(piece)} disabled={chosen.includes(piece)} className={`${activityStep === piece ? "selected" : ""} ${chosen.includes(piece) ? "placed" : ""}`} onClick={() => { sound("tap"); setActivityStep(piece); }} onDragStart={(event) => event.dataTransfer.setData("text/plain", String(piece))}><LanternQuarter part={piece as 1|2|3|4}/><b>Lantern part {piece}</b></button>)}<button className="jigsaw-reset" onClick={retryRound}>Shuffle and reset</button></div></div>
      </MiniGame>;
    }
    if (scene.activity === "sum") {
      const order = roundSetup.sumPartOrder;
      const selectedPart = activityStep > 0 && activityStep < 5 ? activityStep : 0;
      const placeNext = () => {
        if (!selectedPart || chosen.includes(selectedPart)) { showFeedback("Choose one lantern part from the tray first.", 1500); return; }
        const next = [...chosen, selectedPart]; clearFeedback(); setChosen(next); sound("step"); setActivityStep(next.length === 4 ? 5 : 0);
      };
      const chooseTotal = (answer: number) => {
        if (answer !== 4) { wrongTry("Count the four filled spaces once. The total must name every lantern part you can see."); return; }
        clearFeedback(); sound("good"); setActivityStep(6);
      };
      return <MiniGame title="Lantern Sum Builder" icon="➕" progress={activityStep < 5 ? `${chosen.length}/4 parts placed` : activityStep === 5 ? "Choose the total" : "Equation complete"}>
        <div className={`lantern-sum-game stage-${activityStep}`}>
          <div className="sum-equation" aria-label={chosen.length < 4 ? `${chosen.length} of 4 addition spaces filled` : activityStep < 6 ? "one part plus one part plus one part plus one part equals how many parts" : "one part plus one part plus one part plus one part equals four parts"}>
            {[0,1,2,3].map((slot) => <span className="sum-term" key={slot}>{chosen[slot] ? <><LanternQuarter part={chosen[slot] as 1|2|3|4}/><b>1 PART</b></> : <b>?</b>}</span>)}
            <i className="plus plus-one">+</i><i className="plus plus-two">+</i><i className="plus plus-three">+</i><i className="equals">=</i>
            <span className="sum-total">{activityStep >= 6 ? <><b>4</b><small>PARTS</small></> : <b>?</b>}</span>
          </div>
          {chosen.length < 4 && <><div className="sum-part-tray"><strong>CHOOSE A LANTERN PART</strong>{order.map((part: number) => <button key={part} disabled={chosen.includes(part)} className={selectedPart === part ? "selected" : ""} onClick={() => { clearFeedback(); setActivityStep(part); sound("tap"); }}><LanternQuarter part={part as 1|2|3|4}/><b>PART {part}</b></button>)}</div><button className="sum-action" onClick={placeNext}>Put the chosen part in the next space</button></>}
          {activityStep === 5 && <div className="sum-answer"><strong>How many lantern parts are there altogether?</strong><div>{[3,4,5].map((answer) => <button key={answer} onClick={() => chooseTotal(answer)}>{answer}</button>)}</div></div>}
          {activityStep === 6 && <div className="sum-meaning"><p><b>Plus</b> joins the separate counted parts.</p><p><b>Equals</b> says both sides count the same four parts.</p><button onClick={finish}>Take all 4 parts to the round frame</button></div>}
        </div>
      </MiniGame>;
    }
    return null;
  }

  if (!storageReady) return <main className="restore-screen"><p>Returning to your adventure…</p></main>;

  if (introOpen) return <LevelPrelude
    levelClass="level-two-prelude"
    eyebrow="LEVEL TWO · A NEW PARCEL"
    title="The Moon Lantern Workshop"
    subtitle="Remember the first mystery, follow the parcel into a new room, and discover how several exact parts can make one whole."
    background="/art/stages/e01-stage-06-library-v1.png"
    lines={levelTwoPrelude}
    characters={[
      { id: "mia", name: "Mia", image: image("mira") },
      { id: "tavi", name: "Tavi", image: image("tavi") },
      { id: "sol", name: "Sol", image: image("sol") },
    ]}
    discoveries={[<>🏮 Study one whole lantern</>, <>🧩 Keep track of four parts</>, <>➕ Learn what plus and equals mean</>]}
    initialStep={preludeStep}
    onStepChange={setPreludeStep}
    onSpeak={(current) => { startMusic(); playLine(current); }}
    onBegin={() => { audioRef.current?.pause(); duckMusic(false); setIntroOpen(false); lastLineRef.current = ""; }}
    onExit={exitLevel}
    musicOn={musicOn}
    onToggleMusic={toggleMusic}
  />;

  if (finished) return <main className="ending-screen e02-ending">
    <div className="ending-art" /><button className="ending-home" onClick={exitLevel} aria-label="Choose a level">⌂ Levels</button><section><p className="eyebrow">LEVEL TWO COMPLETE</p><div className="e02-progress" aria-label="9 of 9 story steps complete">{scenes.map((_, index) => <span className="done" key={index}>●</span>)}</div><h1>The Moon Lantern shines.</h1><p>Mia, Sol, Tavi and Pax solved the problem: the whole lantern was too wide for the small door.</p><blockquote>Four exact parts were counted, carried and fitted back into one whole.</blockquote><p className="rebuild-equation">1 + 1 + 1 + 1 = 4 PARTS → 1 WHOLE LANTERN</p><div className="ending-lesson"><span aria-hidden="true">📖</span><div><strong>NARRATOR TO YOU</strong><p>{endingLesson.text}</p></div><button onClick={() => playLine(endingLesson)}>Hear the lesson again</button></div><div className="ending-controls"><button className="primary" onClick={goToNextLevel}>Next level</button><button className="secondary" onClick={restart}>Play Level 2 again</button><button className="secondary" onClick={exitLevel}>Choose a level</button><button className="secondary" onClick={toggleMusic}>{musicOn ? "Turn music off" : "Turn music on"}</button></div></section>
  </main>;

  return <main className="game-shell level-two-shell">
    <header className="game-hud e02-hud">
      <div><span className="eyebrow">THE MOON LANTERN WORKSHOP</span><strong>{scene.title}</strong></div>
      <div className="e02-progress" aria-label={`${sceneIndex + (complete ? 1 : 0)} of 9 story steps complete`}>{scenes.map((_, index) => <span key={index} className={index < sceneIndex || (index === sceneIndex && complete) ? "done" : index === sceneIndex ? "now" : ""}>●</span>)}</div>
      <nav><button onClick={exitLevel} aria-label="Choose a level">⌂ <span>Levels</span></button><button onClick={() => playLine()} aria-label="Replay narration">↻ <span>Hear again</span></button><button onClick={toggleNarration} aria-pressed={muted}>{muted ? "🔇" : "🔊"} <span>{muted ? "Narration off" : "Narration on"}</span></button><button onClick={toggleMusic} aria-pressed={musicOn}>{musicOn ? "♫" : "♩"} <span>{musicOn ? "Music on" : "Music off"}</span></button><button onClick={() => setCodesOpen(true)}>⌨ <span>Book code</span></button></nav>
    </header>
    <section key={scene.id} className={`play-stage e02-stage scene-e02-${scene.id}`} style={{ backgroundImage: `url('/art/stages/${scene.background}')` }} aria-label={`${scene.title}, an animated Moon Lantern story scene`}>
      <div className="stage-light" />
      {beat === 0 && scene.journey && <div className="journey-banner"><span aria-hidden="true">→</span><strong>{scene.journey}</strong></div>}
      {scene.introduces && beat <= 1 && <div className="guest-banner">New friend for Level Two: <strong>{names[scene.introduces]}</strong></div>}
      <div className="walking-cast" aria-hidden="true">{scene.cast.map((name, index) => <CharacterSprite key={name} name={name} index={index} speaking={speaking === name} />)}</div>
      {scene.id === "parcel" && !dialogueDone && <div className="story-parcel" aria-label="parcel beside the map"><span aria-hidden="true">📦</span><b>PARCEL</b></div>}
      {dialogueDone && !complete && <div className="activity-layer"><TryLights mistakes={mistakes}/>{!roundLost && <button className="round-reset" onClick={retryRound} aria-label="Reset this puzzle round">↻ Reset round</button>}{!roundLost && activity()}{wrong && !roundLost && <p className="e02-feedback" role="status">{wrong}</p>}{roundLost && <section className="round-lost" role="alert"><span aria-hidden="true">◆ ◆ ◆</span><h2>Round over</h2><p>That round used all three try lights. The story is safe. Change your plan and try this puzzle again.</p><button onClick={retryRound}>Try again</button></section>}</div>}
      <aside className={`speech-panel ${dialogueDone && !complete ? "prompting" : ""} ${complete ? "completed" : ""}`} aria-live="polite">
        {!dialogueDone || complete ? <><div className="speaker-portrait"><Portrait speaker={line.speaker} /></div><span className="speaker">{complete ? "NARRATOR · WHAT YOU DISCOVERED" : line.speaker}</span><p>{line.text}</p>{complete ? <div className="completion-controls"><button className="replay-control" onClick={replay}><span aria-hidden="true">↻</span> Play again</button><button className="next-control" onClick={nextScene}>{sceneIndex === scenes.length - 1 ? "Light the lantern" : "Follow the plan"} <span aria-hidden="true">→</span></button></div> : <button className="next-control" onClick={nextBeat}>Next <span aria-hidden="true">→</span></button>}</> : <><div className="speaker-portrait prompt-portrait" aria-hidden="true">☝️</div><span className="speaker">YOUR TURN</span><p>{scene.prompt}</p><span className="action-nudge" aria-hidden="true">↑ Try it in the scene</span></>}
      </aside>
    </section>
    <button className="restart-corner" onClick={restart}>Start over</button>
    {codesOpen && <div className="modal-backdrop" role="presentation" onMouseDown={() => setCodesOpen(false)}><section className="code-modal" role="dialog" aria-modal="true" aria-labelledby="e02-code-title" onMouseDown={(event) => event.stopPropagation()}><button className="close-modal" onClick={() => setCodesOpen(false)} aria-label="Close">×</button><p className="eyebrow">OPTIONAL BOOK SECRET</p><h2 id="e02-code-title">Mia’s code pocket</h2><p>Codes unlock jokes and small previews. They never give an answer or skip a lesson.</p><form onSubmit={submitCode}><label htmlFor="e02-book-code">Code from Book Two</label><div><input id="e02-book-code" value={code} onChange={(event) => setCode(event.target.value)} autoComplete="off" /><button>Open</button></div></form><p className="code-result" aria-live="polite">{codeMessage}</p></section></div>}
  </main>;
}
