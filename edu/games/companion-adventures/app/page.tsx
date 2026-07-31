"use client";

import { CSSProperties, FormEvent, PointerEvent, useEffect, useLayoutEffect, useRef, useState } from "react";
import LevelTwo from "./level-two";
import LevelThree from "./level-three";
import LevelFour from "./level-four";
import LevelPrelude, { PreludeLine } from "./level-prelude";
import { startNarration, stopNarration } from "./narration-controller.mjs";
import useLevelMusic from "./use-level-music";
import {
  claimLevelOneCompletion,
  LEVEL_ONE_STORAGE_KEY,
  levelOneRoundSetup,
  pendingLevelOneResolution,
  restoreLevelOneProgress,
  snapshotLevelOneProgress,
} from "./level-one-state.mjs";

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
    id: "note", title: "A note arrives", background: "e01-stage-01-observatory-v1.png", cast: ["mira", "tavi", "sol"], activity: "note",
    lines: [
      { speaker: "Narrator", text: "Mia, Sol and Tavi stepped into the Star Room. At the far end, the Star Door was closed.", audio: "01-narrator-door-shut" },
      { speaker: "Narrator", text: "A note slid through the letter box and landed on the floor beside Mia.", audio: "02-narrator-note-through-letter-box" },
      { speaker: "Narrator", text: "Mia saw the note, picked it up and opened it.", audio: "03-narrator-mira-picks-up-note" },
      { speaker: "Mia", text: "A note! It says, ‘Find nothing. Five clues will show the way.’", audio: "04-mira-finds-and-reads-note" },
      { speaker: "Sol", text: "Find nothing? How do we look for that? Let's follow the clues and find out!", audio: "05-sol-strange-mystery" },
      { speaker: "Tavi", text: "We will look carefully and say what we really find. First, can you spot Mia's note?", audio: "06-tavi-spot-note" },
    ],
    prompt: "A note is a short message written on paper. Tap Mia's note.",
    success: { speaker: "Narrator", text: "You found the note by looking for a sheet of paper with writing on it. Clear names help us tell one object from another. The five empty star shapes will show your progress. The first clue points to the parcel.", audio: "07-mira-star-map" },
  },
  {
    id: "box", title: "The parcel clue", background: "e01-stage-01-observatory-v1.png", cast: ["mira", "tavi", "sol"], journey: "The first arrow points across the star room to the parcel.", activity: "box", star: 1,
    lines: [
      { speaker: "Narrator", text: "The friends followed the arrow across the room. It pointed to a parcel.", audio: "08-narrator-to-parcel" },
      { speaker: "Sol", text: "I opened the parcel. Look! My brown teddy is inside.", audio: "09-sol-sees-toy" },
      { speaker: "Tavi", text: "The first clue says to move the teddy. Tap the toy to lift it out. Then tap the box and look inside.", audio: "10-tavi-move-then-look" },
    ],
    prompt: "First move the teddy outside. Then tap the box and look inside.",
    success: { speaker: "Narrator", text: "You moved the teddy out and looked inside. The box is empty. Empty means the teddy is not inside the box now. The box is still here. This clue teaches us that empty and nothing do not mean the same thing.", audio: "11-tavi-empty-defined" },
  },
  {
    id: "bell", title: "Meet Nori in the bell room", background: "e01-stage-02-bell-gallery-v1.png", cast: ["mira", "tavi", "sol", "nori"], journey: "The box was still there, so the next arrow leads to the bell room.", introduces: "nori", activity: "bell", star: 2,
    lines: [
      { speaker: "Narrator", text: "They had found an empty box, not a thing called nothing. The first star turned gold. A blue door opened.", audio: "12-narrator-first-star-door" },
      { speaker: "Narrator", text: "The friends went through the door. They entered a room with three big bells.", audio: "13-narrator-enter-bells" },
      { speaker: "Nori", text: "Hello! I am Nori. I listen for tiny sounds. May I help you check the bell room?", audio: "14-nori-meets" },
      { speaker: "Mia", text: "Yes, please. The note tells us to find nothing. We found an empty box in the first room. Let's check the bells next.", audio: "15-mira-welcome" },
      { speaker: "Nori", text: "The wind stopped, and the big bell stopped moving. Hold the bell while we stay quiet and listen.", audio: "16-nori-listen" },
    ],
    prompt: "Press and hold the big bell while everyone listens.",
    success: { speaker: "Narrator", text: "You held the bell still and listened. The bell made no ringing sound, so it was quiet. The bell was still in the room. This clue teaches us that no bell sound is not the same as no bell.", audio: "17-nori-no-ring" },
  },
  {
    id: "card", title: "The paper room", background: "e01-stage-03-paper-room-v1.png", cast: ["mira", "tavi", "sol", "nori"], journey: "The bell stayed in the room, so everyone follows the next arrow to the paper room.", activity: "card", star: 3,
    lines: [
      { speaker: "Narrator", text: "The bell did not ring, but it was still there. The second star turned gold. A door opened to the paper room.", audio: "18-narrator-to-paper" },
      { speaker: "Mia", text: "I found a white card on this table. Look, there are no marks on it yet.", audio: "19-mira-finds-card" },
      { speaker: "Tavi", text: "Touch the card. You can draw a mark, or choose Leave blank and do not draw.", audio: "20-tavi-draw-or-leave" },
    ],
    prompt: "Draw on the card—or leave it blank—then check.",
    success: { speaker: "Narrator", text: "A card with no mark is called blank. If you drew, the mark appeared on the card. If you left it blank, the card stayed there without a mark. This clue teaches us to say what is missing and what is still present.", audio: "21-mira-card-result" },
  },
  {
    id: "word", title: "Seven glowing letters", background: "e01-stage-03-paper-room-v1.png", cast: ["mira", "tavi", "sol", "nori"], journey: "The card stayed there, so seven wall tiles light up for the next clue.", activity: "word", star: 4,
    lines: [
      { speaker: "Narrator", text: "The card stayed there with or without a mark. The third star lit. Then seven wall tiles lit up, one after another.", audio: "22-narrator-to-word" },
      { speaker: "Sol", text: "Each glowing tile shows one letter. Read them from left to right with me!", audio: "23-sol-step" },
    ],
    prompt: "Tap the letters in order to spell NOTHING.",
    success: { speaker: "Narrator", text: "You put seven letters in order to spell NOTHING. The written word is something we can see and read. This clue teaches us that a word can name an idea without becoming the thing it names.", audio: "24-tavi-word" },
  },
  {
    id: "curtain", title: "Behind the curtain", background: "e01-stage-04-curtain-passage-v1.png", cast: ["mira", "tavi", "sol", "nori"], journey: "The word stayed visible, so a golden arrow leads everyone to the curtain passage.", activity: "curtain", star: 5,
    lines: [
      { speaker: "Narrator", text: "The written word stayed on the tiles, so the fourth star lit. A gold arrow appeared on the floor and led the friends to a red curtain.", audio: "25-narrator-to-curtain" },
      { speaker: "Sol", text: "My teddy rolled out of my bag! It crossed the floor and went behind the curtain. I saw where it went, but I cannot see it now!", audio: "26-sol-curtain" },
      { speaker: "Nori", text: "Slide the curtain slowly. Let's see what is behind it.", audio: "27-nori-curtain" },
    ],
    prompt: "Slowly slide the curtain open and watch for the toy.",
    success: { speaker: "Narrator", text: "There is the teddy. It was hidden: the curtain stopped you from seeing it, but the teddy stayed behind the curtain. This clue teaches us that hidden and gone do not mean the same thing.", audio: "28-mira-hidden" },
  },
  {
    id: "doors", title: "The final question", background: "e01-stage-05-star-door-v1.png", cast: ["mira", "tavi", "sol", "nori"], journey: "Five clues are complete, so five bright stars open the Star Door.", activity: "doors",
    lines: [
      { speaker: "Narrator", text: "Opening the curtain showed the teddy. The fifth star turned gold. Now all five stars were gold, and the Star Door opened.", audio: "29-narrator-to-doors" },
      { speaker: "Narrator", text: "Behind the Star Door were two small doors, marked A and B. The friends could not see what was behind them yet.", audio: "30-narrator-two-doors" },
      { speaker: "Mia", text: "My note still says, Find nothing. Tap both small doors. We must look at each one before we answer.", audio: "31-mira-question" },
    ],
    prompt: "Look behind both little doors before choosing.",
    success: { speaker: "Narrator", text: "You checked both doors before answering. One held a card. The other held an empty shelf. Neither showed a thing called nothing. This teaches us to look at all the evidence before we decide.", audio: "32-tavi-neither" },
  },
  {
    id: "recall", title: "The map remembers", background: "e01-stage-06-library-v1.png", cast: ["mira", "tavi", "sol", "nori"], journey: "The mystery is solved, so the friends carry their map to the library and remember the journey.", activity: "recall",
    lines: [
      { speaker: "Narrator", text: "The friends solved the note's puzzle. Mia folded the note. Everyone carried the five-star map into the library before going home.", audio: "33-narrator-library" },
      { speaker: "Tavi", text: "Before we put the map away, let's remember the first clue. Which thing became empty after you moved Sol's teddy outside?", audio: "34-tavi-remember" },
    ],
    prompt: "Tap the thing that became empty in the first clue.",
    success: { speaker: "Narrator", text: "You remembered that the box became empty when the teddy moved out. Remembering an earlier clue helps us check what we learned. Mia placed the finished map on the library stand. A hidden ramp opened, and a new parcel slid down beside it. Their next adventure had arrived.", audio: "35-mira-ending" },
  },
];

