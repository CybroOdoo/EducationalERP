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
"""education.enrollment — Student Enrollment Record.

Created automatically when an admission application is approved.
Links student → class → academic year; manages portal accounts.
"""
from odoo import api, fields, models, _
from odoo.exceptions import UserError


class EducationEnrollment(models.Model):
    """Student enrollment — one per student per academic year."""

    _name = "education.enrollment"
    _description = "Student Enrollment"
    _inherit = ["mail.thread", "mail.activity.mixin"]
    _order = "enrollment_date desc, enrollment_no desc"
    _rec_name = "display_name"

    # ── Standard Fields
    enrollment_no = fields.Char(
        string="Enrollment No.",
        readonly=True,
        copy=False,
        default="New",
        tracking=True,
    )
    state = fields.Selection(
        selection=[
            ("active", "Active"),
            ("suspended", "Suspended"),
            ("graduated", "Graduated"),
            ("withdrawn", "Withdrawn"),
        ],
        string="Status",
        default="active",
        required=True,
        tracking=True,
    )
    enrollment_date = fields.Date(
        string="Enrollment Date",
        default=fields.Date.context_today,
        required=True,
    )
    portal_password_set = fields.Boolean(
        string="Portal Password Set",
        default=False,
        copy=False,
        readonly=True,
    )
    active = fields.Boolean(
        string="Active",
        default=True,
    )
    notes = fields.Text(string="Notes")

    # ── Relational Fields
    application_id = fields.Many2one(
        comodel_name="education.application",
        string="Application",
        required=True,
        ondelete="restrict",
        readonly=True,
        index=True,
    )
    program_id = fields.Many2one(
        comodel_name="education.program",
        string="Program",
        required=True,
        tracking=True,
        ondelete="restrict",
    )
    academic_year_id = fields.Many2one(
        comodel_name="education.academic.year",
        string="Academic Year",
        required=True,
        tracking=True,
        ondelete="restrict",
    )
    class_id = fields.Many2one(
        comodel_name="education.class",
        string="Class / Section",
        tracking=True,
        ondelete="restrict",
        domain="[('program_id', '=', program_id), ('academic_year_id', '=', "
               "academic_year_id)]",
    )
    student_partner_id = fields.Many2one(
        comodel_name="res.partner",
        string="Student Portal Account",
        readonly=True,
        copy=False,
        help="Created when application is approved.",
    )
    student_user_id = fields.Many2one(
        comodel_name="res.users",
        string="Student Portal User",
        readonly=True,
        copy=False,
        help="Created when portal access is granted.",
    )
    guardian_partner_id = fields.Many2one(
        comodel_name="res.partner",
        string="Guardian Portal Account",
        readonly=True,
        copy=False,
    )
    company_id = fields.Many2one(
        comodel_name="res.company",
        string="Institution",
        related='application_id.company_id'
    )
    document_ids = fields.One2many(
        comodel_name="education.document",
        inverse_name="enrollment_id",
        string="Documents",
    )
    admission_fee = fields.Float(
        string="Admission Fee",
        related="application_id.admission_fee",
        readonly=True,
    )
    admission_fee_invoice_id = fields.Many2one(
        comodel_name="account.move",
        related="application_id.admission_fee_invoice_id",
        string="Admission Fee Invoice",
    )

    # ── Related Fields
    student_name = fields.Char(
        string="Student Name",
        related="application_id.name",
        store=True,
        readonly=True,
    )
    student_email = fields.Char(
        string="Student Email",
        related="application_id.email",
        store=True,
        readonly=True,
    )
    date_of_birth = fields.Date(
        string="Date of Birth",
        related="application_id.date_of_birth",
        store=True,
        readonly=True,
    )
    photo = fields.Image(
        string="Photo",
        related="application_id.photo",
        store=False,
        readonly=True,
    )
    guardian_name = fields.Char(
        string="Guardian Name",
        related="application_id.guardian_name",
        store=True,
        readonly=True,
    )
    guardian_phone = fields.Char(
        string="Guardian Phone",
        related="application_id.guardian_phone",
        store=True,
        readonly=True,
    )
    guardian_email = fields.Char(
        string="Guardian Email",
        related="application_id.guardian_email",
        store=True,
        readonly=True,
    )
    department_id = fields.Many2one(
        comodel_name="education.department",
        string="Department",
        related="program_id.department_id",
        store=True,
        readonly=True,
    )

    # ── Computed Fields
    display_name = fields.Char(
        string="Display Name",
        compute="_compute_display_name",
        store=True,
        help="Shows student name + enrollment no. for easy identification.",
    )
    document_count = fields.Integer(
        string="Document Count",
        compute="_compute_document_count",
    )
    doc_completion_pct = fields.Integer(
        string="Doc Completion %",
        compute="_compute_doc_completion",
        help="Percentage of documents verified.",
    )
    fee_count = fields.Integer(
        string="Invoices",
        compute="_compute_fee_count",
    )
    attendance_pct = fields.Float(
        string="Attendance %",
        compute="_compute_attendance_pct",
        store=False,
        help="% of periods marked Present or Late vs total recorded periods.",
    )
    attendance_warning = fields.Boolean(
        string="Below 75%",
        compute="_compute_attendance_pct",
        store=False,
    )

    # ── SQL Constraints
    _enrollment_no_uniq = models.Constraint(
        "UNIQUE(enrollment_no, company_id)",
        "Enrollment number must be unique.",
    )
    _application_year_uniq = models.Constraint(
        "UNIQUE(application_id, academic_year_id)",
        "A student can only be enrolled once per academic year.",
    )

    # ── ORM Overrides
    @api.model_create_multi
    def create(self, vals_list):
        """Override create to assign auto-generated enrollment number."""
        sequence = self.env["ir.sequence"].sudo().search(
            [("code", "=", "education.enrollment"),
             ("company_id", "=", self.env.company.id)])
        if not sequence:
            sequence.sudo().create({
                "code": "education.enrollment",
                "name": "Student Enrollment",
                "prefix": "ENR/%(year)s/",
                "padding": 5,
                "number_increment": 1,
                "number_next": 1,
                "company_id": self.env.company.id,

            })
        for vals in vals_list:
            if vals.get("enrollment_no", "New") == "New":
                vals["enrollment_no"] = (
                        sequence.next_by_code("education.enrollment")
                        or "New"
                )
        return super().create(vals_list)

    # ── Compute Methods
    @api.depends("student_name", "enrollment_no")
    def _compute_display_name(self):
        """Build display name as 'Student Name (Enrollment No)'."""
        for rec in self:
            if rec.student_name and rec.enrollment_no:
                rec.display_name = f"{rec.student_name} ({rec.enrollment_no})"
            else:
                rec.display_name = rec.enrollment_no or "New"

    @api.depends("document_ids")
    def _compute_document_count(self):
        """Count linked document records for this enrollment."""
        for rec in self:
            rec.document_count = len(rec.document_ids)

    @api.depends("document_ids", "document_ids.state")
    def _compute_doc_completion(self):
        """Calculate percentage of verified documents vs total required."""
        for rec in self:
            total = len(rec.document_ids)
            if not total:
                rec.doc_completion_pct = 0
            else:
                verified = rec.document_ids.filtered(
                    lambda d: d.state == "verified")
                rec.doc_completion_pct = int(len(verified) / total * 100)

    @api.depends("student_partner_id")
    def _compute_fee_count(self):
        """Batched calculation of outgoing invoices per student."""
        partner_ids = self.student_partner_id.ids
        if not partner_ids:
            for rec in self:
                rec.fee_count = 0
            return

        invoice_data = self.env["account.move"]._read_group(
            domain=[
                ("partner_id", "in", partner_ids),
                ("move_type", "=", "out_invoice"),
                ("invoice_type", "!=", False),
            ],
            groupby=["partner_id"],
            aggregates=["__count"],
        )
        counts = {partner.id: count for partner, count in invoice_data}
        for rec in self:
            rec.fee_count = counts.get(rec.student_partner_id.id, 0)

    def _compute_attendance_pct(self):
        """Batched calculation of student attendance percentages and warning
        threshold."""
        enrollment_ids = self.ids
        if not enrollment_ids:
            for rec in self:
                rec.attendance_pct = 100.0
                rec.attendance_warning = False
            return

        Att = self.env["education.attendance"]
        total_data = Att._read_group(
            domain=[
                ("enrollment_id", "in", enrollment_ids),
                ("state", "!=", "holiday"),
                ("academic_year_id", "=",
                 self.env["education.academic.year"].get_current_year())
            ],
            groupby=["enrollment_id"],
            aggregates=["__count"],
        )
        total_map = {enr.id: count for enr, count in total_data}

        present_data = Att._read_group(
            domain=[
                ("enrollment_id", "in", enrollment_ids),
                ("state", "in", ("present", "late", "excused")),
            ],
            groupby=["enrollment_id"],
            aggregates=["__count"],
        )
        present_map = {enr.id: count for enr, count in present_data}

        for rec in self:
            total = total_map.get(rec.id, 0)
            if not total:
                rec.attendance_pct = 100.0
                rec.attendance_warning = False
            else:
                present = present_map.get(rec.id, 0)
                pct = (present / total) * 100
                rec.attendance_pct = round(pct, 1)
                rec.attendance_warning = pct < 75.0

    # ── Action Methods
    def action_view_fees(self, invoice_id=None):
        """View all fee invoices for this student."""
        self.ensure_one()
        if invoice_id:
            return {
                "name": _("Fees"),
                "view_mode": "form",
                "res_model": "account.move",
                "res_id": invoice_id,
                "type": "ir.actions.act_window",
                "context": {
                    "default_partner_id": self.student_partner_id.id,
                    "default_move_type": "out_invoice",
                    "default_invoice_type": "general",
                },
            }
        return {
            "name": _("Fees"),
            "view_mode": "list,form",
            "res_model": "account.move",
            "type": "ir.actions.act_window",
            "views": [
                (self.env.ref(
                    "education_core.education_fee_invoice_status").id, "list"),
                (False, "form"),
            ],
            "domain": [
                ("partner_id", "=", self.student_partner_id.id),
                ("move_type", "=", "out_invoice"),
                ("invoice_type", "!=", False),
            ],
            "context": {
                "default_partner_id": self.student_partner_id.id,
                "default_move_type": "out_invoice",
                "default_invoice_type": "general",
            },
        }

    def action_pay_fee(self):
        """Create an admission fee invoice and open it for review."""
        product = self.env.ref("education_core.product_fee_admission")
        invoice = self.env["account.move"].create({
            "move_type": "out_invoice",
            "invoice_type": 'admission_fee',
            "invoice_date": fields.Date.today(),
            "partner_id": self.student_partner_id.id,
            "enrollment_id": self.id,
            "invoice_line_ids": [fields.Command.create({
                "product_id": product.id if product else False,
                "name": _("Admission Fee"),
                "quantity": 1,
                "price_unit": self.admission_fee,
            })],
        })
        self.application_id.admission_fee_invoice_id = invoice.id
        return self.action_view_fees(invoice.id)

    def action_grant_portal_access(self):
        """Create res.partner for student and send portal invitation."""
        for rec in self:
            if rec.student_partner_id.user_ids:
                raise UserError(
                    _(
                        "Portal access has already been granted for "
                        "enrollment %(number)s.",
                        number=rec.enrollment_no,
                    )
                )
            partner = rec.student_partner_id
            wizard = self.env["portal.wizard"].create({
                "partner_ids": [(4, partner.id)],
            })
            wizard_user = wizard.user_ids.filtered(
                lambda u: u.partner_id == partner)
            if wizard_user:
                wizard_user.action_grant_access()
                rec.student_user_id = rec.student_partner_id.user_ids[:1]
            rec.message_post(
                body=_(
                    "Portal access granted. Login invitation sent to %("
                    "email)s.",
                    email=partner.email or _("(no email)"),
                ),
            )

    def action_set_portal_password(self):
        """Open the wizard to set/reset the student's portal password
        directly."""
        self.ensure_one()
        if not self.student_partner_id:
            raise UserError(
                _(
                    "Grant portal access first — no portal account exists "
                    "for enrollment %(number)s.",
                    number=self.enrollment_no,
                )
            )
        user = self.student_partner_id.user_ids[:1]
        if not user:
            raise UserError(
                _("No portal user is linked to this student yet. Use 'Grant "
                  "Portal Access' first.")
            )
        return {
            "type": "ir.actions.act_window",
            "name": _("Set Portal Password"),
            "res_model": "education.portal.password",
            "view_mode": "form",
            "target": "new",
            "context": {
                "default_enrollment_id": self.id,
                "default_user_id": user.id,
            },
        }

    def action_suspend(self):
        """Set enrollment state to suspended."""
        self.write({"state": "suspended"})

    def action_reactivate(self):
        """Reactivate a previously suspended enrollment."""
        self.write({"state": "active"})

    def action_graduate(self):
        """Mark enrollment as graduated and archive the record."""
        self.write({"state": "graduated", "active": False})
        self.remove_portal_access()

    def action_withdraw(self):
        """Mark enrollment as withdrawn and archive the record."""
        self.write({"state": "withdrawn", "active": False})
        self.remove_portal_access()

    def action_view_application(self):
        """Open the originating application record in form view."""
        self.ensure_one()
        return {
            "type": "ir.actions.act_window",
            "name": _("Application"),
            "res_model": "education.application",
            "res_id": self.application_id.id,
            "view_mode": "form",
            "target": "current",
        }

    def remove_portal_access(self):
        """Archive student portal user and partner upon graduation or
        withdrawal."""
        for rec in self:
            if rec.student_partner_id:
                users = self.env["res.users"].search([
                    ("partner_id", "=", rec.student_partner_id.id),
                ])
                users.action_archive()
                rec.student_partner_id.action_archive()

    # ── Cron Jobs
    @api.model
    def _cron_attendance_threshold_check(self):
        """Cron entry point — runs daily.

        Finds all active enrollments below 75% attendance and sends alerts.
        """
        active_enrollments = self.search([("state", "=", "active")])
        template = self.env.ref(
            "education_core.mail_template_attendance_warning",
            raise_if_not_found=False,
        )
        active_enrollments._compute_attendance_pct()
        for enr in active_enrollments:
            if enr.attendance_warning:
                enr.message_post(
                    body=_(
                        "⚠️ Attendance Alert: %(name)s attendance is %("
                        "pct).1f%% "
                        "(below the 75%% threshold).",
                        name=enr.student_name,
                        pct=enr.attendance_pct,
                    ),
                    message_type="comment",
                )
                if template and enr.guardian_email:
                    template.send_mail(enr.id, force_send=False)
