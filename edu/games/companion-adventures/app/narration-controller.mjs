function retireAudio(audio) {
  if (!audio) return;
  audio.pause();
  try {
    audio.removeAttribute("src");
    audio.load();
  } catch {
    // A paused element is already safe when a test double or older browser
    // does not implement the complete media-element reset API.
  }
}

export function stopNarration(audioRef, generationRef, duckMusic) {
  generationRef.current += 1;
  const audio = audioRef.current;
  audioRef.current = null;
  retireAudio(audio);
  duckMusic(false);
}

export function startNarration({ src, audioRef, generationRef, duckMusic, AudioConstructor = globalThis.Audio, visibility = () => document.visibilityState }) {
  if (visibility() !== "visible") return null;

  stopNarration(audioRef, generationRef, duckMusic);
  const generation = generationRef.current;
  const audio = new AudioConstructor(src);
  audioRef.current = audio;
  duckMusic(true);

  const finish = () => {
    if (generationRef.current !== generation || audioRef.current !== audio) return;
    audioRef.current = null;
    duckMusic(false);
  };
  audio.addEventListener("ended", finish, { once: true });
  audio.addEventListener("error", finish, { once: true });

  try {
    Promise.resolve(audio.play()).then(() => {
      if (generationRef.current !== generation || audioRef.current !== audio || visibility() !== "visible") retireAudio(audio);
    }).catch(finish);
  } catch {
    finish();
  }
  return audio;
}
