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
"""education.document.type — Configurable document types (Birth Certificate, 
etc.).

education.document      — Uploaded student document with verification workflow.
"""
import base64
from odoo import api, fields, models, _
from odoo.exceptions import ValidationError

ALLOWED_DOCUMENT_EXTENSIONS = (".pdf", ".jpg", ".jpeg", ".png")
MAX_DOCUMENT_FILE_SIZE = 5 * 1024 * 1024  # 5 MB in bytes


class EducationDocumentType(models.Model):
    """Master list of document types required during admission."""

    _name = "education.document.type"
    _description = "Document Type"
    _order = "sequence, name"

    # ── Standard Fields   
    name = fields.Char(
        string="Document Type",
        required=True,
        translate=True,
    )
    code = fields.Char(
        string="Code",
        size=20,
        help="Short code, e.g. BIRTH_CERT, MARK_SHEET.",
    )
    sequence = fields.Integer(default=10)
    is_mandatory = fields.Boolean(
        string="Mandatory",
        default=False,
        help="If checked, applicants must upload this document before "
             "approval.",
    )
    description = fields.Text(
        string="Description / Instructions",
        translate=True,
    )
    active = fields.Boolean(
        string="Active",
        default=True,
    )

    # ── SQL Constraints   
    _code_uniq = models.Constraint(
        "UNIQUE(code)",
        "Document type code must be unique.",
    )


