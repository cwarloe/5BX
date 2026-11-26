#!/usr/bin/env node
"use strict";
const assert=require("node:assert/strict");
const fs=require("node:fs");
const path=require("node:path");
const root=__dirname;
const data=JSON.parse(fs.readFileSync(path.join(root,"data.json"),"utf8"));
const html=fs.readFileSync(path.join(root,"index.html"),"utf8");
assert.equal(data.schema,"5bx-photo-traveler/v1");
assert.equal(data.charts.length,6);
assert.deepEqual(data.charts.map(x=>x.id),[1,2,3,4,5,6]);
assert.ok(data.cards.length>=25,"At least 25 recorded experiments");
const seen=new Set();
const allowed=new Set(["conditional","candidate","hold","reject","video-unverified"]);
for(const card of data.cards) {
  assert.ok(!seen.has(card.id),"No repeated test ID "+card.id);
  seen.add(card.id);
  assert.ok(data.charts.some(c=>c.id===card.chart),"Chart exists: "+card.id);
  assert.ok(card.title&&card.note,"Traveler has a title and editorial review caveat: "+card.id);
  assert.ok(allowed.has(card.status),"Controlled disposition vocabulary: "+card.id);
  assert.ok(Boolean(card.url)!==Boolean(card.driveId),"Exactly one primary source locator: "+card.id);
  for(const related of [...(card.stills||[]),...(card.variants||[])]) {
    assert.ok(related.title&&related.id,"Variant has title and direct Drive ID: "+card.id);
  }
  if(card.prompt) assert.match(card.prompt,/^https:\/\/github\.com\/cwarloe\/5BX\//);
}
assert.equal(data.cards.filter(x=>x.status==="approved").length,0,"No auto approvals");
assert.equal(data.cards.find(x=>x.id==="34K").driveId,"106bH7oPR8fB6trXiOXppJ95DtG-WcP0Z");
assert.equal(data.cards.find(x=>x.id==="29K").status,"hold","Deep V push-up unresolved");
assert.ok(data.cards.find(x=>x.id==="35R").variants.some(x=>x.title.includes("REJECT")),"Preserve failed provenance");
assert.ok(html.includes('id="stills"'),"Dedicated high-resolution single-stills footer");
assert.ok(html.includes('id="filters"'),"Mobile search/filter entry points");
assert.ok(html.includes("this.parentElement.insertAdjacentText"),"Failure mode for Drive thumbnails");
const inline=html.match(/<script>([\s\S]*?)<\/script>/);
assert.ok(inline,"Standalone script exists");
new Function(inline[1]);
console.log("PASS: "+data.cards.length+" photographic pilots across "+data.charts.length+" charts, statuses, prompt/variant links and browser JS");
