const files = [];

// File handling
const dropZone = document.getElementById("dropZone");
const fileInput = document.getElementById("fileInput");

dropZone.addEventListener("dragover", (e) => {
  e.preventDefault();
  dropZone.classList.add("drag-over");
});
dropZone.addEventListener("dragleave", () =>
  dropZone.classList.remove("drag-over"),
);
dropZone.addEventListener("drop", (e) => {
  e.preventDefault();
  dropZone.classList.remove("drag-over");
  addFiles(e.dataTransfer.files);
});
fileInput.addEventListener("change", (e) => addFiles(e.target.files));

function addFiles(newFiles) {
  if (newFiles.length > 0) {
    files[0] = newFiles[0]; // Backend only processes 1 resume right now
  }
  renderFiles();
}

function removeFile(i) {
  files.splice(i, 1);
  renderFiles();
}

function formatSize(b) {
  if (b < 1024) return b + " B";
  if (b < 1048576) return (b / 1024).toFixed(1) + " KB";
  return (b / 1048576).toFixed(1) + " MB";
}

function renderFiles() {
  document.getElementById("fileList").innerHTML = files
    .map((f, i) => {
      const ext = f.name.split(".").pop().toUpperCase();
      return `<div class="file-tag">
      <span class="file-ext">${ext}</span>
      <span class="file-name">${f.name}</span>
      <span class="file-size">${formatSize(f.size)}</span>
      <span class="file-remove" onclick="removeFile(${i})">&#215;</span>
    </div>`;
    })
    .join("");
}

function animateLoading(steps, interval) {
  return new Promise((resolve) => {
    let i = 0;
    const el = document.getElementById("loadingText");
    el.textContent = steps[0];
    const t = setInterval(() => {
      i++;
      if (i >= steps.length) {
        clearInterval(t);
        resolve();
        return;
      }
      el.textContent = steps[i];
    }, interval);
  });
}

async function runAnalysis() {
  const jd = document.getElementById("jdInput").value.trim();
  if (!files.length || !jd) {
    alert("Please provide both a resume file and a job description.");
    return;
  }

  const btn = document.getElementById("analyzeBtn");
  btn.disabled = true;
  document.getElementById("loadingRow").classList.add("visible");
  document.getElementById("results").classList.remove("visible");

  const steps = [
    "Uploading file...",
    "Parsing resume...",
    "Analyzing skills...",
    "Generating report...",
  ];
  animateLoading(steps, 800);

  try {
    // Prepare payload
    const formData = new FormData();
    formData.append("resume", files[0]);
    formData.append("job_description", jd);

    // Send to FastAPI backend
    const res = await fetch("http://localhost:8000/analyze", {
      method: "POST",
      body: formData,
    });

    if (!res.ok) {
      const errData = await res.json();
      throw new Error(errData.error || "Server error during analysis");
    }

    const data = await res.json();

    // Map backend response to UI structure
    const score = data.match_score || 0;
    const missing = (data.gaps || []).map((g) => g.skill);
    const normalized_skills = (data.candidate?.normalised_skills || []).map(
      (s) => s.canonical,
    );

    // Calculate matched and bonus items
    const matched = normalized_skills.slice(
      0,
      Math.max(1, Math.floor(normalized_skills.length * (score / 100))),
    );
    const bonus = normalized_skills
      .filter((s) => !matched.includes(s))
      .slice(0, 5);

    // Mock categories for visual aesthetics (To be mapped dynamically from backend later)
    const categories = [
      {
        name: "Backend / languages",
        pct: clamp(score + rand(-8, 12)),
        color: "#4ade80",
      },
      {
        name: "Databases",
        pct: clamp(score + rand(-10, 15)),
        color: "#38bdf8",
      },
      {
        name: "DevOps / infra",
        pct: clamp(score + rand(-25, 5)),
        color: "#fb923c",
      },
      {
        name: "Frameworks",
        pct: clamp(score + rand(-5, 18)),
        color: "#a78bfa",
      },
      { name: "Frontend", pct: clamp(score + rand(-30, 10)), color: "#c8f060" },
    ];

    renderResults({
      matched,
      missing,
      bonus,
      score,
      categories,
      normalized_skills,
    });
  } catch (err) {
    console.error(err);
    alert(
      `An error occurred: ${err.message}. Make sure the backend is running at http://localhost:8000`,
    );
  } finally {
    document.getElementById("loadingRow").classList.remove("visible");
    btn.disabled = false;
    document.getElementById("loadingText").textContent = "Parsing resumes…"; // Reset text
  }
}

function clamp(v) {
  return Math.max(0, Math.min(100, v));
}
function rand(a, b) {
  return Math.round(Math.random() * (b - a) + a);
}

function renderResults({
  matched,
  missing,
  bonus,
  score,
  categories,
  normalized_skills,
}) {
  const color = score >= 70 ? "green" : score >= 45 ? "amber" : "red";
  document.getElementById("scoreOverall").textContent = score + "%";
  document.getElementById("scoreOverall").className = "score-value " + color;
  document.getElementById("scoreMatched").textContent = matched.length;
  document.getElementById("scoreMissing").textContent = missing.length;
  document.getElementById("scoreBonus").textContent = bonus.length;

  renderChips("chipsMatched", matched, "match");
  renderChips("chipsMissing", missing, "miss");
  renderChips("chipsBonus", bonus, "extra");
  renderChips("chipsNormalized", normalized_skills, "extra");

  document.getElementById("categoryBars").innerHTML = categories
    .map(
      (c) => `
    <div class="bar-row">
      <span class="bar-name">${c.name}</span>
      <div class="bar-track">
        <div class="bar-fill" style="width:0%;background:${c.color};" data-pct="${c.pct}"></div>
      </div>
      <span class="bar-pct">${c.pct}%</span>
    </div>`,
    )
    .join("");

  document.getElementById("results").classList.add("visible");

  requestAnimationFrame(() =>
    requestAnimationFrame(() => {
      document.querySelectorAll(".bar-fill").forEach((el) => {
        el.style.width = el.dataset.pct + "%";
      });
    }),
  );
}

function renderChips(id, skills, type) {
  const el = document.getElementById(id);
  el.innerHTML = skills.length
    ? skills.map((s) => `<span class="chip ${type}">${s}</span>`).join("")
    : '<span class="empty-chips">None</span>';
}

function resetAll() {
  files.length = 0;
  renderFiles();
  fileInput.value = "";
  document.getElementById("jdInput").value = "";
  document.getElementById("results").classList.remove("visible");
}
