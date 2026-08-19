(function () {
  const navToggle = document.querySelector(".nav-toggle");
  const navLinks = document.querySelector(".projnav .links");

  if (navToggle && navLinks) {
    const closeNav = () => {
      navLinks.classList.remove("open");
      navToggle.setAttribute("aria-expanded", "false");
    };

    navToggle.addEventListener("click", () => {
      const open = navLinks.classList.toggle("open");
      navToggle.setAttribute("aria-expanded", String(open));
    });

    navLinks.addEventListener("click", event => {
      if (event.target.closest("a")) closeNav();
    });

    document.addEventListener("keydown", event => {
      if (event.key === "Escape") closeNav();
    });
  }

  document.querySelectorAll(".tablewrap").forEach(wrapper => {
    wrapper.tabIndex = 0;
    wrapper.setAttribute("role", "region");
    wrapper.setAttribute("aria-label", wrapper.dataset.label || "Scrollable data table");
    if (!wrapper.dataset.scrollHint) wrapper.dataset.scrollHint = "Swipe to see all columns →";
  });

  document.querySelectorAll(".swipe").forEach(box => {
    const stage = box.querySelector(".stage");
    const top = box.querySelector(".top");
    const bar = box.querySelector(".bar");
    const fullScreenButton = box.querySelector(".fsbtn");
    if (!stage || !top || !bar) return;
    let fraction = 0.5;
    let dragging = false;

    box.tabIndex = 0;
    box.setAttribute("role", "slider");
    box.setAttribute("aria-label", "Compare camera surface with LiDAR bare-earth surface");
    box.setAttribute("aria-valuemin", "2");
    box.setAttribute("aria-valuemax", "98");

    const apply = () => {
      const value = Math.round(fraction * 100);
      top.style.clipPath = `inset(0 ${100 - value}% 0 0)`;
      bar.style.left = `${value}%`;
      box.setAttribute("aria-valuenow", String(value));
      box.setAttribute("aria-valuetext", `${value}% camera surface, ${100 - value}% LiDAR bare earth`);
    };

    const setFromPointer = event => {
      const bounds = stage.getBoundingClientRect();
      fraction = Math.max(0.02, Math.min(0.98, (event.clientX - bounds.left) / bounds.width));
      apply();
    };

    box.addEventListener("pointerdown", event => {
      if (event.target === fullScreenButton) return;
      dragging = true;
      box.setPointerCapture(event.pointerId);
      setFromPointer(event);
    });

    box.addEventListener("pointermove", event => {
      if (dragging) setFromPointer(event);
    });

    ["pointerup", "pointercancel"].forEach(name => {
      box.addEventListener(name, () => { dragging = false; });
    });

    box.addEventListener("keydown", event => {
      const old = fraction;
      if (event.key === "ArrowLeft" || event.key === "ArrowDown") fraction -= 0.02;
      if (event.key === "ArrowRight" || event.key === "ArrowUp") fraction += 0.02;
      if (event.key === "PageDown") fraction -= 0.1;
      if (event.key === "PageUp") fraction += 0.1;
      if (event.key === "Home") fraction = 0.02;
      if (event.key === "End") fraction = 0.98;
      fraction = Math.max(0.02, Math.min(0.98, fraction));
      if (fraction !== old) {
        event.preventDefault();
        apply();
      }
    });

    const setFullScreen = on => {
      box.classList.toggle("fs", on);
      document.body.style.overflow = on ? "hidden" : "";
      if (fullScreenButton) {
        fullScreenButton.textContent = on ? "✕" : "⛶";
        fullScreenButton.setAttribute("aria-label", on ? "Close fullscreen comparison" : "Open fullscreen comparison");
        fullScreenButton.setAttribute("aria-pressed", String(on));
      }
      box.focus();
    };

    if (fullScreenButton) {
      fullScreenButton.addEventListener("click", () => setFullScreen(!box.classList.contains("fs")));
      document.addEventListener("keydown", event => {
        if (event.key === "Escape" && box.classList.contains("fs")) setFullScreen(false);
      });
    }

    apply();
  });

  const lightboxImages = [...document.querySelectorAll("figure img")]
    .filter(image => !image.closest(".swipe, .map-swipe, [data-p04-id]"));
  if (!lightboxImages.length) return;

  const lightbox = document.createElement("div");
  lightbox.className = "lightbox";
  lightbox.setAttribute("role", "dialog");
  lightbox.setAttribute("aria-modal", "true");
  lightbox.setAttribute("aria-label", "Enlarged map image");
  lightbox.innerHTML = `
    <button class="lightbox-close" type="button" aria-label="Close enlarged image">✕</button>
    <div class="lightbox-inner">
      <img alt="">
      <div class="cap"></div>
    </div>`;
  document.body.appendChild(lightbox);

  const expandedImage = lightbox.querySelector("img");
  const caption = lightbox.querySelector(".cap");
  const closeButton = lightbox.querySelector(".lightbox-close");
  let opener = null;

  const close = () => {
    lightbox.classList.remove("open");
    document.body.style.overflow = "";
    if (opener) opener.focus();
  };

  const open = image => {
    opener = image;
    expandedImage.src = image.currentSrc || image.src;
    expandedImage.alt = image.alt;
    const figureCaption = image.closest("figure")?.querySelector("figcaption");
    caption.textContent = figureCaption ? figureCaption.textContent.trim() : image.alt;
    lightbox.classList.add("open");
    document.body.style.overflow = "hidden";
    closeButton.focus();
  };

  lightboxImages.forEach(image => {
    image.dataset.lightbox = "true";
    image.tabIndex = 0;
    image.setAttribute("role", "button");
    image.setAttribute("aria-label", `Open larger image: ${image.alt || "map"}`);
    image.addEventListener("click", () => open(image));
    image.addEventListener("keydown", event => {
      if (event.key === "Enter" || event.key === " ") {
        event.preventDefault();
        open(image);
      }
    });
  });

  closeButton.addEventListener("click", close);
  lightbox.addEventListener("click", event => {
    if (event.target === lightbox) close();
  });
  document.addEventListener("keydown", event => {
    if (event.key === "Escape" && lightbox.classList.contains("open")) close();
  });
})();
