"use client";

import { FormEvent, useEffect, useMemo, useState } from "react";

type AdventureLevel = {
  id: string;
  title: string;
  pages: string;
  code: string;
  scene: "room" | "box" | "bell" | "card" | "curtain" | "doors";
  prompt: string;
  options: string[];
  correct: number;
  explanation: string;
  reread: string;
  bonus: string;
  words: { word: string; meaning: string }[];
};

const levels: AdventureLevel[] = [
  {
    id: "room",
    title: "Level 1: Mira's room",
    pages: "E01 pages 5-6",
    code: "ROOMSTAR",
    scene: "room",
    prompt: "Which list names only things that are clearly in Mira's room?",
    options: [
      "Mira, Pip, bed, lamp and box",
      "Moon, cloud, whale and snowman",
      "Only an empty space",
    ],
    correct: 0,
    explanation:
      "Those objects can all be pointed to in the room. The reveal labels each one so we can check together.",
    reread:
      "Look at the room picture first, then turn to the labelled reveal. Try to find one extra object that is not in the question.",
    bonus:
      "Mira opens a notebook pocket. Inside is a room-star sticker and a note: 'A careful look can find more than the question asks for.'",
    words: [{ word: "clue", meaning: "something you notice that helps you look again" }],
  },
  {
    id: "box",
    title: "Level 2: The empty box",
    pages: "E01 pages 7-9",
    code: "BOXCLUE",
    scene: "box",
    prompt: "The toy is not inside. What can the detectives still check?",
    options: [
      "The box, toy outside, empty inside, Mira and Pip",
      "Nothing at all is shown",
      "A secret toy that the picture never gives us",
    ],
    correct: 0,
    explanation:
      "The named toy is missing from inside, while the container and the looking remain available to check.",
    reread:
      "Follow the labels BOX, TOY OUTSIDE, EMPTY INSIDE, MIRA LOOKING and PIP WATCHING on the reveal page.",
    bonus:
      "Pip finds a tiny gold key-shaped sticker. It does not open the box; it unlocks his joke: 'Empty box, full investigation!'",
    words: [
      { word: "container", meaning: "something that can hold things, like a box" },
      { word: "empty", meaning: "the named thing is not inside the container" },
    ],
  },
  {
    id: "bell",
    title: "Level 3: The still bell",
    pages: "E01 pages 10-11",
    code: "QUIETWINGS",
    scene: "bell",
    prompt: "The bell did not ring. Which happening can the picture still show?",
    options: [
      "Mira listened and Pip waited",
      "The whole room vanished",
      "A sound happened even though no sound was shown",
    ],
    correct: 0,
    explanation:
      "No ring happened during the short check, but listening, waiting and the still bell are all part of the scene.",
    reread:
      "Use the three reveal labels to retell what happened without turning quiet into a hidden object.",
    bonus:
      "Pip gives one silent wing-wave. The Quiet Wings badge joins your clue map.",
    words: [{ word: "still", meaning: "not moving during this short check" }],
  },
  {
    id: "card",
    title: "Level 4: The blank card",
    pages: "E01 pages 12-15",
    code: "BLANKEDGE",
    scene: "card",
    prompt: "A card has no drawing on it. Which statement keeps the clues separate?",
    options: [
      "The card is here; no mark is on it",
      "The card is nothing",
      "The word NOTHING makes the card disappear",
    ],
    correct: 0,
    explanation:
      "Blank tells us about the declared mark. It does not erase the card, edge, feather or magnifying glass.",
    reread:
      "Spot the four labelled clues, then read the coloured letter blocks from left to right.",
    bonus:
      "The magnifying glass reveals a silver line around the card. Your Blank Edge badge appears.",
    words: [{ word: "blank", meaning: "the named mark is not on the card" }],
  },
  {
    id: "curtain",
    title: "Level 5: Behind the curtain",
    pages: "E01 pages 16-17",
    code: "CURTAINMAP",
    scene: "curtain",
    prompt: "The curtain hides part of each toy. What remains easy to recognise?",
    options: [
      "Mira, Pip, the curtain and the visible parts of the toys",
      "No room and no players",
      "Proof that hidden things never exist",
    ],
    correct: 0,
    explanation:
      "Hidden describes this chosen view. The picture keeps the curtain, players and visible toy parts labelled.",
    reread:
      "Compare the challenge and reveal. Name what changed and what stayed in view.",
    bonus:
      "Mira turns the curtain pattern into a small map. It points toward two mystery doors.",
    words: [
      { word: "view", meaning: "what we can see from one place" },
      { word: "hidden", meaning: "blocked from this view, not erased or gone" },
    ],
  },
  {
    id: "doors",
    title: "Final level: The two doors",
    pages: "E01 pages 18-26",
    code: "TWODOORS",
    scene: "doors",
    prompt: "Door A shows a card. Door B shows no card. Which door gives Mira something to look at?",
    options: [
      "Door A, because its card and handover are shown",
      "Door B, because we can imagine a secret card",
      "Both doors show exactly the same thing",
    ],
    correct: 0,
    explanation:
      "Door A shows a card, so Mira can see and point to it. Door B has not shown an object yet. The book later calls this 'no example was given.'",
    reread:
      "Trace both paths. An example means something shown for you to look at or check. Then read Mira's detective rule and the Fair-play Rule.",
    bonus:
      "Both doors become bookmarks. Together they reveal the complete bonus message: 'Show the path. Say where the check stops.'",
    words: [
      { word: "example", meaning: "something shown or given for us to look at or check" },
      { word: "no example given", meaning: "no object has been shown for us to look at yet" },
    ],
  },
];

