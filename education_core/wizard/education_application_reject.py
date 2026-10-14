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
"""education.application.reject — Admission Application Rejection Wizard.

Captures rejection reason and transitions the application to 'rejected'.
Triggers the rejection email template and logs a note to the chatter.
"""
from odoo import api, fields, models, _
from odoo.exceptions import ValidationError


class EducationApplicationReject(models.TransientModel):
    """Wizard to reject a student application with mandatory explanation."""

    _name = "education.application.reject"
    _description = "Education Application Rejection"

    # ── Standard Fields
    # ────────────────────────────────────────────────────────
    rejection_reason = fields.Text(
        string="Rejection Reason",
        required=True,
        help="This reason will be included in the rejection email sent to "
             "the applicant.",
    )

    # ── Relational Fields
    # ──────────────────────────────────────────────────────
    application_id = fields.Many2one(
        comodel_name="education.application",
        string="Application",
        required=True,
        readonly=True,
    )

    # ── Computed / Related Fields
    # ──────────────────────────────────────────────
    applicant_name = fields.Char(
        string="Applicant",
        related="application_id.name",
        readonly=True,
    )
    program_name = fields.Char(
        string="Program",
        related="application_id.program_id.name",
        readonly=True,
    )

    # ── Constraints
    # ───────────────────────────────────────────────────────────
    @api.constrains("rejection_reason")
    def _check_reason(self):
        for rec in self:
            if rec.rejection_reason and len(rec.rejection_reason.strip()) < 10:
                raise ValidationError(
                    _("Please provide a meaningful rejection reason (at "
                      "least 10 characters).")
                )

    # ── Action Methods
    # ────────────────────────────────────────────────────────
    def action_confirm_reject(self):
        """Confirm rejection, write to application, send email, and log
        chatter note."""
        self.ensure_one()
        self.application_id.write({
            "state": "rejected",
            "rejection_reason": self.rejection_reason,
            "rejected_by_id": self.env.user.id,
            "rejection_date": fields.Date.context_today(self),
        })

        # Send rejection email if template exists
        template = self.env.ref(
            "education_core.mail_template_application_rejected",
            raise_if_not_found=False,
        )
        if template:
            template.send_mail(self.application_id.id, force_send=False)

        # Post audit note to application chatter
        self.application_id.message_post(
            body=_(
                "Application rejected. Reason: %(reason)s",
                reason=self.rejection_reason,
            ),
        )

        return {"type": "ir.actions.act_window_close"}
