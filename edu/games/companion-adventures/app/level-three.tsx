"use client";
/* eslint-disable react-hooks/refs -- refs are read only inside event handlers and effects */

import { CSSProperties, FormEvent, PointerEvent as ReactPointerEvent, ReactNode, useEffect, useLayoutEffect, useRef, useState } from "react";

type Character = "mira" | "tavi" | "sol" | "vee";
type Activity = "trail" | "sides" | "turn" | "return" | "continue" | "repair" | "bridge" | "routes" | "transfer";
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
    id: "trail", title: "The garden path goes dark", gameTitle: "Moon-and-Sun Catch", gameIcon: "✨", background: "e03-source/e03-stage-01-trail-station-v1.png", cast: ["mira", "tavi", "sol"], journey: "The Moon Lantern sends a line of light from the balcony into the garden.", activity: "trail",
    lines: [
      { speaker: "Narrator", text: "The Moon Lantern shone on the balcony. A blue moon picture lit up, then a gold sun picture. The two lights jumped onto the garden path. Then the path went dark.", audio: "01-narrator-trail-stops" },
      { speaker: "Mia", text: "The Sunrise Arch is at the far end of the garden. Its light helps everyone find the garden gate in the morning. Let’s catch the moon and sun lights so we can see how the path should work.", audio: "02-mira-catch-lights" },
    ],
    prompt: "Move the catcher below the falling light, then catch it. Three missed catches end the round.",
    success: { speaker: "Tavi", text: "We caught blue moon, gold sun, blue moon, gold sun. They took turns. Now we can follow the dark path and find out why it stopped.", audio: "03-tavi-four-lights" },
  },
  {
    id: "sides", title: "Vee and the turning tile", gameTitle: "Two-Side Camera", gameIcon: "📷", background: "e03-source/e03-stage-02-turn-gate-v1.png", cast: ["mira", "tavi", "sol", "vee"], journey: "The friends follow the dark stones to a gate that turns the path tiles.", introduces: "vee", activity: "sides",
    lines: [
      { speaker: "Narrator", text: "Mia, Sol and Tavi followed the dark stones to a turning gate. Vee hurried over with one round path tile.", audio: "04-narrator-meet-vee" },
      { speaker: "Vee", text: "Hello! I’m Vee. I look after this path. One side of my tile has a blue moon. The other side has a gold sun. Help me take a picture of each side.", audio: "05-vee-two-sides" },
    ],
    prompt: "Take one picture. Turn the tile over, then take a picture of its other side. A repeated picture uses one try light.",
    success: { speaker: "Vee", text: "Both pictures are in my notebook. It is one tile with two different sides. Their names help us tell them apart.", audio: "06-vee-both-sides" },
  },
  {
    id: "turn", title: "The first gate is stuck", gameTitle: "Gate Crank", gameIcon: "↻", background: "e03-source/e03-stage-02-turn-gate-v1.png", cast: ["mira", "tavi", "sol", "vee"], journey: "Vee puts the tile into the first gate with its blue moon side facing up.", activity: "turn",
    lines: [
      { speaker: "Narrator", text: "The first gate was stuck. Vee put the tile inside with the blue moon facing up.", audio: "07-narrator-first-turn" },
      { speaker: "Sol", text: "The curved handle turns the tile over. Pull the handle all the way to the gold mark, then release it.", audio: "08-sol-turn-wheel" },
    ],
    prompt: "Drag the gate handle, or tap the gold mark. Then release it. Releasing too soon rolls the tile back safely.",
    success: { speaker: "Mia", text: "The gate turned the tile over once. The blue moon went underneath, and the gold sun came out on top.", audio: "09-mira-gold-shows" },
  },
  {
    id: "return", title: "Choose the next path", gameTitle: "Return Run", gameIcon: "🔄", background: "e03-source/e03-stage-02-turn-gate-v1.png", cast: ["mira", "tavi", "sol", "vee"], journey: "The gold sun is showing. The tile must pass through one more turning gate.", activity: "return",
    lines: [
      { speaker: "Narrator", text: "Three short paths led forward. One missed the next gate. One went through it once. One looped through it twice.", audio: "10-narrator-second-gate" },
      { speaker: "Tavi", text: "We need one more turn. Choose a path, then send the gold sun tile through it. Watch which side comes back.", audio: "11-tavi-turn-return" },
    ],
    prompt: "Choose the path that will bring the blue moon back on top, then launch the tile. A wrong path uses one try light.",
    success: { speaker: "Vee", text: "The gold sun turned over once, and the blue moon came back. Return means the side we saw earlier is showing again.", audio: "12-vee-return-defined" },
  },
  {
    id: "continue", title: "Light the next stones", gameTitle: "Path Builder", gameIcon: "💡", background: "e03-source/e03-stage-01-trail-station-v1.png", cast: ["mira", "tavi", "sol", "vee"], journey: "The working gate lights four stones. Three dark stones wait ahead.", activity: "continue",
    lines: [
      { speaker: "Narrator", text: "The working stones showed blue moon, gold sun, blue moon, gold sun. Three dark stones waited next.", audio: "13-narrator-next-place" },
      { speaker: "Mia", text: "Look from left to right. Put the next three lights on the path. Use the same turn-over rule the gate showed us.", audio: "14-mira-pattern-defined" },
    ],
    prompt: "Wait for the next light on the moving belt. Place three lights, one at a time, in the dark spaces.",
    success: { speaker: "Sol", text: "Blue moon, gold sun, blue moon came next. The path follows a pattern. Pattern means a rule that tells us what comes next.", audio: "15-sol-next-moon" },
  },
  {
    id: "repair", title: "Sol's first try", gameTitle: "Rule Repair", gameIcon: "🛠️", background: "e03-source/e03-stage-01-trail-station-v1.png", cast: ["mira", "tavi", "sol", "vee"], journey: "The trail reaches the balcony. Sol places one tile the wrong way, and the light stops.", activity: "repair",
    lines: [
      { speaker: "Narrator", text: "Sol hurried ahead and placed six tiles. Two matching pictures met in one place, so the light stopped. His whole first try stayed where everyone could see it.", audio: "16-narrator-sols-row" },
      { speaker: "Sol", text: "Start at the left and check each move. Find the first tile that stops taking turns, then replace only that tile.", audio: "17-sol-repair-row" },
    ],
    prompt: "Choose a moon or sun replacement, then put it on the first broken place. Every wrong place or picture uses one try light.",
    success: { speaker: "Tavi", text: "We kept Sol's first try, found the first broken move, and repaired only that tile. Now the light can move again.", audio: "18-tavi-row-repaired" },
  },
  {
    id: "bridge", title: "Over and under", gameTitle: "Bridge Hop", gameIcon: "🌉", background: "e03-source/e03-stage-03-over-under-bridge-v1.png", cast: ["mira", "tavi", "sol", "vee"], journey: "The repaired light reaches a bridge with one path over and one path under.", activity: "bridge",
    lines: [
      { speaker: "Narrator", text: "The light reached a bridge. The first sign showed whether Vee should start over or under. After each arch, the safe path had to change.", audio: "19-narrator-over-under" },
      { speaker: "Vee", text: "Move me onto the path shown by the first sign. Then change between over and under as I cross. A closed gate will stop me safely.", audio: "20-vee-bridge-rule" },
    ],
    prompt: "Move Vee over or under, then cross one arch. Change path after every safe crossing.",
    success: { speaker: "Mia", text: "Vee changed between over and under all the way across. The pictures changed, but the two roles still took turns.", audio: "21-mira-bridge-crossed" },
  },
  {
    id: "routes", title: "Three routes to the arch", gameTitle: "Trail Mapper", gameIcon: "🗺️", background: "e03-source/e03-stage-04-sunrise-arch-v1.png", cast: ["mira", "tavi", "sol", "vee"], journey: "Three routes wait at the last gate. Only one is complete and follows every turn.", activity: "routes",
    lines: [
      { speaker: "Narrator", text: "At the last gate, three route maps lay side by side. One stopped before the arch. One put matching lights together. One reached the arch and kept taking turns.", audio: "22-narrator-three-routes" },
      { speaker: "Tavi", text: "Check where each route ends. Then check its lights from left to right. Choose one map and send Vee to test it.", audio: "23-tavi-check-routes" },
    ],
    prompt: "Choose a route that reaches the Sunrise Arch and changes picture at every move. A short or broken route uses one try light.",
    success: { speaker: "Vee", text: "Route C follows every turn and reaches the Sunrise Arch. The repaired light trail is complete.", audio: "24-vee-route-c" },
  },
  {
    id: "transfer", title: "The Sunrise Arch", gameTitle: "New-Role Relay", gameIcon: "⭐", background: "e03-source/e03-stage-04-sunrise-arch-v1.png", cast: ["mira", "tavi", "sol", "vee"], journey: "The trail reaches the arch. A final row uses star and leaf instead of moon and sun.", activity: "transfer",
    lines: [
      { speaker: "Narrator", text: "The light reached the Sunrise Arch. Four empty windows opened. A star and a leaf waited beside them.", audio: "25-narrator-star-leaf" },
      { speaker: "Mia", text: "First build a star-and-leaf row that takes turns. Then remember the first gate: a blue moon went in and the tile turned over once. Which side came out?",
        audio: "26-mira-transfer-recall" },
    ],
    prompt: "The first window already has a star. Fill the other three so star and leaf take turns. Then answer the one-turn memory card.",
    success: { speaker: "Mia", text: "Star and leaf took turns, and gold sun came out after blue moon turned over once. The pictures changed, but the rule did not. The Sunrise Arch is shining!", audio: "27-mira-arch-shines" },
  },
];

