"use client";

import { CSSProperties, FormEvent, PointerEvent, useEffect, useLayoutEffect, useRef, useState } from "react";
import LevelTwo from "./level-two";

type Character = "mira" | "tavi" | "sol" | "nori";
type Activity = "note" | "box" | "bell" | "card" | "word" | "curtain" | "doors" | "recall";
type Line = { speaker: string; text: string; audio: string };
type Scene = {
  id: string;
  title: string;
  background: string;
  cast: Character[];
  journey?: string;
  introduces?: Character;
  activity: Activity;
  star?: number;
  lines: Line[];
  prompt: string;
  success: Line;
};

const scenes: Scene[] = [
  {
    id: "note", title: "A note comes through", background: "e01-stage-01-observatory-v1.png", cast: ["mira", "tavi", "sol"], activity: "note",
    lines: [
      { speaker: "Narrator", text: "Before breakfast, Mira, Sol and Tavi met in the star room. The Star Door was shut.", audio: "01-narrator-door-shut" },
      { speaker: "Narrator", text: "A note came through the letter box and landed next to Mira.", audio: "02-narrator-note-through-letter-box" },
      { speaker: "Narrator", text: "Mira picked up the note and opened it.", audio: "03-narrator-mira-picks-up-note" },
      { speaker: "Mira", text: "I found a note! It says: Find nothing. Five clues will show the way.", audio: "04-mira-finds-and-reads-note" },
      { speaker: "Sol", text: "Find nothing? That is a funny thing to look for. Let's follow the clues!", audio: "05-sol-strange-mystery" },
      { speaker: "Tavi", text: "Let's stay together and look carefully. First, can you spot Mira's note?", audio: "06-tavi-spot-note" },
    ],
    prompt: "Mira picked up the note that came through the letter box. Tap the note.",
    success: { speaker: "Mira", text: "You found the note. Look at the five star outlines at the top. None are gold yet. Each clue will turn one star gold. The first arrow points to the parcel!", audio: "07-mira-star-map" },
  },
  {
    id: "box", title: "The parcel clue", background: "e01-stage-01-observatory-v1.png", cast: ["mira", "tavi", "sol"], journey: "The first arrow points across the star room to the parcel.", activity: "box", star: 1,
    lines: [
      { speaker: "Narrator", text: "The friends followed the arrow across the room. It pointed to a parcel.", audio: "08-narrator-to-parcel" },
      { speaker: "Sol", text: "I opened the parcel. Look! My brown teddy is inside.", audio: "09-sol-sees-toy" },
      { speaker: "Tavi", text: "The first clue says to move the teddy. Tap the toy to lift it out. Then tap the box and look inside.", audio: "10-tavi-move-then-look" },
    ],
    prompt: "First move the teddy outside. Then tap the box and look inside.",
    success: { speaker: "Tavi", text: "You moved the teddy outside and looked inside. The box is empty. Empty means there is no toy inside this box. The box is still here.", audio: "11-tavi-empty-defined" },
  },
  {
    id: "bell", title: "Meet Nori in the bell room", background: "e01-stage-02-bell-gallery-v1.png", cast: ["mira", "tavi", "sol", "nori"], journey: "The box was still there, so the next arrow leads to the bell room.", introduces: "nori", activity: "bell", star: 2,
    lines: [
      { speaker: "Narrator", text: "They had found an empty box, not a thing called nothing. The first star turned gold. A blue door opened.", audio: "12-narrator-first-star-door" },
      { speaker: "Narrator", text: "The friends went through the door. They entered a room with three big bells.", audio: "13-narrator-enter-bells" },
      { speaker: "Nori", text: "Hello! I am Nori. I listen for tiny sounds. May I help you check the bell room?", audio: "14-nori-meets" },
      { speaker: "Mira", text: "Yes, please. The note tells us to find nothing. We found an empty box in the first room. Let's check the bells next.", audio: "15-mira-welcome" },
      { speaker: "Nori", text: "The wind stopped, and the big bell stopped moving. Hold the bell while we stay quiet and listen.", audio: "16-nori-listen" },
    ],
    prompt: "Press and hold the big bell while everyone listens.",
    success: { speaker: "Nori", text: "The bell did not ring while we listened. I heard my breath, and the bell stayed right there. We found a quiet bell, not a thing called nothing.", audio: "17-nori-no-ring" },
  },
  {
    id: "card", title: "The paper room", background: "e01-stage-03-paper-room-v1.png", cast: ["mira", "tavi", "sol", "nori"], journey: "The bell stayed in the room, so everyone follows the next arrow to the paper room.", activity: "card", star: 3,
    lines: [
      { speaker: "Narrator", text: "The bell did not ring, but it was still there. The second star turned gold. A door opened to the paper room.", audio: "18-narrator-to-paper" },
      { speaker: "Mira", text: "I found a white card on this table. Look, there are no marks on it yet.", audio: "19-mira-finds-card" },
      { speaker: "Tavi", text: "Touch the card. You can draw a mark, or choose Leave blank and do not draw.", audio: "20-tavi-draw-or-leave" },
    ],
    prompt: "Draw on the card—or leave it blank—then check.",
    success: { speaker: "Mira", text: "If you drew, there is a mark on the card. If you did not draw, the card is blank. Blank means there is no mark on the card. The card is still here both times.", audio: "21-mira-card-result" },
  },
  {
    id: "word", title: "Seven glowing letters", background: "e01-stage-03-paper-room-v1.png", cast: ["mira", "tavi", "sol", "nori"], journey: "The card stayed there, so seven wall tiles light up for the next clue.", activity: "word", star: 4,
    lines: [
      { speaker: "Narrator", text: "The card stayed there with or without a mark. The third star lit. Then seven wall tiles lit up, one after another.", audio: "22-narrator-to-word" },
      { speaker: "Sol", text: "Each glowing tile shows one letter. Read them from left to right with me!", audio: "23-sol-step" },
    ],
    prompt: "Tap the letters in order to spell NOTHING.",
    success: { speaker: "Tavi", text: "The seven letters spell the word nothing. We can see and read the word. The word does not show us a thing called nothing.", audio: "24-tavi-word" },
  },
  {
    id: "curtain", title: "Behind the curtain", background: "e01-stage-04-curtain-passage-v1.png", cast: ["mira", "tavi", "sol", "nori"], journey: "The word stayed visible, so a golden arrow leads everyone to the curtain passage.", activity: "curtain", star: 5,
    lines: [
      { speaker: "Narrator", text: "The written word stayed on the tiles, so the fourth star lit. A gold arrow appeared on the floor and led the friends to a red curtain.", audio: "25-narrator-to-curtain" },
      { speaker: "Sol", text: "My teddy rolled out of my bag! It crossed the floor and went behind the curtain. I saw where it went, but I cannot see it now!", audio: "26-sol-curtain" },
      { speaker: "Nori", text: "Slide the curtain slowly. Let's see what is behind it.", audio: "27-nori-curtain" },
    ],
    prompt: "Slowly slide the curtain open and watch for the toy.",
    success: { speaker: "Mira", text: "There is the teddy. Hidden means it was there, but the curtain stopped us from seeing it. The toy did not disappear.", audio: "28-mira-hidden" },
  },
  {
    id: "doors", title: "The final question", background: "e01-stage-05-star-door-v1.png", cast: ["mira", "tavi", "sol", "nori"], journey: "Five clues are complete, so five bright stars open the Star Door.", activity: "doors",
    lines: [
      { speaker: "Narrator", text: "Opening the curtain showed the teddy. The fifth star turned gold. Now all five stars were gold, and the Star Door opened.", audio: "29-narrator-to-doors" },
      { speaker: "Narrator", text: "Behind the Star Door were two small doors. Door A had a white card on its shelf. Door B had an empty shelf.", audio: "30-narrator-two-doors" },
      { speaker: "Mira", text: "My note still says, Find nothing. Tap both small doors. We must look at each one before we answer.", audio: "31-mira-question" },
    ],
    prompt: "Look behind both little doors before choosing.",
    success: { speaker: "Tavi", text: "Door A showed a card. Door B showed an empty shelf. Neither door showed a thing called nothing.", audio: "32-tavi-neither" },
  },
  {
    id: "recall", title: "The map remembers", background: "e01-stage-06-library-v1.png", cast: ["mira", "tavi", "sol", "nori"], journey: "The mystery is solved, so the friends carry their map to the library and remember the journey.", activity: "recall",
    lines: [
      { speaker: "Narrator", text: "The friends solved the note's puzzle. Mira folded the note. Everyone carried the five-star map into the library before going home.", audio: "33-narrator-library" },
      { speaker: "Tavi", text: "Before we put the map away, let's remember the first clue. Which thing became empty after you moved Sol's teddy outside?", audio: "34-tavi-remember" },
    ],
    prompt: "Tap the thing that became empty in the first clue.",
    success: { speaker: "Mira", text: "The box became empty after the teddy moved outside, but the box stayed in the room. We checked every clue. We found things, sounds and a written word, but no thing called nothing.", audio: "35-mira-ending" },
  },
];

