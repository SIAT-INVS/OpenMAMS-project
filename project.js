"use strict";

// Keep the compact mobile navigation keyboard-accessible and close it after use.
const navigation = document.querySelector(".navigation");
const menuToggle = document.querySelector(".menu-toggle");
if (navigation && menuToggle) {
  const closeMenu = () => menuToggle.setAttribute("aria-expanded", "false");
  menuToggle.hidden = false;
  navigation.classList.add("menu-ready");
  menuToggle.addEventListener("click", () => {
    const expanded = menuToggle.getAttribute("aria-expanded") === "true";
    menuToggle.setAttribute("aria-expanded", String(!expanded));
  });
  navigation.addEventListener("click", event => {
    if (event.target.closest("a")) closeMenu();
  });
  document.addEventListener("keydown", event => {
    if (event.key === "Escape" && menuToggle.getAttribute("aria-expanded") === "true") {
      closeMenu();
      menuToggle.focus();
    }
  });
  document.addEventListener("click", event => {
    if (!navigation.contains(event.target)) closeMenu();
  });
  navigation.addEventListener("focusout", event => {
    if (!navigation.contains(event.relatedTarget)) closeMenu();
  });
  window.matchMedia("(max-width: 1100px)").addEventListener("change", closeMenu);
}

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
function isVideoVisible(video) {
  const rect = video.getBoundingClientRect();
  const width = Math.max(0, Math.min(rect.right, window.innerWidth) - Math.max(rect.left, 0));
  const height = Math.max(0, Math.min(rect.bottom, window.innerHeight) - Math.max(rect.top, 0));
  return rect.width > 0 && rect.height > 0 && width * height / (rect.width * rect.height) >= 0.1;
}
const playback = new Map(videos.map(video => [video, {
  visible: isVideoVisible(video), userPaused: false, automaticPauses: 0,
  pendingPlay: false, controlInteraction: -Infinity,
}]));

function pauseAutomatically(video) {
  if (!video.paused) {
    playback.get(video).automaticPauses += 1;
    video.pause();
  }
}

function syncPlayback(video) {
  const state = playback.get(video);
  state.visible = isVideoVisible(video);
  if (!state.visible || document.hidden || reducedMotion.matches) {
    pauseAutomatically(video);
  } else if (!state.userPaused && video.paused && !state.pendingPlay) {
    state.pendingPlay = true;
    // Rejections are retried on media readiness, page return, or a user gesture.
    Promise.resolve(video.play()).catch(() => {}).finally(() => {
      state.pendingPlay = false;
    });
  }
}

videos.forEach(video => {
  video.defaultMuted = true;
  video.muted = true;
  video.playsInline = true;
  video.setAttribute("muted", "");
  video.setAttribute("playsinline", "");
  video.setAttribute("webkit-playsinline", "");
  // Preserve native muted autoplay, including Safari's visibility handling.
  video.autoplay = !reducedMotion.matches;
  const noteControlInteraction = () => {
    if (video.controls) playback.get(video).controlInteraction = performance.now();
  };
  ["pointerdown", "touchstart", "keydown"].forEach(event =>
    video.addEventListener(event, noteControlInteraction, { passive: true }));
  video.addEventListener("pause", () => {
    const state = playback.get(video);
    if (state.automaticPauses > 0) state.automaticPauses -= 1;
    else if (!document.hidden && isVideoVisible(video) &&
        performance.now() - state.controlInteraction < 1500) state.userPaused = true;
  });
  video.addEventListener("play", () => {
    const state = playback.get(video);
    state.userPaused = false;
    if (!isVideoVisible(video) || document.hidden) pauseAutomatically(video);
  });
  ["loadedmetadata", "canplay"].forEach(event =>
    video.addEventListener(event, () => syncPlayback(video)));
  syncPlayback(video);
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
window.addEventListener("pageshow", () => videos.forEach(syncPlayback));
reducedMotion.addEventListener("change", () => videos.forEach(video => {
  video.autoplay = !reducedMotion.matches;
  syncPlayback(video);
}));
function retryOnGesture(event) {
  // Let native player controls handle their own play/pause interaction.
  if (event.target instanceof Element && event.target.closest("video[controls]")) return;
  videos.forEach(syncPlayback);
}
["touchend", "click", "keydown"].forEach(event =>
  document.addEventListener(event, retryOnGesture, { passive: true }));

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
