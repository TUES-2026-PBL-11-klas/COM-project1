// get questions from the server
async function fetchQuestions(quizId) {
    return [
        {
            "q": "test",
            "options": ["test", "test", "test", "test"]
        },
        {
            "q": "test",
            "options": ["test", "test", "test", "test"]
        },
        {
            "q": "test",
            "options": ["test", "test", "test", "test"]
        },
        {
            "q": "test",
            "options": ["test", "test", "test", "test"]
        },
        {
            "q": "test",
            "options": ["test", "test", "test", "test"]
        },
        {
            "q": "test",
            "options": ["test", "test", "test", "test"]
        },
        {
            "q": "test",
            "options": ["test", "test", "test", "test"]
        },
        {
            "q": "test",
            "options": ["test", "test", "test", "test"]
        },
        {
            "q": "test",
            "options": ["test", "test", "test", "test"]
        },
        {
            "q": "test",
            "options": ["test", "test", "test", "test"]
        }
    ]

    const response = await fetch(`/api/quizzes/v1.0/quizzes/${quizId}/questions`);
    if (!response.ok) throw new Error(`Server returned ${response.status}`);
    const data = await response.json();
    return data.map(q => ({
        q: q.question,
        options: q.options,
    })); // some example layout (tbd)
}

// send answers to server with some layout
async function submitAnswers(quizId, answers, secondsElapsed) {
    return;

    const response = await fetch(`/api/results/v1.0/attempts`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ quizId, elapsed: secondsElapsed, answers }), // tbd
    });
    if (!response.ok) throw new Error(`Submit failed: ${response.status}`);
    const data = await response.json();
    // Server should return { resultsUrl: "/results/42" } (or similar)
    window.location.href = data.resultsUrl;
}