class EducationDocument(models.Model):
    """A single document uploaded by or for a student."""

    _name = "education.document"
    _description = "Student Document"
    _inherit = ["mail.thread"]
    _order = "document_type_id, id"

    # ── Standard Fields   
    file = fields.Binary(
        string="File",
        attachment=True,
        help="Upload PDF, JPG, JPEG, or PNG (max 5 MB).",
    )
    file_name = fields.Char(string="File Name")
    issue_date = fields.Date(string="Issue Date")
    expiry_date = fields.Date(string="Expiry Date")
    state = fields.Selection(
        selection=[
            ("pending", "Pending Upload"),
            ("uploaded", "Uploaded — Pending Review"),
            ("verified", "Verified"),
            ("rejected", "Rejected / Resubmit"),
        ],
        string="Status",
        default="pending",
        required=True,
        tracking=True,
    )
    verified_date = fields.Date(
        string="Verified On",
        readonly=True,
    )
    remarks = fields.Text(
        string="Remarks",
        help="Reviewer notes / rejection reason.",
    )
    active = fields.Boolean(
        string="Active",
        default=True,
    )

    # ── Relational Fields
    application_id = fields.Many2one(
        comodel_name="education.application",
        string="Application",
        ondelete="cascade",
        index=True,
    )
    enrollment_id = fields.Many2one(
        comodel_name="education.enrollment",
        string="Enrollment",
        ondelete="cascade",
        index=True,
    )
    document_type_id = fields.Many2one(
        comodel_name="education.document.type",
        string="Document Type",
        required=True,
        ondelete="restrict",
    )
    verified_by_id = fields.Many2one(
        comodel_name="res.users",
        string="Verified By",
        readonly=True,
    )

    # ── Related Fields   ─
    student_name = fields.Char(
        string="Student Name",
        related="enrollment_id.student_name",
        readonly=True,
    )
    academic_year_id = fields.Many2one(
        comodel_name="education.academic.year",
        string="Academic Year",
        related="enrollment_id.academic_year_id",
        readonly=True,
    )
    is_mandatory = fields.Boolean(
        string="Mandatory",
        related="document_type_id.is_mandatory",
        store=True,
        readonly=True,
    )
    company_id = fields.Many2one(
        comodel_name="res.company",
        string="Institution",
        related="enrollment_id.company_id",
    )

    # ── Computed Fields   
    name = fields.Char(
        string="Document Reference",
        compute="_compute_name",
        store=True,
    )

    # ── Compute Methods   
    @api.depends(
        "document_type_id.name",
        "application_id.admission_no",
        "enrollment_id.enrollment_no",
    )
    def _compute_name(self):
        """Auto-generate document name from type and
        application/enrollment ref."""
        for rec in self:
            ref = (
                    rec.application_id.admission_no
                    or rec.enrollment_id.enrollment_no
                    or "—"
            )
            doc_type = rec.document_type_id.name or _("Document")
            rec.name = f"{doc_type} [{ref}]"

    # ── Constraints   ────
    @api.constrains("file", "file_name")
    def _check_file_and_size(self):
        """Ensure uploaded file is an allowed type (PDF, JPG, JPEG, PNG) and 
        does not exceed 5 MB."""
        for rec in self:
            if not rec.file:
                continue

            # 1. File extension validation
            if rec.file_name and not rec.file_name.lower().endswith(
                    ALLOWED_DOCUMENT_EXTENSIONS):
                raise ValidationError(
                    _(
                        "Only PDF, JPG, JPEG, and PNG files are allowed for "
                        "'%(doc)s' (received: %(filename)s).",
                        doc=rec.document_type_id.name or _("Document"),
                        filename=rec.file_name,
                    )
                )

            # 2. File size validation
            try:
                file_bytes = base64.b64decode(rec.file)
            except Exception:
                raise ValidationError(_("Corrupted file content uploaded."))

            if len(file_bytes) > MAX_DOCUMENT_FILE_SIZE:
                file_size_mb = round(len(file_bytes) / (1024 * 1024), 2)
                raise ValidationError(
                    _(
                        "The file size for '%(doc)s' is %(size)s MB, "
                        "which exceeds the maximum allowed limit of 5 MB.",
                        doc=rec.document_type_id.name or _("Document"),
                        size=file_size_mb,
                    )
                )

    @api.constrains("file", "state")
    def _check_file_on_upload(self):
        """Require a file attachment when state is uploaded or verified."""
        for rec in self:
            if rec.state in ("uploaded", "verified") and not rec.file:
                raise ValidationError(
                    _(
                        "Document '%(name)s' must have a file attached "
                        "before marking as uploaded.",
                        name=rec.document_type_id.name or _("Document"),
                    )
                )

    @api.constrains("issue_date", "expiry_date")
    def _check_dates(self):
        """Ensure expiry date is after the issue date."""
        for rec in self:
            if (rec.issue_date and rec.expiry_date and rec.expiry_date <=
                    rec.issue_date):
                raise ValidationError(
                    _(
                        "Expiry Date must be after Issue Date for document "
                        "'%(name)s'.",
                        name=rec.document_type_id.name or _("Document"),
                    )
                )

    # ── CRUD Methods   ───
    @api.model_create_multi
    def create(self, vals_list):
        """Sets the state to uploaded if file exists"""
        for vals in vals_list:
            if vals.get("file") and vals.get("state", "pending") == "pending":
                vals["state"] = "uploaded"
        return super().create(vals_list)

    def write(self, vals):
        """Sets the state to uploaded if file exists"""
        res = super().write(vals)
        if "file" in vals and "state" not in vals:
            if vals.get("file"):
                to_upload = self.filtered(lambda r: r.state == "pending")
                if to_upload:
                    super(EducationDocument, to_upload).write(
                        {"state": "uploaded"})
            else:
                to_pending = self.filtered(lambda r: r.state == "uploaded")
                if to_pending:
                    super(EducationDocument, to_pending).write(
                        {"state": "pending"})
        return res

    # ── Action Methods   ─
    def action_mark_uploaded(self):
        """Transition document state to uploaded after verifying file exists."""
        for rec in self:
            if not rec.file:
                raise ValidationError(
                    _(
                        "Please attach a file before marking '%(name)s' as "
                        "uploaded.",
                        name=rec.document_type_id.name or _("Document"),
                    )
                )
        self.write({"state": "uploaded"})

    def action_verify(self):
        """Mark the document as verified and record the verifier details."""
        self.write({
            "state": "verified",
            "verified_by_id": self.env.uid,
            "verified_date": fields.Date.context_today(self),
        })

    def action_reject_doc(self):
        """Reject the document and reset its state to rejected."""
        self.write({"state": "rejected"})
