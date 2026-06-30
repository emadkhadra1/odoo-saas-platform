/** @odoo-module **/

(function () {
    "use strict";

    const ICON_BASE = "/qimam_backend_theme/static/src/img/icons/";
    const APP_ITEM_SELECTOR = "a, button, li, .dropdown-item, .o_app, [role='menuitem'], [data-menu-id], [data-menu-xmlid]";
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

    function cleanText(element) {
        return (element.textContent || "").replace(/\s+/g, " ").trim();
    }

    function isVisible(element) {
        const style = getComputedStyle(element);
        const box = element.getBoundingClientRect();
        return style.display !== "none" && style.visibility !== "hidden" && box.width > 0 && box.height > 0;
    }

    function isAppLikeItem(item) {
        const label = cleanText(item);
        if (!label) {
            return false;
        }
        const href = item.getAttribute("href") || "";
        const classes = item.className ? String(item.className) : "";
        return classes.includes("o_app") || href.includes("menu_id=") || ICONS.some(([pattern]) => pattern.test(label));
    }

    function appMenuContainers() {
        const selectors = [
            ".o_main_navbar .o_menu_apps .dropdown-menu",
            ".o_main_navbar .o_menu_apps_menu",
            ".o_main_navbar .o_menu_toggle ~ .dropdown-menu",
            ".o-dropdown--menu.dropdown-menu",
            ".dropdown-menu",
        ].join(",");
        return [...document.querySelectorAll(selectors)].filter((container) => {
            const items = [...container.querySelectorAll(APP_ITEM_SELECTOR)].filter(isAppLikeItem);
            return items.length >= 4;
        });
    }

    function enhanceItem(item, iconClass, titleClass) {
        if (item.classList.contains("qimam-app-tile") || item.classList.contains("qimam-menu-tile")) {
            return;
        }
        const label = cleanText(item);
        if (!label) {
            return;
        }
        item.classList.add(iconClass === "qimam-app-icon" ? "qimam-app-tile" : "qimam-menu-tile");
        const iconInfo = iconFor(label);
        item.dataset.qimamIcon = iconInfo.code;
        item.textContent = "";

        const icon = document.createElement("span");
        icon.className = iconClass;
        applyIcon(icon, iconInfo);

        const title = document.createElement("span");
        title.className = titleClass;
        title.textContent = label;

        item.append(icon, title);
    }

    function enhanceLauncher() {
        for (const container of appMenuContainers()) {
            container.classList.add("qimam-app-menu-panel");
            container.classList.toggle("qimam-app-menu-panel-open", isVisible(container));
            const items = [...container.querySelectorAll(APP_ITEM_SELECTOR)].filter(isAppLikeItem);
            for (const item of items) {
                enhanceItem(item, "qimam-app-icon", "qimam-app-title");
            }
        }
    }

    function enhanceSidebar() {
        const items = document.querySelectorAll(".o_app_menu_sidebar li.py-2");
        for (const item of items) {
            enhanceItem(item, "qimam-menu-icon", "qimam-menu-title");
        }
    }

    function enhanceMenus() {
        enhanceLauncher();
        enhanceSidebar();
    }

    let enhanceQueued = false;

    function queueEnhanceMenus() {
        if (enhanceQueued) {
            return;
        }
        enhanceQueued = true;
        requestAnimationFrame(() => {
            enhanceQueued = false;
            enhanceMenus();
        });
    }

    const observer = new MutationObserver(queueEnhanceMenus);

    function start() {
        enhanceMenus();
        observer.observe(document.body, {
            childList: true,
            subtree: true,
            attributes: true,
            attributeFilter: ["class", "style"],
        });
    }

    if (document.readyState === "loading") {
        document.addEventListener("DOMContentLoaded", start, { once: true });
    } else {
        start();
    }
})();
