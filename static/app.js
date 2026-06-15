const API = 'http://localhost:5000/api';

const AGENTS_META = [
  {icon:'🧠', name:'Profiler Agent', desc:'Analyzing your profile and motivation'},
  {icon:'🔍', name:'Knowledge Checker', desc:'Assessing current knowledge'},
  {icon:'📚', name:'Learning Path Planner', desc:'Creating personalized learning path'},
  {icon:'📅', name:'Adaptive Planner', desc:'Building your study schedule'},
  {icon:'👨‍🏫', name:'Teaching Agent', desc:'Teaching your weak concepts'},
  {icon:'✍️', name:'Examiner Agent', desc:'Testing your knowledge'},
  {icon:'📊', name:'Manager Insights', desc:'Analyzing your performance'},
  {icon:'🎓', name:'CEO Decision', desc:'Making the final readiness call'},
];

let state = {
  step: 0,
  loopCount: 0,
  learnerId: 'L-1001',
  employeeId: 'EMP-001',
  memory: {},
  agentOutputs: {},
  kqIndex: 0,
  kqAnswers: [],
  kqQuestions: [],
  eqIndex: 0,
  eqAnswers: [],
  eqQuestions: [],
  selectedKQ: null,
  selectedEQ: null,
  examScore: 0,
};

let learnersData = {};

// ========== UTILITY FUNCTIONS ==========

function toggleAgentOutput(agentNum) {
  const outputBox = document.getElementById(`agent-output-${agentNum}`);
  const arrow = document.getElementById(`arrow-${agentNum}`);
  
  if (outputBox && arrow) {
    outputBox.classList.toggle('open');
    arrow.classList.toggle('open');
  }
}

function spinner(msg) {
  return `<div class="spinner"><div class="spin"></div>${msg}</div>`;
}

function setAgentContent(agentNum, html) {
  const outputBox = document.getElementById(`agent-output-${agentNum}`);
  if (outputBox) {
    outputBox.innerHTML = html;
    outputBox.classList.add('open');
    const arrow = document.getElementById(`arrow-${agentNum}`);
    if (arrow) arrow.classList.add('open');
  }
}

function updateProgress(step) {
  state.step = step;
  const pct = Math.round((step / 8) * 100);
  document.getElementById('progressFill').style.width = pct + '%';
  document.getElementById('progressPct').textContent = pct + '%';
  document.getElementById('progressStep').textContent = `Agent ${step} of 8`;
  document.getElementById('stepCounter').textContent = `Agent ${step} of 8`;
  renderPipeline();
}

function renderPipeline() {
  const el = document.getElementById('agentRows');
  el.innerHTML = AGENTS_META.map((a, i) => {
    const agentNum = i + 1;
    const s = agentNum < state.step ? 'completed' : agentNum === state.step ? 'active' : 'pending';
    const numClass = s === 'completed' ? 'done' : s === 'active' ? 'active' : '';
    const badge = s === 'completed' ? '<span class="agent-badge badge-done">Completed</span>' :
                  s === 'active' ? '<span class="agent-badge badge-active">Running</span>' :
                  '<span class="agent-badge badge-pending">Pending</span>';
    
    const hasOutput = state.agentOutputs[agentNum] && state.agentOutputs[agentNum].trim();
    
    const dropdownHTML = ((s === 'completed' || s === 'active') && hasOutput) 
      ? `<span class="dropdown-arrow" id="arrow-${agentNum}">▼</span>` 
      : '';
    
    const outputBoxHTML = `
      <div class="agent-output-box ${s === 'active' ? 'open' : ''}" id="agent-output-${agentNum}">
        ${hasOutput ? state.agentOutputs[agentNum] : ''}
      </div>`;
    
    const clickHandler = hasOutput ? `onclick="toggleAgentOutput(${agentNum})"` : '';
    
    return `<div class="agent-row ${s}">
      <div class="agent-row-header" ${clickHandler}>
        <div class="agent-num ${numClass}">${agentNum}</div>
        <div class="agent-icon">${a.icon}</div>
        <div class="agent-info">
          <div class="agent-name">${a.name}</div>
          <div class="agent-desc">${a.desc}</div>
        </div>
        ${badge}
        ${dropdownHTML}
      </div>
      ${outputBoxHTML}
    </div>`;
  }).join('');
}

// ========== DATA LOADING ==========

async function loadLearners() {
  try {
    const res = await fetch(`${API}/learners`);
    const data = await res.json();
    data.learners.forEach(l => learnersData[l.id] = l);
    renderTeam(data.team);
    updateProfile();
  } catch(e) { console.error(e); }
}

