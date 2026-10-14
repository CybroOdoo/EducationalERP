/** @odoo-module **/
/**
 * education_dashboard — shared helpers and base class for the Admin and
 * Faculty dashboards (filters, formatting, navigation).
 */
import { Component, useState } from "@odoo/owl";
import { useService } from "@web/core/utils/hooks";

export const PERIODS = [
    { key: "today", label: "Today" },
    { key: "7d", label: "Last 7 days" },
    { key: "30d", label: "Last 30 days" },
    { key: "month", label: "This month" },
    { key: "year", label: "This year" },
    { key: "all", label: "All time" },
    { key: "custom", label: "Custom range…" },
];

const pad = (n) => String(n).padStart(2, "0");
export const isoDate = (d) => `${d.getFullYear()}-${pad(d.getMonth() + 1)}-${pad(d.getDate())}`;

/** Convert a period preset to {date_from, date_to} ISO strings ("" = open). */
export function periodRange(key) {
    const today = new Date();
    const start = new Date(today);
    switch (key) {
        case "today":
            return { date_from: isoDate(today), date_to: isoDate(today) };
        case "7d":
            start.setDate(today.getDate() - 6);
            return { date_from: isoDate(start), date_to: isoDate(today) };
        case "30d":
            start.setDate(today.getDate() - 29);
            return { date_from: isoDate(start), date_to: isoDate(today) };
        case "month":
            return {
                date_from: isoDate(new Date(today.getFullYear(), today.getMonth(), 1)),
                date_to: isoDate(today),
            };
        case "year":
            return {
                date_from: isoDate(new Date(today.getFullYear(), 0, 1)),
                date_to: isoDate(today),
            };
        default:
            return { date_from: "", date_to: "" };
    }
}

export const sleep = (ms) => new Promise((resolve) => setTimeout(resolve, ms));

export class EduDashboardBase extends Component {
    static props = ["*"];
    defaultPeriod = "30d";

    setup() {
        this.orm = useService("orm");
        this.action = useService("action");
        this.periods = PERIODS;
        this.state = useState({
            loading: true,
            data: null,
            period: this.defaultPeriod,
            ...periodRange(this.defaultPeriod),
            class_id: "",
            program_id: "",
            department_id: "",
            facultyId: false, // faculty dashboard: drill-down target
            search: "", // faculty dashboard: client-side name search
            refreshing: false, // silent reload in progress (dims the content)
            anim: "", // view-transition phase, e.g. "out-forward"
            selectedId: false, // faculty row that was clicked
        });
        this._loadSeq = 0;
    }

    // ── Loading ──────────────────────────────────────────────────────
    get filterPayload() {
        const s = this.state;
        return {
            date_from: s.date_from || false,
            date_to: s.date_to || false,
            class_id: s.class_id ? parseInt(s.class_id, 10) : false,
            program_id: s.program_id ? parseInt(s.program_id, 10) : false,
            department_id: s.department_id ? parseInt(s.department_id, 10) : false,
        };
    }

    /** Subclasses return the ORM promise that fetches their data. */
    fetchData() {
        throw new Error("fetchData() not implemented");
    }

    async load({ silent = false } = {}) {
        const seq = ++this._loadSeq;
        if (!silent) {
            this.state.loading = true;
        } else {
            this.state.refreshing = true;
        }
        try {
            const data = await this.fetchData();
            if (seq === this._loadSeq) {
                this.state.data = data;
            }
        } finally {
            if (seq === this._loadSeq) {
                this.state.loading = false;
                this.state.refreshing = false;
            }
        }
    }

    /** CSS classes for the dashboard body (loading dim + view transition). */
    get bodyClass() {
        return {
            o_ed_refreshing: this.state.refreshing,
            [`o_ed_${this.state.anim}`]: !!this.state.anim,
        };
    }

    // ── Filters ──────────────────────────────────────────────────────
    get hasActiveFilters() {
        const s = this.state;
        return !!(
            s.class_id ||
            s.program_id ||
            s.department_id ||
            s.period !== this.defaultPeriod
        );
    }

    onPeriodChange(ev) {
        const key = ev.target.value;
        this.state.period = key;
        if (key !== "custom") {
            Object.assign(this.state, periodRange(key));
            this.load({ silent: true });
        }
    }

    onDateChange(key, ev) {
        this.state[key] = ev.target.value || "";
        const s = this.state;
        if (s.date_from && s.date_to && s.date_from > s.date_to) {
            if (key === "date_from") {
                s.date_to = s.date_from;
            } else {
                s.date_from = s.date_to;
            }
        }
        this.load({ silent: true });
    }

    onFilterChange(key, ev) {
        this.state[key] = ev.target.value || "";
        this.afterFilterChange(key);
        this.load({ silent: true });
    }

    afterFilterChange() {}

    resetFilters() {
        Object.assign(this.state, {
            period: this.defaultPeriod,
            ...periodRange(this.defaultPeriod),
            class_id: "",
            program_id: "",
            department_id: "",
        });
        this.load({ silent: true });
    }

    // ── Formatting ───────────────────────────────────────────────────
    money(value) {
        const cur = this.state.data.currency;
        const num = new Intl.NumberFormat(undefined, {
            minimumFractionDigits: cur.decimals,
            maximumFractionDigits: cur.decimals,
        }).format(value || 0);
        return cur.position === "before" ? `${cur.symbol} ${num}` : `${num} ${cur.symbol}`;
    }

    compact(value) {
        if (!value) {
            return "";
        }
        const abs = Math.abs(value);
        if (abs >= 1e6) {
            return (value / 1e6).toFixed(1).replace(/\.0$/, "") + "M";
        }
        if (abs >= 1e3) {
            return (value / 1e3).toFixed(1).replace(/\.0$/, "") + "K";
        }
        return String(Math.round(value));
    }

    /** Template-safe id comparison (templates cannot call String()). */
    sameId(a, b) {
        return String(a) === String(b);
    }

    rateTone(rate) {
        if (rate === null || rate === undefined) {
            return "secondary";
        }
        if (rate >= 90) {
            return "success";
        }
        if (rate >= 75) {
            return "warning";
        }
        return "danger";
    }

    stateLabel(state) {
        return (
            {
                draft: "Draft",
                scheduled: "Scheduled",
                ongoing: "Ongoing",
                valuation: "Under valuation",
                result_published: "Result published",
            }[state] || state
        );
    }

    /** Human readable text for the active period (used in card sub-labels). */
    get periodLabel() {
        return this.periods.find((p) => p.key === this.state.period)?.label || "";
    }

    // ── Navigation ───────────────────────────────────────────────────
    openList(name, model, domain = [], context = {}) {
        this.action.doAction({
            type: "ir.actions.act_window",
            name,
            res_model: model,
            views: [
                [false, "list"],
                [false, "form"],
            ],
            domain,
            context,
            target: "current",
        });
    }

    openRecord(model, resId) {
        if (!resId) {
            return;
        }
        this.action.doAction({
            type: "ir.actions.act_window",
            res_model: model,
            res_id: resId,
            views: [[false, "form"]],
            target: "current",
        });
    }

    /** Domain pieces for the selected period on a date field. */
    dateDomain(field) {
        const domain = [];
        if (this.state.date_from) {
            domain.push([field, ">=", this.state.date_from]);
        }
        if (this.state.date_to) {
            domain.push([field, "<=", this.state.date_to]);
        }
        return domain;
    }

    openExams(name, states, classIds) {
        const domain = [["state", "in", states]];
        if (classIds) {
            domain.push(["class_ids", "in", classIds]);
        }
        this.openList(name, "education.exam", domain);
    }
}
