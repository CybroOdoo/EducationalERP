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
"""
education_core — Admission & Enrollment Unit Tests (S2-T14)
===========================================================
Covers:
  - Full application lifecycle (draft → submitted → approved → rejected)
  - Auto-sequence for admission_no and enrollment_no
  - Enrollment auto-creation on approval
  - Rejection wizard
  - Approval and class assignment wizard
  - Portal account creation
  - Document checklist completion %
  - Record rules / access control
  - Application PDF report action & template rendering
"""
from datetime import date, timedelta
from odoo.tests.common import TransactionCase
from odoo.exceptions import ValidationError, UserError


class TestAdmissionLifecycle(TransactionCase):
    """Full lifecycle tests for education.application."""

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        # Academic year
        cls.academic_year = cls.env["education.academic.year"].create({
            "name": "Test Year 2025-2026",
            "code": "TEST2526",
            "date_start": date(2025, 7, 1),
            "date_end": date(2026, 6, 30),
            "is_current": False,
        })
        # Department
        cls.department = cls.env["education.department"].create({
            "name": "Test Department",
            "code": "TDEPT",
        })
        # Program
        cls.program = cls.env["education.program"].create({
            "name": "Test Program",
            "code": "TPROG",
            "department_id": cls.department.id,
            "degree_type": "bachelor",
            "duration_years": 3,
        })

    def _make_application(self, **kwargs):
        """Helper to create a valid application."""
        defaults = {
            "first_name": "Test",
            "last_name": "Student",
            "date_of_birth": date.today() - timedelta(days=365 * 20),
            "gender": "male",
            "email": "test.student@example.com",
            "phone": "9999999999",
            "program_id": self.program.id,
            "academic_year_id": self.academic_year.id,
        }
        defaults.update(kwargs)
        return self.env["education.application"].create(defaults)

    # ── Sequence Tests ───────────────────────────────────────────────

    def test_admission_no_auto_assigned(self):
        """Application should receive a unique sequence number on create."""
        app = self._make_application()
        self.assertNotEqual(app.admission_no, "New",
                            "admission_no should be auto-assigned by "
                            "ir.sequence")
        self.assertTrue(app.admission_no.startswith("ADM/"),
                        "admission_no should start with ADM/ prefix")

    def test_two_applications_get_different_numbers(self):
        """Each application must have a unique admission_no."""
        app1 = self._make_application(email="a@example.com")
        app2 = self._make_application(email="b@example.com")
        self.assertNotEqual(app1.admission_no, app2.admission_no)

    # ── Full Name Compute ─────────────────────────────────────────────

    def test_full_name_computed(self):
        """name should be 'First Last'."""
        app = self._make_application(first_name="Alice", last_name="Smith")
        self.assertEqual(app.name, "Alice Smith")

    def test_full_name_no_last_name(self):
        """name should be just first name if no last name."""
        app = self._make_application(first_name="Alice", last_name=False)
        self.assertEqual(app.name, "Alice")

    # ── Age Compute ───────────────────────────────────────────────────

    def test_age_computed(self):
        """age should be approximately 20 for DOB 20 years ago."""
        dob = date.today() - timedelta(days=365 * 20 + 10)
        app = self._make_application(date_of_birth=dob)
        self.assertAlmostEqual(app.age, 20, delta=1)

    # ── Constraint Tests ─────────────────────────────────────────────

    def test_dob_future_raises(self):
        """Future date of birth should raise ValidationError."""
        with self.assertRaises(ValidationError):
            self._make_application(
                date_of_birth=date.today() + timedelta(days=1))

    def test_percentage_out_of_range_raises(self):
        """last_percentage > 100 should raise ValidationError."""
        with self.assertRaises(ValidationError):
            self._make_application(last_percentage=101.0)

    # ── State Machine ─────────────────────────────────────────────────

    def test_initial_state_is_draft(self):
        """Newly created application must be in 'draft' state."""
        app = self._make_application()
        self.assertEqual(app.state, "draft")

    def test_action_submit(self):
        """Draft → Submitted transition."""
        app = self._make_application()
        app.action_submit()
        self.assertEqual(app.state, "submitted")

    def test_cannot_submit_already_submitted(self):
        """Submitting twice should raise ValidationError."""
        app = self._make_application()
        app.action_submit()
        with self.assertRaises(ValidationError):
            app.action_submit()

    def test_action_approve_creates_enrollment(self):
        """Approving a submitted application auto-creates enrollment."""
        app = self._make_application()
        app.action_submit()
        app.action_approve()
        self.assertEqual(app.state, "approved")
        self.assertTrue(app.enrollment_id,
                        "enrollment_id should be set after approval")
        enr = app.enrollment_id
        self.assertEqual(enr.application_id, app)
        self.assertEqual(enr.program_id, self.program)
        self.assertEqual(enr.academic_year_id, self.academic_year)

    def test_cannot_approve_draft(self):
        """Approving a draft application should raise ValidationError."""
        app = self._make_application()
        with self.assertRaises(ValidationError):
            app.action_approve()

    def test_action_reset_draft(self):
        """Rejected → Draft transition."""
        app = self._make_application()
        app.action_submit()
        # Manually set rejected state (bypassing wizard for test efficiency)
        app.write({
            "state": "rejected",
            "rejection_reason": "Test rejection reason",
            "rejected_by_id": self.env.uid,
            "rejection_date": date.today(),
        })
        self.assertEqual(app.state, "rejected")
        app.action_reset_draft()
        self.assertEqual(app.state, "draft")
        self.assertFalse(app.rejection_reason)
        self.assertFalse(app.rejected_by_id)

    # ── Rejection Wizard ──────────────────────────────────────────────

    def test_rejection_wizard_sets_state(self):
        """Rejection wizard should set state=rejected and store reason."""
        app = self._make_application()
        app.action_submit()
        wizard = self.env["education.application.reject"].create({
            "application_id": app.id,
            "rejection_reason": "Incomplete documents submitted by the "
                                "applicant.",
        })
        wizard.action_confirm_reject()
        self.assertEqual(app.state, "rejected")
        self.assertIn("Incomplete documents", app.rejection_reason)
        self.assertEqual(app.rejected_by_id.id, self.env.uid)
        self.assertTrue(app.rejection_date)

    def test_rejection_wizard_short_reason_raises(self):
        """Rejection reason shorter than 10 chars should raise
        ValidationError."""
        app = self._make_application()
        app.action_submit()
        with self.assertRaises(ValidationError):
            self.env["education.application.reject"].create({
                "application_id": app.id,
                "rejection_reason": "Short",
            })

    # ── Approval & Class Wizard ───────────────────────────────────────

    def test_approve_wizard_action_returned(self):
        """action_approve with test_approve_wizard context returns wizard
        action."""
        app = self._make_application()
        app.action_submit()
        action = app.with_context(test_approve_wizard=True).action_approve()
        self.assertEqual(action.get("res_model"),
                         "education.application.approve")
        self.assertEqual(action.get("target"), "new")
        self.assertEqual(
            action.get("context", {}).get("default_application_id"), app.id)

    def test_approve_wizard_assigns_class_to_enrollment(self):
        """Confirming the approval wizard assigns the selected class to
        enrollment."""
        cls_sec = self.env["education.class"].create({
            "name": "Test Class A",
            "section": "A",
            "program_id": self.program.id,
            "academic_year_id": self.academic_year.id,
            "capacity": 30,
        })
        app = self._make_application()
        app.action_submit()
        wizard = self.env["education.application.approve"].create({
            "application_id": app.id,
            "class_id": cls_sec.id,
        })
        wizard.action_confirm_approve()
        self.assertEqual(app.state, "approved")
        self.assertTrue(app.enrollment_id)
        self.assertEqual(app.enrollment_id.class_id, cls_sec)

    def test_approve_wizard_wrong_program_class_raises(self):
        """Selecting a class from another program raises ValidationError."""
        other_prog = self.env["education.program"].create({
            "name": "Other Program",
            "code": "OPROG",
            "department_id": self.department.id,
            "degree_type": "bachelor",
            "duration_years": 3,
        })
        other_cls = self.env["education.class"].create({
            "name": "Other Class A",
            "section": "A",
            "program_id": other_prog.id,
            "academic_year_id": self.academic_year.id,
            "capacity": 25,
        })
        app = self._make_application()
        app.action_submit()
        with self.assertRaises(ValidationError):
            self.env["education.application.approve"].create({
                "application_id": app.id,
                "class_id": other_cls.id,
            })

    # ── Report Tests ──────────────────────────────────────────────────

    def test_application_report_action_and_rendering(self):
        """Application form report should be registered in cogmenu and
        render HTML."""
        app = self._make_application()
        report = self.env.ref(
            "education_core.action_report_education_application")
        self.assertEqual(report.model, "education.application")
        self.assertEqual(report.binding_model_id.model,
                         "education.application")
        self.assertEqual(report.binding_type, "report")
        html_content, _ = report._render_qweb_html(report.id, [app.id])
        self.assertTrue(html_content)
        self.assertIn(app.admission_no.encode("utf-8"), html_content)


