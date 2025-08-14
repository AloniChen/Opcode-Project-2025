// signup.js — progressive enhancement for the Delivery Service sign-up page
// Works with the fields/IDs in the current HTML. No frameworks required.

(function () {
  const $ = (sel, root = document) => root.querySelector(sel);
  const $$ = (sel, root = document) => Array.from(root.querySelectorAll(sel));

  const form = $("form.form");
  if (!form) return; // Abort if markup changes

  const nameI = $("#name");
  const emailI = $("#email");
  const phoneI = $("#phone");
  const passI = $("#password");
  const addrStreetI = $("#address_street");
  const addrHouseI = $("#address_house_number");
  const addrCityI = $("#address_city");
  const addrPostalI = $("#address_postal_code");
  const addrCountryI = $("#address_country");
  const submitBtn = $("button[type=submit]");

  // --- Utilities ---
  function sanitizeSpaces(el) {
    el.value = el.value.replace(/\s+/g, " ").trimStart();
  }

  function titleCaseName(v) {
    return v
      .toLowerCase()
      .split(/\s+/)
      .filter(Boolean)
      .map(w => w.charAt(0).toUpperCase() + w.slice(1))
      .join(" ");
  }

  function emailValid(v) {
    // Light RFC5322-ish check (good enough for client-side)
    return /^[^\s@]+@[^\s@]+\.[^\s@]{2,}$/.test(v);
  }

  function phoneDigits(v) { return v.replace(/\D+/g, ""); }

  function formatIntlPhone(v) {
    // Minimal, non-intrusive formatting: keep + and digits, insert spaces
    let s = v.replace(/[^+\d]/g, "");
    // If it starts with 0 and no +, just group a bit; if +972, format Israeli-ish
    if (s.startsWith("+972")) {
      const d = s.slice(4); // rest after +972
      return "+972 " + d.replace(/(\d{2})(\d{3})(\d{4})/, (m, a, b, c) => `${a}-${b}-${c}`);
    }
    // Fallback: group by 3-3-4 if 10 digits, else return as-is
    const d10 = phoneDigits(s);
    if (d10.length === 10) return d10.replace(/(\d{3})(\d{3})(\d{4})/, "$1-$2-$3");
    return s;
  }

  function setFieldError(el, msg = "") {
    el.setCustomValidity(msg);
    // Let the browser draw native error styles if invalid
  }

  function validateField(el) {
    const id = el.id;
    const v = el.value.trim();

    switch (id) {
      case "name": {
        if (v.length < 2) setFieldError(el, "Please enter your full name.");
        else setFieldError(el);
        break;
      }
      case "email": {
        if (!emailValid(v)) setFieldError(el, "Enter a valid email address.");
        else setFieldError(el);
        break;
      }
      case "phone": {
        // Require at least 9 digits
        if (phoneDigits(v).length < 9) setFieldError(el, "Enter a valid phone number.");
        else setFieldError(el);
        break;
      }
      case "password": {
        const score = passwordScore(v);
        if (score < 2) setFieldError(el, "Use a stronger password.");
        else setFieldError(el);
        updatePasswordMeter(score);
        break;
      }
      case "address_street":
      case "address_house_number":
      case "address_city":
      case "address_postal_code":
      case "address_country": {
        if (!v) setFieldError(el, "Required");
        else setFieldError(el);
        break;
      }
    }
  }

  // --- Password strength meter ---
  const meter = document.createElement("div");
  meter.setAttribute("aria-hidden", "true");
  meter.style.height = "6px";
  meter.style.borderRadius = "999px";
  meter.style.background = "#e5e7eb"; // neutral track
  meter.style.marginTop = "4px";
  const bar = document.createElement("div");
  bar.style.height = "100%";
  bar.style.width = "0%";
  bar.style.borderRadius = "inherit";
  bar.style.background = "var(--primary)";
  meter.appendChild(bar);
  passI.insertAdjacentElement("afterend", meter);

  function passwordScore(pw) {
    let s = 0;
    if (pw.length >= 8) s++;
    if (/[A-Z]/.test(pw)) s++;
    if (/[a-z]/.test(pw)) s++;
    if (/[0-9]/.test(pw)) s++;
    if (/[^A-Za-z0-9]/.test(pw)) s++;
    return Math.min(s, 4); // 0..4
  }

  function updatePasswordMeter(score) {
    const widths = ["0%", "25%", "50%", "75%", "100%"]; // 0..4
    bar.style.width = widths[score];
  }

  // Show/Hide password toggle
  const toggleBtn = document.createElement("button");
  toggleBtn.type = "button";
  toggleBtn.textContent = "Show";
  toggleBtn.className = "btn btn-ghost";
  toggleBtn.style.marginTop = "4px";
  toggleBtn.style.background = "transparent";
  toggleBtn.style.color = "var(--primary)";
  toggleBtn.style.border = "none";
  toggleBtn.style.cursor = "pointer";
  passI.insertAdjacentElement("afterend", toggleBtn);
  toggleBtn.addEventListener("click", () => {
    const isPw = passI.type === "password";
    passI.type = isPw ? "text" : "password";
    toggleBtn.textContent = isPw ? "Hide" : "Show";
  });

  // --- Country-aware postal code hint (simple) ---
  function applyPostalRules() {
    const country = (addrCountryI.value || "").toLowerCase();
    if (country.includes("israel")) {
      addrPostalI.pattern = "\\d{5,7}"; // 5–7 digits
      addrPostalI.title = "Postal code should be 5–7 digits.";
    } else {
      addrPostalI.removeAttribute("pattern");
      addrPostalI.removeAttribute("title");
    }
  }

  applyPostalRules();
  addrCountryI.addEventListener("input", applyPostalRules);

  // --- Live formatting & validation ---
  nameI.addEventListener("input", () => {
    sanitizeSpaces(nameI);
    // Title-case without jumping caret: only on blur to avoid cursor jumps
  });
  nameI.addEventListener("blur", () => nameI.value = titleCaseName(nameI.value.trim()));

  emailI.addEventListener("input", () => validateField(emailI));

  phoneI.addEventListener("input", () => {
    const caret = phoneI.selectionStart;
    const beforeLen = phoneI.value.length;
    phoneI.value = formatIntlPhone(phoneI.value);
    // Best-effort caret restore
    const afterLen = phoneI.value.length;
    phoneI.selectionStart = phoneI.selectionEnd = Math.max(0, caret + (afterLen - beforeLen));
    validateField(phoneI);
  });

  passI.addEventListener("input", () => validateField(passI));

  [addrStreetI, addrHouseI, addrCityI, addrPostalI, addrCountryI].forEach(el => {
    el && el.addEventListener("input", () => validateField(el));
  });

  // --- Save draft (except password) ---
  const DRAFT_KEY = "signupDraft.v1";
  function saveDraft() {
    const data = {
      name: nameI.value,
      email: emailI.value,
      phone: phoneI.value,
      address_street: addrStreetI.value,
      address_house_number: addrHouseI.value,
      address_city: addrCityI.value,
      address_postal_code: addrPostalI.value,
      address_country: addrCountryI.value,
      address_apartment: $("#address_apartment")?.value || "",
      address_floor: $("#address_floor")?.value || "",
      address_message: $("#address_message")?.value || "",
    };
    localStorage.setItem(DRAFT_KEY, JSON.stringify(data));
  }

  function loadDraft() {
    try {
      const raw = localStorage.getItem(DRAFT_KEY);
      if (!raw) return;
      const d = JSON.parse(raw);
      if (d.name) nameI.value = d.name;
      if (d.email) emailI.value = d.email;
      if (d.phone) phoneI.value = d.phone;
      if (d.address_street) addrStreetI.value = d.address_street;
      if (d.address_house_number) addrHouseI.value = d.address_house_number;
      if (d.address_city) addrCityI.value = d.address_city;
      if (d.address_postal_code) addrPostalI.value = d.address_postal_code;
      if (d.address_country) addrCountryI.value = d.address_country;
      const ap = $("#address_apartment"); if (ap && d.address_apartment) ap.value = d.address_apartment;
      const fl = $("#address_floor"); if (fl && d.address_floor) fl.value = d.address_floor;
      const msg = $("#address_message"); if (msg && d.address_message) msg.value = d.address_message;
    } catch {}
  }

  loadDraft();
  $$("input").forEach(el => el.addEventListener("input", saveDraft));

  // --- Disable submit until valid ---
  function formIsValid() {
    // Trigger validation pass without blocking
    [nameI, emailI, phoneI, passI, addrStreetI, addrHouseI, addrCityI, addrPostalI, addrCountryI]
      .filter(Boolean).forEach(validateField);
    return form.checkValidity();
  }

  function updateSubmitState() {
    submitBtn.disabled = !formIsValid();
  }

  form.addEventListener("input", updateSubmitState);
  updateSubmitState();

  // --- Submit UX (prevent double submit) ---
  form.addEventListener("submit", (e) => {
    if (!formIsValid()) {
      e.preventDefault();
      form.reportValidity();
      return;
    }
    submitBtn.disabled = true;
    const prev = submitBtn.textContent;
    submitBtn.textContent = "Creating account…";
    // Let the real submit proceed; if the server responds with an error page,
    // the button will reset on load. If you stay on page (AJAX), reset manually.
    setTimeout(() => (submitBtn.textContent = prev), 10000); // safety reset
  });
})();
