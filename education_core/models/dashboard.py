# -*- coding: utf-8 -*-
###############################################################################
#
#    Cybrosys Technologies Pvt. Ltd.
#
#    Copyright (C) 2026-TODAY Cybrosys Technologies(
#    <https://www.cybrosys.com>).
#    Author: Cybrosys Techno Solutions(<https://www.cybrosys.com>)
#
#    This program is under the terms of the Odoo Proprietary License v1.0 (
#    OPL-1)
#    It is forbidden to publish, distribute, sublicense, or sell copies of the
#    Software or modified copies of the Software.
#
#    THE SOFTWARE IS PROVIDED “AS IS”, WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
#    IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
#    FITNESS FOR A PARTICULAR PURPOSE AND NON INFRINGEMENT. IN NO EVENT SHALL
#    THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM,DAMAGES OR OTHER
#    LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE,ARISING
#    FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER
#    DEALINGS IN THE SOFTWARE.
#
"""
Education ERP — Dashboard Data Provider
=======================================
AbstractModel exposing @api.model methods consumed by the Admin and Faculty
OWL dashboards. Everything is read with the current user's rights (no sudo)
and returns plain dicts, so the front-end stays dependency-free.

Optional integrations (exams, hostel, transport, scholarships) are only
queried when their models are installed.
"""

from collections import defaultdict
from datetime import datetime, timedelta

from dateutil.relativedelta import relativedelta

from odoo import api, fields, models

LOW_ATTENDANCE_THRESHOLD = 75.0   # % below which a student is flagged
LOW_ATTENDANCE_MIN_RECORDS = 3    # need at least this many records to flag
TREND_DAYS = 14
WEEKDAYS = ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat"]


def float_to_time(value):
    """Convert float hours to 12-hour formatted time ('7:30 AM')."""
    if value is False or value is None:
        return ""
    hours = int(value)
    minutes = round((value - hours) * 60)
    time_value = datetime(2000, 1, 1, hours % 24, 0) + timedelta(
        minutes=minutes)
    return time_value.strftime("%I:%M %p").lstrip("0")


def float_to_time_string(time_float):
    """Convert a float duration to '1 Hour 30 Minutes'."""
    hours = int(time_float)
    minutes = int(round((time_float - hours) * 60))
    parts = []
    if hours > 0:
        parts.append(f"{hours} {'Hour' if hours == 1 else 'Hours'}")
    if minutes > 0:
        parts.append(f"{minutes} {'Minute' if minutes == 1 else 'Minutes'}")
    return " ".join(parts) or "0 Hours"


