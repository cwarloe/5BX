#!/usr/bin/env node
"use strict";
const fs=require("node:fs");
const assert=require("node:assert/strict");
const vm=require("node:vm");
const html=fs.readFileSync(require("node:path").join(__dirname,"chart1.html"),"utf8");
const match=html.match(/<script>([\s\S]*?)<\/script>/);
assert.ok(match,"Traveler has an inline script so the HTML works as one file");
new Function(match[1]);
assert.ok(!/fetch\s*\(/.test(match[1]),"Standalone HTML does not need a separate data.json fetch");
assert.ok(!html.includes("1odMu_JB1_-2BxcLu99Xm_rs8t2ze6P9d"),"Deliberately discarded sit-up video is absent");
assert.match(html,/5BX workout generator/,"Original workout generator is linked");
assert.match(html,/Copy handoff to ChatGPT/,"Manual video return path exists");
assert.match(html,/Upload to Grok folder/,"Ordered source packet has direct link");

const elements=new Map();
function get(id){
  if(!elements.has(id)) elements.set(id,{id,innerHTML:"",value:"",dataset:{},hidden:false,addEventListener(){},style:{}});
  return elements.get(id);
}
const document={
  getElementById:get,
  addEventListener(){},
  querySelectorAll(){return []}
};
const context={document,localStorage:{getItem:()=>null},navigator:{},window:{isSecureContext:false},setTimeout(){return 1},clearTimeout(){},console};
vm.runInNewContext(match[1],context,{timeout:2500});
const listing=get("exercise-list").innerHTML;
assert.equal((listing.match(/class="exercise"/g)||[]).length,5,"Five top-level exercise panels");
assert.equal((listing.match(/class="sub-task"/g)||[]).length,2,"Run and scissor are distinct stages of exercise 5");
assert.equal((listing.match(/data-copy="/g)||[]).length,9,"Six gym prompts, one white scissor proof, and two leg fallbacks");
assert.ok((listing.match(/class="asset"/g)||[]).length>=25,"All reference cards and individual PNGs are visible as linked thumbnails");
assert.ok(listing.includes("only one foot airborne at a time"),"Leg isolation and both-feet-down bridge are explicit in gym prompt");
assert.ok(listing.includes("AUTHORITATIVE MOVEMENT AND TIMING SOURCE"),"Sit-up uses the recovered restricted motion workprint");
assert.ok(listing.includes("Review Flow loop"),"Alternate leg raise recovers the existing Flow source and review");
assert.ok(listing.includes("1qsoEJseKk2mBahA_vHEKKGNfc8-HLjBd"),"Original eight-second Flow source is linked");
assert.ok(listing.includes("1FA0bYUeQvd37W9o1Q3zDoZpPgAhP4DE7"),"Existing three-cycle review is linked");
assert.ok(listing.includes("Find exact source prompt in Flow"),"Grok prompt is not mislabeled as exact Flow provenance");
assert.ok(!listing.includes("Previous gray-background loop · HOLD"),"Obsolete gray-background hold label removed");
assert.ok(listing.includes("tousled brown hair"),"Original run prompt is present");
assert.ok(listing.includes("three low, controlled scissor exchanges"),"Scissor proof and gym motion are explicit");
assert.ok(listing.includes("White-motion proof"),"Scissor-specific white motion proof is copyable");
assert.ok(listing.includes("11-qZjVdIGFykAHoyeBRGyXNKGj2OmT2y"),"Corrected no-arm-windup six-phase card is primary");
assert.ok(listing.includes("1SKXu1BQ9Bd-vAEfOXwQoRLQ7PnGAHq3v"),"Recovered head-only three-repetition workprint is linked");
assert.ok(listing.includes("Archive ·"),"Older diagnostic reference cards are folded away");
assert.ok(listing.includes("Return" )||listing.includes("Returned Flow"),"Video handoff is visible");
for(const id of ["toe","situp","leg","knee","five"]) assert.ok(listing.includes(`id="exercise-${id}"`),id+" is linkable");
assert.equal(get("shared-links").innerHTML.match(/class="link/g).length,4,"Four shared assets");
console.log("PASS: Chart 1 traveler renders six movement packets, nine copy prompts, selected cards, collapsed archives, clips, and handoff without external data");
