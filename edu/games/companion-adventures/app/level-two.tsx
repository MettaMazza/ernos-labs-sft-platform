"use client";
/* eslint-disable react-hooks/refs -- refs are read only inside event handlers and effects */

import { CSSProperties, FormEvent, ReactNode, useEffect, useLayoutEffect, useRef, useState } from "react";

type Character = "mira" | "tavi" | "sol" | "pax";
type Activity = "parcel" | "whole" | "bridge" | "parts" | "rebuild" | "match" | "gap" | "count" | "sum";
type Line = { speaker: string; text: string; audio: string };
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
    success: { speaker: "Tavi", text: "You guided the parcel to our mat. Inside is a Moon Lantern! The card asks us to take it to the balcony before the first evening star.", audio: "03-tavi-reads-card" },
  },
  {
    id: "whole", title: "The small door", gameTitle: "Lantern Detective", gameIcon: "🔎", background: "e02-stage-02-whole-room-v1.png", cast: ["mira", "tavi", "sol", "pax"], journey: "Mission: get the whole lantern through the small door, then take it to the balcony.", introduces: "pax", activity: "whole",
    lines: [
      { speaker: "Narrator", text: "The friends followed the card towards the balcony. A small door blocked the way. The lantern was too wide to fit through it.", audio: "04-narrator-workshop-door" },
      { speaker: "Pax", text: "Hello! I’m Pax. We can take the lantern apart, carry every part through, and build the whole lantern again. First, tap the covered lantern. Each tap will uncover one part.", audio: "05-pax-meets" },
    ],
    prompt: "Tap the covered lantern four times. Each tap uncovers one part. When the whole lantern is visible, say what you found.",
    success: { speaker: "Mia", text: "That is our whole lantern. Every part is here, with no gap and no extra piece. Now we know what we must build again.", audio: "06-mira-whole" },
  },
  {
    id: "parts", title: "Choose the four-part plan", gameTitle: "Fit-the-Circle Lab", gameIcon: "🧩", background: "e02-stage-04-part-gate-v1.png", cast: ["mira", "tavi", "sol", "pax"], journey: "Step 1 of 4: choose parts that fill the whole lantern.", activity: "parts",
    lines: [
      { speaker: "Narrator", text: "Pax laid four lantern-picture cards beside a round plan frame.", audio: "10-narrator-next-door" },
      { speaker: "Pax", text: "Each card shows one same-size part. Match every curved part to its place. The four parts must fill the lantern plan with no gap and no part on top of another.", audio: "11-pax-find-parts" },
    ],
    prompt: "Tap a lantern-part card, then tap its matching place in the round plan. Fit all four parts with no gap or overlap.",
    success: { speaker: "Pax", text: "All four lantern pictures fit the plan. There is no gap, and no part covers another. Together, they fill the same whole lantern.", audio: "12-pax-parts-fit" },
  },
  {
    id: "match", title: "Check the sizes", gameTitle: "Twin-Part Test", gameIcon: "📏", background: "e02-stage-06-match-table-v1.png", cast: ["mira", "tavi", "sol", "pax"], journey: "Step 1 continued: check what ‘same size’ looks like before Pax uses the plan.", activity: "match",
    lines: [
      { speaker: "Narrator", text: "Pax put two pairs of lantern-part pictures on the balance table.", audio: "16-narrator-two-pairs" },
      { speaker: "Tavi", text: "One pair shows lantern parts that are the same size. Look at both pairs before you choose.", audio: "17-tavi-check-pairs" },
    ],
    prompt: "Choose or drag a lantern-part pair onto the balance track. Release it and find the pair that stays level.",
    success: { speaker: "Tavi", text: "Pair A has same-size lantern parts. Pair B has one big lantern part and one small one. Now Pax can use the four-part plan.", audio: "18-tavi-same-size" },
  },
  {
    id: "bridge", title: "Carry every part", gameTitle: "Doorway Delivery", gameIcon: "🚪", background: "e02-stage-03-count-bridge-v1.png", cast: ["mira", "tavi", "sol", "pax"], journey: "Step 2 of 4: Pax separates the lantern. Carry all four parts through the small door.", activity: "bridge",
    lines: [
      { speaker: "Narrator", text: "The lantern came apart into four pieces. All four waited beside the small door.", audio: "07-narrator-four-tiles" },
      { speaker: "Sol", text: "The door is narrow, so we must carry one lantern part at a time. Let’s move all four through, and not carry any part twice.", audio: "08-sol-twice" },
    ],
    prompt: "Tap one lantern part. Then tap the small door to carry it through. Move all four parts once.",
    success: { speaker: "Tavi", text: "All four lantern parts went through the small door. Each part moved once, and none was left behind.", audio: "09-tavi-four-once" },
  },
  {
    id: "count", title: "Count what is held", gameTitle: "Count-and-Collect", gameIcon: "👐", background: "e02-stage-07-checking-room-v1.png", cast: ["mira", "tavi", "sol", "pax"], journey: "Step 3 of 4: check that all four parts are safely on the other side.", activity: "count",
    lines: [
      { speaker: "Narrator", text: "Pax held two lantern parts. The other two waited on the tray, so all four were still easy to see.", audio: "22-narrator-pax-holds" },
      { speaker: "Pax", text: "How many parts am I holding? Then tell me how many parts make the whole lantern.", audio: "23-pax-two-counts" },
    ],
    prompt: "Tap each visible lantern part once to count all four. Then answer how many Pax is holding and how many make the whole lantern.",
    success: { speaker: "Sol", text: "Pax is holding two. Four parts make the whole lantern. We have all four, so we can rebuild it.", audio: "24-sol-two-four" },
  },
  {
    id: "gap", title: "Find the missing part", gameTitle: "Gap Repair", gameIcon: "🛠️", background: "e02-stage-07-checking-room-v1.png", cast: ["mira", "tavi", "sol", "pax"], journey: "Step 4 of 4: choose the right parts for the whole lantern.", activity: "gap",
    lines: [
      { speaker: "Narrator", text: "Mia placed three lantern parts in the round frame. One space was still empty. A lantern part and a triangle were nearby.", audio: "19-narrator-gap" },
      { speaker: "Mia", text: "Which piece is part of this lantern? Choose it, turn its top upright, and fit it into the empty space.", audio: "20-mira-gap-extra" },
    ],
    prompt: "Choose the missing lantern part. It starts sideways, so turn it until its top points up, then fit it into the empty space.",
    success: { speaker: "Pax", text: "The lantern part belongs in the gap. The triangle stays outside because it is not part of this lantern.", audio: "21-pax-gap-extra" },
  },
  {
    id: "rebuild", title: "Build the whole again", gameTitle: "Lantern Builder", gameIcon: "🌕", background: "e02-stage-05-rebuild-room-v1.png", cast: ["mira", "tavi", "sol", "pax"], journey: "Finish Step 4: put every lantern part back into the round frame.", activity: "rebuild",
    lines: [
      { speaker: "Narrator", text: "All four lantern parts waited beside the empty round frame.", audio: "13-narrator-four-parts" },
      { speaker: "Mia", text: "Put every part into the frame. Use each part once, and leave none behind.", audio: "14-mira-rebuild" },
    ],
    prompt: "Choose or drag each curved piece into its matching place. Three wrong fits end the round.",
    success: { speaker: "Sol", text: "We did it! All four parts fit together. The same whole lantern is back, and the tray is empty.", audio: "15-sol-whole-again" },
  },
  {
    id: "sum", title: "Light the balcony", gameTitle: "Lantern Sum Builder", gameIcon: "➕", background: "e02-stage-08-balcony-v1.png", cast: ["mira", "tavi", "sol", "pax"], journey: "The four lantern parts reached the balcony. Count them together, then rebuild the whole lantern.", activity: "sum",
    lines: [
      { speaker: "Narrator", text: "The friends reached the balcony before the first evening star. The four lantern parts were still separate. They needed to count the parts together before rebuilding the lantern.", audio: "25-narrator-balcony" },
      { speaker: "Tavi", text: "Put one lantern part in each space. The plus signs mean we are joining the separate counted parts. Then choose how many parts there are altogether.", audio: "26-tavi-remembers" },
    ],
    prompt: "Put one lantern part in each space. Choose the total that makes the equation true. Then join the four parts to rebuild one whole lantern.",
    success: { speaker: "Mia", text: "One part plus one part plus one part plus one part equals four parts. Equals means both sides count the same four parts. Then we joined the four parts and rebuilt one whole lantern. A blue moon picture lit up. Then a gold sun picture lit up. The two pictures began to take turns.", audio: "27-mira-ending" },
  },
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
const endingLesson: Line = { speaker: "Narrator", text: "Here is the lesson. Addition joins separate counted groups without losing or repeating anything. One part plus one part plus one part plus one part equals four parts. The equals sign tells us that both sides count the same four parts. Then we fitted those four parts together to rebuild one whole lantern. This matters because addition helps us check how many things we have altogether, while a parts plan helps us build the whole correctly.", audio: "28-narrator-to-you" };
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
  return <span className={`lantern-quarter lantern-quarter-${part}`} style={{ transform: `rotate(${turned * 90}deg)` }} role="img" aria-label={`lantern part ${part}, one of four same-size parts`}><svg viewBox={viewBoxes[part]} preserveAspectRatio="none"><LanternDrawing /></svg></span>;
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
  const [roundLost, setRoundLost] = useState(false);
  const [round, setRound] = useState(0);
  const [storageReady, setStorageReady] = useState(false);
  const audioRef = useRef<HTMLAudioElement | null>(null);
  const soundRef = useRef<AudioContext | null>(null);
  const lastLineRef = useRef("");
  const progressRef = useRef<Record<string, unknown>>({});

  useEffect(() => {
    try { localStorage.setItem("sft-active-level-v1", "e02"); } catch { /* optional */ }
  }, []);
  const chosenRef = useRef<number[]>([]);

  const scene = scenes[sceneIndex];
  const dialogueDone = beat >= scene.lines.length;
  const line = complete ? scene.success : scene.lines[Math.min(beat, scene.lines.length - 1)];
  const speaking = (!dialogueDone || complete) ? (line?.speaker.toLowerCase() === "mia" ? "mira" : line?.speaker.toLowerCase()) : "";

  useEffect(() => {
    const stopBackgroundAudio = () => {
      if (document.visibilityState !== "hidden") return;
      audioRef.current?.pause();
      audioRef.current = null;
    };
    const stopForPageHide = () => {
      audioRef.current?.pause();
      audioRef.current = null;
    };
    document.addEventListener("visibilitychange", stopBackgroundAudio);
    window.addEventListener("pagehide", stopForPageHide);
    return () => {
      document.removeEventListener("visibilitychange", stopBackgroundAudio);
      window.removeEventListener("pagehide", stopForPageHide);
    };
  }, []);

  useLayoutEffect(() => {
    chosenRef.current = chosen;
    progressRef.current = { sceneIndex, beat, complete, finished, activityStep, chosen, wrong, mistakes, roundLost, round };
  }, [sceneIndex, beat, complete, finished, activityStep, chosen, wrong, mistakes, roundLost, round]);

  useEffect(() => {
    const timeout = window.setTimeout(() => {
      try {
        const saved = JSON.parse(localStorage.getItem("sft-e02-moving-stage-v1") ?? "{}");
        if (typeof saved.sceneIndex === "number") setSceneIndex(Math.min(Math.max(saved.sceneIndex, 0), scenes.length - 1));
        if (typeof saved.beat === "number") setBeat(Math.max(saved.beat, 0));
        if (typeof saved.complete === "boolean") setComplete(saved.complete);
        if (typeof saved.finished === "boolean") setFinished(saved.finished);
        if (typeof saved.activityStep === "number") setActivityStep(Math.max(saved.activityStep, 0));
        if (Array.isArray(saved.chosen)) setChosen(saved.chosen.filter((value: unknown) => typeof value === "number"));
        if (typeof saved.wrong === "string") setWrong(saved.wrong);
        if (typeof saved.mistakes === "number") setMistakes(Math.max(0, Math.min(3, saved.mistakes)));
        if (typeof saved.roundLost === "boolean") setRoundLost(saved.roundLost);
        if (typeof saved.round === "number") setRound(Math.max(0, saved.round));
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
        localStorage.setItem("sft-e02-moving-stage-v1", JSON.stringify(progress));
        localStorage.setItem("sft-active-level-v1", "e02");
      } catch { /* optional */ }
    };
    save();
    const hidden = () => { if (document.visibilityState === "hidden") save(); };
    window.addEventListener("pagehide", save);
    document.addEventListener("visibilitychange", hidden);
    return () => { window.removeEventListener("pagehide", save); document.removeEventListener("visibilitychange", hidden); };
  }, [storageReady, sceneIndex, beat, complete, finished, activityStep, chosen, wrong, mistakes, roundLost, round]);

  useEffect(() => {
    if (!finished || muted) return;
    let lessonAudio: HTMLAudioElement | null = null;
    const timeout = window.setTimeout(() => {
      if (document.visibilityState !== "visible") return;
      audioRef.current?.pause();
      const audio = new Audio(`/audio/e02-v1.0.0/${endingLesson.audio}.mp3?v=e02-story-20260731d`);
      lessonAudio = audio;
      audioRef.current = audio;
      audio.play().catch(() => undefined);
    }, 120);
    return () => {
      window.clearTimeout(timeout);
      lessonAudio?.pause();
      if (audioRef.current === lessonAudio) audioRef.current = null;
    };
  }, [finished, muted]);

  useEffect(() => () => {
    audioRef.current?.pause();
    audioRef.current = null;
  }, []);

  function playLine(current = line) {
    if (!current || muted) return;
    audioRef.current?.pause();
    const audio = new Audio(`/audio/e02-v1.0.0/${current.audio}.mp3?v=e02-story-20260731d`);
    audioRef.current = audio;
    audio.play().catch(() => undefined);
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
    if (!line || (dialogueDone && !complete)) { audioRef.current?.pause(); return; }
    const key = `${sceneIndex}:${complete ? "success" : beat}`;
    const timeout = window.setTimeout(() => {
      if (document.visibilityState !== "visible") return;
      if (lastLineRef.current === key) return;
      lastLineRef.current = key;
      playLine(line);
    }, 25);
    return () => { window.clearTimeout(timeout); audioRef.current?.pause(); };
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [sceneIndex, beat, complete]);

  function finish() { sound("good"); setWrong(""); setMistakes(0); setRoundLost(false); setComplete(true); }
  function wrongTry(message: string) {
    if (roundLost) return;
    sound("wrong"); const next = mistakes + 1; setMistakes(next); setWrong(message);
    if (next >= 3) setRoundLost(true); else window.setTimeout(() => setWrong(""), 2200);
  }
  function retryRound() { sound("step"); setRound((value) => value + 1); setMistakes(0); setRoundLost(false); setWrong(""); setActivityStep(0); setChosen([]); }
  function nextBeat() { sound("tap"); if (beat < scene.lines.length) setBeat((value) => value + 1); }
  function nextScene() {
    sound("step");
    if (sceneIndex === scenes.length - 1) { setFinished(true); return; }
    setSceneIndex((value) => value + 1); setBeat(0); setComplete(false); setActivityStep(0); setChosen([]); setWrong(""); setMistakes(0); setRoundLost(false); lastLineRef.current = "";
  }
  function replay() { audioRef.current?.pause(); setComplete(false); setActivityStep(0); setChosen([]); setWrong(""); setMistakes(0); setRoundLost(false); setRound((value) => value + 1); lastLineRef.current = ""; }
  function restart() {
    audioRef.current?.pause(); setSceneIndex(0); setBeat(0); setComplete(false); setFinished(false); setActivityStep(0); setChosen([]); setWrong(""); setMistakes(0); setRoundLost(false); setRound(0); lastLineRef.current = "";
    try {
      localStorage.removeItem("sft-e02-moving-stage-v1");
      localStorage.setItem("sft-active-level-v1", "e02");
    } catch { /* optional */ }
  }
  function submitCode(event: FormEvent) {
    event.preventDefault(); const clean = code.toUpperCase().replace(/[^A-Z]/g, "");
    setCodeMessage(codes[clean] ?? "That code is hiding on another book page. Keep looking.");
    if (codes[clean]) setCode("");
  }

  function activity() {
    if (complete) return null;
    if (scene.activity === "parcel") {
      const open = [10,11,6,7,2,3,4];
      const current = activityStep || 10;
      const move = (delta: number) => {
        const column = current % 5; const next = current + delta;
        if ((delta === -1 && column === 0) || (delta === 1 && column === 4) || next < 0 || next > 14 || !open.includes(next)) { wrongTry("A book cart blocks that square. Keep the parcel on the glowing floor path."); return; }
        if (next === 10 || chosen.includes(next)) { wrongTry("That square is behind the parcel. Keep moving towards the yellow reading mat."); return; }
        const nextPath=[...chosen,next];setChosen(nextPath);setActivityStep(next);sound("step");if(next===4)window.setTimeout(finish,450);
      };
      return <MiniGame title={scene.gameTitle} icon="📦" progress={`${chosen.length + 1}/${open.length} path squares`}><div className="parcel-path-game"><div className="parcel-path-grid">{Array.from({length:15},(_,cell)=><span key={cell} className={`${open.includes(cell)?"open":"cart"} ${chosen.includes(cell)?"used":""} ${cell===current?"parcel-here":""} ${cell===4?"reading-mat":""}`}>{cell===current?"📦":cell===4?"🟨":open.includes(cell)?"✨":"📚"}<b>{cell===10?"START":cell===4?"READING MAT":""}</b></span>)}</div><div className="parcel-arrows"><button onClick={()=>move(-5)}>↑</button><button onClick={()=>move(-1)}>←</button><button onClick={()=>move(1)}>→</button><button onClick={()=>move(5)}>↓</button></div></div></MiniGame>;
    }
    if (scene.activity === "whole") {
      const inspect = () => { if(chosen.length<4)setChosen([...chosen,chosen.length+1]);sound("tap"); };
      return <MiniGame title={scene.gameTitle} icon="🔎" progress={`${chosen.length}/4 parts revealed`}><div className="lantern-inspector"><button className={`whole-lantern-reveal revealed-${chosen.length}`} onClick={inspect} aria-label={`${chosen.length} of 4 lantern parts revealed. ${chosen.length<4?"Tap to uncover the next part.":"The whole lantern is visible."}`}><span className="lantern-reveal-window" aria-hidden="true"><WholeLantern />{[1,2,3,4].map((part)=><span key={part} className={`lantern-cover cover-${part}`}>?</span>)}</span><b>{chosen.length<4?"Tap to uncover the next part":"The whole lantern is visible"}</b></button><div className="lantern-part-notebook"><strong>PARTS WE CAN SEE</strong>{[1,2,3,4].map((part)=><span key={part} className={chosen.includes(part)?"found":""}>{chosen.includes(part)?<LanternQuarter part={part as 1|2|3|4}/>:"?"}<b>PART {part}</b></span>)}</div><div className="whole-answer"><button disabled={chosen.length<4} onClick={finish}>Every part is here: the whole lantern</button><button disabled={chosen.length<4} onClick={()=>wrongTry("Look at the four notebook spaces. Is any lantern part missing?")}>A lantern part is missing</button><button disabled={chosen.length<4} onClick={()=>wrongTry("Only the four lantern parts are here. Is there an extra object?")}>An extra object is attached</button></div></div></MiniGame>;
    }
    if (scene.activity === "parts") {
      const cardOrder = round % 2 ? [3,1,4,2] : [2,4,1,3];
      const selectedPart = activityStep;
      const placePart = (slot: number) => {
        if (!selectedPart) { setWrong("Choose one lantern-part card first."); window.setTimeout(() => setWrong(""),1400); return; }
        if (selectedPart !== slot) { wrongTry("That curved edge does not match this place. Keep the card and try another place."); return; }
        const next = [...chosen,slot]; setChosen(next); setActivityStep(0); sound("step"); if(next.length===4)window.setTimeout(finish,500);
      };
      return <MiniGame title={scene.gameTitle} icon="🏮" progress={`${chosen.length}/4 plan parts placed`}><div className="plan-workbench"><div className="lantern-plan-frame" aria-label={`${chosen.length} of 4 lantern plan parts placed`}>{[1,2,3,4].map((slot)=><button key={slot} className={`plan-slot plan-slot-${slot} ${chosen.includes(slot)?"filled":""}`} onClick={()=>placePart(slot)} disabled={chosen.includes(slot)} aria-label={chosen.includes(slot)?`Lantern part ${slot} is placed`:`Empty place ${slot}`}>{chosen.includes(slot)?<LanternQuarter part={slot as 1|2|3|4}/>:<span>?</span>}</button>)}</div><div className="plan-card-tray"><strong>LANTERN-PICTURE CARDS</strong>{cardOrder.map((part)=><button key={part} className={selectedPart===part?"selected":""} onClick={()=>{setActivityStep(part);sound("tap");}} disabled={chosen.includes(part)} aria-label={`Choose lantern part ${part}`}><LanternQuarter part={part as 1|2|3|4}/><b>PART {part}</b></button>)}</div><p>{chosen.length===4?"The four parts fill one whole lantern.":selectedPart?`Part ${selectedPart} is ready. Tap its matching place.`:"Choose a picture card."}</p></div></MiniGame>;
    }
    if (scene.activity === "match") {
      const pairOrder = [1,2];
      const selectedPair = activityStep;
      const test = () => {
        if (!selectedPair) {
          setWrong("Choose or drag one pair onto the balance track.");
          window.setTimeout(() => setWrong(""), 1600);
          return;
        }
        if (selectedPair === 1) finish();
        else wrongTry("The track tipped because one part reaches farther. Try the other pair.");
      };
      return <MiniGame title={scene.gameTitle} icon="⚖️" progress={selectedPair ? "Ready to test" : "Choose a pair"}><div className="balance-puzzle"><div className={`balance-track ${selectedPair === 2 ? "tilted" : selectedPair === 1 ? "level" : ""}`} onDragOver={(event) => event.preventDefault()} onDrop={(event) => { event.preventDefault(); setActivityStep(Number(event.dataTransfer.getData("text/plain"))); }}><div className="balance-lantern-load">{selectedPair?<><LanternQuarter part={1}/><span className={selectedPair===2?"small-part":""}><LanternQuarter part={2}/></span></>:<WholeLantern label="whole lantern waiting for a pair test" />}</div><i/><b>{selectedPair ? `Lantern pair ${selectedPair === 1 ? "A" : "B"} on the track` : "Drop a lantern pair here"}</b></div><div className="balance-pairs">{pairOrder.map((pair) => <button key={pair} draggable onDragStart={(event) => event.dataTransfer.setData("text/plain",String(pair))} onClick={() => setActivityStep(pair)} className={selectedPair === pair ? "selected" : ""}><b>PAIR {pair === 1 ? "A" : "B"}</b><span className={`pair-lantern-parts ${pair === 1 ? "same" : "different"}`}><LanternQuarter part={1}/><span className={pair===2?"small-part":""}><LanternQuarter part={2}/></span></span></button>)}</div><button className="test-balance" onClick={test}>Release the lantern-part balance</button></div></MiniGame>;
    }
    if (scene.activity === "bridge") {
      const pieceOrder = round % 2 ? [2,4,1,3] : [3,1,4,2];
      const selectedPart = activityStep;
      const choosePart = (part: number) => {
        if (chosen.includes(part)) { wrongTry(`Lantern part ${part} is already through the door. Choose one still on this side.`); return; }
        setActivityStep(part); sound("tap");
      };
      const carryThrough = () => {
        if (!selectedPart) { setWrong("Choose one lantern part beside the door first."); window.setTimeout(()=>setWrong(""),1500); return; }
        const next=[...chosen,selectedPart];setChosen(next);setActivityStep(0);sound("step");if(next.length===4)window.setTimeout(finish,550);
      };
      return <MiniGame title={scene.gameTitle} icon="🚪" progress={`${chosen.length}/4 lantern parts through`}><div className="doorway-delivery"><section className="delivery-side workshop-side"><strong>WORKSHOP SIDE</strong><div>{pieceOrder.map((part)=><button key={part} className={`${selectedPart===part?"selected":""} ${chosen.includes(part)?"carried":""}`} onClick={()=>choosePart(part)} aria-label={chosen.includes(part)?`Lantern part ${part} has already gone through`:`Choose lantern part ${part}`}><LanternQuarter part={part as 1|2|3|4}/><b>PART {part}</b></button>)}</div></section><button className={`delivery-door ${selectedPart?"ready":""}`} onClick={carryThrough}><span aria-hidden="true">🚪</span><b>{selectedPart ? `Carry part ${selectedPart} through` : "Choose a part"}</b></button><section className="delivery-side arrival-side"><strong>OTHER SIDE</strong><div>{[1,2,3,4].map((part)=><span key={part} className={chosen.includes(part)?"arrived":""}>{chosen.includes(part)?<LanternQuarter part={part as 1|2|3|4}/>:"?"}<b>PART {part}</b></span>)}</div></section></div></MiniGame>;
    }
    if (scene.activity === "count") {
      const countPart = (part: number) => {
        if(chosen.includes(part)){wrongTry(`You already counted lantern part ${part}. Count a part without a number badge.`);return;}
        const next=[...chosen,part];setChosen(next);sound("tap");if(next.length===4)setActivityStep(1);
      };
      const answerHeld = (answer:number) => answer===2 ? (setActivityStep(2),sound("good")) : wrongTry("Look only at Pax's hands. Tap and count the lantern parts he is holding.");
      const answerWhole = (answer:number) => answer===4 ? finish() : wrongTry("Count the two parts in Pax's hands and the two parts on the tray together.");
      return <MiniGame title={scene.gameTitle} icon="👐" progress={activityStep===0?`${chosen.length}/4 parts counted`:activityStep===1?"How many held?":"How many altogether?"}><div className="lantern-count-game"><div className="count-groups"><section><strong>PAX IS HOLDING</strong><div>{[1,2].map((part)=><button key={part} onClick={()=>countPart(part)} className={chosen.includes(part)?"counted":""}><LanternQuarter part={part as 1|2}/>{chosen.includes(part)&&<i>{chosen.indexOf(part)+1}</i>}<b>LANTERN PART {part}</b></button>)}</div></section><section><strong>WAITING ON THE TRAY</strong><div>{[3,4].map((part)=><button key={part} onClick={()=>countPart(part)} className={chosen.includes(part)?"counted":""}><LanternQuarter part={part as 3|4}/>{chosen.includes(part)&&<i>{chosen.indexOf(part)+1}</i>}<b>LANTERN PART {part}</b></button>)}</div></section></div>{activityStep===0?<p>Tap each lantern part once. The number badge shows your count.</p>:<div className="count-question"><strong>{activityStep===1?"How many lantern parts is Pax holding?":"How many lantern parts make the whole lantern?"}</strong><div>{[1,2,3,4].map(answer=><button key={answer} onClick={()=>activityStep===1?answerHeld(answer):answerWhole(answer)}>{answer}</button>)}</div></div>}</div></MiniGame>;
    }
    if (scene.activity === "gap") {
      const pieceOrder = [2,1,3];
      const selected = activityStep; const turns = chosen[0] ?? 0;
      const fitPiece = () => {
        if (!selected) { setWrong("Choose one loose piece first."); window.setTimeout(() => setWrong(""),1500); return; }
        if (selected !== 1 || turns % 4 !== 1) { wrongTry("The piece must be part of the lantern, and its top must point up like the lantern in the frame."); return; }
        finish();
      };
      return <MiniGame title={scene.gameTitle} icon="🛠️" progress={selected ? `${turns} turns` : "Choose piece"}><div className="gap-fit-puzzle"><div className="emoji-lantern-gap"><strong>THE LANTERN</strong><div>{([1,2,3] as const).map(part=><LanternQuarter key={part} part={part}/>)}<span className="empty-quarter">?</span></div><b>One lantern part is missing</b></div><div className="loose-shape-tray">{pieceOrder.map((piece)=><button key={piece} className={selected===piece?"selected":""} onClick={()=>{setActivityStep(piece);setChosen([]);sound("tap");}}>{piece===1?<LanternQuarter part={4} turned={selected===piece?turns-1:-1}/>:<span className="loose-shape">{piece===2?"🔺":"🟦"}</span>}<b>{piece===1?"Lantern part":piece===2?"Triangle":"Blue square"}</b></button>)}</div><div className="gap-tools"><button onClick={()=>selected?setChosen([(turns+1)%4]):setWrong("Choose a piece before turning it.")}>↻ Turn the chosen piece</button><button onClick={fitPiece}>Fit it into the empty space</button></div></div></MiniGame>;
    }
    if (scene.activity === "rebuild") {
      const orders = [[3,1,4,2],[2,4,1,3],[4,2,3,1]];
      const pieceOrder = orders[0];
      const place = (slot: number, piece = activityStep) => {
        if (!piece) { setWrong("Choose or drag a lantern piece first."); window.setTimeout(() => setWrong(""), 1600); return; }
        if (piece !== slot) { wrongTry("That curved edge does not meet this corner. Try a different slot or reset the board."); return; }
        if (chosen.includes(piece)) return;
        const next = [...chosen, piece]; setChosen(next); setActivityStep(0); sound("good");
        if (next.length === 4) window.setTimeout(finish, 500);
      };
      return <MiniGame title={scene.gameTitle} icon={scene.gameIcon} progress={`${chosen.length}/4 fitted`}>
        <div className="lantern-jigsaw"><div className="lantern-frame" aria-label={`${chosen.length} of 4 lantern pieces fitted`}>{[1,2,3,4].map((slot) => <button key={slot} data-slot={slot} className={`jigsaw-slot slot-${slot} ${chosen.includes(slot) ? "filled" : ""}`} onClick={() => place(slot)} onDragOver={(event) => event.preventDefault()} onDrop={(event) => { event.preventDefault(); place(slot, Number(event.dataTransfer.getData("text/plain"))); }} aria-label={`Lantern slot ${slot}`}>{chosen.includes(slot) ? <LanternQuarter part={slot as 1|2|3|4}/> : <span>{slot}</span>}</button>)}</div><div className="jigsaw-tray"><strong>Choose or drag a lantern part</strong>{pieceOrder.map((piece) => <button key={piece} draggable={!chosen.includes(piece)} disabled={chosen.includes(piece)} className={`${activityStep === piece ? "selected" : ""} ${chosen.includes(piece) ? "placed" : ""}`} onClick={() => { sound("tap"); setActivityStep(piece); }} onDragStart={(event) => event.dataTransfer.setData("text/plain", String(piece))}><LanternQuarter part={piece as 1|2|3|4}/><b>Lantern part {piece}</b></button>)}<button className="jigsaw-reset" onClick={retryRound}>Shuffle and reset</button></div></div>
      </MiniGame>;
    }
    if (scene.activity === "sum") {
      const order = round % 2 ? [3, 1, 4, 2] : [2, 4, 1, 3];
      const selectedPart = activityStep > 0 && activityStep < 5 ? activityStep : 0;
      const placeNext = () => {
        if (!selectedPart || chosen.includes(selectedPart)) { setWrong("Choose one lantern part from the tray first."); window.setTimeout(() => setWrong(""), 1500); return; }
        const next = [...chosen, selectedPart]; setChosen(next); sound("step"); setActivityStep(next.length === 4 ? 5 : 0);
      };
      const chooseTotal = (answer: number) => {
        if (answer !== 4) { wrongTry("Count the four filled spaces once. The total must name every lantern part you can see."); return; }
        sound("good"); setWrong(""); setActivityStep(6);
      };
      return <MiniGame title="Lantern Sum Builder" icon="➕" progress={activityStep < 5 ? `${chosen.length}/4 parts placed` : activityStep === 5 ? "Choose the total" : "Equation complete"}>
        <div className={`lantern-sum-game stage-${activityStep}`}>
          <div className="sum-equation" aria-label={chosen.length < 4 ? `${chosen.length} of 4 addition spaces filled` : activityStep < 6 ? "one part plus one part plus one part plus one part equals how many parts" : "one part plus one part plus one part plus one part equals four parts"}>
            {[0,1,2,3].map((slot) => <span className="sum-term" key={slot}>{chosen[slot] ? <><LanternQuarter part={chosen[slot] as 1|2|3|4}/><b>1 PART</b></> : <b>?</b>}</span>)}
            <i className="plus plus-one">+</i><i className="plus plus-two">+</i><i className="plus plus-three">+</i><i className="equals">=</i>
            <span className="sum-total">{activityStep >= 6 ? <><b>4</b><small>PARTS</small></> : <b>?</b>}</span>
          </div>
          {chosen.length < 4 && <><div className="sum-part-tray"><strong>CHOOSE A LANTERN PART</strong>{order.map((part) => <button key={part} disabled={chosen.includes(part)} className={selectedPart === part ? "selected" : ""} onClick={() => { setActivityStep(part); sound("tap"); }}><LanternQuarter part={part as 1|2|3|4}/><b>PART {part}</b></button>)}</div><button className="sum-action" onClick={placeNext}>Put the chosen part in the next space</button></>}
          {activityStep === 5 && <div className="sum-answer"><strong>How many lantern parts are there altogether?</strong><div>{[3,4,5].map((answer) => <button key={answer} onClick={() => chooseTotal(answer)}>{answer}</button>)}</div></div>}
          {activityStep === 6 && <div className="sum-meaning"><p><b>Plus</b> joins the separate counted parts.</p><p><b>Equals</b> says both sides count the same four parts.</p><button onClick={() => { sound("good"); setActivityStep(7); }}>Join the 4 parts</button></div>}
          {activityStep === 7 && <div className="sum-reassembly"><div><LanternQuarter part={1}/><LanternQuarter part={2}/><LanternQuarter part={3}/><LanternQuarter part={4}/></div><span aria-hidden="true">→</span><WholeLantern /><b>4 PARTS → 1 WHOLE LANTERN</b><button onClick={finish}>Light the whole lantern</button></div>}
        </div>
      </MiniGame>;
    }
    return null;
  }

  if (!storageReady) return <main className="restore-screen"><p>Returning to your adventure…</p></main>;

  if (finished) return <main className="ending-screen e02-ending">
    <div className="ending-art" /><button className="ending-home" onClick={onExit} aria-label="Choose a level">⌂ Levels</button><section><p className="eyebrow">LEVEL TWO COMPLETE</p><div className="e02-progress" aria-label="9 of 9 story steps complete">{scenes.map((_, index) => <span className="done" key={index}>●</span>)}</div><h1>The Moon Lantern shines.</h1><p>Mia, Sol, Tavi and Pax solved one clear problem: the whole lantern was too wide for the small door.</p><blockquote>They counted the four separate parts with addition, then fitted those parts together to rebuild one whole lantern.</blockquote><div className="ending-lesson"><span aria-hidden="true">📖</span><div><strong>NARRATOR TO YOU</strong><p>{endingLesson.text}</p></div><button onClick={() => playLine(endingLesson)}>Hear the lesson again</button></div><p className="grownup-boundary"><strong>For grown-ups:</strong> this level uses exact positive finite counts, exact visible parts, and exact addition. It does not introduce zero, fractions, infinity or hidden equivalence.</p><div className="ending-controls"><button className="primary" onClick={onNext}>Next level</button><button className="secondary" onClick={restart}>Play Level 2 again</button><button className="secondary" onClick={onExit}>Choose a level</button></div></section>
  </main>;

  return <main className="game-shell level-two-shell">
    <header className="game-hud e02-hud">
      <div><span className="eyebrow">THE MOON LANTERN WORKSHOP</span><strong>{scene.title}</strong></div>
      <div className="e02-progress" aria-label={`${sceneIndex + (complete ? 1 : 0)} of 9 story steps complete`}>{scenes.map((_, index) => <span key={index} className={index < sceneIndex || (index === sceneIndex && complete) ? "done" : index === sceneIndex ? "now" : ""}>●</span>)}</div>
      <nav><button onClick={onExit} aria-label="Choose a level">⌂ <span>Levels</span></button><button onClick={() => playLine()} aria-label="Replay narration">↻ <span>Hear again</span></button><button onClick={() => setMuted((value) => !value)} aria-pressed={muted}>{muted ? "🔇" : "🔊"} <span>{muted ? "Narration off" : "Narration on"}</span></button><button onClick={() => setCodesOpen(true)}>⌨ <span>Book code</span></button></nav>
    </header>
    <section key={scene.id} className={`play-stage e02-stage scene-e02-${scene.id}`} style={{ backgroundImage: `url('/art/stages/${scene.background}')` }} aria-label={`${scene.title}, an animated Moon Lantern story scene`}>
      <div className="stage-light" />
      {beat === 0 && scene.journey && <div className="journey-banner"><span aria-hidden="true">→</span><strong>{scene.journey}</strong></div>}
      {scene.introduces && beat <= 1 && <div className="guest-banner">New friend for Level Two: <strong>{names[scene.introduces]}</strong></div>}
      <div className="walking-cast" aria-hidden="true">{scene.cast.map((name, index) => <CharacterSprite key={name} name={name} index={index} speaking={speaking === name} />)}</div>
      {scene.id === "parcel" && !dialogueDone && <div className="story-parcel" aria-label="parcel beside the map"><span aria-hidden="true">📦</span><b>PARCEL</b></div>}
      {dialogueDone && !complete && <div className="activity-layer"><TryLights mistakes={mistakes}/>{!roundLost && activity()}{wrong && <p className="e02-feedback" role="status">{wrong}</p>}{roundLost && <section className="round-lost" role="alert"><span aria-hidden="true">◆ ◆ ◆</span><h2>Round over</h2><p>That round used all three try lights. The story is safe. Change your plan and try this puzzle again.</p><button onClick={retryRound}>Try again</button></section>}</div>}
      <aside className={`speech-panel ${dialogueDone && !complete ? "prompting" : ""} ${complete ? "completed" : ""}`} aria-live="polite">
        {!dialogueDone || complete ? <><div className="speaker-portrait"><Portrait speaker={line.speaker} /></div><span className="speaker">{line.speaker}</span><p>{line.text}</p>{complete ? <div className="completion-controls"><button className="replay-control" onClick={replay}><span aria-hidden="true">↻</span> Play again</button><button className="next-control" onClick={nextScene}>{sceneIndex === scenes.length - 1 ? "Light the lantern" : "Follow the plan"} <span aria-hidden="true">→</span></button></div> : <button className="next-control" onClick={nextBeat}>Next <span aria-hidden="true">→</span></button>}</> : <><div className="speaker-portrait prompt-portrait" aria-hidden="true">☝️</div><span className="speaker">YOUR TURN</span><p>{scene.prompt}</p><span className="action-nudge" aria-hidden="true">↑ Try it in the scene</span></>}
      </aside>
    </section>
    <button className="restart-corner" onClick={restart}>Start over</button>
    {codesOpen && <div className="modal-backdrop" role="presentation" onMouseDown={() => setCodesOpen(false)}><section className="code-modal" role="dialog" aria-modal="true" aria-labelledby="e02-code-title" onMouseDown={(event) => event.stopPropagation()}><button className="close-modal" onClick={() => setCodesOpen(false)} aria-label="Close">×</button><p className="eyebrow">OPTIONAL BOOK SECRET</p><h2 id="e02-code-title">Mia’s code pocket</h2><p>Codes unlock jokes and small previews. They never give an answer or skip a lesson.</p><form onSubmit={submitCode}><label htmlFor="e02-book-code">Code from Book Two</label><div><input id="e02-book-code" value={code} onChange={(event) => setCode(event.target.value)} autoComplete="off" /><button>Open</button></div></form><p className="code-result" aria-live="polite">{codeMessage}</p></section></div>}
  </main>;
}
