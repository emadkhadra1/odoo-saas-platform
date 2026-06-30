/** @odoo-module **/
import {browser} from "@web/core/browser/browser";
import {registry} from "@web/core/registry";

export const webNotificationService = {
    dependencies: ["notification"],

    start(env, {notification}) {
        let webNotifTimeouts = {};
                let calendarNotifTimeouts = {};

        let nextCalendarNotifTimeout = null;
        const displayedNotifications = new Set();

        /**
         * Displays the web notification on user's screen
         */

        function displaywebNotification(notifications) {
            Object.values(webNotifTimeouts).forEach((notif) =>
                browser.clearTimeout(notif)
            );
            webNotifTimeouts = {};

            notifications.forEach(function (notif) {
                browser.setTimeout(function () {
                    notification.add(notif.message, {
                        title: notif.title,
                        type: notif.type,
                        sticky: notif.sticky,
                        className: notif.className,

                    });
                });
            });
        }
        function displayCalendarNotification(notifications) {
            let lastNotifTimer = 0;

            // Clear previously set timeouts and destroy currently displayed calendar notifications
            browser.clearTimeout(nextCalendarNotifTimeout);
            Object.values(calendarNotifTimeouts).forEach((notif) => browser.clearTimeout(notif));
            calendarNotifTimeouts = {};

            // For each notification, set a timeout to display it
            notifications.forEach(function (notif) {
                const key = notif.event_id + "," + notif.alarm_id;
                if (displayedNotifications.has(key)) {
                    return;
                }
                calendarNotifTimeouts[key] = browser.setTimeout(function () {
                    const notificationRemove = notification.add(notif.message, {
                        title: notif.title,
                        type: "warning",
                        sticky: true,
                        onClose: () => {
                            displayedNotifications.delete(key);
                        },
                        buttons: [
                            {
                                name: env._t("OK"),
                                primary: true,
                                onClick: async () => {
                                    await rpc("/calendar/notify_ack");
                                    notificationRemove();
                                },
                            },
                            {
                                name: env._t("Details"),
                                onClick: async () => {
                                    await action.doAction({
                                        type: 'ir.actions.act_window',
                                        res_model: 'calendar.event',
                                        res_id: notif.event_id,
                                        views: [[false, 'form']],
                                    }
                                    );
                                    notificationRemove();
                                },
                            },
                            {
                                name: env._t("Snooze"),
                                onClick: () => {
                                    notificationRemove();
                                },
                            },
                        ],
                    });
                    displayedNotifications.add(key);
                }, notif.timer * 1000);
                lastNotifTimer = Math.max(lastNotifTimer, notif.timer);
            });

            // Set a timeout to get the next notifications when the last one has been displayed
            if (lastNotifTimer > 0) {
                nextCalendarNotifTimeout = browser.setTimeout(
                    getNextCalendarNotif,
                    lastNotifTimer * 1000
                );
            }
        }

        env.bus.on("WEB_CLIENT_READY", null, async () => {
            const legacyEnv = owl.Component.env;
            legacyEnv.services.bus_service.onNotification(this, (notifications) => {
                for (const {payload, type} of notifications) {
                    if (type === "web.notify") {
                        displaywebNotification(payload);

                    }
                }
            });
            legacyEnv.services.bus_service.startPolling();
        });
    },
};

registry.category("services").add("webNotification", webNotificationService);
