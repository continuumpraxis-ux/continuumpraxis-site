(function () {
  // Mobile nav toggle is handled in main.js. This module only drives the
  // self-hosted reel players: autoplay the clips that are on screen, pause the
  // rest, and send a click on any tile to the original post on Instagram.
  var reduceMotion =
    window.matchMedia &&
    window.matchMedia("(prefers-reduced-motion: reduce)").matches;

  function markPlaying(media, on) {
    if (on) media.classList.add("is-playing");
    else media.classList.remove("is-playing");
  }

  var videos = Array.prototype.slice.call(
    document.querySelectorAll(".reel-media video")
  );

  function tryPlay(v) {
    if (reduceMotion) return;
    var p = v.play();
    if (p && typeof p.catch === "function") p.catch(function () {});
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
        var m = v.closest(".reel-media");
        if (m) markPlaying(m, true);
      });
      v.addEventListener("pause", function () {
        var m = v.closest(".reel-media");
        if (m) markPlaying(m, false);
      });
    });
  } else {
    // No IntersectionObserver: at least attempt to play the first few.
    videos.slice(0, 4).forEach(tryPlay);
  }

  // Clicking anywhere on a tile opens the original reel/post on Instagram.
  document.addEventListener("click", function (ev) {
    var media = ev.target.closest ? ev.target.closest(".reel-media") : null;
    if (!media) return;
    var href = media.getAttribute("data-href");
    if (!href) return;
    ev.preventDefault();
    window.open(href, "_blank", "noopener,noreferrer");
  });

  // Keyboard access: Enter/Space on a focused tile opens Instagram.
  document.addEventListener("keydown", function (ev) {
    if (ev.key !== "Enter" && ev.key !== " ") return;
    var media =
      document.activeElement && document.activeElement.classList
        ? document.activeElement
        : null;
    if (!media || !media.classList.contains("reel-media")) return;
    var href = media.getAttribute("data-href");
    if (!href) return;
    ev.preventDefault();
    window.open(href, "_blank", "noopener,noreferrer");
  });
})();
