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
"""education.leave.request — Student leave application with approval (S3-T03).

Students (or guardians) apply for leave; admin/teacher approves/rejects.
Approved leaves auto-mark attendance as 'excused' for the covered dates.
"""
from odoo import api, fields, models, _
from odoo.exceptions import ValidationError


class EducationLeaveRequest(models.Model):
    """Student leave request — applies for excused absence."""

    _name = "education.leave.request"
    _description = "Student Leave Request"
    _inherit = ["mail.thread", "mail.activity.mixin"]
    _order = "date_from desc, id desc"
    _rec_name = "reference"

    # ── Standard Fields
    reference = fields.Char(
        string="Reference",
        readonly=True,
        copy=False,
        default="New",
    )
    state = fields.Selection(
        selection=[
            ("draft", "Draft"),
            ("submitted", "Submitted"),
            ("approved", "Approved"),
            ("rejected", "Rejected"),
        ],
        string="Status",
        default="draft",
        required=True,
        tracking=True,
    )
    date_from = fields.Date(
        string="From Date",
        required=True,
    )
    date_to = fields.Date(
        string="To Date",
        required=True,
    )
    leave_type = fields.Selection(
        selection=[
            ("medical", "Medical / Sick Leave"),
            ("personal", "Personal"),
            ("family", "Family Emergency"),
            ("event", "Participation in Event"),
            ("other", "Other"),
        ],
        string="Leave Type",
        required=True,
        default="personal",
    )
    reason = fields.Text(
        string="Reason",
        required=True,
    )
    supporting_document = fields.Binary(
        string="Supporting Document",
        attachment=True,
        help="Medical certificate, event permission letter, etc.",
    )
    supporting_document_name = fields.Char(string="Supporting Document Name")
    approval_date = fields.Date(
        string="Decision Date",
        readonly=True,
    )
    rejection_reason = fields.Text(
        string="Rejection Reason",
        readonly=True,
    )

    # ── Relational Fields
    enrollment_id = fields.Many2one(
        comodel_name="education.enrollment",
        string="Student Enrollment",
        required=True,
        ondelete="restrict",
        index=True,
    )
    approved_by_id = fields.Many2one(
        comodel_name="res.users",
        string="Approved / Rejected By",
        readonly=True,
    )
    company_id = fields.Many2one(
        comodel_name="res.company",
        string="Institution",
        related="enrollment_id.company_id",
    )

    # ── Related Fields
    student_name = fields.Char(
        string="Student Name",
        related="enrollment_id.student_name",
        store=True,
        readonly=True,
    )
    class_id = fields.Many2one(
        comodel_name="education.class",
        string="Class / Section",
        related="enrollment_id.class_id",
        store=True,
        readonly=True,
    )

    # ── Computed Fields
    days_count = fields.Integer(
        string="Days",
        compute="_compute_days_count",
        store=True,
    )
    _reference_uniq = models.Constraint(
        "UNIQUE(reference, company_id)",
        "Leave reference must be unique.",
    )

    # ── ORM Overrides
    @api.model_create_multi
    def create(self, vals_list):
        """Override create to assign auto-generated leave reference."""
        sequence = self.env["ir.sequence"].sudo().search(
            [("code", "=", "education.leave.request"),
             ("company_id", "=", self.env.company.id)])
        if not sequence:
            sequence.sudo().create({
                "code": "education.leave.request",
                "name": "Student Leave Request",
                "prefix": "LVE/%(year)s/",
                "padding": 5,
                "number_increment": 1,
                "number_next": 1,
                "company_id": self.env.company.id,
            })
        for vals in vals_list:
            if vals.get("reference", "New") == "New":
                vals["reference"] = sequence.next_by_code(
                    "education.leave.request") or "New"
        return super().create(vals_list)

    # ── Compute Methods
    @api.depends("date_from", "date_to")
    def _compute_days_count(self):
        """Calculate number of days covered by the leave request."""
        for rec in self:
            if rec.date_from and rec.date_to:
                delta = rec.date_to - rec.date_from
                rec.days_count = max(1, delta.days + 1)
            else:
                rec.days_count = 0

    # ── Constraints
    @api.constrains("date_from", "date_to")
    def _check_dates(self):
        """Ensure To Date is on or after From Date."""
        for rec in self:
            if rec.date_from and rec.date_to and rec.date_to < rec.date_from:
                raise ValidationError(
                    _("To Date must be on or after From Date."))

    # ── Action Methods
    def action_submit(self):
        """Submit draft leave requests for approval."""
        self.filtered(lambda r: r.state == "draft").write(
            {"state": "submitted"})

    def action_approve(self):
        """Approve and mark attendance as excused for covered periods."""
        records_to_approve = self.filtered(lambda r: r.state == "submitted")
        if not records_to_approve:
            return

        today = fields.Date.context_today(self)
        records_to_approve.write({
            "state": "approved",
            "approved_by_id": self.env.uid,
            "approval_date": today,
        })

        approve_template = self.env.ref(
            "education_core.mail_template_leave_request_approved",
            raise_if_not_found=False,
        )

        for rec in records_to_approve:
            rec._mark_attendance_excused()
            rec.message_post(
                body=_(
                    "Leave approved for %(date_from)s to %(date_to)s (%("
                    "days)s day(s)).",
                    date_from=rec.date_from,
                    date_to=rec.date_to,
                    days=rec.days_count,
                )
            )
            if approve_template:
                approve_template.send_mail(rec.id, force_send=True)

    def action_reject(self):
        """Reject submitted leave requests and notify the student."""
        records_to_reject = self.filtered(lambda r: r.state == "submitted")
        if not records_to_reject:
            return

        today = fields.Date.context_today(self)
        records_to_reject.write({
            "state": "rejected",
            "approved_by_id": self.env.uid,
            "approval_date": today,
        })

        reject_template = self.env.ref(
            "education_core.mail_template_leave_request_rejected",
            raise_if_not_found=False,
        )
        if reject_template:
            for rec in records_to_reject:
                reject_template.send_mail(rec.id, force_send=True)

    def action_reset_draft(self):
        """Reset rejected leave requests back to draft for re-submission."""
        self.filtered(lambda r: r.state == "rejected").write(
            {"state": "draft"})

    def _mark_attendance_excused(self):
        """Mark all absence records in the leave period as 'excused'."""
        for rec in self:
            attendances = self.env["education.attendance"].search([
                ("enrollment_id", "=", rec.enrollment_id.id),
                ("date", ">=", rec.date_from),
                ("date", "<=", rec.date_to),
                ("state", "=", "absent"),
            ])
            if attendances:
                attendances.write({"state": "excused"})