function renderTeam(team) {
  const el = document.getElementById('teamRows');
  el.innerHTML = team.map(m => {
    const sc = m.status === 'At Risk' ? 's-risk' : m.status === 'On Track' ? 's-ok' : 's-warn';
    const dot = m.status === 'At Risk' ? '🔴' : m.status === 'On Track' ? '🟢' : '🟡';
    return `<div class="team-row">
      <div><div class="team-name">${m.name}</div><div class="team-role">${m.role}</div></div>
      <div style="text-align:right">
        <div class="team-score">${m.practice_score}%</div>
        <div class="team-status ${sc}">${dot} ${m.status}</div>
      </div>
    </div>`;
  }).join('');
}

function updateProfile() {
  state.learnerId = document.getElementById('learnerSelect').value;
  const l = learnersData[state.learnerId];
  if (!l) return;
  const initials = l.name.split(' ').map(n=>n[0]).join('');
  document.getElementById('avatar').textContent = initials;
  document.getElementById('profileName').textContent = l.name;
  document.getElementById('profileRole').textContent = l.role;
  document.getElementById('profileCert').textContent = l.certification;
  document.getElementById('profileHours').textContent = l.hours + ' hrs';
  document.getElementById('profileScore').textContent = l.score + '%';
}

// ========== JOURNEY FLOW ==========

function startJourney() {
  state = { ...state, step:0, loopCount:0, memory:{}, agentOutputs: {}, kqIndex:0, kqAnswers:[], kqQuestions:[], eqIndex:0, eqAnswers:[], eqQuestions:[], examScore:0 };
  state.learnerId = document.getElementById('learnerSelect').value;
  state.employeeId = document.getElementById('employeeSelect').value;
  document.getElementById('landingBtns').style.display = 'none';
  document.getElementById('pipeline').style.display = 'block';
  document.getElementById('loopBadge').style.display = 'none';
  updateProgress(1);
  runStep1();
}

// ========== STEP 1: PROFILER ==========

async function runStep1() {
  updateProgress(1);
  renderPipeline();
  
  setAgentContent(1, spinner('Profiler Agent is analyzing your profile...'));

  const res = await fetch(`${API}/run/profiler`, {
    method:'POST', headers:{'Content-Type':'application/json'},
    body: JSON.stringify({learner_id: state.learnerId, employee_id: state.employeeId})
  });
  const data = await res.json();
  state.memory.profile = data.result;
  state.agentOutputs[1] = data.result;

  setAgentContent(1, `
    <div class="agent-output-header">● Output</div>
    <div class="agent-output-content">${data.result}</div>
    <div style="padding: 1.5rem; background: white; border-top: 1px solid #e5e5e5;">
      <div class="radio-group" id="motivationGroup">
        ${['🏢 Company requires it','🚀 Career growth or promotion','💡 Personal interest and curiosity'].map((m,i)=>`
          <div class="radio-option" onclick="selectMotivation(this,'${m}')">
            <input type="radio" name="motivation" value="${m}"> ${m}
          </div>`).join('')}
      </div>
      <button class="btn btn-primary" onclick="step1Next()">Continue ➡️</button>
    </div>
  `);
}

function selectMotivation(el, val) {
  document.querySelectorAll('#motivationGroup .radio-option').forEach(e => e.classList.remove('selected'));
  el.classList.add('selected');
  el.querySelector('input').checked = true;
  state.memory.motivation = val;
}

function step1Next() {
  if (!state.memory.motivation) { alert('Please select your motivation'); return; }
  runStep2();
}

// ========== STEP 2: KNOWLEDGE CHECKER ==========

async function runStep2() {
  updateProgress(2);
  renderPipeline();
  
  setAgentContent(2, spinner('Generating your diagnostic questions...'));

  const res = await fetch(`${API}/run/knowledge`, {
    method:'POST', headers:{'Content-Type':'application/json'},
    body: JSON.stringify({learner_id: state.learnerId, employee_id: state.employeeId})
  });
  const data = await res.json();
  
  let questions = [];
  try {
    let raw = data.result.trim();
    if (raw.includes('```')) { raw = raw.split('```')[1]; if(raw.startsWith('json')) raw = raw.slice(4); }
    const parsed = JSON.parse(raw);
    questions = parsed.questions || [];
  } catch(e) { questions = []; }
  
  state.kqQuestions = questions;
  state.kqIndex = 0;
  state.kqAnswers = [];
  renderKQ();
}

