"use client";

import { FormEvent, useEffect, useMemo, useState } from "react";

type CharacterName = "tavi" | "sol" | "vee" | "moss" | "nori" | "luma";
type PropName = "box" | "teddy" | "bell" | "card" | "map" | "door" | "door-card" | "empty-frame" | "word" | "curtain" | "toy-parts";

type Choice = {
  id: string;
  label: string;
  detail: string;
  prop?: PropName;
  character?: CharacterName;
};

type StoryScene = {
  id: string;
  act: string;
  title: string;
  pages: string;
  speaker: string;
  story: string;
  prompt: string;
  helper: string;
  choices: Choice[];
  correct: string[];
  multi?: boolean;
  star?: number;
  answer: string;
  word?: { term: string; meaning: string };
  code?: string;
  codeBonus?: string;
};

const scenes: StoryScene[] = [
  {
    id: "arrival",
    act: "Arrival",
    title: "The parcel on the table",
    pages: "Book pages 3–4",
    speaker: "Mira",
    story:
      "Six travellers reach Mira’s Clue Workshop just as a parcel begins to glow. Its note says: FIND NOTHING TO OPEN THE STAR DOOR. The map beside it has five empty star spaces.",
    prompt: "What must the crew understand before they begin?",
    helper: "Look at the map. The five spaces are empty now; each checked clue will light one.",
    choices: [
      { id: "five", label: "FIVE CLUES FIRST", detail: "Check five clues, light five stars, then open the door.", prop: "map" },
      { id: "door", label: "THE DOOR IS OPEN", detail: "Skip the clues because the mystery is already solved.", prop: "door" },
      { id: "guess", label: "GUESS A SECRET", detail: "Invent an answer that the parcel never showed.", character: "vee" },
    ],
    correct: ["five"],
    answer:
      "The map gives the journey a clear order: five checked clues will light five stars. Only then can the crew test the parcel’s note at the Star Door.",
    word: { term: "clue", meaning: "something you notice that helps you look again" },
  },
  {
    id: "practice",
    act: "Practice search",
    title: "Know the workshop",
    pages: "Book pages 5–6",
    speaker: "Tavi",
    story:
      "Mira will not send the crew into a mystery before everyone knows how to look. This is a practice search, so the map cannot earn a star yet.",
    prompt: "Find every named object on the workshop table.",
    helper: "Choose all four. Their names are above their pictures, so the check is clear.",
    choices: [
      { id: "box", label: "OPEN BOX", detail: "A container with its flaps open.", prop: "box" },
      { id: "bell", label: "HAND BELL", detail: "A bell with a wooden handle.", prop: "bell" },
      { id: "card", label: "BLANK CARD", detail: "A card with no drawing on it.", prop: "card" },
      { id: "map", label: "FIVE-STAR MAP", detail: "The route to the Star Door.", prop: "map" },
    ],
    correct: ["box", "bell", "card", "map"],
    multi: true,
    answer:
      "Practice complete: box, bell, card and map are all here to inspect. No star lights because Mira said this search was practice before Clue One.",
    code: "ROOMSTAR",
    codeBonus: "Pip’s margin note appears: “A practice search prepares the crew; it does not secretly add a sixth star.”",
  },
  {
    id: "box",
    act: "Clue One",
    title: "The toy and the empty box",
    pages: "Book pages 7–9",
    speaker: "Sol",
    story:
      "Sol lifts the toy out of the parcel box. He peers inside and cries, ‘I found nothing!’ Mira asks everyone to slow down and name what the scene still gives them.",
    prompt: "Which picture matches what Mira can check?",
    helper: "The named toy is not inside. Keep the container and the toy separate.",
    choices: [
      { id: "outside", label: "TOY OUTSIDE • BOX EMPTY", detail: "The toy and box are both here; the toy is not inside.", prop: "box" },
      { id: "nothing", label: "NO BOX • NO TOY", detail: "Nothing in the scene can be pointed to.", character: "sol" },
      { id: "hidden", label: "SECRET TOY INSIDE", detail: "Add another toy that was never shown.", prop: "teddy" },
    ],
    correct: ["outside"],
    star: 1,
    answer:
      "The toy is outside and the box is still here. Empty means the named toy is not inside the container; it does not mean the box became nothing.",
    word: { term: "empty", meaning: "the named thing is not inside the container" },
    code: "BOXCLUE",
    codeBonus: "The first map star reveals a tiny cupboard. Inside is Sol’s joke: “Empty box, full of clues.”",
  },
  {
    id: "bell",
    act: "Clue Two",
    title: "The bell that stayed still",
    pages: "Book pages 10–11",
    speaker: "Nori",
    story:
      "Nori waits beside the bell. Mira listens. The handle never moves and no ring is heard during their short check.",
    prompt: "What remained in the scene while no ring was heard?",
    helper: "Choose every thing the game actually shows.",
    choices: [
      { id: "bell", label: "THE STILL BELL", detail: "The bell stayed in view without ringing.", prop: "bell" },
      { id: "listener", label: "NORI LISTENING", detail: "Nori remained while the crew checked.", character: "nori" },
      { id: "ring", label: "A RINGING SOUND", detail: "A ring happened during the check.", prop: "bell" },
    ],
    correct: ["bell", "listener"],
    multi: true,
    star: 2,
    answer:
      "The bell and the listener remained. ‘No ring’ names the event that did not happen during this short check; it does not erase the bell or the listening.",
    word: { term: "still", meaning: "not moving during this short check" },
    code: "QUIETWINGS",
    codeBonus: "Pip performs one silent wing-wave. The second star stores it as the crew’s quiet greeting.",
  },
  {
    id: "card",
    act: "Clue Three",
    title: "The card with no mark",
    pages: "Book pages 12–13",
    speaker: "Vee",
    story:
      "Vee raises a cream card. No letter, line or drawing is on its face. ‘Is the card nothing?’ Vee asks.",
    prompt: "Which description says exactly what is shown?",
    helper: "Name the object first, then name what is missing from it.",
    choices: [
      { id: "blank", label: "CARD HERE • NO MARK", detail: "The card is present and its face is blank.", prop: "card" },
      { id: "gone", label: "NO CARD EXISTS", detail: "The card disappeared because it has no drawing.", prop: "empty-frame" },
      { id: "secret", label: "A HIDDEN DRAWING", detail: "Imagine a drawing the scene did not show.", character: "vee" },
    ],
    correct: ["blank"],
    star: 3,
    answer:
      "The card is here and can be inspected. Blank means there is no mark on the card; it does not mean no card was presented.",
    word: { term: "blank", meaning: "there is no mark on the card" },
    code: "BLANKEDGE",
    codeBonus: "A silver line travels around the card’s edge and reveals Vee’s sketchbook pocket—still empty until the player chooses to draw in it.",
  },
  {
    id: "word",
    act: "Clue Four",
    title: "The word that can be seen",
    pages: "Book pages 14–15",
    speaker: "Moss",
    story:
      "Seven floor tiles turn over one by one: N, O, T, H, I, N, G. The tiles name the very thing the crew was told to find.",
    prompt: "What can the crew point to now?",
    helper: "Read from left to right. A word is a visible record even when it names an absence.",
    choices: [
      { id: "word", label: "THE WORD NOTHING", detail: "Seven visible letters make a readable word.", prop: "word" },
      { id: "vanished", label: "THE TILES VANISHED", detail: "Reading the word erased every tile.", prop: "empty-frame" },
      { id: "unreadable", label: "NO LETTERS ARE HERE", detail: "The crew cannot point to any letter.", character: "moss" },
    ],
    correct: ["word"],
    star: 4,
    answer:
      "The written word NOTHING is here as seven letters the crew can see and read. The word is a presented record even though it names nothing.",
    word: { term: "word", meaning: "letters placed together so they can be read" },
  },
  {
    id: "curtain",
    act: "Clue Five",
    title: "Behind the violet curtain",
    pages: "Book pages 16–17",
    speaker: "Luma",
    story:
      "Luma draws the violet curtain across the toy shelf. A paw and one round ear still peek past its edge. The curtain changes the crew’s view, not the whole workshop.",
    prompt: "Which things remain available in this view?",
    helper: "Choose every visible clue. Hidden means blocked from this chosen view—not erased.",
    choices: [
      { id: "curtain", label: "THE CURTAIN", detail: "The cloth blocking part of the shelf remains visible.", prop: "curtain" },
      { id: "parts", label: "VISIBLE TOY PARTS", detail: "A paw and ear remain recognisable past the curtain.", prop: "toy-parts" },
      { id: "luma", label: "LUMA LOOKING", detail: "Luma remains in front of the shelf.", character: "luma" },
      { id: "nothing", label: "NOTHING AT ALL", detail: "The curtain erased the room and everyone in it.", prop: "empty-frame" },
    ],
    correct: ["curtain", "parts", "luma"],
    multi: true,
    star: 5,
    answer:
      "The curtain, visible toy parts and Luma remain. Hidden means blocked from this selected view. With Clue Five checked, the fifth map star lights and the Star Door can open.",
    word: { term: "hidden", meaning: "blocked from this view, not erased or gone" },
    code: "CURTAINMAP",
    codeBonus: "The curtain’s stitched stars become a route map. It points straight from the workshop table to the now-glowing Star Door.",
  },
  {
    id: "doors",
    act: "The Star Door",
    title: "Two doors, two paths",
    pages: "Book pages 18–26",
    speaker: "Mira",
    story:
      "All five stars shine. The Star Door opens and reveals two smaller doors. Door A offers a card. Door B offers no object. The parcel’s note can finally be tested without guessing.",
    prompt: "Which door gives the crew an object to look at?",
    helper: "Inspect both paths. An example is something shown for us to look at or check.",
    choices: [
      { id: "a", label: "DOOR A • CARD SHOWN", detail: "A card is presented for the crew to inspect.", prop: "door-card" },
      { id: "b", label: "DOOR B • NO OBJECT SHOWN", detail: "No object is supplied from this door yet.", prop: "empty-frame" },
      { id: "same", label: "BOTH SHOW A CARD", detail: "Invent a second card behind Door B.", prop: "card" },
    ],
    correct: ["a"],
    answer:
      "Door A presents a card, so the card is an example—something the crew can inspect. Door B supplies no object to inspect, so no example was given from that path. We do not invent one. Together the two paths support the result: there is no nothing.",
    word: { term: "no example given", meaning: "no object has been shown for us to look at yet" },
    code: "TWODOORS",
    codeBonus: "The parcel ribbon unfolds into a bookmark: “Show the path. Say where the check stops.” A sealed corner previews the next parcel about one whole and many parts.",
  },
  {
    id: "recall",
    act: "Case file",
    title: "The first star remembers",
    pages: "Book pages 27–31",
    speaker: "Tavi",
    story:
      "The mystery is solved, but Mira will not shelve a map that no one can explain. As the crew carries it to the library, the first star glows and returns to Sol’s box clue from earlier.",
    prompt: "What did Clue One actually show?",
    helper: "This is a later memory check. Think back before choosing; a correct answer earns a memory spark, not another map star.",
    choices: [
      { id: "box", label: "BOX HERE • TOY OUTSIDE", detail: "The container remained while the named toy was not inside.", prop: "box" },
      { id: "vanished", label: "THE BOX VANISHED", detail: "Empty made the whole box disappear.", prop: "empty-frame" },
      { id: "secret", label: "A SECRET TOY INSIDE", detail: "The crew added a toy that was never shown.", prop: "teddy" },
    ],
    correct: ["box"],
    answer:
      "Memory spark earned: the box remained and the toy was outside. The crew can now explain why the first star lit, so Mira files the completed map in the workshop library.",
    word: { term: "remember", meaning: "bring an earlier clue back to mind" },
  },
];

