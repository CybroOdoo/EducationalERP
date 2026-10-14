/** @odoo-module **/
/**
 * education_dashboard — small reusable presentational components.
 */
import { Component, onMounted, onWillUnmount, onWillUpdateProps, useState } from "@odoo/owl";

const prefersReducedMotion = () =>
    !!(window.matchMedia && window.matchMedia("(prefers-reduced-motion: reduce)").matches);

/**
 * Split a display value like "85%", "120" or "$ 5,000.00" into an
 * animatable number and a formatter. Returns null for anything else
 * (e.g. "2/3"), which is then shown as is.
 */
function parseAnimatable(value) {
    if (typeof value === "number") {
        return { num: value, format: (n) => String(Math.round(n)) };
    }
    const m = /^(\D*?)(-?[\d,]*\.?\d+)(\D*)$/.exec(String(value).trim());
    if (!m) {
        return null;
    }
    const [, prefix, digits, suffix] = m;
    const decimals = digits.includes(".") ? digits.split(".")[1].length : 0;
    const grouped = digits.includes(",");
    return {
        num: parseFloat(digits.replace(/,/g, "")),
        format: (n) => {
            const txt = n.toLocaleString(undefined, {
                minimumFractionDigits: decimals,
                maximumFractionDigits: decimals,
                useGrouping: grouped,
            });
            return `${prefix}${txt}${suffix}`;
        },
    };
}

/** Clickable KPI card; numbers count up when the card appears / changes. */
export class KpiCard extends Component {
    static template = "education_core.KpiCard";
    static props = {
        icon: String,
        tone: { type: String, optional: true },
        value: [String, Number],
        label: String,
        sub: { type: String, optional: true },
        onClick: Function,
    };

    setup() {
        const parsed = parseAnimatable(this.props.value);
        this.state = useState({
            text: parsed && !prefersReducedMotion() ? parsed.format(0) : String(this.props.value),
        });
        this._from = 0;
        this._raf = null;
        onMounted(() => this.animateTo(this.props.value));
        onWillUpdateProps((next) => {
            if (next.value !== this.props.value) {
                this.animateTo(next.value);
            }
        });
        onWillUnmount(() => this._raf && cancelAnimationFrame(this._raf));
    }

    animateTo(value, duration = 750) {
        if (this._raf) {
            cancelAnimationFrame(this._raf);
        }
        const target = parseAnimatable(value);
        if (!target || prefersReducedMotion()) {
            this.state.text = String(value);
            return;
        }
        const from = this._from;
        const start = performance.now();
        const step = () => {
            const t = Math.min(1, (performance.now() - start) / duration);
            const eased = 1 - Math.pow(1 - t, 3); // ease-out cubic
            const current = from + (target.num - from) * eased;
            this._from = current;
            this.state.text = target.format(current);
            if (t < 1) {
                this._raf = requestAnimationFrame(step);
            } else {
                this._from = target.num;
                this.state.text = String(value);
                this._raf = null;
            }
        };
        this._raf = requestAnimationFrame(step);
    }
}

/** Donut chart with a clickable legend (pure SVG). */
export class DonutChart extends Component {
    static template = "education_core.DonutChart";
    static props = {
        segments: Array, // [{label, value, tone, onClick?}]
        centerValue: [String, Number],
        centerLabel: String,
        legendTitle: { type: String, optional: true },
    };

    get arcs() {
        const total = this.props.segments.reduce((t, s) => t + s.value, 0);
        let offset = 25;
        return this.props.segments
            .filter((s) => s.value && total)
            .map((s) => {
                const pct = (s.value * 100) / total;
                const arc = { tone: s.tone, dash: `${pct} ${100 - pct}`, offset };
                offset -= pct;
                return arc;
            });
    }
}

/** Vertical bars, one or two series (e.g. billed vs collected). */
export class TrendBars extends Component {
    static template = "education_core.TrendBars";
    static props = {
        rows: Array, // [{label, value, value2?, tip?, tip2?}]
        max: { type: Number, optional: true }, // fixed scale (e.g. 100 for %)
        unit: { type: String, optional: true },
        compact: { type: Boolean, optional: true },
        tone: { type: String, optional: true },
        tone2: { type: String, optional: true },
        onBarClick: { type: Function, optional: true },
    };

    get scale() {
        if (this.props.max) {
            return this.props.max;
        }
        return Math.max(
            1,
            ...this.props.rows.map((r) => Math.max(r.value || 0, r.value2 || 0))
        );
    }

    height(value) {
        return Math.round(((value || 0) * 100) / this.scale);
    }

    text(value) {
        if (!value) {
            return "";
        }
        let txt = String(value);
        if (this.props.compact) {
            const abs = Math.abs(value);
            if (abs >= 1e6) {
                txt = (value / 1e6).toFixed(1).replace(/\.0$/, "") + "M";
            } else if (abs >= 1e3) {
                txt = (value / 1e3).toFixed(1).replace(/\.0$/, "") + "K";
            } else {
                txt = String(Math.round(value));
            }
        }
        return txt + (this.props.unit || "");
    }
}

/** Horizontal bars with optional click-through. */
export class BarList extends Component {
    static template = "education_core.BarList";
    static props = {
        rows: Array, // [{label, value, sub?, onClick?}]
        tone: { type: String, optional: true },
    };

    get scaled() {
        const max = Math.max(1, ...this.props.rows.map((r) => r.value));
        return this.props.rows.map((r) => ({ ...r, pct: Math.round((r.value * 100) / max) }));
    }
}
