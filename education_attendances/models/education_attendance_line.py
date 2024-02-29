# -*- coding: utf-8 -*-
##############################################################################
#
#    Cybrosys Technologies Pvt. Ltd.
#
#    Copyright (C) 2024-TODAY Cybrosys Technologies(<https://www.cybrosys.com>)
#    Author: Raneesha M K (odoo@cybrosys.com)
#
#    You can modify it under the terms of the GNU AFFERO
#    GENERAL PUBLIC LICENSE (AGPL v3), Version 3.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU AFFERO GENERAL PUBLIC LICENSE (AGPL v3) for more details.
#
#    You should have received a copy of the GNU AFFERO GENERAL PUBLIC LICENSE
#    (AGPL v3) along with this program.
#    If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################
from odoo import models, fields


class EducationAttendanceLine(models.Model):
    """Used for managing attendance shift details"""
    _name = 'education.attendance.line'
    _description = 'Attendance Lines'

    name = fields.Char(string='Name', help="Name of Attendance")
    attendance_id = fields.Many2one('education.attendance',
                                    string='Attendance Id',
                                    help="Connected Attendance")
    student_id = fields.Many2one('education.student',
                                 string='Student',
                                 help="Student ID for the attendance")
    student_name = fields.Char(string='Student', related='student_id.name',
                               help="Student name for attendance")
    class_id = fields.Many2one('education.class', string='Class',
                               required=True,
                               help="Enter class for attendance")
    division_id = fields.Many2one('education.class.division',
                                  string='Division',
                                  help="Enter class division for attendance",
                                  required=True)
    date = fields.Date(string='Date', required=True, help="Date of attendance")
    present_morning = fields.Boolean(string='Morning',
                                     help="Enable if the student is present "
                                          "in the morning.")
    present_afternoon = fields.Boolean(string='After Noon',
                                       help="Enable if the student is present "
                                            "in the afternoon")
    full_day_absent = fields.Integer(string='Full Day',
                                     help="Full day present or not")
    half_day_absent = fields.Integer(string='Half Day',
                                     help="Half present or not")
    state = fields.Selection([('draft', 'Draft'), ('done', 'Done')],
                             string='State', default='draft',
                             help="Stages of student every day attendance")
    company_id = fields.Many2one(
        'res.company', string='Company', help="Current Company",
        default=lambda self: self.env.company)
    academic_year_id = fields.Many2one('education.academic.year',
                                       string='Academic Year',
                                       related='division_id.academic_year_id',
                                       help="Academic year of education")
