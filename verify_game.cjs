const fs = require('fs'), vm = require('vm'), assert = require('assert');
const elements = new Map();
function el() { return {style:{},classList:{add(){}},children:[],textContent:'',setAttribute(){},addEventListener(){},appendChild(x){this.children.push(x)},replaceChildren(){this.children=[]},set innerHTML(v){this.children=[]}}; }
const context = {console, Math, fetch:async()=>({ok:true,json:async()=>JSON.parse(fs.readFileSync('puzzles.json','utf8'))}), document:{getElementById(id){if(!elements.has(id))elements.set(id,el());return elements.get(id)},createElement:el},window:{AudioContext:class{constructor(){this.state='running';this.currentTime=0;this.destination={}}createOscillator(){return{connect(){},frequency:{setValueAtTime(){}},start(){},stop(){}}}createGain(){return{connect(){},gain:{setValueAtTime(){},exponentialRampToValueAtTime(){}}}}}},setInterval:()=>1,clearInterval(){},setTimeout:fn=>fn()};
vm.createContext(context);
vm.runInContext(fs.readFileSync('index.html','utf8').match(/<script>([\s\S]*?)<\/script>/)[1],context);
setImmediate(()=>{
  vm.runInContext(`
    if (items.length !== 16 || puzzles.length !== 417) throw Error('Load failed');
    startGame();
    handleSelect(solutionGroups[0].items[0]); handleSelect(solutionGroups[1].items[0]); handleSelect(solutionGroups[2].items[0]); handleSelect(solutionGroups[3].items[0]);
    if (solvedGroups.length !== 0) throw Error('Invalid group accepted');
    for (const group of solutionGroups) for (const item of group.items) handleSelect(item);
    if (gameActive || solvedGroups.length !== 4) throw Error('Win failed');
    const previous = currentPuzzleId; startGame();
    if (!gameActive || solvedGroups.length || previous === currentPuzzleId) throw Error('Restart failed');
    for (const group of solutionGroups.slice(0,2)) for (const item of group.items) handleSelect(item);
    for(let n=0;n<3;n++) for(const item of [...solutionGroups[2].items.slice(0,2),...solutionGroups[3].items.slice(0,2)]) handleSelect(item);
    if(gameActive || strikesLeft!==0) throw Error('Loss failed');
    startGame(); endGame(false, "Time's up!");
    if(gameActive) throw Error('Timeout failed');
  `,context);
  console.log('PASS: data loading, 16 tiles, wrong guess, solving all groups, next puzzle, three-strike loss, timeout end state');
});
