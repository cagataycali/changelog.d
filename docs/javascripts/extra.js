/* changelog.d · small, dependency-free behaviours. */
(function () {
  const reduced = window.matchMedia("(prefers-reduced-motion: reduce)").matches;

  function slugify(text) {
    const words = (text.toLowerCase().match(/[a-z0-9]+/g) || []);
    let slug = "";
    for (const w of words) {
      const next = slug ? slug + "-" + w : w;
      if (next.length > 60) break;
      slug = next;
    }
    return slug || "change";
  }

  /* --- the typed terminal on the home page --- */
  function terminal(el) {
    const script = [
      ["cmd", 'changelog-d new 42 Fixed "the arm stops in 10 ms, not 400"'],
      ["out", "changelog.d/42-the-arm-stops-in-10-ms-not-400.md"],
      ["cmd", "changelog-d check"],
      ["ok", "changelog fragments OK (3 pending)"],
      ["cmd", "git push   # no rebase. no conflict. no re-review."],
    ];
    const out = el.querySelector(".cd-term__out");
    if (reduced) {
      out.innerHTML = script.map(([k, t]) => (k === "cmd" ? '<span class="p">$</span> ' + t : '<span class="' + (k === "ok" ? "ok" : "dim") + '">' + t + "</span>")).join("\n");
      return;
    }
    let line = 0, ch = 0, html = "";
    const caret = '<span class="cd-caret"></span>';
    function tick() {
      if (line >= script.length) {
        out.innerHTML = html + caret;
        setTimeout(() => { line = 0; ch = 0; html = ""; tick(); }, 4200);
        return;
      }
      const [kind, text] = script[line];
      if (kind !== "cmd") {
        html += '<span class="' + (kind === "ok" ? "ok" : "dim") + '">' + text + "</span>\n";
        line++;
        out.innerHTML = html + caret;
        return setTimeout(tick, 420);
      }
      ch++;
      out.innerHTML = html + '<span class="p">$</span> ' + text.slice(0, ch) + caret;
      if (ch >= text.length) {
        html += '<span class="p">$</span> ' + text + "\n";
        line++; ch = 0;
        return setTimeout(tick, 380);
      }
      setTimeout(tick, 26 + Math.random() * 40);
    }
    tick();
  }

  /* --- fragment maker: type a change, get the file --- */
  function maker(el) {
    const num = el.querySelector("[name=number]");
    const cat = el.querySelector("[name=category]");
    const sum = el.querySelector("[name=summary]");
    const file = el.querySelector(".cd-maker__file");
    const code = el.querySelector("code");
    function render() {
      const n = parseInt(num.value, 10);
      const s = sum.value.trim() || "what a user would notice";
      const placeholder = !n || n === 0 || /^9{3,}$/.test(String(n));
      const name = "changelog.d/" + (num.value || "<pr>") + "-" + slugify(s) + ".md";
      file.innerHTML = placeholder
        ? '<span class="bad">✗ ' + name + " · use the real PR number, placeholders are refused</span>"
        : "✓ <b>" + name + "</b>";
      code.textContent = "### " + cat.value + ": " + s + "\n\nOne short paragraph: what changed, and why a user would care.\n";
    }
    [num, cat, sum].forEach((i) => i.addEventListener("input", render));
    render();
  }

  /* --- the signature draws itself once the footer is in view --- */
  function observe(selector, cls, opts) {
    const els = document.querySelectorAll(selector);
    if (!("IntersectionObserver" in window) || reduced) {
      els.forEach((e) => e.classList.add(cls));
      return;
    }
    const io = new IntersectionObserver((entries) => {
      entries.forEach((en) => {
        if (en.isIntersecting) { en.target.classList.add(cls); io.unobserve(en.target); }
      });
    }, opts || { threshold: 0.25 });
    els.forEach((e) => io.observe(e));
  }

  function init() {
    document.querySelectorAll(".cd-term").forEach(terminal);
    document.querySelectorAll(".cd-maker").forEach(maker);
    observe(".cd-sign", "is-signed", { threshold: 0.6 });
    observe(".cd-reveal", "is-in", { threshold: 0.15 });
  }

  if (window.document$ && typeof window.document$.subscribe === "function") {
    window.document$.subscribe(init);
  } else if (document.readyState === "loading") {
    document.addEventListener("DOMContentLoaded", init);
  } else {
    init();
  }
})();
