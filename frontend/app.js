const files = [];

// ── Skill alias map (mirrors normalizer/skill_aliases.py) ─────────────────
const SKILL_ALIASES = {
  'js':'JavaScript','javascript':'JavaScript','ts':'TypeScript','typescript':'TypeScript',
  'node':'Node.js','node.js':'Node.js','nodejs':'Node.js',
  'react':'React','react.js':'React','reactjs':'React',
  'next':'Next.js','next.js':'Next.js','nextjs':'Next.js',
  'vue':'Vue.js','vue.js':'Vue.js','vuejs':'Vue.js',
  'angular':'Angular','angularjs':'AngularJS',
  'express':'Express.js','express.js':'Express.js','expressjs':'Express.js',
  'nestjs':'NestJS','nest.js':'NestJS',
  'python':'Python','python3':'Python','py':'Python',
  'django':'Django','flask':'Flask','fastapi':'FastAPI','fast api':'FastAPI',
  'sqlalchemy':'SQLAlchemy','celery':'Celery','pydantic':'Pydantic',
  'numpy':'NumPy','pandas':'Pandas','scipy':'SciPy','matplotlib':'Matplotlib',
  'sklearn':'scikit-learn','scikit-learn':'scikit-learn','scikit learn':'scikit-learn',
  'tensorflow':'TensorFlow','tf':'TensorFlow','keras':'Keras',
  'pytorch':'PyTorch','torch':'PyTorch',
  'postgres':'PostgreSQL','postgresql':'PostgreSQL','psql':'PostgreSQL',
  'mysql':'MySQL','sqlite':'SQLite','mariadb':'MariaDB',
  'mongo':'MongoDB','mongodb':'MongoDB',
  'redis':'Redis','elasticsearch':'Elasticsearch','opensearch':'OpenSearch',
  'dynamodb':'DynamoDB','firebase':'Firebase','firestore':'Firestore',
  'clickhouse':'ClickHouse','supabase':'Supabase',
  'aws':'AWS','amazon web services':'AWS',
  'gcp':'GCP','google cloud':'GCP','google cloud platform':'GCP',
  'azure':'Azure','microsoft azure':'Azure',
  'docker':'Docker','kubernetes':'Kubernetes','k8s':'Kubernetes',
  'terraform':'Terraform','helm':'Helm','ansible':'Ansible',
  'ci/cd':'CI/CD','cicd':'CI/CD',
  'github actions':'GitHub Actions','gitlab ci':'GitLab CI',
  'jenkins':'Jenkins','circleci':'CircleCI','argocd':'ArgoCD',
  'nginx':'Nginx','prometheus':'Prometheus','grafana':'Grafana','datadog':'Datadog',
  'java':'Java','c++':'C++','cpp':'C++','c#':'C#','csharp':'C#',
  'go':'Go','golang':'Go','rust':'Rust','ruby':'Ruby','php':'PHP',
  'swift':'Swift','kotlin':'Kotlin','scala':'Scala','bash':'Bash',
  'html':'HTML','html5':'HTML','css':'CSS','css3':'CSS',
  'sass':'Sass','scss':'Sass','tailwind':'Tailwind CSS','tailwindcss':'Tailwind CSS',
  'bootstrap':'Bootstrap','material ui':'Material UI','mui':'Material UI',
  'sql':'SQL','nosql':'NoSQL','graphql':'GraphQL',
  'rest':'REST API','restful':'REST API','rest api':'REST API','grpc':'gRPC',
  'git':'Git','github':'GitHub','gitlab':'GitLab',
  'jira':'Jira','figma':'Figma','linux':'Linux','postman':'Postman',
  'kafka':'Apache Kafka','apache kafka':'Apache Kafka',
  'spark':'Apache Spark','airflow':'Apache Airflow',
  'react native':'React Native','flutter':'Flutter',
  'jest':'Jest','pytest':'pytest','cypress':'Cypress','playwright':'Playwright',
  'langchain':'LangChain','llamaindex':'LlamaIndex','openai':'OpenAI API',
  'huggingface':'Hugging Face','hugging face':'Hugging Face',
  'dbt':'dbt','tableau':'Tableau','power bi':'Power BI',
};

