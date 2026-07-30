// Hero demo: a faithful little recreation of the Nectar app working through a
// drawing set. The markup ships in its finished state; when motion is allowed
// we rewind it and replay the pipeline in a loop.

const SHEETS = [
  { file: "scan_0041.pdf", num: "A-101", title: "FIRST FLOOR PLAN", final: "A-101 - First Floor Plan.pdf" },
  { file: "scan_0042.pdf", num: "A-201", title: "EXTERIOR ELEVATIONS", final: "A-201 - Exterior Elevations.pdf" },
  { file: "scan_0043.pdf", num: "S-301", title: "FOUNDATION DETAILS", final: "S-301 - Foundation Details.pdf" },
  { file: "scan_0044.pdf", num: "E-101", title: "LIGHTING PLAN, LEVEL 1", final: "E-101 - Lighting Plan, Level 1.pdf", review: true },
  { file: "scan_0045.pdf", num: "M-401", title: "HVAC PLAN, LEVEL 1", final: "M-401 - HVAC Plan, Level 1.pdf" },
  { file: "scan_0046.pdf", num: "P-102", title: "PLUMBING RISERS", final: "P-102 - Plumbing Risers.pdf" },
];

const STATUS = {
  uploading: { label: "Uploading", classes: ["bg-white/5", "text-zinc-400"] },
  inspecting: { label: "Inspecting", classes: ["bg-sky-400/10", "text-sky-300"] },
  verifying: { label: "Verifying", classes: ["bg-sky-400/10", "text-sky-300"] },
  review: { label: "Review", classes: ["bg-amber-400/10", "text-amber-300"] },
  ready: { label: "Ready", classes: ["bg-emerald-400/10", "text-emerald-300"] },
  done: { label: "Done", classes: ["bg-emerald-400/10", "text-emerald-300"] },
};

const ALL_STATUS_CLASSES = Object.values(STATUS).flatMap((s) => s.classes);

export function initDemo() {
  const root = document.getElementById("demo");
  if (!root) return;
  if (window.matchMedia("(prefers-reduced-motion: reduce)").matches) return;

  const rows = [...root.querySelectorAll("[data-demo-row]")].map((el, i) => ({
    el,
    data: SHEETS[i],
    file: el.querySelector('[data-cell="file"]'),
    num: el.querySelector('[data-cell="num"]'),
    title: el.querySelector('[data-cell="title"]'),
    status: el.querySelector('[data-cell="status"]'),
    autoMarks: [...el.querySelectorAll("[data-auto]")],
  }));
  const summary = document.getElementById("demo-summary");
  const renameHint = document.getElementById("demo-rename");
  if (rows.some((r) => !r.data || !r.file || !r.num || !r.title || !r.status)) return;

  let visible = false;
  new IntersectionObserver(
    (entries) => {
      visible = entries[0].isIntersecting;
    },
    { threshold: 0.35 },
  ).observe(root);

  const sleep = (ms) => new Promise((resolve) => setTimeout(resolve, ms));
  const waitUntilVisible = async () => {
    while (!visible) await sleep(200);
  };

  function setStatus(row, key) {
    row.status.classList.remove(...ALL_STATUS_CLASSES);
    row.status.classList.add(...STATUS[key].classes);
    row.status.textContent = STATUS[key].label;
  }

  function setSummary(text) {
    if (summary) summary.textContent = text;
  }

  async function type(el, text) {
    el.classList.add("demo-caret");
    el.textContent = "";
    for (const char of text) {
      el.textContent += char;
      await sleep(24);
    }
    el.classList.remove("demo-caret");
  }

  async function swapText(el, text) {
    el.classList.add("is-swapping");
    await sleep(350);
    el.textContent = text;
    el.classList.remove("is-swapping");
    await sleep(350);
  }

  function reset() {
    for (const row of rows) {
      row.el.style.opacity = "0";
      row.file.textContent = row.data.file;
      row.num.textContent = "";
      row.title.textContent = "";
      setStatus(row, "uploading");
      for (const mark of row.autoMarks) mark.style.opacity = "0";
    }
    renameHint?.style.setProperty("opacity", "0");
    setSummary(`${rows.length} sheets · uploading`);
  }

  async function play() {
    reset();
    await sleep(400);

    for (const row of rows) {
      row.el.style.transition = "opacity 0.4s ease";
      row.el.style.opacity = "1";
      await sleep(120);
    }

    await sleep(300);
    setSummary(`${rows.length} sheets · reading title blocks`);
    for (const row of rows) {
      setStatus(row, "inspecting");
      await sleep(140);
    }

    let ready = 0;
    for (const row of rows) {
      setStatus(row, "verifying");
      await type(row.num, row.data.num);
      await type(row.title, row.data.title);
      for (const mark of row.autoMarks) {
        mark.style.transition = "opacity 0.3s ease";
        mark.style.opacity = "1";
      }
      if (row.data.review) {
        setStatus(row, "review");
        setSummary(`${rows.length} sheets · ${ready} ready · 1 to review`);
      } else {
        ready += 1;
        setStatus(row, "ready");
        setSummary(`${rows.length} sheets · ${ready} ready${ready < rows.length ? " · reading" : ""}`);
      }
      await sleep(220);
    }

    // The one uncertain sheet gets a quick human confirm.
    const reviewRow = rows.find((r) => r.data.review);
    await sleep(1200);
    if (reviewRow) {
      setStatus(reviewRow, "ready");
      setSummary(`${rows.length} sheets · ${rows.length} ready`);
    }

    // Rename: originals become filed names.
    await sleep(900);
    if (renameHint) {
      renameHint.style.transition = "opacity 0.3s ease";
      renameHint.style.opacity = "1";
    }
    await sleep(900);
    await Promise.all(
      rows.map(async (row, i) => {
        await sleep(i * 120);
        await swapText(row.file, row.data.final);
        setStatus(row, "done");
        for (const mark of row.autoMarks) mark.style.opacity = "0";
      }),
    );
    setSummary(`${rows.length} sheets · renamed and filed`);

    await sleep(4000);
  }

  (async () => {
    // Let the loop idle until the demo scrolls into view, then replay forever.
    for (;;) {
      await waitUntilVisible();
      await play();
    }
  })();
}
