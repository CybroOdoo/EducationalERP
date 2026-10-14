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
education_analytics — Unit Tests
==================================
Verifies that the four SQL view-backed models are searchable and that the
dashboard AbstractModel returns the expected KPI dict structure.

No setUpClass is needed — the SQL views are created by each model's init()
method at module install time, so they already exist when these tests run.
"""
from odoo.tests.common import TransactionCase, tagged


@tagged("post_install", "-at_install")
class TestAnalytics(TransactionCase):
    """Unit tests for edu.analytics.* view models and dashboard provider."""

    # ── SQL view existence tests ───────────────────────────────────────────

    def test_enrollment_summary_view_exists(self):
        """education.analytics.enrollment.summary SQL view should be
        searchable without error."""
        results = self.env["education.analytics.enrollment.summary"].search([])
        # The search itself must not raise; result can be empty in a fresh DB
        self.assertIsNotNone(results)

    def test_fee_collection_view_exists(self):
        """education.analytics.fee.collection SQL view should be searchable
        without error."""
        results = self.env["education.analytics.fee.collection"].search([])
        self.assertIsNotNone(results)

    def test_attendance_rate_view_exists(self):
        """education.analytics.attendance.rate SQL view should be searchable
        without error."""
        results = self.env["education.analytics.attendance.rate"].search([])
        self.assertIsNotNone(results)

    def test_exam_pass_rate_view_exists(self):
        """education.analytics.exam.pass.rate SQL view should be searchable
        without error."""
        results = self.env["education.analytics.exam.pass.rate"].search([])
        self.assertIsNotNone(results)

    # ── Dashboard KPI method test ──────────────────────────────────────────

    def test_admin_kpis_returns_dict(self):
        """get_admin_kpis() should return a dict with the expected keys."""
        kpis = self.env["edu.analytics.dashboard"].get_admin_kpis()

        self.assertIsInstance(kpis, dict,
                              "get_admin_kpis() must return a dict")
        self.assertIn(
            "total_students", kpis,
            "KPI dict must contain 'total_students'",
        )
        self.assertIn(
            "pending_fees_count", kpis,
            "KPI dict must contain 'pending_fees_count'",
        )
        self.assertIn(
            "attendance_rate", kpis,
            "KPI dict must contain 'attendance_rate'",
        )
        # Value types — integers / floats, never None
        self.assertIsInstance(kpis["total_students"], int)
        self.assertIsInstance(kpis["pending_fees_count"], int)
        self.assertIsInstance(kpis["attendance_rate"], float)