function initQuiz(quizId, QUESTIONS) {
    const KEYS = ["A", "B", "C", "D"];

    // ── State ────────────────────────────────────────────────
    let current = 0;
    let answers = new Array(QUESTIONS.length).fill(null);
    let timerInterval = null;
    let secondsElapsed = 0;

    // ── DOM refs ─────────────────────────────────────────────
    const viewport = document.getElementById("quiz-viewport");
    const progressFill = document.getElementById("progress-fill");
    const progressLabel = document.getElementById("progress-label");
    const timerDisplay = document.getElementById("timer-display");
    const qMap = document.getElementById("q-map");

    // ── Question map dots ─────────────────────────────────────
    function buildMap() {
        qMap.innerHTML = "";
        QUESTIONS.forEach((_, i) => {
            const dot = document.createElement("div");
            dot.className = "q-dot";
            dot.title = `Question ${i + 1}`;
            dot.addEventListener("click", () => goTo(i));
            dot.id = `dot-${i}`;
            qMap.appendChild(dot);
        });
    }

    function updateMapDots() {
        QUESTIONS.forEach((_, i) => {
            const dot = document.getElementById(`dot-${i}`);
            dot.className = "q-dot";
            if (i === current) dot.classList.add("current");
            else if (answers[i] !== null) dot.classList.add("answered");
        });
    }

    // ── Card builder ──────────────────────────────────────────
    function buildCard(index) {
        const qdata = QUESTIONS[index];
        const card = document.createElement("div");
        card.className = "quiz-card";
        card.id = `card-${index}`;
        const isLast = index === QUESTIONS.length - 1;

        card.innerHTML = `
            <div class="question-number">Question ${index + 1} of ${QUESTIONS.length}</div>
            <p class="question-text">${qdata.q}</p>
            <div class="options-grid">
                ${qdata.options.map((opt, oi) => `
                    <button class="option-btn" id="opt-${index}-${oi}" data-oi="${oi}">
                        <span class="option-key">${KEYS[oi]}</span>
                        ${opt}
                    </button>
                `).join("")}
            </div>
            <div class="nav-row">
                ${index > 0
                ? `<button class="btn-back" id="back-${index}">← Back</button>`
                : `<span></span>`}
                <button id="next-${index}" ${isLast ? "" : "disabled"}>
                    ${isLast ? "Finish" : "Next →"}
                </button>
            </div>
        `;

        // Restore selected answer if revisiting
        if (answers[index] !== null) {
            card.querySelector(`#opt-${index}-${answers[index]}`)?.classList.add("selected");
            if (!isLast) card.querySelector(`#next-${index}`).disabled = false;
        }

        card.querySelectorAll(".option-btn").forEach(btn => {
            btn.addEventListener("click", () => selectOption(index, parseInt(btn.dataset.oi)));
        });

        if (index > 0) {
            card.querySelector(`#back-${index}`).addEventListener("click", () => goTo(index - 1));
        }

        if (isLast) {
            card.querySelector(`#next-${index}`).addEventListener("click", () => finish());
        } else {
            card.querySelector(`#next-${index}`).addEventListener("click", () => goTo(index + 1));
        }

        return card;
    }

    function selectOption(qi, oi) {
        answers[qi] = oi;
        const card = document.getElementById(`card-${qi}`);
        card.querySelectorAll(".option-btn").forEach(b => b.classList.remove("selected"));
        card.querySelector(`#opt-${qi}-${oi}`).classList.add("selected");
        if (qi < QUESTIONS.length - 1) card.querySelector(`#next-${qi}`).disabled = false;
        updateMapDots();
        updateProgress();
    }

    // ── Navigation ────────────────────────────────────────────
    let cards = {};

    function getOrBuildCard(index) {
        if (!cards[index]) {
            cards[index] = buildCard(index);
            viewport.appendChild(cards[index]);
        }
        return cards[index];
    }

    function goTo(index) {
        if (index < 0 || index >= QUESTIONS.length) return;

        const prevCard = cards[current];
        current = index;
        const nextCard = getOrBuildCard(index);

        if (prevCard) prevCard.classList.remove("active");
        nextCard.classList.add("active");

        updateProgress();
        updateMapDots();
    }

    function updateProgress() {
        const answered = answers.filter(a => a !== null).length;
        progressFill.style.width = (answered / QUESTIONS.length * 100) + "%";
        progressLabel.textContent = `${answered} / ${QUESTIONS.length} answered`;
    }

    // ── Timer ─────────────────────────────────────────────────
    function startTimer() {
        timerInterval = setInterval(() => {
            secondsElapsed++;
            const m = Math.floor(secondsElapsed / 60);
            const s = secondsElapsed % 60;
            timerDisplay.textContent =
                `${String(m).padStart(2, "0")}:${String(s).padStart(2, "0")}`;
        }, 1000);
    }

    // ── Finish ────────────────────────────────────────────────
    async function finish() {
        clearInterval(timerInterval);
        const finishBtn = document.getElementById(`next-${QUESTIONS.length - 1}`);
        finishBtn.disabled = true;
        finishBtn.textContent = "Submitting…";

        try {
            await submitAnswers(quizId, answers, secondsElapsed);
            // submitAnswers redirects on success; nothing more to do here
        } catch (err) {
            finishBtn.disabled = false;
            finishBtn.textContent = "Finish";
            // Show error inline below the button
            let errEl = document.getElementById("submit-error");
            if (!errEl) {
                errEl = document.createElement("p");
                errEl.id = "submit-error";
                errEl.style.cssText = "color:#dc2626;font-size:0.85rem;margin-top:0.5rem;";
                finishBtn.parentElement.after(errEl);
            }
            errEl.textContent = `Could not submit: ${err.message}`;
            startTimer(); // resume timer so elapsed is accurate on retry
        }
    }

    // ── Start ─────────────────────────────────────────────────
    buildMap();
    getOrBuildCard(0).classList.add("active");
    updateProgress();
    updateMapDots();
    startTimer();
}

// ════════════════════════════════════════════════════════════
// ENTRY POINT
// ════════════════════════════════════════════════════════════

// Quiz ID comes from <main data-quiz-id="42">
const quizId = document.querySelector("main").dataset.quizId ?? "1";

// Show loading state while fetching
const loadingEl = document.createElement("p");
loadingEl.textContent = "Loading questions…";
loadingEl.style.cssText = "text-align:center;color:var(--pico-muted-color);margin:3rem 0;";
document.getElementById("quiz-viewport").replaceWith(loadingEl);

(async () => {
    try {
        const questions = await fetchQuestions(quizId);

        const vp = document.createElement("div");
        vp.className = "quiz-card-viewport";
        vp.id = "quiz-viewport";
        loadingEl.replaceWith(vp);

        initQuiz(quizId, questions);
    } catch (err) {
        loadingEl.innerHTML =
            `<strong>Could not load questions.</strong><br>
             <small style="color:var(--pico-muted-color)">${err.message}</small>`;
    }
})();
