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
from odoo import api, fields, models, _
from odoo.exceptions import UserError, ValidationError


class EducationAttendance(models.Model):
    """For managing attendance details of class"""
    _name = 'education.attendance'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _description = 'Students Attendance'

    name = fields.Char(string='Name', default='New',
                       help="Name of the attendance")
    class_id = fields.Many2one('education.class', string='Class',
                               help="Class of the attendance")
    division_id = fields.Many2one('education.class.division',
                                  string='Division', required=True,
                                  help="Class division for attendance")
    date = fields.Date(string='Date', default=fields.Date.today, required=True,
                       help="Attendance date")
    attendance_line_ids = fields.One2many('education.attendance.line',
                                          'attendance_id',
                                          string='Attendance Line',
                                          help="Student attendance line")
    attendance_created = fields.Boolean(string='Attendance Created',
                                        help="Enable if attendance is created")
    all_marked_morning = fields.Boolean(string="All Present Morning",
                                        help='Enable if all students are '
                                             'present in the morning')
    all_marked_afternoon = fields.Boolean(string="All Present Afternoon",
                                          help='Enable if all students are '
                                               'present in the afternoon')
    state = fields.Selection([('draft', 'Draft'), ('done', 'Done')],
                             default='draft', string="State",
                             help="Stages of attendance")
    academic_year_id = fields.Many2one('education.academic.year',
                                       string='Academic Year',
                                       related='division_id.academic_year_id',
                                       help="Academic year of the class")
    faculty_id = fields.Many2one('education.faculty',
                                 string='Faculty',
                                 related='division_id.faculty_id',
                                 help="Faculty of the class")
    company_id = fields.Many2one(
        'res.company', string='Company', help="Current Company",
        default=lambda self: self.env.company)

    @api.model
    def create(self, vals):
        """Method create already existing method create supering to add this
        module functionality"""
        res = super(EducationAttendance, self).create(vals)
        res.class_id = res.division_id.class_id.id
        attendance_obj = self.env['education.attendance']
        already_created_attendance = attendance_obj.search(
            [('division_id', '=', res.division_id.id), ('date', '=', res.date),
             ('company_id', '=', res.company_id.id)])
        if len(already_created_attendance) > 1:
            raise ValidationError(
                _('Attendance register of %s is already created on "%s"', ) % (
                    res.division_id.name, res.date))
        return res

    def action_create_attendance_line(self):
        """ Action for creating attendance line for the students
            present in the division"""
        self.name = str(self.date)
        attendance_line_obj = self.env['education.attendance.line']
        students = self.division_id.student_ids
        if len(students) < 1:
            raise UserError(_('There are no students in this Division'))
        for student in students:
            data = {
                'name': self.name,
                'attendance_id': self.id,
                'student_id': student.id,
                'student_name': student.name,
                'class_id': self.division_id.class_id.id,
                'division_id': self.division_id.id,
                'date': self.date,
            }
            attendance_line_obj.create(data)
        self.attendance_created = True

    def action_mark_all_present_morning(self):
        """Action for marking all students morning attendance"""
        for records in self.attendance_line_ids:
            records.present_morning = True
        self.all_marked_morning = True

    def action_un_mark_all_present_morning(self):
        """Action for un marking all students morning attendance"""
        for records in self.attendance_line_ids:
            records.present_morning = False
        self.all_marked_morning = False

    def action_mark_all_present_afternoon(self):
        """Action for marking all students afternoon attendance"""
        for records in self.attendance_line_ids:
            records.present_afternoon = True
        self.all_marked_afternoon = True

    def action_un_mark_all_present_afternoon(self):
        """Action for un marking all students afternoon attendance"""
        for records in self.attendance_line_ids:
            records.present_afternoon = False
        self.all_marked_afternoon = False

    def action_attendance_done(self):
        """Button action for setting attendance and line status to done"""
        for records in self.attendance_line_ids:
            records.state = 'done'
            if not records.present_morning and not records.present_afternoon:
                records.full_day_absent = 1
            elif not records.present_morning:
                records.half_day_absent = 1
            elif not records.present_afternoon:
                records.half_day_absent = 1
        self.state = 'done'

    def action_set_to_draft(self):
        """Button action for setting attendance and line status to draft"""
        for records in self.attendance_line_ids:
            records.state = 'draft'
        self.state = 'draft'
