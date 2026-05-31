

// ─── КОНСТАНТЫ ───────────────────────────────────────────────
const CUBIE_SIZE   = 5;
const GAP          = 0.5;
const STEP         = CUBIE_SIZE + GAP;
const STICKER_SIZE = CUBIE_SIZE * 0.85;
const STICKER_OFF  = CUBIE_SIZE / 2 + 0.1;
const TURN_MS      = 250;            // длительность анимации одного поворота

// Цвета граней (совпадают с нумерацией сегментов)
const COLORS = {
  R: 0xcc0000,  // красный   x = +1
  L: 0xff6000,  // оранжевый x = -1
  U: 0xffffff,  // белый     y = +1
  D: 0xffd500,  // жёлтый    y = -1
  F: 0x009b48,  // зелёный   z = +1
  B: 0x0045ad,  // синий     z = -1
};

// ─── СЦЕНА ───────────────────────────────────────────────────
const scene = new THREE.Scene();
scene.background = new THREE.Color(0xeef1f6);

const camera   = new THREE.PerspectiveCamera(45, window.innerWidth / window.innerHeight, 0.1, 1000);
const renderer = new THREE.WebGLRenderer({ antialias: true });
renderer.setSize(window.innerWidth, window.innerHeight);
document.body.appendChild(renderer.domElement);

// ─── ПОСТРОЕНИЕ КУБИКА ───────────────────────────────────────
// cubeState: список { mesh: THREE.Group, x, y, z }
const cubeState = [];

function createSticker(color, px, py, pz, rx, ry) {
  const mesh = new THREE.Mesh(
    new THREE.PlaneGeometry(STICKER_SIZE, STICKER_SIZE),
    new THREE.MeshBasicMaterial({ color, side: THREE.FrontSide })
  );
  mesh.position.set(px, py, pz);
  mesh.rotation.set(rx, ry, 0);
  return mesh;
}

function createCubie(x, y, z) {
  const group = new THREE.Group();
  group.add(new THREE.Mesh(
    new THREE.BoxGeometry(CUBIE_SIZE, CUBIE_SIZE, CUBIE_SIZE),
    new THREE.MeshLambertMaterial({ color: 0x111111 })
  ));

  if (x ===  1) group.add(createSticker(COLORS.R,  STICKER_OFF, 0, 0,            0,  Math.PI / 2));
  if (x === -1) group.add(createSticker(COLORS.L, -STICKER_OFF, 0, 0,            0, -Math.PI / 2));
  if (y ===  1) group.add(createSticker(COLORS.U, 0,  STICKER_OFF, 0, -Math.PI / 2, 0));
  if (y === -1) group.add(createSticker(COLORS.D, 0, -STICKER_OFF, 0,  Math.PI / 2, 0));
  if (z ===  1) group.add(createSticker(COLORS.F, 0, 0,  STICKER_OFF,            0, 0));
  if (z === -1) group.add(createSticker(COLORS.B, 0, 0, -STICKER_OFF,            0, Math.PI));

  group.position.set(x * STEP, y * STEP, z * STEP);
  return group;
}

function buildCube() {
  for (let x = -1; x <= 1; x++)
    for (let y = -1; y <= 1; y++)
      for (let z = -1; z <= 1; z++) {
        if (x === 0 && y === 0 && z === 0) continue;   // цеент скипаем по дефолту
        const mesh = createCubie(x, y, z);
        scene.add(mesh);
        cubeState.push({ mesh, x, y, z });
      }
}

function resetCube() {
  if (isAnimating) return;
  cubeState.forEach(c => scene.remove(c.mesh));
  cubeState.length = 0;
  buildCube();
}

buildCube();

// ─── ПОВОРОТЫ ГРАНЕЙ ─────────────────────────────────────────
let isAnimating = false;

function getSlice(axis, layer) {
  return cubeState.filter(c => c[axis] === layer);
}

// Логическое обновление координат.
function updatePositions(slice, axis, dir) {
  for (const c of slice) {
    const { x, y, z } = c;
    if (axis === 'x') { c.y = Math.round( dir * z); c.z = Math.round(-dir * y); }
    if (axis === 'y') { c.x = Math.round( dir * z); c.z = Math.round(-dir * x); }
    if (axis === 'z') { c.x = Math.round( dir * y); c.y = Math.round(-dir * x); }
  }
}