class EducationDashboard(models.AbstractModel):
    """Education Dashboard Data Provider."""

    _name = "education.dashboard"
    _description = "Education Dashboard Data Provider"

    # ══════════════════════════════════════════════════════════════════
    # Admin dashboard
    # ══════════════════════════════════════════════════════════════════
    @api.model
    def get_admin_dashboard(self, filters=None):
        """Institution-wide figures for the Admin Dashboard.

        ``filters``: {"date_from", "date_to", "program_id", "class_id"}
        * program / class: students, attendance, fees, exams, results
        * date range: attendance, admission funnel, fee trend end-point
        """
        f = self._clean_filters(filters)
        today = fields.Date.context_today(self)
        classes = self._filtered_classes(f)
        class_ids = classes.ids if self._is_class_filtered(f) else None

        enrol_domain = [("state", "=", "active")] + self._in(
            "class_id", class_ids)
        att_domain = self._in("class_id", class_ids) + self._date_domain(
            "date", f)
        Enrollment = self.env["education.enrollment"]

        attendance = self._attendance_breakdown(att_domain)
        unmarked = self._unmarked_classes(today, class_ids)
        fees = self._fee_data(class_ids, today)
        exams = self._exam_data(class_ids, today)
        applications = self._application_data(f)

        response = {
            "currency": self._currency(),
            "program_options": [
                {"id": p.id, "name": p.display_name}
                for p in self.env["education.program"].search([])],
            "class_options": [
                {"id": c.id, "name": c.display_name,
                 "program_id": c.program_id.id}
                for c in self.env["education.class"].search([])],
            "date_from": fields.Date.to_string(f["date_from"]) or False,
            "date_to": fields.Date.to_string(f["date_to"]) or False,
            "class_scope": class_ids,
            "kpis": {
                "students": Enrollment.search_count(enrol_domain),
                "faculty": self._faculty_count(class_ids),
                "classes": len(classes) if class_ids is not None
                else self.env["education.class"].search_count([]),
                "programs": self.env["education.program"].search_count([]),
                "attendance_rate": attendance["rate"],
                "pending_applications": applications["pending"],
                "fees_outstanding": fees["outstanding"],
                "unmarked_classes": unmarked["count"],
            },
            "attendance": attendance,
            "attendance_trend": self._attendance_trend(
                self._in("class_id", class_ids), f, today),
            "by_program": self._students_by_program(enrol_domain),
            "funnel": applications["funnel"],
            "recent_applications": applications["recent"],
            "unmarked": unmarked,
            "fees": fees,
            "classes_attention": self._classes_attention(
                classes if class_ids is not None
                else self.env["education.class"].search([]), att_domain),
            "exams": exams,
            "services": self._campus_services(),
        }
        return response

    # ── Admin helpers ─────────────────────────────────────────────────
    @api.model
    def _application_data(self, f):
        """Admission funnel, pending count and latest pending applications.

        The funnel follows the program filter and the period (application
        creation date); ``pending`` follows the program filter only.

        :param dict f: cleaned filters (see ``_clean_filters``).
        :rtype: dict
        """
        Application = self.env["education.application"]
        base = []
        if f["program_id"]:
            base.append(("program_id", "=", f["program_id"]))
        period = []
        if f["date_from"]:
            period.append(("create_date", ">=", f"{f['date_from']} 00:00:00"))
        if f["date_to"]:
            period.append(("create_date", "<=", f"{f['date_to']} 23:59:59"))
        counts = dict(Application._read_group(
            base + period, ["state"], ["__count"]))
        pending_domain = base + [("state", "=", "submitted")]
        recent = Application.search(pending_domain, limit=6, order="id desc")
        return {
            "pending": Application.search_count(pending_domain),
            "funnel": [
                {"key": key, "label": label, "value": counts.get(key, 0)}
                for key, label in [("draft", "Draft"),
                                   ("submitted", "Submitted"),
                                   ("approved", "Approved"),
                                   ("rejected", "Rejected")]],
            "recent": [{
                "id": app.id,
                "name": app.display_name,
                "program": app.program_id.name or "",
                "date": fields.Date.to_string(app.create_date.date())
                if app.create_date else "",
            } for app in recent],
        }

    @api.model
    def _students_by_program(self, enrol_domain):
        """Top programs (max. 8) by number of students.

        ``enrol_domain`` is the enrollment domain to count. Students without a
        program are grouped as 'Unassigned'.
        """
        rows = self.env["education.enrollment"]._read_group(
            enrol_domain, ["program_id"], ["__count"])
        result = [{
            "id": program.id,
            "label": program.name if program else "Unassigned",
            "value": count,
        } for program, count in rows]
        result.sort(key=lambda r: r["value"], reverse=True)
        return result[:8]

    @api.model
    def _classes_attention(self, classes, att_domain, limit=6):
        """Classes with the lowest attendance rate in the selected period."""
        if not classes:
            return []
        Att = self.env["education.attendance"]
        domain = [d for d in att_domain if d[0] != "class_id"] + [
            ("class_id", "in", classes.ids)]
        per_class = defaultdict(lambda: defaultdict(int))
        for klass, state, count in Att._read_group(
                domain, ["class_id", "state"], ["__count"]):
            per_class[klass.id][state] += count
        students = dict(self.env["education.enrollment"]._read_group(
            [("state", "=", "active"), ("class_id", "in", classes.ids)],
            ["class_id"], ["__count"]))
        rows = []
        for klass in classes:
            stats = per_class.get(klass.id)
            if not stats:
                continue
            total = sum(stats.values())
            rows.append({
                "id": klass.id,
                "name": klass.display_name,
                "teacher": klass.class_teacher_id.name or "",
                "students": students.get(klass, 0),
                "absent": stats.get("absent", 0),
                "rate": round(
                    (stats.get("present", 0) + stats.get("late", 0))
                    * 100.0 / total, 1),
            })
        rows.sort(key=lambda r: r["rate"])
        return rows[:limit]

    @api.model
    def _fee_data(self, class_ids, today):
        """Student fee invoices: outstanding, overdue, collected, trend."""
        Move = self.env["account.move"]
        base = [("move_type", "=", "out_invoice"),
                ("enrollment_id", "!=", False),
                ("state", "=", "posted")]
        if class_ids is not None:
            base.append(("enrollment_id.class_id", "in", class_ids))
        unpaid = base + [("payment_state", "in", ("not_paid", "partial"))]

        def _sum(domain, field):
            """Return ``(sum of field, record count)`` for ``domain``."""
            rows = Move._read_group(domain, [], [f"{field}:sum", "__count"])
            return (rows[0][0] or 0.0, rows[0][1]) if rows else (0.0, 0)

        outstanding, unpaid_count = _sum(unpaid, "amount_residual_signed")
        overdue_domain = unpaid + [("invoice_date_due", "<", today)]
        overdue_amount, overdue_count = _sum(
            overdue_domain, "amount_residual_signed")

        month_start = today.replace(day=1)
        trend = []
        for offset in range(5, -1, -1):
            start = month_start - relativedelta(months=offset)
            end = start + relativedelta(months=1)
            window = base + [("invoice_date", ">=", start),
                             ("invoice_date", "<", end)]
            billed, _n = _sum(window, "amount_total_signed")
            pending, _n = _sum(window, "amount_residual_signed")
            trend.append({"label": start.strftime("%b"), "billed": billed,
                          "collected": billed - pending})
        this_month = trend[-1]
        overdue_rows = Move.search(
            overdue_domain, order="invoice_date_due, id", limit=6)
        return {
            "outstanding": outstanding,
            "unpaid_count": unpaid_count,
            "overdue_amount": overdue_amount,
            "overdue_count": overdue_count,
            "collected_month": this_month["collected"],
            "billed_month": this_month["billed"],
            "collection_rate": round(
                this_month["collected"] * 100.0 / this_month["billed"], 1
            ) if this_month["billed"] else 0.0,
            "trend": trend,
            "overdue": [{
                "id": inv.id,
                "student": inv.enrollment_id.student_name
                or inv.partner_id.name or "",
                "class": inv.enrollment_id.class_id.display_name or "",
                "days": (today - inv.invoice_date_due).days,
                "amount": inv.amount_residual_signed,
            } for inv in overdue_rows],
        }

    @api.model
    def _exam_data(self, class_ids, today):
        """Exam status counts, pass rate and upcoming exams.

        Returns ``{'enabled': False}`` when the exam app is not installed.
        ``class_ids`` limits the figures to those classes (``None`` = all
        classes).
        """
        if "education.exam" not in self.env:
            return {"enabled": False}
        Exam = self.env["education.exam"]
        exam_domain = self._in("class_ids", class_ids)
        counts = dict(Exam._read_group(exam_domain, ["state"], ["__count"]))
        result_domain = [("state", "=", "published")] + self._in(
            "class_id", class_ids)
        outcome = dict(self.env["education.exam.result"]._read_group(
            result_domain, ["pass_fail"], ["__count"]))
        passed, failed = outcome.get("pass", 0), outcome.get("fail", 0)
        pending_reeval = 0
        if "education.exam.reevaluation.request" in self.env:
            pending_reeval = self.env[
                "education.exam.reevaluation.request"].search_count(
                [("state", "=", "pending")] + self._in(
                    "result_id.class_id", class_ids))
        upcoming = Exam.search(
            [("state", "in", ("scheduled", "ongoing"))] + exam_domain,
            order="date_from, id", limit=5)
        return {
            "enabled": True,
            "counts": {k: counts.get(k, 0) for k in (
                "scheduled", "ongoing", "valuation", "result_published")},
            "passed": passed,
            "failed": failed,
            "pass_rate": round(passed * 100.0 / (passed + failed), 1)
            if (passed + failed) else 0.0,
            "pending_reeval": pending_reeval,
            "upcoming": [{
                "id": exam.id,
                "name": exam.name,
                "state": exam.state,
                "date": fields.Date.to_string(exam.date_from) or "",
                "classes": ", ".join(
                    exam.class_ids[:2].mapped("display_name"))
                + (" +%d" % (len(exam.class_ids) - 2)
                   if len(exam.class_ids) > 2 else ""),
            } for exam in upcoming],
        }

    @api.model
    def _campus_services(self):
        """Hostel / transport / scholarship summary (installed apps only)."""
        services = {}
        if "education.hostel.room" in self.env:
            rooms = self.env["education.hostel.room"].search_read(
                [], ["capacity", "occupied_beds", "available_beds", "state"])
            usable = [r for r in rooms if r["state"] != "maintenance"]
            beds = sum(r["capacity"] for r in usable)
            occupied = sum(r["occupied_beds"] for r in usable)
            services["hostel"] = {
                "rooms": len(rooms),
                "beds": beds,
                "occupied": occupied,
                "free": sum(r["available_beds"] for r in usable),
                "occupancy": round(occupied * 100.0 / beds, 1)
                if beds else 0.0,
            }
        if "education.transport.assignment" in self.env:
            vehicles = 0
            if "fleet.vehicle" in self.env:
                vehicles = self.env["fleet.vehicle"].search_count(
                    [("is_school_vehicle", "=", True)])
            services["transport"] = {
                "students": self.env[
                    "education.transport.assignment"].search_count(
                    [("state", "=", "active")]),
                "routes": self.env[
                    "education.transport.route"].search_count([]),
                "vehicles": vehicles,
            }
        if "education.scholarship" in self.env:
            Application = self.env["education.scholarship.application"]
            services["scholarship"] = {
                "active": self.env["education.scholarship"].search_count(
                    [("state", "=", "active")]),
                "to_review": Application.search_count(
                    [("state", "in", ("submitted", "review"))]),
                "approved": Application.search_count(
                    [("state", "=", "approved")]),
            }
        return services

    # ══════════════════════════════════════════════════════════════════
    # Faculty dashboard (admin view + faculty view)
    # ══════════════════════════════════════════════════════════════════
    @api.model
    def get_faculty_dashboard(self, faculty_id=None, filters=None):
        """Faculty dashboard data.

        * Education admins without ``faculty_id``  → *admin view*: every
          faculty member's workload and attendance-marking status.
        * Education admins with ``faculty_id``     → *faculty view* of that
          member (drill-down from the admin view).
        * Other users                              → *faculty view* of the
          faculty member linked to the logged-in user.
        """
        f = self._clean_filters(filters)
        is_admin = self.env.user.has_group(
            "education_core.group_education_admin")
        Employee = self.env["hr.employee"]
        base = {
            "is_admin": is_admin,
            "currency": self._currency(),
            "department_options": [
                {"id": d.id, "name": d.display_name}
                for d in self.env["education.department"].search([])],
        }
        if is_admin and not faculty_id:
            return {**base, "mode": "admin",
                    "class_options": self._class_options(),
                    "admin": self._faculty_admin_view(f), "faculty": False}

        if is_admin:
            faculty = Employee.search([("id", "=", int(faculty_id)),
                                       ("is_faculty", "=", True)], limit=1)
        else:
            faculty = Employee.search([("is_faculty", "=", True),
                                       ("user_id", "=", self.env.user.id)],
                                      limit=1)
        if not faculty:
            return {**base, "mode": "none", "class_options": [],
                    "admin": False, "faculty": False}
        _slots, own_classes = self._faculty_classes(faculty)
        return {**base, "mode": "faculty",
                "class_options": [
                    {"id": c.id, "name": c.display_name,
                     "program_id": c.program_id.id} for c in own_classes],
                "admin": False,
                "faculty": self._faculty_view(faculty, f)}

    # ── Faculty: admin view ───────────────────────────────────────────
    @api.model
    def _faculty_admin_view(self, f):
        """Data of the *admin view* of the faculty dashboard.

        Builds the KPI cards, the attendance marking status of today's
        classes, the exam alerts and one row per faculty member (classes,
        students, subjects, weekly and today's periods, attendance rate).
        Honours the department, class and period filters.

        :param dict f: cleaned filters (see ``_clean_filters``).
        :rtype: dict
        """
        today = fields.Date.context_today(self)
        Slot = self.env["education.timetable.slot"]
        Class = self.env["education.class"]
        Enrollment = self.env["education.enrollment"]
        Att = self.env["education.attendance"]

        fac_domain = [("is_faculty", "=", True)]
        if f["department_id"]:
            fac_domain.append(("edu_department_id", "=", f["department_id"]))
        faculties = self.env["hr.employee"].search(fac_domain, order="name")

        slots = Slot.search([("timetable_id.active", "=", True)])
        weekday = str(today.weekday())
        slots_by_teacher = defaultdict(lambda: Slot)
        for slot in slots:
            if slot.teacher_id:
                slots_by_teacher[slot.teacher_id.id] |= slot

        all_classes = Class.search([])
        teacher_classes = defaultdict(set)
        for slot in slots:
            if slot.teacher_id and slot.class_id:
                teacher_classes[slot.teacher_id.id].add(slot.class_id.id)
        for klass in all_classes:
            if klass.class_teacher_id:
                teacher_classes[klass.class_teacher_id.id].add(klass.id)

        class_filter = f["class_id"]
        scope = all_classes.filtered(
            lambda c: not class_filter or c.id == class_filter)
        students = dict(Enrollment._read_group(
            [("state", "=", "active"), ("class_id", "in", scope.ids)],
            ["class_id"], ["__count"]))
        marked_today = {
            klass.id for klass, _n in Att._read_group(
                [("date", "=", today), ("class_id", "in", scope.ids)],
                ["class_id"], ["__count"])}
        att_domain = [("class_id", "in", scope.ids)] + self._date_domain(
            "date", f)
        per_class = defaultdict(lambda: defaultdict(int))
        for klass, state, count in Att._read_group(
                att_domain, ["class_id", "state"], ["__count"]):
            per_class[klass.id][state] += count

        today_class_ids = set(slots.filtered(
            lambda s: s.weekday == weekday).mapped("class_id").ids)
        unmarked_ids = sorted(
            (today_class_ids & set(scope.ids)) - marked_today)

        rows = []
        for fac in faculties:
            fac_class_ids = (
                teacher_classes.get(fac.id, set()) & set(scope.ids))
            fac_slots = slots_by_teacher.get(fac.id, Slot)
            if class_filter:
                fac_slots = fac_slots.filtered(
                    lambda s: s.class_id.id == class_filter)
                if not fac_class_ids:
                    continue
            today_slots = fac_slots.filtered(lambda s: s.weekday == weekday)
            today_classes = set(today_slots.mapped("class_id").ids)
            present = total = 0
            for cid in fac_class_ids:
                stats = per_class.get(cid, {})
                total += sum(stats.values())
                present += stats.get("present", 0) + stats.get("late", 0)
            rows.append({
                "id": fac.id,
                "name": fac.name,
                "designation": fac.designation or "",
                "department": fac.edu_department_id.name or "",
                "classes": len(fac_class_ids),
                "students": sum(students.get(Class.browse(cid), 0)
                                for cid in fac_class_ids),
                "subjects": len(set(fac_slots.mapped("subject_id").ids)),
                "weekly_periods": len(fac_slots),
                "today_periods": len(today_slots),
                "today_pending": len(today_classes - marked_today),
                "attendance_rate": round(present * 100.0 / total, 1)
                if total else None,
            })

        attendance = self._attendance_breakdown(att_domain)
        exam_domain = [("class_ids", "in", scope.ids)]
        exams = {"enabled": False}
        if "education.exam" in self.env:
            Exam = self.env["education.exam"]
            counts = dict(Exam._read_group(
                exam_domain, ["state"], ["__count"]))
            valuation = Exam.search(
                [("state", "=", "valuation")] + exam_domain,
                order="date_from, id", limit=5)
            pending_reeval = 0
            if "education.exam.reevaluation.request" in self.env:
                pending_reeval = self.env[
                    "education.exam.reevaluation.request"].search_count(
                    [("state", "=", "pending"),
                     ("result_id.class_id", "in", scope.ids)])
            exams = {
                "enabled": True,
                "upcoming": counts.get("scheduled", 0),
                "ongoing": counts.get("ongoing", 0),
                "valuation": counts.get("valuation", 0),
                "pending_reeval": pending_reeval,
                "valuation_list": [{
                    "id": exam.id,
                    "name": exam.name,
                    "date": fields.Date.to_string(exam.date_from) or "",
                    "classes": ", ".join(
                        exam.class_ids[:2].mapped("display_name")),
                } for exam in valuation],
            }

        no_teacher = scope.filtered(lambda c: not c.class_teacher_id)
        return {
            "weekday": weekday,
            "faculties": rows,
            "kpis": {
                "faculty": len(rows),
                "students": sum(students.values()),
                "attendance_rate": attendance["rate"],
                "pending_classes": len(unmarked_ids),
                "no_class_teacher": len(no_teacher),
                "upcoming_exams": exams.get("upcoming", 0),
                "under_valuation": exams.get("valuation", 0),
                "weekly_periods": sum(r["weekly_periods"] for r in rows),
            },
            "attendance": attendance,
            "marking": {
                "pending": len(unmarked_ids),
                "done": len(today_class_ids & set(scope.ids) & marked_today),
                "pending_ids": unmarked_ids,
            },
            "no_teacher_ids": no_teacher.ids,
            "scope_class_ids": scope.ids,
            "exams": exams,
        }

    # ── Faculty: faculty view ─────────────────────────────────────────
    @api.model
    def _faculty_classes(self, faculty):
        """Return (timetable slots, classes) handled by a faculty member."""
        Slot = self.env["education.timetable.slot"]
        my_slots = Slot.search([("teacher_id", "=", faculty.id),
                                ("timetable_id.active", "=", True)])
        my_classes = self.env["education.class"].search([
            "|",
            ("class_teacher_id", "=", faculty.id),
            ("id", "in", my_slots.mapped("class_id").ids),
        ])
        return my_slots, my_classes

    @api.model
    def _faculty_view(self, faculty, f):
        """Data of the *faculty view* for one faculty member.

        Classes, students, today's schedule, attendance (rate, daily trend,
        students with low attendance), weekly load and exams of ``faculty``.
        Honours the class and period filters.

        :param faculty: ``hr.employee`` record of the faculty member.
        :param dict f: cleaned filters (see ``_clean_filters``).
        :rtype: dict
        """
        today = fields.Date.context_today(self)
        weekday = str(today.weekday())
        Enrollment = self.env["education.enrollment"]
        Att = self.env["education.attendance"]

        my_slots, my_classes = self._faculty_classes(faculty)
        if f["class_id"]:
            my_classes = my_classes.filtered(lambda c: c.id == f["class_id"])
            my_slots = my_slots.filtered(
                lambda s: s.class_id.id == f["class_id"])
        class_ids = my_classes.ids
        today_slots = my_slots.filtered(
            lambda s: s.weekday == weekday).sorted("start_time")

        students = dict(Enrollment._read_group(
            [("state", "=", "active"), ("class_id", "in", class_ids)],
            ["class_id"], ["__count"]))
        marked_today = {
            klass.id for klass, _n in Att._read_group(
                [("date", "=", today), ("class_id", "in", class_ids)],
                ["class_id"], ["__count"])}
        att_domain = [("class_id", "in", class_ids)] + self._date_domain(
            "date", f)
        per_class = defaultdict(lambda: defaultdict(int))
        for klass, state, count in Att._read_group(
                att_domain, ["class_id", "state"], ["__count"]):
            per_class[klass.id][state] += count

        today_class_ids = set(today_slots.mapped("class_id").ids)
        classes = []
        for klass in my_classes:
            stats = per_class.get(klass.id, {})
            total = sum(stats.values())
            if klass.id in today_class_ids:
                status = "marked" if klass.id in marked_today else "pending"
            else:
                status = "none"
            classes.append({
                "id": klass.id,
                "name": klass.display_name,
                "is_class_teacher": klass.class_teacher_id == faculty,
                "students": students.get(klass, 0),
                "today": status,
                "rate": round((stats.get("present", 0)
                               + stats.get("late", 0)) * 100.0 / total, 1)
                if total else None,
            })
        pending_ids = sorted(today_class_ids - marked_today)

        attendance = self._attendance_breakdown(att_domain)
        low_students = self._low_attendance_students(att_domain)
        subjects = sorted({
            f"{s.subject_id.name} / {s.subject_id.code}"
            if s.subject_id.code else s.subject_id.name
            for s in my_slots if s.subject_id})
        total_hours = sum(
            s.end_time - s.start_time for s in today_slots
            if s.start_time is not False and s.end_time is not False)
        week = [0] * len(WEEKDAYS)
        for slot in my_slots:
            if slot.weekday and slot.weekday.isdigit() and int(
                    slot.weekday) < len(WEEKDAYS):
                week[int(slot.weekday)] += 1

        exams = self._faculty_exams(my_classes)
        return {
            "profile": {
                "id": faculty.id,
                "name": faculty.name,
                "designation": faculty.designation or "",
                "department": faculty.edu_department_id.name or "",
            },
            "weekday": weekday,
            "kpis": {
                "classes": len(my_classes),
                "students": sum(students.values()),
                "today_periods": len(today_slots),
                "pending_attendance": len(pending_ids),
                "attendance_rate": attendance["rate"],
                "low_attendance": len(low_students["all"]),
                "upcoming_exams": exams.get("upcoming", 0),
                "under_valuation": exams.get("valuation", 0),
            },
            "class_ids": class_ids,
            "pending_class_ids": pending_ids,
            "low_student_ids": low_students["all"],
            "classes": classes,
            "subjects": subjects,
            "today_schedule": [{
                "id": slot.id,
                "period": slot.period_no,
                "start": slot.start_time,
                "end": slot.end_time,
                "start_label": float_to_time(slot.start_time),
                "end_label": float_to_time(slot.end_time),
                "subject": slot.subject_id.name or "",
                "class_name": slot.class_id.display_name or "",
                "class_id": slot.class_id.id,
                "room": slot.classroom_id.display_name or "",
                "attendance": "marked" if slot.class_id.id in marked_today
                else "pending",
            } for slot in today_slots],
            "work_hours_today": float_to_time_string(total_hours),
            "week_load": [{"label": label, "value": week[i]}
                          for i, label in enumerate(WEEKDAYS)],
            "attendance": attendance,
            "attendance_trend": self._attendance_trend(
                [("class_id", "in", class_ids)], f, today),
            "low_students": low_students["rows"],
            "exams": exams,
        }

    @api.model
    def _faculty_exams(self, my_classes):
        """Exam counts and upcoming / valuation lists for some classes.

        Returns zero counts when the exam app is not installed or the faculty
        member has no class.
        """
        if "education.exam" not in self.env or not my_classes:
            return {"enabled": "education.exam" in self.env,
                    "upcoming": 0, "valuation": 0, "pending_reeval": 0,
                    "upcoming_list": [], "valuation_list": []}
        Exam = self.env["education.exam"]
        base = [("class_ids", "in", my_classes.ids)]
        counts = dict(Exam._read_group(base, ["state"], ["__count"]))
        upcoming = Exam.search(
            [("state", "in", ("scheduled", "ongoing"))] + base,
            order="date_from, id", limit=6)
        valuation = Exam.search(
            [("state", "=", "valuation")] + base,
            order="date_from, id", limit=6)
        pending_reeval = 0
        if "education.exam.reevaluation.request" in self.env:
            pending_reeval = self.env[
                "education.exam.reevaluation.request"].search_count(
                [("state", "=", "pending"),
                 ("result_id.class_id", "in", my_classes.ids)])

        def _rows(exams):
            """One row per paper of the exams, sorted by date (max. 6)."""
            rows = []
            for exam in exams:
                mine = exam.class_ids & my_classes
                for line in exam.subject_line_ids:
                    rows.append({
                        "id": exam.id,
                        "name": exam.name or "",
                        "state": exam.state,
                        "subject": line.subject_id.name or "",
                        "classes": ", ".join(mine.mapped("display_name")),
                        "room": line.classroom_id.display_name or "",
                        "date": fields.Date.to_string(line.exam_date)
                        if line.exam_date else "",
                        "time": float_to_time(line.exam_time),
                    })
            rows.sort(key=lambda r: (r["date"], r["time"]))
            return rows[:6]

        return {
            "enabled": True,
            "upcoming": counts.get("scheduled", 0),
            "ongoing": counts.get("ongoing", 0),
            "valuation": counts.get("valuation", 0),
            "pending_reeval": pending_reeval,
            "upcoming_list": _rows(upcoming),
            "valuation_list": [{
                "id": exam.id,
                "name": exam.name or "",
                "classes": ", ".join(
                    (exam.class_ids & my_classes).mapped("display_name")),
                "date": fields.Date.to_string(exam.date_from) or "",
            } for exam in valuation],
        }

    @api.model
    def _low_attendance_students(self, att_domain, limit=8):
        """Students whose attendance rate is below the threshold.

        A student needs at least ``LOW_ATTENDANCE_MIN_RECORDS`` records to be
        flagged. Returns the ids of every flagged student and the ``limit``
        worst rows.
        """
        per_student = defaultdict(lambda: defaultdict(int))
        for enrol, state, count in self.env[
                "education.attendance"]._read_group(
                att_domain, ["enrollment_id", "state"], ["__count"]):
            per_student[enrol][state] += count
        flagged = []
        for enrol, stats in per_student.items():
            total = sum(stats.values())
            if total < LOW_ATTENDANCE_MIN_RECORDS:
                continue
            rate = (stats.get("present", 0) + stats.get("late", 0)) \
                * 100.0 / total
            if rate < LOW_ATTENDANCE_THRESHOLD:
                flagged.append((rate, enrol, stats))
        flagged.sort(key=lambda r: r[0])
        return {
            "all": [enrol.id for _r, enrol, _s in flagged],
            "rows": [{
                "id": enrol.id,
                "student": enrol.student_name or "",
                "class": enrol.class_id.display_name or "",
                "rate": round(rate, 1),
                "absent": stats.get("absent", 0),
                "total": sum(stats.values()),
            } for rate, enrol, stats in flagged[:limit]],
        }

    # ══════════════════════════════════════════════════════════════════
    # Shared helpers
    # ══════════════════════════════════════════════════════════════════
    @api.model
    def _clean_filters(self, filters):
        """Sanitise the filters sent by the client."""
        filters = filters or {}

        def _to_date(value):
            """Convert ``value`` to a date, ``False`` if invalid."""
            try:
                return fields.Date.to_date(value) if value else False
            except (ValueError, TypeError):
                return False

        def _to_int(value):
            """Convert ``value`` to an int, ``0`` if invalid."""
            try:
                return int(value or 0)
            except (TypeError, ValueError):
                return 0

        date_from = _to_date(filters.get("date_from"))
        date_to = _to_date(filters.get("date_to"))
        if date_from and date_to and date_from > date_to:
            date_from, date_to = date_to, date_from
        return {
            "date_from": date_from,
            "date_to": date_to,
            "class_id": _to_int(filters.get("class_id")),
            "program_id": _to_int(filters.get("program_id")),
            "department_id": _to_int(filters.get("department_id")),
        }

    @api.model
    def _currency(self):
        """Currency details (symbol, position, decimals) of the company."""
        currency = self.env.company.currency_id
        return {"symbol": currency.symbol, "position": currency.position,
                "decimals": currency.decimal_places}

    @api.model
    def _class_options(self):
        """Classes offered by the class filter (id, name, program)."""
        return [{"id": c.id, "name": c.display_name,
                 "program_id": c.program_id.id}
                for c in self.env["education.class"].search([])]

    @staticmethod
    def _in(field, ids):
        """``[(field, 'in', ids)]`` or ``[]`` when not filtered (ids=None)."""
        return [] if ids is None else [(field, "in", ids)]

    @staticmethod
    def _date_domain(field, f):
        """Domain terms limiting ``field`` to the filter's date range."""
        domain = []
        if f["date_from"]:
            domain.append((field, ">=", f["date_from"]))
        if f["date_to"]:
            domain.append((field, "<=", f["date_to"]))
        return domain

    @staticmethod
    def _is_class_filtered(f):
        """Tell whether a class or a program filter is active."""
        return bool(f["class_id"] or f["program_id"])

    @api.model
    def _filtered_classes(self, f):
        """Classes matching the class / program filters."""
        domain = []
        if f["class_id"]:
            domain.append(("id", "=", f["class_id"]))
        if f["program_id"]:
            domain.append(("program_id", "=", f["program_id"]))
        return self.env["education.class"].search(domain)

    @api.model
    def _faculty_count(self, class_ids):
        """Number of faculty members, optionally for some classes only.

        With ``class_ids`` a member counts when he or she teaches a period of
        those classes or is their class teacher.
        """
        Employee = self.env["hr.employee"]
        if class_ids is None:
            return Employee.search_count([("is_faculty", "=", True)])
        slots = self.env["education.timetable.slot"].search(
            [("class_id", "in", class_ids)])
        teacher_ids = set(slots.mapped("teacher_id").ids)
        teacher_ids |= set(self.env["education.class"].browse(
            class_ids).mapped("class_teacher_id").ids)
        return Employee.search_count([("is_faculty", "=", True),
                                      ("id", "in", list(teacher_ids))])

    @api.model
    def _attendance_breakdown(self, domain):
        """Present / absent / late / excused counts and present-rate %."""
        counts = dict(self.env["education.attendance"]._read_group(
            domain, ["state"], ["__count"]))
        out = {key: counts.get(key, 0)
               for key in ("present", "absent", "late", "excused")}
        out["total"] = sum(counts.values())
        out["rate"] = round(
            (out["present"] + out["late"]) * 100.0 / out["total"], 1
        ) if out["total"] else 0.0
        return out

    @api.model
    def _attendance_trend(self, class_domain, f, today):
        """Daily attendance rate for the last days of the period."""
        end = min(f["date_to"], today) if f["date_to"] else today
        start = end - timedelta(days=TREND_DAYS - 1)
        if f["date_from"] and f["date_from"] > start:
            start = f["date_from"]
        domain = class_domain + [("date", ">=", start), ("date", "<=", end)]
        per_day = defaultdict(lambda: defaultdict(int))
        for day, state, count in self.env["education.attendance"]._read_group(
                domain, ["date:day", "state"], ["__count"]):
            per_day[fields.Date.to_string(day)][state] += count
        rows = []
        for day in sorted(per_day):
            stats = per_day[day]
            total = sum(stats.values())
            rows.append({
                "label": day[8:10] + "/" + day[5:7],
                "date": day,
                "value": round((stats.get("present", 0)
                                + stats.get("late", 0)) * 100.0 / total, 1),
                "absent": stats.get("absent", 0),
            })
        return rows

    @api.model
    def _unmarked_classes(self, today, class_ids):
        """Classes that have a period today but no attendance marked yet."""
        slots = self.env["education.timetable.slot"].search([
            ("timetable_id.active", "=", True),
            ("weekday", "=", str(today.weekday())),
        ] + self._in("class_id", class_ids))
        scheduled = set(slots.mapped("class_id").ids)
        marked = {klass.id for klass, _n in self.env[
            "education.attendance"]._read_group(
            [("date", "=", today), ("class_id", "in", list(scheduled))],
            ["class_id"], ["__count"])}
        pending = sorted(scheduled - marked)
        return {"count": len(pending), "ids": pending,
                "scheduled": len(scheduled)}
