const header = document.querySelector("[data-header]");
const toggles = document.querySelectorAll("[data-cycle]");
const priceNodes = document.querySelectorAll("[data-price]");
const periodNodes = document.querySelectorAll("[data-period]");
const leadForm = document.querySelector(".lead-form");
const solutionCards = document.querySelectorAll("[data-solution]");
const solutionBadge = document.querySelector("#solutionBadge");
const solutionTitle = document.querySelector("#solutionTitle");
const solutionSummary = document.querySelector("#solutionSummary");
const solutionFeatures = document.querySelector("#solutionFeatures");
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
    solutions: {
      construction: {
        badge: "CON",
        title: "نظام المقاولات",
        summary: "حل SaaS لإدارة دورة المقاولات من BOQ إلى المستخلصات وتقارير المشروع.",
        features: ["BOQ وبنود الأعمال", "مستخلصات المالك والمقاول", "ميزانيات وتكاليف المشاريع", "مشتريات ومخزون", "تقارير تقدم الأعمال", "عهد مالية وتشغيلية"],
      },
      realestate: {
        badge: "REA",
        title: "نظام الاستثمار العقاري",
        summary: "حل لإدارة دورة الاستثمار العقاري من lead في CRM إلى الوحدة والحجز وخطة الدفعات.",
        features: ["مشروعات ومبان ووحدات", "CRM ومتابعة العملاء", "حجز وحدات وعروض سعر", "خطط دفعات", "تحصيلات وفواتير", "تقارير المبيعات والوحدات"],
      },
      hr: {
        badge: "HR",
        title: "نظام الموارد البشرية السعودي",
        summary: "حل HR يدعم الحضور، الجزاءات، المكافآت، العهد، القروض، ونهاية الخدمة.",
        features: ["ملف موظف متكامل", "قواعد حضور وانصراف", "مكافآت وجزاءات", "عهد الموظفين", "قروض وسلف", "نهاية خدمة وتأمينات"],
      },
      logistics: {
        badge: "3PL",
        title: "نظام 3PL واللوجستيات",
        summary: "حل لشركات التوصيل وإدارة المناديب والتسعير والتسويات والأداء.",
        features: ["إدارة المناديب", "عقود وتدرجات أسعار", "استيراد عمليات التوصيل", "تسويات ومحاسبة", "محافظ وأهداف", "Dashboard أداء"],
      },
    },
  },
  en: {
    currency: "SAR",
    locale: "en-US",
    monthly: "/ month",
    yearly: "/ year",
    sending: "Sending...",
    sent: "Lead created in CRM",
    error: "Could not send. Please try again",
    solutions: {
      construction: {
        badge: "CON",
        title: "Construction System",
        summary: "A SaaS solution for managing construction from BOQ and cost control to progress certificates and reports.",
        features: ["BOQ and work items", "Owner and subcontractor certificates", "Project budgets and costs", "Procurement and inventory", "Progress reports", "Financial and site custody"],
      },
      realestate: {
        badge: "REA",
        title: "Real Estate Investment System",
        summary: "Manage the real estate cycle from CRM lead to unit reservation, payment plans, invoicing, and collection.",
        features: ["Projects, buildings, and units", "Real estate CRM", "Reservations and quotations", "Payment plans", "Collections and invoices", "Sales and unit reports"],
      },
      hr: {
        badge: "HR",
        title: "Saudi HR System",
        summary: "An HR solution for employee files, attendance, custody, loans, penalties, rewards, and end-of-service workflows.",
        features: ["Employee profile", "Attendance rules", "Rewards and penalties", "Employee custody", "Loans and advances", "End-of-service tracking"],
      },
      logistics: {
        badge: "3PL",
        title: "3PL Logistics System",
        summary: "A logistics solution for couriers, contracts, tiered pricing, delivery operations, settlements, and performance.",
        features: ["Courier management", "Contracts and pricing tiers", "Delivery operation imports", "Settlements and accounting", "Wallets and targets", "Performance dashboard"],
      },
    },
  },
};

if (header) {
  window.addEventListener("scroll", () => {
    header.style.transform = window.scrollY > 8 ? "translateY(-2px)" : "translateY(0)";
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

solutionCards.forEach((card) => {
  card.addEventListener("click", (event) => {
    if (event.target.closest("a")) return;
    showSolution(card.dataset.solution);
  });
  card.addEventListener("keydown", (event) => {
    if (event.key === "Enter" || event.key === " ") {
      event.preventDefault();
      showSolution(card.dataset.solution);
    }
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

function showSolution(key) {
  const solution = copy[lang].solutions[key];
  if (!solution || !solutionBadge || !solutionTitle || !solutionSummary || !solutionFeatures) return;
  solutionCards.forEach((card) => card.classList.toggle("active", card.dataset.solution === key));
  solutionBadge.textContent = solution.badge;
  solutionTitle.textContent = solution.title;
  solutionSummary.textContent = solution.summary;
  solutionFeatures.innerHTML = "";
  solution.features.forEach((feature) => {
    const item = document.createElement("li");
    item.textContent = feature;
    solutionFeatures.appendChild(item);
  });
}

showSolution("construction");
