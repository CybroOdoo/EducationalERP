/** @odoo-module **/
/**
 * education_dashboard — Admin Dashboard (OWL client action)
 * Institution-wide students, attendance, admissions, fees, exams and
 * campus services with global period / program / class filters.
 */
import { registry } from "@web/core/registry";
import { onWillStart } from "@odoo/owl";
import { EduDashboardBase } from "@education_core/js/dashboard_common";
import { BarList, DonutChart, KpiCard, TrendBars } from "@education_core/js/dashboard_components";

export class EduAdminDashboard extends EduDashboardBase {
    static template = "education_core.AdminDashboard";
    static components = { KpiCard, DonutChart, TrendBars, BarList };

    setup() {
        super.setup();
        onWillStart(() => this.load());
    }

    fetchData() {
        return this.orm.call("education.dashboard", "get_admin_dashboard", [], {
            filters: this.filterPayload,
        });
    }

    // ── Filters ──────────────────────────────────────────────────────
    get classOptions() {
        const all = this.state.data?.class_options || [];
        const program = parseInt(this.state.program_id, 10);
        return program ? all.filter((c) => c.program_id === program) : all;
    }

    afterFilterChange(key) {
        if (key === "program_id" && this.state.class_id) {
            const ok = this.classOptions.some((c) => String(c.id) === String(this.state.class_id));
            if (!ok) {
                this.state.class_id = "";
            }
        }
    }

    // ── Scope helpers (class / program filter → list domains) ────────
    get scope() {
        return this.state.data.class_scope; // array of class ids, or null
    }

    scopeDomain(field) {
        return this.scope === null ? [] : [[field, "in", this.scope]];
    }

    get programDomain() {
        return this.state.program_id ? [["program_id", "=", parseInt(this.state.program_id, 10)]] : [];
    }

    // ── Chart data ───────────────────────────────────────────────────
    get attendanceSegments() {
        const a = this.state.data.attendance;
        const open = (key, label) => () =>
            this.openList(label, "education.attendance", [
                ...this.scopeDomain("class_id"),
                ...this.dateDomain("date"),
                ["state", "=", key],
            ]);
        return [
            { label: "Present", value: a.present, tone: "success", onClick: open("present", "Present") },
            { label: "Late", value: a.late, tone: "warning", onClick: open("late", "Late") },
            { label: "Absent", value: a.absent, tone: "danger", onClick: open("absent", "Absent") },
            { label: "Excused", value: a.excused, tone: "info", onClick: open("excused", "Excused") },
        ];
    }

    get attendanceTrendRows() {
        return this.state.data.attendance_trend.map((d) => ({
            label: d.label,
            value: d.value,
            tip: `${d.date}: ${d.value}% present · ${d.absent} absent`,
        }));
    }

    get feeTrendRows() {
        return this.state.data.fees.trend.map((t) => ({
            label: t.label,
            value: t.billed,
            value2: t.collected,
            tip: `Billed: ${this.money(t.billed)}`,
            tip2: `Collected: ${this.money(t.collected)}`,
        }));
    }

    get programRows() {
        return this.state.data.by_program.map((p) => ({
            label: p.label,
            value: p.value,
            onClick: () =>
                this.openList(`Students — ${p.label}`, "education.enrollment", [
                    ["state", "=", "active"],
                    ["program_id", "=", p.id || false],
                    ...this.scopeDomain("class_id"),
                ]),
        }));
    }

    get funnelRows() {
        return this.state.data.funnel.map((r) => ({
            label: r.label,
            value: r.value,
            onClick: () =>
                this.openList(`${r.label} applications`, "education.application", [
                    ["state", "=", r.key],
                    ...this.programDomain,
                    ...this.dateDomain("create_date"),
                ]),
        }));
    }

    get examTiles() {
        const c = this.state.data.exams.counts;
        const open = (name, states) => () => this.openExams(name, states, this.scope);
        return [
            { label: "Scheduled", value: c.scheduled, tone: "info", onClick: open("Scheduled Exams", ["scheduled"]) },
            { label: "Ongoing", value: c.ongoing, tone: "warning", onClick: open("Ongoing Exams", ["ongoing"]) },
            { label: "Under valuation", value: c.valuation, tone: "danger", onClick: open("Exams Under Valuation", ["valuation"]) },
            { label: "Results published", value: c.result_published, tone: "success", onClick: open("Published Exams", ["result_published"]) },
        ];
    }

