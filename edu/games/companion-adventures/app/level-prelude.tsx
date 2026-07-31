"use client";

import { useState } from "react";
import type { CSSProperties, ReactNode } from "react";

export type PreludeLine = {
  speaker: string;
  text: string;
  audio: string;
  heading: string;
};

type PreludeCharacter = {
  id: string;
  name: string;
  image: string;
};

export default function LevelPrelude({
  levelClass,
  eyebrow,
  title,
  subtitle,
  background,
  lines,
  characters,
  discoveries,
  initialStep = -1,
  onStepChange,
  onSpeak,
  onBegin,
  onExit,
  musicOn,
  onToggleMusic,
}: {
  levelClass: string;
  eyebrow: string;
  title: string;
  subtitle: string;
  background: string;
  lines: PreludeLine[];
  characters: PreludeCharacter[];
  discoveries: ReactNode[];
  initialStep?: number;
  onStepChange?: (step: number) => void;
  onSpeak: (line: PreludeLine) => void;
  onBegin: () => void;
  onExit: () => void;
  musicOn: boolean;
  onToggleMusic: () => void;
}) {
  const [step, setStep] = useState(() => Math.min(lines.length - 1, Math.max(-1, initialStep)));
  const line = step >= 0 ? lines[step] : null;
  const speaking = line?.speaker.toLowerCase();

  function beginPrelude() {
    setStep(0);
    onStepChange?.(0);
    onSpeak(lines[0]);
  }

  function continuePrelude() {
    if (step >= lines.length - 1) {
      onBegin();
      return;
    }
    const next = step + 1;
    setStep(next);
    onStepChange?.(next);
    onSpeak(lines[next]);
  }

  return <main className={`level-prelude ${levelClass}`}>
    <div className="prelude-art" style={{ backgroundImage: `url('${background}')` }} />
    <div className="prelude-sky" aria-hidden="true"><i /><i /><i /><i /><i /><i /></div>
    <button className="prelude-home" onClick={onExit} aria-label="Choose a level">⌂ Levels</button>
    <button className="prelude-music" onClick={onToggleMusic} aria-pressed={musicOn} aria-label={musicOn ? "Turn background music off" : "Turn background music on"}>{musicOn ? "♫ Music on" : "♫ Music off"}</button>
    <div className="prelude-cast" aria-label="The adventure team">
      {characters.map((character, index) => <figure key={character.id} className={`${speaking === character.name.toLowerCase() ? "speaking" : ""} prelude-${character.id}`} style={{ "--prelude-index": index } as CSSProperties}>
        <img src={character.image} alt={character.name} draggable={false} />
        <figcaption>{character.name}</figcaption>
      </figure>)}
    </div>

    {step < 0 ? <section className="prelude-cover">
      <p className="eyebrow">{eyebrow}</p>
      <h1>{title}</h1>
      <p>{subtitle}</p>
      <div className="prelude-discoveries" aria-label="What this adventure will explore">
        {discoveries.map((item, index) => <span key={index}>{item}</span>)}
      </div>
      <button className="primary" onClick={beginPrelude}>Begin the introduction <span aria-hidden="true">✨</span></button>
    </section> : <section className="prelude-story" aria-live="polite">
      <div className="prelude-story-icon" aria-hidden="true">{line?.speaker === "Narrator" ? "📖" : "💬"}</div>
      <div>
        <span className="speaker">{line?.speaker}</span>
        <h2>{line?.heading}</h2>
        <p>{line?.text}</p>
        <small>{step + 1} of {lines.length}</small>
      </div>
      <div className="prelude-actions">
        <button className="replay-control" onClick={() => line && onSpeak(line)}>Hear again</button>
        <button className="next-control" onClick={continuePrelude}>{step === lines.length - 1 ? "Step into the adventure" : "Keep listening"} <span aria-hidden="true">→</span></button>
      </div>
    </section>}
  </main>;
}
