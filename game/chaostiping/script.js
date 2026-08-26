const words = [
  "galaxy", "typing", "chaos", "mirror", "reverse", "portal",
  "neon", "shadow", "glitch", "random", "level", "rule",
  "impossible", "spiral", "quantum", "paradox", "illusion"
];

const rules = [
  {
    name: "通常ルール",
    description: "そのまま表示された単語をタイプする",
    apply: (text) => text
  },
  {
    name: "逆さタイピング",
    description: "表示された単語を逆順にタイプする",
    apply: (text) => text.split("").reverse().join("")
  },
  {
    name: "母音禁止タイピング",
    description: "表示された単語から母音を抜いた形をタイプする",
    apply: (text) => text.replace(/[aeiou]/gi, "")
  },
  {
    name: "ランダム大文字タイピング",
    description: "ランダムに大文字化された形をタイプする",
    apply: (text) =>
      text
        .split("")
        .map(ch => (Math.random() < 0.5 ? ch.toUpperCase() : ch.toLowerCase()))
        .join("")
  },
  {
    name: "鏡像タイピング",
    description: "左右反転したように見える文字列をタイプする（実際は普通の文字）",
    apply: (text) => text // 見た目はCSSで揺らすなど、ここでは同じ
  }
];

let level = 1;
let score = 0;
let timeLeft = 30;
let currentWord = "";
let currentRuleIndex = 0;
let expectedInput = "";
let timerId = null;
let gameRunning = false;

const overlay = document.getElementById("overlay");
const startBtn = document.getElementById("start-btn");
const levelSpan = document.getElementById("level");
const scoreSpan = document.getElementById("score");
const timeSpan = document.getElementById("time");
const ruleTextSpan = document.getElementById("rule-text");
const currentWordDiv = document.getElementById("current-word");
const input = document.getElementById("input");
const messageDiv = document.getElementById("message");
const visualLayer = document.getElementById("visual-layer");
const gameContainer = document.getElementById("game-container");

startBtn.addEventListener("click", startGame);
input.addEventListener("input", handleInput);

function startGame() {
  overlay.style.display = "none";
  resetGameState();
  gameRunning = true;
  input.focus();
  nextWord();
  startTimer();
}

function resetGameState() {
  level = 1;
  score = 0;
  timeLeft = 30;
  currentRuleIndex = 0;
  updateHUD();
  messageDiv.textContent = "";
  visualLayer.innerHTML = "";
  gameContainer.classList.remove("shake");
}

function startTimer() {
  if (timerId) clearInterval(timerId);
  timerId = setInterval(() => {
    timeLeft--;
    timeSpan.textContent = timeLeft;
    if (timeLeft <= 0) {
      endGame();
    }
  }, 1000);
}

function endGame() {
  clearInterval(timerId);
  gameRunning = false;
  input.value = "";
  messageDiv.innerHTML = `<span class="game-over">ゲームオーバー！ スコア: ${score}</span><br>もう一度遊ぶにはページをリロードしてください`;
  gameContainer.classList.add("shake");
}

function updateHUD() {
  levelSpan.textContent = level;
  scoreSpan.textContent = score;
  ruleTextSpan.textContent = rules[currentRuleIndex].name;
}

function nextWord() {
  currentWord = words[Math.floor(Math.random() * words.length)];
  const rule = rules[currentRuleIndex];

  // 表示される単語（視覚的な変化を付ける）
  currentWordDiv.textContent = currentWord;
  currentWordDiv.style.transform = `scale(${1 + level * 0.05}) rotate(${(Math.random() - 0.5) * level * 2}deg)`;

  // プレイヤーが入力すべき文字列
  expectedInput = rule.apply(currentWord);

  // レベルに応じて視覚効果を追加
  spawnParticles();
  flashScreen();
}

function handleInput() {
  if (!gameRunning) return;

  const value = input.value;

  if (value === expectedInput) {
    // 正解
    score += 10 * level;
    timeLeft += 2; // 正解で少し時間回復
    messageDiv.textContent = "ナイス！";
    messageDiv.style.color = "#00ffff";
    input.value = "";
    levelUpCheck();
    updateHUD();
    nextWord();
  } else if (!expectedInput.startsWith(value)) {
    // 明らかなミス
    score = Math.max(0, score - 5);
    timeLeft = Math.max(0, timeLeft - 1);
    messageDiv.textContent = "ミス！画面が不安定になる…";
    messageDiv.style.color = "#ff5555";
    shakeScreen();
    spawnParticles(true);
    updateHUD();
  }
}

function levelUpCheck() {
  // スコアに応じてレベルアップ
  const newLevel = 1 + Math.floor(score / 50);
  if (newLevel > level) {
    level = newLevel;
    messageDiv.textContent = `レベルアップ！ Lv.${level}`;
    messageDiv.style.color = "#ffcc00";

    // レベルが上がると「あり得ないルール」が順に追加される
    currentRuleIndex = Math.min(rules.length - 1, level - 1);

    // レベルが上がるほど視覚効果を強く
    flashScreen(true);
  }
}

function flashScreen(strong = false) {
  gameContainer.classList.add("flash");
  if (strong) {
    gameContainer.style.filter = "hue-rotate(90deg) saturate(1.5)";
    setTimeout(() => {
      gameContainer.style.filter = "";
    }, 300);
  }
  setTimeout(() => {
    gameContainer.classList.remove("flash");
  }, 300);
}

function shakeScreen() {
  gameContainer.classList.add("shake");
  setTimeout(() => {
    gameContainer.classList.remove("shake");
  }, 400);
}

function spawnParticles(isError = false) {
  const count = isError ? 30 : 15 + level * 2;
  const centerX = window.innerWidth / 2;
  const centerY = window.innerHeight / 2;

  for (let i = 0; i < count; i++) {
    const p = document.createElement("div");
    p.className = "particle";
    const angle = Math.random() * Math.PI * 2;
    const distance = 80 + Math.random() * 80;
    const dx = Math.cos(angle) * distance;
    const dy = Math.sin(angle) * distance;
    p.style.left = centerX + "px";
    p.style.top = centerY + "px";
    p.style.setProperty("--dx", dx + "px");
    p.style.setProperty("--dy", dy + "px");
    if (isError) {
      p.style.background = "radial-gradient(circle, #ff0000 0%, transparent 70%)";
    }
    visualLayer.appendChild(p);
    setTimeout(() => {
      p.remove();
    }, 800);
  }
}