// Анимация поворота грани. axis: 'x'|'y'|'z', layer: -1|0|1,
// dir: +1 (по часовой) | -1 (против). Возвращает Promise завершения.
// Знак угла для оси Y обратный
function rotateFace(axis, layer, dir) {
  if (isAnimating) return Promise.resolve();
  isAnimating = true;
  return new Promise((resolve) => {
    const slice = getSlice(axis, layer);
    const pivot = new THREE.Group();
    scene.add(pivot);
    slice.forEach(c => pivot.attach(c.mesh));   // attach сохраняет коорды

    const angleSign   = axis === 'y' ? 1 : -1;
    const targetAngle = angleSign * dir * Math.PI / 2;
    const startTime   = performance.now();

    function animate(now) {
      const t     = Math.min((now - startTime) / TURN_MS, 1);
      const eased = t < 0.5 ? 2 * t * t : -1 + (4 - 2 * t) * t;   // ease-in-out по формуле из гугла :D
      pivot.rotation[axis] = targetAngle * eased;

      if (t < 1) {
        requestAnimationFrame(animate);
        return;
      }
      // вернуть кубики в сцену, снапнуть позиции, обновить логику
      slice.forEach(c => scene.attach(c.mesh));
      scene.remove(pivot);
      slice.forEach(c => {
        c.mesh.position.x = Math.round(c.mesh.position.x / STEP) * STEP;
        c.mesh.position.y = Math.round(c.mesh.position.y / STEP) * STEP;
        c.mesh.position.z = Math.round(c.mesh.position.z / STEP) * STEP;
      });
      updatePositions(slice, axis, dir);
      isAnimating = false;
      resolve();
    }
    requestAnimationFrame(animate);
  });
}

// ─── ВОСПРОИЗВЕДЕНИЕ ХОДОВ ───────────────────────────────────
// Нотация → (ось, слой, dir)
// у оси Y знак dir обратный из-за angleSign.
const LABEL_MAP = {
  R: ['x', 1, 1],  L: ['x', -1, -1],
  U: ['y', 1, -1], D: ['y', -1, 1],
  F: ['z', 1, 1],  B: ['z', -1, -1],
};

function labelToTurns(label) {
  const [axis, layer, base] = LABEL_MAP[label[0]];
  const suffix = label.slice(1);
  if (suffix === "'") return [[axis, layer, -base]];
  if (suffix === '2')  return [[axis, layer, base], [axis, layer, base]];
  return [[axis, layer, base]];
}

async function playLabel(label) {
  for (const [axis, layer, dir] of labelToTurns(label)) {
    await rotateFace(axis, layer, dir);
  }
}

async function playLabels(labels, onStep) {
  for (let i = 0; i < labels.length; i++) {
    await playLabel(labels[i]);
    if (onStep) onStep(i);
  }
}

// ─── КЛАВИШИ ХОДОВ ───────────────────────────────────────────
// R L U N(=D) F B; Shift — обратный ход. N вместо D, чтобы не конфликтовать с WASD.
const KEY_FACE = { r: 'R', l: 'L', u: 'U', n: 'D', f: 'F', b: 'B' };
window.addEventListener('keydown', (e) => {
  const face = KEY_FACE[e.key.toLowerCase()];
  if (face) doMove(face + (e.shiftKey ? "'" : ''));
});

// ─── КАМЕРА (орбита мышью, зум колесом, WASD — сдвиг точки взгляда)
let phi = 0.4, theta = 0.6, radius = 30;
const target = new THREE.Vector3(0, 0, 0);

function updateCamera() {
  camera.position.set(
    target.x + radius * Math.cos(phi) * Math.cos(theta),
    target.y + radius * Math.sin(phi),
    target.z + radius * Math.cos(phi) * Math.sin(theta)
  );
  camera.lookAt(target);
}

let isDragging = false, prevX = 0, prevY = 0;
window.addEventListener('mousedown', (e) => { isDragging = true; prevX = e.clientX; prevY = e.clientY; });
window.addEventListener('mouseup',   () => { isDragging = false; });
window.addEventListener('mouseleave', () => { isDragging = false; });
window.addEventListener('mousemove', (e) => {
  if (!isDragging) return;
  theta -= (e.clientX - prevX) * 0.01;
  phi    = Math.max(-Math.PI / 2 + 0.01, Math.min(Math.PI / 2 - 0.01, phi - (e.clientY - prevY) * 0.01));
  prevX  = e.clientX;
  prevY  = e.clientY;
});
window.addEventListener('wheel', (e) => {
  radius = Math.max(10, Math.min(100, radius + e.deltaY * 0.05));
});

