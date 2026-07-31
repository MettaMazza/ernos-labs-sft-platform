"use client";

import { CSSProperties, FormEvent, PointerEvent as ReactPointerEvent, ReactNode, useEffect, useLayoutEffect, useRef, useState } from "react";
import LevelPrelude, { PreludeLine } from "./level-prelude";
import { startNarration, stopNarration } from "./narration-controller.mjs";
import { levelThreeRelayForRound, pendingLevelThreeResolution, readLevelThreeIntroSeen, readLevelThreeResolution } from "./level-three-state.mjs";
import useLevelMusic from "./use-level-music";

type Character = "mira" | "tavi" | "sol" | "vee";
type Activity = "trail" | "sides" | "turn" | "return" | "continue" | "repair" | "bridge" | "routes" | "transfer";
type Line = { speaker: string; text: string; audio: string };
type Resolution = "finish" | "transfer-memory" | null;
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
      { speaker: "Mia", text: "The Sunrise Arch lights the way to the garden gate each morning. Let’s catch the moon and sun lights so we can see how the path should work.", audio: "02-mira-catch-lights" },
    ],
    prompt: "Move the catcher below the falling light, then catch it. The next light will move to a new lane. Three missed catches end the round.",
    success: { speaker: "Narrator", text: "You caught blue moon, gold sun, blue moon, gold sun. The two pictures took turns in the same order. Watching the order gives us a clue about how the dark path is meant to work.", audio: "03-tavi-four-lights" },
  },
  {
    id: "sides", title: "Vee and the turning tile", gameTitle: "Two-Side Camera", gameIcon: "📷", background: "e03-source/e03-stage-02-turn-gate-v1.png", cast: ["mira", "tavi", "sol", "vee"], journey: "The friends follow the dark stones to a gate that turns the path tiles.", introduces: "vee", activity: "sides",
    lines: [
      { speaker: "Narrator", text: "Mia, Sol and Tavi followed the dark stones to a turning gate. Vee hurried over with one round path tile.", audio: "04-narrator-meet-vee" },
      { speaker: "Vee", text: "Hello! I’m Vee. I look after this path. One side of my tile has a blue moon. The other side has a gold sun. Help me take a picture of each side.", audio: "05-vee-two-sides" },
    ],
    prompt: "Take one picture. Turn the tile over, then take a picture of its other side. A repeated picture uses one try light.",
    success: { speaker: "Narrator", text: "You recorded both sides of one tile: blue moon on one side and gold sun on the other. The tile is one object with two different roles. Naming both sides helps us describe what changes when it turns.", audio: "06-vee-both-sides" },
  },
  {
    id: "turn", title: "The first gate is stuck", gameTitle: "Gate Crank", gameIcon: "↻", background: "e03-source/e03-stage-02-turn-gate-v1.png", cast: ["mira", "tavi", "sol", "vee"], journey: "Vee puts the tile into the first gate with its blue moon side facing up.", activity: "turn",
    lines: [
      { speaker: "Narrator", text: "The first gate was stuck. Vee put the tile inside with the blue moon facing up.", audio: "07-narrator-first-turn" },
      { speaker: "Sol", text: "The curved handle turns the tile over. Pull the handle all the way to the gold mark, then release it.", audio: "08-sol-turn-wheel" },
    ],
    prompt: "Drag the gate handle, or tap the gold mark. Then release it. Releasing too soon rolls the tile back safely.",
    success: { speaker: "Narrator", text: "You completed one full turn. Blue moon began on top; after the turn, gold sun was on top. This teaches us that one clear move changes which side we can see.", audio: "09-mira-gold-shows" },
  },
  {
    id: "return", title: "Choose the next path", gameTitle: "Return Run", gameIcon: "🔄", background: "e03-source/e03-stage-02-turn-gate-v1.png", cast: ["mira", "tavi", "sol", "vee"], journey: "The gold sun is showing. The tile must pass through one more turning gate.", activity: "return",
    lines: [
      { speaker: "Narrator", text: "Three short paths led forward. One missed the next gate. One went through it once. One looped through it twice.", audio: "10-narrator-second-gate" },
      { speaker: "Tavi", text: "We need one more turn. Choose a path, then send the gold sun tile through it. Watch which side comes back.", audio: "11-tavi-turn-return" },
    ],
    prompt: "Choose the path that will bring the blue moon back on top, then launch the tile. A wrong path uses one try light.",
    success: { speaker: "Narrator", text: "The gold sun turned over once and the blue moon came back. Return means an earlier side is showing again. Two turns brought the tile back to the side that was visible at the start.", audio: "12-vee-return-defined" },
  },
  {
    id: "continue", title: "Light the next stones", gameTitle: "Path Builder", gameIcon: "💡", background: "e03-source/e03-stage-01-trail-station-v1.png", cast: ["mira", "tavi", "sol", "vee"], journey: "The working gate lights four stones. Three dark stones wait ahead.", activity: "continue",
    lines: [
      { speaker: "Narrator", text: "The working stones showed blue moon, gold sun, blue moon, gold sun. Three dark stones waited next.", audio: "13-narrator-next-place" },
      { speaker: "Mia", text: "Look from left to right. Put the next three lights on the path. Use the same turn-over rule the gate showed us.", audio: "14-mira-pattern-defined" },
    ],
    prompt: "Choose the moon or sun light that belongs in the glowing space. Fill the three spaces from left to right.",
    success: { speaker: "Narrator", text: "You continued the row with blue moon, gold sun, blue moon. The pictures follow a pattern. A pattern is an order with a rule that helps us work out what comes next.", audio: "15-sol-next-moon" },
  },
  {
    id: "repair", title: "Sol's first try", gameTitle: "Rule Repair", gameIcon: "🛠️", background: "e03-source/e03-stage-01-trail-station-v1.png", cast: ["mira", "tavi", "sol", "vee"], journey: "The light reaches a bend in the garden path. Sol places one tile the wrong way, and the light stops.", activity: "repair",
    lines: [
      { speaker: "Narrator", text: "Sol hurried ahead and placed six tiles. Two matching pictures met in one place, so the light stopped. His whole first try stayed where everyone could see it.", audio: "16-narrator-sols-row" },
      { speaker: "Sol", text: "Start at the left and check each move. Find the first tile that stops taking turns, then replace only that tile.", audio: "17-sol-repair-row" },
    ],
    prompt: "Choose a moon or sun replacement, then put it on the first broken place. Every wrong place or picture uses one try light.",
    success: { speaker: "Narrator", text: "You kept Sol's first try where you could see it, checked from the left, and found the first place that broke the rule. Keeping the old try helped you explain exactly what needed to change.", audio: "18-tavi-row-repaired" },
  },
  {
    id: "bridge", title: "Over and under", gameTitle: "Bridge Hop", gameIcon: "🌉", background: "e03-source/e03-stage-03-over-under-bridge-v1.png", cast: ["mira", "tavi", "sol", "vee"], journey: "The repaired light reaches a bridge with one path over and one path under.", activity: "bridge",
    lines: [
      { speaker: "Narrator", text: "The light reached a bridge. The first sign showed whether Vee should start over or under. After each arch, the safe path had to change.", audio: "19-narrator-over-under" },
      { speaker: "Vee", text: "Move me onto the path shown by the first sign. Then change between over and under as I cross. A closed gate will stop me safely.", audio: "20-vee-bridge-rule" },
    ],
    prompt: "Move Vee over or under, then cross one arch. Change path after every safe crossing.",
    success: { speaker: "Narrator", text: "You moved Vee across all five arches: over, under, over, under, over when the first sign said over; or under, over, under, over, under when the first sign said under. In both paths, over and under alternated from one arch to the next, so the same take-turns rule worked all the way across. A useful rule can guide more than one kind of object or place.", audio: "21-mira-bridge-crossed" },
  },
  {
    id: "routes", title: "Three routes to the arch", gameTitle: "Trail Mapper", gameIcon: "🗺️", background: "e03-source/e03-stage-04-sunrise-arch-v1.png", cast: ["mira", "tavi", "sol", "vee"], journey: "Three routes wait at the last gate. Only one is complete and follows every turn.", activity: "routes",
    lines: [
      { speaker: "Narrator", text: "At the last gate, three route maps lay side by side. One stopped before the arch. One put matching lights together. One reached the arch and kept taking turns.", audio: "22-narrator-three-routes" },
      { speaker: "Tavi", text: "Check where each route ends. Then check its lights from left to right. Choose one map and send Vee to test it.", audio: "23-tavi-check-routes" },
    ],
    prompt: "Choose a route that reaches the Sunrise Arch and changes picture at every move. A short or broken route uses one try light.",
    success: { speaker: "Narrator", text: "You chose the route that reached the Sunrise Arch and changed picture at every step. A complete answer must meet every part of the question, not just one part of it.", audio: "24-vee-route-c" },
  },
  {
    id: "transfer", title: "The Sunrise Arch", gameTitle: "New-Role Relay", gameIcon: "⭐", background: "e03-source/e03-stage-04-sunrise-arch-v1.png", cast: ["mira", "tavi", "sol", "vee"], journey: "The trail reaches the arch. A final row uses star and leaf instead of moon and sun.", activity: "transfer",
    lines: [
      { speaker: "Narrator", text: "The light reached the Sunrise Arch. Four windows opened. The first window already showed the starting picture, and star and leaf choices waited below.", audio: "25-narrator-star-leaf" },
      { speaker: "Mia", text: "First build a star-and-leaf row that takes turns. Then remember the first gate: a blue moon went in and the tile turned over once. Which side came out?",
        audio: "26-mira-transfer-recall" },
    ],
    prompt: "The first window already has a star. Fill the other three so star and leaf take turns. Then answer the one-turn memory card.",
    success: { speaker: "Narrator", text: "Star and leaf took turns just as moon and sun did. You also remembered that one turn changes blue moon to gold sun. The pictures changed, but the rule stayed the same. That is why the Sunrise Arch can shine again.", audio: "27-mira-arch-shines" },
  },
];

