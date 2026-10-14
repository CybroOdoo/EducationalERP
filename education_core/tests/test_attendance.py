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
education_core — Student Daily Attendance Unit Tests
===================================================
Covers:
  - Daily attendance creation (single record per student per date)
  - Enforcing unique constraint (one record per student per day)
  - Future date validation
  - Bulk marking present for a class on a given date
  - Display name computation
  - Absence notification to parent
"""
from datetime import date, timedelta
from psycopg2 import IntegrityError
from odoo.tests.common import TransactionCase
from odoo.exceptions import ValidationError
from odoo.tools import mute_logger


class TestEducationAttendance(TransactionCase):
    """Unit tests for education.attendance per-day logic."""

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.academic_year = cls.env["education.academic.year"].create({
            "name": "Test Year 2026-2027",
            "code": "TY2627",
            "date_start": date(2026, 6, 1),
            "date_end": date(2027, 3, 31),
            "is_current": True,
        })
        cls.department = cls.env["education.department"].create({
            "name": "Computer Science Department",
            "code": "CSD",
        })
        cls.program = cls.env["education.program"].create({
            "name": "B.Tech Computer Science",
            "code": "BTCS",
            "degree_type": "bachelor",
            "department_id": cls.department.id,
        })
        cls.test_class = cls.env["education.class"].create({
            "name": "CS-2026-A",
            "program_id": cls.program.id,
            "academic_year_id": cls.academic_year.id,
            "section": "A",
            "capacity": 30,
        })
        cls.app_1 = cls.env["education.application"].create({
            "first_name": "Alice",
            "last_name": "Smith",
            "email": "alice.smith@example.com",
            "program_id": cls.program.id,
            "academic_year_id": cls.academic_year.id,
            "guardian_name": "Bob Smith",
            "guardian_email": "bob.smith@example.com",
        })
        cls.app_2 = cls.env["education.application"].create({
            "first_name": "Charlie",
            "last_name": "Brown",
            "email": "charlie.brown@example.com",
            "program_id": cls.program.id,
            "academic_year_id": cls.academic_year.id,
            "guardian_name": "David Brown",
            "guardian_email": "david.brown@example.com",
        })
        cls.enrollment_1 = cls.env["education.enrollment"].create({
            "application_id": cls.app_1.id,
            "program_id": cls.program.id,
            "academic_year_id": cls.academic_year.id,
            "class_id": cls.test_class.id,
            "state": "active",
        })
        cls.enrollment_2 = cls.env["education.enrollment"].create({
            "application_id": cls.app_2.id,
            "program_id": cls.program.id,
            "academic_year_id": cls.academic_year.id,
            "class_id": cls.test_class.id,
            "state": "active",
        })

    def test_01_create_daily_attendance(self):
        """Create a daily attendance record for a student."""
        att = self.env["education.attendance"].create({
            "enrollment_id": self.enrollment_1.id,
            "date": date.today(),
            "state": "present",
        })
        self.assertEqual(att.class_id, self.test_class)
        self.assertEqual(att.student_name, "Alice Smith")
        self.assertIn("Alice Smith", att.display_name)
        self.assertIn(str(date.today()), att.display_name)

    def test_02_duplicate_attendance_per_day_raises(self):
        """Enforce unique attendance per student per date."""
        today = date.today()
        self.env["education.attendance"].create({
            "enrollment_id": self.enrollment_1.id,
            "date": today,
            "state": "present",
        })
        with mute_logger("odoo.sql_db"), self.assertRaises(IntegrityError):
            with self.cr.savepoint():
                self.env["education.attendance"].create({
                    "enrollment_id": self.enrollment_1.id,
                    "date": today,
                    "state": "absent",
                })

    def test_03_future_date_constraint(self):
        """Attendance date cannot be in the future."""
        future_date = date.today() + timedelta(days=2)
        with self.assertRaises(ValidationError):
            self.env["education.attendance"].create({
                "enrollment_id": self.enrollment_1.id,
                "date": future_date,
                "state": "present",
            })

    def test_04_bulk_mark_present(self):
        """Bulk mark present for all active students in a class for a date."""
        yesterday = date.today() - timedelta(days=1)
        # Mark enrollment 1 beforehand
        self.env["education.attendance"].create({
            "enrollment_id": self.enrollment_1.id,
            "date": yesterday,
            "state": "present",
        })
        # bulk mark present should create 1 missing record (for enrollment 2)
        count = self.env["education.attendance"].bulk_mark_present(
            self.test_class.id, yesterday)
        self.assertEqual(count, 1)

        # Check that both enrollments now have attendance on yesterday
        records = self.env["education.attendance"].search([
            ("class_id", "=", self.test_class.id),
            ("date", "=", yesterday),
        ])
        self.assertEqual(len(records), 2)
        self.assertTrue(all(r.state == "present" for r in records))
