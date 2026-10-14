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
"""education.application — Student Admission Application.

State machine: draft → submitted → approved / rejected
On approval: auto-creates education.enrollment and portal account.
"""
from odoo import api, fields, models, _
from odoo.exceptions import ValidationError, UserError
from odoo.tools import config
from odoo.addons.phone_validation.tools import phone_validation
import phonenumbers


class EducationApplication(models.Model):
    """Student admission application with full state machine."""

    _name = "education.application"
    _description = "Student Application"
    _inherit = ["mail.thread", "mail.activity.mixin"]
    _order = "date_application desc, admission_no desc"
    _rec_name = "admission_no"

    # ── Standard Fields ───────────────────────────────────────────────
    admission_no = fields.Char(
        string="Application No.",
        readonly=True,
        copy=False,
        default="New",
        tracking=True,
        help="Unique auto-generated application reference number "
             "(e.g. ADM/2025/00001).",
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
        help="Workflow status of the application: Draft -> Submitted -> "
             "Approved or Rejected.",
    )
    date_application = fields.Date(
        string="Application Date",
        default=fields.Date.context_today,
        readonly=True,
        tracking=True,
        help="Date on which this application was created.",
    )
    first_name = fields.Char(
        string="First Name",
        required=True,
        tracking=True,
        help="Applicant's given name as it appears on official documents.",
    )
    last_name = fields.Char(
        string="Last Name",
        tracking=True,
        help="Applicant's family name or surname.",
    )
    date_of_birth = fields.Date(
        string="Date of Birth",
        required=True,
        tracking=True,
        help="Applicant's date of birth. Must be in the past. "
             "Used to calculate age.",
    )
    gender = fields.Selection(
        selection=[
            ("male", "Male"),
            ("female", "Female"),
            ("other", "Other / Prefer not to say"),
        ],
        string="Gender",
        required=True,
        help="Applicant's gender identity.",
    )
    blood_group = fields.Selection(
        selection=[
            ("a+", "A+"), ("a-", "A−"),
            ("b+", "B+"), ("b-", "B−"),
            ("ab+", "AB+"), ("ab-", "AB−"),
            ("o+", "O+"), ("o-", "O−"),
        ],
        string="Blood Group",
        help="Applicant's blood group for medical and emergency records.",
    )
    photo = fields.Image(
        string="Passport Photo",
        max_width=256,
        max_height=256,
        help="Passport-size photograph of the applicant (max 256x256 px).",
    )
    email = fields.Char(
        string="Email",
        required=True,
        tracking=True,
        help="Applicant's email address used for notifications and portal "
             "account creation.",
    )
    phone = fields.Char(
        string="Phone",
        required=True,
        help="Primary contact phone number of the applicant.",
    )
    mobile = fields.Char(
        string="Mobile",
        help="Mobile number of the applicant for SMS notifications.",
    )
    address = fields.Text(
        string="Address",
        help="Residential or mailing address of the applicant.",
    )
    city = fields.Char(
        string="City",
        help="City of residence of the applicant.",
    )
    zip_code = fields.Char(
        string="ZIP Code",
        size=10,
        help="Postal/ZIP code of the applicant's address.",
    )
    last_school = fields.Char(
        string="Last School / College",
        help="Name of the institution the applicant last attended.",
    )
    last_qualification = fields.Char(
        string="Qualification Obtained",
        help="Highest academic qualification the applicant has already "
             "completed (e.g. 10+2, Diploma, B.Sc).",
    )
    last_percentage = fields.Float(
        string="Percentage / GPA",
        digits=(5, 2),
        help="Overall score in last qualification (0–100 or GPA scale).",
    )
    guardian_name = fields.Char(
        string="Guardian Name",
        tracking=True,
        help="Full name of the applicant's parent or legal guardian.",
    )
    guardian_relation = fields.Selection(
        selection=[
            ("father", "Father"),
            ("mother", "Mother"),
            ("spouse", "Spouse"),
            ("sibling", "Sibling"),
            ("legal_guardian", "Legal Guardian"),
            ("other", "Other"),
        ],
        string="Relationship",
        help="Relationship of the guardian to the applicant.",
    )
    guardian_phone = fields.Char(
        string="Guardian Phone",
        help="Contact phone number of the guardian for urgent "
             "communications.",
    )
    guardian_email = fields.Char(
        string="Guardian Email",
        help="Email address of the guardian for notifications and portal "
             "access.",
    )
    guardian_occupation = fields.Char(
        string="Guardian Occupation",
        help="Occupation or profession of the guardian.",
    )
    rejection_reason = fields.Text(
        string="Rejection Reason",
        readonly=True,
        help="Reason provided by the reviewer when rejecting this "
             "application.",
    )
    rejection_date = fields.Date(
        string="Rejection Date",
        readonly=True,
        help="Date on which this application was formally rejected.",
    )
    active = fields.Boolean(
        string="Active",
        default=True,
        help="Uncheck to archive this application without deleting it.",
    )
    notes = fields.Text(
        string="Internal Notes",
        help="Internal reviewer notes not visible to the applicant.",
    )

    # ── Relational Fields ─────────────────────────────────────────────
    nationality_id = fields.Many2one(
        comodel_name="res.country",
        string="Nationality",
        help="Country of citizenship/nationality of the applicant.",
    )
    country_id = fields.Many2one(
        comodel_name="res.country",
        string="Country",
        help="Country of residence of the applicant.",
    )
    state_id = fields.Many2one(
        comodel_name="res.country.state",
        string="State / Province",
        domain="[('country_id', '=', country_id)]",
        help="State or province within the applicant's selected country.",
    )
    program_id = fields.Many2one(
        comodel_name="education.program",
        string="Applied Program",
        required=True,
        tracking=True,
        ondelete="restrict",
        help="Academic program the applicant is applying for.",
    )
    academic_year_id = fields.Many2one(
        comodel_name="education.academic.year",
        string="Academic Year",
        required=True,
        tracking=True,
        ondelete="restrict",
        default=lambda self: self.env[
            "education.academic.year"].get_current_year(),
        help="Academic year for which admission is being requested.",
    )
    department_id = fields.Many2one(
        comodel_name="education.department",
        string="Department",
        related="program_id.department_id",
        store=True,
        readonly=True,
        help="Department derived from the applied program.",
    )
    document_ids = fields.One2many(
        comodel_name="education.document",
        inverse_name="application_id",
        string="Documents",
        default=lambda self: self._default_documents(),
        help="Documents submitted with the application. Mandatory document "
             "types are pre-populated automatically.",
    )
    rejected_by_id = fields.Many2one(
        comodel_name="res.users",
        string="Rejected By",
        readonly=True,
        help="User who rejected this application.",
    )
    enrollment_id = fields.Many2one(
        comodel_name="education.enrollment",
        string="Enrollment",
        readonly=True,
        copy=False,
        help="Enrollment record created automatically when this application "
             "is approved.",
    )
    company_id = fields.Many2one(
        comodel_name="res.company",
        string="Institution",
        related="academic_year_id.company_id",
        help="Institution derived from the selected academic year.",
    )

    # ── Computed Fields ───────────────────────────────────────────────
    name = fields.Char(
        string="Full Name",
        compute="_compute_name",
        store=True,
        help="Computed: First Name + Last Name.",
    )
    age = fields.Integer(
        string="Age",
        compute="_compute_age",
        help="Calculated age of the applicant based on date of birth.",
    )
    document_count = fields.Integer(
        string="Documents",
        compute="_compute_document_count",
        help="Number of documents submitted with this application.",
    )
    admission_fee = fields.Float(
        string="Admission Fee",
        default=0.0,
        help="One-time admission fee charged to the applicant upon approval.",
    )
    admission_fee_invoice_id = fields.Many2one(
        comodel_name="account.move",
        string="Admission Fee Invoice",
        help="Invoice generated for the admission fee payment.",
    )

    # ── SQL Constraints ───────────────────────────────────────────────
    _admission_no_uniq = models.Constraint(
        "UNIQUE(admission_no, company_id)",
        "Application number must be unique.",
    )

    # ── Compute Methods ───────────────────────────────────────────────
    @api.depends("first_name", "last_name")
    def _compute_name(self):
        """Build full applicant name from first and last name fields."""
        for rec in self:
            parts = filter(None, [rec.first_name, rec.last_name])
            rec.name = " ".join(parts) or False

    @api.depends("date_of_birth")
    def _compute_age(self):
        """Compute applicant age in years from date of birth."""
        today = fields.Date.context_today(self)
        for rec in self:
            if rec.date_of_birth:
                rec.age = (today - rec.date_of_birth).days // 365
            else:
                rec.age = 0

    @api.depends("document_ids")
    def _compute_document_count(self):
        """Count linked documents submitted with this application."""
        for rec in self:
            rec.document_count = len(rec.document_ids)

    # ── Default Methods ───────────────────────────────────────────────
    @api.model
    def _default_documents(self):
        """Generate default document lines for all mandatory document
        types.
        """
        mandatory_types = self.env["education.document.type"].search([
            ("is_mandatory", "=", True),
            ("active", "=", True),
        ], order="sequence, id")
        return [
            fields.Command.create({
                "document_type_id": doc_type.id,
                "state": "pending",
            })
            for doc_type in mandatory_types
        ]

    # ── Constraints ───────────────────────────────────────────────────
    @api.constrains("date_of_birth")
    def _check_dob(self):
        """Ensure date of birth is in the past."""
        today = fields.Date.context_today(self)
        for rec in self:
            if rec.date_of_birth and rec.date_of_birth >= today:
                raise ValidationError(
                    _(
                        "Date of Birth must be in the past for applicant '%("
                        "name)s'.",
                        name=rec.name,
                    )
                )

    @api.constrains("last_percentage")
    def _check_percentage(self):
        """Ensure last academic percentage is between 0 and 100."""
        for rec in self:
            if rec.last_percentage and not (0 <= rec.last_percentage <= 100):
                raise ValidationError(
                    _(
                        "Percentage must be between 0 and 100 for applicant "
                        "'%(name)s'.",
                        name=rec.name,
                    )
                )

    # ── Phone Validation ──────────────────────────────────────────────
    @api.constrains("phone", "mobile", "guardian_phone", "country_id")
    def _check_phone_numbers(self):
        """Validate phone/mobile/guardian_phone structure (length, prefix
        rules) per selected country."""
        for rec in self:
            if not rec.country_id:
                continue  # nothing to validate against yet
            for fname in ("phone", "mobile", "guardian_phone"):
                number = rec[fname]
                if not number:
                    continue
                try:
                    phone_nbr = phone_validation.phone_parse(
                        number, rec.country_id.code)
                except UserError as e:
                    raise ValidationError(
                        _(
                            "%(field)s: %(error)s",
                            field=rec._fields[fname].string,
                            error=str(e),
                        )
                    )
                # phone_parse() only guarantees the string is *parseable* in
                # some Odoo
                # versions — it does not always enforce that the number of
                # digits is
                # actually correct for the country. Check validity
                # explicitly so a
                # too-short/too-long number is always rejected.
                if not phonenumbers.is_valid_number(phone_nbr):
                    raise ValidationError(
                        _(
                            "'%(number)s' is not a valid %(field)s number "
                            "for %(country)s "
                            "(wrong number of digits).",
                            number=number,
                            field=rec._fields[fname].string,
                            country=rec.country_id.name,
                        )
                    )
                # A number that already carries its own "+<calling code>" (
                # e.g. after
                # being formatted for a different Country) can still pass
                # is_valid_number()
                # above even when Country has since been changed, because a
                # leading '+'
                # makes phonenumbers trust the embedded calling code over
                # the region hint.
                # Explicitly confirm the number's calling code matches the
                # selected Country.
                if phone_nbr.country_code != rec.country_id.phone_code:
                    raise ValidationError(
                        _(
                            "'%(number)s' has the calling code for a "
                            "different country "
                            "than %(country)s. Please update the %(field)s "
                            "to match "
                            "the selected Country.",
                            number=number,
                            field=rec._fields[fname].string,
                            country=rec.country_id.name,
                        )
                    )

    @api.onchange("phone", "mobile", "guardian_phone", "country_id")
    def _onchange_format_phone_numbers(self):
        """Reformat phone/mobile/guardian_phone into international display
        format once a Country is set.
        Uses phonenumbers directly (rather than
        phone_validation.phone_format) so that
        an invalid number explicitly yields False instead of silently
        falling back to
        the original, unformatted string.
        """
        if not self.country_id:
            return
        for fname in ("phone", "mobile", "guardian_phone"):
            number = self[fname]
            if not number:
                continue
            try:
                phone_nbr = phonenumbers.parse(
                    number, region=self.country_id.code)
                formatted = (
                    phonenumbers.format_number(
                        phone_nbr,
                        phonenumbers.PhoneNumberFormat.INTERNATIONAL)
                    if phonenumbers.is_valid_number(phone_nbr)
                    else False
                )
            except phonenumbers.phonenumberutil.NumberParseException:
                formatted = False
            if formatted:
                self[fname] = formatted

    # ── ORM Overrides (CRUD) ──────────────────────────────────────────
    @api.model_create_multi
    def create(self, vals_list):
        """Override create to assign auto-generated admission number."""
        sequence = self.env["ir.sequence"].sudo().search(
            [("code", "=", "education.application"),
             ("company_id", "=", self.env.company.id)])
        if not sequence:
            sequence = self.env["ir.sequence"].sudo().create({
                "code": "education.application",
                "company_id": self.env.company.id,
                "name": "Student Application",
                "prefix": "ADM/%(year)s/",
                "padding": 5,
                "number_increment": 1,
                "number_next": 1,
            })
        for vals in vals_list:
            if vals.get("admission_no", "New") == "New":
                vals["admission_no"] = (
                        sequence.next_by_code("education.application")
                        or "New"
                )
        return super().create(vals_list)

    # ── Action Methods ────────────────────────────────────────────────
    def action_submit(self):
        """Student or Admission Officer submits the application."""
        non_draft = self.filtered(lambda r: r.state != "draft")
        if non_draft:
            raise ValidationError(
                _("Only Draft applications can be submitted."))
        self.write({"state": "submitted"})
        template = self.env.ref(
            "education_core.mail_template_application_received",
            raise_if_not_found=False,
        )
        if template:
            for rec in self:
                template.send_mail(rec.id, force_send=False)

    def action_approve(self, class_id=False):
        """Approve the application.

        When invoked from the user interface, opens the approval wizard
        so that the user can select or create a class/section for the student's
        enrollment.
        In automated/test environments or when class_id is passed, completes
        approval directly.
        """
        self.ensure_one()
        if self.state != "submitted":
            raise ValidationError(
                _("Only Submitted applications can be approved."))

        if class_id or self.env.context.get("direct_approve") or (
                config.get("test_enable") and not self.env.context.get(
            "test_approve_wizard")
        ):
            return self._perform_approve(class_id=class_id)

        return {
            "type": "ir.actions.act_window",
            "name": _("Approve Application"),
            "res_model": "education.application.approve",
            "view_mode": "form",
            "target": "new",
            "context": {
                "default_application_id": self.id,
            },
        }

    def _perform_approve(self, class_id=False):
        """Execute approval and auto-create enrollment with assigned class."""
        self.ensure_one()
        if self.state != "submitted":
            raise ValidationError(
                _("Only Submitted applications can be approved."))

        template = self.env.ref(
            "education_core.mail_template_application_approved",
            raise_if_not_found=False,
        )

        enrollment_vals = {
            "application_id": self.id,
            "program_id": self.program_id.id,
            "academic_year_id": self.academic_year_id.id,
            "company_id": self.company_id.id,
            "admission_fee_invoice_id": self.admission_fee_invoice_id.id,
            "admission_fee": self.admission_fee,
        }
        if class_id:
            enrollment_vals["class_id"] = class_id.id if hasattr(class_id,
                                                                 "id") else (
                class_id)

        enrollment = self.env["education.enrollment"].create(enrollment_vals)
        partner = self.env["res.partner"].create({
            "name": enrollment.student_name,
            "email": enrollment.student_email,
            "is_company": False,
            "type": "contact",
            "comment": _(
                "Auto-created for enrollment %(enrollment_no)s",
                enrollment_no=enrollment.enrollment_no,
            ),
        })
        enrollment.student_partner_id = partner
        self.admission_fee_invoice_id.partner_id = partner.id,
        self.write({"state": "approved", "enrollment_id": enrollment.id})

        if self.document_ids:
            self.document_ids.write({"enrollment_id": enrollment.id})

        if template:
            template.send_mail(self.id, force_send=False)

        return enrollment

    def action_reject(self):
        """Open rejection wizard."""
        self.ensure_one()
        return {
            "type": "ir.actions.act_window",
            "name": _("Reject Application"),
            "res_model": "education.application.reject",
            "view_mode": "form",
            "target": "new",
            "context": {"default_application_id": self.id},
        }

    def action_reset_draft(self):
        """Allow re-submission after rejection."""
        rejected = self.filtered(lambda r: r.state == "rejected")
        rejected.write({
            "state": "draft",
            "rejection_reason": False,
            "rejected_by_id": False,
            "rejection_date": False,
        })

    def action_create_fee(self):
        """Create an admission fee invoice for this application."""
        product = self.env.ref("education_core.product_fee_admission")
        invoice = self.env["account.move"].create({
            "move_type": "out_invoice",
            "invoice_type": 'admission_fee',
            "invoice_date": fields.Date.today(),
            "invoice_line_ids": [fields.Command.create({
                "product_id": product.id if product else False,
                "name": _("Admission Fee"),
                "quantity": 1,
                "price_unit": self.admission_fee,
            })],
        })
        self.admission_fee_invoice_id = invoice.id
        return self.action_view_invoice()

    def action_view_enrollment(self):
        """Smart button to open the linked enrollment."""
        self.ensure_one()
        if not self.enrollment_id:
            return False
        return {
            "type": "ir.actions.act_window",
            "name": _("Enrollment"),
            "res_model": "education.enrollment",
            "res_id": self.enrollment_id.id,
            "view_mode": "form",
        }

    def action_view_invoice(self):
        """Open the admission fee invoice linked to this application."""
        self.ensure_one()
        if not self.admission_fee_invoice_id:
            return False
        return {
            "type": "ir.actions.act_window",
            "name": _("Admission Fee"),
            "res_model": "account.move",
            "res_id": self.admission_fee_invoice_id.id,
            "view_mode": "form",
            "target": "current",
        }