const codes: Record<string, string> = {
  TRAILLIGHT: "The trail lights play a four-note blue-and-gold tune.",
  TWOSIDES: "Vee's tile performs a slow practice flip.",
  TURNBACK: "The gate leaves a glowing turn-and-return footprint.",
  NEXTLIGHT: "A tiny blue moon lamp dances beside the trail.",
  KEEPTHETRY: "Sol pins his first try into the team scrapbook.",
  OVERUNDER: "The bridge plays one high note, then one low note.",
  RIGHTROUTE: "Route C grows a harmless ribbon of sparkles.",
  NEWROLES: "A star and leaf wave hello from the next adventure.",
};

const names: Record<Character, string> = { mira: "Mia", tavi: "Tavi", sol: "Sol", vee: "Vee" };
const endingLesson: Line = { speaker: "Narrator", text: "Here is the lesson. A pattern is a rule that tells us what comes next. We watched moon and sun take turns, turned one tile to see its other side, saw the first side return, repaired the first move that broke the rule, and used the same rule with over and under, then star and leaf. This matters because a clear rule helps us predict what comes next and find where a mistake began.", audio: "28-narrator-to-you" };
const image = (name: Character) => name === "mira"
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

function MiniGame({ title, icon, progress, children }: { title: string; icon: string; progress: string; children: ReactNode }) {
  return <section className="e03-mini-game" aria-label={`${title} mini-game`}>
    <header className="mini-game-header"><span aria-hidden="true">{icon}</span><div><small>MINI-GAME</small><strong>{title}</strong></div><b>{progress}</b></header>
    {children}
  </section>;
}

