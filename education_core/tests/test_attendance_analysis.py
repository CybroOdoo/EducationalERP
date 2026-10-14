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
"""Tests — Attendance Analysis SQL view."""

from odoo.tests import TransactionCase, tagged


@tagged("post_install", "-at_install")
class TestAttendanceAnalysis(TransactionCase):

    def test_view_is_queryable(self):
        """The SQL view builds and every field maps to a real column."""
        Report = self.env["education.attendance.report"]
        Report.search_read([], limit=1)  # selects every column
        self.assertGreaterEqual(Report.search_count([]), 0)

    def test_grouping_and_rate(self):
        """Counters and the rate aggregate for any grouping."""
        Report = self.env["education.attendance.report"]
        for _klass, present, absent, rate in Report._read_group(
                [], ["class_id"],
                ["present_count:sum", "absent_count:sum",
                 "attendance_rate:avg"]):
            self.assertGreaterEqual(present, 0)
            self.assertGreaterEqual(absent, 0)
            if rate is not None:
                self.assertTrue(0.0 <= rate <= 100.0)
