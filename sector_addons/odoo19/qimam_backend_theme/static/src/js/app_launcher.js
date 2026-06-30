/** @odoo-module **/

(function () {
    "use strict";

    const ICONS = [
        [/construction/i, "CON"],
        [/financial custody/i, "FIN"],
        [/discuss/i, "DS"],
        [/to-?do/i, "TD"],
        [/sales/i, "SAL"],
        [/crm/i, "CRM"],
        [/dashboard/i, "DB"],
        [/invoice|invoicing/i, "INV"],
        [/project/i, "PRJ"],
        [/purchase/i, "PO"],
        [/inventory/i, "INV"],
        [/manufacturing/i, "MFG"],
        [/employee|hr/i, "HR"],
        [/link tracker/i, "LNK"],
        [/website/i, "WEB"],
        [/contact/i, "CNT"],
        [/calendar/i, "CAL"],
        [/apps/i, "APP"],
        [/setting/i, "SET"],
        [/real estate|property/i, "RE"],
        [/3pl|delivery/i, "3PL"],
    ];

    function iconFor(label) {
        const text = (label || "").trim();
        const match = ICONS.find(([pattern]) => pattern.test(text));
        if (match) {
            return match[1];
        }
        return text
            .split(/\s+/)
            .filter(Boolean)
            .slice(0, 2)
            .map((part) => part.charAt(0).toUpperCase())
            .join("") || "QM";
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
            item.dataset.qimamIcon = iconFor(label);
            item.textContent = "";

            const icon = document.createElement("span");
            icon.className = "qimam-app-icon";
            icon.textContent = item.dataset.qimamIcon;

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
            item.dataset.qimamIcon = iconFor(label);
            item.textContent = "";

            const icon = document.createElement("span");
            icon.className = "qimam-menu-icon";
            icon.textContent = item.dataset.qimamIcon;

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