const levelThreePrelude: PreludeLine[] = [
  { speaker: "Narrator", heading: "What you learned before", text: "In the Moon Lantern workshop, you counted four separate parts and fitted them together to rebuild one whole. Plus joined the counts, and equals showed that both sides named the same total.", audio: "00a-narrator-recap" },
  { speaker: "Narrator", heading: "The lantern points ahead", text: "When the Moon Lantern began to shine, a blue moon appeared, then a gold sun. The two lights leapt from the balcony onto the garden path, where the trail suddenly went dark.", audio: "00b-narrator-trail-link" },
  { speaker: "Narrator", heading: "What you will discover", text: "You will turn one two-sided tile, watch an earlier side return, continue an order, repair its first broken move, and use the same rule with new pictures.", audio: "00c-narrator-discover" },
  { speaker: "Narrator", heading: "Follow the light with Vee", text: "Vee looks after the garden trail and will join the team here. Try each puzzle, keep your mistakes where you can learn from them, and listen after every game for what you discovered.", audio: "00d-narrator-vee-tease" },
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

const codeTreats: Record<string, string> = {
  TRAILLIGHT: "🎵 ✨ 🏮 ✨",
  TWOSIDES: "🥽 ✨ 📷",
  TURNBACK: "✨ ↻ ✨ ↻",
  NEXTLIGHT: "🎶 💡 🎶",
  KEEPTHETRY: "🖼️ ⭐",
  OVERUNDER: "🎵 🌉 🎶",
  RIGHTROUTE: "✨ 🗺️ ✨",
  NEWROLES: "⭐ 👋 🍃",
};

const names: Record<Character, string> = { mira: "Mia", tavi: "Tavi", sol: "Sol", vee: "Vee" };
const endingLesson: Line = { speaker: "Narrator", text: "Here is what you learned. One turn changed which side of the tile was showing, and another turn made the first side return. Repeating that move created a pattern: an order with a rule that tells us what comes next. You kept a broken try, found where its rule first failed, and used the same rule with new pictures. This matters because a clear rule helps us predict, check and repair.", audio: "28-narrator-to-you" };
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
  const [introSeen, setIntroSeen] = useState(false);
  const [beat, setBeat] = useState(0);
  const [complete, setComplete] = useState(false);
  const [finished, setFinished] = useState(false);
  const [muted, setMuted] = useState(false);
  const [codesOpen, setCodesOpen] = useState(false);
  const [code, setCode] = useState("");
  const [codeMessage, setCodeMessage] = useState("");
  const [unlockedCode, setUnlockedCode] = useState("");
  const [activityStep, setActivityStep] = useState(0);
  const [chosen, setChosen] = useState<number[]>([]);
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
  const pointerStartRef = useRef(0);
  const swipedRef = useRef(false);
  const { enabled: musicOn, start: startMusic, stop: stopMusic, toggle: toggleMusic, duck: duckMusic } = useLevelMusic("level-three");

  useEffect(() => {
    try { localStorage.setItem("sft-active-level-v1", "e03"); } catch { /* optional */ }
  }, []);

  const scene = scenes[sceneIndex];
  const introOpen = !introSeen;
  const dialogueDone = beat >= scene.lines.length;
  const line = complete ? scene.success : scene.lines[Math.min(beat, scene.lines.length - 1)];
  const speaking = (!dialogueDone || complete) ? (line?.speaker.toLowerCase() === "mia" ? "mira" : line?.speaker.toLowerCase()) : "";
  const inferredResolution = complete ? null : pendingLevelThreeResolution(scene.activity, chosen, activityStep);
  const pendingResolution = resolution ?? inferredResolution;
  const resolving = pendingResolution !== null;
  const relay = levelThreeRelayForRound(round);

  useEffect(() => {
    if (storageReady) startMusic();
  }, [storageReady, startMusic]);

  useEffect(() => {
    const stopBackgroundAudio = () => {
      if (document.visibilityState !== "hidden") return;
      stopNarration(audioRef, narrationGenerationRef, duckMusic);
    };
    const stopForPageHide = () => {
      stopNarration(audioRef, narrationGenerationRef, duckMusic);
    };
    document.addEventListener("visibilitychange", stopBackgroundAudio);
    window.addEventListener("pagehide", stopForPageHide);
    return () => {
      document.removeEventListener("visibilitychange", stopBackgroundAudio);
      window.removeEventListener("pagehide", stopForPageHide);
    };
  }, [duckMusic]);

  useLayoutEffect(() => {
    progressRef.current = { introSeen, sceneIndex, beat, complete, finished, activityStep, chosen, wrong, mistakes, roundLost, round, resolution };
  }, [introSeen, sceneIndex, beat, complete, finished, activityStep, chosen, wrong, mistakes, roundLost, round, resolution]);

  useEffect(() => {
    const timeout = window.setTimeout(() => {
      try {
        const stored = localStorage.getItem("sft-e03-moving-stage-v1");
        const saved = JSON.parse(stored ?? "{}");
        const restoredIntroSeen = readLevelThreeIntroSeen(saved, stored !== null);
        const restoredSceneIndex = typeof saved.sceneIndex === "number" ? Math.min(Math.max(saved.sceneIndex, 0), scenes.length - 1) : 0;
        const restoredBeat = typeof saved.beat === "number" ? Math.max(saved.beat, 0) : 0;
        const restoredComplete = saved.complete === true;
        const restoredFinished = saved.finished === true;
        setIntroSeen(restoredIntroSeen);
        setSceneIndex(restoredSceneIndex);
        setBeat(restoredBeat);
        setComplete(restoredComplete);
        setFinished(restoredFinished);
        lastLineRef.current = restoredIntroSeen && !restoredFinished ? `${restoredSceneIndex}:${restoredComplete ? "success" : restoredBeat}` : "";
        endingLessonPlayedRef.current = restoredFinished;
        if (typeof saved.activityStep === "number") setActivityStep(Math.max(saved.activityStep, 0));
        if (Array.isArray(saved.chosen)) setChosen(saved.chosen.filter((value: unknown) => typeof value === "number"));
        if (typeof saved.wrong === "string") setWrong(saved.wrong);
        if (typeof saved.mistakes === "number") setMistakes(Math.max(0, Math.min(3, saved.mistakes)));
        if (typeof saved.roundLost === "boolean") setRoundLost(saved.roundLost);
        if (typeof saved.round === "number") setRound(Math.max(0, saved.round));
        setResolution(readLevelThreeResolution(saved.resolution));
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
  }, [storageReady, introSeen, sceneIndex, beat, complete, finished, activityStep, chosen, wrong, mistakes, roundLost, round, resolution]);

  useEffect(() => {
    if (!storageReady || !finished || muted || endingLessonPlayedRef.current) return;
    endingLessonPlayedRef.current = true;
    let lessonAudio: HTMLAudioElement | null = null;
    const scheduledGeneration = narrationGenerationRef.current;
    const timeout = window.setTimeout(() => {
      if (document.visibilityState !== "visible") return;
      if (narrationGenerationRef.current !== scheduledGeneration) return;
      if (audioRef.current && !audioRef.current.paused) return;
      lessonAudio = startNarration({
        src: `/audio/e03-v1.0.0/${endingLesson.audio}.mp3?v=e03-review-20260731c`,
        audioRef,
        generationRef: narrationGenerationRef,
        duckMusic,
      });
    }, 120);
    return () => {
      window.clearTimeout(timeout);
      stopNarration(audioRef, narrationGenerationRef, duckMusic);
      lessonAudio?.pause();
    };
  }, [storageReady, finished, muted, duckMusic]);

  useEffect(() => () => {
    stopNarration(audioRef, narrationGenerationRef, duckMusic);
    stopMusic();
  }, [duckMusic, stopMusic]);

  function playLine(current = line) {
    if (!current || muted) return;
    startNarration({
      src: `/audio/e03-v1.0.0/${current.audio}.mp3?v=e03-review-20260731c`,
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
    if (finished) return;
    if (introOpen || !line || (dialogueDone && !complete)) { stopNarration(audioRef, narrationGenerationRef, duckMusic); return; }
    const key = `${sceneIndex}:${complete ? "success" : beat}`;
    const scheduledGeneration = narrationGenerationRef.current;
    const timeout = window.setTimeout(() => {
      if (document.visibilityState !== "visible") return;
      if (narrationGenerationRef.current !== scheduledGeneration) return;
      if (lastLineRef.current === key) return;
      lastLineRef.current = key;
      playLine(line);
    }, 25);
    return () => { window.clearTimeout(timeout); stopNarration(audioRef, narrationGenerationRef, duckMusic); };
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [finished, introOpen, sceneIndex, beat, complete, muted]);

  function finish() { sound("good"); setResolution(null); setWrong(""); setMistakes(0); setRoundLost(false); setComplete(true); }
  function beginResolution(next: Exclude<Resolution, null>) { if (resolving || complete || roundLost) return; setResolution(next); }
  function wrongTry(message: string) { if (roundLost || resolving) return; sound("wrong"); const next = mistakes + 1; setMistakes(next); setWrong(message); if (next >= 3) setRoundLost(true); else window.setTimeout(() => setWrong(""), 2200); }
  function retryRound() { sound("step"); setResolution(null); setRound((value) => value + 1); setMistakes(0); setRoundLost(false); setWrong(""); setActivityStep(0); setChosen([]); }
  function nextBeat() { sound("tap"); if (beat < scene.lines.length) setBeat((value) => value + 1); }
  function nextScene() {
    sound("step");
    if (sceneIndex === scenes.length - 1) { stopNarration(audioRef, narrationGenerationRef, duckMusic); endingLessonPlayedRef.current = false; setResolution(null); setFinished(true); return; }
    setResolution(null); setSceneIndex((value) => value + 1); setBeat(0); setComplete(false); setActivityStep(0); setChosen([]); setWrong(""); setMistakes(0); setRoundLost(false); lastLineRef.current = "";
  }
  function replay() { stopNarration(audioRef, narrationGenerationRef, duckMusic); setResolution(null); setComplete(false); setActivityStep(0); setChosen([]); setWrong(""); setMistakes(0); setRoundLost(false); setRound((value) => value + 1); lastLineRef.current = ""; }
  function restart() {
    stopNarration(audioRef, narrationGenerationRef, duckMusic); setIntroSeen(false); setResolution(null); setSceneIndex(0); setBeat(0); setComplete(false); setFinished(false); setActivityStep(0); setChosen([]); setWrong(""); setMistakes(0); setRoundLost(false); setRound(0); lastLineRef.current = ""; endingLessonPlayedRef.current = false;
    try {
      localStorage.removeItem("sft-e03-moving-stage-v1");
      localStorage.setItem("sft-active-level-v1", "e03");
    } catch { /* optional */ }
  }
  function submitCode(event: FormEvent) {
    event.preventDefault(); const clean = code.toUpperCase().replace(/[^A-Z]/g, "");
    setCodeMessage(codes[clean] ?? "That code is hiding on another book page. Keep looking.");
    if (codes[clean]) { setUnlockedCode(clean); setCode(""); sound("good"); }
  }
  function toggleNarration() { const next = !muted; setMuted(next); if (next) stopNarration(audioRef, narrationGenerationRef, duckMusic); }
  function exitLevel() { stopNarration(audioRef, narrationGenerationRef, duckMusic); stopMusic(); onExit(); }

  useEffect(() => {
    if (!pendingResolution || complete || roundLost) return;
    const timeout = window.setTimeout(() => {
      if (pendingResolution === "transfer-memory") {
        setWrong(""); setActivityStep(1); setChosen([]); setResolution(null); sound("good");
        return;
      }
      finish();
    }, 450);
    return () => window.clearTimeout(timeout);
    // finish and sound intentionally consume the current render's audio settings.
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [pendingResolution, resolution, complete, roundLost, sceneIndex]);

  function activity() {
    if (complete) return null;
    const icons = { moon: "🌙", sun: "☀️", star: "⭐", leaf: "🍃" };
    if (scene.activity === "trail") {
      const expected = chosen.length % 2 ? "sun" : "moon";
      const lane = (chosen.length + mistakes + round) % 3;
      const catcherLane = activityStep % 3;
      const moveCatcher = (change: number) => { setActivityStep((value) => (value + change + 3) % 3); sound("step"); };
      const catchLight = () => {
        if (catcherLane !== lane) { wrongTry("The catcher was under a different lane. Move it below the falling light, then try again."); return; }
        const next = [...chosen, expected === "moon" ? 1 : 2]; setChosen(next); sound("good"); if (next.length === 4) beginResolution("finish");
      };
      return <MiniGame title={scene.gameTitle} icon={scene.gameIcon} progress={`${chosen.length}/4 caught`}><div className="light-catch-board"><div className="caught-light-row" aria-label={`${chosen.length} lights caught`}>{[0,1,2,3].map((value)=><span key={value}>{value<chosen.length?(chosen[value]===1?icons.moon:icons.sun):"·"}</span>)}</div><div className="light-lanes">{[0,1,2].map((value)=><div key={value} className={value===lane?"live":""}><span>{value===lane?icons[expected]:"·"}</span><i>{value===catcherLane?"🪄":""}</i></div>)}</div><div className="catcher-controls"><button onClick={()=>moveCatcher(-1)} aria-label="Move catcher left">← Move</button><button className="catch-now" onClick={catchLight}>CATCH NOW</button><button onClick={()=>moveCatcher(1)} aria-label="Move catcher right">Move →</button></div></div></MiniGame>;
    }
    if (scene.activity === "sides") {
      const side = (activityStep + round) % 2;
      const flip = () => { setActivityStep((value)=>value+1); sound("step"); };
      const pointerUp = (event: ReactPointerEvent<HTMLButtonElement>) => { if (Math.abs(event.clientX-pointerStartRef.current)>35) { swipedRef.current=true; flip(); } };
      const record = () => { const value=side+1; if(chosen.includes(value)){wrongTry("That side is already in Vee's notebook. Flip the tile and record its other side.");return;}const next=[...chosen,value];setChosen(next);sound("good");if(next.length===2)beginResolution("finish"); };
      return <MiniGame title={scene.gameTitle} icon={scene.gameIcon} progress={`${chosen.length}/2 pictures taken`}><div className="two-side-lab"><button className={`turning-tile side-${side}`} onPointerDown={(event)=>{pointerStartRef.current=event.clientX;swipedRef.current=false;}} onPointerUp={pointerUp} onClick={()=>{if(swipedRef.current){swipedRef.current=false;return;}flip();}} onKeyDown={(event)=>{if(event.key==="Enter"||event.key===" "){event.preventDefault();flip();}}} aria-label={`Tile showing ${side?"gold sun":"blue moon"}. Swipe sideways, tap, or press Enter to turn it over.`}><span>{side?icons.sun:icons.moon}</span><b>{side?"GOLD SUN":"BLUE MOON"}</b><small>Swipe, tap or press Enter to turn over</small></button><button className="record-side" onClick={record}>📷 Take a picture of this side</button><div className="side-notebook" aria-label="Vee's two-picture notebook">{[1,2].map(value=><span key={value} className={chosen.includes(value)?"recorded":""}>{chosen.includes(value)?(value===1?icons.moon:icons.sun):"?"}</span>)}</div></div></MiniGame>;
    }
    if (scene.activity === "turn") {
      const crank = Math.min(activityStep, 4);
      const release = () => { if (crank < 4) { wrongTry("The handle was released before the gold mark. The tile rolled back safely. Pull it all the way across."); setActivityStep(0); return; } finish(); };
      return <MiniGame title={scene.gameTitle} icon={scene.gameIcon} progress={`${crank}/4 handle marks`}><div className={`gate-crank ${round % 2 ? "crank-reversed" : ""}`}><div className="crank-machine"><span className={`crank-tile crank-${crank}`}>{crank < 2 ? icons.moon : icons.sun}</span><div className="crank-arc" aria-hidden="true">↷</div><label><b>Pull the handle to the gold mark</b><input type="range" min="0" max="4" step="1" value={crank} onChange={(event)=>{setActivityStep(Number(event.currentTarget.value));sound("step");}} /></label><div className="crank-marks" aria-hidden="true"><i/><i/><i/><i/><i className="gold"/></div><button className="tap-gold-mark" onClick={()=>{setActivityStep(4);sound("step");}}>Tap the gold mark</button></div><button className="release-crank" onClick={release}>Release the handle</button></div></MiniGame>;
    }
    if (scene.activity === "return") {
      const kinds = [
        { turns: 0, track: ["☀️", "—", "—", "—", "☀️"] },
        { turns: 1, track: ["☀️", "—", "↻", "—", "🌙"] },
        { turns: 2, track: ["☀️", "↻", "—", "↻", "☀️"] },
      ];
      const rotated = [...kinds.slice(round % 3), ...kinds.slice(0, round % 3)];
      const paths = rotated.map((path, index) => ({ ...path, name: `Path ${String.fromCharCode(65 + index)}` }));
      const selected = activityStep ? paths[activityStep - 1] : null;
      const launch = () => { if (!selected) { setWrong("Choose one path before you launch the tile."); return; } setChosen((values)=>[...values,activityStep]); if (selected.turns !== 1) { wrongTry(selected.turns === 0 ? "That path missed the gate, so the gold sun stayed on top." : "That path turned the tile twice, so the gold sun came back on top. We need one turn."); return; } finish(); };
      return <MiniGame title={scene.gameTitle} icon={scene.gameIcon} progress={selected?`${selected.name} ready` : "Choose one path"}><div className="return-lane-puzzle"><div className="return-paths">{paths.map((path,index)=><button key={path.name} className={`${activityStep===index+1?"selected":""} ${chosen.includes(index+1)?"tested":""}`} onClick={()=>{setActivityStep(index+1);sound("tap");}}><b>{path.name}</b><span>{path.track.join(" ")}</span><small>{path.turns === 0 ? "no gate" : `${path.turns} turning ${path.turns===1?"gate":"gates"}`}</small></button>)}</div><button className="launch-return" onClick={launch}>Send the gold sun tile →</button></div></MiniGame>;
    }
    if (scene.activity === "continue") {
      const expected=chosen.length%2===0?"moon":"sun";
      const drop=(role:string)=>{if(role!==expected){wrongTry(`That ${role} picture would put two matching pictures together. Look at the last stone, then choose the other picture.`);return;}const next=[...chosen,role==="moon"?1:2];setChosen(next);sound("good");if(next.length===3)beginResolution("finish");};
      const options = (round % 2 ? ["sun", "moon"] : ["moon", "sun"]) as Array<"moon"|"sun">;
      return <MiniGame title={scene.gameTitle} icon={scene.gameIcon} progress={`${chosen.length}/3 dark stones lit`}><div className="pattern-conveyor"><div className="fixed-pattern" aria-label="Moon, sun, moon, sun, then three dark stones"><span>{icons.moon}</span><span>{icons.sun}</span><span>{icons.moon}</span><span>{icons.sun}</span>{[0,1,2].map((index)=><button key={index} className={index===chosen.length?"next-gap":""} disabled={index>chosen.length} onDragOver={(event)=>event.preventDefault()} onDrop={(event)=>index===chosen.length&&drop(event.dataTransfer.getData("text/plain"))}>{index<chosen.length?(chosen[index]===1?icons.moon:icons.sun):"?"}</button>)}</div><div className="conveyor-choices" aria-label="Choose the next moving light">{options.map((role)=><button key={role} className={`belt-tile ${role}`} draggable onDragStart={(event)=>event.dataTransfer.setData("text/plain",role)} onClick={()=>drop(role)}><span>{icons[role]}</span><b>Choose {role}</b></button>)}</div><small>Both lights keep moving. Choose the one that belongs after the last lit stone.</small></div></MiniGame>;
    }
    if (scene.activity === "repair") {
      const brokenIndex=1+(round%4);const correct=(brokenIndex%2?"sun":"moon") as "moon"|"sun";const row=["moon","sun","moon","sun","moon","sun"] as Array<"moon"|"sun">;row[brokenIndex]=row[brokenIndex-1];
      const repair=(slot:number,role:string)=>{if(slot!==brokenIndex){setChosen((values)=>values.includes(slot)?values:[...values,slot]);wrongTry("That tile already changes from the picture before it. Start at the left and keep checking.");return;}if(role!==correct){setChosen((values)=>values.includes(slot)?values:[...values,slot]);wrongTry("That replacement still leaves two matching pictures together. Try the other picture.");return;}finish();};
      return <MiniGame title={scene.gameTitle} icon={scene.gameIcon} progress="Find and repair one broken move"><div className="rule-repair-board"><div className="first-try-label"><strong>SOL&apos;S FIRST TRY</strong><span>It stays visible while you check.</span></div><div className="repair-row">{row.map((role,index)=><button key={index} className={chosen.includes(index)?"tried":""} onDragOver={(event)=>event.preventDefault()} onDrop={(event)=>repair(index,event.dataTransfer.getData("text/plain"))} onClick={()=>activityStep?repair(index,activityStep===1?"moon":"sun"):setWrong("Choose a replacement picture, then place it on the first broken spot.")}><span>{icons[role]}</span><b>Spot {index+1}</b></button>)}</div><div className="repair-parts">{(["moon","sun"] as const).map((role,index)=><button key={role} draggable onDragStart={(event)=>event.dataTransfer.setData("text/plain",role)} onClick={()=>setActivityStep(index+1)} className={activityStep===index+1?"selected":""}><span>{icons[role]}</span><b>{role.toUpperCase()} REPLACEMENT</b></button>)}</div></div></MiniGame>;
    }
    if (scene.activity === "bridge") {
      const startsOver=round%2===0;const path=Array.from({length:5},(_,index)=>((index+(startsOver?1:0))%2));const step=chosen.length;const lane=activityStep;
      const move=()=>{if(lane!==path[step]){wrongTry(`Vee met the closed ${lane?"over":"under"} gate and stopped safely. Change to the other path before crossing this arch.`);return;}const next=[...chosen,step];setChosen(next);sound("step");if(next.length===path.length)beginResolution("finish");};
      const veeToken = <img className="bridge-vee-token" src={image("vee")} alt="Vee" />;
      return <MiniGame title={scene.gameTitle} icon={scene.gameIcon} progress={`${step}/5 bridge arches`}><div className="bridge-runner"><div className="bridge-start-sign">FIRST SIGN: <b>{startsOver?"OVER":"UNDER"}</b></div><div className="bridge-lanes"><div className={lane===1?"vee-here":""}>OVER</div><div className={lane===0?"vee-here":""}>UNDER</div>{path.map((open,index)=><i key={index} className={index===step?"next":""} aria-label={`Arch ${index+1}: ${open?"over is open and under is closed":"under is open and over is closed"}`}><small>ARCH {index+1}</small><span className={open===1?"open":"closed"}>{index===step&&lane===1?veeToken:index<step&&open===1?"✓":open===1?"GO":"×"}</span><span className={open===0?"open":"closed"}>{index===step&&lane===0?veeToken:index<step&&open===0?"✓":open===0?"GO":"×"}</span></i>)}</div><div><button className={lane===1?"selected":""} onClick={()=>{setActivityStep(1);sound("tap");}}>Move Vee OVER</button><button className={lane===0?"selected":""} onClick={()=>{setActivityStep(0);sound("tap");}}>Move Vee UNDER</button><button className="cross-arch" onClick={move}>Cross this arch →</button></div></div></MiniGame>;
    }
    if (scene.activity === "routes") {
      const routes=[
        {id:1,name:"ROUTE A",kind:"short",lights:["moon","sun","moon"] as const,end:"STOP"},
        {id:2,name:"ROUTE B",kind:"broken",lights:["moon","sun","moon","moon","sun"] as const,end:"ARCH"},
        {id:3,name:"ROUTE C",kind:"complete",lights:["moon","sun","moon","sun","moon"] as const,end:"ARCH"},
      ];
      const ordered=round%3===0?routes:round%3===1?[routes[1],routes[2],routes[0]]:[routes[2],routes[0],routes[1]];
      const testRoute=(route:typeof routes[number])=>{setChosen((values)=>values.includes(route.id)?values:[...values,route.id]);sound("step");if(route.kind==="short"){wrongTry("This route takes turns, but it stops before the Sunrise Arch. Check where every route ends.");return;}if(route.kind==="broken"){wrongTry("This route reaches the arch, but two moon pictures meet. Check every move from left to right.");return;}beginResolution("finish");};
      return <MiniGame title={scene.gameTitle} icon={scene.gameIcon} progress={`${chosen.length}/3 maps tested`}><div className="route-compare"><div className="route-map-cards">{ordered.map(route=><button key={route.id} className={chosen.includes(route.id)?"tested":""} onClick={()=>testRoute(route)}><b>{route.name}</b><span className="route-lights">START {route.lights.map((role,index)=><i key={index}>{icons[role]}</i>)} {route.end==="ARCH"?"🌅":"⛔"}</span><small>{route.end==="ARCH"?"reaches the arch":"stops early"}</small></button>)}</div><p>Check the end. Then check every pair of lights.</p></div></MiniGame>;
    }
    if (scene.activity === "transfer") {
      const phase=activityStep;const sequence=relay.sequence;
      const press=(role:string)=>{if(phase===1){if(role!=="sun"){wrongTry("A blue moon went into the first gate. One turn showed the tile's other side. Try the other picture.");return;}beginResolution("finish");return;}const expected=sequence[chosen.length];if(role!==expected){wrongTry(`The first window already has a ${relay.start}. Look at it, then choose the other picture so they take turns.`);setChosen([]);return;}const next=[...chosen,role==="star"?1:2];setChosen(next);sound("tap");if(next.length===3)beginResolution("transfer-memory");};
      return <MiniGame title={scene.gameTitle} icon={scene.gameIcon} progress={phase===0?`Arch windows · ${chosen.length+1}/4`:"First-gate memory"}><div className="role-relay">{phase===0?<><div className="relay-track"><span className="lit given">{icons[relay.start]}</span>{sequence.map((role,index)=><span key={index} className={index<chosen.length?"lit":""}>{index<chosen.length?icons[role]:"?"}</span>)}</div><div>{(["star","leaf"] as const).map(role=><button key={role} onClick={()=>press(role)}><span>{icons[role]}</span><b>{role.toUpperCase()}</b></button>)}</div></>:<><div className="gate-memory-card"><strong>FIRST GATE</strong><span>{icons.moon} → ↻ → ?</span><small>Blue moon went in. The tile turned over once.</small></div><div>{(["moon","sun"] as const).map(role=><button key={role} onClick={()=>press(role)}><span>{icons[role]}</span><b>{role.toUpperCase()} CAME OUT</b></button>)}</div></>}</div></MiniGame>;
    }
    return null;
  }

  if (!storageReady) return <main className="restore-screen"><p>Returning to your adventure…</p></main>;

  if (introOpen) return <LevelPrelude
    levelClass="level-three-prelude"
    eyebrow="LEVEL THREE · THE LIGHT TRAIL"
    title="The Turning-Light Trail"
    subtitle="Carry the Moon Lantern's light into the garden and discover how one clear move can create, continue and repair a pattern."
    background="/art/stages/e03-source/e03-stage-01-trail-station-v1.png"
    lines={levelThreePrelude}
    characters={[
      { id: "mia", name: "Mia", image: image("mira") },
      { id: "tavi", name: "Tavi", image: image("tavi") },
      { id: "sol", name: "Sol", image: image("sol") },
    ]}
    discoveries={[<>↻ Turn a two-sided tile</>, <>🌙☀️ Work out what comes next</>, <>🛠️ Keep and repair a first try</>]}
    onSpeak={(current) => { startMusic(); playLine(current); }}
    onBegin={() => { stopNarration(audioRef, narrationGenerationRef, duckMusic); setIntroSeen(true); lastLineRef.current = ""; }}
    onExit={exitLevel}
    musicOn={musicOn}
    onToggleMusic={toggleMusic}
  />;

  if (finished) return <main className="ending-screen e03-ending">
    <div className="ending-art" /><button className="ending-home" onClick={exitLevel} aria-label="Choose a level">⌂ Levels</button><section><p className="eyebrow">LEVEL THREE COMPLETE</p><div className="e03-progress" aria-label="9 of 9 story steps complete">{scenes.map((_, index) => <span className="done" key={index}>●</span>)}</div><h1>The Sunrise Arch shines.</h1><p>Mia, Sol, Tavi and Vee restored the turning-light trail before sunrise.</p><blockquote>A clear move made a pattern. Keeping the first try helped the team find and repair the break.</blockquote><div className="ending-lesson"><span aria-hidden="true">📖</span><div><strong>NARRATOR TO YOU</strong><p>{endingLesson.text}</p></div><button onClick={() => playLine(endingLesson)}>Hear the lesson again</button></div><div className="ending-controls"><button className="primary" disabled title="Book Four and Level Four are in development">Next level · coming soon</button><button className="secondary" onClick={restart}>Play Level 3 again</button><button className="secondary" onClick={exitLevel}>Choose a level</button><button className="secondary" onClick={toggleMusic}>{musicOn ? "Turn music off" : "Turn music on"}</button></div></section>
  </main>;

  const promptText = scene.activity === "transfer" && activityStep === 1
    ? "At the first gate, a blue moon went in and the tile turned over once. Which side came out?"
    : scene.activity === "transfer"
      ? `The first window already has a ${relay.start}. Fill the other three so star and leaf take turns. Then answer the one-turn memory card.`
      : scene.prompt;

  return <main className="game-shell level-three-shell">
    <header className="game-hud e03-hud">
      <div><span className="eyebrow">THE TURNING-LIGHT TRAIL</span><strong>{scene.title}</strong></div>
      <div className="e03-progress" aria-label={`${sceneIndex + (complete ? 1 : 0)} of 9 story steps complete`}>{scenes.map((_, index) => <span key={index} className={index < sceneIndex || (index === sceneIndex && complete) ? "done" : index === sceneIndex ? "now" : ""}>●</span>)}</div>
      <nav><button onClick={exitLevel} aria-label="Choose a level">⌂ <span>Levels</span></button><button onClick={() => playLine()} aria-label="Replay narration">↻ <span>Hear again</span></button><button onClick={toggleNarration} aria-pressed={muted}>{muted ? "🔇" : "🔊"} <span>{muted ? "Narration off" : "Narration on"}</span></button><button onClick={toggleMusic} aria-pressed={musicOn}>{musicOn ? "♫" : "♩"} <span>{musicOn ? "Music on" : "Music off"}</span></button><button onClick={restart} aria-label="Restart Level Three">↺ <span>Start over</span></button><button onClick={() => setCodesOpen(true)}>⌨ <span>Book code</span></button></nav>
    </header>
    <section key={scene.id} className={`play-stage e03-stage scene-e03-${scene.id}`} style={{ backgroundImage: `url('/art/stages/${scene.background}')` }} aria-label={`${scene.title}, an animated turning-light story scene`}>
      <div className="stage-light" />
      {beat === 0 && scene.journey && <div className="journey-banner"><span aria-hidden="true">→</span><strong>{scene.journey}</strong></div>}
      {scene.introduces && beat <= 1 && <div className="guest-banner">New friend for Level Three: <strong>{names[scene.introduces]}</strong></div>}
      {scene.id === "trail" && !dialogueDone && <div className="story-moon-lantern" role="img" aria-label="The Moon Lantern beside the garden path"><strong>MOON LANTERN</strong><span aria-hidden="true">🏮</span></div>}
      <div className="walking-cast" aria-hidden="true">{scene.cast.map((name, index) => <CharacterSprite key={name} name={name} index={index} speaking={speaking === name} />)}</div>
      {dialogueDone && !complete && <div className="activity-layer"><TryLights mistakes={mistakes}/>{!roundLost && <fieldset className="resolution-lock" disabled={resolving} aria-busy={resolving}>{activity()}</fieldset>}{wrong && <p className="e03-feedback" role="status">{wrong}</p>}{roundLost && <section className="round-lost" role="alert"><span aria-hidden="true">◆ ◆ ◆</span><h2>Round over</h2><p>That round used all three try lights. The story is safe. Change your plan and try this puzzle again.</p><button onClick={retryRound}>Try a new board</button></section>}</div>}
      <aside className={`speech-panel ${dialogueDone && !complete ? "prompting" : ""} ${complete ? "completed" : ""}`} aria-live="polite">
        {!dialogueDone || complete ? <><div className="speaker-portrait"><Portrait speaker={line.speaker} /></div><span className="speaker">{complete ? "NARRATOR · WHAT YOU DISCOVERED" : line.speaker}</span><p>{line.text}</p>{complete ? <div className="completion-controls"><button className="replay-control" onClick={replay}><span aria-hidden="true">↻</span> Play again</button><button className="next-control" onClick={nextScene}>{sceneIndex === scenes.length - 1 ? "Light the arch" : "Follow the trail"} <span aria-hidden="true">→</span></button></div> : <button className="next-control" onClick={nextBeat}>Next <span aria-hidden="true">→</span></button>}</> : <><div className="speaker-portrait prompt-portrait" aria-hidden="true">☝️</div><span className="speaker">YOUR TURN</span><p>{promptText}</p><span className="action-nudge" aria-hidden="true">↑ Try it in the scene</span></>}
      </aside>
    </section>
    {codesOpen && <div className="modal-backdrop" role="presentation" onMouseDown={() => setCodesOpen(false)}><section className="code-modal" role="dialog" aria-modal="true" aria-labelledby="e03-code-title" onMouseDown={(event) => event.stopPropagation()}><button className="close-modal" onClick={() => setCodesOpen(false)} aria-label="Close">×</button><p className="eyebrow">OPTIONAL BOOK SECRET</p><h2 id="e03-code-title">Mia’s code pocket</h2><p>Codes unlock jokes and small previews. They never give an answer or skip a lesson.</p><form onSubmit={submitCode}><label htmlFor="e03-book-code">Code from Book Three</label><div><input id="e03-book-code" value={code} onChange={(event) => setCode(event.target.value)} autoComplete="off" /><button>Open</button></div></form>{unlockedCode && <div className="code-treat" role="img" aria-label="A harmless animated book-code surprise">{codeTreats[unlockedCode]}</div>}<p className="code-result" aria-live="polite">{codeMessage}</p></section></div>}
  </main>;
}
