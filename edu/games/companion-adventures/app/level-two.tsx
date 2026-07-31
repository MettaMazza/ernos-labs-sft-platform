"use client";

import { CSSProperties, FormEvent, ReactNode, useEffect, useLayoutEffect, useRef, useState } from "react";

type Character = "mira" | "tavi" | "sol" | "pax";
type Activity = "parcel" | "whole" | "bridge" | "parts" | "rebuild" | "match" | "gap" | "count" | "recall";
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
      { speaker: "Narrator", text: "The parcel from the last adventure rolled down the library ramp. Mira picked it up.", audio: "01-narrator-new-parcel" },
      { speaker: "Mira", text: "It has our names on it! Let’s open it and see what is inside.", audio: "02-mira-open-parcel" },
    ],
    prompt: "Catch the rolling parcel, undo its three ribbons, lift the lid, and find the card.",
    success: { speaker: "Tavi", text: "A Moon Lantern! The card asks us to take it to the balcony before the first evening star.", audio: "03-tavi-reads-card" },
  },
  {
    id: "whole", title: "The small door", gameTitle: "Lantern Detective", gameIcon: "🔎", background: "e02-stage-02-whole-room-v1.png", cast: ["mira", "tavi", "sol", "pax"], journey: "Mission: get the whole lantern through the small door, then take it to the balcony.", introduces: "pax", activity: "whole",
    lines: [
      { speaker: "Narrator", text: "The friends followed the card towards the balcony. A small door blocked the way. The lantern was too wide to fit through it.", audio: "04-narrator-workshop-door" },
      { speaker: "Pax", text: "Hello! I’m Pax. We can take the lantern apart, carry every part through, and build the whole lantern again. First, let’s look at the whole lantern.", audio: "05-pax-meets" },
    ],
    prompt: "Find the whole lantern. Then inspect all three clues: every part, no gap, and no extra piece.",
    success: { speaker: "Mira", text: "That is our whole lantern. Every part is here, with no gap and no extra piece. Now we know what we must build again.", audio: "06-mira-whole" },
  },
  {
    id: "parts", title: "Choose the four-part plan", gameTitle: "Fit-the-Circle Lab", gameIcon: "🧩", background: "e02-stage-04-part-gate-v1.png", cast: ["mira", "tavi", "sol", "pax"], journey: "Step 1 of 4: choose parts that fill the whole lantern.", activity: "parts",
    lines: [
      { speaker: "Narrator", text: "Pax showed three plans for taking the round lantern apart.", audio: "10-narrator-next-door" },
      { speaker: "Pax", text: "We need four same-size parts that fill the whole circle. There must be no gap, and no part can sit on top of another.", audio: "11-pax-find-parts" },
    ],
    prompt: "Choose the plan with four same-size parts. Then fit its four pieces into the circle.",
    success: { speaker: "Pax", text: "That plan gives us four clear parts. Together, they fill the same whole circle.", audio: "12-pax-parts-fit" },
  },
  {
    id: "match", title: "Check the sizes", gameTitle: "Twin-Part Test", gameIcon: "📏", background: "e02-stage-06-match-table-v1.png", cast: ["mira", "tavi", "sol", "pax"], journey: "Step 1 continued: check what ‘same size’ looks like before Pax uses the plan.", activity: "match",
    lines: [
      { speaker: "Narrator", text: "Pax put two pairs of practice parts on the table.", audio: "16-narrator-two-pairs" },
      { speaker: "Tavi", text: "One pair has parts that are the same size. Look at both pairs before you choose.", audio: "17-tavi-check-pairs" },
    ],
    prompt: "Find the same-size pair. Then measure both parts to prove they match.",
    success: { speaker: "Tavi", text: "Pair A has same-size parts. Pair B has one big part and one small part. Now we can check Pax’s plan.", audio: "18-tavi-same-size" },
  },
  {
    id: "bridge", title: "Carry every part", gameTitle: "Doorway Delivery", gameIcon: "🚪", background: "e02-stage-03-count-bridge-v1.png", cast: ["mira", "tavi", "sol", "pax"], journey: "Step 2 of 4: Pax separates the lantern. Carry all four parts through the small door.", activity: "bridge",
    lines: [
      { speaker: "Narrator", text: "The lantern came apart into four pieces. Four glowing carrying spots showed the way through the small door.", audio: "07-narrator-four-tiles" },
      { speaker: "Sol", text: "I checked one spot twice. That could make us think we carried a part twice. Can you use every spot once?", audio: "08-sol-twice" },
    ],
    prompt: "Pick one lantern part, then choose one empty carrying spot. Carry every part through once.",
    success: { speaker: "Tavi", text: "Four different spots, one time each. All four lantern parts made it through. None was left behind.", audio: "09-tavi-four-once" },
  },
  {
    id: "count", title: "Count what is held", gameTitle: "Count-and-Collect", gameIcon: "👐", background: "e02-stage-07-checking-room-v1.png", cast: ["mira", "tavi", "sol", "pax"], journey: "Step 3 of 4: check that all four parts are safely on the other side.", activity: "count",
    lines: [
      { speaker: "Narrator", text: "Pax held two lantern parts. The other two waited on the tray, so all four were still easy to see.", audio: "22-narrator-pax-holds" },
      { speaker: "Pax", text: "How many parts am I holding? Then tell me how many parts make the whole lantern.", audio: "23-pax-two-counts" },
    ],
    prompt: "Collect the two parts in Pax’s hands. Then collect the other two and count all four.",
    success: { speaker: "Sol", text: "Pax is holding two. Four parts make the whole lantern. We have all four, so we can rebuild it.", audio: "24-sol-two-four" },
  },
  {
    id: "gap", title: "Find the missing part", gameTitle: "Gap Repair", gameIcon: "🛠️", background: "e02-stage-07-checking-room-v1.png", cast: ["mira", "tavi", "sol", "pax"], journey: "Step 4 of 4: choose the right parts for the whole lantern.", activity: "gap",
    lines: [
      { speaker: "Narrator", text: "Mira placed three lantern parts in the round frame. One space was still empty. A lantern part and a triangle were nearby.", audio: "19-narrator-gap" },
      { speaker: "Mira", text: "Which piece belongs in the empty space? Choose it, and keep the piece that does not belong outside.", audio: "20-mira-gap-extra" },
    ],
    prompt: "Fit the lantern part, tap three repair sparks, then move the extra triangle outside.",
    success: { speaker: "Pax", text: "The lantern part belongs in the gap. The triangle stays outside because it is not part of this lantern.", audio: "21-pax-gap-extra" },
  },
  {
    id: "rebuild", title: "Build the whole again", gameTitle: "Lantern Builder", gameIcon: "🌕", background: "e02-stage-05-rebuild-room-v1.png", cast: ["mira", "tavi", "sol", "pax"], journey: "Finish Step 4: put every lantern part back into the round frame.", activity: "rebuild",
    lines: [
      { speaker: "Narrator", text: "All four lantern parts waited beside the empty round frame.", audio: "13-narrator-four-parts" },
      { speaker: "Mira", text: "Put every part into the frame. Use each part once, and leave none behind.", audio: "14-mira-rebuild" },
    ],
    prompt: "Fit all four parts into the frame. Then wake its four lights.",
    success: { speaker: "Sol", text: "We did it! All four parts fit together. The same whole lantern is back, and the tray is empty.", audio: "15-sol-whole-again" },
  },
  {
    id: "recall", title: "The balcony", gameTitle: "Memory Moonwalk", gameIcon: "👣", background: "e02-stage-08-balcony-v1.png", cast: ["mira", "tavi", "sol", "pax"], journey: "The plan worked: the whole lantern went through the small door and reached the balcony.", activity: "recall",
    lines: [
      { speaker: "Narrator", text: "The friends reached the balcony before the first evening star. Tavi asked one last question about their journey.", audio: "25-narrator-balcony" },
      { speaker: "Tavi", text: "What did Sol do when we were checking the four carrying spots? Choose what you remember. Then put the lantern on its stand.", audio: "26-tavi-remembers" },
    ],
    prompt: "Remember Sol’s first try, cross the four memory stones in order, and place the lantern on its stand.",
    success: { speaker: "Mira", text: "Sol checked one spot twice. Then we counted each part once. We took the whole apart, carried every part, and built the whole again!", audio: "27-mira-ending" },
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

const names: Record<Character, string> = { mira: "Mira", tavi: "Tavi", sol: "Sol", pax: "Pax" };
const image = (name: Character) => name === "mira" || name === "pax"
  ? "/art/characters/individual/" + name + "-v1.png"
  : "/art/characters/individual/" + name + ".png";

function CharacterSprite({ name, speaking, index }: { name: Character; speaking: boolean; index: number }) {
  return <div className={`actor actor-${name} ${speaking ? "speaking" : ""}`} style={{ "--actor-index": index } as CSSProperties}>
    <img src={image(name)} alt="" draggable={false} /><span>{names[name]}</span>
  </div>;
}

function Portrait({ speaker }: { speaker: string }) {
  const id = speaker.toLowerCase() as Character;
  if (!(id in names)) return <span className="narrator-portrait" aria-hidden="true">📖</span>;
  return <img className={`portrait-${id}`} src={image(id)} alt="" aria-hidden="true" />;
}

function Moon({ kind, label }: { kind: "gap" | "whole" | "extra" | "unequal"; label: string }) {
  return <span className={`e02-moon moon-${kind}`}><i aria-hidden="true" /><b>{label}</b></span>;
}

function MiniGame({ title, icon, progress, children }: { title: string; icon: string; progress: string; children: ReactNode }) {
  return <section className="e02-mini-game" aria-label={`${title} mini-game`}>
    <header className="mini-game-header"><span aria-hidden="true">{icon}</span><div><small>MINI-GAME</small><strong>{title}</strong></div><b>{progress}</b></header>
    {children}
  </section>;
}

export default function LevelTwo({ onExit }: { onExit: () => void }) {
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
  const [storageReady, setStorageReady] = useState(false);
  const audioRef = useRef<HTMLAudioElement | null>(null);
  const soundRef = useRef<AudioContext | null>(null);
  const lastLineRef = useRef("");
  const progressRef = useRef<Record<string, unknown>>({});

  const scene = scenes[sceneIndex];
  const dialogueDone = beat >= scene.lines.length;
  const line = complete ? scene.success : scene.lines[Math.min(beat, scene.lines.length - 1)];
  const speaking = (!dialogueDone || complete) ? line?.speaker.toLowerCase() : "";

  useLayoutEffect(() => {
    progressRef.current = { sceneIndex, beat, complete, finished, activityStep, chosen, wrong };
  }, [sceneIndex, beat, complete, finished, activityStep, chosen, wrong]);

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
        localStorage.setItem("sft-active-level-v1", progress.finished === true ? "select" : "e02");
      } catch { /* optional */ }
    };
    save();
    const hidden = () => { if (document.visibilityState === "hidden") save(); };
    window.addEventListener("pagehide", save);
    document.addEventListener("visibilitychange", hidden);
    return () => { window.removeEventListener("pagehide", save); document.removeEventListener("visibilitychange", hidden); };
  }, [storageReady, sceneIndex, beat, complete, finished, activityStep, chosen, wrong]);

  function playLine(current = line) {
    if (!current || muted) return;
    audioRef.current?.pause();
    const audio = new Audio(`/audio/e02-v1.0.0/${current.audio}.mp3`);
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
      if (lastLineRef.current === key) return;
      lastLineRef.current = key;
      playLine(line);
    }, 25);
    return () => { window.clearTimeout(timeout); audioRef.current?.pause(); };
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [sceneIndex, beat, complete]);

  function finish() { sound("good"); setWrong(""); setComplete(true); }
  function wrongTry(message: string) { sound("wrong"); setWrong(message); window.setTimeout(() => setWrong(""), 2200); }
  function nextBeat() { sound("tap"); if (beat < scene.lines.length) setBeat((value) => value + 1); }
  function nextScene() {
    sound("step");
    if (sceneIndex === scenes.length - 1) { setFinished(true); return; }
    setSceneIndex((value) => value + 1); setBeat(0); setComplete(false); setActivityStep(0); setChosen([]); setWrong(""); lastLineRef.current = "";
  }
  function replay() { audioRef.current?.pause(); setComplete(false); setActivityStep(0); setChosen([]); setWrong(""); lastLineRef.current = ""; }
  function restart() {
    audioRef.current?.pause(); setSceneIndex(0); setBeat(0); setComplete(false); setFinished(false); setActivityStep(0); setChosen([]); setWrong(""); lastLineRef.current = "";
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

  function addOnce(value: number, total: number, onDone: () => void = finish) {
    if (chosen.includes(value)) { wrongTry("You already used that one. Choose a different one."); return; }
    const next = [...chosen, value]; setChosen(next); sound("tap");
    if (next.length === total) window.setTimeout(onDone, 350);
  }

  function activity() {
    if (complete) return null;
    if (scene.activity === "parcel") return <MiniGame title={scene.gameTitle} icon={scene.gameIcon} progress={activityStep === 0 ? "Catch" : activityStep === 1 ? `${chosen.length}/3 ribbons` : activityStep === 2 ? "Lift" : "Discover"}>
      <div className="e02-parcel-game">
        {activityStep === 0 && <button className="e02-big-prop parcel-rolling pulse" onClick={() => { sound("good"); setActivityStep(1); setChosen([]); }}><span aria-hidden="true">📦</span><b>Catch the parcel!</b></button>}
        {activityStep === 1 && <div className="e02-ribbon-board"><span aria-hidden="true">🎁</span><strong>Undo every ribbon</strong><div>{["Red", "Blue", "Gold"].map((label, index) => <button key={label} disabled={chosen.includes(index + 1)} className={chosen.includes(index + 1) ? "used" : "pulse"} onClick={() => addOnce(index + 1, 3, () => { sound("good"); setChosen([]); setActivityStep(2); })}>{chosen.includes(index + 1) ? "✓" : "🎀"}<b>{label}</b></button>)}</div></div>}
        {activityStep === 2 && <button className="e02-big-prop pulse" onClick={() => { sound("good"); setActivityStep(3); }}><span aria-hidden="true">🎁</span><b>Lift the lid</b></button>}
        {activityStep === 3 && <button className="e02-card-prop pulse" onClick={finish}><span aria-hidden="true">💌</span><b>Read the card</b></button>}
      </div>
    </MiniGame>;
    if (scene.activity === "whole") return <MiniGame title={scene.gameTitle} icon={scene.gameIcon} progress={activityStep === 0 ? "Find" : `${chosen.length}/3 clues`}>
      {activityStep === 0 ? <div className="e02-choice-row whole-choices">
        <button onClick={() => wrongTry("That lantern has a gap. Look for every part.")}><Moon kind="gap" label="A · Has a gap" /></button>
        <button className="pulse" onClick={() => { sound("good"); setChosen([]); setActivityStep(1); }}><Moon kind="whole" label="B · Every part" /></button>
        <button onClick={() => wrongTry("That lantern has an extra piece. Look again.")}><Moon kind="extra" label="C · Extra piece" /></button>
      </div> : <div className="e02-inspection-game"><Moon kind="whole" label="Inspect the whole" /><div>{["Every part", "No gap", "No extra"].map((label, index) => <button key={label} disabled={chosen.includes(index + 1)} className={chosen.includes(index + 1) ? "used" : "pulse"} onClick={() => addOnce(index + 1, 3)}><span aria-hidden="true">{chosen.includes(index + 1) ? "⭐" : "🔎"}</span><b>{label}</b></button>)}</div></div>}
    </MiniGame>;
    if (scene.activity === "parts") return <MiniGame title={scene.gameTitle} icon={scene.gameIcon} progress={activityStep === 0 ? "Choose" : `${chosen.length}/4 fitted`}>
      {activityStep === 0 ? <div className="e02-choice-row parts-choices">
        <button onClick={() => wrongTry("A space is empty. That leaves a gap.")}><Moon kind="gap" label="A · Gap" /></button>
        <button onClick={() => wrongTry("Two parts are on top of each other.")}><Moon kind="unequal" label="B · Parts overlap" /></button>
        <button className="pulse" onClick={() => { sound("good"); setChosen([]); setActivityStep(1); }}><Moon kind="whole" label="C · Four fit" /></button>
      </div> : <div className="e02-fit-lab"><div className={`e02-build-circle filled-${chosen.length}`}><span>{chosen.length} / 4</span></div><div className="e02-piece-tray">{[1,2,3,4].map((value) => <button key={value} disabled={chosen.includes(value)} className={chosen.includes(value) ? "placed" : "pulse"} onClick={() => addOnce(value, 4)} aria-label={`Fit part ${value}`}><span aria-hidden="true">◔</span><b>Fit part {value}</b></button>)}</div></div>}
    </MiniGame>;
    if (scene.activity === "match") return <MiniGame title={scene.gameTitle} icon={scene.gameIcon} progress={activityStep === 0 ? "Compare" : `${chosen.length}/2 measured`}>
      {activityStep === 0 ? <div className="e02-pairs">
        <button className="pulse" onClick={() => { sound("good"); setChosen([]); setActivityStep(1); }}><b>Pair A</b><span><i className="half" /><i className="half" /></span><small>Check these parts</small></button>
        <button onClick={() => wrongTry("One part is big and one is small. Check the other pair.")}><b>Pair B</b><span><i className="big" /><i className="small" /></span><small>Check these parts</small></button>
      </div> : <div className="e02-measure-board"><div className="measure-track"><i /><i /></div><strong>Measure both equal parts</strong><div>{[1,2].map((value) => <button key={value} disabled={chosen.includes(value)} className={chosen.includes(value) ? "used" : "pulse"} onClick={() => addOnce(value, 2)}><span aria-hidden="true">{chosen.includes(value) ? "✓" : "📏"}</span><b>{value === 1 ? "Left part" : "Right part"}</b></button>)}</div></div>}
    </MiniGame>;
    if (scene.activity === "bridge") {
      const hasNewCarrySave = chosen.some((value) => value > 10);
      const usedSpots = chosen.filter((value) => value > 0 && value < 10);
      const deliveredParts = hasNewCarrySave ? chosen.filter((value) => value > 10).map((value) => value - 10) : usedSpots;
      return <MiniGame title={scene.gameTitle} icon={scene.gameIcon} progress={`${deliveredParts.length}/4 delivered`}>
        <div className="e02-carry-game"><div className="carry-parts"><strong>1. Pick a part</strong>{[1,2,3,4].map((value) => <button key={value} disabled={deliveredParts.includes(value)} className={deliveredParts.includes(value) ? "delivered" : activityStep === value ? "selected" : "pulse"} onClick={() => { sound("tap"); setActivityStep(value); }}><span aria-hidden="true">{deliveredParts.includes(value) ? "✓" : "◔"}</span><b>Part {value}</b></button>)}</div><div className="carry-door"><span aria-hidden="true">🚪</span><strong>2. Choose an empty spot</strong><div>{[1,2,3,4].map((value) => <button key={value} disabled={usedSpots.includes(value)} className={usedSpots.includes(value) ? "used" : activityStep ? "pulse" : ""} onClick={() => {
          if (!activityStep) { wrongTry("Pick one lantern part first."); return; }
          if (usedSpots.includes(value)) { wrongTry("That spot already carried a part. Choose an empty spot."); return; }
          const base = hasNewCarrySave ? chosen : [...chosen, ...chosen.map((item) => item + 10)];
          const next = [...base, value, activityStep + 10]; setChosen(next); setActivityStep(0); sound("good");
          if (usedSpots.length + 1 === 4) window.setTimeout(finish, 420);
        }}><span aria-hidden="true">{usedSpots.includes(value) ? "👣" : value}</span><b>Spot {value}</b></button>)}</div></div></div>
      </MiniGame>;
    }
    if (scene.activity === "count") return <MiniGame title={scene.gameTitle} icon={scene.gameIcon} progress={`${chosen.length}/4 collected`}>
      <div className="e02-collect-zones"><section><strong>Pax’s hands</strong><div>{[1,2].map((value) => <button key={value} disabled={chosen.includes(value)} className={chosen.includes(value) ? "collected" : "pulse"} onClick={() => addOnce(value, 2, () => { sound("good"); setActivityStep(1); })}><span aria-hidden="true">{chosen.includes(value) ? "✓" : "◔"}</span><b>Part {value}</b></button>)}</div><small>Find both held parts</small></section><section className={activityStep === 0 ? "locked" : ""}><strong>The tray</strong><div>{[3,4].map((value) => <button key={value} disabled={activityStep === 0 || chosen.includes(value)} className={chosen.includes(value) ? "collected" : activityStep ? "pulse" : ""} onClick={() => addOnce(value, 4)}><span aria-hidden="true">{chosen.includes(value) ? "✓" : "◔"}</span><b>Part {value}</b></button>)}</div><small>{activityStep === 0 ? "Collect Pax’s two first" : "Now make all four"}</small></section></div>
    </MiniGame>;
    if (scene.activity === "gap") return <MiniGame title={scene.gameTitle} icon={scene.gameIcon} progress={activityStep === 0 ? "Choose" : activityStep === 1 ? `${chosen.length}/3 sparks` : "Clear extra"}>
      <div className="e02-gap-game"><div className={`e02-gap-lantern ${activityStep > 0 ? "filled" : ""}`}><span>{activityStep > 0 ? "🌕" : "◕"}</span><b>{activityStep > 0 ? "Gap filled" : "One empty space"}</b></div>
      {activityStep === 0 ? <div className="e02-loose-parts"><button className="pulse" onClick={() => { sound("good"); setChosen([]); setActivityStep(1); }}><span aria-hidden="true">◔</span><b>Lantern part</b></button><button onClick={() => wrongTry("The triangle does not fit the gap.")}><span aria-hidden="true">🔺</span><b>Triangle</b></button></div> : activityStep === 1 ? <div className="repair-sparks">{[1,2,3].map((value) => <button key={value} disabled={chosen.includes(value)} className={chosen.includes(value) ? "used" : "pulse"} onClick={() => addOnce(value, 3, () => { sound("good"); setChosen([]); setActivityStep(2); })} aria-label={`Repair spark ${value}`}>{chosen.includes(value) ? "✓" : "✨"}</button>)}</div> : <button className="e02-extra pulse" onClick={finish}><span aria-hidden="true">🔺</span><b>Move the extra outside</b></button>}
      </div>
    </MiniGame>;
    if (scene.activity === "rebuild") {
      const placed = activityStep === 0 ? chosen.length : 4;
      return <MiniGame title={scene.gameTitle} icon={scene.gameIcon} progress={activityStep === 0 ? `${chosen.length}/4 parts` : `${chosen.length}/4 lights`}>
        <div className="e02-rebuild"><div className={`e02-build-circle filled-${placed}`} aria-label={`${placed} of 4 parts placed`}>{placed === 4 ? "🌕" : <span>{placed} / 4</span>}</div>{activityStep === 0 ? <div className="e02-piece-tray">{[1,2,3,4].map((value) => <button key={value} disabled={chosen.includes(value)} className={chosen.includes(value) ? "placed" : "pulse"} onClick={() => addOnce(value, 4, () => { sound("good"); setChosen([]); setActivityStep(1); })} aria-label={`Place part ${value}`}><span aria-hidden="true">◔</span><b>Part {value}</b></button>)}</div> : <div className="lantern-lights">{[1,2,3,4].map((value) => <button key={value} disabled={chosen.includes(value)} className={chosen.includes(value) ? "used" : "pulse"} onClick={() => addOnce(value, 4)} aria-label={`Wake light ${value}`}>{chosen.includes(value) ? "⭐" : "✦"}<b>Light {value}</b></button>)}</div>}</div>
      </MiniGame>;
    }
    if (scene.activity === "recall") return <MiniGame title={scene.gameTitle} icon={scene.gameIcon} progress={activityStep === 0 ? "Remember" : activityStep === 1 ? `${chosen.length}/4 stones` : "Place lantern"}>
      <div className="e02-recall-game">{activityStep === 0 ? <div className="recall-choices"><button onClick={() => wrongTry("Look back in your mind. Did Sol leave a spot untouched?")}><b>A · Missed one spot</b><span className="footprint-row"><i>—</i><i>👣</i><i>👣</i><i>👣</i></span></button><button className="pulse" onClick={() => { sound("good"); setChosen([]); setActivityStep(1); }}><b>B · One spot twice</b><span className="footprint-row"><i>👣</i><i>👣👣</i><i>👣</i><i>👣</i></span></button><button onClick={() => wrongTry("That is what you did. What happened on Sol’s first try?")}><b>C · Each spot once</b><span className="footprint-row"><i>👣</i><i>👣</i><i>👣</i><i>👣</i></span></button></div> : activityStep === 1 ? <div className="memory-stones"><strong>Cross in order: 1, 2, 3, 4</strong><div>{[1,2,3,4].map((value) => <button key={value} disabled={chosen.includes(value)} className={chosen.includes(value) ? "used" : chosen.length + 1 === value ? "pulse" : ""} onClick={() => {
          if (value !== chosen.length + 1) { wrongTry(`Stone ${chosen.length + 1} comes next.`); return; }
          const next = [...chosen, value]; setChosen(next); sound("tap"); if (next.length === 4) window.setTimeout(() => { sound("good"); setChosen([]); setActivityStep(2); }, 350);
        }}><span aria-hidden="true">{chosen.includes(value) ? "👣" : value}</span><b>Stone {value}</b></button>)}</div></div> : <button className="e02-lantern-stand pulse" onClick={finish}><b>Put the lantern on its stand</b><span aria-hidden="true">🌕</span></button>}</div>
    </MiniGame>;
    return null;
  }

  if (!storageReady) return <main className="restore-screen"><p>Returning to your adventure…</p></main>;

  if (finished) return <main className="ending-screen e02-ending">
    <div className="ending-art" /><button className="ending-home" onClick={onExit} aria-label="Choose a level">⌂ Levels</button><section><p className="eyebrow">LEVEL TWO COMPLETE</p><div className="e02-progress" aria-label="9 of 9 story steps complete">{scenes.map((_, index) => <span className="done" key={index}>●</span>)}</div><h1>The Moon Lantern shines.</h1><p>Mira, Sol, Tavi and Pax solved one clear problem: the whole lantern was too wide for the small door.</p><blockquote>They checked the whole, took it apart, carried every part, and built the same whole again.</blockquote><p className="grownup-boundary"><strong>For grown-ups:</strong> this level uses exact positive finite counts and exact visible parts only. It does not introduce zero, fractions, infinity or hidden equivalence.</p><div className="ending-controls"><button className="primary" onClick={restart}>Play Level 2 again</button><button className="secondary" onClick={onExit}>Choose a level</button></div></section>
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
      {dialogueDone && !complete && <div className="activity-layer">{activity()}{wrong && <p className="e02-feedback" role="status">{wrong}</p>}</div>}
      <aside className={`speech-panel ${dialogueDone && !complete ? "prompting" : ""} ${complete ? "completed" : ""}`} aria-live="polite">
        {!dialogueDone || complete ? <><div className="speaker-portrait"><Portrait speaker={line.speaker} /></div><span className="speaker">{line.speaker}</span><p>{line.text}</p>{complete ? <div className="completion-controls"><button className="replay-control" onClick={replay}><span aria-hidden="true">↻</span> Play again</button><button className="next-control" onClick={nextScene}>{sceneIndex === scenes.length - 1 ? "Light the lantern" : "Follow the plan"} <span aria-hidden="true">→</span></button></div> : <button className="next-control" onClick={nextBeat}>Next <span aria-hidden="true">→</span></button>}</> : <><div className="speaker-portrait prompt-portrait" aria-hidden="true">☝️</div><span className="speaker">YOUR TURN</span><p>{scene.prompt}</p><span className="action-nudge" aria-hidden="true">↑ Try it in the scene</span></>}
      </aside>
    </section>
    <button className="restart-corner" onClick={restart}>Start over</button>
    {codesOpen && <div className="modal-backdrop" role="presentation" onMouseDown={() => setCodesOpen(false)}><section className="code-modal" role="dialog" aria-modal="true" aria-labelledby="e02-code-title" onMouseDown={(event) => event.stopPropagation()}><button className="close-modal" onClick={() => setCodesOpen(false)} aria-label="Close">×</button><p className="eyebrow">OPTIONAL BOOK SECRET</p><h2 id="e02-code-title">Mira’s code pocket</h2><p>Codes unlock jokes and small previews. They never give an answer or skip a lesson.</p><form onSubmit={submitCode}><label htmlFor="e02-book-code">Code from Book Two</label><div><input id="e02-book-code" value={code} onChange={(event) => setCode(event.target.value)} autoComplete="off" /><button>Open</button></div></form><p className="code-result" aria-live="polite">{codeMessage}</p></section></div>}
  </main>;
}
