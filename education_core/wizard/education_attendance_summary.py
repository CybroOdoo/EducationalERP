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
###############################################################################
"""education.attendance.summary — Attendance Summary Reporting Wizard.

Filters attendance by class + date range and either opens the list view
or triggers the PDF attendance report.
"""
from odoo import api, fields, models, _
from odoo.exceptions import ValidationError


class EducationAttendanceSummary(models.TransientModel):
    """Wizard to filter and generate class attendance summaries and PDF
    reports."""

    _name = "education.attendance.summary"
    _description = "Education Attendance Summary"

    # ── Standard Fields
    # ────────────────────────────────────────────────────────
    date_from = fields.Date(
        string="From Date",
        required=True,
        default=lambda self: fields.Date.context_today(self).replace(day=1),
    )
    date_to = fields.Date(
        string="To Date",
        required=True,
        default=fields.Date.context_today,
    )

    # ── Relational Fields
    # ──────────────────────────────────────────────────────
    class_id = fields.Many2one(
        comodel_name="education.class",
        string="Class",
        required=True,
    )

    # ── Constraints
    # ───────────────────────────────────────────────────────────
    @api.constrains("date_from", "date_to")
    def _check_dates(self):
        for rec in self:
            if rec.date_from and rec.date_to and rec.date_to < rec.date_from:
                raise ValidationError(
                    _("To Date must be on or after From Date."))

    # ── Helper Methods
    # ────────────────────────────────────────────────────────
    def _get_domain(self):
        return [
            ("class_id", "=", self.class_id.id),
            ("date", ">=", self.date_from),
            ("date", "<=", self.date_to),
        ]

    # ── Action Methods
    # ────────────────────────────────────────────────────────
    def action_view_attendance(self):
        """Open the attendance list filtered by wizard parameters."""
        self.ensure_one()
        return {
            "type": "ir.actions.act_window",
            "name": _("Attendance — %(class_name)s",
                      class_name=self.class_id.name),
            "res_model": "education.attendance",
            "view_mode": "list,form",
            "domain": self._get_domain(),
            "context": {
                "default_class_id": self.class_id.id,
                "search_default_date_range": 1,
            },
        }

    def action_print_report(self):
        """Render the QWeb PDF attendance report."""
        self.ensure_one()
        records = self.env["education.attendance"].search(self._get_domain())
        if not records:
            raise ValidationError(
                _("No attendance records found for the selected class and "
                  "date range.")
            )

        summary_lines = []
        for enr in records.mapped("enrollment_id"):
            enr_records = records.filtered(lambda a: a.enrollment_id == enr)
            total = len(enr_records)
            present_cnt = len(
                enr_records.filtered(lambda a: a.state == "present"))
            absent_cnt = len(
                enr_records.filtered(lambda a: a.state == "absent"))
            late_cnt = len(enr_records.filtered(lambda a: a.state == "late"))
            excused_cnt = len(
                enr_records.filtered(lambda a: a.state == "excused"))
            pct = round((present_cnt + late_cnt + excused_cnt) / total * 100,
                        1) if total else 0.0
            summary_lines.append({
                "student_name": enr.student_name,
                "total": total,
                "present": present_cnt,
                "absent": absent_cnt,
                "late": late_cnt,
                "excused": excused_cnt,
                "pct": pct,
            })

        return self.env.ref(
            "education_core.action_report_attendance_period"
        ).report_action(
            records,
            data={
                "class_name": self.class_id.name,
                "date_from": str(self.date_from),
                "date_to": str(self.date_to),
                "summary_lines": summary_lines,
            },
        )