function renderKQ() {
  const questions = state.kqQuestions;
  const idx = state.kqIndex;
  const total = questions.length;

  if (idx >= total) {
    evaluateKQ();
    return;
  }

  const q = questions[idx];
  const pct = Math.round((idx / total) * 100);

  setAgentContent(2, `
    <div class="agent-output-header">● Baseline Assessment</div>
    <div style="padding: 1.5rem;">
      <div class="q-progress">
        <div class="q-prog-label"><span>Question ${idx+1} of ${total}</span><span style="color:#6D5DFC;font-weight:700">${pct}%</span></div>
        <div class="progress-bar"><div class="progress-fill" style="width:${pct}%"></div></div>
      </div>
      <div class="q-card">
        <div class="q-skill">📌 ${q.skill || ''}</div>
        <div class="q-text">Q${idx+1}: ${q.question}</div>
      </div>
      <div class="options" id="kqOptions">
        ${q.options.map((opt, i) => `
          <div class="option" onclick="selectKQ(this, '${String.fromCharCode(65+i)}')">
            <input type="radio" name="kq" value="${String.fromCharCode(65+i)}"> ${opt}
          </div>`).join('')}
      </div>
      <button class="btn btn-primary" onclick="nextKQ('${q.correct_answer}')">Next ➡️</button>
    </div>
  `);
}

function selectKQ(el, val) {
  document.querySelectorAll('.option').forEach(e => e.classList.remove('selected'));
  el.classList.add('selected');
  state.selectedKQ = val;
}

function nextKQ(correct) {
  if (!state.selectedKQ) { alert('Please select an answer'); return; }
  const q = state.kqQuestions[state.kqIndex];
  state.kqAnswers.push({ choice: state.selectedKQ, answer: correct, skill: q.skill, question: q.question });
  state.selectedKQ = null;
  state.kqIndex++;
  renderKQ();
}

async function evaluateKQ() {
  const score = state.kqAnswers.filter(a => a.choice === a.answer).length;
  const total = state.kqAnswers.length;
  const pct = Math.round((score/total)*100);
  const results = state.kqAnswers.map((a,i) =>
    `Q${i+1} [${a.skill}]: ${a.choice === a.answer ? '✅' : '❌ correct='+a.answer}`
  ).join('\n');

  setAgentContent(2, spinner('Analyzing your knowledge...'));

  const res = await fetch(`${API}/evaluate_knowledge`, {
    method:'POST', headers:{'Content-Type':'application/json'},
    body: JSON.stringify({ learner_id: state.learnerId, score, total, results })
  });
  const data = await res.json();
  state.memory.knowledge = data.result;
  
  const summary = `Score: ${score}/${total} (${pct}%)\n\n${data.result}`;
  state.agentOutputs[2] = summary;
  renderPipeline();

  const weak = [...new Set(state.kqAnswers.filter(a=>a.choice!==a.answer).map(a=>a.skill))];

  setAgentContent(2, `
    <div class="agent-output-header">● Results</div>
    <div style="padding: 1.5rem;">
      <div class="metrics">
        <div class="metric-box"><div class="metric-val">${score}/${total}</div><div class="metric-lbl">Correct</div></div>
        <div class="metric-box"><div class="metric-val" style="color:${pct>=70?'#10b981':'#ef4444'}">${pct}%</div><div class="metric-lbl">Score</div></div>
        <div class="metric-box"><div class="metric-val" style="color:#f59e0b">${weak.length}</div><div class="metric-lbl">Weak Areas</div></div>
      </div>
      <div class="agent-output-content" style="margin-top:1rem; padding:0">${data.result}</div>
      <button class="btn btn-primary" style="margin-top:1rem" onclick="runStep3()">Build My Learning Path ➡️</button>
    </div>
  `);
}

// ========== STEP 3: LEARNING PATH ==========

async function runStep3() {
  updateProgress(3);
  renderPipeline();
  
  setAgentContent(3, spinner('Building your personalized learning path...'));

  const res = await fetch(`${API}/run/learning_path`, {
    method:'POST', headers:{'Content-Type':'application/json'},
    body: JSON.stringify({ learner_id: state.learnerId, employee_id: state.employeeId, extra: state.memory.knowledge })
  });
  const data = await res.json();
  state.memory.learning_path = data.result;
  state.agentOutputs[3] = data.result;
  renderPipeline();

  setAgentContent(3, `
    <div class="agent-output-header">● Custom Learning Path</div>
    <div style="padding: 1.5rem;">
      <div class="agent-output-content" style="padding:0">${data.result}</div>
      <button class="btn btn-primary" style="margin-top:1rem" onclick="runStep4()">Build My Study Plan ➡️</button>
    </div>
  `);
}

// ========== STEP 4: ADAPTIVE PLANNER ==========

