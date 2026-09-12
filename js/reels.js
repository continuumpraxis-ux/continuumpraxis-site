(function () {
  function loadEmbed(hostBtn) {
    var wrap = hostBtn.closest(".reel-media--click");
    if (!wrap || wrap.classList.contains("is-loaded")) return;
    var src = wrap.getAttribute("data-embed-src");
    if (!src) return;
    var host = wrap.querySelector(".reel-iframe-host");
    if (!host) return;
    var iframe = document.createElement("iframe");
    iframe.className = "reel-iframe";
    iframe.src = src;
    iframe.title = "Instagram embed";
    iframe.width = "100%";
    iframe.height = "540";
    iframe.setAttribute("loading", "lazy");
    iframe.setAttribute("allowfullscreen", "");
    iframe.setAttribute(
      "allow",
      "encrypted-media; clipboard-write; web-share; fullscreen"
    );
    iframe.setAttribute("scrolling", "no");
    iframe.frameBorder = "0";
    host.hidden = false;
    host.appendChild(iframe);
    wrap.classList.add("is-loaded");
    if (
      window.instgrm &&
      window.instgrm.Embeds &&
      typeof window.instgrm.Embeds.process === "function"
    ) {
      try {
        window.instgrm.Embeds.process();
      } catch (e) {}
    }
  }

  document.addEventListener("click", function (ev) {
    var btn = ev.target.closest(".reel-poster");
    if (btn) {
      ev.preventDefault();
      loadEmbed(btn);
    }
  });

  function processEmbeds() {
    if (
      window.instgrm &&
      window.instgrm.Embeds &&
      typeof window.instgrm.Embeds.process === "function"
    ) {
      try {
        window.instgrm.Embeds.process();
      } catch (e) {}
    }
  }

  if (document.readyState === "complete") processEmbeds();
  else window.addEventListener("load", processEmbeds);
})();