const levelOnePrelude: PreludeLine[] = [
  { speaker: "Narrator", heading: "A door to another world", text: "Somewhere between an ordinary morning and a sky full of stars, a little door waits for curious explorers. Beyond it is the Star House, where every question can become an adventure.", audio: "00a-narrator-world" },
  { speaker: "Narrator", heading: "Meet Mia", text: "This is Mia. She looks closely, asks what words mean, and makes sure the team never rushes past an important clue.", audio: "00b-narrator-meet-mia" },
  { speaker: "Narrator", heading: "Meet Sol and Tavi", text: "Sol loves to try things and make his friends laugh. Tavi remembers what the team has already found. Together with Mia, they are the Star House adventure team.", audio: "00c-narrator-meet-sol-tavi" },
  { speaker: "Narrator", heading: "You are part of the team", text: "Today, a mysterious note will ask you to find nothing. You will look, listen, move objects and peek behind hiding places. Help the friends say exactly what they find.", audio: "00d-narrator-your-adventure" },
];

const codes: Record<string, string> = {
  ROOMSTAR: "Mia finds a tiny practice star tucked under the route map.",
  BOXCLUE: "Sol's joke: an empty box can still be full of clues.",
  QUIETWINGS: "Nori teaches the trio a quiet listening wave.",
  BLANKEDGE: "Tavi finds a tiny sketchbook pocket.",
  CURTAINMAP: "The curtain stitches glow like a route map.",
  TWODOORS: "The next parcel whispers: one whole can have many parts.",
};

const characterNames: Record<Character, string> = { mira: "Mia", tavi: "Tavi", sol: "Sol", nori: "Nori" };
const endingLesson: Line = { speaker: "Narrator", text: "Here is what you learned. We never found a thing called nothing. We found an empty box, a quiet bell, a blank card, the written word nothing and a hidden teddy. Each time, something was still there. This matters because words such as empty, quiet, blank and hidden tell people exactly what you observed.", audio: "36-narrator-to-you" };
const characterImage = (name: Character) => name === "mira" ? "/art/characters/individual/mira-v1.png" : `/art/characters/individual/${name}.png`;

function CharacterSprite({ name, speaking, index }: { name: Character; speaking: boolean; index: number }) {
  return <div className={`actor actor-${name} ${speaking ? "speaking" : ""}`} style={{ "--actor-index": index } as CSSProperties}>
    <img src={characterImage(name)} alt="" draggable={false} /><span>{characterNames[name]}</span>
  </div>;
}

