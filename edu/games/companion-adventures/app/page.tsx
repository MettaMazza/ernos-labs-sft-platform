"use client";

import { FormEvent, PointerEvent, useEffect, useRef, useState } from "react";

type Character = "tavi" | "sol" | "vee" | "moss" | "nori" | "luma";
type Activity = "note" | "box" | "bell" | "card" | "word" | "curtain" | "doors" | "recall";

type Line = { speaker: string; text: string; audio: string };
type Scene = {
  id: string;
  title: string;
  background: string;
  cast: Character[];
  activity: Activity;
  star?: number;
  lines: Line[];
  prompt: string;
  success: Line;
};

const scenes: Scene[] = [
  {
    id: "note", title: "The door wakes", background: "e01-stage-01-observatory-v1.png", cast: ["tavi", "sol"], activity: "note",
    lines: [
      { speaker: "Narrator", text: "Before breakfast, the brass Star Door woke with a clunk.", audio: "01-narrator-door-wakes" },
      { speaker: "Mira", text: "A note! It says: Find nothing. Five clues will show the way.", audio: "02-mira-note" },
      { speaker: "Sol", text: "Find nothing? Easy. I am brilliant at finding things that are not there!", audio: "03-sol-easy" },
    ],
    prompt: "Tap the glowing note beside the Star Door.",
    success: { speaker: "Mira", text: "Then we start with what the door gave us: a real note and five empty star spaces.", audio: "04-mira-start" },
  },
  {
    id: "box", title: "Sol's missing toy", background: "e01-stage-01-observatory-v1.png", cast: ["sol", "tavi"], activity: "box", star: 1,
    lines: [
      { speaker: "Narrator", text: "The first clue was tucked inside the parcel. Sol reached in.", audio: "05-narrator-parcel" },
      { speaker: "Sol", text: "My toy! I knew I packed you.", audio: "06-sol-toy" },
      { speaker: "Sol", text: "Now the box has nothing in it.", audio: "07-sol-nothing" },
      { speaker: "Tavi", text: "Look again, Sol. Move the toy, then look inside the box.", audio: "08-tavi-look" },
    ],
    prompt: "Move the toy out, then tap the open box.",
    success: { speaker: "Tavi", text: "The toy is outside. The empty box is still here. Empty means the toy is not inside.", audio: "09-tavi-empty" },
  },
  {
    id: "bell", title: "The quiet bell", background: "e01-stage-02-bell-gallery-v1.png", cast: ["nori", "tavi"], activity: "bell", star: 2,
    lines: [
      { speaker: "Nori", text: "Shh. The wind has stopped.", audio: "10-nori-shh" },
      { speaker: "Narrator", text: "The brass bell hung still. Nori leaned close to listen.", audio: "11-narrator-bell" },
    ],
    prompt: "Press and hold the bell while you listen.",
    success: { speaker: "Nori", text: "I heard no ring. But I heard my breath, and the bell stayed right there.", audio: "12-nori-no-ring" },
  },
  {
    id: "card", title: "Vee's blank card", background: "e01-stage-03-paper-room-v1.png", cast: ["vee", "tavi"], activity: "card", star: 3,
    lines: [
      { speaker: "Vee", text: "This card has nothing on it. Shall we test that?", audio: "13-vee-card" },
      { speaker: "Mira", text: "Use your finger. Make a mark, or choose to leave the card blank.", audio: "14-mira-draw" },
    ],
    prompt: "Draw on the card—or leave it blank—then check.",
    success: { speaker: "Vee", text: "A mark is something we can see. A blank card is still a card. Neither choice made nothing appear.", audio: "15-vee-result" },
  },
  {
    id: "word", title: "Seven glowing steps", background: "e01-stage-03-paper-room-v1.png", cast: ["moss", "vee"], activity: "word", star: 4,
    lines: [
      { speaker: "Moss", text: "The card made the wall tiles glow.", audio: "16-moss-glow" },
      { speaker: "Moss", text: "They want us to spell the mystery word. Step with me.", audio: "17-moss-step" },
    ],
    prompt: "Tap the letters in order to spell NOTHING.",
    success: { speaker: "Moss", text: "Nothing is a word we can see, say and read. The word did not vanish when we named it.", audio: "18-moss-word" },
  },
  {
    id: "curtain", title: "Luma's vanishing trick", background: "e01-stage-04-curtain-passage-v1.png", cast: ["luma", "sol"], activity: "curtain", star: 5,
    lines: [
      { speaker: "Luma", text: "I can make Sol's toy vanish. Watch!", audio: "19-luma-trick" },
      { speaker: "Sol", text: "Hey! That is my toy!", audio: "20-sol-hey" },
    ],
    prompt: "Drag the curtain all the way open.",
    success: { speaker: "Luma", text: "There it is. Hidden is not gone. The curtain only changed what we could see.", audio: "21-luma-hidden" },
  },
  {
    id: "doors", title: "The final question", background: "e01-stage-05-star-door-v1.png", cast: ["tavi", "nori", "moss"], activity: "doors",
    lines: [
      { speaker: "Mira", text: "Five clues. Five stars. The Star Door is opening!", audio: "22-mira-five" },
      { speaker: "Narrator", text: "Two little doors waited. Door A offered a card. Door B offered no object.", audio: "23-narrator-two-doors" },
      { speaker: "Mira", text: "The note said, find nothing. Which door showed us nothing?", audio: "24-mira-question" },
    ],
    prompt: "Inspect both little doors.",
    success: { speaker: "Tavi", text: "Neither door showed nothing. A showed a card. B showed no object, so we do not invent one.", audio: "25-tavi-neither" },
  },
  {
    id: "recall", title: "The map remembers", background: "e01-stage-06-library-v1.png", cast: ["tavi", "sol", "vee"], activity: "recall",
    lines: [
      { speaker: "Narrator", text: "The crew carried the bright map into the library. Its first star blinked.", audio: "26-narrator-library" },
      { speaker: "Tavi", text: "Before we file it: what did Sol call empty?", audio: "27-tavi-remember" },
    ],
    prompt: "Tap the object that was empty in the first clue.",
    success: { speaker: "Mira", text: "The box was here. The toy was outside. We found no nothing, and we never had to pretend.", audio: "28-mira-ending" },
  },
];

