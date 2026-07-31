/** @typedef {"finish"} LevelFourResolution */

/**
 * Copy-locked visible captions and their Kokoro file stems. Any change here
 * requires the E04 narration manifest and local audio to be regenerated.
 */
export const LEVEL_FOUR_NARRATION = Object.freeze([
  { audio: "00a-narrator-recap", speaker: "Narrator", heading: "The light reaches the garden", text: "You helped the moon-and-sun light travel along the garden path. It shines through the Sunrise Arch. Mia, Sol and Tavi follow it to a closed garden gate." },
  { audio: "00b-narrator-mission", speaker: "Narrator", heading: "A sign needs help", text: "Words glow on the gate. Please finish my Welcome Sign before the morning visitors arrive. Beside the gate are a picture plan and an empty sign." },
  { audio: "00c-narrator-discover", speaker: "Narrator", heading: "What you will do", text: "You will look closely, copy four pictures, keep a wrong sign so you can find its mistake, and check whether the finished sign fits the gate." },
  { audio: "00d-narrator-ivo", speaker: "Narrator", heading: "Meet Ivo", text: "A green garden helper called Ivo waves. He likes to look twice. Later, he will make his own sign without peeking at the team's sign." },

  { audio: "01a-narrator-gate", speaker: "Narrator", text: "The picture plan has four corners. The corner marks are sun, moon, leaf and star. Each corner holds one picture." },
  { audio: "01b-mia-find", speaker: "Mia", text: "The gate gives us our first clue. Look at the moon corner. Move the lens to the moon. What picture can you see?" },
  { audio: "01c-narrator-observation", speaker: "Narrator", text: "You found the bee in the moon corner. You looked before you answered. Something you find by looking is called an observation." },

  { audio: "02a-narrator-ivo-arrives", speaker: "Narrator", text: "The empty sign has the same sun, moon, leaf and star corner marks as the picture plan." },
  { audio: "02b-ivo-build", speaker: "Ivo", text: "Look at one corner on the plan. Put that picture in the same corner on the sign. Use every card once." },
  { audio: "02c-narrator-build-check", speaker: "Narrator", text: "All four pictures are in the same places as the plan. The sign and the plan match. Looking at them side by side helped you check your work." },

  { audio: "03a-narrator-curtain", speaker: "Narrator", text: "Look closely at all four pictures now. In a moment, the curtain will hide the plan and an empty sign will appear." },
  { audio: "03b-tavi-memory", speaker: "Tavi", text: "Put one picture in every corner. Then check your sign. If it is different, we will keep it, look again and make a new sign." },
  { audio: "03c-narrator-memory-check", speaker: "Narrator", text: "You built and checked your sign. Any wrong sign stayed below so you could look at it again. Sol made his own sign too. Let us see it next." },

  { audio: "04a-narrator-first-try", speaker: "Narrator", text: "Sol puts his whole sign beside the picture plan. He does not erase it. Now everyone can look for what changed." },
  { audio: "04b-sol-compare", speaker: "Sol", text: "Oops! I mixed up two pictures. Please tap the two corners on my sign that do not match the plan." },
  { audio: "04c-narrator-retained-try", speaker: "Narrator", text: "You put Sol's sign beside the picture plan and found the bee and boot in different corners. Looking at two things side by side to find what is the same or different is called comparing. Sol's wrong sign stayed where everyone could see it, so it helped show what needed to change." },

  { audio: "05a-narrator-footprints", speaker: "Narrator", text: "Each of Ivo's four cards shows one move. It shows which picture Sol picked and where he put it." },
  { audio: "05b-mia-trace", speaker: "Mia", text: "Tap Move 1 and look at it beside the plan. If it matches, go to the next move. Stop at the first move that does not match." },
  { audio: "05c-narrator-trace", speaker: "Narrator", text: "Moves 1 and 2 matched. Move 3 was the first move that changed. Mia puts the bee and boot back in their right corners. Now the sign matches. A record is something we keep to remember what happened. These four cards are Sol's record." },

  { audio: "06a-narrator-frame", speaker: "Narrator", text: "First, the team checks the width. Width means how far the sign goes from one side to the other." },
  { audio: "06b-ivo-measure", speaker: "Ivo", text: "Put the ribbon on the left hook. Make it longer or shorter until it touches the right hook too. Then test the width." },
  { audio: "06c-narrator-boundary", speaker: "Narrator", text: "The ribbon touches both hooks. The sign has the right width. This check tells us about width only. It does not tell us how tall the sign is or whether its pictures are right. One check answers one question." },

  { audio: "07a-narrator-friend-check", speaker: "Narrator", text: "Ivo cannot see the team's sign. He will make his own sign by looking only at the picture plan." },
  { audio: "07b-tavi-scan", speaker: "Ivo", text: "My card tells me which corner to look at next. Move my lens there. I will put that picture on my sign. No peeking at the team's sign!" },
  { audio: "07c-narrator-independent", speaker: "Narrator", text: "Ivo made his sign without seeing the team's sign. When the cloth lifted, both signs matched. Checking without seeing or copying the first answer is called an independent check." },

  { audio: "08a-narrator-disagreement", speaker: "Narrator", text: "The width check looked from side to side. No one has measured from the bottom edge to the top edge yet." },
  { audio: "08b-ivo-outcomes", speaker: "Ivo", text: "Width means side to side. Height means bottom to top. Shall we guess, vote or measure? Choose the action that can really check the height." },
  { audio: "08c-narrator-outcomes", speaker: "Narrator", text: "The height tool touches the bottom and top edges. The sign has the right height. Mia and Ivo were not sure, so you measured instead of guessing. Another check answered the question." },

  { audio: "09a-narrator-checkpoint", speaker: "Narrator", text: "Four empty locks light up on the gate. They ask: Do the pictures match? Is the width right? Is the height right? Did Ivo's sign match? One answer card waits for each question." },
  { audio: "09b-mia-final", speaker: "Mia", text: "Pick one answer card. Then tap the question it answers. If it belongs somewhere else, we will leave the try where we can see it and try again." },
  { audio: "09c-narrator-final-check", speaker: "Narrator", text: "You gave each gate question its own answer card. The gate stayed closed while a question had no answer. When all four checks were complete, it opened. Evidence is something we can point to that shows what we found. These four answer cards are evidence." },

  { audio: "10-narrator-to-you", speaker: "Narrator", text: "Here is what you learned. You looked at the picture plan instead of guessing. You kept Sol's wrong sign and compared it with the plan. You followed Sol's moves and found the first move that changed. You measured side to side for width, then bottom to top for height. Ivo made a new sign without looking at the team's sign, and both signs matched. When Mia and Ivo were not sure, you checked again. At the gate, you put each of the four answer cards beside the question it answered. This matters because a careful check helps us find mistakes, shows what we know, and tells us what still needs checking." },
]);

