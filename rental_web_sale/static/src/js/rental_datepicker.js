/** @odoo-module **/
import { loadJS, loadCSS } from "@web/core/assets";

document.addEventListener("DOMContentLoaded", async () => {
    await loadJS("https://cdn.jsdelivr.net/npm/flatpickr");
    await loadCSS("https://cdn.jsdelivr.net/npm/flatpickr/dist/flatpickr.min.css");

    flatpickr('input[name="start_date"]', { dateFormat: "Y-m-d" });
    flatpickr('input[name="end_date"]', { dateFormat: "Y-m-d" });
    flatpickr('input[name="start_time"]', { enableTime: true, noCalendar: true, dateFormat: "H:i" });
    flatpickr('input[name="end_time"]', { enableTime: true, noCalendar: true, dateFormat: "H:i" });
});
