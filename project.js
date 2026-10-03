"use strict";

// Reserve space for the navbar in the video height limit and section anchor offset.
const siteHeader = document.querySelector(".site-header");
if (siteHeader) {
  const measureHeader = () => document.documentElement.style.setProperty("--header-height", `${siteHeader.getBoundingClientRect().height}px`);
  measureHeader();
  if ("ResizeObserver" in window) new ResizeObserver(measureHeader).observe(siteHeader);
}

// Match an animated GIF's quiet loop; inline demos retain native pause/seek controls.
// Only visible demonstrations play; a visitor's manual pause is respected.
const videos = [...document.querySelectorAll("video[data-autoplay]")];
const reducedMotion = window.matchMedia("(prefers-reduced-motion: reduce)");
const playback = new Map(videos.map(video => [video, {
  visible: false, userPaused: false, automaticPauses: 0,
}]));

function pauseAutomatically(video) {
  if (!video.paused) {
    playback.get(video).automaticPauses += 1;
    video.pause();
  }
}

function syncPlayback(video) {
  const state = playback.get(video);
  if (!state.visible || document.hidden || reducedMotion.matches) {
    pauseAutomatically(video);
  } else if (!state.userPaused && video.paused) {
    video.play().catch(() => {}); // Keep the poster visible if autoplay is blocked.
  }
}

videos.forEach(video => {
  video.muted = true;
  // JavaScript handles visibility; the HTML attribute provides a no-JS fallback.
  video.removeAttribute("autoplay");
  video.addEventListener("pause", () => {
    const state = playback.get(video);
    if (state.automaticPauses > 0) state.automaticPauses -= 1;
    else state.userPaused = true;
  });
  video.addEventListener("play", () => {
    const state = playback.get(video);
    state.userPaused = false;
    if (!state.visible || document.hidden) pauseAutomatically(video);
  });
});

if ("IntersectionObserver" in window) {
  const observer = new IntersectionObserver(entries => {
    entries.forEach(entry => {
      playback.get(entry.target).visible = entry.isIntersecting && entry.intersectionRatio >= 0.1;
      syncPlayback(entry.target);
    });
  }, { threshold: [0, 0.1] });
  videos.forEach(video => observer.observe(video));
} else {
  videos.forEach(video => { playback.get(video).visible = true; syncPlayback(video); });
}

document.addEventListener("visibilitychange", () => videos.forEach(syncPlayback));
reducedMotion.addEventListener("change", () => videos.forEach(syncPlayback));

document.querySelectorAll("[data-copy]").forEach(button => {
  button.addEventListener("click", async () => {
    const code = document.getElementById(button.dataset.copy);
    const status = document.getElementById("copy-status");
    try {
      await navigator.clipboard.writeText(code.textContent.trim());
      button.textContent = "Copied ✓";
      status.textContent = "BibTeX copied to clipboard.";
      setTimeout(() => { button.textContent = "Copy BibTeX"; }, 2200);
    } catch {
      const selection = window.getSelection();
      const range = document.createRange();
      range.selectNodeContents(code);
      selection.removeAllRanges();
      selection.addRange(range);
      status.textContent = "BibTeX selected. Press Ctrl+C (Windows/Linux) or Command+C (Mac) to copy.";
    }
  });
});