const codes: Record<string, string> = {
  ROOMSTAR: "Mira finds a tiny practice star tucked under the route map.",
  BOXCLUE: "Sol's joke: an empty box can still be full of clues.",
  QUIETWINGS: "Nori teaches the trio a quiet listening wave.",
  BLANKEDGE: "Tavi finds a tiny sketchbook pocket.",
  CURTAINMAP: "The curtain stitches glow like a route map.",
  TWODOORS: "The next parcel whispers: one whole can have many parts.",
};

const characterNames: Record<Character, string> = { mira: "Mira", tavi: "Tavi", sol: "Sol", nori: "Nori" };
const characterImage = (name: Character) => name === "mira" ? "/art/characters/individual/mira-v1.png" : `/art/characters/individual/${name}.png`;

function CharacterSprite({ name, speaking, index }: { name: Character; speaking: boolean; index: number }) {
  return <div className={`actor actor-${name} ${speaking ? "speaking" : ""}`} style={{ "--actor-index": index } as CSSProperties}>
    <img src={characterImage(name)} alt="" draggable={false} /><span>{characterNames[name]}</span>
  </div>;
}

function SpeakerPortrait({ speaker }: { speaker: string }) {
  const id = speaker.toLowerCase() as Character;
  if (!(id in characterNames)) return <span className="narrator-portrait" aria-hidden="true">📖</span>;
  return <img className={`portrait-${id}`} src={characterImage(id)} alt="" aria-hidden="true" />;
}