// ── Skill helpers ─────────────────────────────────────────────────────────
function normalizeSkill(raw) {
  const key = raw.trim().toLowerCase();
  return SKILL_ALIASES[key] || raw.trim().replace(/\b\w/g, c => c.toUpperCase());
}

function extractSkillsFromText(text) {
  const lower = text.toLowerCase();
  const found = new Map();
  // Sort longest alias first so "react native" matches before "react"
  const sorted = Object.entries(SKILL_ALIASES).sort((a, b) => b[0].length - a[0].length);
  for (const [alias, canonical] of sorted) {
    if (!found.has(canonical) && lower.includes(alias)) found.set(canonical, canonical);
  }
  return [...found.values()];
}

// ── File handling ─────────────────────────────────────────────────────────
const dropZone = document.getElementById('dropZone');
const fileInput = document.getElementById('fileInput');

dropZone.addEventListener('dragover', e => { e.preventDefault(); dropZone.classList.add('drag-over'); });
dropZone.addEventListener('dragleave', () => dropZone.classList.remove('drag-over'));
dropZone.addEventListener('drop', e => {
  e.preventDefault();
  dropZone.classList.remove('drag-over');
  addFiles(e.dataTransfer.files);
});
fileInput.addEventListener('change', e => addFiles(e.target.files));

function addFiles(newFiles) {
  Array.from(newFiles).forEach(f => {
    if (!files.find(x => x.name === f.name)) files.push(f);
  });
  renderFiles();
}

function removeFile(i) {
  files.splice(i, 1);
  renderFiles();
}

function formatSize(b) {
  if (b < 1024) return b + ' B';
  if (b < 1048576) return (b / 1024).toFixed(1) + ' KB';
  return (b / 1048576).toFixed(1) + ' MB';
}

function renderFiles() {
  document.getElementById('fileList').innerHTML = files.map((f, i) => {
    const ext = f.name.split('.').pop().toUpperCase();
    return `<div class="file-tag">
      <span class="file-ext">${ext}</span>
      <span class="file-name">${f.name}</span>
      <span class="file-size">${formatSize(f.size)}</span>
      <span class="file-remove" onclick="removeFile(${i})">&#215;</span>
    </div>`;
  }).join('');
}

// ── Mock resume skills (replace with real parser output) ──────────────────
function getMockResumeSkills() {
  const base = ['Python','FastAPI','PostgreSQL','Docker','Git','REST API','Redis','Linux','JavaScript','React','Nginx','Bash','GitHub'];
  const extra = files.length > 1 ? ['Kubernetes','Terraform','CI/CD','pytest','TypeScript'] : [];
  return [...base, ...extra];
}

// ── Loading animation ─────────────────────────────────────────────────────
function animateLoading(steps, interval) {
  return new Promise(resolve => {
    let i = 0;
    const el = document.getElementById('loadingText');
    el.textContent = steps[0];
    const t = setInterval(() => {
      i++;
      if (i >= steps.length) { clearInterval(t); resolve(); return; }
      el.textContent = steps[i];
    }, interval);
  });
}