const codes: Record<string, string> = {
  ROOMSTAR: "Pip found a practice star tucked under Mira's rug.",
  BOXCLUE: "Sol's joke: an empty box can still be full of clues.",
  QUIETWINGS: "Nori teaches Pip a silent wing-wave.",
  BLANKEDGE: "Vee opens a secret sketchbook pocket.",
  CURTAINMAP: "Luma's curtain stitches glow like a route map.",
  TWODOORS: "The next parcel whispers: one whole can have many parts.",
};

const characterNames: Record<Character, string> = { tavi: "Tavi", sol: "Sol", vee: "Vee", moss: "Moss", nori: "Nori", luma: "Luma" };

function CharacterSprite({ name, speaking, index }: { name: Character; speaking: boolean; index: number }) {
  return (
    <div className={`actor actor-${name} ${speaking ? "speaking" : ""}`} style={{ "--actor-index": index } as React.CSSProperties}>
      <img src={`/art/characters/individual/${name}.png`} alt="" draggable={false} />
      <span>{characterNames[name]}</span>
    </div>
  );
}

function StarTrail({ count }: { count: number }) {
  return <div className="star-trail" aria-label={`${count} of 5 clue stars lit`}>{[1, 2, 3, 4, 5].map((n) => <span key={n} className={n <= count ? "lit" : ""}>{n <= count ? "★" : "☆"}</span>)}</div>;
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
  const audioRef = useRef<HTMLAudioElement | null>(null);
  const canvasRef = useRef<HTMLCanvasElement | null>(null);
  const drawingRef = useRef(false);
  const soundContextRef = useRef<AudioContext | null>(null);

  const scene = scenes[sceneIndex];
  const dialogueDone = beat >= scene.lines.length;
  const currentLine = complete ? scene.success : scene.lines[Math.min(beat, scene.lines.length - 1)];
  const speakingName = currentLine?.speaker.toLowerCase();
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
      gain.gain.setValueAtTime(0.0001, now + index * .075);
      gain.gain.exponentialRampToValueAtTime(kind === "listen" ? .035 : .09, now + index * .075 + .012);
      gain.gain.exponentialRampToValueAtTime(0.0001, now + index * .075 + (kind === "star" ? .42 : .16));
      oscillator.connect(gain).connect(context.destination);
      oscillator.start(now + index * .075);
      oscillator.stop(now + index * .075 + (kind === "star" ? .44 : .18));
    });
  }

  useEffect(() => {
    if (started && currentLine) playLine(currentLine);
    return () => audioRef.current?.pause();
    // The selected line is the intentional narration trigger.
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
    if (scene.star) setSavedStars((value) => Math.max(value, scene.star ?? value));
  }

  function nextScene() {
    playEffect("step");
    if (sceneIndex === scenes.length - 1) { setFinished(true); return; }
    setSceneIndex((value) => value + 1);
    setBeat(0); setActivityStep(0); setComplete(false); setLetters(0); setCurtain(0); setDoors([]); setDrawn(false); setCardOpen(false);
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
    audioRef.current?.pause(); setStarted(true); setFinished(false); setSceneIndex(0); setBeat(0); setActivityStep(0); setComplete(false); setSavedStars(0); setLetters(0); setCurtain(0); setDoors([]);
    try { localStorage.removeItem("sft-e01-moving-stage-v1"); } catch { /* optional */ }
  }

  function activity() {
    if (complete) return null;
    if (scene.activity === "note") return <button className="hotspot note-hotspot pulse" onClick={() => { playEffect("clunk"); finishActivity(); }}><span>Read the note</span></button>;
    if (scene.activity === "box") return <>
      <button className={`stage-prop toy-prop ${activityStep ? "toy-moved" : ""}`} onClick={() => { playEffect("rustle"); setActivityStep(1); }} aria-label="Move Sol's toy out of the box"><img src="/art/props/teddy.png" alt="Sol's toy" /></button>
      <button className={`hotspot box-hotspot ${activityStep ? "pulse" : "locked"}`} onClick={() => activityStep && finishActivity()} disabled={!activityStep}><span>Look inside</span></button>
    </>;
    if (scene.activity === "bell") return <button className="hotspot bell-hotspot pulse" onPointerDown={() => { playEffect("listen"); setActivityStep(1); }} onPointerUp={() => activityStep && finishActivity()} onPointerCancel={() => setActivityStep(0)}><span>{activityStep ? "Listening…" : "Hold to listen"}</span></button>;
    if (scene.activity === "card") return <>
      {!cardOpen && <button className="hotspot card-hotspot pulse" onClick={() => setCardOpen(true)}><span>Touch the card</span></button>}
      {cardOpen && <div className="drawing-card">
        <canvas ref={canvasRef} width="420" height="230" aria-label="A blank card you can draw on" onPointerDown={drawStart} onPointerMove={drawMove} onPointerUp={() => { drawingRef.current = false; }} onPointerCancel={() => { drawingRef.current = false; }} />
        <div><button onClick={finishActivity}>{drawn ? "Keep my mark" : "Leave it blank"}</button><button onClick={() => { const c = canvasRef.current; c?.getContext("2d")?.clearRect(0, 0, c.width, c.height); setDrawn(false); }}>Clear</button></div>
      </div>}
    </>;
    if (scene.activity === "word") return <div className="letter-steps" aria-label={`${letters} of 7 letters found`}>{"NOTHING".split("").map((letter, index) => <button key={index} className={index < letters ? "found" : index === letters ? "next-letter pulse" : ""} onClick={() => { if (index !== letters) return; playEffect("tap"); const value = letters + 1; setLetters(value); if (value === 7) window.setTimeout(finishActivity, 450); }} aria-label={index === letters ? `Choose ${letter}` : index < letters ? `${letter} found` : "A sleeping tile"}>{index <= letters ? letter : "?"}</button>)}</div>;
    if (scene.activity === "curtain") return <div className="curtain-play"><img src="/art/props/teddy.png" alt="Sol's toy behind the curtain" /><div className="curtain-overlay" style={{ transform: `translateX(${curtain}%)` }} /><label><span>Slide the curtain</span><input aria-label="Slide the curtain open" type="range" min="0" max="105" value={curtain} onInput={(event) => { const value = Number(event.currentTarget.value); setCurtain(value); if (value >= 100) finishActivity(); }} /></label></div>;
    if (scene.activity === "doors") return <>
      <button className={`hotspot door-a ${doors.includes("A") ? "inspected" : "pulse"}`} onClick={() => { playEffect("clunk"); const next = doors.includes("A") ? doors : [...doors, "A"]; setDoors(next); if (next.includes("A") && next.includes("B")) window.setTimeout(finishActivity, 500); }}><span>{doors.includes("A") ? "A showed a card" : "Inspect A"}</span></button>
      <button className={`hotspot door-b ${doors.includes("B") ? "inspected" : "pulse"}`} onClick={() => { playEffect("clunk"); const next = doors.includes("B") ? doors : [...doors, "B"]; setDoors(next); if (next.includes("A") && next.includes("B")) window.setTimeout(finishActivity, 500); }}><span>{doors.includes("B") ? "B showed no object" : "Inspect B"}</span></button>
    </>;
    return <>
      <button className="stage-prop recall-box pulse" onClick={finishActivity} aria-label="Choose the empty box"><img src="/art/props/box.png" alt="Open box" /></button>
      <button className="stage-prop recall-toy" onClick={() => setActivityStep(1)} aria-label="Choose Sol's toy"><img src="/art/props/teddy.png" alt="Sol's toy" /></button>
      {activityStep > 0 && <p className="gentle-hint">The toy was outside. What was empty?</p>}
    </>;
  }

  if (!started) return <main className="opening-screen">
    <div className="opening-art" />
    <div className="opening-shade" />
    <section>
      <p className="eyebrow">BOOK ONE · PLAYABLE LEVEL ONE · REBUILD 1.4.0</p>
      <h1>The Star Door Mystery</h1>
      <p>The door has woken. Mira and six little travellers need your help to follow five clues.</p>
      <button className="primary" onClick={() => { setStarted(true); window.setTimeout(() => playEffect("clunk"), 50); }}>Start the story</button>
      <p className="small-print">Narrated with local Kokoro voices · captions always shown · no adverts or sign-in</p>
    </section>
  </main>;

  if (finished) return <main className="ending-screen">
    <div className="ending-art" />
    <section>
      <p className="eyebrow">LEVEL ONE COMPLETE</p><StarTrail count={5} />
      <h1>The mystery is solved.</h1>
      <p>The crew always found something they could see, hear, say, draw or remember. When a door showed no object, they did not pretend it had shown “nothing”.</p>
      <blockquote>There is no nothing.</blockquote>
      <p className="grownup-boundary"><strong>For grown-ups:</strong> this is the E01 operational boundary. It concerns what is presented within the check; it makes no claim of authority over an unexpressed metaphysical domain.</p>
      <button className="primary" onClick={restart}>Play the story again</button>
    </section>
  </main>;

  return <main className="game-shell">
    <header className="game-hud">
      <div><span className="eyebrow">THE STAR DOOR MYSTERY</span><strong>{scene.title}</strong></div>
      <StarTrail count={starCount} />
      <nav>
        <button onClick={() => playLine()} aria-label="Replay narration">↻ <span>Hear again</span></button>
        <button onClick={() => setMuted((value) => !value)} aria-pressed={muted}>{muted ? "🔇" : "🔊"} <span>{muted ? "Narration off" : "Narration on"}</span></button>
        <button onClick={() => setJournalOpen(true)}>⌨ <span>Book code</span></button>
      </nav>
    </header>

    <section key={scene.id} className={`play-stage scene-${scene.id}`} style={{ backgroundImage: `url('/art/stages/${scene.background}')` }} aria-label={`${scene.title}, an animated observatory story scene`}>
      <div className="stage-light" />
      <div className="walking-cast" aria-hidden="true">{scene.cast.map((name, index) => <CharacterSprite key={name} name={name} index={index} speaking={speakingName === name} />)}</div>
      {dialogueDone && !complete && <div className="activity-layer">{activity()}</div>}

      <aside className={`speech-panel ${dialogueDone && !complete ? "prompting" : ""}`} aria-live="polite">
        {!dialogueDone || complete ? <>
          <span className="speaker">{currentLine.speaker}</span>
          <p>{currentLine.text}</p>
          <button className="next-control" onClick={complete ? nextScene : nextBeat}>{complete ? (sceneIndex === scenes.length - 1 ? "Finish the case" : "Walk to the next room") : "Next"} <span aria-hidden="true">→</span></button>
        </> : <>
          <span className="speaker">YOUR TURN</span><p>{scene.prompt}</p>
          <span className="action-nudge" aria-hidden="true">↑ Try it in the room</span>
        </>}
      </aside>
    </section>

    <button className="restart-corner" onClick={restart}>Start over</button>

    {journalOpen && <div className="modal-backdrop" role="presentation" onMouseDown={() => setJournalOpen(false)}>
      <section className="code-modal" role="dialog" aria-modal="true" aria-labelledby="code-title" onMouseDown={(event) => event.stopPropagation()}>
        <button className="close-modal" onClick={() => setJournalOpen(false)} aria-label="Close">×</button>
        <p className="eyebrow">OPTIONAL BOOK SECRET</p><h2 id="code-title">Pip’s code pocket</h2>
        <p>The book hides six codes in its pictures. They unlock jokes and previews, never lessons or progress.</p>
        <form onSubmit={submitCode}><label htmlFor="book-code">Code from the book</label><div><input id="book-code" value={code} onChange={(event) => setCode(event.target.value)} autoComplete="off" /><button>Open</button></div></form>
        <p className="code-result" aria-live="polite">{codeMessage}</p>
      </section>
    </div>}
  </main>;
}
