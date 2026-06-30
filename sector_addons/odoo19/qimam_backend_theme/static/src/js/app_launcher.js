/** @odoo-module **/

(function () {
    "use strict";

    const ICON_BASE = "/qimam_backend_theme/static/src/img/icons/";
    const ICONS = [
        [/construction|contract/i, { code: "CON", icon: "construction.svg" }],
        [/financial custody|account|invoice|invoicing/i, { code: "FIN", icon: "finance.svg" }],
        [/discuss/i, { code: "DS", icon: "messages.svg" }],
        [/to-?do/i, { code: "TD", icon: "tasks.svg" }],
        [/sales|crm/i, { code: "SAL", icon: "sales.svg" }],
        [/dashboard/i, { code: "DB", icon: "dashboard.svg" }],
        [/project/i, { code: "PRJ", icon: "project.svg" }],
        [/purchase/i, { code: "PO", icon: "purchase.svg" }],
        [/inventory|stock/i, { code: "STK", icon: "inventory.svg" }],
        [/manufacturing|mrp/i, { code: "MFG", icon: "manufacturing.svg" }],
        [/employee|hr|human/i, { code: "HR", icon: "hr.svg" }],
        [/link tracker/i, { code: "LNK", icon: "link.svg" }],
        [/website/i, { code: "WEB", icon: "website.svg" }],
        [/contact/i, { code: "CNT", icon: "contacts.svg" }],
        [/calendar/i, { code: "CAL", icon: "calendar.svg" }],
        [/apps/i, { code: "APP", icon: "apps.svg" }],
        [/setting|configuration/i, { code: "SET", icon: "settings.svg" }],
        [/real estate|property/i, { code: "RE", icon: "realestate.svg" }],
        [/3pl|delivery|logistic/i, { code: "3PL", icon: "delivery.svg" }],
    ];

    function iconFor(label) {
        const text = (label || "").trim();
        const match = ICONS.find(([pattern]) => pattern.test(text));
        if (match) {
            return match[1];
        }
        return {
            code: text
                .split(/\s+/)
                .filter(Boolean)
                .slice(0, 2)
                .map((part) => part.charAt(0).toUpperCase())
                .join("") || "QM",
            icon: "default.svg",
        };
    }

    function applyIcon(iconElement, iconInfo) {
        iconElement.dataset.qimamIcon = iconInfo.code;
        iconElement.style.setProperty("--qimam-icon-url", `url("${ICON_BASE}${iconInfo.icon}")`);
        iconElement.title = iconInfo.code;
    }

    function enhanceLauncher() {
        const items = document.querySelectorAll(
            ".o_main_navbar .o_menu_apps .dropdown-menu .dropdown-item, .o_main_navbar .o_menu_apps_menu .dropdown-item"
        );
        for (const item of items) {
            if (item.classList.contains("qimam-app-tile")) {
                continue;
            }
            const label = item.textContent.replace(/\s+/g, " ").trim();
            if (!label) {
                continue;
            }
            item.classList.add("qimam-app-tile");
            const iconInfo = iconFor(label);
            item.dataset.qimamIcon = iconInfo.code;
            item.textContent = "";

            const icon = document.createElement("span");
            icon.className = "qimam-app-icon";
            applyIcon(icon, iconInfo);

            const title = document.createElement("span");
            title.className = "qimam-app-title";
            title.textContent = label;

            item.append(icon, title);
        }
    }

    function enhanceSidebar() {
        const items = document.querySelectorAll(".o_app_menu_sidebar li.py-2");
        for (const item of items) {
            if (item.classList.contains("qimam-menu-tile")) {
                continue;
            }
            const label = item.textContent.replace(/\s+/g, " ").trim();
            if (!label) {
                continue;
            }
            item.classList.add("qimam-menu-tile");
            const iconInfo = iconFor(label);
            item.dataset.qimamIcon = iconInfo.code;
            item.textContent = "";

            const icon = document.createElement("span");
            icon.className = "qimam-menu-icon";
            applyIcon(icon, iconInfo);

            const title = document.createElement("span");
            title.className = "qimam-menu-title";
            title.textContent = label;

            item.append(icon, title);
        }
    }

    function enhanceMenus() {
        enhanceLauncher();
        enhanceSidebar();
    }

    const observer = new MutationObserver(enhanceMenus);

    function start() {
        enhanceMenus();
        observer.observe(document.body, {
            childList: true,
            subtree: true,
        });
    }

    if (document.readyState === "loading") {
        document.addEventListener("DOMContentLoaded", start, { once: true });
    } else {
        start();
    }
})();
