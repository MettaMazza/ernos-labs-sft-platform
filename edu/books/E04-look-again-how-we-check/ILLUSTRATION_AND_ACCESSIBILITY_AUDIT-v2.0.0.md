# E04 illustration and accessibility audit — review 2.0.0

## Illustration contract

- Student book format is 210 mm square with no game interface, menu, dialogue box or screen chrome.
- Story pages use generated garden and workshop settings with separate character sprites.
- All repeated teaching identities use stable OpenMoji 16.0 emoji assets.
- Sign labels sit above their emoji illustrations inside each sign space.
- Paper activities use a warm cream page distinct from story scenes.
- Challenge pages leave answers unmarked; reveal pages retain the same objects and explain the answer.

## Manual visual pass

All 32 student pages were rendered to PNG and inspected at full rendered resolution. The final pass checked:

- all words and emoji remain inside the page;
- the gate is visibly closed before the final checkpoint and open afterwards;
- the plan/sign mapping is unchanged on every page;
- no emoji card, label, character or page number clips;
- the plan stays visible on the ordered-step challenge;
- the team sign is labelled as covered during Ivo’s fresh build;
- width shows four equal yellow tiles across both the sign and gate space;
- height shows three equal blue tiles up both the sign and gate space;
- record-card illustrations match the questions they answer; and
- the final direct-child lesson fits without collision.

All four adult-guide pages were rendered and inspected for clipping, overflow, unintended blank pages and footer consistency.

## Accessibility

- The book never relies on colour alone: every item also has a stable picture, position and spoken name.
- Choice pages accept pointing, gaze, signing, speech or adult-mediated action.
- “I’m not sure” is explicitly accepted before the memory reveal.
- Equal measuring tiles have identical shape and a visible counted position.
- Accessible HTML contains one ordered semantic section for every page, marks all paper activities and supplies a picture description.
- The PDF has extractable text and accurate document metadata, but is not represented as fully tagged. Use the HTML edition for structured access.

## Asset boundary

OpenMoji 16.0 assets are used under CC BY-SA 4.0. Generated setting and character assets are presentation tools only and never function as scientific authority or repeated answer objects.