const panKeys = { w: false, s: false, a: false, d: false };
window.addEventListener('keydown', (e) => { if (e.key in panKeys) panKeys[e.key] = true; });
window.addEventListener('keyup',   (e) => { if (e.key in panKeys) panKeys[e.key] = false; });
function handlePan() {
  const speed = 0.1;
  if (panKeys.w) target.y += speed;
  if (panKeys.s) target.y -= speed;
  if (panKeys.a) target.x -= speed;
  if (panKeys.d) target.x += speed;
}

window.addEventListener('resize', () => {
  camera.aspect = window.innerWidth / window.innerHeight;
  camera.updateProjectionMatrix();
  renderer.setSize(window.innerWidth, window.innerHeight);
});

function render() {
  requestAnimationFrame(render);
  handlePan();
  updateCamera();
  renderer.render(scene, camera);
}
render();

// ─── API-КЛИЕНТ ──────────────────────────────────────────────
async function api(path, body) {
  const opt = { method: 'POST', headers: { 'Content-Type': 'application/json' } };
  if (body !== undefined) opt.body = JSON.stringify(body);
  const res = await fetch('/api' + path, opt);
  if (!res.ok) throw new Error(await res.text());
  return res.json();
}

// ─── СВЯЗКА UI ───────────────────────────────────────────────
let solution = [];
let busy = false;

function setBusy(b) {
  busy = b;
  document.querySelectorAll('button').forEach((el) => { el.disabled = b; });
}
function setStatus(text) {
  const el = document.getElementById('status');
  if (el) el.textContent = text;
}

function showSolution(r) {
  const box = document.getElementById('solution');
  const cnt = document.getElementById('moveCount');
  if (!box) return;
  if (!r) {
    box.innerHTML = '<span class="dim">—</span>';
    cnt.textContent = '';
    return;
  }
  box.innerHTML = r.solution.map((m, i) => `<span class="mv" data-i="${i}">${m}</span>`).join(' ');
  cnt.textContent = r.length + ' ходов';
}
function highlightMove(i) {
  document.querySelectorAll('.mv').forEach((el) => el.classList.remove('cur'));
  const el = document.querySelector(`.mv[data-i="${i}"]`);
  if (el) { el.classList.add('cur'); el.scrollIntoView({ block: 'nearest' }); }
}

// Один ход анимируем и идем на бек.
async function doMove(label) {
  if (busy || isAnimating) return;
  setBusy(true);
  await playLabel(label);
  try { await api('/move', { move: label }); } catch (e) { console.error(e); }
  setBusy(false);
}

async function onScramble() {
  if (busy) return;
  setBusy(true);
  setStatus('Перемешиваю…');
  resetCube();
  const r = await api('/scramble', { n: 25 });
  await playLabels(r.scramble);
  solution = [];
  showSolution(null);
  setStatus('Перемешано: ' + r.scramble.join(' '));
  setBusy(false);
}

async function onSolve() {
  if (busy) return;
  setBusy(true);
  setStatus('Ищу решение…');
  const r = await api('/solve');
  solution = r.solution;
  showSolution(r);
  setStatus('Решение найдено: ' + r.length + ' ходов');
  setBusy(false);
}

async function onPlay() {
  if (busy || solution.length === 0) return;
  setBusy(true);
  setStatus('Сборка…');
  await playLabels(solution, highlightMove);
  await api('/apply', { moves: solution });   // синхронизируем бэкенд следоваьтельно собран
  setStatus('Собрано!');
  setBusy(false);
}

async function onReset() {
  if (busy) return;
  setBusy(true);
  resetCube();
  await api('/reset');
  solution = [];
  showSolution(null);
  setStatus('Собранный куб');
  setBusy(false);
}

window.addEventListener('load', () => {
  document.getElementById('scrambleBtn')?.addEventListener('click', onScramble);
  document.getElementById('solveBtn')?.addEventListener('click', onSolve);
  document.getElementById('playBtn')?.addEventListener('click', onPlay);
  document.getElementById('resetBtn')?.addEventListener('click', onReset);
  document.querySelectorAll('#moves button[data-move]').forEach((btn) => {
    btn.addEventListener('click', () => doMove(btn.dataset.move));
  });
  api('/reset').then(() => setStatus('Собранный куб')).catch(() => setStatus('Бэкенд недоступен'));
});
