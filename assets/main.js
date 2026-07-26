(() => {
  const menuButton = document.querySelector(".menu-toggle");
  const nav = document.querySelector(".site-nav");

  if (menuButton && nav) {
    menuButton.addEventListener("click", () => {
      const open = menuButton.getAttribute("aria-expanded") === "true";
      menuButton.setAttribute("aria-expanded", String(!open));
      nav.classList.toggle("is-open", !open);
    });
  }

  const search = document.querySelector("#system-search");
  const cards = [...document.querySelectorAll(".system-card")];
  const filters = [...document.querySelectorAll(".filter-chip")];
  const empty = document.querySelector("#empty-state");
  let activeFilter = "all";

  const applyFilters = () => {
    const query = (search?.value || "").trim().toLowerCase();
    let visible = 0;

    cards.forEach((card) => {
      const categories = card.dataset.category || "";
      const haystack = `${card.dataset.search || ""} ${card.textContent || ""}`.toLowerCase();
      const categoryMatch = activeFilter === "all" || categories.split(" ").includes(activeFilter);
      const searchMatch = !query || haystack.includes(query);
      const show = categoryMatch && searchMatch;
      card.hidden = !show;
      if (show) visible += 1;
    });

    if (empty) empty.hidden = visible !== 0;
  };

  search?.addEventListener("input", applyFilters);
  filters.forEach((filter) => {
    filter.addEventListener("click", () => {
      activeFilter = filter.dataset.filter || "all";
      filters.forEach((item) => item.classList.toggle("is-active", item === filter));
      applyFilters();
    });
  });

  const article = document.querySelector("#article");
  const toc = document.querySelector("#table-of-contents");

  if (article && toc) {
    const headings = [...article.querySelectorAll("h2, h3")];
    const used = new Set();

    headings.forEach((heading) => {
      const base = (heading.textContent || "section")
        .toLowerCase()
        .replace(/[^a-z0-9]+/g, "-")
        .replace(/^-|-$/g, "");
      let id = base;
      let suffix = 2;
      while (used.has(id)) id = `${base}-${suffix++}`;
      used.add(id);
      heading.id = id;

      const link = document.createElement("a");
      link.href = `#${id}`;
      link.textContent = (heading.textContent || "").replace(/^\d+\.\s*/, "");
      if (heading.tagName === "H3") link.className = "toc-sub";
      toc.appendChild(link);
    });

    const tocLinks = [...toc.querySelectorAll("a")];
    if ("IntersectionObserver" in window) {
      const observer = new IntersectionObserver(
        (entries) => {
          entries.forEach((entry) => {
            if (!entry.isIntersecting) return;
            tocLinks.forEach((link) => {
              link.classList.toggle("is-active", link.getAttribute("href") === `#${entry.target.id}`);
            });
          });
        },
        { rootMargin: "-18% 0px -72% 0px" }
      );
      headings.forEach((heading) => observer.observe(heading));
    }
  }

  const progress = document.querySelector(".reading-progress span");
  if (progress) {
    const updateProgress = () => {
      const max = document.documentElement.scrollHeight - window.innerHeight;
      const value = max > 0 ? Math.min(1, window.scrollY / max) : 0;
      progress.style.transform = `scaleX(${value})`;
    };
    updateProgress();
    window.addEventListener("scroll", updateProgress, { passive: true });
  }
})();
