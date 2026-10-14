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
"""education.subject — Subject / course model within an academic program."""
from odoo import api, fields, models


class EducationSubject(models.Model):
    """Subject / course within an academic program."""

    _name = "education.subject"
    _description = "Subject"
    _order = "program_id, sequence, name"
    _rec_name = "display_name"

    # ── Standard Fields
    name = fields.Char(
        string="Subject Name",
        required=True,
        translate=True,
        copy=False,
        help="Full name of the subject or course (e.g. Data Structures, "
             "Financial Accounting).",
    )
    code = fields.Char(
        string="Code",
        size=20,
        copy=False,
        help="Unique subject code within the program (e.g. CS301, FIN201).",
    )
    sequence = fields.Integer(
        string="Sequence",
        default=10,
        help="Display order within the program's subject list.",
    )
    active = fields.Boolean(
        string="Active",
        default=True,
        help="Uncheck to archive this subject. Archived subjects will not "
             "appear in timetable slot selection.",
    )

    # ── Relational Fields
    program_id = fields.Many2one(
        comodel_name="education.program",
        string="Program",
        required=True,
        ondelete="cascade",
        index=True,
        help="Academic program to which this subject belongs.",
    )
    department_id = fields.Many2one(
        comodel_name="education.department",
        string="Department",
        related="program_id.department_id",
        help="Department derived automatically from the linked program.",
    )
    class_ids = fields.One2many(
        comodel_name="education.class",
        related="program_id.class_ids",
        string="Classes",
        readonly=True,
        help="Classes running this subject, inherited from the program.",
    )

    company_id = fields.Many2one(
        comodel_name="res.company",
        string="Institution",
        related="program_id.company_id",
        help="Institution derived from the linked program.",
    )

    # ── Computed Fields
    display_name = fields.Char(
        string="Display Name",
        compute="_compute_display_name",
        store=True,
        help="Auto-generated display name combining the subject code and name "
             "(e.g. [CS301] Data Structures).",
    )

    # ── SQL Constraints
    _program_code_uniq = models.Constraint(
        "UNIQUE(program_id, code)",
        "Subject code must be unique within a program.",
    )

    # ── Compute Methods
    @api.depends("code", "name")
    def _compute_display_name(self):
        """Build display name combining subject code and name."""
        for rec in self:
            rec.display_name = f"[{rec.code}] {rec.name}" if rec.code else (
                rec.name)
