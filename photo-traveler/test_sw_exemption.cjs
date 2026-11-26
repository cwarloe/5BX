#!/usr/bin/env node
"use strict";
// Smoke-regression test for the 5BX root PWA service worker navigation scope.
// Run from repository root: node photo-traveler/test_sw_exemption.cjs
// Or pass --stdin to check the exact deployed/sw candidate bytes.
const assert=require("node:assert/strict");
const fs=require("node:fs");
const path=require("node:path");
const vm=require("node:vm");
const sw=process.argv.includes("--stdin")
  ? fs.readFileSync(0,"utf8")
  : fs.readFileSync(path.join(__dirname,"../sw.js"),"utf8");
const listeners={};
const stall=()=>new Promise(()=>{});
const self={
  location:new URL("https://cwarloe.github.io/5BX/sw.js"),
  addEventListener:(event,callback)=>{listeners[event]=callback}
};
vm.runInNewContext(sw,{
  self,URL,Promise,
  caches:{open:stall,match:stall,keys:async()=>[]},
  fetch:stall
},{timeout:2000});
assert.ok(listeners.fetch,"Service worker fetch handler registered");
function intercepted(pathname,mode="navigate") {
  let captured=false;
  listeners.fetch({
    request:{method:"GET",mode,url:"https://cwarloe.github.io"+pathname},
    respondWith:()=>{captured=true}
  });
  return captured;
}
assert.equal(intercepted("/5BX/"),true,"Workout home remains SW-managed");
assert.equal(intercepted("/5BX/index.html"),true,"Workout shell remains SW-managed");
assert.equal(intercepted("/5BX/app.js","cors"),true,"Existing app assets remain cache-managed");
assert.equal(intercepted("/5BX/game/"),false,"Arcade sub-app bypasses workout cache");
assert.equal(intercepted("/5BX/photo-traveler/"),false,"Photo traveler page bypasses workout cache");
assert.equal(intercepted("/5BX/photo-traveler"),false,"Photo traveler no-slash redirect bypasses workout cache");
assert.equal(intercepted("/5BX/photo-traveler/data.json","cors"),false,"Photo traveler data bypasses workout cache");
console.log("PASS: workout shell remains intercepted; game and photo traveler are isolated from the PWA offline home");
