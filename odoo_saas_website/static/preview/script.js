const header = document.querySelector("[data-header]");
const toggles = document.querySelectorAll("[data-cycle]");
const priceNodes = document.querySelectorAll("[data-price]");
const periodNodes = document.querySelectorAll("[data-period]");
const leadForm = document.querySelector(".lead-form");
const loginLinks = document.querySelectorAll("[data-odoo-login]");
const lang = document.documentElement.lang === "en" ? "en" : "ar";

const copy = {
  ar: {
    currency: "ر.س",
    locale: "ar-SA",
    monthly: "/ شهريا",
    yearly: "/ سنويا",
    sending: "جاري الإرسال...",
    sent: "تم إنشاء Lead في CRM",
    error: "تعذر الإرسال، حاول مرة أخرى",
  },
  en: {
    currency: "SAR",
    locale: "en-US",
    monthly: "/ month",
    yearly: "/ year",
    sending: "Sending...",
    sent: "Lead created in CRM",
    error: "Could not send. Please try again",
  },
};

if (header) {
  window.addEventListener("scroll", () => {
    header.style.transform = window.scrollY > 8 ? "translateY(-2px)" : "translateY(0)";
  });
}

if (loginLinks.length) {
  const localPreview = ["127.0.0.1", "localhost"].includes(window.location.hostname) || window.location.protocol === "file:";
  const loginPath = "/web/login?db=sass";
  const loginUrl = localPreview ? "http://178.104.83.32:8069/web/login?db=sass" : loginPath;
  loginLinks.forEach((link) => {
    link.href = loginUrl;
  });
}

toggles.forEach((button) => {
  button.addEventListener("click", () => {
    const cycle = button.dataset.cycle;
    toggles.forEach((item) => item.classList.toggle("active", item === button));
    priceNodes.forEach((node) => {
      const formattedPrice = Number(node.dataset[cycle]).toLocaleString(copy[lang].locale);
      node.textContent = lang === "ar" ? `${formattedPrice} ${copy[lang].currency}` : `${copy[lang].currency} ${formattedPrice}`;
    });
    periodNodes.forEach((node) => {
      node.textContent = cycle === "yearly" ? copy[lang].yearly : copy[lang].monthly;
    });
  });
});

if (leadForm) {
  leadForm.addEventListener("submit", async (event) => {
    event.preventDefault();
    const button = leadForm.querySelector("button");
    const originalText = button.textContent;
    const formData = new FormData(leadForm);
    const payload = Object.fromEntries(formData.entries());

    button.textContent = copy[lang].sending;
    button.disabled = true;

    try {
      const response = await fetch(leadForm.dataset.crmEndpoint, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify(payload),
      });
      const result = await response.json();
      if (!response.ok || !result.ok) {
        throw new Error(result.error || "crm_error");
      }
      button.textContent = copy[lang].sent;
      leadForm.reset();
    } catch (error) {
      button.textContent = copy[lang].error;
      setTimeout(() => {
        button.textContent = originalText;
        button.disabled = false;
      }, 2600);
    }
  });
}