const sceneObjects: Record<AdventureLevel["scene"], { icon: string; label: string }[]> = {
  room: [
    { icon: "👧", label: "MIRA" },
    { icon: "🐦", label: "PIP" },
    { icon: "🛏️", label: "BED" },
    { icon: "🪟", label: "WINDOW" },
    { icon: "📚", label: "BOOKS" },
    { icon: "💡", label: "LAMP" },
    { icon: "📦", label: "BOX" },
    { icon: "🔔", label: "BELL" },
  ],
  box: [
    { icon: "📦", label: "BOX" },
    { icon: "🧸", label: "TOY OUTSIDE" },
    { icon: "⬚", label: "EMPTY INSIDE" },
    { icon: "👧", label: "MIRA LOOKING" },
    { icon: "🐦", label: "PIP WATCHING" },
  ],
  bell: [
    { icon: "👂", label: "MIRA LISTENING" },
    { icon: "🐦", label: "PIP WAITING" },
    { icon: "🔕", label: "BELL STAYED STILL" },
  ],
  card: [
    { icon: "▭", label: "BLANK CARD" },
    { icon: "⌜", label: "CARD EDGE" },
    { icon: "🪶", label: "PIP'S FEATHER" },
    { icon: "🔍", label: "MAGNIFYING GLASS" },
  ],
  curtain: [
    { icon: "👧", label: "MIRA" },
    { icon: "🐦", label: "PIP" },
    { icon: "▥", label: "CURTAIN" },
    { icon: "🧸", label: "TOY PARTLY HIDDEN" },
  ],
  doors: [
    { icon: "🚪", label: "DOOR A" },
    { icon: "🃏", label: "CARD SHOWN" },
    { icon: "👧", label: "MIRA LOOKING" },
    { icon: "▧", label: "DOOR B: NO CARD SHOWN YET" },
  ],
};

function normalizeCode(value: string) {
  return value.toUpperCase().replace(/[^A-Z0-9]/g, "");
}