export const LEVEL_FOUR_SOURCE = Object.freeze([
  Object.freeze({ symbol: "sun", symbolLabel: "SUN", picture: "sunflower" }),
  Object.freeze({ symbol: "moon", symbolLabel: "MOON", picture: "bee" }),
  Object.freeze({ symbol: "leaf", symbolLabel: "LEAF", picture: "watering-can" }),
  Object.freeze({ symbol: "star", symbolLabel: "STAR", picture: "boot" }),
]);

export const LEVEL_FOUR_PICTURES = Object.freeze(LEVEL_FOUR_SOURCE.map((entry) => entry.picture));
export const LEVEL_FOUR_PICTURE_LABELS = Object.freeze({
  sunflower: "sunflower",
  bee: "bee",
  "watering-can": "watering can",
  boot: "boot",
});

export const LEVEL_FOUR_FINAL_LESSON = LEVEL_FOUR_NARRATION.at(-1).text;

const TRACE_VARIANTS = Object.freeze([
  Object.freeze([
    { picture: "sunflower", symbol: "sun" },
    { picture: "watering-can", symbol: "leaf" },
    { picture: "boot", symbol: "moon" },
    { picture: "bee", symbol: "star" },
  ]),
  Object.freeze([
    { picture: "sunflower", symbol: "sun" },
    { picture: "bee", symbol: "moon" },
    { picture: "boot", symbol: "leaf" },
    { picture: "watering-can", symbol: "star" },
  ]),
  Object.freeze([
    { picture: "watering-can", symbol: "leaf" },
    { picture: "boot", symbol: "star" },
    { picture: "bee", symbol: "sun" },
    { picture: "sunflower", symbol: "moon" },
  ]),
  Object.freeze([
    { picture: "boot", symbol: "star" },
    { picture: "bee", symbol: "moon" },
    { picture: "watering-can", symbol: "sun" },
    { picture: "sunflower", symbol: "leaf" },
  ]),
]);

