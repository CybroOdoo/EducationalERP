/** @odoo-module **/
/**
 * education_dashboard — Faculty Dashboard (OWL client action)
 *
 * Two views in one screen:
 *  - Admin view   : all faculty members, workload and attendance marking
 *                   (education admins). Click a faculty row to drill down.
 *  - Faculty view : one member's classes, today's periods, attendance, exams
 *                   (faculty users, or an admin after drilling down).
 */
import { registry } from "@web/core/registry";
import { onWillStart, useRef } from "@odoo/owl";
import { EduDashboardBase, sleep } from "@education_core/js/dashboard_common";
import { BarList, DonutChart, KpiCard, TrendBars } from "@education_core/js/dashboard_components";

export class EduFacultyDashboard extends EduDashboardBase {
    static template = "education_core.FacultyDashboard";
    static components = { KpiCard, DonutChart, TrendBars, BarList };

    setup() {
        super.setup();
        this.rootRef = useRef("root");
        onWillStart(() => this.load());
    }

    fetchData() {
        return this.orm.call("education.dashboard", "get_faculty_dashboard", [], {
            faculty_id: this.state.facultyId || false,
            filters: this.filterPayload,
        });
    }

    // ── Navigation between the two views (animated) ──────────────────
    /**
     * Slide the current view out, load the other one while it leaves, then
     * slide the new view in. ``direction`` is "forward" (drill down) or
     * "back" (return to the list).
     */
    async switchView(direction) {
        const seq = ++this._loadSeq;
        this.state.anim = `out-${direction}`;
        try {
            const [data] = await Promise.all([this.fetchData(), sleep(230)]);
            if (seq === this._loadSeq) {
                this.state.data = data;
                this.state.anim = `in-${direction}`;
                this.rootRef.el?.scrollTo?.({ top: 0, behavior: "smooth" });
            }
        } catch (error) {
            this.state.anim = "";
            throw error;
        } finally {
            if (seq === this._loadSeq) {
                this.state.selectedId = false;
            }
        }
    }

    openFaculty(id) {
        if (this.state.selectedId) {
            return; // a transition is already running
        }
        this.state.selectedId = id;
        this.state.facultyId = id;
        this.state.class_id = "";
        return this.switchView("forward");
    }

    backToAll() {
        this.state.facultyId = false;
        this.state.class_id = "";
        return this.switchView("back");
    }

    get initials() {
        const name = this.state.data?.faculty?.profile?.name || "";
        return name
            .split(/\s+/)
            .filter(Boolean)
            .slice(0, 2)
            .map((w) => w[0].toUpperCase())
            .join("");
    }

    // ── Admin view ───────────────────────────────────────────────────
    get admin() {
        return this.state.data.admin;
    }

    get filteredFaculties() {
        const q = (this.state.search || "").trim().toLowerCase();
        const rows = this.admin.faculties;
        if (!q) {
            return rows;
        }
        return rows.filter((r) =>
            [r.name, r.department, r.designation].some((v) => (v || "").toLowerCase().includes(q))
        );
    }

    get loadRows() {
        return [...this.admin.faculties]
            .sort((a, b) => b.weekly_periods - a.weekly_periods)
            .slice(0, 10)
            .map((r) => ({
                label: r.name,
                value: r.weekly_periods,
                onClick: () => this.openFaculty(r.id),
            }));
    }

    get markingSegments() {
        const m = this.admin.marking;
        return [
            { label: "Marked today", value: m.done, tone: "success" },
            {
                label: "Not marked yet",
                value: m.pending,
                tone: "danger",
                onClick: () => this.openClasses("Classes without attendance today", m.pending_ids),
            },
        ];
    }

    get adminAttention() {
        const a = this.admin;
        const items = [];
        if (a.marking.pending) {
            items.push({
                tone: "danger",
                icon: "fa-calendar-check-o",
                text: `${a.marking.pending} class(es) have no attendance marked today`,
                click: () => this.openClasses("Classes without attendance today", a.marking.pending_ids),
            });
        }
        if (a.kpis.no_class_teacher) {
            items.push({
                tone: "warning",
                icon: "fa-user-times",
                text: `${a.kpis.no_class_teacher} class(es) have no class teacher`,
                click: () => this.openClasses("Classes without class teacher", a.no_teacher_ids),
            });
        }
        if (a.exams.enabled && a.exams.valuation) {
            items.push({
                tone: "info",
                icon: "fa-pencil-square-o",
                text: `${a.exams.valuation} exam(s) waiting for valuation`,
                click: () => this.openExams("Exams Under Valuation", ["valuation"], a.scope_class_ids),
            });
        }
        if (a.exams.enabled && a.exams.pending_reeval) {
            items.push({
                tone: "info",
                icon: "fa-refresh",
                text: `${a.exams.pending_reeval} re-evaluation request(s) pending`,
                click: () => this.openReevaluations(a.scope_class_ids),
            });
        }
        return items;
    }

