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
"""education.program — Academic program / course of study model."""
from odoo import api, fields, models, _
from odoo.exceptions import ValidationError

DEGREE_TYPE = [
    ("certificate", "Certificate"),
    ("diploma", "Diploma"),
    ("bachelor", "Bachelor's Degree"),
    ("master", "Master's Degree"),
    ("phd", "PhD / Doctorate"),
    ("professional", "Professional Degree (MBBS, LLB, etc.)"),
    ("vocational", "Vocational / Trade"),
    ("corporate", "Corporate Training"),
    ("other", "Other"),
]


class EducationProgram(models.Model):
    """Academic program offered by a department (e.g. B.Tech CSE, MBA, MBBS).

    Programs group into classes/sections per academic year.
    """

    _name = "education.program"
    _description = "Academic Program"
    _inherit = ["mail.thread"]
    _order = "department_id, name"
    _rec_name = "full_name"

    # ── Standard Fields
    name = fields.Char(
        string="Program Name",
        tracking=True,
        translate=True,
        help="Full name, e.g. Bachelor of Technology — Computer Science.",
        copy=False,
    )
    code = fields.Char(
        string="Program Code",
        size=20,
        tracking=True,
        help="Short code used in class names and sequences (e.g. BTECH-CSE).",
        copy=False,
    )
    degree_type = fields.Selection(
        selection=DEGREE_TYPE,
        string="Degree Type",
        required=True,
        default="bachelor",
        tracking=True,
        help="Level of the academic credential awarded on completion "
             "(e.g. Bachelor, Master, PhD).",
    )
    duration_years = fields.Integer(
        string="Duration (Years)",
        required=True,
        default=3,
        help="Total number of academic years to complete this program.",
    )
    semesters_per_year = fields.Integer(
        string="Semesters per Year",
        default=2,
        help="Number of semesters or terms within a single academic year "
             "for this program (e.g. 2 for bi-annual, 3 for tri-semester).",
    )
    sequence = fields.Integer(
        string="Sequence",
        default=10,
        help="Controls the display order of programs in lists and dropdowns.",
    )
    description = fields.Html(
        string="Program Description",
        sanitize=True,
        help="Detailed description of the program including objectives, "
             "curriculum overview and career prospects.",
    )
    eligibility = fields.Text(
        string="Eligibility / Entry Requirements",
        help="Minimum qualifications or prerequisites a student must meet "
             "to apply for this program.",
    )
    active = fields.Boolean(
        string="Active",
        default=True,
        help="Uncheck to archive this program. Archived programs will not "
             "appear in application or enrollment forms.",
    )

    # ── Relational Fields
    department_id = fields.Many2one(
        comodel_name="education.department",
        string="Department",
        required=True,
        tracking=True,
        ondelete="restrict",
        index=True,
        help="Academic department that owns and administers this program.",
    )
    class_ids = fields.One2many(
        comodel_name="education.class",
        inverse_name="program_id",
        string="Classes",
        help="All class sections running under this program.",
    )
    subject_ids = fields.One2many(
        comodel_name="education.subject",
        inverse_name="program_id",
        string="Subjects",
        help="All subjects/courses belonging to this program's curriculum.",
    )

    company_id = fields.Many2one(
        comodel_name="res.company",
        string="Institution",
        related="department_id.company_id",
        help="Institution derived from the linked department.",
    )

    # ── Computed Fields
    full_name = fields.Char(
        string="Display Name",
        compute="_compute_full_name",
        store=True,
        help="Code + Name used as _rec_name.",
        copy=False,
    )
    class_count = fields.Integer(
        string="# Classes",
        compute="_compute_class_count",
        help="Total number of class sections currently running for this "
             "program.",
    )
    subject_count = fields.Integer(
        string="# Subjects",
        compute="_compute_subject_count",
        help="Total number of subjects / courses defined for this program.",
    )

    # ── SQL Constraints
    _code_company_uniq = models.Constraint(
        "UNIQUE(code, company_id)",
        "Program code must be unique per company.",
    )

    # ── Compute Methods
    @api.depends("code", "name")
    def _compute_full_name(self):
        """Build full name combining program code and name."""
        for rec in self:
            rec.full_name = f"[{rec.code}] {rec.name}" if rec.code else (
                rec.name)

    @api.depends("class_ids")
    def _compute_class_count(self):
        """Batched calculation of class counts without hydrating child
        records."""
        program_ids = self.ids
        if not program_ids:
            for rec in self:
                rec.class_count = 0
            return

        class_data = self.env["education.class"]._read_group(
            domain=[("program_id", "in", program_ids)],
            groupby=["program_id"],
            aggregates=["__count"],
        )
        counts = {program.id: count for program, count in class_data}
        for rec in self:
            rec.class_count = counts.get(rec.id, 0)

    @api.depends("subject_ids")
    def _compute_subject_count(self):
        """Batched calculation of subject counts without hydrating child
        records."""
        program_ids = self.ids
        if not program_ids:
            for rec in self:
                rec.subject_count = 0
            return

        subject_data = self.env["education.subject"]._read_group(
            domain=[("program_id", "in", program_ids)],
            groupby=["program_id"],
            aggregates=["__count"],
        )
        counts = {program.id: count for program, count in subject_data}
        for rec in self:
            rec.subject_count = counts.get(rec.id, 0)

    # ── Constraints
    @api.constrains("duration_years")
    def _check_duration(self):
        """Ensure program duration is at least 1 year."""
        for rec in self:
            if rec.duration_years < 1:
                raise ValidationError(
                    _("Program duration must be at least 1 year."))

    # ── Action Methods
    def action_view_subjects(self):
        """Open subject list view belonging to this program."""
        self.ensure_one()
        return {
            "type": "ir.actions.act_window",
            "name": _("Subjects — %(name)s", name=self.full_name),
            "res_model": "education.subject",
            "domain": [("program_id", "=", self.id)],
            "view_mode": "list",
            "context": {"default_program_id": self.id},
        }

    def action_view_classes(self):
        """Open class list/form views belonging to this program."""
        self.ensure_one()
        return {
            "type": "ir.actions.act_window",
            "name": _("Classes — %(name)s", name=self.full_name),
            "res_model": "education.class",
            "domain": [("program_id", "=", self.id)],
            "view_mode": "list,form",
            "context": {"default_program_id": self.id},
        }
