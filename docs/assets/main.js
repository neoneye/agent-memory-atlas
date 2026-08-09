(() => {
  // ---------------------------------------------------------------- consent
  // The head sets every Consent Mode signal to denied before gtag configures,
  // so no analytics cookie exists until someone chooses here. Declining is a
  // stored choice, not an absence of one, so the banner does not reappear.
  const CONSENT_KEY = "ama-consent";
  const readConsent = () => {
    try {
      return localStorage.getItem(CONSENT_KEY);
    } catch {
      return null; // private mode, or storage disabled — treat as undecided
    }
  };
  const writeConsent = (value) => {
    try {
      localStorage.setItem(CONSENT_KEY, value);
    } catch {
      /* a reader who blocks storage has already expressed a preference */
    }
  };

  const applyConsent = (granted) => {
    if (typeof window.gtag !== "function") return;
    window.gtag("consent", "update", {
      analytics_storage: granted ? "granted" : "denied",
    });
  };

  let banner = null;

  const closeBanner = () => {
    banner?.remove();
    banner = null;
  };

  const showBanner = () => {
    if (banner) return;
    banner = document.createElement("div");
    banner.className = "consent-banner";
    banner.setAttribute("role", "region");
    banner.setAttribute("aria-label", "Analytics cookie choice");
    banner.innerHTML = `
      <p>This site uses Google Analytics to count visits. Nothing is collected
      until you choose, and declining is remembered.</p>
      <div class="consent-actions">
        <button type="button" data-consent="declined">Decline</button>
        <button type="button" data-consent="granted">Allow</button>
      </div>`;
    banner.addEventListener("click", (event) => {
      const choice = event.target.closest("[data-consent]")?.dataset.consent;
      if (!choice) return;
      writeConsent(choice);
      applyConsent(choice === "granted");
      closeBanner();
    });
    document.body.appendChild(banner);
    // Focus the banner itself, not a choice. Focusing "Allow" put a keyboard
    // reader one Enter away from consenting to analytics without reading the
    // question, which is the same thumb on the scale as styling it primary.
    banner.setAttribute("tabindex", "-1");
    banner.focus();
  };

  const stored = readConsent();
  if (stored) applyConsent(stored === "granted");
  else showBanner();

  document.querySelectorAll("[data-consent-reopen]").forEach((control) => {
    control.addEventListener("click", () => {
      closeBanner();
      showBanner();
    });
  });

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
  const filters = [...document.querySelectorAll(".filter-chip[data-filter]")];
  const capFilters = [...document.querySelectorAll(".filter-chip[data-capability]")];
  const empty = document.querySelector("#empty-state");
  const count = document.querySelector("#result-count");
  let activeFilter = "all";
  // Capabilities combine with AND: "show me the systems that have a tombstone
  // *and* enforce scope" is the question worth asking, and it is the one a
  // per-column OR filter cannot answer.
  const activeCaps = new Set();

  const applyFilters = () => {
    const query = (search?.value || "").trim().toLowerCase();
    let visible = 0;

    cards.forEach((card) => {
      const categories = card.dataset.category || "";
      const caps = (card.dataset.capabilities || "").split(" ").filter(Boolean);
      const haystack = `${card.dataset.search || ""} ${card.textContent || ""}`.toLowerCase();
      const categoryMatch = activeFilter === "all" || categories.split(" ").includes(activeFilter);
      const searchMatch = !query || haystack.includes(query);
      const capMatch = [...activeCaps].every((flag) => caps.includes(flag));
      const show = categoryMatch && searchMatch && capMatch;
      card.hidden = !show;
      if (show) visible += 1;
    });

    // Nothing matched an AND of capabilities. Rather than report a dead end,
    // fall back to the nearest partial matches: the systems carrying the most
    // of what was asked for. An engineer filtering for four mechanisms wants to
    // know which system gets closest, not to be told the combination is rare.
    let fallback = 0;
    if (visible === 0 && activeCaps.size > 1) {
      const eligible = cards.filter((card) => {
        const categories = card.dataset.category || "";
        const haystack = `${card.dataset.search || ""} ${card.textContent || ""}`.toLowerCase();
        return (activeFilter === "all" || categories.split(" ").includes(activeFilter))
          && (!query || haystack.includes(query));
      });
      const overlap = (card) => {
        const caps = (card.dataset.capabilities || "").split(" ").filter(Boolean);
        return [...activeCaps].filter((flag) => caps.includes(flag)).length;
      };
      const best = eligible.reduce((max, card) => Math.max(max, overlap(card)), 0);
      if (best > 0) {
        eligible.forEach((card) => {
          if (overlap(card) === best) {
            card.hidden = false;
            fallback += 1;
          }
        });
        if (empty) {
          empty.hidden = false;
          empty.textContent =
            `No system carries all ${activeCaps.size}. Showing the ${fallback} that ` +
            `carr${fallback === 1 ? "ies" : "y"} ${best} of ${activeCaps.size}.`;
        }
      } else if (empty) {
        empty.hidden = false;
        empty.textContent = "No system carries any of these together with the other filters.";
      }
    } else if (empty) {
      empty.hidden = visible !== 0;
      empty.textContent = "Nothing matches those filters.";
    }

    if (count) {
      const filtered = activeCaps.size > 0 || activeFilter !== "all" || query;
      count.textContent = filtered
        ? (fallback > 0
            ? `0 exact, ${fallback} closest of ${cards.length} systems`
            : `${visible} of ${cards.length} systems`)
        : "";
    }
  };

  search?.addEventListener("input", applyFilters);
  filters.forEach((filter) => {
    filter.addEventListener("click", () => {
      activeFilter = filter.dataset.filter || "all";
      // Radio-like — one architecture at a time — so the selection has to be
      // announced as well as coloured. The capability chips below carried
      // aria-pressed from the start and these did not, which left a screen
      // reader unable to tell which architecture filter was selected.
      filters.forEach((item) => {
        const on = item === filter;
        item.classList.toggle("is-active", on);
        item.setAttribute("aria-pressed", String(on));
      });
      applyFilters();
    });
  });
  capFilters.forEach((filter) => {
    filter.addEventListener("click", () => {
      const flag = filter.dataset.capability;
      const on = !activeCaps.has(flag);
      if (on) activeCaps.add(flag);
      else activeCaps.delete(flag);
      filter.classList.toggle("is-active", on);
      filter.setAttribute("aria-pressed", String(on));
      applyFilters();
    });
  });

  // ------------------------------------------------- legacy verdict anchors
  // The 140 per-system verdict anchors lived on /compare/ until 4 August 2026.
  // Fragments never reach the server, so an external deep link to
  // /compare/#mem0 cannot be redirected by the host — it has to be caught here.
  // Deliberately not a hardcoded slug list: any hash that matches nothing on
  // this page is either a moved verdict or already broken, and /verdicts/ is
  // the only place it can now be. check_verdict_anchors.py asserts every slug
  // resolves there.
  if (/\/compare\/?$/.test(location.pathname) && location.hash.length > 1) {
    const id = decodeURIComponent(location.hash.slice(1));
    if (/^[a-z0-9][a-z0-9-]*$/.test(id) && !document.getElementById(id)) {
      location.replace("../verdicts/" + location.hash);
    }
  }

  // ------------------------------------------------- verdict page search
  const verdictSearch = document.querySelector("#verdict-search");
  if (verdictSearch) {
    const entries = [...document.querySelectorAll(".prose h3")].map((h) => {
      const block = [h];
      let el = h.nextElementSibling;
      while (el && el.tagName !== "H3" && el.tagName !== "H2") {
        block.push(el);
        el = el.nextElementSibling;
      }
      return { name: h.textContent.toLowerCase(), block };
    });
    const vCount = document.querySelector("#verdict-count");
    const tocLinks = [...document.querySelectorAll(".toc a")];
    const applyVerdicts = () => {
      const q = verdictSearch.value.trim().toLowerCase();
      let visible = 0;
      entries.forEach(({ name, block }) => {
        const show = !q || name.includes(q);
        block.forEach((el) => { el.hidden = !show; });
        if (show) visible += 1;
      });
      tocLinks.forEach((a) => {
        a.hidden = Boolean(q) && !a.textContent.toLowerCase().includes(q);
      });
      if (vCount) {
        vCount.textContent = q
          ? `${visible} of ${entries.length} systems match "${verdictSearch.value.trim()}"`
          : `${entries.length} systems`;
      }
    };
    verdictSearch.addEventListener("input", applyVerdicts);
    applyVerdicts();
  }

  // ------------------------------------------------- comparative matrix search
  // The matrix is twelve columns of prose and cannot be sorted into an answer,
  // so the one control it needs is "show me this system". Name-only on purpose:
  // filtering on the other eleven columns would imply they hold values rather
  // than sentences, which they do not. See the compare-page note.
  const matrixSearch = document.querySelector("#matrix-search");
  if (matrixSearch) {
    const table = [...document.querySelectorAll(".prose table")].find(
      (el) => el.querySelector("th")?.textContent.trim().toLowerCase() === "repo",
    );
    const matrixCount = document.querySelector("#matrix-count");
    if (table) {
      const rows = [...table.querySelectorAll("tbody tr")];
      const applyMatrix = () => {
        const q = matrixSearch.value.trim().toLowerCase();
        let visible = 0;
        rows.forEach((row) => {
          const name = row.querySelector("td")?.textContent.toLowerCase() || "";
          const show = !q || name.includes(q);
          row.hidden = !show;
          if (show) visible += 1;
        });
        if (matrixCount) {
          matrixCount.textContent = q
            ? `${visible} of ${rows.length} systems match "${matrixSearch.value.trim()}"`
            : `${rows.length} systems`;
        }
      };
      matrixSearch.addEventListener("input", applyMatrix);
      applyMatrix();
    }
  }

  // ------------------------------------------------- capability grid page
  const grid = document.querySelector(".capability-grid");
  const gridFilters = [...document.querySelectorAll("#capability-filters [data-capability]")];
  if (grid && gridFilters.length) {
    const rows = [...grid.querySelectorAll("tbody tr")];
    const gridCount = document.querySelector("#capability-count");
    const active = new Set();

    const applyGrid = () => {
      let visible = 0;
      rows.forEach((row) => {
        const caps = (row.dataset.capabilities || "").split(" ").filter(Boolean);
        const show = [...active].every((flag) => caps.includes(flag));
        row.hidden = !show;
        if (show) visible += 1;
      });
      if (gridCount) {
        gridCount.textContent = active.size
          ? `${visible} of ${rows.length} systems have ${[...active].length === 1 ? "this" : "all of these"}`
          : `${rows.length} systems`;
      }
    };

    gridFilters.forEach((filter) => {
      filter.addEventListener("click", () => {
        const flag = filter.dataset.capability;
        const on = !active.has(flag);
        if (on) active.add(flag);
        else active.delete(flag);
        filter.classList.toggle("is-active", on);
        filter.setAttribute("aria-pressed", String(on));
        applyGrid();
      });
    });

    applyGrid();
  }

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

  const tableWraps = [...document.querySelectorAll(".prose .table-wrap")];

  if (tableWraps.length) {
    const siteHeader = document.querySelector(".site-header");
    const stickyTables = tableWraps
      .map((wrap) => {
        const table = wrap.querySelector(":scope > table");
        const sourceHead = table?.tHead;
        if (!table || !sourceHead) return null;

        const holder = document.createElement("div");
        holder.className = "sticky-table-head";
        holder.setAttribute("aria-hidden", "true");

        const clone = document.createElement("table");
        const columns = document.createElement("colgroup");
        clone.append(columns, sourceHead.cloneNode(true));
        holder.appendChild(clone);
        document.body.appendChild(holder);

        return { wrap, table, sourceHead, holder, clone, columns };
      })
      .filter(Boolean);

    let updateFrame = 0;

    const syncStickyTables = () => {
      updateFrame = 0;
      const stickyTop = siteHeader?.getBoundingClientRect().bottom || 0;

      stickyTables.forEach(({ wrap, table, sourceHead, holder, clone, columns }) => {
        const wrapRect = wrap.getBoundingClientRect();
        const headerHeight = sourceHead.getBoundingClientRect().height;
        const active = wrapRect.top < stickyTop && wrapRect.bottom > stickyTop + headerHeight;

        holder.classList.toggle("is-visible", active);
        if (!active) return;

        const sourceCells = [...sourceHead.rows[0].cells];
        while (columns.children.length < sourceCells.length) {
          columns.appendChild(document.createElement("col"));
        }
        while (columns.children.length > sourceCells.length) {
          columns.lastElementChild.remove();
        }
        sourceCells.forEach((cell, index) => {
          columns.children[index].style.width = `${cell.getBoundingClientRect().width}px`;
        });

        holder.style.top = `${stickyTop}px`;
        holder.style.left = `${wrapRect.left}px`;
        holder.style.width = `${wrapRect.width}px`;
        clone.style.width = `${table.scrollWidth}px`;
        clone.style.transform = `translateX(${-wrap.scrollLeft}px)`;
      });
    };

    const requestStickyTableSync = () => {
      if (updateFrame) return;
      updateFrame = window.requestAnimationFrame(syncStickyTables);
    };

    window.addEventListener("scroll", requestStickyTableSync, { passive: true });
    window.addEventListener("resize", requestStickyTableSync);
    tableWraps.forEach((wrap) => {
      wrap.addEventListener("scroll", requestStickyTableSync, { passive: true });
    });

    if ("ResizeObserver" in window) {
      const resizeObserver = new ResizeObserver(requestStickyTableSync);
      stickyTables.forEach(({ wrap, table }) => {
        resizeObserver.observe(wrap);
        resizeObserver.observe(table);
      });
    }

    document.fonts?.ready.then(requestStickyTableSync);
    syncStickyTables();

    // Wide tables (the comparative matrix is 12 columns) are squeezed into the
    // ~820px prose column while the viewport is often far wider. Offer a toggle
    // that breaks the table out to the full viewport. The prose column is a grid
    // cell rather than a centred block, so the usual `margin-left: calc(50% -
    // 50vw)` full-bleed trick would mis-centre it — measure the host instead.
    const EXPAND_GUTTER = 24;
    const EXPAND_MIN_GAIN = 120;

    tableWraps.forEach((wrap) => {
      const host = wrap.parentElement;
      if (!host) return;

      const tools = document.createElement("div");
      tools.className = "table-tools";

      const button = document.createElement("button");
      button.type = "button";
      button.className = "table-expand";
      button.setAttribute("aria-expanded", "false");
      button.textContent = "Expand to full width";
      tools.appendChild(button);
      host.insertBefore(tools, wrap);

      const sizeToViewport = () => {
        if (!wrap.classList.contains("is-expanded")) return;
        const viewport = document.documentElement.clientWidth;
        wrap.style.marginLeft = `${EXPAND_GUTTER - host.getBoundingClientRect().left}px`;
        wrap.style.width = `${viewport - EXPAND_GUTTER * 2}px`;
      };

      const collapse = () => {
        wrap.classList.remove("is-expanded");
        wrap.style.marginLeft = "";
        wrap.style.width = "";
        button.setAttribute("aria-expanded", "false");
        button.textContent = "Expand to full width";
      };

      const expand = () => {
        wrap.classList.add("is-expanded");
        sizeToViewport();
        button.setAttribute("aria-expanded", "true");
        button.textContent = "Collapse to column";
      };

      const toggle = () => {
        // Widening the columns makes cells wrap less, so the table gets shorter.
        // Hold the table's position under the cursor instead of letting the page
        // jump.
        const before = wrap.getBoundingClientRect().top;
        wrap.classList.contains("is-expanded") ? collapse() : expand();
        const after = wrap.getBoundingClientRect().top;
        window.scrollBy(0, after - before);
        requestStickyTableSync();
      };

      const evaluate = () => {
        const viewport = document.documentElement.clientWidth;
        const gain = viewport - host.getBoundingClientRect().width - EXPAND_GUTTER * 2;
        const worthwhile = gain > EXPAND_MIN_GAIN;
        tools.classList.toggle("is-available", worthwhile);
        if (!worthwhile && wrap.classList.contains("is-expanded")) collapse();
        sizeToViewport();
        requestStickyTableSync();
      };

      button.addEventListener("click", toggle);
      window.addEventListener("resize", evaluate);
      evaluate();
    });
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
