(function () {
  // Self-hosted reel players: autoplay muted clips that are on screen,
  // pause the rest, and toggle play/pause on tile click. Instagram is only
  // reached via the explicit "Open on Instagram" link under each card —
  // never via the play control.
  var reduceMotion =
    window.matchMedia &&
    window.matchMedia("(prefers-reduced-motion: reduce)").matches;

  function markPlaying(media, on) {
    if (!media) return;
    if (on) media.classList.add("is-playing");
    else media.classList.remove("is-playing");
  }

  var videos = Array.prototype.slice.call(
    document.querySelectorAll(".reel-media video")
  );

  function pauseOthers(except) {
    videos.forEach(function (v) {
      if (v === except) return;
      v.pause();
      markPlaying(v.closest(".reel-media"), false);
    });
  }

  function tryPlay(v) {
    if (reduceMotion) return;
    var p = v.play();
    if (p && typeof p.catch === "function") p.catch(function () {});
  }

  function toggleVideo(v) {
    if (!v) return;
    if (v.paused) {
      pauseOthers(v);
      tryPlay(v);
      markPlaying(v.closest(".reel-media"), true);
    } else {
      v.pause();
      markPlaying(v.closest(".reel-media"), false);
    }
  }

  if ("IntersectionObserver" in window && videos.length) {
    var io = new IntersectionObserver(
      function (entries) {
        entries.forEach(function (entry) {
          var v = entry.target;
          var media = v.closest(".reel-media");
          if (entry.isIntersecting && entry.intersectionRatio >= 0.5) {
            tryPlay(v);
          } else {
            v.pause();
          }
          if (media) markPlaying(media, !v.paused);
        });
      },
      { threshold: [0, 0.5, 1] }
    );
    videos.forEach(function (v) {
      io.observe(v);
      v.addEventListener("playing", function () {
        markPlaying(v.closest(".reel-media"), true);
      });
      v.addEventListener("pause", function () {
        markPlaying(v.closest(".reel-media"), false);
      });
    });
  } else {
    videos.slice(0, 4).forEach(tryPlay);
  }

  document.addEventListener("click", function (ev) {
    // Explicit Instagram links under each card — leave them alone.
    if (ev.target.closest && ev.target.closest("a[href*='instagram.com']")) {
      return;
    }
    var media = ev.target.closest ? ev.target.closest(".reel-media") : null;
    if (!media) return;
    var video = media.querySelector("video");
    if (!video) return;
    ev.preventDefault();
    toggleVideo(video);
  });

  document.addEventListener("keydown", function (ev) {
    if (ev.key !== "Enter" && ev.key !== " ") return;
    var media =
      document.activeElement && document.activeElement.classList
        ? document.activeElement
        : null;
    if (!media || !media.classList.contains("reel-media")) return;
    var video = media.querySelector("video");
    if (!video) return;
    ev.preventDefault();
    toggleVideo(video);
  });
})();