function StarTrail({ count, focus = false, newest = null }: { count: number; focus?: boolean; newest?: number | null }) {
  return <div className={`star-trail-wrap ${focus ? "focus-stars" : ""}`}>
    <div className="star-trail" aria-label={`${count} of 5 clue stars lit`}>{[1, 2, 3, 4, 5].map((n) => <span key={n} className={`${n <= count ? "lit" : "hollow"} ${n === newest ? "new-star" : ""}`}>{n <= count ? "★" : "☆"}</span>)}</div>
    {focus && <small>Each clue lights one</small>}
  </div>;
}

export default function Home() {
  const [levelTwoActive, setLevelTwoActive] = useState(false);
  const [savedLevelTwoRooms, setSavedLevelTwoRooms] = useState(0);
  const [started, setStarted] = useState(false);
  const [sceneIndex, setSceneIndex] = useState(0);
  const [beat, setBeat] = useState(0);
  const [activityStep, setActivityStep] = useState(0);
  const [complete, setComplete] = useState(false);
  const [finished, setFinished] = useState(false);
  const [muted, setMuted] = useState(false);
  const [journalOpen, setJournalOpen] = useState(false);
  const [code, setCode] = useState("");
  const [codeMessage, setCodeMessage] = useState("");
  const [letters, setLetters] = useState(0);
  const [curtain, setCurtain] = useState(0);
  const [doors, setDoors] = useState<string[]>([]);
  const [drawn, setDrawn] = useState(false);
  const [cardOpen, setCardOpen] = useState(false);
  const [savedStars, setSavedStars] = useState(0);
  const [earnedStar, setEarnedStar] = useState<number | null>(null);
  const [storageReady, setStorageReady] = useState(false);
  const audioRef = useRef<HTMLAudioElement | null>(null);
  const canvasRef = useRef<HTMLCanvasElement | null>(null);
  const drawingRef = useRef(false);
  const curtainRevealRef = useRef(false);
  const soundContextRef = useRef<AudioContext | null>(null);
  const lastAutoLineRef = useRef("");
  const storageReadyRef = useRef(false);
  const progressRef = useRef<Record<string, unknown>>({});

  const scene = scenes[sceneIndex];
  const dialogueDone = beat >= scene.lines.length;
  const currentLine = complete ? scene.success : scene.lines[Math.min(beat, scene.lines.length - 1)];
  const speakingName = (!dialogueDone || complete) ? currentLine?.speaker.toLowerCase() : "";
  const starCount = Math.max(savedStars, scenes.slice(0, sceneIndex + (complete ? 1 : 0)).filter((item) => item.star).length);

  useLayoutEffect(() => {
    progressRef.current = {
      started, finished, sceneIndex, beat, activityStep, complete,
      stars: starCount, letters, curtain, doors, drawn, cardOpen,
    };
  }, [started, finished, sceneIndex, beat, activityStep, complete, starCount, letters, curtain, doors, drawn, cardOpen]);

  function playLine(line = currentLine) {
    if (!line || muted) return;
    audioRef.current?.pause();
    const audio = new Audio(`/audio/e01-v1.6.0/${line.audio}.mp3`);
    audioRef.current = audio;
    audio.play().catch(() => undefined);
  }

  function playEffect(kind: "step" | "tap" | "clunk" | "star" | "rustle" | "listen") {
    if (muted) return;
    const context = soundContextRef.current ?? new AudioContext();
    soundContextRef.current = context;
    const now = context.currentTime;
    const tones = kind === "star" ? [523, 659, 784, 1047] : kind === "step" ? [150, 115] : kind === "clunk" ? [105, 65] : kind === "rustle" ? [260, 310] : kind === "listen" ? [220, 330] : [380, 520];
    tones.forEach((frequency, index) => {
      const oscillator = context.createOscillator();
      const gain = context.createGain();
      oscillator.type = kind === "clunk" || kind === "step" ? "square" : kind === "star" ? "sine" : "triangle";
      oscillator.frequency.setValueAtTime(frequency, now + index * .075);
      gain.gain.setValueAtTime(.0001, now + index * .075);
      gain.gain.exponentialRampToValueAtTime(kind === "listen" ? .035 : .09, now + index * .075 + .012);
      gain.gain.exponentialRampToValueAtTime(.0001, now + index * .075 + (kind === "star" ? .42 : .16));
      oscillator.connect(gain).connect(context.destination);
      oscillator.start(now + index * .075);
      oscillator.stop(now + index * .075 + (kind === "star" ? .44 : .18));
    });
  }

  useEffect(() => {
    // Crossing from the final story beat into the activity must not replay that
    // final line. The activity panel is a new turn with its own visible prompt.
    if (!started || !currentLine || (dialogueDone && !complete)) {
      audioRef.current?.pause();
      return;
    }
    const lineKey = `${sceneIndex}:${complete ? "success" : beat}`;
    const timeout = window.setTimeout(() => {
      if (lastAutoLineRef.current === lineKey) return;
      lastAutoLineRef.current = lineKey;
      playLine(currentLine);
    }, 25);
    return () => { window.clearTimeout(timeout); audioRef.current?.pause(); };
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [started, sceneIndex, beat, complete]);

  useEffect(() => {
    const timeout = window.setTimeout(() => {
      try {
        const activeLevel = localStorage.getItem("sft-active-level-v1");
        const saved = JSON.parse(localStorage.getItem("sft-e01-moving-stage-v1") ?? "{}");
        const savedLevelTwo = JSON.parse(localStorage.getItem("sft-e02-moving-stage-v1") ?? "{}");
        if (typeof saved.sceneIndex === "number") setSceneIndex(Math.min(saved.sceneIndex, scenes.length - 1));
        if (typeof saved.beat === "number") setBeat(Math.max(0, saved.beat));
        if (typeof saved.activityStep === "number") setActivityStep(Math.max(0, saved.activityStep));
        if (typeof saved.complete === "boolean") setComplete(saved.complete);
        if (typeof saved.finished === "boolean") setFinished(saved.finished);
        if (activeLevel === "e02") setLevelTwoActive(true);
        else if (activeLevel === "select") setStarted(false);
        else if (typeof saved.started === "boolean") setStarted(saved.started);
        if (typeof saved.stars === "number") setSavedStars(Math.min(saved.stars, 5));
        if (typeof saved.letters === "number") setLetters(Math.max(0, Math.min(saved.letters, 7)));
        if (typeof saved.curtain === "number") setCurtain(Math.max(0, Math.min(saved.curtain, 100)));
        if (Array.isArray(saved.doors)) setDoors(saved.doors.filter((door: unknown) => door === "A" || door === "B"));
        if (typeof saved.drawn === "boolean") setDrawn(saved.drawn);
        if (typeof saved.cardOpen === "boolean") setCardOpen(saved.cardOpen);
        if (savedLevelTwo.finished === true) setSavedLevelTwoRooms(9);
        else if (typeof savedLevelTwo.sceneIndex === "number") setSavedLevelTwoRooms(Math.max(0, Math.min(9, savedLevelTwo.sceneIndex + (savedLevelTwo.complete ? 1 : 0))));
      } catch { /* The story also works without local saving. */ }
      storageReadyRef.current = true;
      setStorageReady(true);
    }, 0);
    return () => window.clearTimeout(timeout);
  }, []);

  useEffect(() => {
    if (!storageReady) return;
    try {
      localStorage.setItem("sft-e01-moving-stage-v1", JSON.stringify(progressRef.current));
    } catch { /* optional */ }
  }, [storageReady, started, finished, sceneIndex, beat, activityStep, complete, starCount, letters, curtain, doors, drawn, cardOpen]);

  useEffect(() => {
    if (!storageReady) return;
    const saveNow = () => {
      try { localStorage.setItem("sft-e01-moving-stage-v1", JSON.stringify(progressRef.current)); } catch { /* optional */ }
    };
    const saveWhenHidden = () => { if (document.visibilityState === "hidden") saveNow(); };
    window.addEventListener("pagehide", saveNow);
    document.addEventListener("visibilitychange", saveWhenHidden);
    return () => {
      window.removeEventListener("pagehide", saveNow);
      document.removeEventListener("visibilitychange", saveWhenHidden);
    };
  }, [storageReady]);

  function nextBeat() {
    playEffect("tap");
    if (beat < scene.lines.length) setBeat((value) => value + 1);
  }

  function finishActivity() {
    playEffect(scene.star ? "star" : "tap");
    setComplete(true);
    if (scene.star) {
      setSavedStars((value) => Math.max(value, scene.star ?? value));
      setEarnedStar(scene.star);
      window.setTimeout(() => setEarnedStar(null), 2400);
    }
  }

  function replayActivity() {
    audioRef.current?.pause();
    lastAutoLineRef.current = "";
    setComplete(false); setActivityStep(0); setLetters(0); setCurtain(0); setDoors([]); setDrawn(false); setCardOpen(false); setEarnedStar(null);
    curtainRevealRef.current = false;
  }

  function nextScene() {
    playEffect("step");
    if (sceneIndex === scenes.length - 1) {
      setFinished(true);
      try { localStorage.setItem("sft-active-level-v1", "select"); } catch { /* optional */ }
      return;
    }
    setSceneIndex((value) => value + 1);
    setBeat(0); setActivityStep(0); setComplete(false); setLetters(0); setCurtain(0); setDoors([]); setDrawn(false); setCardOpen(false); setEarnedStar(null);
    curtainRevealRef.current = false;
  }

  function pointerPosition(event: PointerEvent<HTMLCanvasElement>) {
    const canvas = canvasRef.current!;
    const box = canvas.getBoundingClientRect();
    return { x: (event.clientX - box.left) * canvas.width / box.width, y: (event.clientY - box.top) * canvas.height / box.height };
  }

  function drawStart(event: PointerEvent<HTMLCanvasElement>) {
    if (!drawn) playEffect("rustle");
    drawingRef.current = true; setDrawn(true); event.currentTarget.setPointerCapture(event.pointerId);
    const point = pointerPosition(event); const context = canvasRef.current?.getContext("2d");
    context?.beginPath(); context?.moveTo(point.x, point.y);
  }

  function drawMove(event: PointerEvent<HTMLCanvasElement>) {
    if (!drawingRef.current) return;
    const context = canvasRef.current?.getContext("2d"); const point = pointerPosition(event);
    if (context) { context.strokeStyle = "#243653"; context.lineWidth = 7; context.lineCap = "round"; context.lineTo(point.x, point.y); context.stroke(); }
  }

  function submitCode(event: FormEvent) {
    event.preventDefault();
    const clean = code.toUpperCase().replace(/[^A-Z]/g, "");
    setCodeMessage(codes[clean] ?? "That code is sleeping in another book page. Keep looking.");
    if (codes[clean]) setCode("");
  }

  function restart() {
    audioRef.current?.pause(); setStarted(true); setFinished(false); setSceneIndex(0); setBeat(0); setActivityStep(0); setComplete(false); setSavedStars(0); setLetters(0); setCurtain(0); setDoors([]); setDrawn(false); setCardOpen(false); setEarnedStar(null);
    lastAutoLineRef.current = "";
    curtainRevealRef.current = false;
    try {
      localStorage.removeItem("sft-e01-moving-stage-v1");
      localStorage.setItem("sft-active-level-v1", "e01");
    } catch { /* optional */ }
  }

  function beginLevelOne() {
    setFinished(false); setStarted(true);
    try { localStorage.setItem("sft-active-level-v1", "e01"); } catch { /* optional */ }
    window.setTimeout(() => playEffect("clunk"), 50);
  }

  function beginLevelTwo() {
    audioRef.current?.pause(); setStarted(false);
    try {
      if (savedLevelTwoRooms === 9) {
        localStorage.removeItem("sft-e02-moving-stage-v1");
        setSavedLevelTwoRooms(0);
      }
      localStorage.setItem("sft-active-level-v1", "e02");
    } catch { /* optional */ }
    setLevelTwoActive(true);
  }

  function showLevelSelect() {
    audioRef.current?.pause(); setFinished(false); setStarted(false); setLevelTwoActive(false); setJournalOpen(false);
    try {
      localStorage.setItem("sft-active-level-v1", "select");
      const savedLevelTwo = JSON.parse(localStorage.getItem("sft-e02-moving-stage-v1") ?? "{}");
      if (savedLevelTwo.finished === true) setSavedLevelTwoRooms(9);
      else if (typeof savedLevelTwo.sceneIndex === "number") setSavedLevelTwoRooms(Math.max(0, Math.min(9, savedLevelTwo.sceneIndex + (savedLevelTwo.complete ? 1 : 0))));
    } catch { /* optional */ }
  }

  function activity() {
    if (complete) return null;
    if (scene.activity === "note") return <div className="note-search" aria-label="Find the note among three things">
      <button className="emoji-prop note-choice note-map" onClick={() => { playEffect("tap"); setActivityStep(1); }} aria-label="Choose the route map"><span aria-hidden="true">🗺️</span><b>Map</b></button>
      <button className="emoji-prop note-choice note-book" onClick={() => { playEffect("tap"); setActivityStep(2); }} aria-label="Choose the blue book"><span aria-hidden="true">📘</span><b>Book</b></button>
      <button className="emoji-prop note-choice note-paper pulse" onClick={() => { playEffect("rustle"); finishActivity(); }} aria-label="Choose the written note"><span aria-hidden="true">📝</span><b>Note</b></button>
      {activityStep > 0 && <p className="gentle-hint note-hint">That is the {activityStep === 1 ? "map" : "book"}. Which thing is one sheet of paper with writing on it?</p>}
    </div>;
    if (scene.activity === "box") return <>
      <button className={`emoji-prop toy-prop ${activityStep ? "toy-moved" : "pulse"}`} onClick={() => { playEffect("rustle"); setActivityStep(1); }} aria-label="Move Sol's toy outside the box"><span aria-hidden="true">🧸</span><b>Move toy</b></button>
      <button className={`emoji-prop box-emoji ${activityStep ? "pulse" : "locked"}`} onClick={() => activityStep && finishActivity()} disabled={!activityStep} aria-label="Look inside the cardboard box"><span aria-hidden="true">📦</span><b>Look inside</b></button>
    </>;
    if (scene.activity === "bell") return <button className="hotspot emoji-hotspot bell-hotspot pulse" onPointerDown={() => { playEffect("listen"); setActivityStep(1); }} onPointerUp={() => activityStep && finishActivity()} onPointerCancel={() => setActivityStep(0)}><span className="object-emoji" aria-hidden="true">🔔</span><span className="object-label">{activityStep ? "Listening…" : "Hold the bell"}</span></button>;
    if (scene.activity === "card") return <>
      {!cardOpen && <button className="hotspot emoji-hotspot card-hotspot pulse" onClick={() => setCardOpen(true)}><span className="object-emoji" aria-hidden="true">📄</span><span className="object-label">Touch the card</span></button>}
      {cardOpen && <div className="drawing-card">
        <canvas ref={canvasRef} width="420" height="230" aria-label="A blank card you can draw on" onPointerDown={drawStart} onPointerMove={drawMove} onPointerUp={() => { drawingRef.current = false; }} onPointerCancel={() => { drawingRef.current = false; }} />
        <div><button onClick={finishActivity}>{drawn ? "Keep my mark" : "Leave it blank"}</button><button onClick={() => { const c = canvasRef.current; c?.getContext("2d")?.clearRect(0, 0, c.width, c.height); setDrawn(false); }}>Clear</button></div>
      </div>}
    </>;
    if (scene.activity === "word") return <div className="letter-steps" aria-label={`${letters} of 7 letters found`}>{"NOTHING".split("").map((letter, index) => <button key={index} className={index < letters ? "found" : index === letters ? "next-letter pulse" : ""} onClick={() => { if (index !== letters) return; playEffect("tap"); const value = letters + 1; setLetters(value); if (value === 7) window.setTimeout(finishActivity, 650); }} aria-label={index === letters ? `Choose ${letter}` : index < letters ? `${letter} found` : "A sleeping tile"}>{index <= letters ? letter : "?"}</button>)}</div>;
    if (scene.activity === "curtain") return <div className={`curtain-play ${activityStep ? "revealed" : ""}`}><span className="curtain-toy" role="img" aria-label="Sol's teddy behind the curtain">🧸</span><div className="curtain-overlay" style={{ transform: `translateX(${curtain}%)` }} />{activityStep > 0 && <div className="curtain-surprise">There you are! <span aria-hidden="true">✨</span></div>}<label><span>Slide slowly</span><input aria-label="Slide the curtain open" type="range" min="0" max="105" value={curtain} onInput={(event) => { const value = Number(event.currentTarget.value); setCurtain(value); if (value >= 100 && !curtainRevealRef.current) { curtainRevealRef.current = true; setActivityStep(1); playEffect("rustle"); window.setTimeout(finishActivity, 3200); } }} /></label></div>;
    if (scene.activity === "doors") return <>
      <button className={`hotspot emoji-hotspot door-a ${doors.includes("A") ? "inspected" : "pulse"}`} onClick={() => { playEffect("clunk"); const next = doors.includes("A") ? doors : [...doors, "A"]; setDoors(next); if (next.includes("A") && next.includes("B")) window.setTimeout(finishActivity, 900); }}><span className="object-emoji" aria-hidden="true">🚪</span><span className="object-label">{doors.includes("A") ? "A showed a card 📄" : "Look behind door A"}</span></button>
      <button className={`hotspot emoji-hotspot door-b ${doors.includes("B") ? "inspected" : "pulse"}`} onClick={() => { playEffect("clunk"); const next = doors.includes("B") ? doors : [...doors, "B"]; setDoors(next); if (next.includes("A") && next.includes("B")) window.setTimeout(finishActivity, 900); }}><span className="object-emoji" aria-hidden="true">🚪</span><span className="object-label">{doors.includes("B") ? "B showed no object" : "Look behind door B"}</span></button>
    </>;
    return <>
      <button className="emoji-prop recall-box pulse" onClick={finishActivity} aria-label="Choose the empty cardboard box"><span aria-hidden="true">📦</span><b>Box</b></button>
      <button className="emoji-prop recall-toy" onClick={() => setActivityStep(1)} aria-label="Choose Sol's toy"><span aria-hidden="true">🧸</span><b>Toy</b></button>
      {activityStep > 0 && <p className="gentle-hint">The toy was outside. What was empty?</p>}
    </>;
  }

  if (levelTwoActive) return <LevelTwo onExit={showLevelSelect} />;

  if (!started) return <main className="opening-screen level-select-screen">
    {!storageReady && <div className="restore-screen" aria-label="Returning to your adventure"><p>Returning to your adventure…</p></div>}
    <div className="opening-art" /><div className="opening-shade" />
    <div className="opening-cast" aria-hidden="true">
      <CharacterSprite name="mira" speaking={false} index={0} />
      <CharacterSprite name="tavi" speaking={false} index={1} />
      <CharacterSprite name="sol" speaking={false} index={2} />
    </div>
    <section><p className="eyebrow">SFT LEARNING ADVENTURES</p><h1>Choose an adventure</h1><p>Mira, Sol and Tavi travel through one complete learning level for each book. Pick the level you want to play.</p><div className="level-grid"><article className="level-card available"><span>LEVEL 1 · READY</span><h2>The Star Door Mystery</h2><p>Book One: <em>Something Is Here</em><br />Eight replayable learning games</p><button className="primary" onClick={beginLevelOne}>{savedStars > 0 ? "Continue Level 1" : "Play Level 1"}</button>{savedStars > 0 && <small>{savedStars} of 5 clue stars found on this device</small>}</article><article className="level-card available level-two-card"><span>LEVEL 2 · READY</span><h2>The Moon Lantern Workshop</h2><p>Book Two: <em>One Whole, Many Parts</em><br />Nine replayable learning games</p><button className="primary" onClick={beginLevelTwo}>{savedLevelTwoRooms === 9 ? "Play Level 2 again" : savedLevelTwoRooms > 0 ? "Continue Level 2" : "Play Level 2"}</button>{savedLevelTwoRooms > 0 && <small>{savedLevelTwoRooms} of 9 story steps complete on this device</small>}</article></div><p className="small-print">Local Kokoro narration · captions always shown · no adverts or sign-in</p></section>
  </main>;

  if (finished) return <main className="ending-screen">
    <div className="ending-art" /><button className="ending-home" onClick={showLevelSelect} aria-label="Choose a level">⌂ Levels</button><section><p className="eyebrow">LEVEL ONE COMPLETE</p><StarTrail count={5} /><h1>The mystery is solved.</h1><p>Mira, Sol, Tavi and their new friend Nori searched every room. They found things, sounds and a written word—but no thing called nothing.</p><blockquote>Nothing was not a thing they could find.</blockquote><p className="grownup-boundary"><strong>For grown-ups:</strong> this is the E01 operational boundary. It concerns what is presented within the check; it makes no claim of authority over an unexpressed metaphysical domain.</p><div className="ending-controls"><button className="primary" onClick={restart}>Play Level 1 again</button><button className="secondary" onClick={showLevelSelect}>Choose a level</button></div></section>
  </main>;

  return <main className="game-shell">
    <header className="game-hud">
      <div><span className="eyebrow">THE STAR DOOR MYSTERY</span><strong>{scene.title}</strong></div>
      <StarTrail count={starCount} focus={starCount === 0} newest={earnedStar} />
      <nav><button onClick={showLevelSelect} aria-label="Choose a level">⌂ <span>Levels</span></button><button onClick={() => playLine()} aria-label="Replay narration">↻ <span>Hear again</span></button><button onClick={() => setMuted((value) => !value)} aria-pressed={muted}>{muted ? "🔇" : "🔊"} <span>{muted ? "Narration off" : "Narration on"}</span></button><button onClick={() => setJournalOpen(true)}>⌨ <span>Book code</span></button></nav>
    </header>

    <section key={scene.id} className={`play-stage scene-${scene.id}`} style={{ backgroundImage: `url('/art/stages/${scene.background}')` }} aria-label={`${scene.title}, an animated star-room story scene`}>
      <div className="stage-light" />
      {beat === 0 && scene.journey && <div className="journey-banner"><span aria-hidden="true">✨</span><strong>{scene.journey}</strong></div>}
      {scene.introduces && beat <= 1 && <div className="guest-banner">New friend for Level One: <strong>{characterNames[scene.introduces]}</strong></div>}
      {scene.id === "note" && beat >= 1 && !dialogueDone && <div className={`story-note ${beat >= 2 ? "picked-up" : "landed"}`} role="img" aria-label={beat >= 2 ? "Mira is holding the note" : "The note has landed next to Mira"}><strong>Note</strong><span aria-hidden="true">📝</span></div>}
      <div className="walking-cast" aria-hidden="true">{scene.cast.map((name, index) => <CharacterSprite key={name} name={name} index={index} speaking={speakingName === name} />)}</div>
      {dialogueDone && !complete && <div className="activity-layer">{activity()}</div>}
      {earnedStar && <div className="star-reward" role="status"><span aria-hidden="true">★</span><strong>Clue star {earnedStar} lights!</strong></div>}

      <aside className={`speech-panel ${dialogueDone && !complete ? "prompting" : ""} ${complete ? "completed" : ""}`} aria-live="polite">
        {!dialogueDone || complete ? <>
          <div className="speaker-portrait"><SpeakerPortrait speaker={currentLine.speaker} /></div><span className="speaker">{currentLine.speaker}</span><p>{currentLine.text}</p>{complete ? <div className="completion-controls"><button className="replay-control" onClick={replayActivity}><span aria-hidden="true">↻</span> Play again</button><button className="next-control" onClick={nextScene}>{sceneIndex === scenes.length - 1 ? "Finish the case" : "Follow the next arrow"} <span aria-hidden="true">→</span></button></div> : <button className="next-control" onClick={nextBeat}>Next <span aria-hidden="true">→</span></button>}
        </> : <>
          <div className="speaker-portrait prompt-portrait" aria-hidden="true">☝️</div><span className="speaker">YOUR TURN</span><p>{scene.prompt}</p><span className="action-nudge" aria-hidden="true">↑ Try it in the room</span>
        </>}
      </aside>
    </section>

    <button className="restart-corner" onClick={restart}>Start over</button>
    {journalOpen && <div className="modal-backdrop" role="presentation" onMouseDown={() => setJournalOpen(false)}><section className="code-modal" role="dialog" aria-modal="true" aria-labelledby="code-title" onMouseDown={(event) => event.stopPropagation()}><button className="close-modal" onClick={() => setJournalOpen(false)} aria-label="Close">×</button><p className="eyebrow">OPTIONAL BOOK SECRET</p><h2 id="code-title">Mira&apos;s code pocket</h2><p>The book hides six codes in its pictures. They unlock jokes and previews, never lessons or progress.</p><form onSubmit={submitCode}><label htmlFor="book-code">Code from the book</label><div><input id="book-code" value={code} onChange={(event) => setCode(event.target.value)} autoComplete="off" /><button>Open</button></div></form><p className="code-result" aria-live="polite">{codeMessage}</p></section></div>}
  </main>;
}