    get attention() {
        const d = this.state.data;
        const items = [];
        if (d.kpis.pending_applications) {
            items.push({
                tone: "warning",
                icon: "fa-user-plus",
                text: `${d.kpis.pending_applications} admission application(s) to review`,
                click: () => this.onApplications(),
            });
        }
        if (d.fees.overdue_count) {
            items.push({
                tone: "danger",
                icon: "fa-exclamation-triangle",
                text: `${d.fees.overdue_count} overdue fee invoice(s) · ${this.money(d.fees.overdue_amount)}`,
                click: () => this.onFees("overdue"),
            });
        }
        if (d.unmarked.count) {
            items.push({
                tone: "warning",
                icon: "fa-calendar-check-o",
                text: `Attendance not marked today in ${d.unmarked.count} class(es)`,
                click: () => this.onUnmarked(),
            });
        }
        if (d.exams.enabled && d.exams.counts.valuation) {
            items.push({
                tone: "info",
                icon: "fa-pencil-square-o",
                text: `${d.exams.counts.valuation} exam(s) under valuation`,
                click: () => this.openExams("Exams Under Valuation", ["valuation"], this.scope),
            });
        }
        if (d.exams.enabled && d.exams.pending_reeval) {
            items.push({
                tone: "info",
                icon: "fa-refresh",
                text: `${d.exams.pending_reeval} re-evaluation request(s) pending`,
                click: () => this.onReevaluations(),
            });
        }
        const sch = d.services.scholarship;
        if (sch && sch.to_review) {
            items.push({
                tone: "secondary",
                icon: "fa-graduation-cap",
                text: `${sch.to_review} scholarship application(s) awaiting decision`,
                click: () => this.onScholarshipReview(),
            });
        }
        return items;
    }

    // ── KPI / drill-down handlers ────────────────────────────────────
    onStudents() {
        this.openList("Students", "education.enrollment", [
            ["state", "=", "active"],
            ...this.scopeDomain("class_id"),
        ]);
    }

    onFaculty() {
        this.action.doAction("education_core.hr_employee_action_faculty");
    }

    onClasses() {
        this.openList("Classes", "education.class", this.scopeDomain("id"));
    }

    onAttendance() {
        this.openList("Attendance", "education.attendance", [
            ...this.scopeDomain("class_id"),
            ...this.dateDomain("date"),
        ]);
    }

    onUnmarked() {
        this.openList("Classes without attendance today", "education.class", [
            ["id", "in", this.state.data.unmarked.ids],
        ]);
    }

    onApplications() {
        this.openList("Applications to review", "education.application", [
            ["state", "=", "submitted"],
            ...this.programDomain,
        ]);
    }

    onFees(kind) {
        const domain = [
            ["move_type", "=", "out_invoice"],
            ["enrollment_id", "!=", false],
            ["state", "=", "posted"],
            ["payment_state", "in", ["not_paid", "partial"]],
        ];
        if (this.scope !== null) {
            domain.push(["enrollment_id.class_id", "in", this.scope]);
        }
        if (kind === "overdue") {
            domain.push(["invoice_date_due", "<", new Date().toISOString().slice(0, 10)]);
        }
        this.openList(kind === "overdue" ? "Overdue Fee Invoices" : "Outstanding Fee Invoices", "account.move", domain, {
            default_move_type: "out_invoice",
        });
    }

    onPassRate() {
        this.openList("Published Results", "education.exam.result", [
            ["state", "=", "published"],
            ...this.scopeDomain("class_id"),
        ]);
    }

    onReevaluations() {
        this.openList("Pending Re-evaluations", "education.exam.reevaluation.request", [
            ["state", "=", "pending"],
            ...this.scopeDomain("result_id.class_id"),
        ]);
    }

    onScholarshipReview() {
        this.openList("Scholarship Applications", "education.scholarship.application", [
            ["state", "in", ["submitted", "review"]],
        ]);
    }

    // Campus services
    onHostel() {
        this.openList("Hostel Rooms", "education.hostel.room", []);
    }

    onTransport() {
        this.openList("Transport Assignments", "education.transport.assignment", [["state", "=", "active"]]);
    }

    onScholarships() {
        this.openList("Active Scholarships", "education.scholarship", [["state", "=", "active"]]);
    }
}

registry.category("actions").add("education_core.admin_dashboard", EduAdminDashboard);
