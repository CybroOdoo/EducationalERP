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
Education Analytics — SQL Read-Only View Models
===============================================
PostgreSQL views surfaced as Odoo models with _auto = False:
  - education.analytics.enrollment.summary
  - education.analytics.attendance.rate
"""
from odoo import fields, models, tools


class EducationAnalyticsEnrollmentSummary(models.Model):
    """Enrollment counts grouped by program and academic year."""

    _name = "education.analytics.enrollment.summary"
    _description = "Enrollment Summary Analytics"
    _auto = False
    _rec_name = "program_name"
    _order = "program_name"

    program_name = fields.Char(
        string="Program",
        readonly=True,
        help="Name of the academic program (e.g. B.Tech Computer Science).",
    )
    academic_year_name = fields.Char(
        string="Academic Year",
        readonly=True,
        help="Academic year in which these enrollments were recorded "
             "(e.g. 2025-2026).",
    )
    total_enrolled = fields.Integer(
        string="Total Enrolled",
        readonly=True,
        aggregator="sum",
        help="Total number of students enrolled in this program for the "
             "given academic year.",
    )
    active_count = fields.Integer(
        string="Active",
        readonly=True,
        aggregator="sum",
        help="Number of students currently in active enrollment status.",
    )
    graduated_count = fields.Integer(
        string="Graduated",
        readonly=True,
        aggregator="sum",
        help="Number of students who have successfully graduated from "
             "this program.",
    )

    def init(self):
        """Create or replace the SQL view for enrollment summary."""
        tools.drop_view_if_exists(self.env.cr, self._table)
        self.env.cr.execute("""
                            CREATE
                            OR REPLACE VIEW 
                            education_analytics_enrollment_summary AS (
                SELECT
                    ROW_NUMBER() OVER ()            AS id,
                    ep.name ->> 'en_US'             AS program_name,
                    ay.name                         AS academic_year_name,
                    COUNT(ee.id)                    AS total_enrolled,
                    COUNT(ee.id) FILTER (
                        WHERE ee.state = 'active'
                    )                               AS active_count,
                    COUNT(ee.id) FILTER (
                        WHERE ee.state = 'graduated'
                    )                               AS graduated_count
                FROM education_enrollment ee
                JOIN education_program ep
                    ON ep.id = ee.program_id
                JOIN education_academic_year ay
                    ON ay.id = ee.academic_year_id
                GROUP BY
                    ep.name ->> 'en_US',
                    ay.name
            )
                            """)


class EducationAnalyticsAttendanceRate(models.Model):
    """Attendance rate per class per academic year."""

    _name = "education.analytics.attendance.rate"
    _description = "Attendance Rate Analytics"
    _auto = False
    _rec_name = "class_name"
    _order = "class_name"

    class_name = fields.Char(
        string="Class",
        readonly=True,
        help="Name of the class for which this attendance rate is computed.",
    )
    academic_year_name = fields.Char(
        string="Academic Year",
        readonly=True,
        help="Academic year to which these attendance records belong.",
    )
    total_records = fields.Integer(
        string="Total Records",
        readonly=True,
        aggregator="sum",
        help="Total number of attendance records (all statuses) for "
             "this class in the given academic year.",
    )
    present_count = fields.Integer(
        string="Present",
        readonly=True,
        aggregator="sum",
        help="Number of attendance records where the student was present "
             "or marked as late.",
    )
    attendance_rate = fields.Float(
        string="Attendance Rate (%)",
        readonly=True,
        aggregator="avg",
        help="Percentage of periods where students were present or late, "
             "calculated as (present_count / total_records) × 100.",
    )

    def init(self):
        """Create or replace the SQL view for attendance rate analytics."""
        tools.drop_view_if_exists(self.env.cr, self._table)
        self.env.cr.execute("""
                            CREATE
                            OR REPLACE VIEW 
                            education_analytics_attendance_rate AS (
                SELECT
                    ROW_NUMBER() OVER ()            AS id,
                    ec.name                         AS class_name,
                    ay.name                         AS academic_year_name,
                    COUNT(ea.id)                    AS total_records,
                    COUNT(ea.id) FILTER (
                        WHERE ea.state IN ('present', 'late')
                    )                               AS present_count,
                    CASE
                        WHEN COUNT(ea.id) = 0 THEN 0
                        ELSE ROUND(
                            COUNT(ea.id) FILTER (
                                WHERE ea.state IN ('present', 'late')
                            ) * 100.0 / COUNT(ea.id),
                            2
                        )
                    END                             AS attendance_rate
                FROM education_attendance ea
                JOIN education_class ec
                    ON ec.id = ea.class_id
                JOIN education_academic_year ay
                    ON ay.id = ea.academic_year_id
                GROUP BY
                    ec.name,
                    ay.name
            )
                            """)
