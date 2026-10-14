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
"""hr.employee extension for educational faculty management and
qualifications."""
from odoo import api, fields, models, _
from odoo.exceptions import UserError, ValidationError

OVERLOAD_THRESHOLD = 30


class HrEmployee(models.Model):
    """Faculty profile extension for hr.employee."""

    _inherit = "hr.employee"

    # ── Standard Fields
    is_faculty = fields.Boolean(
        string="Faculty Member",
        default=False,
    )
    faculty_id = fields.Char(
        string="Faculty ID",
        required=True,
        copy=False,
        default="New",
        tracking=True,
    )
    blood_group = fields.Selection(
        selection=[
            ("a+", "A+"), ("a-", "A−"),
            ("b+", "B+"), ("b-", "B−"),
            ("ab+", "AB+"), ("ab-", "AB−"),
            ("o+", "O+"), ("o-", "O−"),
        ],
        string="Blood Group",
    )
    designation = fields.Char(
        string="Designation",
        tracking=True,
    )
    specialization = fields.Char(
        string="Specialization / Subject Area",
        tracking=True,
    )
    date_joined = fields.Date(
        string="Date Joined",
        default=fields.Date.context_today,
        tracking=True,
    )
    edu_employment_type = fields.Selection(
        selection=[
            ("permanent", "Permanent"),
            ("contract", "Contract"),
            ("visiting", "Visiting / Adjunct"),
            ("part_time", "Part-time"),
        ],
        string="Employment Type",
        default="permanent",
        tracking=True,
    )

    # ── Relational Fields
    edu_department_id = fields.Many2one(
        comodel_name="education.department",
        string="Education Department",
        tracking=True,
        ondelete="restrict",
    )
    qualification_ids = fields.One2many(
        comodel_name="education.faculty.qualification",
        inverse_name="faculty_id",
        string="Qualifications",
    )

    # ── Computed Fields
    highest_qualification = fields.Char(
        string="Highest Qualification",
        compute="_compute_highest_qualification",
        store=True,
    )
    weekly_periods = fields.Integer(
        string="Assigned Weekly Periods",
        compute="_compute_weekly_periods",
        store=False,
    )
    is_overloaded = fields.Boolean(
        string="Overloaded",
        compute="_compute_weekly_periods",
        store=False,
    )

    # ── SQL Constraints
    _faculty_id_company_uniq = models.Constraint(
        "UNIQUE(faculty_id, company_id)",
        "Faculty ID must be unique.",
    )
    _email_company_uniq = models.Constraint(
        "UNIQUE(work_email, company_id)",
        "A faculty member with this work email already exists in this "
        "institution.",
    )

    # ── CRUD Overrides
    def _get_sequence(self):
        """Fetch or create the faculty ID sequence for the current company."""
        sequence = self.env["ir.sequence"].sudo().search(
            [("code", "=", "education.faculty"),
             ("company_id", "=", self.env.company.id)])
        if not sequence:
            sequence.sudo().create({
                "code": "education.faculty",
                "name": "Faculty ID",
                "prefix": "FAC/%(year)s/",
                "padding": 5,
                "number_increment": 1,
                "number_next": 1,
                "company_id": self.env.company.id,

            })
        return sequence

    @api.model_create_multi
    def create(self, vals_list):
        """Override create to auto-assign faculty ID
         for new faculty members."""
        for vals in vals_list:
            if vals.get("is_faculty") and vals.get("faculty_id",
                                                   "New") == "New":
                vals["faculty_id"] = self._get_sequence().next_by_code(
                    "education.faculty") or "New"
        return super().create(vals_list)

    def write(self, vals):
        """Override write to assign faculty ID when is_faculty is set True."""
        res = super().write(vals)
        if vals.get("is_faculty"):
            for rec in self:
                if rec.faculty_id == "New":
                    rec.faculty_id = self._get_sequence().next_by_code(
                        "education.faculty") or "New"
        return res

    # ── Compute Methods
    @api.depends("qualification_ids", "qualification_ids.degree")
    def _compute_highest_qualification(self):
        """Determine the highest academic qualification from linked records."""
        degree_rank = {
            "post_doc": 6,
            "phd": 5,
            "master": 4,
            "bachelor": 3,
            "diploma": 2,
            "certificate": 1,
            "other": 0,
        }
        for rec in self:
            if not rec.qualification_ids:
                rec.highest_qualification = ""
                continue
            top = max(rec.qualification_ids,
                      key=lambda q: degree_rank.get(q.degree, 0))
            rec.highest_qualification = top.display_name or ""

    def _compute_weekly_periods(self):
        """Batched calculation of weekly teaching periods for faculty."""
        faculty_members = self.filtered("is_faculty")
        non_faculty = self - faculty_members
        non_faculty.weekly_periods = 0
        non_faculty.is_overloaded = False

        if not faculty_members:
            return

        slot_data = self.env["education.timetable.slot"]._read_group(
            domain=[
                ("teacher_id", "in", faculty_members.ids),
                ("timetable_id.state", "=", "published"),
            ],
            groupby=["teacher_id"],
            aggregates=["__count"],
        )
        counts = {teacher.id: count for teacher, count in slot_data}
        for rec in faculty_members:
            periods = counts.get(rec.id, 0)
            rec.weekly_periods = periods
            rec.is_overloaded = periods > OVERLOAD_THRESHOLD

    # ── Action Methods
    def action_view_timetable_slots(self):
        """Open timetable slots filtered to those assigned to this faculty."""
        self.ensure_one()
        return {
            "type": "ir.actions.act_window",
            "name": _("Timetable Slots — %(name)s", name=self.name),
            "res_model": "education.timetable.slot",
            "view_mode": "list,form",
            "domain": [("teacher_id", "=", self.id)],
        }

    def action_create_user(self):
        """Create a user account and flag it as faculty if applicable."""
        result = super().action_create_user()
        if isinstance(result, dict) and "context" in result:
            result["context"]["is_faculty"] = self.is_faculty
        return result

    def action_set_password(self):
        """Open the change-password wizard for the faculty's user account."""
        self.ensure_one()
        if not self.user_id:
            raise UserError(
                _(
                    "Grant user account first — no user account exists for "
                    "teacher %(faculty_id)s.",
                    faculty_id=self.faculty_id or self.name,
                )
            )
        return {
            "type": "ir.actions.act_window",
            "name": _("Change Password"),
            "res_model": "change.password.wizard",
            "view_mode": "form",
            "target": "new",
            "context": {
                "active_id": self.user_id.id,
                "active_ids": [self.user_id.id],
                "active_model": "res.users",
            },
        }

    # ── Helper Methods
    def _get_sex_display(self):
        """Return the human-readable label for the faculty's sex field."""
        self.ensure_one()
        selection = dict(self._fields["sex"]._description_selection(self.env))
        return selection.get(self.sex, "—")