function TryLights({ mistakes }: { mistakes: number }) {
  return <div className="try-lights" aria-label={`${3 - mistakes} of 3 try lights left`}><b>TRY LIGHTS</b>{[0,1,2].map((value) => <span key={value} className={value < 3 - mistakes ? "on" : "off"}>◆</span>)}</div>;
}

export default function LevelThree({ onExit }: { onExit: () => void }) {
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
  const [tick, setTick] = useState(0);
  const [storageReady, setStorageReady] = useState(false);
  const audioRef = useRef<HTMLAudioElement | null>(null);
  const soundRef = useRef<AudioContext | null>(null);
  const lastLineRef = useRef("");
  const progressRef = useRef<Record<string, unknown>>({});
  const pointerStartRef = useRef(0);
  const swipedRef = useRef(false);

  useEffect(() => {
    try { localStorage.setItem("sft-active-level-v1", "e03"); } catch { /* optional */ }
  }, []);

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
    progressRef.current = { sceneIndex, beat, complete, finished, activityStep, chosen, wrong, mistakes, roundLost, round };
  }, [sceneIndex, beat, complete, finished, activityStep, chosen, wrong, mistakes, roundLost, round]);

  useEffect(() => {
    const timeout = window.setTimeout(() => {
      try {
        const saved = JSON.parse(localStorage.getItem("sft-e03-moving-stage-v1") ?? "{}");
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
        localStorage.setItem("sft-e03-moving-stage-v1", JSON.stringify(progress));
        localStorage.setItem("sft-active-level-v1", "e03");
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
      const audio = new Audio(`/audio/e03-v1.0.0/${endingLesson.audio}.mp3?v=mia-20260731`);
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

  useEffect(() => {
    if (!storageReady || !dialogueDone || complete || roundLost || !["trail", "continue"].includes(scene.activity)) return;
    const timer = window.setInterval(() => setTick((value) => value + 1), scene.activity === "trail" ? 1600 : 900);
    return () => window.clearInterval(timer);
  }, [storageReady, dialogueDone, complete, roundLost, scene.activity, round]);

  function playLine(current = line) {
    if (!current || muted) return;
    audioRef.current?.pause();
    const audio = new Audio(`/audio/e03-v1.0.0/${current.audio}.mp3?v=mia-20260731`);
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
  function wrongTry(message: string) { if (roundLost) return; sound("wrong"); const next = mistakes + 1; setMistakes(next); setWrong(message); if (next >= 3) setRoundLost(true); else window.setTimeout(() => setWrong(""), 2200); }
  function retryRound() { sound("step"); setRound((value) => value + 1); setMistakes(0); setRoundLost(false); setWrong(""); setActivityStep(0); setChosen([]); setTick(0); }
  function nextBeat() { sound("tap"); if (beat < scene.lines.length) setBeat((value) => value + 1); }
  function nextScene() {
    sound("step");
    if (sceneIndex === scenes.length - 1) { setFinished(true); return; }
    setSceneIndex((value) => value + 1); setBeat(0); setComplete(false); setActivityStep(0); setChosen([]); setWrong(""); setMistakes(0); setRoundLost(false); setTick(0); lastLineRef.current = "";
  }
  function replay() { audioRef.current?.pause(); setComplete(false); setActivityStep(0); setChosen([]); setWrong(""); setMistakes(0); setRoundLost(false); setRound((value) => value + 1); setTick(0); lastLineRef.current = ""; }
  function restart() {
    audioRef.current?.pause(); setSceneIndex(0); setBeat(0); setComplete(false); setFinished(false); setActivityStep(0); setChosen([]); setWrong(""); setMistakes(0); setRoundLost(false); setRound(0); setTick(0); lastLineRef.current = "";
    try {
      localStorage.removeItem("sft-e03-moving-stage-v1");
      localStorage.setItem("sft-active-level-v1", "e03");
    } catch { /* optional */ }
  }
  function submitCode(event: FormEvent) {
    event.preventDefault(); const clean = code.toUpperCase().replace(/[^A-Z]/g, "");
    setCodeMessage(codes[clean] ?? "That code is hiding on another book page. Keep looking.");
    if (codes[clean]) setCode("");
  }

  function activity() {
    if (complete) return null;
    const icons = { moon: "🌙", sun: "☀️", star: "⭐", leaf: "🍃" };
    if (scene.activity === "trail") {
      const expected = chosen.length % 2 ? "sun" : "moon";
      const lane = (tick + round) % 3;
      const catcherLane = activityStep % 3;
      const moveCatcher = (change: number) => { setActivityStep((value) => (value + change + 3) % 3); sound("step"); };
      const catchLight = () => {
        if (catcherLane !== lane) { wrongTry("The catcher was under a different lane. Move it below the falling light, then try again."); return; }
        const next = [...chosen, expected === "moon" ? 1 : 2]; setChosen(next); sound("good"); if (next.length === 4) window.setTimeout(finish, 400);
      };
      return <MiniGame title={scene.gameTitle} icon={scene.gameIcon} progress={`${chosen.length}/4 caught`}><div className="light-catch-board"><div className="caught-light-row" aria-label={`${chosen.length} lights caught`}>{[0,1,2,3].map((value)=><span key={value}>{value<chosen.length?(chosen[value]===1?icons.moon:icons.sun):"·"}</span>)}</div><div className="light-lanes">{[0,1,2].map((value)=><div key={value} className={value===lane?"live":""}><span>{value===lane?icons[expected]:"·"}</span><i>{value===catcherLane?"🪄":""}</i></div>)}</div><div className="catcher-controls"><button onClick={()=>moveCatcher(-1)} aria-label="Move catcher left">← Move</button><button className="catch-now" onClick={catchLight}>CATCH NOW</button><button onClick={()=>moveCatcher(1)} aria-label="Move catcher right">Move →</button></div></div></MiniGame>;
    }
    if (scene.activity === "sides") {
      const side = (activityStep + round) % 2;
      const flip = () => { setActivityStep((value)=>value+1); sound("step"); };
      const pointerUp = (event: ReactPointerEvent<HTMLButtonElement>) => { if (Math.abs(event.clientX-pointerStartRef.current)>35) { swipedRef.current=true; flip(); } };
      const record = () => { const value=side+1; if(chosen.includes(value)){wrongTry("That side is already in Vee's notebook. Flip the tile and record its other side.");return;}const next=[...chosen,value];setChosen(next);sound("good");if(next.length===2)window.setTimeout(finish,400); };
      return <MiniGame title={scene.gameTitle} icon={scene.gameIcon} progress={`${chosen.length}/2 pictures taken`}><div className="two-side-lab"><button className={`turning-tile side-${side}`} onPointerDown={(event)=>{pointerStartRef.current=event.clientX;swipedRef.current=false;}} onPointerUp={pointerUp} onClick={()=>{if(swipedRef.current){swipedRef.current=false;return;}flip();}} aria-label={`Tile showing ${side?"gold sun":"blue moon"}. Swipe sideways, tap, or press Enter to turn it over.`}><span>{side?icons.sun:icons.moon}</span><b>{side?"GOLD SUN":"BLUE MOON"}</b><small>Swipe or tap to turn over</small></button><button className="record-side" onClick={record}>📷 Take a picture of this side</button><div className="side-notebook" aria-label="Vee's two-picture notebook">{[1,2].map(value=><span key={value} className={chosen.includes(value)?"recorded":""}>{chosen.includes(value)?(value===1?icons.moon:icons.sun):"?"}</span>)}</div></div></MiniGame>;
    }
    if (scene.activity === "turn") {
      const crank = Math.min(activityStep, 4);
      const release = () => { if (crank < 4) { wrongTry("The handle was released before the gold mark. The tile rolled back safely. Pull it all the way across."); setActivityStep(0); return; } finish(); };
      return <MiniGame title={scene.gameTitle} icon={scene.gameIcon} progress={`${crank}/4 handle marks`}><div className={`gate-crank ${round % 2 ? "crank-reversed" : ""}`}><div className="crank-machine"><span className={`crank-tile crank-${crank}`}>{crank < 2 ? icons.moon : icons.sun}</span><div className="crank-arc" aria-hidden="true">↷</div><label><b>Pull the handle to the gold mark</b><input type="range" min="0" max="4" step="1" value={crank} onChange={(event)=>{setActivityStep(Number(event.currentTarget.value));sound("step");}} /></label><div className="crank-marks" aria-hidden="true"><i/><i/><i/><i/><i className="gold"/></div><button className="tap-gold-mark" onClick={()=>{setActivityStep(4);sound("step");}}>Tap the gold mark</button></div><button className="release-crank" onClick={release}>Release the handle</button></div></MiniGame>;
    }
    if (scene.activity === "return") {
      const paths = [
        { name: "Path A", turns: 0, track: ["☀️", "—", "—", "—", "☀️"] },
        { name: "Path B", turns: 1, track: ["☀️", "—", "↻", "—", "🌙"] },
        { name: "Path C", turns: 2, track: ["☀️", "↻", "—", "↻", "☀️"] },
      ];
      const selected = activityStep ? paths[activityStep - 1] : null;
      const launch = () => { if (!selected) { setWrong("Choose one path before you launch the tile."); return; } setChosen((values)=>[...values,activityStep]); if (selected.turns !== 1) { wrongTry(selected.turns === 0 ? "That path missed the gate, so the gold sun stayed on top." : "That path turned the tile twice, so the gold sun came back on top. We need one turn."); return; } finish(); };
      return <MiniGame title={scene.gameTitle} icon={scene.gameIcon} progress={selected?`${selected.name} ready` : "Choose one path"}><div className="return-lane-puzzle"><div className="return-paths">{paths.map((path,index)=><button key={path.name} className={`${activityStep===index+1?"selected":""} ${chosen.includes(index+1)?"tested":""}`} onClick={()=>{setActivityStep(index+1);sound("tap");}}><b>{path.name}</b><span>{path.track.join(" ")}</span><small>{path.turns === 0 ? "no gate" : `${path.turns} turning ${path.turns===1?"gate":"gates"}`}</small></button>)}</div><button className="launch-return" onClick={launch}>Send the gold sun tile →</button></div></MiniGame>;
    }
    if (scene.activity === "continue") {
      const belt=round%2?["sun","sun","moon","sun","moon"]:["moon","sun","sun","moon","moon"];const visible=belt[tick%belt.length];
      const expected=chosen.length%2===0?"moon":"sun";
      const drop=(role:string)=>{if(role!==expected){wrongTry(`That ${role} picture would put two matching pictures together. Look at the last stone and wait for the other picture.`);return;}const next=[...chosen,role==="moon"?1:2];setChosen(next);sound("good");if(next.length===3)window.setTimeout(finish,450);};
      return <MiniGame title={scene.gameTitle} icon={scene.gameIcon} progress={`${chosen.length}/3 dark stones lit`}><div className="pattern-conveyor"><div className="fixed-pattern" aria-label="Moon, sun, moon, sun, then three dark stones"><span>{icons.moon}</span><span>{icons.sun}</span><span>{icons.moon}</span><span>{icons.sun}</span>{[0,1,2].map((index)=><button key={index} className={index===chosen.length?"next-gap":""} disabled={index>chosen.length} onDragOver={(event)=>event.preventDefault()} onDrop={(event)=>index===chosen.length&&drop(event.dataTransfer.getData("text/plain"))} onClick={()=>index===chosen.length&&drop(visible)}>{index<chosen.length?(chosen[index]===1?icons.moon:icons.sun):"?"}</button>)}</div><button className={`belt-tile ${visible}`} draggable onDragStart={(event)=>event.dataTransfer.setData("text/plain",visible)} onClick={()=>drop(visible)}><span>{icons[visible as "moon"|"sun"]}</span><b>Place this moving light</b></button><small>The belt keeps moving. Look at the last lit stone before choosing.</small></div></MiniGame>;
    }
    if (scene.activity === "repair") {
      const brokenIndex=1+(round%4);const correct=(brokenIndex%2?"sun":"moon") as "moon"|"sun";const row=["moon","sun","moon","sun","moon","sun"] as Array<"moon"|"sun">;row[brokenIndex]=row[brokenIndex-1];
      const repair=(slot:number,role:string)=>{if(slot!==brokenIndex){setChosen((values)=>values.includes(slot)?values:[...values,slot]);wrongTry("That tile already changes from the picture before it. Start at the left and keep checking.");return;}if(role!==correct){setChosen((values)=>values.includes(slot)?values:[...values,slot]);wrongTry("That replacement still leaves two matching pictures together. Try the other picture.");return;}finish();};
      return <MiniGame title={scene.gameTitle} icon={scene.gameIcon} progress="Find and repair one broken move"><div className="rule-repair-board"><div className="first-try-label"><strong>SOL&apos;S FIRST TRY</strong><span>It stays visible while you check.</span></div><div className="repair-row">{row.map((role,index)=><button key={index} className={chosen.includes(index)?"tried":""} onDragOver={(event)=>event.preventDefault()} onDrop={(event)=>repair(index,event.dataTransfer.getData("text/plain"))} onClick={()=>activityStep?repair(index,activityStep===1?"moon":"sun"):setWrong("Choose a replacement picture, then place it on the first broken spot.")}><span>{icons[role]}</span><b>Spot {index+1}</b></button>)}</div><div className="repair-parts">{(["moon","sun"] as const).map((role,index)=><button key={role} draggable onDragStart={(event)=>event.dataTransfer.setData("text/plain",role)} onClick={()=>setActivityStep(index+1)} className={activityStep===index+1?"selected":""}><span>{icons[role]}</span><b>{role.toUpperCase()} REPLACEMENT</b></button>)}</div></div></MiniGame>;
    }
    if (scene.activity === "bridge") {
      const startsOver=round%2===0;const path=Array.from({length:5},(_,index)=>((index+(startsOver?1:0))%2));const step=chosen.length;const lane=activityStep;
      const move=()=>{if(lane!==path[step]){wrongTry(`Vee met the closed ${lane?"over":"under"} gate and stopped safely. Change to the other path before crossing this arch.`);return;}const next=[...chosen,step];setChosen(next);sound("step");if(next.length===path.length)window.setTimeout(finish,450);};
      return <MiniGame title={scene.gameTitle} icon={scene.gameIcon} progress={`${step}/5 bridge arches`}><div className="bridge-runner"><div className="bridge-start-sign">FIRST SIGN: <b>{startsOver?"OVER":"UNDER"}</b></div><div className="bridge-lanes"><div className={lane===1?"vee-here":""}>OVER</div><div className={lane===0?"vee-here":""}>UNDER</div>{path.map((open,index)=><i key={index} className={index===step?"next":""} aria-label={`Arch ${index+1}: ${open?"over is open and under is closed":"under is open and over is closed"}`}><small>ARCH {index+1}</small><span className={open===1?"open":"closed"}>{index===step&&lane===1?"🟣":index<step&&open===1?"✓":open===1?"GO":"×"}</span><span className={open===0?"open":"closed"}>{index===step&&lane===0?"🟣":index<step&&open===0?"✓":open===0?"GO":"×"}</span></i>)}</div><div><button className={lane===1?"selected":""} onClick={()=>{setActivityStep(1);sound("tap");}}>Move Vee OVER</button><button className={lane===0?"selected":""} onClick={()=>{setActivityStep(0);sound("tap");}}>Move Vee UNDER</button><button className="cross-arch" onClick={move}>Cross this arch →</button></div></div></MiniGame>;
    }
    if (scene.activity === "routes") {
      const routes=[
        {id:1,name:"ROUTE A",kind:"short",lights:["moon","sun","moon"] as const,end:"STOP"},
        {id:2,name:"ROUTE B",kind:"broken",lights:["moon","sun","moon","moon","sun"] as const,end:"ARCH"},
        {id:3,name:"ROUTE C",kind:"complete",lights:["moon","sun","moon","sun","moon"] as const,end:"ARCH"},
      ];
      const ordered=round%3===0?routes:round%3===1?[routes[1],routes[2],routes[0]]:[routes[2],routes[0],routes[1]];
      const testRoute=(route:typeof routes[number])=>{setChosen((values)=>values.includes(route.id)?values:[...values,route.id]);sound("step");if(route.kind==="short"){wrongTry("This route takes turns, but it stops before the Sunrise Arch. Check where every route ends.");return;}if(route.kind==="broken"){wrongTry("This route reaches the arch, but two moon pictures meet. Check every move from left to right.");return;}window.setTimeout(finish,500);};
      return <MiniGame title={scene.gameTitle} icon={scene.gameIcon} progress={`${chosen.length}/3 maps tested`}><div className="route-compare"><div className="route-map-cards">{ordered.map(route=><button key={route.id} className={chosen.includes(route.id)?"tested":""} onClick={()=>testRoute(route)}><b>{route.name}</b><span className="route-lights">START {route.lights.map((role,index)=><i key={index}>{icons[role]}</i>)} {route.end==="ARCH"?"🌅":"⛔"}</span><small>{route.end==="ARCH"?"reaches the arch":"stops early"}</small></button>)}</div><p>Check the end. Then check every pair of lights.</p></div></MiniGame>;
    }
    if (scene.activity === "transfer") {
      const phase=activityStep;const sequence=["leaf","star","leaf"] as const;
      const press=(role:string)=>{if(phase===1){if(role!=="sun"){wrongTry("A blue moon went into the first gate. One turn showed the tile's other side. Try the other picture.");return;}finish();return;}const expected=sequence[chosen.length];if(role!==expected){wrongTry("The first window already has a star. Look at it, then choose the other picture so they take turns.");setChosen([]);return;}const next=[...chosen,role==="star"?1:2];setChosen(next);sound("tap");if(next.length===3)window.setTimeout(()=>{setActivityStep(1);setChosen([]);sound("good");},450);};
      return <MiniGame title={scene.gameTitle} icon={scene.gameIcon} progress={phase===0?`Arch windows · ${chosen.length+1}/4`:"First-gate memory"}><div className="role-relay">{phase===0?<><div className="relay-track"><span className="lit given">{icons.star}</span>{sequence.map((role,index)=><span key={index} className={index<chosen.length?"lit":""}>{index<chosen.length?icons[role]:"?"}</span>)}</div><div>{(["star","leaf"] as const).map(role=><button key={role} onClick={()=>press(role)}><span>{icons[role]}</span><b>{role.toUpperCase()}</b></button>)}</div></>:<><div className="gate-memory-card"><strong>FIRST GATE</strong><span>{icons.moon} → ↻ → ?</span><small>Blue moon went in. The tile turned over once.</small></div><div>{(["moon","sun"] as const).map(role=><button key={role} onClick={()=>press(role)}><span>{icons[role]}</span><b>{role.toUpperCase()} CAME OUT</b></button>)}</div></>}</div></MiniGame>;
    }
    return null;
  }

  if (!storageReady) return <main className="restore-screen"><p>Returning to your adventure…</p></main>;

  if (finished) return <main className="ending-screen e03-ending">
    <div className="ending-art" /><button className="ending-home" onClick={onExit} aria-label="Choose a level">⌂ Levels</button><section><p className="eyebrow">LEVEL THREE COMPLETE</p><div className="e03-progress" aria-label="9 of 9 story steps complete">{scenes.map((_, index) => <span className="done" key={index}>●</span>)}</div><h1>The Sunrise Arch shines.</h1><p>Mia, Sol, Tavi and Vee restored the turning-light trail before sunrise.</p><blockquote>They named both roles, made one move, checked what came next, and kept a broken try while they repaired it.</blockquote><div className="ending-lesson"><span aria-hidden="true">📖</span><div><strong>NARRATOR TO YOU</strong><p>{endingLesson.text}</p></div><button onClick={() => playLine(endingLesson)}>Hear the lesson again</button></div><p className="grownup-boundary"><strong>For grown-ups:</strong> this level translates the admitted two-role Fold transition and return into visible play. The activities are demonstrations, not proofs.</p><div className="ending-controls"><button className="primary" disabled title="Book Four and Level Four are in development">Next level · coming soon</button><button className="secondary" onClick={restart}>Play Level 3 again</button><button className="secondary" onClick={onExit}>Choose a level</button></div></section>
  </main>;

  const promptText = scene.activity === "transfer" && activityStep === 1
    ? "At the first gate, a blue moon went in and the tile turned over once. Which side came out?"
    : scene.prompt;

  return <main className="game-shell level-three-shell">
    <header className="game-hud e03-hud">
      <div><span className="eyebrow">THE TURNING-LIGHT TRAIL</span><strong>{scene.title}</strong></div>
      <div className="e03-progress" aria-label={`${sceneIndex + (complete ? 1 : 0)} of 9 story steps complete`}>{scenes.map((_, index) => <span key={index} className={index < sceneIndex || (index === sceneIndex && complete) ? "done" : index === sceneIndex ? "now" : ""}>●</span>)}</div>
      <nav><button onClick={onExit} aria-label="Choose a level">⌂ <span>Levels</span></button><button onClick={() => playLine()} aria-label="Replay narration">↻ <span>Hear again</span></button><button onClick={() => setMuted((value) => !value)} aria-pressed={muted}>{muted ? "🔇" : "🔊"} <span>{muted ? "Narration off" : "Narration on"}</span></button><button onClick={() => setCodesOpen(true)}>⌨ <span>Book code</span></button></nav>
    </header>
    <section key={scene.id} className={`play-stage e03-stage scene-e03-${scene.id}`} style={{ backgroundImage: `url('/art/stages/${scene.background}')` }} aria-label={`${scene.title}, an animated turning-light story scene`}>
      <div className="stage-light" />
      {beat === 0 && scene.journey && <div className="journey-banner"><span aria-hidden="true">→</span><strong>{scene.journey}</strong></div>}
      {scene.introduces && beat <= 1 && <div className="guest-banner">New friend for Level Three: <strong>{names[scene.introduces]}</strong></div>}
      {scene.id === "trail" && !dialogueDone && <div className="story-moon-lantern" role="img" aria-label="The Moon Lantern beside the garden path"><strong>MOON LANTERN</strong><span aria-hidden="true">🏮</span></div>}
      <div className="walking-cast" aria-hidden="true">{scene.cast.map((name, index) => <CharacterSprite key={name} name={name} index={index} speaking={speaking === name} />)}</div>
      {dialogueDone && !complete && <div className="activity-layer"><TryLights mistakes={mistakes}/>{!roundLost && activity()}{wrong && <p className="e03-feedback" role="status">{wrong}</p>}{roundLost && <section className="round-lost" role="alert"><span aria-hidden="true">◆ ◆ ◆</span><h2>Round over</h2><p>That round used all three try lights. The story is safe. Change your plan and try this puzzle again.</p><button onClick={retryRound}>Try a new board</button></section>}</div>}
      <aside className={`speech-panel ${dialogueDone && !complete ? "prompting" : ""} ${complete ? "completed" : ""}`} aria-live="polite">
        {!dialogueDone || complete ? <><div className="speaker-portrait"><Portrait speaker={line.speaker} /></div><span className="speaker">{line.speaker}</span><p>{line.text}</p>{complete ? <div className="completion-controls"><button className="replay-control" onClick={replay}><span aria-hidden="true">↻</span> Play again</button><button className="next-control" onClick={nextScene}>{sceneIndex === scenes.length - 1 ? "Light the arch" : "Follow the trail"} <span aria-hidden="true">→</span></button></div> : <button className="next-control" onClick={nextBeat}>Next <span aria-hidden="true">→</span></button>}</> : <><div className="speaker-portrait prompt-portrait" aria-hidden="true">☝️</div><span className="speaker">YOUR TURN</span><p>{promptText}</p><span className="action-nudge" aria-hidden="true">↑ Try it in the scene</span></>}
      </aside>
    </section>
    <button className="restart-corner" onClick={restart}>Start over</button>
    {codesOpen && <div className="modal-backdrop" role="presentation" onMouseDown={() => setCodesOpen(false)}><section className="code-modal" role="dialog" aria-modal="true" aria-labelledby="e03-code-title" onMouseDown={(event) => event.stopPropagation()}><button className="close-modal" onClick={() => setCodesOpen(false)} aria-label="Close">×</button><p className="eyebrow">OPTIONAL BOOK SECRET</p><h2 id="e03-code-title">Mia’s code pocket</h2><p>Codes unlock jokes and small previews. They never give an answer or skip a lesson.</p><form onSubmit={submitCode}><label htmlFor="e03-book-code">Code from Book Three</label><div><input id="e03-book-code" value={code} onChange={(event) => setCode(event.target.value)} autoComplete="off" /><button>Open</button></div></form><p className="code-result" aria-live="polite">{codeMessage}</p></section></div>}
  </main>;
}
