const header = document.querySelector("[data-header]");
const toggles = document.querySelectorAll("[data-cycle]");
const priceNodes = document.querySelectorAll("[data-price]");
const periodNodes = document.querySelectorAll("[data-period]");
const leadForm = document.querySelector(".lead-form");

const backendTitle = document.querySelector("#backendTitle");
const backendNavItems = document.querySelectorAll("[data-backend-tab]");
const backendViews = document.querySelectorAll("[data-backend-view]");
const tenantRows = document.querySelector("#tenantRows");
const tenantCards = document.querySelector("#tenantCards");
const selectedTenant = document.querySelector("#selectedTenant");
const tenantModal = document.querySelector("#tenantModal");
const tenantForm = document.querySelector("#tenantForm");
const openTenantModal = document.querySelector("[data-open-tenant-modal]");
const closeModalButtons = document.querySelectorAll("[data-close-modal]");
const logList = document.querySelector("#logList");
const importResult = document.querySelector("#importResult");
const solutionCards = document.querySelectorAll("[data-solution]");
const solutionBadge = document.querySelector("#solutionBadge");
const solutionTitle = document.querySelector("#solutionTitle");
const solutionSummary = document.querySelector("#solutionSummary");
const solutionFeatures = document.querySelector("#solutionFeatures");

