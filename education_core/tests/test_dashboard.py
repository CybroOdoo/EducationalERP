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
"""Unit tests for the dashboard data provider."""

import json

from odoo.tests import TransactionCase, tagged


@tagged("post_install", "-at_install")
class TestEducationDashboard(TransactionCase):
    """Unit tests for the dashboard data provider."""

    @classmethod
    def setUpClass(cls):
        """Create the academic year, program, class and a faculty member."""
        super().setUpClass()
        year = cls.env["education.academic.year"].create({
            "name": "Dashboard Year",
            "code": "DBY26",
            "date_start": "2026-01-01",
            "date_end": "2026-12-31",
        })
        dept = cls.env["education.department"].create(
            {"name": "Dash Dept", "code": "DSD"})
        program = cls.env["education.program"].create({
            "name": "Dash Program", "code": "DSP", "department_id": dept.id})
        cls.klass = cls.env["education.class"].create({
            "section": "A",
            "academic_year_id": year.id,
            "program_id": program.id,
        })
        cls.faculty = cls.env["hr.employee"].create({
            "name": "Dash Faculty", "is_faculty": True})
        cls.klass.write({"class_teacher_id": cls.faculty.id})
        cls.dash = cls.env["education.dashboard"]

    def test_clean_filters(self):
        """Reversed dates are swapped and invalid numbers become 0."""
        cleaned = self.dash._clean_filters({
            "date_from": "2026-10-10", "date_to": "2026-10-01",
            "class_id": "7", "program_id": "x", "department_id": None})
        # reversed range is swapped, bad numbers become 0
        self.assertLessEqual(cleaned["date_from"], cleaned["date_to"])
        self.assertEqual(cleaned["class_id"], 7)
        self.assertEqual(cleaned["program_id"], 0)
        self.assertEqual(cleaned["department_id"], 0)

    def test_admin_dashboard_structure(self):
        """The admin payload is complete and JSON serialisable."""
        data = self.dash.get_admin_dashboard()
        json.dumps(data)  # must be JSON serialisable for the client
        for key in ("kpis", "attendance", "attendance_trend", "by_program",
                    "funnel", "fees", "exams", "services", "unmarked",
                    "classes_attention", "class_options"):
            self.assertIn(key, data)
        self.assertGreaterEqual(data["kpis"]["classes"], 1)
        self.assertEqual(len(data["fees"]["trend"]), 6)
        self.assertIsNone(data["class_scope"])

    def test_admin_dashboard_class_filter(self):
        """A class filter scopes the admin dashboard to that class."""
        data = self.dash.get_admin_dashboard({"class_id": self.klass.id})
        json.dumps(data)
        self.assertEqual(data["class_scope"], [self.klass.id])
        self.assertEqual(data["kpis"]["classes"], 1)
        # the class teacher counts as faculty of the filtered class
        self.assertEqual(data["kpis"]["faculty"], 1)

    def test_faculty_admin_view(self):
        """The admin view lists the faculty member with their class."""
        view = self.dash._faculty_admin_view(self.dash._clean_filters({}))
        json.dumps(view)
        rows = {r["id"]: r for r in view["faculties"]}
        self.assertIn(self.faculty.id, rows)
        self.assertEqual(rows[self.faculty.id]["classes"], 1)
        self.assertEqual(view["kpis"]["faculty"], len(view["faculties"]))

    def test_faculty_view(self):
        """The faculty view reports the member's profile and classes."""
        view = self.dash._faculty_view(
            self.faculty, self.dash._clean_filters({}))
        json.dumps(view)
        self.assertEqual(view["profile"]["id"], self.faculty.id)
        self.assertEqual(view["kpis"]["classes"], 1)
        self.assertEqual(view["class_ids"], [self.klass.id])
        self.assertEqual(len(view["week_load"]), 6)
