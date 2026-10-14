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
"""education.application.approve — Application Approval & Class Assignment
Wizard.

Allows admission officers and admins to select or create a class/section
for the applicant's program before finalizing enrollment.
"""
from odoo import api, fields, models, _
from odoo.exceptions import ValidationError


class EducationApplicationApprove(models.TransientModel):
    """Wizard to assign a class/section to a student upon application
    approval."""

    _name = "education.application.approve"
    _description = "Approve Application and Assign Class"

    # ── Relational Fields ────────────────────────────────────────────────────
    application_id = fields.Many2one(
        comodel_name="education.application",
        string="Application",
        required=True,
        readonly=True,
    )
    class_id = fields.Many2one(
        comodel_name="education.class",
        string="Class / Section",
        required=True,
        domain="[('program_id', '=', program_id)]",
        help="Select or create a class/section belonging to the applied "
             "program.",
    )

    # ── Related / Computed Fields ────────────────────────────────────────────
    applicant_name = fields.Char(
        string="Applicant",
        related="application_id.name",
        readonly=True,
    )
    program_id = fields.Many2one(
        comodel_name="education.program",
        string="Program",
        related="application_id.program_id",
        readonly=True,
    )
    academic_year_id = fields.Many2one(
        comodel_name="education.academic.year",
        string="Academic Year",
        related="application_id.academic_year_id",
        readonly=True,
    )

    # ── Constraints ──────────────────────────────────────────────────────────
    @api.constrains("class_id")
    def _check_class_program(self):
        for rec in self:
            if (rec.class_id and rec.program_id and rec.class_id.program_id
                    != rec.program_id):
                raise ValidationError(
                    _(
                        "The selected class '%(class_name)s' does not belong "
                        "to program '%(program_name)s'.",
                        class_name=rec.class_id.name,
                        program_name=rec.program_id.name,
                    )
                )

    # ── Action Methods ───────────────────────────────────────────────────────
    def action_confirm_approve(self):
        """Confirm approval and create enrollment with the assigned class."""
        self.ensure_one()
        self.application_id._perform_approve(class_id=self.class_id)
        return {"type": "ir.actions.act_window_close"}
