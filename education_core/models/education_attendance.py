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
"""education.attendance — Per-student daily attendance record.

One record per student per date.
Supports bulk marking (all-present) and parent notification.
"""
from odoo import api, fields, models, _
from odoo.exceptions import ValidationError


class EducationAttendance(models.Model):
    """Single attendance record: one student, one date."""

    _name = "education.attendance"
    _description = "Student Attendance"
    _inherit = ["mail.thread"]
    _order = "date desc, id desc"
    _rec_name = "display_name"

    # ── Standard Fields
    # ────────────────────────────────────────────────────────────
    date = fields.Date(
        string="Date",
        required=True,
        default=fields.Date.context_today,
        index=True,
    )
    state = fields.Selection(
        selection=[
            ("present", "Present"),
            ("absent", "Absent"),
            ("late", "Late"),
            ("excused", "Excused"),
            ("holiday", "Holiday / Off"),
        ],
        string="Status",
        required=True,
        default="present",
        tracking=True,
    )
    notes = fields.Char(string="Notes / Remarks")

    # ── Relational Fields
    # ──────────────────────────────────────────────────────────
    enrollment_id = fields.Many2one(
        comodel_name="education.enrollment",
        string="Student Enrollment",
        required=True,
        ondelete="cascade",
        index=True,
    )
    student_name = fields.Char(
        string="Student",
        related="enrollment_id.student_name",
        store=True,
        readonly=True,
    )
    class_id = fields.Many2one(
        comodel_name="education.class",
        string="Class",
        compute="_compute_class_id",
        store=True,
        readonly=False,
        index=True,
    )
    academic_year_id = fields.Many2one(
        comodel_name="education.academic.year",
        string="Academic Year",
        related="class_id.academic_year_id",
        store=True,
        readonly=True,
    )
    marked_by_id = fields.Many2one(
        comodel_name="res.users",
        string="Marked By",
        default=lambda self: self.env.user,
        readonly=True,
    )
    company_id = fields.Many2one(
        comodel_name="res.company",
        string="Institution",
        related="enrollment_id.company_id",
        store=True,
        index=True,
    )

    # ── Computed Fields
    # ────────────────────────────────────────────────────────────
    display_name = fields.Char(
        compute="_compute_display_name",
        store=True,
    )

    # ── SQL Constraints
    # ────────────────────────────────────────────────────────────
    _enrollment_date_uniq = models.Constraint(
        "UNIQUE(enrollment_id, date)",
        "Attendance for this student on this date already exists.",
    )

    # ── Compute Methods
    # ────────────────────────────────────────────────────────────
    @api.depends("student_name", "date")
    def _compute_display_name(self):
        """Build display name as 'Student / Date'."""
        for rec in self:
            rec.display_name = (
                f"{rec.student_name or '?'} / "
                f"{rec.date or '?'}"
            )

    @api.depends("enrollment_id.class_id")
    def _compute_class_id(self):
        """Derive class from the linked enrollment record."""
        for rec in self:
            if rec.enrollment_id and rec.enrollment_id.class_id:
                rec.class_id = rec.enrollment_id.class_id
            elif not rec.class_id:
                rec.class_id = False

    # ── Python Constraints
    # ─────────────────────────────────────────────────────────
    @api.constrains("enrollment_id", "date")
    def _check_enrollment_date_unique(self):
        """Ensure only one attendance record exists per student per date."""
        for rec in self:
            if not rec.enrollment_id or not rec.date:
                continue
            # Check within current batch/recordset
            duplicate = self.filtered(
                lambda r:
                r.enrollment_id == rec.enrollment_id and r.date == rec.date
            )
            if len(duplicate) > 1:
                raise ValidationError(
                    _("Attendance of the student is already marked for this "
                      "date.")
                )
            # Check against existing records in database
            domain = [
                ("id", "!=", rec.id),
                ("enrollment_id", "=", rec.enrollment_id.id),
                ("date", "=", rec.date),
            ]
            if self.search_count(domain) > 0:
                raise ValidationError(
                    _("Attendance for this student on this date already "
                      "exists.")
                )

    @api.constrains("date")
    def _check_date(self):
        """Prevent future-dated attendance records."""
        today = fields.Date.context_today(self)
        for rec in self:
            if rec.date and rec.date > today:
                raise ValidationError(
                    _("Attendance date cannot be in the future."))

    # ── Action Methods
    # ─────────────────────────────────────────────────────────────
    def action_notify_parent(self):
        """Send absence notification email to guardian."""
        absent_with_guardian = self.filtered(
            lambda r: r.state == "absent" and r.enrollment_id.guardian_email
        )
        if not absent_with_guardian:
            return

        template = self.env.ref(
            "education_core.mail_template_attendance_absent",
            raise_if_not_found=False,
        )
        if template:
            for rec in absent_with_guardian:
                template.send_mail(rec.id, force_send=False)

    # ── Business / Model Methods
    # ───────────────────────────────────────────────────
    @api.model
    def bulk_mark_present(self, class_id, date):
        """Mark all active enrollments in a class as Present for a given
        date in a single batch.

        Returns count of records created.
        """
        enrollments = self.env["education.enrollment"].search([
            ("class_id", "=", class_id),
            ("state", "=", "active"),
        ])
        if not enrollments:
            return 0

        # Query existing attendances in one shot to avoid N queries
        existing_attendances = self.search([
            ("enrollment_id", "in", enrollments.ids),
            ("date", "=", date),
        ])
        existing_enrollment_ids = set(
            existing_attendances.mapped("enrollment_id.id"))

        # Batch-create missing records
        vals_list = [
            {
                "enrollment_id": enr.id,
                "class_id": class_id,
                "date": date,
                "state": "present",
            }
            for enr in enrollments
            if enr.id not in existing_enrollment_ids
        ]

        if vals_list:
            self.create(vals_list)

        return len(vals_list)
