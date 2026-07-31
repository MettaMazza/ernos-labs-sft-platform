import assert from "node:assert/strict";
import test from "node:test";

async function render() {
  const workerUrl = new URL("../dist/server/index.js", import.meta.url);
  workerUrl.searchParams.set("test", `${process.pid}-${Date.now()}`);
  const { default: worker } = await import(workerUrl.href);
  return worker.fetch(new Request("http://localhost/", { headers: { accept: "text/html" } }), { ASSETS: { fetch: async () => new Response("Not found", { status: 404 }) } }, { waitUntil() {}, passThroughOnException() {} });
}

test("server renders the new narrated moving-stage adventure", async () => {
  const response = await render();
  assert.equal(response.status, 200);
  assert.match(response.headers.get("content-type") ?? "", /^text\/html\b/i);
  const html = await response.text();
  assert.match(html, /Choose an adventure/);
  assert.match(html, /LEVEL 1 · READY/);
  assert.match(html, /LEVEL 2 · READY/);
  assert.match(html, /The Star Door Mystery/);
  assert.match(html, /Play Level 1/);
  assert.match(html, /Play Level 2/);
  assert.match(html, /The Moon Lantern Workshop/);
  assert.match(html, /Local Kokoro narration/);
  assert.match(html, /Mira, Sol and Tavi travel through one complete learning level for each book/);
  assert.doesNotMatch(html, /Every star answers the mystery|complete lesson in game form|scene-choice/);
});
