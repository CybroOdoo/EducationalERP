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
"""Tests — the demo data of the three institutions (skipped without demo)."""

from odoo import fields
from odoo.tests import TransactionCase, tagged

INSTITUTIONS = (
    "base.main_company",
    "education_core.company_school",
    "education_core.company_corporate",
)


@tagged("post_install", "-at_install")
class TestDemoData(TransactionCase):
    """Every institution has a complete, date-relative demo data set."""

    @classmethod
    def setUpClass(cls):
        """Skip the whole class when the module has no demo data."""
        super().setUpClass()
        params = cls.env["ir.config_parameter"].sudo()
        cls.has_demo = bool(
            params.get_param("education_core.demo_data_loaded"))
        cls.today = fields.Date.today()

    def setUp(self):
        """Skip each test when the module was installed without demo."""
        super().setUp()
        if not self.has_demo:
            self.skipTest("Education Core demo data is not installed.")

    def _companies(self):
        """The three demo institutions."""
        return [self.env.ref(xml_id) for xml_id in INSTITUTIONS]

    def test_three_institutions_of_different_types(self):
        """School, college and corporate centre, two years each."""
        types = {c.institution_type for c in self._companies()}
        self.assertEqual(types, {"school", "college", "corporate"})
        for company in self._companies():
            years = self.env["education.academic.year"].search(
                [("company_id", "=", company.id)])
            self.assertGreaterEqual(len(years), 2, company.name)
            current = years.filtered("is_current")
            self.assertEqual(len(current), 1, company.name)
            self.assertLessEqual(current.date_start, self.today)
            self.assertGreaterEqual(current.date_end, self.today)

    def test_structure_minimums(self):
        """3 departments, 2 programs each, 2 classes each, 10 students."""
        for company in self._companies():
            depts = self.env["education.department"].search(
                [("company_id", "=", company.id)])
            self.assertGreaterEqual(len(depts), 3, company.name)
            for dept in depts:
                self.assertGreaterEqual(len(dept.program_ids), 2, dept.name)
                for program in dept.program_ids:
                    self.assertGreaterEqual(
                        len(program.class_ids), 2, program.name)
                    for klass in program.class_ids:
                        self.assertGreaterEqual(
                            len(klass.enrollment_ids), 10,
                            klass.display_name)

    def test_every_enrollment_has_thirty_past_attendances(self):
        """30 records on the 30 days before today, none in the future."""
        Attendance = self.env["education.attendance"]
        first_day = fields.Date.subtract(self.today, days=30)
        for company in self._companies():
            enrollments = self.env["education.enrollment"].search(
                [("program_id.company_id", "=", company.id)])
            counts = dict(Attendance._read_group(
                [("enrollment_id", "in", enrollments.ids),
                 ("date", ">=", first_day), ("date", "<", self.today)],
                ["enrollment_id"], ["__count"]))
            for enrollment in enrollments:
                self.assertGreaterEqual(
                    counts.get(enrollment, 0), 30, enrollment.display_name)
            self.assertFalse(Attendance.search_count(
                [("company_id", "=", company.id),
                 ("date", ">", self.today)]))

    def test_every_model_has_data_in_every_institution(self):
        """Faculty, rooms, subjects, timetables, leaves, documents..."""
        for company in self._companies():
            domain = [("company_id", "=", company.id)]
            for model in ("hr.employee", "education.classroom",
                          "education.application", "education.enrollment",
                          "education.leave.request", "education.document",
                          "education.timetable", "education.timetable.slot",
                          "education.subject", "education.class",
                          "education.faculty.qualification"):
                self.assertTrue(
                    self.env[model].search_count(domain),
                    "%s has no %s" % (company.name, model))

    def test_administrator_works_in_all_institutions(self):
        """The default administrator is allowed in the three companies."""
        admin = self.env.ref("base.user_admin")
        self.assertLessEqual(
            set(c.id for c in self._companies()), set(admin.company_ids.ids))
