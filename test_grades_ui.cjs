// Render the real browser code against results from the compiled C++ engine.
const fs=require('node:fs'),path=require('node:path'),vm=require('node:vm');
const assert=require('node:assert/strict'),{execFileSync}=require('node:child_process');
const engine=process.env.GRADE_ENGINE||path.join(__dirname,process.platform==='win32'?'grade_engine.exe':'grade_engine');
const totals=[80,79.9999,74.9999,69.9999,64.9999,59.9999,54.9999,49.9999,44.9999,39.9999];
const calculated=JSON.parse(execFileSync(engine,{input:totals.map((n,i)=>`W ${i+1} 1 ${n} 100 100\n`).join(''),encoding:'utf8'}));
const students=totals.map((n,i)=>({id:i+1,name:`Learner ${i+1}`,group:'Review',scores:{general:{work:n}}}));
calculated.records=calculated.records.map((row,i)=>({...students[i],...row}));calculated.ungraded=0;
const subject={id:'general',name:'Review subject',code:'REV',components:[{id:'work',name:'Work',maximum:100,weight:100}]};
const fixture={...calculated,students,subjects:[subject],subject_results:{general:calculated}};
const elements=new Map();
function element(selector){
  if(!elements.has(selector))elements.set(selector,{value:selector==='#result-filter'?'all':'',textContent:'',innerHTML:'',style:{},dataset:{},classList:{toggle(){}},setAttribute(){},removeAttribute(){}});
  return elements.get(selector);
}
const panels=['overview','students','subjects','gradebook','insights'].map(panel=>({dataset:{panel},hidden:false}));
const context={document:{querySelector:element,querySelectorAll:selector=>selector==='[data-panel]'?panels:[],addEventListener(){}},fetch:async()=>({ok:true,json:async()=>fixture}),AppUI:{hydrate(){},reveal(){},feedback(){}},location:{hash:'#insights'},history:{replaceState(){}},innerWidth:1280,setTimeout:()=>0,clearTimeout(){},console};
context.window=context;context.scrollTo=()=>{};
vm.createContext(context);vm.runInContext(fs.readFileSync(path.join(__dirname,'static/app.js'),'utf8'),context);
setImmediate(()=>{
  const chart=element('#distribution').innerHTML;
  assert.equal((chart.match(/class="distribution-row"/g)||[]).length,10,'Every grade band needs a chart row');
  for(const {grade} of fixture.grading_scale)assert.ok(chart.includes(`Grade ${grade}: 1 students`),`Missing ${grade} result`);
  assert.equal([...chart.matchAll(/value="(\d+)" aria-label/g)].reduce((n,m)=>n+Number(m[1]),0),10,'All graded students must be counted');
  assert.ok(!/class="(?:grade grade|meter)-[^\"]*[+-]/.test(chart),'CSS classes use stable grade families');
  assert.ok(element('#subject-comparison').innerHTML.includes('1 below 40'));
  assert.ok(element('#distribution-note').textContent.includes('Pass mark: 40/100'));
  assert.ok(element('#grading-key').innerHTML.includes('A- ≥75'));
  assert.ok(element('#grading-key').innerHTML.includes('F &lt;40'));
  assert.ok(element('#gradebook-table').innerHTML.includes('79.9999'));
  assert.ok(element('#result-highlights').innerHTML.includes('79.9999'));
  assert.equal(element('#toast').textContent,'','The full application must boot without an error');
  console.log('C++ → browser: all 10 grade bands, distribution counts, pass threshold and fractional totals passed');
});