const FRIEND_ORDERS = Object.freeze([
  ["moon", "star", "sun", "leaf"],
  ["leaf", "sun", "star", "moon"],
  ["star", "leaf", "moon", "sun"],
  ["sun", "moon", "leaf", "star"],
]);

const RECORDS = Object.freeze(["pictures", "width", "height", "friend"]);

function positiveModulo(value, divisor) {
  return ((value % divisor) + divisor) % divisor;
}

function rotate(values, places) {
  const offset = positiveModulo(places, values.length);
  return [...values.slice(offset), ...values.slice(0, offset)];
}

function firstTraceDeparture(trace) {
  return trace.findIndex((step) => LEVEL_FOUR_SOURCE.find((entry) => entry.picture === step.picture)?.symbol !== step.symbol);
}

/** @param {number} previous @param {number} sample */
export function nextLevelFourRound(previous = -1, sample = Math.random()) {
  const bounded = Number.isFinite(sample) ? Math.min(Math.max(sample, 0), 0.999999) : 0;
  const candidate = Math.floor(bounded * 4);
  return candidate === positiveModulo(previous, 4) ? (candidate + 1) % 4 : candidate;
}

/**
 * The source law and the narrated opening question never vary. Card trays,
 * trace presentation, tool targets and record presentation vary between
 * proven-solvable rounds.
 *
 * @param {number} round
 */
export function levelFourRoundForRound(round) {
  const variant = positiveModulo(Math.trunc(round) || 0, 4);
  const source = LEVEL_FOUR_SOURCE.map((entry) => ({ ...entry }));
  const plan = source.map((entry) => entry.picture);
  const symbols = source.map((entry) => entry.symbol);
  const cardTray = rotate([...plan].reverse(), variant);
  // Mia's caption and its Kokoro clip always ask for MOON and name BEE.
  const requestIndex = 1;
  const firstTry = ["sunflower", "boot", "watering-can", "bee"];
  const trace = TRACE_VARIANTS[variant].map((entry) => ({ ...entry }));
  const firstDepartureIndex = firstTraceDeparture(trace);

  return {
    variant,
    source,
    plan,
    symbols,
    cardTray,
    requestIndex,
    requestSymbol: symbols[requestIndex],
    requestPicture: plan[requestIndex],
    memoryPlan: [...plan],
    firstTry,
    differenceIndexes: [1, 3],
    trace,
    firstDepartureIndex,
    measureWidth: [3, 2, 4, 3][variant],
    friendOrder: [...FRIEND_ORDERS[variant]],
    friendBoard: [...plan],
    // The visible height frame always runs from the bottom edge to the top
    // edge, so its truthful full-height answer is always step 4.
    heightTarget: 4,
    checkpointQuestions: [...RECORDS],
    checkpointRecords: rotate([...RECORDS], variant + 1),
  };
}

/** @param {Record<string, unknown>} saved @param {boolean} hasStoredProgress */
export function readLevelFourIntroSeen(saved, hasStoredProgress) {
  if (typeof saved.introSeen === "boolean") return saved.introSeen;
  if (!hasStoredProgress) return false;
  return saved.finished === true
    || saved.complete === true
    || (typeof saved.sceneIndex === "number" && saved.sceneIndex > 0)
    || (typeof saved.beat === "number" && saved.beat > 0)
    || (Array.isArray(saved.chosen) && saved.chosen.length > 0);
}

/** @param {unknown} value @returns {LevelFourResolution | null} */
export function readLevelFourResolution(value) {
  return value === "finish" ? value : null;
}

/**
 * Restore-only inference. Answer-specific activities finish in their guarded
 * input event so a final correct action cannot win twice.
 *
 * @param {string} activity
 * @param {string[]} chosen
 * @returns {LevelFourResolution | null}
 */
export function pendingLevelFourResolution(activity, chosen) {
  if (activity === "search" && chosen.length >= 1) return "finish";
  if (activity === "build" && new Set(chosen.map((value) => value.split(":")[0])).size >= 4) return "finish";
  if (activity === "difference" && new Set(chosen).size >= 2) return "finish";
  if (activity === "checkpoint" && new Set(chosen.map((value) => value.split(":")[0])).size >= 4) return "finish";
  return null;
}
