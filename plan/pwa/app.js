(() => {
  "use strict";

  const app = document.querySelector("#app");
  const bottomNav = document.querySelector("#bottomNav");
  const imageViewer = document.querySelector("#imageViewer");
  const viewerImage = document.querySelector("#viewerImage");
  const viewerTitle = document.querySelector("#viewerTitle");
  let deferredInstallPrompt = null;
  let renderTimer = null;

  const escapeHtml = (value = "") => String(value)
    .replaceAll("&", "&amp;")
    .replaceAll("<", "&lt;")
    .replaceAll(">", "&gt;")
    .replaceAll('"', "&quot;")
    .replaceAll("'", "&#039;");

  const richText = (value = "") => escapeHtml(value)
    .replace(/\*\*(.+?)\*\*/g, "<strong>$1</strong>");

  const safeId = (value) => /^[a-z0-9][a-z0-9-]*$/.test(value);
  const validTime = (value) => /^([01]\d|2[0-3]):[0-5]\d$/.test(value);

  function validateDay(day) {
    const errors = [];
    const requiredStrings = ["id", "date", "timeZone", "utcOffset", "title", "subtitle"];

    if (!day || typeof day !== "object") return ["Day data must be an object."];
    requiredStrings.forEach((key) => {
      if (typeof day[key] !== "string" || !day[key].trim()) errors.push(`${key} is required.`);
    });

    if (!/^\d{4}-\d{2}-\d{2}$/.test(day.date || "")) errors.push("date must use YYYY-MM-DD.");
    if (!/^[+-]\d{2}:\d{2}$/.test(day.utcOffset || "")) errors.push("utcOffset must look like +09:00.");
    if (!Array.isArray(day.steps) || day.steps.length === 0) errors.push("At least one step is required.");
    if (!Array.isArray(day.preparation)) errors.push("preparation must be an array.");
    if (!Array.isArray(day.resources)) errors.push("resources must be an array.");

    const ids = new Set();
    (day.steps || []).forEach((step, index) => {
      const prefix = `steps[${index}]`;
      if (!safeId(step.id || "")) errors.push(`${prefix}.id must be a lowercase kebab-case ID.`);
      if (ids.has(step.id)) errors.push(`${prefix}.id is duplicated.`);
      ids.add(step.id);
      ["title", "kind", "summary"].forEach((key) => {
        if (typeof step[key] !== "string" || !step[key].trim()) errors.push(`${prefix}.${key} is required.`);
      });
      if (!validTime(step.start || "") || !validTime(step.end || "")) errors.push(`${prefix} has an invalid time.`);
      if (typeof step.hardDeadline !== "boolean") errors.push(`${prefix}.hardDeadline must be true or false.`);
      if (!Array.isArray(step.blocks) || !Array.isArray(step.actions)) errors.push(`${prefix} needs blocks and actions arrays.`);
    });

    (day.preparation || []).forEach((item, index) => {
      if (!safeId(item.id || "") || typeof item.text !== "string") {
        errors.push(`preparation[${index}] needs a valid id and text.`);
      }
    });

    return errors;
  }

  function dateAt(day, time, addDay = false) {
    const date = new Date(`${day.date}T${time}:00${day.utcOffset}`);
    if (addDay) date.setTime(date.getTime() + 86400000);
    return date;
  }

  function hydrateSteps(day) {
    return day.steps.map((step) => {
      const start = dateAt(day, step.start);
      let end = dateAt(day, step.end);
      if (end <= start) end = dateAt(day, step.end, true);
      return { ...step, startDate: start, endDate: end };
    });
  }

  function renderBlock(block) {
    if (block.type === "paragraph") return `<p>${richText(block.text)}</p>`;
    if (block.type === "warning") return `<p class="warning">${richText(block.text)}</p>`;
    if (block.type === "list") {
      const tag = block.ordered ? "ol" : "ul";
      const items = (block.items || []).map((item) => `<li>${richText(item)}</li>`).join("");
      return `<${tag}>${items}</${tag}>`;
    }
    return "";
  }

  function renderAction(action) {
    const classes = `action${action.primary ? " primary" : ""}`;
    if (action.type === "image") {
      return `<button class="${classes} image-link" type="button" data-image="${escapeHtml(action.src)}" data-label="${escapeHtml(action.imageLabel || action.label)}">${escapeHtml(action.label)}</button>`;
    }
    return `<a class="${classes}" href="${escapeHtml(action.url)}" target="_blank" rel="noopener">${escapeHtml(action.label)} ↗</a>`;
  }

  function renderStep(step) {
    const blocks = step.blocks.map(renderBlock).join("");
    const actions = step.actions.length
      ? `<div class="actions">${step.actions.map(renderAction).join("")}</div>`
      : "";

    return `
      <details class="step" id="${escapeHtml(step.id)}">
        <summary>
          <span class="time">${escapeHtml(step.start)}<br>${escapeHtml(step.end)}</span>
          <span>
            <span class="step-title">${escapeHtml(step.title)}</span>
            <span class="kind">${escapeHtml(step.kind)}</span>
          </span>
        </summary>
        <div class="step-body">${blocks}${actions}</div>
      </details>`;
  }

  function renderPreparation(day) {
    return day.preparation.map((item) => {
      const link = item.link
        ? ` <a href="${escapeHtml(item.link.url)}" target="_blank" rel="noopener">${escapeHtml(item.link.label)}</a>`
        : "";
      return `<label class="check-row"><input data-check="${escapeHtml(item.id)}" type="checkbox"><span>${richText(item.text)}${link}</span></label>`;
    }).join("");
  }

  function renderResource(resource) {
    if (resource.type === "image") {
      return `<button class="resource image-link" type="button" data-image="${escapeHtml(resource.src)}" data-label="${escapeHtml(resource.imageLabel || resource.label)}">${escapeHtml(resource.label)}<small>${escapeHtml(resource.description)}</small></button>`;
    }
    return `<a class="resource" href="${escapeHtml(resource.url)}" target="_blank" rel="noopener">${escapeHtml(resource.label)}<small>${escapeHtml(resource.description)} ↗</small></a>`;
  }

  function renderShell(day) {
    document.title = `${day.title} · ${day.subtitle.split(" · ")[0]}`;
    app.innerHTML = `
      <header class="page-header" id="top">
        <p class="eyebrow">${escapeHtml(day.eyebrow || "Japan · Day plan")}</p>
        <h1>${escapeHtml(day.title)}</h1>
        <p class="date">${escapeHtml(day.subtitle)}</p>
        <button class="install-button" id="installButton" type="button" hidden>Install</button>
      </header>

      <article class="now-card" aria-live="polite">
        <div class="now-top">
          <span class="status-label"><span class="status-dot"></span><span id="statusLabel">UP NEXT</span></span>
          <time id="clock">Japan time</time>
        </div>
        <h2 id="nowTitle"></h2>
        <p id="nowTime"></p>
        <p id="nowSummary"></p>
        <div id="countdown" class="countdown"></div><br>
        <a id="nowButton" class="now-button" href="#timeline-section">View timeline ↓</a>
      </article>

      <details class="preview">
        <summary>Preview the itinerary at another time</summary>
        <div class="preview-controls">
          <select id="previewTime" aria-label="Preview itinerary time">
            <option value="">Live Japan time</option>
            ${day.previewTimes.map((item) => `<option value="${escapeHtml(item.time)}">${escapeHtml(item.time)} · ${escapeHtml(item.label)}</option>`).join("")}
          </select>
          <button id="liveButton" class="small-button" type="button">Live</button>
        </div>
      </details>

      <section id="prepare">
        <div class="section-heading">
          <h2>Before leaving</h2>
          <span class="section-note">Saved on this device</span>
        </div>
        <div class="prep-list">${renderPreparation(day)}</div>
      </section>

      <section id="timeline-section">
        <div class="section-heading">
          <h2>Timeline</h2>
          <span class="section-note">Tap a step for details</span>
        </div>
        <div class="timeline" id="timeline">${day.steps.map(renderStep).join("")}</div>
      </section>

      <section id="resources">
        <div class="section-heading"><h2>Quick references</h2></div>
        <div class="resource-grid">${day.resources.map(renderResource).join("")}</div>
      </section>

      <p class="footer-note">${escapeHtml(day.footer || "")}</p>`;

    app.setAttribute("aria-busy", "false");
    bottomNav.hidden = false;
  }

  function durationText(milliseconds) {
    const totalMinutes = Math.max(0, Math.ceil(milliseconds / 60000));
    const days = Math.floor(totalMinutes / 1440);
    const hours = Math.floor((totalMinutes % 1440) / 60);
    const minutes = totalMinutes % 60;
    if (days) return `${days}d ${hours}h`;
    if (hours) return `${hours}h ${minutes}m`;
    return `${minutes} min`;
  }

  function bindTimeline(day, steps) {
    const previewTime = document.querySelector("#previewTime");
    const clock = document.querySelector("#clock");
    const statusLabel = document.querySelector("#statusLabel");
    const nowTitle = document.querySelector("#nowTitle");
    const nowTime = document.querySelector("#nowTime");
    const nowSummary = document.querySelector("#nowSummary");
    const countdown = document.querySelector("#countdown");
    const nowButton = document.querySelector("#nowButton");
    const formatter = new Intl.DateTimeFormat("en-GB", {
      timeZone: day.timeZone,
      hour: "2-digit",
      minute: "2-digit",
      hour12: false
    });

    steps.forEach((step) => {
      step.element = document.querySelector(`#${step.id}`);
    });

    const currentTime = () => previewTime.value ? dateAt(day, previewTime.value) : new Date();

    function renderStatus() {
      const now = currentTime();
      const first = steps[0];
      const last = steps.at(-1);
      const active = steps.find((step) => now >= step.startDate && now < step.endDate);
      const next = steps.find((step) => step.startDate > now);

      clock.textContent = previewTime.value ? `${formatter.format(now)} · preview` : `${formatter.format(now)} JST`;
      steps.forEach((step) => {
        const isCurrent = step === active;
        step.element.classList.toggle("is-current", isCurrent);
        step.element.classList.toggle("is-past", now >= step.endDate);
        if (isCurrent) step.element.open = true;
      });

      if (now < first.startDate) {
        setNowCard("UP NEXT", first, `Starts in ${durationText(first.startDate - now)}`, "View first step ↓");
      } else if (now >= last.endDate) {
        statusLabel.textContent = "COMPLETE";
        nowTitle.textContent = day.completion.title;
        nowTime.textContent = day.completion.time;
        nowSummary.textContent = day.completion.summary;
        countdown.textContent = "All scheduled steps finished";
        nowButton.textContent = "Review timeline ↓";
        nowButton.href = "#timeline-section";
      } else if (active) {
        setNowCard("NOW", active, `${durationText(active.endDate - now)} remaining`, "Open current step ↓");
      } else if (next) {
        const verb = next.hardDeadline ? "Departs" : "Starts";
        setNowCard("UP NEXT", next, `${verb} in ${durationText(next.startDate - now)}`, "View next step ↓");
      }
    }

    function setNowCard(status, step, timing, buttonText) {
      statusLabel.textContent = status;
      nowTitle.textContent = step.title;
      nowTime.textContent = `${step.start}–${step.end}`;
      nowSummary.textContent = step.summary;
      countdown.textContent = timing;
      nowButton.textContent = buttonText;
      nowButton.href = `#${step.id}`;
    }

    previewTime.addEventListener("change", renderStatus);
    document.querySelector("#liveButton").addEventListener("click", () => {
      previewTime.value = "";
      renderStatus();
    });

    renderStatus();
    renderTimer = window.setInterval(renderStatus, 30000);
  }

  function bindChecklist(day) {
    document.querySelectorAll("[data-check]").forEach((checkbox) => {
      const key = `japan-plan:${day.id}:${checkbox.dataset.check}`;
      try {
        checkbox.checked = localStorage.getItem(key) === "true";
        checkbox.addEventListener("change", () => localStorage.setItem(key, String(checkbox.checked)));
      } catch (_) {
        // The checklist remains usable for the current session.
      }
    });
  }

  function bindImages() {
    document.querySelectorAll(".image-link").forEach((button) => {
      button.addEventListener("click", () => {
        viewerImage.src = button.dataset.image;
        viewerImage.alt = button.dataset.label;
        viewerTitle.textContent = button.dataset.label;
        imageViewer.showModal();
      });
    });
  }

  function bindInstall() {
    const installButton = document.querySelector("#installButton");
    if (!installButton) return;

    if (deferredInstallPrompt) installButton.hidden = false;
    installButton.addEventListener("click", async () => {
      if (!deferredInstallPrompt) return;
      deferredInstallPrompt.prompt();
      await deferredInstallPrompt.userChoice;
      deferredInstallPrompt = null;
      installButton.hidden = true;
    });
  }

  function showOfflineStatus() {
    document.querySelector(".offline-toast")?.remove();
    if (navigator.onLine) return;
    const toast = document.createElement("div");
    toast.className = "offline-toast";
    toast.textContent = "Offline · saved plan available";
    document.body.append(toast);
  }

  async function cacheDayAssets(day) {
    const urls = new Set();
    urls.add(`days/${day.id}.json`);
    day.steps.flatMap((step) => step.actions).forEach((action) => {
      if (action.type === "image") urls.add(action.src);
    });
    day.resources.forEach((resource) => {
      if (resource.type === "image") urls.add(resource.src);
    });

    if ("caches" in window) {
      const cache = await caches.open("japan-plan-runtime-v1");
      await Promise.allSettled([...urls].map((url) => cache.add(url)));
      return;
    }

    await Promise.allSettled([...urls].map((url) => fetch(url)));
  }

  function showError(error) {
    console.error(error);
    const fragment = document.querySelector("#errorTemplate").content.cloneNode(true);
    fragment.querySelector("#errorMessage").textContent = error.message || "This itinerary could not be loaded.";
    app.replaceChildren(fragment);
    app.setAttribute("aria-busy", "false");
  }

  async function init() {
    const params = new URLSearchParams(location.search);
    const dayId = params.get("day") || "2026-10-20";
    if (!/^\d{4}-\d{2}-\d{2}$/.test(dayId)) throw new Error("The requested day ID is invalid.");

    const response = await fetch(`days/${dayId}.json`);
    if (!response.ok) throw new Error(`No itinerary was found for ${dayId}.`);
    const day = await response.json();
    const errors = validateDay(day);
    if (errors.length) throw new Error(`Invalid itinerary data: ${errors.join(" ")}`);

    const steps = hydrateSteps(day);
    renderShell(day);
    bindChecklist(day);
    bindTimeline(day, steps);
    bindImages();
    bindInstall();
    showOfflineStatus();
    cacheDayAssets(day);
  }

  window.addEventListener("beforeinstallprompt", (event) => {
    event.preventDefault();
    deferredInstallPrompt = event;
    const button = document.querySelector("#installButton");
    if (button) button.hidden = false;
  });

  window.addEventListener("appinstalled", () => {
    deferredInstallPrompt = null;
    const button = document.querySelector("#installButton");
    if (button) button.hidden = true;
  });

  window.addEventListener("online", showOfflineStatus);
  window.addEventListener("offline", showOfflineStatus);
  window.addEventListener("pagehide", () => window.clearInterval(renderTimer));

  document.querySelector("#closeViewer").addEventListener("click", () => imageViewer.close());
  imageViewer.addEventListener("click", (event) => {
    if (event.target === imageViewer) imageViewer.close();
  });

  if ("serviceWorker" in navigator) {
    window.addEventListener("load", () => navigator.serviceWorker.register("service-worker.js"));
  }

  init().catch(showError);
})();