async function runStep4() {
  updateProgress(4);
  renderPipeline();
  
  setAgentContent(4, `
    <div class="agent-output-header">● Building Your Schedule</div>
    <div style="padding: 1.5rem;">
      <p style="color:#737373;font-size:0.9rem;margin-bottom:1.5rem">Tell me your real situation — I'll build around it:</p>
      <div style="display:grid;grid-template-columns:1fr 1fr;gap:12px;margin-bottom:1rem">
        <div>
          <label style="font-size:0.78rem;color:#737373;display:block;margin-bottom:4px">⏱️ Daily study time?</label>
          <select id="dailyHours" style="width:100%;padding:8px;border:1px solid #e5e5e5;border-radius:8px;font-size:0.85rem">
            <option>15-30 minutes</option><option>30-45 minutes</option>
            <option>1 hour</option><option>1-2 hours</option><option>2+ hours</option>
          </select>
        </div>
        <div>
          <label style="font-size:0.78rem;color:#737373;display:block;margin-bottom:4px">📅 Exam in how long?</label>
          <select id="examWeeks" style="width:100%;padding:8px;border:1px solid #e5e5e5;border-radius:8px;font-size:0.85rem">
            <option>1 week</option><option>2 weeks</option><option>3 weeks</option>
            <option>1 month</option><option>2+ months</option>
          </select>
        </div>
        <div>
          <label style="font-size:0.78rem;color:#737373;display:block;margin-bottom:4px">🌅 Best study time?</label>
          <select id="bestTime" style="width:100%;padding:8px;border:1px solid #e5e5e5;border-radius:8px;font-size:0.85rem">
            <option>Early Morning</option><option>Morning</option><option>Afternoon</option>
            <option>Evening</option><option>Night</option>
          </select>
        </div>
        <div>
          <label style="font-size:0.78rem;color:#737373;display:block;margin-bottom:4px">⚡ Energy after work?</label>
          <select id="energy" style="width:100%;padding:8px;border:1px solid #e5e5e5;border-radius:8px;font-size:0.85rem">
            <option>Still energetic</option><option>Somewhat tired</option>
            <option>Very tired</option><option>Completely drained</option>
          </select>
        </div>
      </div>
      <div style="margin-bottom:1rem">
        <label style="font-size:0.78rem;color:#737373;display:block;margin-bottom:4px">🚨 Any upcoming events or emergencies?</label>
        <input id="emergency" type="text" placeholder="e.g. Project deadline, family event..." style="width:100%;padding:8px 10px;border:1px solid #e5e5e5;border-radius:8px;font-size:0.85rem;outline:none">
      </div>
      <button class="btn btn-primary" onclick="submitPlan()">📅 Build My Plan</button>
    </div>
  `);
}

// FIXED: Made submitPlan a global function by attaching to window
window.submitPlan = async function() {
  const daily = document.getElementById('dailyHours')?.value;
  const weeks = document.getElementById('examWeeks')?.value;
  const time = document.getElementById('bestTime')?.value;
  const energy = document.getElementById('energy')?.value;
  const emg = document.getElementById('emergency')?.value || 'None';

  if (!daily || !weeks || !time || !energy) {
    alert('Please fill all fields');
    return;
  }

  setAgentContent(4, spinner('Building your realistic study plan...'));

  const extra = `Daily: ${daily}, Exam in: ${weeks}, Best time: ${time}, Energy: ${energy}, Emergency: ${emg}`;
  const res = await fetch(`${API}/run/planner`, {
    method:'POST', headers:{'Content-Type':'application/json'},
    body: JSON.stringify({ learner_id: state.learnerId, employee_id: state.employeeId, extra })
  });
  const data = await res.json();
  state.memory.plan = data.result;
  state.agentOutputs[4] = `Daily: ${daily} | Exam: ${weeks} | Time: ${time}\n\n${data.result}`;
  renderPipeline();

  setAgentContent(4, `
    <div class="agent-output-header">● Your Study Schedule</div>
    <div style="padding: 1.5rem;">
      <div class="metrics">
        <div class="metric-box"><div class="metric-val" style="font-size:0.9rem">${daily}</div><div class="metric-lbl">Daily Study</div></div>
        <div class="metric-box"><div class="metric-val" style="font-size:0.9rem">${weeks}</div><div class="metric-lbl">Until Exam</div></div>
        <div class="metric-box"><div class="metric-val" style="font-size:0.9rem">${time}</div><div class="metric-lbl">Best Time</div></div>
      </div>
      <div class="agent-output-content" style="margin-top:1rem; padding:0">${data.result}</div>
      <button class="btn btn-primary" style="margin-top:1rem" onclick="runStep5()">Start Learning ➡️</button>
    </div>
  `);
};

// ========== INITIALIZE ==========
loadLearners();