function SpeakerPortrait({ speaker }: { speaker: string }) {
  const id = (speaker.toLowerCase() === "mia" ? "mira" : speaker.toLowerCase()) as Character;
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
  const [levelThreeActive, setLevelThreeActive] = useState(false);
  const [savedLevelThreeStages, setSavedLevelThreeStages] = useState(0);
  const [levelFourActive, setLevelFourActive] = useState(false);
  const [savedLevelFourStages, setSavedLevelFourStages] = useState(0);
  const [started, setStarted] = useState(false);
  const [introOpen, setIntroOpen] = useState(true);
  const [preludeStep, setPreludeStep] = useState(-1);
  const [sceneIndex, setSceneIndex] = useState(0);
  const [beat, setBeat] = useState(0);
  const [activityStep, setActivityStep] = useState(0);
  const [complete, setComplete] = useState(false);
  const [finished, setFinished] = useState(false);
  const [muted, setMuted] = useState(false);
  const [journalOpen, setJournalOpen] = useState(false);
  const [freshGameOpen, setFreshGameOpen] = useState(false);
  const [code, setCode] = useState("");
  const [codeMessage, setCodeMessage] = useState("");
  const [letters, setLetters] = useState(0);
  const [curtain, setCurtain] = useState(0);
  const [doors, setDoors] = useState<string[]>([]);
  const [drawn, setDrawn] = useState(false);
  const [cardOpen, setCardOpen] = useState(false);
  const [cardInk, setCardInk] = useState("");
  const [round, setRound] = useState(0);
  const [resolution, setResolution] = useState<"finish" | null>(null);
  const [feedback, setFeedback] = useState("");
  const [savedStars, setSavedStars] = useState(0);
  const [earnedStar, setEarnedStar] = useState<number | null>(null);
  const [storageReady, setStorageReady] = useState(false);
  const audioRef = useRef<HTMLAudioElement | null>(null);
  const canvasRef = useRef<HTMLCanvasElement | null>(null);
  const drawingRef = useRef(false);
  const bellHoldRef = useRef(false);
  const curtainRevealRef = useRef(false);
  const soundContextRef = useRef<AudioContext | null>(null);
  const lastAutoLineRef = useRef("");
  const narrationGenerationRef = useRef(0);
  const endingLessonPlayedRef = useRef(false);
  const progressRef = useRef<Record<string, unknown>>({});
  const completionLockRef = useRef(false);
  const resolutionRef = useRef<"finish" | null>(null);
  const feedbackTimerRef = useRef<number | null>(null);
  const rewardTimerRef = useRef<number | null>(null);
  const { enabled: musicOn, start: startMusic, stop: stopMusic, toggle: toggleMusic, duck: duckMusic } = useLevelMusic("level-one");

  const scene = scenes[sceneIndex];
  const dialogueDone = beat >= scene.lines.length;
  const currentLine = complete ? scene.success : scene.lines[Math.min(beat, scene.lines.length - 1)];
  const speakingName = (!dialogueDone || complete) ? (currentLine?.speaker.toLowerCase() === "mia" ? "mira" : currentLine?.speaker.toLowerCase()) : "";
  const starCount = Math.max(savedStars, scenes.slice(0, sceneIndex + (complete ? 1 : 0)).filter((item) => item.star).length);
  const roundSetup = levelOneRoundSetup(round);
  const pendingResolution = complete ? null : pendingLevelOneResolution(scene.activity, { resolution, letters, curtain, activityStep, doors });
  const resolving = pendingResolution === "finish";

  useEffect(() => {
    if (!storageReady) return;
    if (levelTwoActive || levelThreeActive || levelFourActive) {
      stopMusic();
      return;
    }
    startMusic();
  }, [storageReady, levelTwoActive, levelThreeActive, levelFourActive, startMusic, stopMusic]);

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
    completionLockRef.current = complete;
    resolutionRef.current = resolution;
    progressRef.current = snapshotLevelOneProgress({
      started, introOpen, preludeStep, finished, sceneIndex, beat, activityStep, complete,
      stars: starCount, letters, curtain, doors, drawn, cardOpen, cardInk, round, resolution,
    }, scenes.length, levelOnePrelude.length);
  }, [started, introOpen, preludeStep, finished, sceneIndex, beat, activityStep, complete, starCount, letters, curtain, doors, drawn, cardOpen, cardInk, round, resolution]);

  useEffect(() => () => {
    if (feedbackTimerRef.current !== null) window.clearTimeout(feedbackTimerRef.current);
    if (rewardTimerRef.current !== null) window.clearTimeout(rewardTimerRef.current);
  }, []);

  useEffect(() => {
    if (scene.activity !== "card" || !cardOpen || !cardInk || !canvasRef.current) return;
    const canvas = canvasRef.current;
    const image = new Image();
    let cancelled = false;
    image.onload = () => {
      if (cancelled) return;
      const context = canvas.getContext("2d");
      context?.clearRect(0, 0, canvas.width, canvas.height);
      context?.drawImage(image, 0, 0, canvas.width, canvas.height);
    };
    image.src = cardInk;
    return () => { cancelled = true; };
  }, [scene.activity, cardOpen, cardInk]);

  function playLine(line = currentLine) {
    if (!line || muted) return;
    startNarration({
      src: `/audio/e01-v1.6.0/${line.audio}.mp3?v=e01-story-20260731c`,
      audioRef,
      generationRef: narrationGenerationRef,
      duckMusic,
    });
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
    if (finished) return;
    if (!started || introOpen || !currentLine || (dialogueDone && !complete)) {
      stopNarration(audioRef, narrationGenerationRef, duckMusic);
      return;
    }
    const lineKey = `${sceneIndex}:${complete ? "success" : beat}`;
    const scheduledGeneration = narrationGenerationRef.current;
    const timeout = window.setTimeout(() => {
      if (document.visibilityState !== "visible") return;
      if (narrationGenerationRef.current !== scheduledGeneration) return;
      if (lastAutoLineRef.current === lineKey) return;
      lastAutoLineRef.current = lineKey;
      playLine(currentLine);
    }, 25);
    return () => { window.clearTimeout(timeout); stopNarration(audioRef, narrationGenerationRef, duckMusic); };
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [started, finished, introOpen, sceneIndex, beat, complete, muted]);

  useEffect(() => {
    if (!storageReady || !started || levelTwoActive || levelThreeActive || levelFourActive || !finished || muted || endingLessonPlayedRef.current) return;
    endingLessonPlayedRef.current = true;
    let lessonAudio: HTMLAudioElement | null = null;
    const scheduledGeneration = narrationGenerationRef.current;
    const timeout = window.setTimeout(() => {
      if (document.visibilityState !== "visible") return;
      if (narrationGenerationRef.current !== scheduledGeneration) return;
      if (audioRef.current && !audioRef.current.paused) return;
      lessonAudio = startNarration({
        src: `/audio/e01-v1.6.0/${endingLesson.audio}.mp3?v=e01-story-20260731c`,
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
  }, [storageReady, started, levelTwoActive, levelThreeActive, levelFourActive, finished, muted, duckMusic]);

  useEffect(() => {
    const timeout = window.setTimeout(() => {
      try {
        const activeLevel = localStorage.getItem("sft-active-level-v1");
        const saved = restoreLevelOneProgress(localStorage.getItem(LEVEL_ONE_STORAGE_KEY), scenes.length, levelOnePrelude.length);
        const savedLevelTwo = JSON.parse(localStorage.getItem("sft-e02-moving-stage-v1") ?? "{}");
        const savedLevelThree = JSON.parse(localStorage.getItem("sft-e03-moving-stage-v1") ?? "{}");
        const savedLevelFour = JSON.parse(localStorage.getItem("sft-e04-garden-check-v1") ?? "{}");
        lastAutoLineRef.current = saved.started && !saved.introOpen && !saved.finished ? `${saved.sceneIndex}:${saved.complete ? "success" : saved.beat}` : "";
        endingLessonPlayedRef.current = saved.finished;
        setSceneIndex(saved.sceneIndex);
        setBeat(saved.beat);
        setActivityStep(saved.activityStep);
        setComplete(saved.complete);
        setFinished(saved.finished);
        setIntroOpen(saved.introOpen);
        setPreludeStep(saved.preludeStep);
        setRound(saved.round);
        setResolution(saved.resolution);
        resolutionRef.current = saved.resolution;
        completionLockRef.current = saved.complete;
        if (activeLevel === "e04") setLevelFourActive(true);
        else if (activeLevel === "e03") setLevelThreeActive(true);
        else if (activeLevel === "e02") setLevelTwoActive(true);
        else if (activeLevel === "select") setStarted(false);
        else setStarted(saved.started);
        setSavedStars(saved.stars);
        setLetters(saved.letters);
        setCurtain(saved.curtain);
        setDoors(saved.doors);
        setDrawn(saved.drawn);
        setCardOpen(saved.cardOpen);
        setCardInk(saved.cardInk);
        if (savedLevelTwo.finished === true) setSavedLevelTwoRooms(9);
        else if (typeof savedLevelTwo.sceneIndex === "number") setSavedLevelTwoRooms(Math.max(0, Math.min(9, savedLevelTwo.sceneIndex + (savedLevelTwo.complete ? 1 : 0))));
        if (savedLevelThree.finished === true) setSavedLevelThreeStages(9);
        else if (typeof savedLevelThree.sceneIndex === "number") setSavedLevelThreeStages(Math.max(0, Math.min(9, savedLevelThree.sceneIndex + (savedLevelThree.complete ? 1 : 0))));
        if (savedLevelFour.finished === true) setSavedLevelFourStages(9);
        else if (typeof savedLevelFour.sceneIndex === "number") setSavedLevelFourStages(Math.max(0, Math.min(9, savedLevelFour.sceneIndex + (savedLevelFour.complete ? 1 : 0))));
      } catch { /* The story also works without local saving. */ }
      setStorageReady(true);
    }, 0);
    return () => window.clearTimeout(timeout);
  }, []);

  useEffect(() => {
    if (!storageReady) return;
    try {
      localStorage.setItem(LEVEL_ONE_STORAGE_KEY, JSON.stringify(progressRef.current));
    } catch { /* optional */ }
  }, [storageReady, started, introOpen, preludeStep, finished, sceneIndex, beat, activityStep, complete, starCount, letters, curtain, doors, drawn, cardOpen, cardInk, round, resolution]);

  useEffect(() => {
    if (!storageReady) return;
    const saveNow = () => {
      try { localStorage.setItem(LEVEL_ONE_STORAGE_KEY, JSON.stringify(progressRef.current)); } catch { /* optional */ }
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
    clearFeedback();
    if (beat < scene.lines.length) setBeat((value) => value + 1);
  }

  function clearFeedback() {
    if (feedbackTimerRef.current !== null) window.clearTimeout(feedbackTimerRef.current);
    feedbackTimerRef.current = null;
    setFeedback("");
  }

  function showFeedback(message: string) {
    clearFeedback();
    setFeedback(message);
    feedbackTimerRef.current = window.setTimeout(() => {
      setFeedback("");
      feedbackTimerRef.current = null;
    }, 3600);
  }

  function beginResolution() {
    if (complete || resolutionRef.current === "finish") return;
    clearFeedback();
    resolutionRef.current = "finish";
    progressRef.current = snapshotLevelOneProgress({ ...progressRef.current, resolution: "finish" }, scenes.length, levelOnePrelude.length);
    setResolution("finish");
  }

  function finishActivity() {
    if (!claimLevelOneCompletion(completionLockRef)) return;
    clearFeedback();
    resolutionRef.current = null;
    setResolution(null);
    playEffect(scene.star ? "star" : "tap");
    setComplete(true);
    if (scene.star) {
      setSavedStars((value) => Math.max(value, scene.star ?? value));
      setEarnedStar(scene.star);
      if (rewardTimerRef.current !== null) window.clearTimeout(rewardTimerRef.current);
      rewardTimerRef.current = window.setTimeout(() => {
        setEarnedStar(null);
        rewardTimerRef.current = null;
      }, 2400);
    }
  }

  useEffect(() => {
    if (pendingResolution !== "finish" || complete) return;
    const delay = scene.activity === "curtain" ? 3200 : scene.activity === "doors" ? 900 : scene.activity === "word" ? 650 : 0;
    const timeout = window.setTimeout(() => finishActivity(), delay);
    return () => window.clearTimeout(timeout);
    // finishActivity deliberately resolves the current render's scene once.
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [pendingResolution, complete, scene.activity]);

  function resetActivityRound() {
    stopNarration(audioRef, narrationGenerationRef, duckMusic);
    lastAutoLineRef.current = "";
    completionLockRef.current = false;
    resolutionRef.current = null;
    bellHoldRef.current = false;
    setComplete(false); setResolution(null); setActivityStep(0); setLetters(0); setCurtain(0); setDoors([]); setDrawn(false); setCardOpen(false); setCardInk(""); setEarnedStar(null); setRound((value) => value + 1);
    const canvas = canvasRef.current;
    canvas?.getContext("2d")?.clearRect(0, 0, canvas.width, canvas.height);
    clearFeedback();
    curtainRevealRef.current = false;
  }

  function replayActivity() {
    resetActivityRound();
  }

  function retryRound() {
    playEffect("tap");
    resetActivityRound();
  }

  function nextScene() {
    playEffect("step");
    if (sceneIndex === scenes.length - 1) {
      stopNarration(audioRef, narrationGenerationRef, duckMusic);
      endingLessonPlayedRef.current = false;
      setFinished(true);
      try { localStorage.setItem("sft-active-level-v1", "e01"); } catch { /* optional */ }
      return;
    }
    completionLockRef.current = false;
    resolutionRef.current = null;
    setSceneIndex((value) => value + 1);
    setBeat(0); setActivityStep(0); setComplete(false); setResolution(null); setLetters(0); setCurtain(0); setDoors([]); setDrawn(false); setCardOpen(false); setCardInk(""); setEarnedStar(null); setRound(0);
    clearFeedback();
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

  function finishDrawing() {
    drawingRef.current = false;
    const canvas = canvasRef.current;
    if (canvas) setCardInk(canvas.toDataURL("image/png"));
  }

  function submitCode(event: FormEvent) {
    event.preventDefault();
    const clean = code.toUpperCase().replace(/[^A-Z]/g, "");
    setCodeMessage(codes[clean] ?? "That code is sleeping in another book page. Keep looking.");
    if (codes[clean]) setCode("");
  }

  function toggleNarration() {
    const next = !muted;
    setMuted(next);
    if (next) stopNarration(audioRef, narrationGenerationRef, duckMusic);
  }

  function restart() {
    stopNarration(audioRef, narrationGenerationRef, duckMusic); setStarted(true); setIntroOpen(true); setPreludeStep(-1); setFinished(false); setSceneIndex(0); setBeat(0); setActivityStep(0); setComplete(false); setResolution(null); setSavedStars(0); setLetters(0); setCurtain(0); setDoors([]); setDrawn(false); setCardOpen(false); setCardInk(""); setRound(0); setEarnedStar(null);
    lastAutoLineRef.current = "";
    endingLessonPlayedRef.current = false;
    completionLockRef.current = false;
    resolutionRef.current = null;
    bellHoldRef.current = false;
    clearFeedback();
    curtainRevealRef.current = false;
    try {
      localStorage.removeItem(LEVEL_ONE_STORAGE_KEY);
      localStorage.setItem("sft-active-level-v1", "e01");
    } catch { /* optional */ }
  }

  function beginLevelOne() {
    setStarted(true);
    startMusic();
    try { localStorage.setItem("sft-active-level-v1", "e01"); } catch { /* optional */ }
  }

  function beginLevelTwo() {
    stopNarration(audioRef, narrationGenerationRef, duckMusic); stopMusic(); setStarted(false);
    try {
      localStorage.setItem("sft-active-level-v1", "e02");
    } catch { /* optional */ }
    setLevelTwoActive(true);
  }

  function beginLevelThree() {
    stopNarration(audioRef, narrationGenerationRef, duckMusic); stopMusic(); setStarted(false);
    try {
      localStorage.setItem("sft-active-level-v1", "e03");
    } catch { /* optional */ }
    setLevelThreeActive(true);
  }

  function beginLevelFour() {
    stopNarration(audioRef, narrationGenerationRef, duckMusic); stopMusic(); setStarted(false);
    try {
      localStorage.setItem("sft-active-level-v1", "e04");
    } catch { /* optional */ }
    setLevelThreeActive(false);
    setLevelFourActive(true);
  }

  function showLevelSelect() {
    stopNarration(audioRef, narrationGenerationRef, duckMusic); setStarted(false); setLevelTwoActive(false); setLevelThreeActive(false); setLevelFourActive(false); setJournalOpen(false); startMusic();
    try {
      localStorage.setItem("sft-active-level-v1", "select");
      const savedLevelTwo = JSON.parse(localStorage.getItem("sft-e02-moving-stage-v1") ?? "{}");
      if (savedLevelTwo.finished === true) setSavedLevelTwoRooms(9);
      else if (typeof savedLevelTwo.sceneIndex === "number") setSavedLevelTwoRooms(Math.max(0, Math.min(9, savedLevelTwo.sceneIndex + (savedLevelTwo.complete ? 1 : 0))));
      const savedLevelThree = JSON.parse(localStorage.getItem("sft-e03-moving-stage-v1") ?? "{}");
      if (savedLevelThree.finished === true) setSavedLevelThreeStages(9);
      else if (typeof savedLevelThree.sceneIndex === "number") setSavedLevelThreeStages(Math.max(0, Math.min(9, savedLevelThree.sceneIndex + (savedLevelThree.complete ? 1 : 0))));
      const savedLevelFour = JSON.parse(localStorage.getItem("sft-e04-garden-check-v1") ?? "{}");
      if (savedLevelFour.finished === true) setSavedLevelFourStages(9);
      else if (typeof savedLevelFour.sceneIndex === "number") setSavedLevelFourStages(Math.max(0, Math.min(9, savedLevelFour.sceneIndex + (savedLevelFour.complete ? 1 : 0))));
    } catch { /* optional */ }
  }

  function playTitleMusic() {
    if (musicOn) startMusic();
    else toggleMusic();
  }

  function startFreshGame() {
    stopNarration(audioRef, narrationGenerationRef, duckMusic);
    startMusic();
    setLevelTwoActive(false);
    setLevelThreeActive(false);
    setLevelFourActive(false);
    setStarted(false);
    setIntroOpen(true);
    setPreludeStep(-1);
    setFinished(false);
    setSceneIndex(0);
    setBeat(0);
    setActivityStep(0);
    setComplete(false);
    setLetters(0);
    setCurtain(0);
    setDoors([]);
    setDrawn(false);
    setCardOpen(false);
    setCardInk("");
    setRound(0);
    setResolution(null);
    setSavedStars(0);
    setSavedLevelTwoRooms(0);
    setSavedLevelThreeStages(0);
    setSavedLevelFourStages(0);
    setEarnedStar(null);
    setCode("");
    setCodeMessage("");
    lastAutoLineRef.current = "";
    endingLessonPlayedRef.current = false;
    completionLockRef.current = false;
    resolutionRef.current = null;
    bellHoldRef.current = false;
    clearFeedback();
    try {
      localStorage.removeItem(LEVEL_ONE_STORAGE_KEY);
      localStorage.removeItem("sft-e02-moving-stage-v1");
      localStorage.removeItem("sft-e03-moving-stage-v1");
      localStorage.removeItem("sft-e04-garden-check-v1");
      localStorage.setItem("sft-active-level-v1", "select");
    } catch { /* A fresh in-memory game still begins if storage is unavailable. */ }
    setFreshGameOpen(false);
  }

  function activity() {
    if (complete) return null;
    if (scene.activity === "note") {
      const choices = {
        map: { emoji: "🗺️", label: "Map", aria: "Choose the route map" },
        book: { emoji: "📘", label: "Book", aria: "Choose the blue book" },
        note: { emoji: "📝", label: "Note", aria: "Choose the written note" },
      } as const;
      return <div className="note-search" aria-label="Find the note among three things">
        {(roundSetup.noteOrder as Array<keyof typeof choices>).map((kind, index) => {
          const choice = choices[kind];
          return <button key={kind} className={`emoji-prop note-choice note-${kind} note-slot-${index} ${kind === "note" ? "pulse" : ""}`} onClick={() => {
            if (kind === "note") { playEffect("rustle"); beginResolution(); return; }
            playEffect("tap");
            showFeedback(`That is the ${choice.label.toLowerCase()}. Which thing is one sheet of paper with writing on it?`);
          }} aria-label={choice.aria}><span aria-hidden="true">{choice.emoji}</span><b>{choice.label}</b></button>;
        })}
      </div>;
    }
    if (scene.activity === "box") return <>
      <button className={`emoji-prop toy-prop ${activityStep ? "toy-moved" : "pulse"}`} onClick={() => { playEffect("rustle"); setActivityStep(1); }} aria-label="Move Sol's toy outside the box"><span aria-hidden="true">🧸</span><b>Move toy</b></button>
      <button className={`emoji-prop box-emoji ${activityStep ? "pulse" : "locked"}`} onClick={() => activityStep && beginResolution()} disabled={!activityStep} aria-label="Look inside the cardboard box"><span aria-hidden="true">📦</span><b>Look inside</b></button>
    </>;
    if (scene.activity === "bell") return <button className="hotspot emoji-hotspot bell-hotspot pulse" onPointerDown={(event) => { playEffect("listen"); bellHoldRef.current = true; setActivityStep(1); event.currentTarget.setPointerCapture(event.pointerId); }} onPointerUp={() => { if (!bellHoldRef.current) return; bellHoldRef.current = false; beginResolution(); }} onPointerCancel={() => { bellHoldRef.current = false; setActivityStep(0); }}><span className="object-emoji" aria-hidden="true">🔔</span><span className="object-label">{activityStep ? "Listening…" : "Hold the bell"}</span></button>;
    if (scene.activity === "card") return <>
      {!cardOpen && <button className="hotspot emoji-hotspot card-hotspot pulse" onClick={() => setCardOpen(true)}><span className="object-emoji" aria-hidden="true">📄</span><span className="object-label">Touch the card</span></button>}
      {cardOpen && <div className="drawing-card">
        <canvas ref={canvasRef} width="420" height="230" aria-label="A blank card you can draw on" onPointerDown={(event) => { if (!resolving) drawStart(event); }} onPointerMove={drawMove} onPointerUp={finishDrawing} onPointerCancel={finishDrawing} />
        <div><button onClick={beginResolution}>{drawn ? "Keep my mark" : "Leave it blank"}</button><button onClick={() => { const c = canvasRef.current; c?.getContext("2d")?.clearRect(0, 0, c.width, c.height); setDrawn(false); setCardInk(""); }}>Clear</button></div>
      </div>}
    </>;
    if (scene.activity === "word") return <div className="letter-steps" aria-label={`${letters} of 7 letters found`}>{"NOTHING".split("").map((letter, index) => <button key={index} className={index < letters ? "found" : index === letters ? "next-letter pulse" : ""} onClick={() => { if (index !== letters) return; playEffect("tap"); const value = letters + 1; setLetters(value); if (value === 7) beginResolution(); }} aria-label={index === letters ? `Choose ${letter}` : index < letters ? `${letter} found` : "A sleeping tile"}>{index <= letters ? letter : "?"}</button>)}</div>;
    if (scene.activity === "curtain") return <div className={`curtain-play ${activityStep ? "revealed" : ""}`}><span className="curtain-toy" role="img" aria-label="Sol's teddy behind the curtain">🧸</span><div className="curtain-overlay" style={{ transform: `translateX(${curtain}%)` }} />{activityStep > 0 && <div className="curtain-surprise">There you are! <span aria-hidden="true">✨</span></div>}<label><span>Slide slowly</span><input aria-label="Slide the curtain open" type="range" min="0" max="105" value={curtain} disabled={resolving} onInput={(event) => { const value = Number(event.currentTarget.value); setCurtain(value); if (value >= 100 && !curtainRevealRef.current) { curtainRevealRef.current = true; setActivityStep(1); playEffect("rustle"); beginResolution(); } }} /></label></div>;
    if (scene.activity === "doors") return <>
      {(roundSetup.doorOrder as Array<"A" | "B">).map((door, index) => <button key={door} className={`hotspot emoji-hotspot door-${door.toLowerCase()} door-slot-${index} ${doors.includes(door) ? "inspected" : "pulse"}`} onClick={() => { playEffect("clunk"); const next = doors.includes(door) ? doors : [...doors, door]; setDoors(next); if (next.includes("A") && next.includes("B")) beginResolution(); }}><span className="object-emoji" aria-hidden="true">🚪</span><span className="object-label">{doors.includes(door) ? door === "A" ? "A showed a card 📄" : "B showed no object" : `Look behind door ${door}`}</span></button>)}
    </>;
    const recallChoices = {
      box: { emoji: "📦", label: "Box", aria: "Choose the empty cardboard box" },
      toy: { emoji: "🧸", label: "Toy", aria: "Choose Sol's toy" },
    } as const;
    return <>
      {(roundSetup.recallOrder as Array<keyof typeof recallChoices>).map((kind, index) => {
        const choice = recallChoices[kind];
        return <button key={kind} className={`emoji-prop recall-${kind} recall-slot-${index} ${kind === "box" ? "pulse" : ""}`} onClick={() => kind === "box" ? beginResolution() : showFeedback("The toy was outside. What was empty?")} aria-label={choice.aria}><span aria-hidden="true">{choice.emoji}</span><b>{choice.label}</b></button>;
      })}
    </>;
  }

  if (levelFourActive) return <LevelFour onExit={showLevelSelect} />;
  if (levelThreeActive) return <LevelThree onExit={showLevelSelect} onNext={beginLevelFour} />;
  if (levelTwoActive) return <LevelTwo onExit={showLevelSelect} onNext={beginLevelThree} />;

  if (!started) return <main className="opening-screen level-select-screen">
    {!storageReady && <div className="restore-screen" aria-label="Returning to your adventure"><p>Returning to your adventure…</p></div>}
    <div className="opening-art" /><div className="opening-shade" />
    <div className="opening-cast" aria-hidden="true">
      <CharacterSprite name="mira" speaking={false} index={0} />
      <CharacterSprite name="tavi" speaking={false} index={1} />
      <CharacterSprite name="sol" speaking={false} index={2} />
    </div>
    <section><p className="eyebrow">SFT LEARNING ADVENTURES</p><h1>Choose an adventure</h1><p>Mia, Sol and Tavi travel through one complete learning level for each book. Pick the level you want to play.</p><div className="level-grid"><article className="level-card available"><span>LEVEL 1 · READY</span><h2>The Star Door Mystery</h2><p>Book One: <em>Something Is Here</em><br />Eight replayable learning games</p><button className="primary" onClick={beginLevelOne}>{finished ? "Review Level 1 ending" : savedStars > 0 ? "Continue Level 1" : "Play Level 1"}</button>{savedStars > 0 && <small>{finished ? "Level 1 complete on this device" : `${savedStars} of 5 clue stars found on this device`}</small>}</article><article className="level-card available level-two-card"><span>LEVEL 2 · READY</span><h2>The Moon Lantern Workshop</h2><p>Book Two: <em>One Whole, Many Parts</em><br />Nine replayable learning games</p><button className="primary" onClick={beginLevelTwo}>{savedLevelTwoRooms === 9 ? "Review Level 2 ending" : savedLevelTwoRooms > 0 ? "Continue Level 2" : "Play Level 2"}</button>{savedLevelTwoRooms > 0 && <small>{savedLevelTwoRooms} of 9 story steps complete on this device</small>}</article><article className="level-card available level-three-card"><span>LEVEL 3 · READY</span><h2>The Turning-Light Trail</h2><p>Book Three: <em>The Fold Makes a Pattern</em><br />Nine replayable learning games</p><button className="primary" onClick={beginLevelThree}>{savedLevelThreeStages === 9 ? "Review Level 3 ending" : savedLevelThreeStages > 0 ? "Continue Level 3" : "Play Level 3"}</button>{savedLevelThreeStages > 0 && <small>{savedLevelThreeStages} of 9 story steps complete on this device</small>}</article><article className="level-card available level-four-card"><span>LEVEL 4 · READY</span><h2>The Garden Checkpoint</h2><p>Book Four: <em>Look Again: How We Check</em><br />Nine replayable learning games</p><button className="primary" onClick={beginLevelFour}>{savedLevelFourStages === 9 ? "Review Level 4 ending" : savedLevelFourStages > 0 ? "Continue Level 4" : "Play Level 4"}</button>{savedLevelFourStages > 0 && <small>{savedLevelFourStages} of 9 story steps complete on this device</small>}</article></div><p className="small-print">Local Kokoro narration · captions always shown · no adverts or sign-in</p><div className="title-controls"><button className="title-music-button" onClick={playTitleMusic}><span aria-hidden="true">♫</span> Play title music</button><button className="fresh-game-button" onClick={() => setFreshGameOpen(true)}><span aria-hidden="true">↺</span> Start a fresh game</button></div></section>
    {freshGameOpen && <div className="modal-backdrop" role="presentation" onMouseDown={() => setFreshGameOpen(false)}><section className="code-modal fresh-game-modal" role="dialog" aria-modal="true" aria-labelledby="fresh-game-title" onMouseDown={(event) => event.stopPropagation()}><button className="close-modal" onClick={() => setFreshGameOpen(false)} aria-label="Close">×</button><p className="eyebrow">START AGAIN</p><h2 id="fresh-game-title">Begin a completely fresh game?</h2><p>This removes all saved progress from Levels 1, 2, 3 and 4 on this device. The books and game stay safely installed.</p><div className="fresh-game-actions"><button className="secondary" onClick={() => setFreshGameOpen(false)}>Keep my progress</button><button className="danger-action" onClick={startFreshGame}>Restart all progress</button></div></section></div>}
  </main>;

  if (introOpen) return <LevelPrelude
    levelClass="level-one-prelude"
    eyebrow="LEVEL ONE · THE BEGINNING"
    title="Welcome to the Star House"
    subtitle="Meet the adventure team, step into their magical world, and discover why one strange little word begins a very big mystery."
    background="/art/stages/e01-stage-01-observatory-v1.png"
    lines={levelOnePrelude}
    characters={[
      { id: "mia", name: "Mia", image: characterImage("mira") },
      { id: "tavi", name: "Tavi", image: characterImage("tavi") },
      { id: "sol", name: "Sol", image: characterImage("sol") },
    ]}
    discoveries={[<>📝 Find a mysterious note</>, <>👀 Look, listen and check</>, <>⭐ Help five clue stars glow</>]}
    onSpeak={(line) => { startMusic(); playLine(line); }}
    onBegin={() => { stopNarration(audioRef, narrationGenerationRef, duckMusic); setIntroOpen(false); lastAutoLineRef.current = ""; window.setTimeout(() => playEffect("clunk"), 80); }}
    initialStep={preludeStep}
    onStepChange={setPreludeStep}
    onExit={showLevelSelect}
    musicOn={musicOn}
    onToggleMusic={toggleMusic}
  />;

  if (finished) return <main className="ending-screen">
    <div className="ending-art" /><button className="ending-home" onClick={showLevelSelect} aria-label="Choose a level">⌂ Levels</button><section><p className="eyebrow">LEVEL ONE COMPLETE</p><StarTrail count={5} /><h1>The mystery is solved.</h1><p>Mia, Sol, Tavi and their new friend Nori searched every room. They found an empty box, a quiet bell, a blank card, a word and a hidden teddy.</p><blockquote>Empty, quiet, blank and hidden are not the same as nothing.</blockquote><div className="ending-lesson"><span aria-hidden="true">📖</span><div><strong>NARRATOR TO YOU</strong><p>{endingLesson.text}</p></div><button onClick={() => playLine(endingLesson)}>Hear the lesson again</button></div><div className="ending-controls"><button className="primary" onClick={beginLevelTwo}>Next level</button><button className="secondary" onClick={restart}>Play Level 1 again</button><button className="secondary" onClick={showLevelSelect}>Choose a level</button><button className="secondary" onClick={toggleMusic}>{musicOn ? "Turn music off" : "Turn music on"}</button></div></section>
  </main>;

  return <main className="game-shell">
    <header className="game-hud">
      <div><span className="eyebrow">THE STAR DOOR MYSTERY</span><strong>{scene.title}</strong></div>
      <StarTrail count={starCount} focus={starCount === 0} newest={earnedStar} />
      <nav><button onClick={showLevelSelect} aria-label="Choose a level">⌂ <span>Levels</span></button><button onClick={() => playLine()} aria-label="Replay narration">↻ <span>Hear again</span></button><button onClick={toggleNarration} aria-pressed={muted}>{muted ? "🔇" : "🔊"} <span>{muted ? "Narration off" : "Narration on"}</span></button><button onClick={toggleMusic} aria-pressed={musicOn}>{musicOn ? "♫" : "♩"} <span>{musicOn ? "Music on" : "Music off"}</span></button><button onClick={() => setJournalOpen(true)}>⌨ <span>Book code</span></button></nav>
    </header>

    <section key={scene.id} className={`play-stage scene-${scene.id}`} style={{ backgroundImage: `url('/art/stages/${scene.background}')` }} aria-label={`${scene.title}, an animated star-room story scene`}>
      <div className="stage-light" />
      {beat === 0 && scene.journey && <div className="journey-banner"><span aria-hidden="true">✨</span><strong>{scene.journey}</strong></div>}
      {scene.introduces && beat <= 1 && <div className="guest-banner">New friend for Level One: <strong>{characterNames[scene.introduces]}</strong></div>}
      {scene.id === "note" && beat >= 1 && !dialogueDone && <div className={`story-note ${beat >= 2 ? "picked-up" : "landed"}`} role="img" aria-label={beat >= 2 ? "Mia is holding the note" : "The note has landed next to Mia"}><strong>Note</strong><span aria-hidden="true">📝</span></div>}
      <div className="walking-cast" aria-hidden="true">{scene.cast.map((name, index) => <CharacterSprite key={name} name={name} index={index} speaking={speakingName === name} />)}</div>
      {dialogueDone && !complete && <div className="activity-layer"><button className="round-reset" onClick={retryRound}>↺ Reset round</button><fieldset className="resolution-lock" disabled={resolving} aria-busy={resolving}>{activity()}</fieldset>{feedback && <p className="gentle-hint level-one-feedback" role="status">{feedback}</p>}</div>}
      {earnedStar && <div className="star-reward" role="status"><span aria-hidden="true">★</span><strong>Clue star {earnedStar} lights!</strong></div>}

      <aside className={`speech-panel ${dialogueDone && !complete ? "prompting" : ""} ${complete ? "completed" : ""}`} aria-live="polite">
        {!dialogueDone || complete ? <>
          <div className="speaker-portrait"><SpeakerPortrait speaker={currentLine.speaker} /></div><span className="speaker">{complete ? "NARRATOR · WHAT YOU DISCOVERED" : currentLine.speaker}</span><p>{currentLine.text}</p>{complete ? <div className="completion-controls"><button className="replay-control" onClick={replayActivity}><span aria-hidden="true">↻</span> Play again</button><button className="next-control" onClick={nextScene}>{sceneIndex === scenes.length - 1 ? "Finish the case" : "Follow the next arrow"} <span aria-hidden="true">→</span></button></div> : <button className="next-control" onClick={nextBeat}>Next <span aria-hidden="true">→</span></button>}
        </> : <>
          <div className="speaker-portrait prompt-portrait" aria-hidden="true">☝️</div><span className="speaker">YOUR TURN</span><p>{scene.prompt}</p><span className="action-nudge" aria-hidden="true">↑ Try it in the room</span>
        </>}
      </aside>
    </section>

    <button className="restart-corner" onClick={restart}>Start over</button>
    {journalOpen && <div className="modal-backdrop" role="presentation" onMouseDown={() => setJournalOpen(false)}><section className="code-modal" role="dialog" aria-modal="true" aria-labelledby="code-title" onMouseDown={(event) => event.stopPropagation()}><button className="close-modal" onClick={() => setJournalOpen(false)} aria-label="Close">×</button><p className="eyebrow">OPTIONAL BOOK SECRET</p><h2 id="code-title">Mia&apos;s code pocket</h2><p>The book hides six codes in its pictures. They unlock jokes and previews, never lessons or progress.</p><form onSubmit={submitCode}><label htmlFor="book-code">Code from the book</label><div><input id="book-code" value={code} onChange={(event) => setCode(event.target.value)} autoComplete="off" /><button>Open</button></div></form><p className="code-result" aria-live="polite">{codeMessage}</p></section></div>}
  </main>;
}