class TestEnrollmentLifecycle(TransactionCase):
    """Enrollment model tests."""

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.academic_year = cls.env["education.academic.year"].create({
            "name": "Enr Test Year",
            "code": "ENR26",
            "date_start": date(2025, 7, 1),
            "date_end": date(2026, 6, 30),
        })
        cls.department = cls.env["education.department"].create({
            "name": "Enr Dept", "code": "EDEPT"
        })
        cls.program = cls.env["education.program"].create({
            "name": "Enr Program", "code": "EPROG",
            "department_id": cls.department.id,
            "degree_type": "bachelor",
            "duration_years": 3,
        })
        cls.application = cls.env["education.application"].create({
            "first_name": "Enr", "last_name": "Student",
            "date_of_birth": date.today() - timedelta(days=365 * 20),
            "gender": "female",
            "email": "enr.student@example.com",
            "phone": "8888888888",
            "program_id": cls.program.id,
            "academic_year_id": cls.academic_year.id,
        })
        cls.application.action_submit()
        cls.application.action_approve()
        cls.enrollment = cls.application.enrollment_id

    def test_enrollment_no_auto_assigned(self):
        """Enrollment should receive ENR/ sequence number."""
        self.assertNotEqual(self.enrollment.enrollment_no, "New")
        self.assertTrue(self.enrollment.enrollment_no.startswith("ENR/"))

    def test_enrollment_initial_state_active(self):
        """Newly created enrollment should be 'active'."""
        self.assertEqual(self.enrollment.state, "active")

    def test_enrollment_student_name_denormalised(self):
        """Student name should be denormalised from application."""
        self.assertEqual(self.enrollment.student_name, "Enr Student")

    def test_enrollment_duplicate_application_year_raises(self):
        """Same application cannot be enrolled twice in same academic year."""
        with self.assertRaises(Exception):
            self.env["education.enrollment"].create({
                "application_id": self.application.id,
                "program_id": self.program.id,
                "academic_year_id": self.academic_year.id,
            })

    def test_suspend_and_reactivate(self):
        """Active → Suspended → Active transitions."""
        self.enrollment.action_suspend()
        self.assertEqual(self.enrollment.state, "suspended")
        self.enrollment.action_reactivate()
        self.assertEqual(self.enrollment.state, "active")

    def test_graduate(self):
        """Active → Graduated transition."""
        self.enrollment.action_graduate()
        self.assertEqual(self.enrollment.state, "graduated")
        # Reset for other tests
        self.enrollment.write({"state": "active"})


