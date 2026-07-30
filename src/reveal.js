// Scroll reveals. The hidden state is added here, not in the markup, so the
// page is fully readable with JS disabled or prefers-reduced-motion set.
export function initReveals() {
  if (window.matchMedia("(prefers-reduced-motion: reduce)").matches) return;

  const targets = document.querySelectorAll("[data-reveal]");
  if (!targets.length) return;

  const observer = new IntersectionObserver(
    (entries) => {
      for (const entry of entries) {
        if (!entry.isIntersecting) continue;
        entry.target.classList.remove("reveal-hidden");
        observer.unobserve(entry.target);
      }
    },
    { rootMargin: "0px 0px -10% 0px" },
  );

  for (const el of targets) {
    el.classList.add("reveal-hidden");
    observer.observe(el);
  }
}
