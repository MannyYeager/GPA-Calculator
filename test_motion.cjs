const fs = require('node:fs');
const vm = require('node:vm');
const assert = require('node:assert/strict');
{
  let calls = 0, reversions = 0, changed;
  const media = {matches:true,addEventListener:(event,callback) => { changed = callback; }};
  const element = {getClientRects:() => [1]};
  const context = {
    matchMedia:() => media,
    document:{addEventListener:() => {},querySelectorAll:() => [element]},
    window:{},
    anime:{stagger:() => 0,animate:() => { calls++; return {revert:() => reversions++}; }}
  };
  context.window.anime = context.anime;
  vm.runInNewContext(fs.readFileSync(require('node:path').join(__dirname,'static/ui.js'),'utf8'),context);
  context.window.AppUI.reveal('.card');
  context.window.AppUI.feedback('.card');
  assert.equal(calls,0,'Reduced motion must skip entrance and feedback animation');
  media.matches = false;
  context.window.AppUI.reveal('.card');
  assert.equal(calls,1,'Animation should run when motion is enabled');
  media.matches = true; changed();
  assert.equal(reversions,1,'Enabling reduced motion must restore active elements');
  media.matches = false; context.window.anime = undefined;
  context.window.AppUI.feedback('.card');
  assert.equal(calls,1,'A missing runtime must leave the app usable');
  console.log('Reduced motion, preference changes, missing-runtime fallback passed');
}

