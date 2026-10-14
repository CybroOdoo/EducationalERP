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
"""education.academic.year — Academic year model."""
from odoo import api, fields, models, _
from odoo.exceptions import ValidationError


class EducationAcademicYear(models.Model):
    """Represents a single academic year (e.g. 2025-2026).

    Exactly one record should have is_current=True per company.
    """

    _name = "education.academic.year"
    _description = "Academic Year"
    _inherit = ["mail.thread"]
    _order = "date_start desc"

    # --- Standard Fields ---
    name = fields.Char(
        string="Academic Year",
        required=True,
        tracking=True,
        copy=False,
        help='e.g. "2025-2026" or "Spring 2026".',
    )
    code = fields.Char(
        string="Code",
        required=True,
        size=10,
        tracking=True,
        copy=False,
        help='Short code used in sequence prefixes (e.g. "AY2526").',
    )
    date_start = fields.Date(
        string="Start Date",
        required=True,
        tracking=True,
        copy=False,
        help="First day of this academic year (e.g. 2025-06-01).",
    )
    date_end = fields.Date(
        string="End Date",
        required=True,
        tracking=True,
        copy=False,
        help="Last day of this academic year. Must be after the Start Date.",
    )
    is_current = fields.Boolean(
        string="Current Year",
        default=False,
        tracking=True,
        copy=False,
        help="Mark the currently active academic year. Only one year can be "
             "current per company.",
    )
    sequence = fields.Integer(
        string="Sequence",
        default=10,
        help="Display order in lists. Lower numbers appear first.",
    )
    notes = fields.Text(
        string="Notes",
        help="Additional remarks or context about this academic year.",
    )
    active = fields.Boolean(
        string="Active",
        default=True,
        help="Uncheck to archive this academic year without deleting it.",
    )

    # --- Relational Fields ---
    company_id = fields.Many2one(
        comodel_name="res.company",
        string="Institution",
        default=lambda self: self.env.company,
        required=True,
        index=True,
        help="Institution to which this academic year belongs.",
    )

    # --- Computed Fields ---
    enrollment_count = fields.Integer(
        string="Enrollments",
        compute="_compute_enrollment_count",
        help="Number of active student enrollments registered in this "
             "academic year.",
    )

    # --- Compute Methods ---
    def _compute_enrollment_count(self):
        """Batch-count active enrollments using _read_group to prevent N+1
        queries."""
        enrollment_data = self.env["education.enrollment"]._read_group(
            domain=[
                ("academic_year_id", "in", self.ids),
                ("state", "=", "active"),
            ],
            groupby=["academic_year_id"],
            aggregates=["__count"],
        )
        counts = {academic_year.id: count for academic_year, count in
                  enrollment_data}
        for rec in self:
            rec.enrollment_count = counts.get(rec.id, 0)

    # --- Constrains Methods ---
    @api.constrains("date_start", "date_end")
    def _check_dates(self):
        """Ensure End Date is strictly after Start Date."""
        for rec in self:
            if (rec.date_start and rec.date_end and rec.date_end <=
                    rec.date_start):
                raise ValidationError(
                    _("End Date must be after Start Date for academic year "
                      "'%(name)s'.",
                      name=rec.name)
                )

    @api.constrains("is_current", "company_id")
    def _check_single_current(self):
        """Enforce only one academic year is current per company."""
        for rec in self.filtered("is_current"):
            existing = self.search([
                ("is_current", "=", True),
                ("company_id", "=", rec.company_id.id),
                ("id", "!=", rec.id),
            ], limit=1)
            if existing:
                raise ValidationError(
                    _(
                        "Only one Academic Year can be marked as current per "
                        "company. "
                        "'%(existing_year)s' is already set as current.",
                        existing_year=existing.name,
                    )
                )

    # --- Action Methods ---
    def action_set_current(self):
        """Mark this year as current and unset existing active year for this
        company."""
        self.ensure_one()
        # Only write to records that are currently set to True to prevent
        # redundant writes
        self.search([
            ("company_id", "=", self.company_id.id),
            ("id", "!=", self.id),
            ("is_current", "=", True),
        ]).write({"is_current": False})
        self.write({"is_current": True})

    # --- Business Methods ---
    @api.model
    def get_current_year(self, company_id=None):
        """Return the current academic year for the specified or current
        company."""
        target_company_id = company_id or self.env.company.id
        return self.search(
            [("is_current", "=", True),
             ("company_id", "=", target_company_id)],
            limit=1,
        ).id
