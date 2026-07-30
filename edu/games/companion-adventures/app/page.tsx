"use client";

import { CSSProperties, FormEvent, PointerEvent, useEffect, useRef, useState } from "react";

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
    id: "note", title: "The door wakes", background: "e01-stage-01-observatory-v1.png", cast: ["mira", "tavi", "sol"], activity: "note",
    lines: [
      { speaker: "Narrator", text: "Before breakfast, the brass Star Door woke with a clunk.", audio: "01-narrator-door-wakes" },
      { speaker: "Mira", text: "A note! It says: Find nothing. Five clues will show the way.", audio: "02-mira-note" },
      { speaker: "Sol", text: "Find nothing? Easy. I am brilliant at finding things that are not there!", audio: "03-sol-easy" },
      { speaker: "Tavi", text: "Let us stay together and look carefully. We will follow every clue.", audio: "04-tavi-together" },
    ],
    prompt: "Which object slid from the Star Door? Find and tap the written note.",
    success: { speaker: "Mira", text: "Look at the five hollow stars at the top. Each clue we find will light one. The first arrow points to the parcel!", audio: "05-mira-star-map" },
  },
  {
    id: "box", title: "The parcel clue", background: "e01-stage-01-observatory-v1.png", cast: ["mira", "tavi", "sol"], journey: "The first arrow leads across the observatory to the parcel.", activity: "box", star: 1,
    lines: [
      { speaker: "Narrator", text: "Mira, Sol and Tavi followed the first arrow across the observatory. They looked for nothing inside the parcel.", audio: "06-narrator-to-parcel" },
      { speaker: "Sol", text: "My toy! I knew I packed you.", audio: "07-sol-toy" },
      { speaker: "Sol", text: "Now the box has nothing in it.", audio: "08-sol-nothing" },
      { speaker: "Tavi", text: "Let us check. Move the toy outside, then look inside the box.", audio: "09-tavi-look" },
    ],
    prompt: "Move the toy outside, then tap the box.",
    success: { speaker: "Tavi", text: "The toy is outside. The empty box is still here. Empty means the toy is not inside. We found a box, not nothing.", audio: "10-tavi-empty" },
  },
  {
    id: "bell", title: "Meet Nori in the bell room", background: "e01-stage-02-bell-gallery-v1.png", cast: ["mira", "tavi", "sol", "nori"], journey: "The box was still there, so the next arrow leads to the bell room.", introduces: "nori", activity: "bell", star: 2,
    lines: [
      { speaker: "Narrator", text: "They found an empty box, but they did not find nothing. So they followed the next glowing arrow into the bell room to try there.", audio: "11-narrator-to-bells" },
      { speaker: "Nori", text: "Hello! I am Nori. I listen for tiny sounds. May I join your search?", audio: "12-nori-meets" },
      { speaker: "Mira", text: "Yes, please, Nori. We are looking for nothing. Let us listen together.", audio: "13-mira-welcome" },
      { speaker: "Nori", text: "Listen closely. The wind has stopped.", audio: "14-nori-listen" },
      { speaker: "Narrator", text: "The brass bell hung still. Nori leaned close to listen.", audio: "15-narrator-bell" },
    ],
    prompt: "Press and hold the bell while everyone listens.",
    success: { speaker: "Nori", text: "I heard no ring. But I heard my breath, and the bell stayed right there. We found a bell, not nothing.", audio: "16-nori-no-ring" },
  },
  {
    id: "card", title: "The paper room", background: "e01-stage-03-paper-room-v1.png", cast: ["mira", "tavi", "sol", "nori"], journey: "The bell stayed in the room, so everyone follows the next arrow to the paper room.", activity: "card", star: 3,
    lines: [
      { speaker: "Narrator", text: "They heard no ring, but the bell was still there. So the four friends went through the blue door to look for nothing in the paper room.", audio: "17-narrator-to-paper" },
      { speaker: "Mira", text: "Here is a card with no mark on it. Shall we test it?", audio: "18-mira-card" },
      { speaker: "Tavi", text: "Use your finger. Make a mark, or choose to leave the card blank.", audio: "19-tavi-draw" },
    ],
    prompt: "Draw on the card—or leave it blank—then check.",
    success: { speaker: "Mira", text: "A mark is something we can see. A blank card is still a card. We found a card, not nothing.", audio: "20-mira-card-result" },
  },
  {
    id: "word", title: "Seven glowing steps", background: "e01-stage-03-paper-room-v1.png", cast: ["mira", "tavi", "sol", "nori"], journey: "The card remained, so seven tiles glow and offer the next place to look.", activity: "word", star: 4,
    lines: [
      { speaker: "Narrator", text: "They found a card whether it was marked or blank. Then seven wall tiles began to glow, so they tried the word next.", audio: "21-narrator-to-word" },
      { speaker: "Sol", text: "The tiles want us to spell the mystery word. Step with me!", audio: "22-sol-step" },
    ],
    prompt: "Tap the letters in order to spell NOTHING.",
    success: { speaker: "Tavi", text: "Nothing is a word we can see, say and read. The word stayed here when we named it, so it is not nothing.", audio: "23-tavi-word" },
  },
  {
    id: "curtain", title: "Behind the curtain", background: "e01-stage-04-curtain-passage-v1.png", cast: ["mira", "tavi", "sol", "nori"], journey: "The word stayed visible, so a golden arrow leads everyone to the curtain passage.", activity: "curtain", star: 5,
    lines: [
      { speaker: "Narrator", text: "The word stayed visible, so it was not nothing. The next golden arrow led the four friends to a red curtain to try again.", audio: "24-narrator-to-curtain" },
      { speaker: "Sol", text: "My toy rolled behind the curtain. I cannot see it now!", audio: "25-sol-curtain" },
      { speaker: "Nori", text: "Let us slide the curtain slowly and watch what appears.", audio: "26-nori-curtain" },
    ],
    prompt: "Slowly slide the curtain open and watch for the toy.",
    success: { speaker: "Mira", text: "There it is! Hidden is not gone. The curtain changed what we could see. We found the toy, not nothing.", audio: "27-mira-hidden" },
  },
  {
    id: "doors", title: "The final question", background: "e01-stage-05-star-door-v1.png", cast: ["mira", "tavi", "sol", "nori"], journey: "Five clues are complete, so five bright stars open the great Star Door.", activity: "doors",
    lines: [
      { speaker: "Narrator", text: "They had tried five places and found something each time. Their five bright stars opened the great Star Door.", audio: "28-narrator-to-doors" },
      { speaker: "Narrator", text: "Two little doors waited. Door A offered a card. Door B offered no object.", audio: "29-narrator-two-doors" },
      { speaker: "Mira", text: "The note said, find nothing. Which door showed us nothing? Let us inspect both.", audio: "30-mira-question" },
    ],
    prompt: "Inspect both little doors before choosing.",
    success: { speaker: "Tavi", text: "Neither door showed nothing. A showed a card. B showed no object, so we do not invent one.", audio: "31-tavi-neither" },
  },
  {
    id: "recall", title: "The map remembers", background: "e01-stage-06-library-v1.png", cast: ["mira", "tavi", "sol", "nori"], journey: "The mystery is solved, so the friends carry their map to the library and remember the journey.", activity: "recall",
    lines: [
      { speaker: "Narrator", text: "The friends solved the door puzzle. Before going home, they carried the bright map into the library to remember where their search began.", audio: "32-narrator-library" },
      { speaker: "Tavi", text: "Before we file the map, what did Sol call empty in the first room?", audio: "33-tavi-remember" },
    ],
    prompt: "Tap the object that was empty in the first clue.",
    success: { speaker: "Mira", text: "The box was empty, but it was still here. The toy was outside. We searched every room and found no nothing.", audio: "34-mira-ending" },
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
  const audioRef = useRef<HTMLAudioElement | null>(null);
  const canvasRef = useRef<HTMLCanvasElement | null>(null);
  const drawingRef = useRef(false);
  const curtainRevealRef = useRef(false);
  const soundContextRef = useRef<AudioContext | null>(null);
  const lastAutoLineRef = useRef("");

  const scene = scenes[sceneIndex];
  const dialogueDone = beat >= scene.lines.length;
  const currentLine = complete ? scene.success : scene.lines[Math.min(beat, scene.lines.length - 1)];
  const speakingName = (!dialogueDone || complete) ? currentLine?.speaker.toLowerCase() : "";
  const starCount = Math.max(savedStars, scenes.slice(0, sceneIndex + (complete ? 1 : 0)).filter((item) => item.star).length);

  function playLine(line = currentLine) {
    if (!line || muted) return;
    audioRef.current?.pause();
    const audio = new Audio(`/audio/e01/${line.audio}.mp3`);
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
        const saved = JSON.parse(localStorage.getItem("sft-e01-moving-stage-v1") ?? "{}");
        if (typeof saved.sceneIndex === "number") setSceneIndex(Math.min(saved.sceneIndex, scenes.length - 1));
        if (typeof saved.stars === "number") setSavedStars(Math.min(saved.stars, 5));
      } catch { /* The story also works without local saving. */ }
    }, 0);
    return () => window.clearTimeout(timeout);
  }, []);

  useEffect(() => {
    if (!started) return;
    try { localStorage.setItem("sft-e01-moving-stage-v1", JSON.stringify({ sceneIndex, stars: starCount })); } catch { /* optional */ }
  }, [sceneIndex, starCount, started]);

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
    if (sceneIndex === scenes.length - 1) { setFinished(true); return; }
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
    audioRef.current?.pause(); setStarted(true); setFinished(false); setSceneIndex(0); setBeat(0); setActivityStep(0); setComplete(false); setSavedStars(0); setLetters(0); setCurtain(0); setDoors([]); setEarnedStar(null);
    lastAutoLineRef.current = "";
    curtainRevealRef.current = false;
    try { localStorage.removeItem("sft-e01-moving-stage-v1"); } catch { /* optional */ }
  }

  function activity() {
    if (complete) return null;
    if (scene.activity === "note") return <div className="note-search" aria-label="Find the note among three objects">
      <button className="emoji-prop note-choice note-map" onClick={() => { playEffect("tap"); setActivityStep(1); }} aria-label="Choose the route map"><span aria-hidden="true">🗺️</span><b>Map</b></button>
      <button className="emoji-prop note-choice note-book" onClick={() => { playEffect("tap"); setActivityStep(2); }} aria-label="Choose the blue book"><span aria-hidden="true">📘</span><b>Book</b></button>
      <button className="emoji-prop note-choice note-paper pulse" onClick={() => { playEffect("rustle"); finishActivity(); }} aria-label="Choose the written note"><span aria-hidden="true">📝</span><b>Note</b></button>
      {activityStep > 0 && <p className="gentle-hint note-hint">That is the {activityStep === 1 ? "map" : "book"}. Which object has writing on one sheet of paper?</p>}
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
      <button className={`hotspot emoji-hotspot door-a ${doors.includes("A") ? "inspected" : "pulse"}`} onClick={() => { playEffect("clunk"); const next = doors.includes("A") ? doors : [...doors, "A"]; setDoors(next); if (next.includes("A") && next.includes("B")) window.setTimeout(finishActivity, 900); }}><span className="object-emoji" aria-hidden="true">🚪</span><span className="object-label">{doors.includes("A") ? "A showed a card 📄" : "Inspect door A"}</span></button>
      <button className={`hotspot emoji-hotspot door-b ${doors.includes("B") ? "inspected" : "pulse"}`} onClick={() => { playEffect("clunk"); const next = doors.includes("B") ? doors : [...doors, "B"]; setDoors(next); if (next.includes("A") && next.includes("B")) window.setTimeout(finishActivity, 900); }}><span className="object-emoji" aria-hidden="true">🚪</span><span className="object-label">{doors.includes("B") ? "B showed no object" : "Inspect door B"}</span></button>
    </>;
    return <>
      <button className="emoji-prop recall-box pulse" onClick={finishActivity} aria-label="Choose the empty cardboard box"><span aria-hidden="true">📦</span><b>Box</b></button>
      <button className="emoji-prop recall-toy" onClick={() => setActivityStep(1)} aria-label="Choose Sol's toy"><span aria-hidden="true">🧸</span><b>Toy</b></button>
      {activityStep > 0 && <p className="gentle-hint">The toy was outside. What was empty?</p>}
    </>;
  }

  if (!started) return <main className="opening-screen">
    <div className="opening-art" /><div className="opening-shade" />
    <div className="opening-cast" aria-hidden="true">
      <CharacterSprite name="mira" speaking={false} index={0} />
      <CharacterSprite name="tavi" speaking={false} index={1} />
      <CharacterSprite name="sol" speaking={false} index={2} />
    </div>
    <section><p className="eyebrow">BOOK ONE · PLAYABLE LEVEL ONE</p><h1>The Star Door Mystery</h1><p>Mira, Sol and Tavi are the main adventure team. Today they will meet one new friend and follow five clues together.</p><button className="primary" onClick={() => { setStarted(true); window.setTimeout(() => playEffect("clunk"), 50); }}>Start the story</button><p className="small-print">Narrated with local Kokoro voices · captions always shown · no adverts or sign-in</p></section>
  </main>;

  if (finished) return <main className="ending-screen">
    <div className="ending-art" /><section><p className="eyebrow">LEVEL ONE COMPLETE</p><StarTrail count={5} /><h1>The mystery is solved.</h1><p>Mira, Sol, Tavi and their new friend Nori searched every room. They always found something present—or found that no object had been shown.</p><blockquote>There is no nothing.</blockquote><p className="grownup-boundary"><strong>For grown-ups:</strong> this is the E01 operational boundary. It concerns what is presented within the check; it makes no claim of authority over an unexpressed metaphysical domain.</p><button className="primary" onClick={restart}>Play the story again</button></section>
  </main>;

  return <main className="game-shell">
    <header className="game-hud">
      <div><span className="eyebrow">THE STAR DOOR MYSTERY</span><strong>{scene.title}</strong></div>
      <StarTrail count={starCount} focus={starCount === 0} newest={earnedStar} />
      <nav><button onClick={() => playLine()} aria-label="Replay narration">↻ <span>Hear again</span></button><button onClick={() => setMuted((value) => !value)} aria-pressed={muted}>{muted ? "🔇" : "🔊"} <span>{muted ? "Narration off" : "Narration on"}</span></button><button onClick={() => setJournalOpen(true)}>⌨ <span>Book code</span></button></nav>
    </header>

    <section key={scene.id} className={`play-stage scene-${scene.id}`} style={{ backgroundImage: `url('/art/stages/${scene.background}')` }} aria-label={`${scene.title}, an animated observatory story scene`}>
      <div className="stage-light" />
      {beat === 0 && scene.journey && <div className="journey-banner"><span aria-hidden="true">✨</span><strong>{scene.journey}</strong></div>}
      {scene.introduces && beat <= 1 && <div className="guest-banner">New friend for Level One: <strong>{characterNames[scene.introduces]}</strong></div>}
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
