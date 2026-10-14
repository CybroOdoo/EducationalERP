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
"""education.department — Academic department model."""
from odoo import api, fields, models, _


class EducationDepartment(models.Model):
    """Academic department (e.g. Computer Science, Business Administration)."""

    _name = "education.department"
    _description = "Academic Department"
    _inherit = ["mail.thread"]
    _order = "sequence, name"

    # ── Standard Fields

    name = fields.Char(
        string="Department Name",
        required=True,
        tracking=True,
        translate=True,
        copy=False,
        help="Full name of the academic department (e.g. Computer Science, "
             "Business Administration).",
    )
    code = fields.Char(
        string="Code",
        required=True,
        size=10,
        tracking=True,
        help="Short code used in reports (e.g. CSE, MBA, MED).",
        copy=False,
    )
    sequence = fields.Integer(
        default=10,
        help="Determines the display order of departments in lists and menus. "
             "Lower numbers appear first.",
    )
    description = fields.Text(
        string="Description",
        help="Additional details about the department's focus, objectives, "
             "or special notes.",
    )
    active = fields.Boolean(
        string="Active",
        default=True,
        help="Uncheck to archive the department without deleting it. "
             "Archived departments are hidden from menus and dropdowns.",
    )

    # ── Relational Fields
    # ──────────────────────────────────────────────────────
    head_id = fields.Many2one(
        comodel_name="hr.employee",
        string="Department Head",
        domain="[('is_faculty', '=', True)]",
        tracking=True,
        copy=False,
        help="Faculty member responsible for heading and managing this "
             "department.",
    )
    company_id = fields.Many2one(
        comodel_name="res.company",
        string="Institution",
        default=lambda self: self.env.company,
        required=True,
        index=True,
        help="Institution to which this department belongs.",
    )
    program_ids = fields.One2many(
        comodel_name="education.program",
        inverse_name="department_id",
        string="Programs",
        help="All academic programs offered by this department.",
    )

    # ── Computed Fields
    program_count = fields.Integer(
        string="# Programs",
        compute="_compute_program_count",
        help="Total number of academic programs linked to this department.",
    )

    # ── SQL Constraints
    _code_company_uniq = models.Constraint(
        "UNIQUE(code, company_id)",
        "Department code must be unique per company.",
    )

    # ── Compute Methods

    @api.depends("program_ids")
    def _compute_program_count(self):
        """Count academic programs linked to this department."""
        for rec in self:
            rec.program_count = len(rec.program_ids)

    # ── Action Methods

    def action_view_programs(self):
        """Open programs belonging to this department."""
        self.ensure_one()
        return {
            "type": "ir.actions.act_window",
            "name": _("Programs — %(name)s", name=self.name),
            "res_model": "education.program",
            "domain": [("department_id", "=", self.id)],
            "view_mode": "list,form",
            "context": {"default_department_id": self.id},
        }