    // ── Faculty view ─────────────────────────────────────────────────
    get fac() {
        return this.state.data.faculty;
    }

    get attendanceSegments() {
        const a = this.fac.attendance;
        const open = (key, label) => () =>
            this.openList(label, "education.attendance", [
                ["class_id", "in", this.fac.class_ids],
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

    get trendRows() {
        return this.fac.attendance_trend.map((d) => ({
            label: d.label,
            value: d.value,
            tip: `${d.date}: ${d.value}% present · ${d.absent} absent`,
        }));
    }

    get weekRows() {
        return this.fac.week_load.map((w, i) => ({
            label: w.label,
            value: w.value,
            tip: `${w.value} period(s)`,
            today: String(i) === this.fac.weekday,
        }));
    }

    slotStatus(slot) {
        const now = new Date();
        const hours = now.getHours() + now.getMinutes() / 60;
        if (hours >= slot.end) {
            return "done";
        }
        if (hours >= slot.start) {
            return "now";
        }
        return "next";
    }

    classStatusLabel(status) {
        return { marked: "Marked", pending: "Pending", none: "No period today" }[status];
    }

    classStatusTone(status) {
        return { marked: "success", pending: "danger", none: "secondary" }[status];
    }

    get facultyAttention() {
        const f = this.fac;
        const items = [];
        if (f.kpis.pending_attendance) {
            items.push({
                tone: "danger",
                icon: "fa-calendar-check-o",
                text: `Attendance pending today for ${f.kpis.pending_attendance} class(es)`,
                click: () => this.openClasses("Attendance pending today", f.pending_class_ids),
            });
        }
        if (f.kpis.low_attendance) {
            items.push({
                tone: "warning",
                icon: "fa-user-times",
                text: `${f.kpis.low_attendance} student(s) below 75% attendance`,
                click: () => this.onLowAttendance(),
            });
        }
        if (f.exams.enabled && f.exams.valuation) {
            items.push({
                tone: "info",
                icon: "fa-pencil-square-o",
                text: `${f.exams.valuation} exam(s) waiting for your valuation`,
                click: () => this.openExams("Exams Under Valuation", ["valuation"], f.class_ids),
            });
        }
        if (f.exams.enabled && f.exams.pending_reeval) {
            items.push({
                tone: "info",
                icon: "fa-refresh",
                text: `${f.exams.pending_reeval} re-evaluation request(s) pending`,
                click: () => this.openReevaluations(f.class_ids),
            });
        }
        return items;
    }

    // ── Drill-down handlers ──────────────────────────────────────────
    openClasses(name, ids) {
        this.openList(name, "education.class", [["id", "in", ids]]);
    }

    openReevaluations(classIds) {
        this.openList("Pending Re-evaluations", "education.exam.reevaluation.request", [
            ["state", "=", "pending"],
            ["result_id.class_id", "in", classIds],
        ]);
    }

    onLowAttendance() {
        this.openList("Students below 75% attendance", "education.enrollment", [
            ["id", "in", this.fac.low_student_ids],
        ]);
    }

    onFacultyList() {
        const domain = [["is_faculty", "=", true]];
        if (this.state.department_id) {
            domain.push(["edu_department_id", "=", parseInt(this.state.department_id, 10)]);
        }
        this.openList("Faculty", "hr.employee", domain);
    }

    onAdminStudents() {
        this.openList("Students", "education.enrollment", [
            ["state", "=", "active"],
            ["class_id", "in", this.admin.scope_class_ids],
        ]);
    }

    onAdminAttendance() {
        this.openList("Attendance", "education.attendance", [
            ["class_id", "in", this.admin.scope_class_ids],
            ...this.dateDomain("date"),
        ]);
    }

    onAdminPeriods() {
        this.openList("Timetable Periods", "education.timetable.slot", [
            ["timetable_id.active", "=", true],
            ["class_id", "in", this.admin.scope_class_ids],
        ]);
    }

    onMyStudents() {
        this.openList("My Students", "education.enrollment", [
            ["state", "=", "active"],
            ["class_id", "in", this.fac.class_ids],
        ]);
    }

    onMyAttendance() {
        this.openList("Attendance", "education.attendance", [
            ["class_id", "in", this.fac.class_ids],
            ...this.dateDomain("date"),
        ]);
    }

    onTodayPeriods() {
        this.openList("Today's Periods", "education.timetable.slot", [
            ["teacher_id", "=", this.fac.profile.id],
            ["timetable_id.active", "=", true],
            ["weekday", "=", this.fac.weekday],
        ]);
    }

    openClassRoster(classId) {
        this.openList("Class Roster", "education.enrollment", [
            ["class_id", "=", classId],
            ["state", "=", "active"],
        ]);
    }

    openClassAttendance(classId) {
        this.openList("Class Attendance", "education.attendance", [
            ["class_id", "=", classId],
            ...this.dateDomain("date"),
        ]);
    }
}

registry.category("actions").add("education_core.faculty_dashboard", EduFacultyDashboard);
