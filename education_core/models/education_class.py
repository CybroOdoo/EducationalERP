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
"""education.class — Class / Section model."""
from odoo import api, fields, models, _
from odoo.exceptions import ValidationError


class EducationClass(models.Model):
    """A class is a specific section/batch of a program in a given academic
    year.

    Example: B.Tech CSE Section A — 2025-2026.
    Multiple classes can exist for the same program/year with different
    sections.
    """

    _name = "education.class"
    _description = "Class / Section"
    _inherit = ["mail.thread"]
    _order = "academic_year_id desc, program_id, section"

    # ── Standard Fields
    # ────────────────────────────────────────────────────────
    section = fields.Char(
        string="Section",
        required=True,
        default="A",
        size=5,
        help='Section identifier, e.g. "A", "B", "Morning", "Weekend".',
    )
    capacity = fields.Integer(
        string="Max Capacity",
        default=60,
        required=True,
        help="Maximum number of students allowed in this class.",
    )
    active = fields.Boolean(
        string="Active",
        default=True,
        help="Uncheck to archive this class/section without deleting it.",
    )
    notes = fields.Text(
        string="Notes",
        help="Any internal notes or remarks about this class section.",
    )

    # ── Relational Fields
    # ──────────────────────────────────────────────────────
    program_id = fields.Many2one(
        comodel_name="education.program",
        string="Program",
        required=True,
        ondelete="restrict",
        tracking=True,
        index=True,
        help="Academic program to which this class/section belongs.",
    )
    academic_year_id = fields.Many2one(
        comodel_name="education.academic.year",
        string="Academic Year",
        required=True,
        ondelete="restrict",
        tracking=True,
        index=True,
        default=lambda self: self.env[
            "education.academic.year"].get_current_year(),
        help="Academic year in which this class is running.",
    )
    department_id = fields.Many2one(
        comodel_name="education.department",
        string="Department",
        related="program_id.department_id",
        store=True,
        readonly=True,
        help="Department derived from the linked program.",
    )
    class_teacher_id = fields.Many2one(
        comodel_name="hr.employee",
        string="Class Teacher",
        domain="[('is_faculty', '=', True)]",
        tracking=True,
        ondelete="set null",
        help="Primary faculty member responsible for this class section.",
    )
    company_id = fields.Many2one(
        comodel_name="res.company",
        string="Institution",
        related="program_id.company_id",
        help="Institution derived from the linked program.",
    )
    enrollment_ids = fields.One2many(
        comodel_name="education.enrollment",
        inverse_name="class_id",
        string="Enrollments",
        help="All student enrollments assigned to this class section.",
    )
    subject_ids = fields.One2many(
        comodel_name="education.subject",
        string="Subjects",
        related="program_id.subject_ids",
        help="Subjects offered in this class, inherited from the program.",
    )

    # ── Computed Fields
    # ────────────────────────────────────────────────────────
    name = fields.Char(
        string="Class Name",
        compute="_compute_name",
        store=True,
        help="Auto-generated: Program Code + Section + Year, "
             "e.g. BTECH-CSE-A-2526.",
    )
    enrollment_count = fields.Integer(
        string="Enrolled Students",
        compute="_compute_enrollment_count",
        help="Number of active enrollments in this class.",
    )
    seats_available = fields.Integer(
        string="Seats Available",
        compute="_compute_seats_available",
        help="Remaining seats calculated as max capacity minus current active "
             "enrollments.",
    )

    # ── SQL Constraints
    # ───────────────────────────────────────────────────────
    _program_year_section_uniq = models.Constraint(
        "UNIQUE(program_id, academic_year_id, section)",
        "A class with the same program, academic year and section already "
        "exists.",
    )

    # ── Compute Methods
    # ────────────────────────────────────────────────────────
    @api.depends("program_id.code", "section", "academic_year_id.code")
    def _compute_name(self):
        """Auto-generate class name from program code, section, and year."""
        for rec in self:
            parts = [
                rec.program_id.code or "",
                f"Sec-{rec.section}" if rec.section else "",
                rec.academic_year_id.code or "",
            ]
            rec.name = "-".join(p for p in parts if p)

    @api.depends("enrollment_ids.state")
    def _compute_enrollment_count(self):
        """Count active enrollments using a single batched _read_group
        query."""
        enrollment_data = self.env["education.enrollment"]._read_group(
            domain=[
                ("class_id", "in", self.ids),
                ("state", "=", "active"),
            ],
            groupby=["class_id"],
            aggregates=["__count"],
        )
        mapped_data = {class_rec.id: count for class_rec, count in
                       enrollment_data}
        for rec in self:
            rec.enrollment_count = mapped_data.get(rec.id, 0)

    @api.depends("capacity", "enrollment_count")
    def _compute_seats_available(self):
        """Calculate remaining seats as capacity minus active enrollments."""
        for rec in self:
            rec.seats_available = max(0, rec.capacity - rec.enrollment_count)

    # ── Constraints
    # ───────────────────────────────────────────────────────────
    @api.constrains("capacity")
    def _check_capacity(self):
        """Ensure class capacity is at least 1 seat."""
        for rec in self:
            if rec.capacity < 1:
                raise ValidationError(_("Class capacity must be at least 1."))

    # ── Action Methods
    # ────────────────────────────────────────────────────────
    def action_view_enrollments(self):
        """Open the enrollment list filtered to this class section."""
        self.ensure_one()
        return {
            "type": "ir.actions.act_window",
            "name": _("Enrollments — %(name)s", name=self.name),
            "res_model": "education.enrollment",
            "domain": [("class_id", "=", self.id)],
            "view_mode": "list,form",
            "context": {"default_class_id": self.id},
        }

    def action_open_attendance_list(self):
        """Open Attendance list view filtered for the current class record."""
        self.ensure_one()
        return {
            "name": _("%s Attendance", self.name),
            "type": "ir.actions.act_window",
            "res_model": "education.attendance",
            "view_mode": "list,form",
            "domain": [("class_id", "=", self.id),
                       ('date', '=', fields.Date.today())],
            "context": {
                "default_class_id": self.id,
            },
            "target": "current",
        }
