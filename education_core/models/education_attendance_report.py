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
"""education.attendance.report — read-only SQL view for attendance analysis.

One row per attendance record, with ready-made counters so pivot / graph
views can show present / absent / late / excused totals and an attendance
rate for any grouping (student, class, month, weekday ...).

Attendance rate = (present + late + excused) / (present + late + excused +
absent). Holiday / off days are excluded from the rate, which follows the
convention of the existing Attendance Summary report.
"""
from odoo import fields, models

ATTENDANCE_STATES = [
    ("present", "Present"),
    ("absent", "Absent"),
    ("late", "Late"),
    ("excused", "Excused"),
    ("holiday", "Holiday / Off"),
]
WEEKDAYS = [
    ("1", "Monday"),
    ("2", "Tuesday"),
    ("3", "Wednesday"),
    ("4", "Thursday"),
    ("5", "Friday"),
    ("6", "Saturday"),
    ("7", "Sunday"),
]


class EducationAttendanceReport(models.Model):
    """Attendance analysis — one row per attendance record."""

    _name = "education.attendance.report"
    _description = "Attendance Analysis"
    _auto = False
    _order = "date desc, student_name, id"

    date = fields.Date(string="Date", readonly=True)
    weekday = fields.Selection(WEEKDAYS, string="Weekday", readonly=True)
    state = fields.Selection(ATTENDANCE_STATES, string="Status",
                             readonly=True)
    notes = fields.Char(string="Remarks", readonly=True)
    enrollment_id = fields.Many2one(
        "education.enrollment", string="Student Enrollment", readonly=True)
    student_name = fields.Char(string="Student", readonly=True)
    class_id = fields.Many2one("education.class", string="Class",
                               readonly=True)
    academic_year_id = fields.Many2one(
        "education.academic.year", string="Academic Year", readonly=True)
    marked_by_id = fields.Many2one("res.users", string="Marked By",
                                   readonly=True)
    company_id = fields.Many2one("res.company", string="Institution",
                                 readonly=True)
    present_count = fields.Integer(string="Present", readonly=True,
                                   aggregator="sum")
    absent_count = fields.Integer(string="Absent", readonly=True,
                                  aggregator="sum")
    late_count = fields.Integer(string="Late", readonly=True,
                                aggregator="sum")
    excused_count = fields.Integer(string="Excused", readonly=True,
                                   aggregator="sum")
    holiday_count = fields.Integer(string="Holiday / Off", readonly=True,
                                   aggregator="sum")
    attendance_rate = fields.Float(
        string="Attendance Rate (%)", readonly=True, aggregator="avg",
        help="Share of working days attended (present, late or excused). "
             "Correct for any grouping: each row is 100 (attended) or 0 "
             "(absent); holidays are left out.")

    def init(self):
        """Create or replace the attendance analysis SQL view."""
        self.env.cr.execute("""
            CREATE OR REPLACE VIEW education_attendance_report AS (
                SELECT
                    a.id                                AS id,
                    a.date                              AS date,
                    EXTRACT(ISODOW FROM a.date)::int::text AS weekday,
                    a.state                             AS state,
                    a.notes                             AS notes,
                    a.enrollment_id                     AS enrollment_id,
                    a.student_name                      AS student_name,
                    a.class_id                          AS class_id,
                    a.academic_year_id                  AS academic_year_id,
                    a.marked_by_id                      AS marked_by_id,
                    a.company_id                        AS company_id,
                    CASE WHEN a.state = 'present' THEN 1 ELSE 0 END
                                                        AS present_count,
                    CASE WHEN a.state = 'absent' THEN 1 ELSE 0 END
                                                        AS absent_count,
                    CASE WHEN a.state = 'late' THEN 1 ELSE 0 END
                                                        AS late_count,
                    CASE WHEN a.state = 'excused' THEN 1 ELSE 0 END
                                                        AS excused_count,
                    CASE WHEN a.state = 'holiday' THEN 1 ELSE 0 END
                                                        AS holiday_count,
                    CASE
                        WHEN a.state IN ('present', 'late', 'excused')
                            THEN 100.0
                        WHEN a.state = 'absent' THEN 0.0
                    END                                 AS attendance_rate
                FROM education_attendance a
            )
        """)