export default function Home() {
  const [started, setStarted] = useState(false);
  const [levelIndex, setLevelIndex] = useState(0);
  const [answer, setAnswer] = useState<number | null>(null);
  const [message, setMessage] = useState("");
  const [solved, setSolved] = useState(false);
  const [code, setCode] = useState("");
  const [unlocked, setUnlocked] = useState<string[]>([]);
  const [finished, setFinished] = useState(false);
  const [hasLoaded, setHasLoaded] = useState(false);

  const level = levels[levelIndex];
  const correctCount = levelIndex + (solved ? 1 : 0);
  const hasBonus = unlocked.includes(level.id);

  useEffect(() => {
    const timeoutId = window.setTimeout(() => {
      try {
        const saved = window.localStorage.getItem("sft-e01-adventure-progress-v1");
        if (saved) {
          const parsed = JSON.parse(saved) as { levelIndex?: number; unlocked?: string[]; finished?: boolean };
          setLevelIndex(Math.min(Math.max(parsed.levelIndex ?? 0, 0), levels.length - 1));
          setUnlocked(Array.isArray(parsed.unlocked) ? parsed.unlocked.filter((id) => levels.some((item) => item.id === id)) : []);
          setFinished(Boolean(parsed.finished));
        }
      } catch {
        // A corrupt local record is ignored; the game remains fully playable.
      } finally {
        setHasLoaded(true);
      }
    }, 0);
    return () => window.clearTimeout(timeoutId);
  }, []);

  useEffect(() => {
    if (!hasLoaded) return;
    try {
      window.localStorage.setItem(
        "sft-e01-adventure-progress-v1",
        JSON.stringify({ levelIndex, unlocked, finished }),
      );
    } catch {
      // Device-local saving is optional.
    }
  }, [levelIndex, unlocked, finished, hasLoaded]);

  const progressLabel = useMemo(
    () => `${correctCount} of ${levels.length} clue stars solved`,
    [correctCount],
  );

  function chooseAnswer(index: number) {
    setAnswer(index);
    if (index === level.correct) {
      setSolved(true);
      setMessage(`Clue checked. ${level.explanation}`);
    } else {
      setSolved(false);
      setMessage("That answer adds or loses a clue. Look at the labelled scene, keep your first try, and choose again.");
    }
  }

  function submitCode(event: FormEvent) {
    event.preventDefault();
    if (normalizeCode(code) === level.code) {
      setUnlocked((current) => (current.includes(level.id) ? current : [...current, level.id]));
      setMessage(`Book code accepted. ${level.bonus}`);
      setCode("");
    } else {
      setMessage(`That code does not match this level yet. Check ${level.pages}; the code is printed on its reveal page.`);
    }
  }

  function continueAdventure() {
    if (levelIndex === levels.length - 1) {
      setFinished(true);
      return;
    }
    setLevelIndex((current) => current + 1);
    setAnswer(null);
    setSolved(false);
    setCode("");
    setMessage("");
  }

  function resetAdventure() {
    setStarted(false);
    setLevelIndex(0);
    setAnswer(null);
    setMessage("");
    setSolved(false);
    setCode("");
    setUnlocked([]);
    setFinished(false);
    try {
      window.localStorage.removeItem("sft-e01-adventure-progress-v1");
    } catch {
      // Reset remains successful even when local storage is unavailable.
    }
  }

  if (!started) {
    return (
      <main className="site-shell">
        <section className="hero" aria-labelledby="adventure-title">
          <div className="hero-copy">
            <p className="eyebrow">SFT BOOK COMPANION • E01 REVIEW 1.2.0</p>
            <h1 id="adventure-title">Mira &amp; Pip’s Nothing Hunt</h1>
            <p className="hero-lede">
              Read the book. Enter its clue codes. Help the detectives spot what is really shown.
            </p>
            <div className="hero-actions">
              <button className="primary-button" onClick={() => setStarted(true)}>
                Begin the adventure
              </button>
              <a className="secondary-button" href="#grown-ups">
                Information for grown-ups
              </a>
            </div>
            <p className="quiet-note">No sign-in. No adverts. No timer. Progress stays on this device.</p>
          </div>
          <div className="hero-scene" role="img" aria-label="Mira and Pip stand beside a labelled treasure map with six empty clue stars.">
            <span className="hero-mira" aria-hidden="true">👧</span>
            <div className="map-card" aria-hidden="true">
              <span>THE NOTHING HUNT</span>
              <div className="map-route">• · · · · · ★</div>
              <div className="map-stars">☆ ☆ ☆ ☆ ☆ ☆</div>
            </div>
            <span className="hero-pip" aria-hidden="true">🐦</span>
          </div>
        </section>

        <section className="how-it-works" aria-labelledby="loop-title">
          <p className="eyebrow">THE READING-FIRST LOOP</p>
          <h2 id="loop-title">The book gives the deeper clues</h2>
          <div className="loop-grid">
            <article><span>1</span><h3>Play a short scene</h3><p>Spot, choose and keep your first attempt.</p></article>
            <article><span>2</span><h3>Read the named pages</h3><p>The literature contains the demonstration and the reason.</p></article>
            <article><span>3</span><h3>Use the book code</h3><p>Unlock bonus story details, never required knowledge.</p></article>
          </div>
        </section>

        <section id="grown-ups" className="grown-up-panel" aria-labelledby="grown-up-title">
          <p className="eyebrow">FOR GROWN-UPS</p>
          <h2 id="grown-up-title">A companion, not a replacement textbook</h2>
          <p>
            The game uses only E01’s receipt-backed operational distinction. It directs the learner back to exact book pages after every attempt. Book codes unlock optional character moments and badges; they never hide the explanation or block progress.
          </p>
          <p>
            It stores only local progress on this device. It collects no name, age, email, location, voice, image or analytics. Use the reset control at any time.
          </p>
        </section>
      </main>
    );
  }

  if (finished) {
    return (
      <main className="site-shell finish-shell">
        <section className="finish-card" aria-labelledby="finish-title">
          <p className="eyebrow">ADVENTURE COMPLETE</p>
          <div className="finish-stars" aria-label={`${levels.length} clue stars solved`}>★ ★ ★ ★ ★ ★</div>
          <h1 id="finish-title">You followed both paths.</h1>
          <p>You spotted what was shown, kept the missing things separate, and did not invent an example when none was given.</p>
          <blockquote>There is no nothing.</blockquote>
          <p className="bonus-count">Book bonuses found: {unlocked.length} of {levels.length}</p>
          <div className="hero-actions">
            <button className="primary-button" onClick={resetAdventure}>Play again from the beginning</button>
            <button className="secondary-button" onClick={() => { setFinished(false); setLevelIndex(0); setSolved(false); setAnswer(null); }}>
              Revisit the levels
            </button>
          </div>
        </section>
      </main>
    );
  }

  return (
    <main className="game-shell">
      <header className="game-header">
        <div>
          <p className="eyebrow">MIRA &amp; PIP’S NOTHING HUNT</p>
          <p className="progress-text">{progressLabel}</p>
        </div>
        <button className="reset-button" onClick={resetAdventure}>Reset local progress</button>
      </header>

      <div className="progress-track" role="progressbar" aria-valuemin={0} aria-valuemax={levels.length} aria-valuenow={correctCount} aria-label={progressLabel}>
        <span style={{ width: `${(correctCount / levels.length) * 100}%` }} />
      </div>

      <section className="adventure-grid">
        <article className="scene-panel" aria-labelledby="level-title">
          <p className="eyebrow">{level.pages}</p>
          <h1 id="level-title">{level.title}</h1>
          <div className={`object-scene ${answer !== null ? "scene-revealed" : ""}`} role="group" aria-label={`${level.title} labelled object scene`}>
            {sceneObjects[level.scene].map((object) => (
              <div className="object-card" key={object.label}>
                <span className="object-icon" aria-hidden="true">{object.icon}</span>
                <span className="object-label">{answer !== null ? object.label : "?"}</span>
              </div>
            ))}
          </div>
          <p className="scene-instruction">
            {answer === null ? "Look first. The object names appear after your answer." : "Reveal: every pictured object now has its name."}
          </p>
          <aside className="word-helper" aria-labelledby="word-helper-title">
            <h2 id="word-helper-title">Word helper</h2>
            <dl>
              {level.words.map(({ word, meaning }) => (
                <div key={word}><dt>{word}</dt><dd>{meaning}</dd></div>
              ))}
            </dl>
          </aside>
        </article>

        <article className="question-panel" aria-labelledby="question-title">
          <p className="character-line"><span aria-hidden="true">👧</span> Mira asks:</p>
          <h2 id="question-title">{level.prompt}</h2>
          <div className="answer-list">
            {level.options.map((option, index) => (
              <button
                key={option}
                className={`answer-button ${answer === index ? "chosen" : ""} ${solved && index === level.correct ? "correct" : ""}`}
                onClick={() => chooseAnswer(index)}
                aria-pressed={answer === index}
              >
                <span>{String.fromCharCode(65 + index)}</span>{option}
              </button>
            ))}
          </div>

          <div className="feedback" aria-live="polite" aria-atomic="true">
            {message || "Choose an answer. Different first tries are kept without losing a star."}
          </div>

          {answer !== null && (
            <section className="book-bridge" aria-labelledby="book-bridge-title">
              <p className="eyebrow">RETURN TO THE BOOK</p>
              <h3 id="book-bridge-title">Read {level.pages}</h3>
              <p>{level.reread}</p>
              <form onSubmit={submitCode} className="code-form">
                <label htmlFor="book-code">Optional book code</label>
                <div>
                  <input
                    id="book-code"
                    value={code}
                    onChange={(event) => setCode(event.target.value)}
                    autoComplete="off"
                    inputMode="text"
                    placeholder="Enter the reveal-page code"
                  />
                  <button type="submit">Unlock bonus</button>
                </div>
                <small>The code adds story fun. It is never required to learn or continue.</small>
              </form>
              {hasBonus && <p className="bonus-message"><strong>Bonus found:</strong> {level.bonus}</p>}
            </section>
          )}

          {solved && (
            <button className="continue-button" onClick={continueAdventure}>
              {levelIndex === levels.length - 1 ? "Open the final treasure" : "Continue to the next clue"}
            </button>
          )}
        </article>
      </section>
    </main>
  );
}