// ── Main analysis ─────────────────────────────────────────────────────────
async function runAnalysis() {
  const jd = document.getElementById('jdInput').value.trim();
  if (!files.length && !jd) { document.getElementById('jdInput').focus(); return; }

  const btn = document.getElementById('analyzeBtn');
  btn.disabled = true;
  document.getElementById('loadingRow').classList.add('visible');
  document.getElementById('results').classList.remove('visible');

  const steps = ['Parsing resumes…', 'Normalizing skills…', 'Running semantic match…', 'Generating report…'];
  await animateLoading(steps, 500);

  // ── Replace this block with your real API call ────────────────────────
  // const formData = new FormData();
  // files.forEach(f => formData.append('files', f));
  // formData.append('job_description', jd);
  // const res = await fetch('/api/v1/match', { method: 'POST', body: formData });
  // const data = await res.json();
  // renderResults(data);
  // return;
  // ──────────────────────────────────────────────────────────────────────

  // Mock computation
  const jdSkills = jd
    ? extractSkillsFromText(jd)
    : ['Python', 'FastAPI', 'PostgreSQL', 'Docker', 'Redis', 'Kubernetes', 'CI/CD'];
  const resumeSkills = getMockResumeSkills();

  const matched = jdSkills.filter(s => resumeSkills.map(x => x.toLowerCase()).includes(s.toLowerCase()));
  const missing = jdSkills.filter(s => !resumeSkills.map(x => x.toLowerCase()).includes(s.toLowerCase()));
  const bonus   = resumeSkills.filter(s => !jdSkills.map(x => x.toLowerCase()).includes(s.toLowerCase())).slice(0, 10);
  const score   = jdSkills.length ? Math.round((matched.length / jdSkills.length) * 100) : 68;

  const categories = [
    { name: 'Backend / languages', pct: clamp(score + rand(-8, 12)),  color: '#4ade80' },
    { name: 'Databases',           pct: clamp(score + rand(-10, 15)), color: '#38bdf8' },
    { name: 'DevOps / infra',      pct: clamp(score + rand(-25, 5)),  color: '#fb923c' },
    { name: 'Frameworks',          pct: clamp(score + rand(-5, 18)),  color: '#a78bfa' },
    { name: 'Frontend',            pct: clamp(score + rand(-30, 10)), color: '#c8f060' },
  ];

  setTimeout(() => {
    renderResults({ matched, missing, bonus, score, categories, normalized_skills: resumeSkills });
    document.getElementById('loadingRow').classList.remove('visible');
    btn.disabled = false;
  }, 200);
}

// ── Utilities ─────────────────────────────────────────────────────────────
function clamp(v) { return Math.max(0, Math.min(100, v)); }
function rand(a, b) { return Math.round(Math.random() * (b - a) + a); }

// ── Render results ────────────────────────────────────────────────────────
function renderResults({ matched, missing, bonus, score, categories, normalized_skills }) {
  const color = score >= 70 ? 'green' : score >= 45 ? 'amber' : 'red';

  document.getElementById('scoreOverall').textContent = score + '%';
  document.getElementById('scoreOverall').className   = 'score-value ' + color;
  document.getElementById('scoreMatched').textContent = matched.length;
  document.getElementById('scoreMissing').textContent = missing.length;
  document.getElementById('scoreBonus').textContent   = bonus.length;

  renderChips('chipsMatched',    matched,           'match');
  renderChips('chipsMissing',    missing,           'miss');
  renderChips('chipsBonus',      bonus,             'extra');
  renderChips('chipsNormalized', normalized_skills, 'extra');

  document.getElementById('categoryBars').innerHTML = categories.map(c => `
    <div class="bar-row">
      <span class="bar-name">${c.name}</span>
      <div class="bar-track">
        <div class="bar-fill" style="width:0%;background:${c.color};" data-pct="${c.pct}"></div>
      </div>
      <span class="bar-pct">${c.pct}%</span>
    </div>`).join('');

  document.getElementById('results').classList.add('visible');

  // Animate bars after paint
  requestAnimationFrame(() => requestAnimationFrame(() => {
    document.querySelectorAll('.bar-fill').forEach(el => {
      el.style.width = el.dataset.pct + '%';
    });
  }));
}

function renderChips(id, skills, type) {
  const el = document.getElementById(id);
  el.innerHTML = skills.length
    ? skills.map(s => `<span class="chip ${type}">${s}</span>`).join('')
    : '<span class="empty-chips">None</span>';
}

// ── Reset ─────────────────────────────────────────────────────────────────
function resetAll() {
  files.length = 0;
  renderFiles();
  fileInput.value = '';
  document.getElementById('jdInput').value = '';
  document.getElementById('results').classList.remove('visible');
}