const solutions = {
  construction: {
    badge: "CON",
    title: "نظام المقاولات",
    summary: "حل SaaS لإدارة دورة المقاولات من BOQ إلى المستخلصات وتقارير المشروع.",
    features: ["BOQ وبنود الأعمال", "مستخلصات المالك والمقاول", "ميزانيات وتكاليف المشاريع", "مشتريات ومخزون", "تقارير تقدم الأعمال", "عهد مالية وتشغيلية"],
  },
  realestate: {
    badge: "REA",
    title: "نظام ريل ستيت",
    summary: "حل لإدارة دورة الريل ستيت من lead في CRM إلى الوحدة والحجز وخطة الدفعات.",
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
  education: {
    badge: "LMS",
    title: "نظام التعليم وLMS",
    summary: "بوابة تعليمية قابلة للربط مع SaaS لإدارة الدروس والاختبارات والاشتراكات.",
    features: ["دروس ومحتوى تعليمي", "اختبارات وواجبات", "جلسات مباشرة", "بوابة طالب وولي أمر", "اشتراكات تعليمية", "Analytics للمدرسة"],
  },
};

const tenants = [
  {
    company: "Al Riyada Contracting",
    sector: "مقاولات",
    plan: "Construction Business",
    database: "tenant_riyadah",
    status: "Active",
  },
  {
    company: "Fast Mile Logistics",
    sector: "3PL",
    plan: "3PL Business",
    database: "tenant_fastmile",
    status: "Provisioning",
  },
  {
    company: "Jadeer Properties",
    sector: "ريل ستيت",
    plan: "Real Estate Business",
    database: "tenant_jadeer",
    status: "Active",
  },
  {
    company: "Saudi People Co.",
    sector: "HR",
    plan: "Saudi HR Business",
    database: "tenant_hr_sa",
    status: "Suspended",
  },
];

const viewTitles = {
  dashboard: "Dashboard",
  tenants: "Tenants",
  plans: "Plans",
  subscriptions: "Subscriptions",
  payments: "Payments",
  logs: "Provisioning Logs",
  imports: "Onboarding Imports",
};

window.addEventListener("scroll", () => {
  header.style.transform = window.scrollY > 8 ? "translateY(-2px)" : "translateY(0)";
});

toggles.forEach((button) => {
  button.addEventListener("click", () => {
    const cycle = button.dataset.cycle;
    toggles.forEach((item) => item.classList.toggle("active", item === button));
    priceNodes.forEach((node) => {
      node.textContent = `${Number(node.dataset[cycle]).toLocaleString("ar-SA")} ر.س`;
    });
    periodNodes.forEach((node) => {
      node.textContent = cycle === "yearly" ? "/ سنويا" : "/ شهريا";
    });
  });
});

solutionCards.forEach((card) => {
  card.addEventListener("click", () => showSolution(card.dataset.solution));
  card.addEventListener("keydown", (event) => {
    if (event.key === "Enter" || event.key === " ") {
      event.preventDefault();
      showSolution(card.dataset.solution);
    }
  });
});

backendNavItems.forEach((button) => {
  button.addEventListener("click", () => {
    const tab = button.dataset.backendTab;
    backendNavItems.forEach((item) => item.classList.toggle("active", item === button));
    backendViews.forEach((view) => view.classList.toggle("active", view.dataset.backendView === tab));
    backendTitle.textContent = viewTitles[tab];
  });
});

document.querySelectorAll("[data-filter-status]").forEach((button) => {
  button.addEventListener("click", () => {
    renderTenantRows(button.dataset.filterStatus);
    selectedTenant.textContent = `عرض العملاء بحالة ${button.dataset.filterStatus}`;
  });
});

openTenantModal.addEventListener("click", () => {
  tenantModal.showModal();
});

closeModalButtons.forEach((button) => {
  button.addEventListener("click", () => tenantModal.close());
});

tenantForm.addEventListener("submit", (event) => {
  event.preventDefault();
  const formData = new FormData(tenantForm);
  const tenant = {
    company: formData.get("company"),
    sector: formData.get("sector"),
    plan: formData.get("plan"),
    database: formData.get("database"),
    status: "Provisioning",
  };

  tenants.unshift(tenant);
  tenantModal.close();
  renderBackend();
  selectedTenant.textContent = `${tenant.company} تم إنشاؤه وحالته Provisioning`;
  addLog(`create_database - ${tenant.database} - pending`);
});

document.querySelector("[data-simulate-import]").addEventListener("click", () => {
  importResult.textContent = "تمت محاكاة رفع البيانات: 42 record جاهزة للإرسال إلى tenant database.";
  addLog("onboarding_import - demo file - success");
});

leadForm.addEventListener("submit", (event) => {
  event.preventDefault();
  const button = leadForm.querySelector("button");
  button.textContent = "تم استلام الطلب";
  button.disabled = true;
});

function renderBackend() {
  renderTenantRows();
  renderTenantCards();
  updateMetrics();
}

function renderTenantRows(filterStatus = "") {
  tenantRows.innerHTML = "";
  tenants.forEach((tenant) => {
    const row = document.createElement("tr");
    if (filterStatus && tenant.status !== filterStatus) row.classList.add("hidden");
    row.innerHTML = `
      <td>${tenant.company}</td>
      <td>${tenant.sector}</td>
      <td>${tenant.plan}</td>
      <td>${tenant.database}</td>
      <td><span class="status ${statusClass(tenant.status)}">${tenant.status}</span></td>
    `;
    row.addEventListener("click", () => {
      selectedTenant.textContent = `${tenant.company} | ${tenant.database} | ${tenant.plan}`;
      addLog(`open_tenant - ${tenant.database} - viewed`);
    });
    tenantRows.appendChild(row);
  });
}

function renderTenantCards() {
  tenantCards.innerHTML = "";
  tenants.forEach((tenant) => {
    const card = document.createElement("article");
    card.innerHTML = `
      <strong>${tenant.company}</strong>
      <span>${tenant.sector} - ${tenant.plan}</span>
      <p>${tenant.database} · ${tenant.status}</p>
    `;
    card.addEventListener("click", () => {
      backendNavItems.forEach((item) => item.classList.toggle("active", item.dataset.backendTab === "dashboard"));
      backendViews.forEach((view) => view.classList.toggle("active", view.dataset.backendView === "dashboard"));
      backendTitle.textContent = "Dashboard";
      selectedTenant.textContent = `${tenant.company} | ${tenant.database} | ${tenant.plan}`;
    });
    tenantCards.appendChild(card);
  });
}

function updateMetrics() {
  document.querySelector("[data-metric='active']").textContent = tenants.filter((tenant) => tenant.status === "Active").length;
  document.querySelector("[data-metric='provisioning']").textContent = tenants.filter((tenant) => tenant.status === "Provisioning").length;
  document.querySelector("[data-metric='suspended']").textContent = tenants.filter((tenant) => tenant.status === "Suspended").length;
  document.querySelector("[data-metric='mrr']").textContent = `${(tenants.length * 1500).toLocaleString("ar-SA")} ر.س`;
}

function addLog(message) {
  const item = document.createElement("button");
  item.type = "button";
  item.textContent = message;
  logList.prepend(item);
}

function statusClass(status) {
  if (status === "Active") return "ok";
  if (status === "Provisioning") return "warn";
  return "bad";
}

function showSolution(key) {
  const solution = solutions[key];
  if (!solution) return;
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
renderBackend();
