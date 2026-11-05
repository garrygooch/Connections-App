const fs = require('fs'), vm = require('vm'), assert = require('assert');
const elements = new Map();
const audioEvents = [];
const savedHistory = new Map();
class MockAudio {
  constructor(src) { this.src = src; this.currentTime = 0; this.paused = true; }
  play() { this.paused = false; audioEvents.push(this.src); return Promise.resolve(); }
  pause() { this.paused = true; }
}
function el() { return {style:{setProperty(){}},classList:{add(){},remove(){}},children:[],textContent:'',setAttribute(){},addEventListener(){},appendChild(x){this.children.push(x)},replaceChildren(){this.children=[]},set innerHTML(v){this.children=[]}}; }
const context = {console, Math, localStorage: {getItem:key=>savedHistory.get(key) || null, setItem:(key,value)=>savedHistory.set(key,value)}, Audio: MockAudio, fetch:async()=>({ok:true,json:async()=>JSON.parse(fs.readFileSync('puzzles.json','utf8'))}), document:{getElementById(id){if(!elements.has(id))elements.set(id,el());return elements.get(id)},createElement:el},window:{AudioContext:class{constructor(){this.state='running';this.currentTime=0;this.destination={}}createOscillator(){return{connect(){},frequency:{setValueAtTime(){}},start(){},stop(){}}}createGain(){return{connect(){},gain:{setValueAtTime(){},exponentialRampToValueAtTime(){}}}}}},setInterval:()=>1,clearInterval(){},setTimeout:fn=>fn()};
vm.createContext(context);
vm.runInContext(fs.readFileSync('index.html','utf8').match(/<script>([\s\S]*?)<\/script>/)[1],context);
setImmediate(()=>{
  vm.runInContext(`
    if (items.length !== 16 || puzzles.length !== 417) throw Error('Load failed');
    if (wallGrid.children.some(tile => tile.textContent !== '')) throw Error('Tiles visible before start');
    startGame();
    handleSelect(solutionGroups[0].items[0]); handleSelect(solutionGroups[1].items[0]); handleSelect(solutionGroups[2].items[0]); handleSelect(solutionGroups[3].items[0]);
    if (solvedGroups.length !== 0) throw Error('Invalid group accepted');
    if (strikesLeft !== 3 || strikesEl.children.length !== 0) throw Error('Early guess cost a life');
    for (const group of solutionGroups) for (const item of group.items) handleSelect(item);
    if (gameActive || solvedGroups.length !== 4) throw Error('Win failed');
    if (wallGrid.children.some(row => row.children[4].textContent !== 'Click to reveal')) throw Error('Winning revealed connections early');
    const previous = currentPuzzleId; startGame();
    if (!gameActive || solvedGroups.length || previous === currentPuzzleId) throw Error('Restart failed');
    for (const item of solutionGroups[0].items) handleSelect(item);
    if (strikesEl.children.length !== 0) throw Error('Lives shown before two groups');
    for (const item of solutionGroups[1].items) handleSelect(item);
    if (strikesLeft !== 3 || strikesEl.children.length !== 3) throw Error('Three lives not activated');
    solvedGroups.forEach((group, index) => { if (!items.slice(index*4, index*4+4).every(item => item.groupId === group.id)) throw Error('Solved group split across rows'); });
    for(let n=0;n<3;n++) {
      for(const item of [...solutionGroups[2].items.slice(0,2),...solutionGroups[3].items.slice(0,2)]) handleSelect(item);
      if (strikesLeft !== 2-n || strikesEl.children.length !== 2-n || gameActive !== (n<2)) throw Error('Wrong life count or premature game over');
    }
    if (!connectionRound || wallGrid.children.length !== 4) throw Error('Resolved wall missing');
    if (wallGrid.children[0].children[4].textContent !== 'Click to reveal') throw Error('Found connection leaked');
    if (wallGrid.children[2].children[4].textContent !== 'Click to reveal') throw Error('Unfound connection leaked');
    revealedConnections.add(solutionGroups[2].id); renderConnections();
    if (wallGrid.children[2].children[4].textContent !== solutionGroups[2].category) throw Error('Reveal failed');
    const livesAtEnd = strikesLeft;
    handleSelect(solutionGroups[2].items[0]);
    if (strikesLeft !== livesAtEnd || selectedItems.length) throw Error('Input accepted after game over');
    if(gameActive || strikesLeft!==0) throw Error('Loss failed');
    startGame();
    if (connectionRound || revealedConnections.size) throw Error('Connection round not reset');
    toggleAudio();
    if (![music, ...Object.values(sounds)].every(a => a.muted)) throw Error('Mute failed');
    toggleAudio();
    if ([music, ...Object.values(sounds)].some(a => a.muted)) throw Error('Unmute failed');
    endGame(false, "Time's up!", 'timeout');
    if (!music.paused) throw Error('Music continued after game');
    sounds.timeout.onended();
    startGame();
    if (sounds.timeout.onended || music.currentTime !== 0) throw Error('Audio reset failed');
    endGame(false, "Time's up!", 'timeout');
    if(gameActive) throw Error('Timeout failed');
    if (!JSON.parse(localStorage.getItem(historyKey)).includes(currentPuzzleId)) throw Error('Started puzzle not saved');
    puzzles.forEach(puzzle => playedPuzzleIds.add(puzzle.id));
    initGame();
    if (currentPuzzleId !== null || !document.getElementById('start-btn').disabled || items.length) throw Error('Exhausted library repeated a puzzle');
  `,context);
  for (const file of ['background_music.m4a', 'click_on.mp3', 'solved_group.mp3', 'incorrect_group.mp3', 'lose_life.mp3', 'time_up.mp3', 'game_outro.mp3']) {
    assert(fs.existsSync('sounds/' + file));
    assert(audioEvents.some(src => src.split('?')[0] === 'sounds/' + file), `Sound not triggered: ${file}`);
  }
  console.log('PASS: all seven audio files triggered, mute/unmute, music stop/restart, timeout sequence; data loading, 16 tiles, wrong guess, solving all groups, next puzzle, three-strike loss, timeout end state');
});