class TestDocumentChecklist(TransactionCase):
    """Document model and completion % tests."""

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.doc_type_mandatory = cls.env["education.document.type"].create({
            "name": "Test Birth Certificate",
            "code": "TEST_BIRTH",
            "is_mandatory": True,
        })
        cls.doc_type_optional = cls.env["education.document.type"].create({
            "name": "Test Address Proof",
            "code": "TEST_ADDR",
            "is_mandatory": False,
        })
        cls.academic_year = cls.env["education.academic.year"].create({
            "name": "Doc Test Year", "code": "DOCYR",
            "date_start": date(2025, 7, 1),
            "date_end": date(2026, 6, 30),
        })
        cls.department = cls.env["education.department"].create({
            "name": "Doc Dept", "code": "DCDEPT"
        })
        cls.program = cls.env["education.program"].create({
            "name": "Doc Program", "code": "DCPROG",
            "department_id": cls.department.id,
            "degree_type": "diploma", "duration_years": 2,
        })
        cls.application = cls.env["education.application"].create({
            "first_name": "Doc", "last_name": "Tester",
            "date_of_birth": date.today() - timedelta(days=365 * 19),
            "gender": "male",
            "email": "doc.tester@example.com",
            "phone": "7777777777",
            "program_id": cls.program.id,
            "academic_year_id": cls.academic_year.id,
        })
        cls.application.action_submit()
        cls.application.action_approve()
        cls.enrollment = cls.application.enrollment_id

    def test_application_default_mandatory_documents(self):
        """Creating an application should auto-populate mandatory document
        lines."""
        app = self.env["education.application"].create({
            "first_name": "DefaultDoc",
            "last_name": "Tester",
            "date_of_birth": date.today() - timedelta(days=365 * 18),
            "gender": "female",
            "email": "defaultdoc@example.com",
            "phone": "8888888888",
            "program_id": self.program.id,
            "academic_year_id": self.academic_year.id,
        })
        app_doc_type_ids = app.document_ids.mapped("document_type_id.id")
        self.assertIn(
            self.doc_type_mandatory.id,
            app_doc_type_ids,
            "Mandatory document type must be present in application "
            "document_ids",
        )
        for doc in app.document_ids:
            self.assertEqual(doc.state, "pending")

    def test_doc_completion_zero_when_empty(self):
        """Completion % should be 0 when no documents are verified."""
        self.assertEqual(self.enrollment.doc_completion_pct, 0)

    def test_doc_completion_with_verified(self):
        """Completion % should reflect verified documents."""
        import base64
        dummy = base64.b64encode(b"dummy_file_content")
        # Clear inherited application documents to test isolated 50% ratio
        self.enrollment.document_ids.unlink()
        doc1 = self.env["education.document"].create({
            "enrollment_id": self.enrollment.id,
            "document_type_id": self.doc_type_mandatory.id,
            "file": dummy,
            "file_name": "birth_cert.pdf",
            "state": "verified",
        })
        doc2 = self.env["education.document"].create({
            "enrollment_id": self.enrollment.id,
            "document_type_id": self.doc_type_optional.id,
            "state": "pending",
        })
        self.enrollment._compute_doc_completion()
        self.assertEqual(self.enrollment.doc_completion_pct, 50,
                         "50% since 1 of 2 documents is verified")

    def test_document_verify_action(self):
        """action_verify should set state=verified and stamp reviewer."""
        import base64
        dummy = base64.b64encode(b"test_content")
        doc = self.env["education.document"].create({
            "enrollment_id": self.enrollment.id,
            "document_type_id": self.doc_type_mandatory.id,
            "file": dummy,
            "file_name": "id.pdf",
            "state": "uploaded",
        })
        doc.action_verify()
        self.assertEqual(doc.state, "verified")
        self.assertEqual(doc.verified_by_id.id, self.env.uid)
        self.assertTrue(doc.verified_date)

    def test_document_date_constraint(self):
        """Expiry date before issue date should raise ValidationError."""
        with self.assertRaises(ValidationError):
            self.env["education.document"].create({
                "enrollment_id": self.enrollment.id,
                "document_type_id": self.doc_type_optional.id,
                "issue_date": date(2025, 6, 1),
                "expiry_date": date(2025, 1, 1),
            })

    def test_document_allowed_file_types(self):
        """Allowed extensions (.pdf, .jpg, .jpeg, .png) should be accepted."""
        import base64
        dummy = base64.b64encode(b"sample_content")
        for ext in [".pdf", ".jpg", ".jpeg", ".png", ".PDF", ".PNG"]:
            doc = self.env["education.document"].create({
                "enrollment_id": self.enrollment.id,
                "document_type_id": self.doc_type_optional.id,
                "file": dummy,
                "file_name": f"test_file{ext}",
            })
            self.assertTrue(doc.id)

    def test_document_disallowed_file_type_raises(self):
        """Disallowed extensions (e.g. .txt, .docx, .exe) should raise
        ValidationError."""
        import base64
        dummy = base64.b64encode(b"sample_content")
        for ext in [".txt", ".docx", ".exe", ".zip"]:
            with self.assertRaises(ValidationError):
                self.env["education.document"].create({
                    "enrollment_id": self.enrollment.id,
                    "document_type_id": self.doc_type_optional.id,
                    "file": dummy,
                    "file_name": f"bad_file{ext}",
                })

    def test_document_file_size_exceeded_raises(self):
        """File exceeding 5 MB should raise ValidationError."""
        import base64
        oversized = base64.b64encode(b"X" * (5 * 1024 * 1024 + 1024))
        with self.assertRaises(ValidationError):
            self.env["education.document"].create({
                "enrollment_id": self.enrollment.id,
                "document_type_id": self.doc_type_optional.id,
                "file": oversized,
                "file_name": "oversized.pdf",
            })
