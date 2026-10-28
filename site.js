// Best of West Coast — small progressive enhancements.
// The pages are usable with JavaScript off. Cluster lists are real HTML.
// data/places.json is the places catalog; when this file can be fetched
// (a local server or GitHub Pages), the catalog status line confirms it.

(function () {
  "use strict";

  document.querySelectorAll("[data-current-year]").forEach(function (el) {
    el.textContent = String(new Date().getFullYear());
  });

  var menus = document.querySelectorAll(".mobile-menu");

  function closeMenus() {
    menus.forEach(function (menu) {
      menu.open = false;
      menu.removeAttribute("open");
    });
  }

  menus.forEach(function (menu) {
    menu.addEventListener("click", function (event) {
      if (event.target.closest("a")) closeMenus();
    });
  });

  document.addEventListener("click", function (event) {
    if (!event.target.closest(".mobile-menu")) closeMenus();
  });

  document.addEventListener("keydown", function (event) {
    if (event.key === "Escape") closeMenus();
  });

  window.addEventListener("hashchange", closeMenus);
  window.addEventListener("pageshow", closeMenus);

  document.querySelectorAll("[data-newsletter]").forEach(function (form) {
    var status = form.querySelector("[data-newsletter-status]");
    form.addEventListener("submit", function (event) {
      event.preventDefault();
      var email = form.querySelector('input[type="email"]');
      if (!email || !email.checkValidity()) {
        if (email) email.reportValidity();
        return;
      }
      if (status) {
        status.textContent = "Nothing was sent. The first issue isn’t out yet.";
      }
    });
  });

  var discover = document.querySelector("[data-discover]");
  if (discover) {
    var cards = Array.prototype.slice.call(document.querySelectorAll("[data-place]"));
    var countEl = document.querySelector("[data-result-count]");
    var emptyEl = document.querySelector("[data-empty]");
    var query = discover.querySelector('[name="q"]');
    var state = discover.querySelector('[name="state"]');
    var kind = discover.querySelector('[name="kind"]');

    function applyFilters() {
      var q = (query && query.value ? query.value : "").trim().toLowerCase();
      var stateValue = state ? state.value : "";
      var kindValue = kind ? kind.value : "";
      var visible = 0;

      cards.forEach(function (card) {
        var haystack = (card.getAttribute("data-search") || "").toLowerCase();
        var show = (!q || haystack.indexOf(q) !== -1) &&
          (!stateValue || card.getAttribute("data-state") === stateValue) &&
          (!kindValue || card.getAttribute("data-kind") === kindValue);
        card.hidden = !show;
        if (show) visible += 1;
      });

      if (countEl) {
        countEl.textContent = visible + (visible === 1 ? " place" : " places");
      }
      if (emptyEl) emptyEl.hidden = visible !== 0;
    }

    discover.addEventListener("submit", function (event) {
      event.preventDefault();
      applyFilters();
    });
    discover.addEventListener("input", applyFilters);
    discover.addEventListener("change", applyFilters);
    discover.addEventListener("reset", function () {
      window.setTimeout(applyFilters, 0);
    });
  }

  var statusSlot = document.querySelector("[data-catalog-status]");
  if (statusSlot) {
    var script = document.querySelector('script[src*="site.js"]');
    var root = script ? script.src.replace(/site\.js(?:\?.*)?$/, "") : "";
    fetch(root + "data/places.json")
      .then(function (response) {
        if (!response.ok) throw new Error("status " + response.status);
        return response.json();
      })
      .then(function (data) {
        var places = data && Array.isArray(data.places) ? data.places : [];
        var unpublished = places.filter(function (place) { return !place.verified; }).length;
        var sentence = "Catalog loaded from data/places.json: " + places.length +
          " places, " + unpublished + " without a verified recommendation.";
        var listed = document.querySelectorAll('[data-catalog="all"] [data-place]').length;
        if (listed && listed !== places.length) {
          sentence += " This page lists " + listed + ", so the HTML and the database disagree.";
        }
        statusSlot.textContent = sentence;
      })
      .catch(function () {
        // Opening the file directly cannot fetch JSON. The HTML catalog remains.
      });
  }
})();
