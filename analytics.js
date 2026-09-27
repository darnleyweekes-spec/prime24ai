"use strict";

(function () {
  const STORAGE_KEY = "prime24ai_attribution_v1";
  const UTM_KEYS = ["utm_source", "utm_medium", "utm_campaign", "utm_content", "utm_term", "gclid"];

  function safeText(value, limit = 120) {
    return String(value || "").replace(/\s+/g, " ").trim().slice(0, limit);
  }

  function currentAttribution() {
    const params = new URLSearchParams(window.location.search);
    const current = {};
    let hasCampaignData = false;

    UTM_KEYS.forEach((key) => {
      const value = safeText(params.get(key), 160);
      if (value) {
        current[key] = value;
        hasCampaignData = true;
      }
    });

    if (hasCampaignData) {
      current.landing_path = window.location.pathname;
      current.first_seen_at = new Date().toISOString();
      try {
        sessionStorage.setItem(STORAGE_KEY, JSON.stringify(current));
      } catch (_) {}
      return current;
    }

    try {
      return JSON.parse(sessionStorage.getItem(STORAGE_KEY) || "{}") || {};
    } catch (_) {
      return {};
    }
  }

  const attribution = currentAttribution();

  function eventParams(extra) {
    return Object.assign(
      {
        page_path: window.location.pathname,
        page_title: document.title,
        traffic_source: attribution.utm_source || "",
        traffic_medium: attribution.utm_medium || "",
        traffic_campaign: attribution.utm_campaign || "",
        traffic_content: attribution.utm_content || "",
        traffic_term: attribution.utm_term || "",
        landing_path: attribution.landing_path || ""
      },
      extra || {}
    );
  }

  function send(name, extra) {
    if (typeof window.gtag !== "function") return;
    window.gtag("event", name, eventParams(extra));
  }

  window.Prime24Analytics = { send, attribution: Object.assign({}, attribution) };

  function classifyLink(link) {
    const href = link.getAttribute("href") || "";
    const text = safeText(link.textContent, 100).toLowerCase();
    const label = safeText(link.dataset.contactLabel || link.getAttribute("aria-label") || link.textContent, 100);

    if (href.includes("#service-pilot") || text.includes("pilot")) {
      return ["click_service_pilot", { link_text: label, link_url: href }];
    }
    if (/buy\.stripe\.com|book\.stripe\.com|stripe\.com/i.test(href)) {
      return ["click_stripe", { link_text: label, link_url: href }];
    }
    if (/paypal\.com/i.test(href)) {
      return ["click_paypal", { link_text: label, link_url: href }];
    }
    if (href.startsWith("mailto:") || /mail\.google\.com\/mail/i.test(href)) {
      return ["click_email", { link_text: label, link_url: href.split("?")[0] }];
    }
    if (link.dataset.contactSubject || href === "#contact") {
      return ["click_contact", { link_text: label, contact_subject: safeText(link.dataset.contactSubject, 160) }];
    }
    if (/\/proposals\//.test(href)) {
      return ["proposal_cta_click", { link_text: label, link_url: href }];
    }
    return null;
  }

  document.addEventListener("click", (event) => {
    const link = event.target.closest && event.target.closest("a");
    if (link) {
      const classified = classifyLink(link);
      if (classified) send(classified[0], classified[1]);
    }

    const button = event.target.closest && event.target.closest("button");
    if (!button) return;
    const id = button.id || "";
    if (id === "runMission") send("alpha_demo_run", { button_id: id });
    if (id === "runSlop") send("work_slop_check_run", { button_id: id });
  });

  const startedForms = new WeakSet();
  document.addEventListener("focusin", (event) => {
    const form = event.target.closest && event.target.closest("form");
    if (!form || startedForms.has(form)) return;
    startedForms.add(form);
    const formId = form.id || "unnamed";
    if (formId === "intake") send("intake_started", { form_id: formId });
    else send("form_started", { form_id: formId });
  });

  document.addEventListener("submit", (event) => {
    const form = event.target;
    if (!(form instanceof HTMLFormElement)) return;
    const formId = form.id || "unnamed";
    if (formId === "intake") send("intake_completed", { form_id: formId });
    else send("form_submit", { form_id: formId });
  });

  document.querySelectorAll("video").forEach((video, index) => {
    let played = false;
    video.addEventListener("play", () => {
      if (played) return;
      played = true;
      send("video_play", {
        video_index: index + 1,
        video_src: safeText(video.currentSrc || video.querySelector("source")?.src || "", 200)
      });
    });
    video.addEventListener("ended", () => {
      send("video_complete", {
        video_index: index + 1,
        video_src: safeText(video.currentSrc || video.querySelector("source")?.src || "", 200)
      });
    });
  });

  const path = window.location.pathname;
  if (/^\/proposals\/(prime24ai|agents|learn|pitchme|paws-and-power)\/?$/.test(path)) {
    send("proposal_view", { proposal_name: path.split("/").filter(Boolean).pop() });
  } else if (/^\/proposals\/?$/.test(path)) {
    send("proposal_hub_view");
  }
})();