class EducationFacultyQualification(models.Model):
    """Academic and professional qualifications obtained by faculty members."""

    _name = "education.faculty.qualification"
    _description = "Faculty Qualification"
    _order = "year_obtained desc"
    _rec_name = "display_name"

    # ── Standard Fields
    degree = fields.Selection(
        selection=[
            ("certificate", "Certificate"),
            ("diploma", "Diploma"),
            ("bachelor", "Bachelor's Degree"),
            ("master", "Master's Degree"),
            ("phd", "PhD / Doctorate"),
            ("post_doc", "Post-Doctoral"),
            ("other", "Other"),
        ],
        string="Degree",
        required=True,
    )
    field_of_study = fields.Char(
        string="Field of Study",
        required=True,
    )
    institution = fields.Char(
        string="Institution",
        required=True,
    )
    year_obtained = fields.Integer(
        string="Year Obtained",
        required=True,
    )
    grade = fields.Char(string="Grade / GPA")
    certificate_file = fields.Binary(
        string="Certificate",
        attachment=True,
    )
    certificate_file_name = fields.Char(string="Certificate Filename")

    # ── Relational Fields
    faculty_id = fields.Many2one(
        comodel_name="hr.employee",
        string="Faculty Member",
        required=True,
        ondelete="cascade",
        index=True,
    )
    company_id = fields.Many2one(
        related="faculty_id.company_id",
        string="Institution",
    )

    # ── Computed Fields
    display_name = fields.Char(
        string="Display Name",
        compute="_compute_display_name",
        store=True,
    )

    # ── Compute Methods
    @api.depends("degree", "field_of_study", "institution", "year_obtained")
    def _compute_display_name(self):
        """Build display name combining degree, field, institution and year."""
        degree_labels = dict(self._fields["degree"].selection)
        for rec in self:
            rec.display_name = (
                f"{degree_labels.get(rec.degree, '')} in "
                f"{rec.field_of_study} — {rec.institution} ("
                f"{rec.year_obtained})"
            )

    # ── Constraints
    @api.constrains("year_obtained")
    def _check_year(self):
        """Ensure year obtained is between 1900 and next calendar year."""
        current_year = fields.Date.context_today(self).year
        for rec in self:
            if rec.year_obtained and not (
                    1900 <= rec.year_obtained <= current_year + 1):
                raise ValidationError(
                    _(
                        "Year obtained must be between 1900 and %(max_year)d.",
                        max_year=current_year + 1,
                    )
                )