const codeLookup = new Map(
  scenes.filter((scene) => scene.code).map((scene) => [scene.code as string, scene]),
);

function normalizeCode(value: string) {
  return value.toUpperCase().replace(/[^A-Z0-9]/g, "");
}

function Sprite({ prop, character }: { prop?: PropName; character?: CharacterName }) {
  if (character) return <span className={`sprite character character-${character}`} aria-hidden="true" />;
  return <span className={`sprite prop prop-${prop ?? "map"}`} aria-hidden="true" />;
}

function StarMap({ count }: { count: number }) {
  return (
    <div className="star-map" aria-label={`${count} of 5 clue stars lit`}>
      <span className="map-title">THE STAR DOOR MAP</span>
      <div className="star-route" aria-hidden="true">
        {[1, 2, 3, 4, 5].map((star) => <span key={star} className={star <= count ? "lit" : ""}>{star <= count ? "★" : "☆"}</span>)}
        <span className={count === 5 ? "door-lit" : ""}>⌂</span>
      </div>
    </div>
  );
}

export default function Home() {
  const [started, setStarted] = useState(false);
  const [sceneIndex, setSceneIndex] = useState(0);
  const [selected, setSelected] = useState<string[]>([]);
  const [checked, setChecked] = useState(false);
  const [completed, setCompleted] = useState<string[]>([]);
  const [unlocked, setUnlocked] = useState<string[]>([]);
  const [code, setCode] = useState("");
  const [codeMessage, setCodeMessage] = useState("");
  const [finished, setFinished] = useState(false);
  const [loaded, setLoaded] = useState(false);
  const [journalOpen, setJournalOpen] = useState(false);
  const [run, setRun] = useState(1);

  const scene = scenes[sceneIndex];
  const starCount = scenes.filter((item) => item.star && completed.includes(item.id)).length;
  const progress = Math.round((completed.length / scenes.length) * 100);
  const selectionIsCorrect =
    selected.length === scene.correct.length && scene.correct.every((item) => selected.includes(item));

  const orderedChoices = useMemo(() => {
    if (run % 2 === 1 || scene.id === "practice") return scene.choices;
    return [...scene.choices.slice(1), scene.choices[0]];
  }, [run, scene]);

  useEffect(() => {
    const timeout = window.setTimeout(() => {
      try {
        const raw = window.localStorage.getItem("sft-e01-star-door-progress-v2");
        if (raw) {
          const saved = JSON.parse(raw) as { sceneIndex?: number; completed?: string[]; unlocked?: string[]; run?: number };
          setSceneIndex(Math.min(Math.max(saved.sceneIndex ?? 0, 0), scenes.length - 1));
          setCompleted(Array.isArray(saved.completed) ? saved.completed.filter((id) => scenes.some((item) => item.id === id)) : []);
          setUnlocked(Array.isArray(saved.unlocked) ? saved.unlocked.filter((id) => scenes.some((item) => item.id === id)) : []);
          setRun(Math.max(1, saved.run ?? 1));
        }
      } catch {
        // The adventure remains playable when an old local save cannot be read.
      } finally {
        setLoaded(true);
      }
    }, 0);
    return () => window.clearTimeout(timeout);
  }, []);

  useEffect(() => {
    if (!loaded) return;
    try {
      window.localStorage.setItem(
        "sft-e01-star-door-progress-v2",
        JSON.stringify({ sceneIndex, completed, unlocked, run }),
      );
    } catch {
      // Device-local saving is optional.
    }
  }, [sceneIndex, completed, unlocked, run, loaded]);

  function toggleChoice(id: string) {
    if (checked) return;
    if (!scene.multi) {
      setSelected([id]);
      return;
    }
    setSelected((current) => current.includes(id) ? current.filter((item) => item !== id) : [...current, id]);
  }

  function checkChoice() {
    if (selected.length === 0) return;
    setChecked(true);
    if (selectionIsCorrect) {
      setCompleted((current) => current.includes(scene.id) ? current : [...current, scene.id]);
    }
  }

  function tryAgain() {
    setSelected([]);
    setChecked(false);
  }

  function continueStory() {
    if (!selectionIsCorrect) return;
    if (sceneIndex === scenes.length - 1) {
      setFinished(true);
      return;
    }
    setSceneIndex((current) => current + 1);
    setSelected([]);
    setChecked(false);
    setCodeMessage("");
    window.scrollTo({ top: 0, behavior: "smooth" });
  }

  function submitCode(event: FormEvent) {
    event.preventDefault();
    const normalized = normalizeCode(code);
    const codeScene = codeLookup.get(normalized);
    if (!codeScene) {
      setCodeMessage("That code is not in Book One yet. Keep it as your first try, then search a reveal page closely.");
      return;
    }
    setUnlocked((current) => current.includes(codeScene.id) ? current : [...current, codeScene.id]);
    setCodeMessage(`${codeScene.title}: ${codeScene.codeBonus}`);
    setCode("");
  }

  function beginAdventure() {
    setStarted(true);
    window.scrollTo({ top: 0, behavior: "auto" });
  }

  function restart() {
    setStarted(true);
    setFinished(false);
    setSceneIndex(0);
    setSelected([]);
    setChecked(false);
    setCompleted([]);
    setCodeMessage("");
    setRun((current) => current + 1);
    try {
      window.localStorage.removeItem("sft-e01-star-door-progress-v2");
    } catch {
      // Reset succeeds even if local storage is unavailable.
    }
  }

  if (!started) {
    return (
      <main className="landing-shell">
        <section className="world-hero" aria-labelledby="game-title">
          <div className="world-art" role="img" aria-label="Mira, Pip and six original rounded 3D travellers gather around an open parcel, a bell, a blank card and a star map inside a warm observatory workshop." />
          <div className="hero-shade" />
          <div className="hero-story">
            <p className="kicker">BOOK ONE • PLAYABLE LEVEL ONE • REVIEW 1.3.0</p>
            <h1 id="game-title">The Star Door Mystery</h1>
            <p className="hero-lede">One parcel. Five promised clues. A door that will not open until every star has a reason to shine.</p>
            <div className="hero-actions">
              <button className="gold-button" onClick={beginAdventure}>Enter Mira’s workshop</button>
              <a className="glass-button" href="#grown-ups">Grown-up guide</a>
            </div>
            <p className="privacy-line">No sign-in. No adverts. No timer. No network needed after installation. Progress stays on this device.</p>
          </div>
        </section>

        <section className="story-promise" aria-labelledby="story-promise-title">
          <p className="kicker dark">ONE COHERENT ADVENTURE</p>
          <h2 id="story-promise-title">Every star answers the mystery introduced at the start.</h2>
          <div className="promise-route">
            <article><span>1</span><h3>The parcel</h3><p>Meet the crew and learn why the map has five empty spaces.</p></article>
            <article><span>2</span><h3>The investigations</h3><p>Try each scene, name what remains and earn only the star that scene explains.</p></article>
            <article><span>3</span><h3>The two doors</h3><p>Use all five clues to test both paths and resolve the parcel’s note.</p></article>
          </div>
        </section>

        <section id="grown-ups" className="grown-up-card" aria-labelledby="grown-up-title">
          <p className="kicker dark">FOR GROWN-UPS</p>
          <h2 id="grown-up-title">A complete lesson in game form, with the book still worth reading</h2>
          <p>The game defines every learning word, demonstrates the same operational distinction as Book One and never hides scientific content behind a code. The book adds a quieter page-turn rhythm, labelled reveal spreads, hidden codes and discussion prompts. Codes unlock optional character moments only.</p>
          <p>The 3D world and characters are original to this project. The adventure is designed for shared reading or independent play, with large controls, visible labels, no penalties, no public scores and no personal-data collection.</p>
        </section>
      </main>
    );
  }

  if (finished) {
    return (
      <main className="ending-shell">
        <section className="ending-card" aria-labelledby="ending-title">
          <div className="ending-crew" aria-hidden="true">
            {(["tavi", "sol", "vee", "moss", "nori", "luma"] as CharacterName[]).map((name) => <Sprite key={name} character={name} />)}
          </div>
          <p className="kicker dark">CASE ONE COMPLETE</p>
          <StarMap count={5} />
          <h1 id="ending-title">The parcel’s note has an answer.</h1>
          <p className="ending-result">Door A gave the crew a card to inspect. Door B gave no object to inspect. Something shown, said, drawn or saved is here for the crew to check. If no example is shown, the crew does not invent one.</p>
          <blockquote>Inside this game’s careful check: there is no nothing.</blockquote>
          <p className="boundary-note"><strong>Grown-up note:</strong> the exact SFT claim is operational. It does not claim knowledge of an unexpressed metaphysical domain. Its boundary is what was shown, said, drawn or saved in the adventure.</p>
          <div className="next-parcel"><strong>Next parcel preview:</strong> how can one whole have many visible parts?</div>
          <p className="bonus-count">Optional book-code stories found: {unlocked.length} of {codeLookup.size}</p>
          <div className="hero-actions centre">
            <button className="gold-button dark-button" onClick={restart}>Replay with choices moved</button>
            <button className="glass-button light" onClick={() => { setFinished(false); setSceneIndex(0); setSelected([]); setChecked(false); }}>Revisit the story</button>
          </div>
        </section>
      </main>
    );
  }

  return (
    <main className="adventure-shell">
      <header className="adventure-header">
        <div>
          <p className="kicker">THE STAR DOOR MYSTERY</p>
          <p className="scene-counter">Scene {sceneIndex + 1} of {scenes.length} • {scene.act}</p>
        </div>
        <div className="header-actions">
          <button className="journal-button" onClick={() => setJournalOpen((open) => !open)} aria-expanded={journalOpen}>Book-code journal ({unlocked.length})</button>
          <button className="reset-link" onClick={restart}>Start over</button>
        </div>
      </header>

      <div className="journey-progress" role="progressbar" aria-valuemin={0} aria-valuemax={100} aria-valuenow={progress} aria-label={`${completed.length} of ${scenes.length} story scenes completed`}>
        <span style={{ width: `${progress}%` }} />
      </div>

      {journalOpen && (
        <aside className="code-journal" aria-labelledby="journal-title">
          <div>
            <p className="kicker dark">OPTIONAL BOOK SECRETS</p>
            <h2 id="journal-title">Pip’s code journal</h2>
            <p>Codes are hidden inside Book One’s reveal pictures. They add character moments and never block the story, explanation or next scene.</p>
          </div>
          <form onSubmit={submitCode}>
            <label htmlFor="book-code">Enter a code from the book</label>
            <div><input id="book-code" value={code} onChange={(event) => setCode(event.target.value)} autoComplete="off" placeholder="BOOK CODE" /><button type="submit">Open note</button></div>
          </form>
          <p className="code-message" aria-live="polite">{codeMessage || `${unlocked.length} of ${codeLookup.size} optional notes found.`}</p>
        </aside>
      )}

      <section className="story-stage" aria-labelledby="scene-title">
        <div className="stage-world" role="img" aria-label="A warm 3D observatory workshop with a star door, map table and the travelling clue crew.">
          <div className="stage-vignette" />
          <div className="stage-map"><StarMap count={starCount} /></div>
          <div className="stage-cast" aria-hidden="true">
            <Sprite character="tavi" />
            <Sprite character={scene.id === "bell" ? "nori" : scene.id === "curtain" ? "luma" : scene.id === "word" ? "moss" : scene.id === "card" ? "vee" : "sol"} />
          </div>
        </div>

        <article className="story-copy">
          <p className="kicker dark">{scene.pages}</p>
          <h1 id="scene-title">{scene.title}</h1>
          <p className="speaker-line"><strong>{scene.speaker}:</strong> {scene.story}</p>
          <div className="prompt-card">
            <h2>{scene.prompt}</h2>
            <p>{scene.helper}</p>
          </div>
        </article>
      </section>

      <section className="interaction-panel" aria-label="Scene choices">
        <div className="choice-grid">
          {orderedChoices.map((choice) => {
            const isSelected = selected.includes(choice.id);
            const isCorrectChoice = scene.correct.includes(choice.id);
            const stateClass = checked ? (isCorrectChoice ? "correct" : isSelected ? "incorrect" : "") : "";
            return (
              <button key={choice.id} className={`scene-choice ${isSelected ? "selected" : ""} ${stateClass}`} onClick={() => toggleChoice(choice.id)} aria-pressed={isSelected} disabled={checked}>
                <span className="choice-name">{choice.label}</span>
                <Sprite prop={choice.prop} character={choice.character} />
                <span className="choice-detail">{choice.detail}</span>
                <span className="choice-check" aria-hidden="true">{isSelected ? "✓" : ""}</span>
              </button>
            );
          })}
        </div>

        {!checked && (
          <div className="check-row">
            <p>{scene.multi ? "Choose every answer that the scene shows, then check." : "Choose one answer, then check."} First tries are kept without losing a star.</p>
            <button className="gold-button dark-button" onClick={checkChoice} disabled={selected.length === 0}>Check this clue</button>
          </div>
        )}

        {checked && (
          <section className={`result-panel ${selectionIsCorrect ? "success" : "retry"}`} aria-live="polite" aria-atomic="true">
            <p className="result-label">{selectionIsCorrect ? (scene.star ? `CLUE CHECKED • STAR ${scene.star} LIT` : "SCENE CHECKED") : "KEEP THE FIRST TRY • LOOK AGAIN"}</p>
            <h2>{selectionIsCorrect ? "The evidence fits." : "That choice adds or loses something."}</h2>
            <p>{selectionIsCorrect ? scene.answer : "Compare each label with the scene. Keep every object the game shows, and do not add an object that was never presented."}</p>
            {selectionIsCorrect && scene.word && <p className="word-definition"><strong>{scene.word.term}</strong> means {scene.word.meaning}.</p>}
            {selectionIsCorrect && (
              <div className="reading-bridge">
                <div><span>READING BRIDGE</span><strong>Now read {scene.pages.replace("Book ", "")}</strong><p>The book retells this check with a challenge page, a labelled reveal and a hidden optional code.</p></div>
                {scene.code && <button onClick={() => setJournalOpen(true)}>Open code journal</button>}
              </div>
            )}
            <div className="result-actions">
              {!selectionIsCorrect ? <button className="gold-button dark-button" onClick={tryAgain}>Look again</button> : <button className="gold-button dark-button" onClick={continueStory}>{scene.id === "recall" ? "File the completed case" : "Continue the story"}</button>}
            </div>
          </section>
        )}
      </section>
    </main>
  );
}
