# -*- coding: utf-8 -*-
#############################################################################
#
#    Cybrosys Technologies Pvt. Ltd.
#
#    Copyright (C) 2024-TODAY Cybrosys Technologies(<https://www.cybrosys.com>)
#    Author: Cybrosys Techno Solutions (<https://www.cybrosys.com>)
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
#############################################################################
from odoo import api, fields, models, _
from odoo.exceptions import UserError


class EducationExamValuation(models.Model):
    """
        Model representing Exam Valuation for Education.

        This model is used to store information about the valuation of exams,
        including details like the maximum mark, pass mark, students, and results.
    """

    _name = 'education.exam.valuation'
    _description = "Exam Valuation"
    _inherit = ['mail.thread', 'mail.activity.mixin']

    name = fields.Char(
        string='Name', default='New', help='Name of the exam valuation.')
    exam_id = fields.Many2one(
        'education.exam', string='Exam', required=True,
        domain=[('state', '=', 'ongoing')], help='Associated exam for valuation.')
    class_id = fields.Many2one(
        'education.class', string='Class',
        required=True, help='Class associated with the exam valuation.')
    division_id = fields.Many2one(
        'education.class.division',
        string='Division', required=True,
        help='Division associated with the exam valuation.')
    teachers_id = fields.Many2one(
        'education.faculty', string='Evaluator',
        help='Teacher or faculty responsible for exam valuation.')
    mark = fields.Float(
        string='Max Mark', required=True,
        help='Maximum mark for the exam.')
    pass_mark = fields.Float(
        string='Pass Mark', required=True,
        help='Passing mark for the exam.')
    state = fields.Selection(
        [('draft', 'Draft'), ('completed', 'Completed'), ('cancel', 'Canceled')],
        default='draft', help='State of the exam valuation.')
    valuation_line = fields.One2many(
        'exam.valuation.line',
        'valuation_id', string='Students',
        help='Students and their marks in the valuation.')
    subject_id = fields.Many2one(
        'education.subject',
        string='Subject', required=True,
        help='Subject for which the valuation is conducted.')
    mark_sheet_created = fields.Boolean(
        string='Mark sheet Created',
        help='Flag indicating whether the mark sheet is created.')
    date = fields.Date(
        string='Date', default=fields.Date.today,
        help='Date of the exam valuation.')
    academic_year_id = fields.Many2one(
        'education.academic.year', string='Academic Year',
        related='division_id.academic_year_id', store=True,
        help='Academic year associated with the exam valuation.')
    company_id = fields.Many2one(
        'res.company', string='Company',
        default=lambda self: self.env['res.company']._company_default_get(),
        help='Company associated with the exam valuation.')

    @api.onchange('class_id')
    def onchange_class_id(self):
        """
            Update the domain for the 'division_id' field based on the selected class.

            This onchange method is triggered when the 'class_id' field changes.
            It updates the domain for the 'division_id' field to filter divisions based on the selected class.

            :return: A dictionary containing the updated domain for 'division_id'.
        """
        domain = []
        if self.division_id.class_id != self.class_id:
            self.division_id = ''
        if self.class_id:
            domain = [('class_id', '=', self.class_id.id)]
        return {'domain': {'division_id': domain}}

    @api.onchange('pass_mark')
    def onchange_pass_mark(self):
        """
           Update the 'pass_or_fail' field for valuation_line records when 'pass_mark' changes.

           This onchange method is triggered when the 'pass_mark' field changes.
           It updates the 'pass_or_fail' field for all valuation_line records based on the new 'pass_mark'.

           :raises UserError: If 'pass_mark' is greater than 'mark'.
        """
        if self.pass_mark > self.mark:
            raise UserError(_('Pass mark must be less than Max Mark'))
        for records in self.valuation_line:
            records.pass_or_fail = True if records.mark_scored >= self.pass_mark else False

    @api.onchange('exam_id', 'subject_id')
    def onchange_exam_id(self):
        """
            Update fields based on changes in 'exam_id' and 'subject_id'.

            This onchange method is triggered when either 'exam_id' or 'subject_id' changes.
            It updates related fields such as 'class_id', 'division_id', and 'mark' based on the new selections.
            It also updates the domain for 'subject_id' based on the subjects associated with the selected exam.

            :return: A dictionary containing the updated domain for 'subject_id'.
        """
        if self.exam_id:
            if self.exam_id.division_id:
                self.class_id = self.exam_id.class_id
                self.division_id = self.exam_id.division_id
            elif self.exam_id.class_id:
                self.class_id = self.exam_id.class_id
            else:
                self.class_id = ''
                self.division_id = ''
            self.mark = ''
            if self.subject_id:
                for sub in self.exam_id.subject_line_ids:
                    if sub.subject_id.id == self.subject_id.id:
                        if sub.mark:
                            self.mark = sub.mark
        domain = []
        subjects = self.exam_id.subject_line_ids
        for items in subjects:
            domain.append(items.subject_id.id)
        return {'domain': {'subject_id': [('id', 'in', domain)]}}

    def create_mark_sheet(self):
        """
            Create exam valuation lines for all students in the division.
            """
        valuation_line_obj = self.env['exam.valuation.line']
        students = self.division_id.student_ids
        if len(students) < 1:
            raise UserError(_('There are no students in this Division'))
        for student in students:
            data = {
                'student_id': student.id,
                'student_name': student.name,
                'valuation_id': self.id,
            }
            valuation_line_obj.create(data)
        self.mark_sheet_created = True

    @api.model
    def create(self, vals):
        """
            Override the create method to check for existing exam valuations.

            This method overrides the create method to ensure that there is no existing exam valuation
            for the same exam, division, and subject combination. It raises a UserError if such a
            valuation already exists.

            :param vals: Dictionary of values for creating the record.
            :return: The created record.
            :raises UserError: If a valuation sheet for the same exam, division, and subject already exists.
        """
        res = super(EducationExamValuation, self).create(vals)
        valuation_obj = self.env['education.exam.valuation']
        search_valuation = valuation_obj.search(
            [('exam_id', '=', res.exam_id.id),
             ('division_id', '=', res.division_id.id),
             ('subject_id', '=', res.subject_id.id), ('state', '!=', 'cancel')])
        if len(search_valuation) > 1:
            raise UserError(
                _(
                    'Valuation Sheet for \n Subject --> %s \nDivision --> %s \nExam --> %s \n is already created') % (
                    res.subject_id.name, res.division_id.name,
                    res.exam_id.name))
        return res

    def valuation_completed(self):
        """
            Mark the exam valuation as completed and update the related result records.

            This method sets the state of the exam valuation to 'completed' and updates the related
            result records with the calculated marks and pass/fail status for each student.
            """
        self.name = str(self.exam_id.exam_type.name) + '-' + str(
            self.exam_id.start_date)[0:10] + ' (' + str(
            self.division_id.name) + ')'
        result_obj = self.env['education.exam.results']
        result_line_obj = self.env['results.subject.line']
        for students in self.valuation_line:
            search_result = result_obj.search(
                [('exam_id', '=', self.exam_id.id),
                 ('division_id', '=', self.division_id.id),
                 ('student_id', '=', students.student_id.id)])
            if len(search_result) < 1:
                result_data = {
                    'name': self.name,
                    'exam_id': self.exam_id.id,
                    'class_id': self.class_id.id,
                    'division_id': self.division_id.id,
                    'student_id': students.student_id.id,
                    'student_name': students.student_id.name,
                }
                result = result_obj.create(result_data)
                result_line_data = {
                    'name': self.name,
                    'subject_id': self.subject_id.id,
                    'max_mark': self.mark,
                    'pass_mark': self.pass_mark,
                    'mark_scored': students.mark_scored,
                    'pass_or_fail': students.pass_or_fail,
                    'result_id': result.id,
                    'exam_id': self.exam_id.id,
                    'class_id': self.class_id.id,
                    'division_id': self.division_id.id,
                    'student_id': students.student_id.id,
                    'student_name': students.student_id.name,
                }
                result_line_obj.create(result_line_data)
            else:
                result_line_data = {
                    'subject_id': self.subject_id.id,
                    'max_mark': self.mark,
                    'pass_mark': self.pass_mark,
                    'mark_scored': students.mark_scored,
                    'pass_or_fail': students.pass_or_fail,
                    'result_id': search_result.id,
                    'exam_id': self.exam_id.id,
                    'class_id': self.class_id.id,
                    'division_id': self.division_id.id,
                    'student_id': students.student_id.id,
                    'student_name': students.student_id.name,
                }
                result_line_obj.create(result_line_data)
        self.state = 'completed'

    def set_to_draft(self):
        """
           Set the exam valuation back to draft state and unlink related result line records.
           """
        result_line_obj = self.env['results.subject.line']
        result_obj = self.env['education.exam.results']
        for students in self.valuation_line:
            search_result = result_obj.search(
                [('exam_id', '=', self.exam_id.id),
                 ('division_id', '=', self.division_id.id),
                 ('student_id', '=', students.student_id.id)])
            search_result_line = result_line_obj.search(
                [('result_id', '=', search_result.id),
                 ('subject_id', '=', self.subject_id.id)])
            search_result_line.unlink()
        self.state = 'draft'

    def valuation_canceled(self):
        """
            Set the exam valuation state to 'cancel'.
        """
        self.state = 'cancel'


class StudentsExamValuationLine(models.Model):
    """
        Model representing the lines for each student's exam valuation.
        """
    _name = 'exam.valuation.line'
    _description = 'Exam Valuation Line'

    student_id = fields.Many2one('education.student', string='Student',
                                 help='Student associated with this valuation line.')
    student_name = fields.Char(string='Student Name', help='Name of the student.')
    mark_scored = fields.Float(string='Mark Scored', help='Marks obtained by the student in the exam.')
    pass_or_fail = fields.Boolean(string='Pass/Fail',
                                  help='Indicates whether the student has passed or failed in the exam.')
    valuation_id = fields.Many2one('education.exam.valuation', string='Valuation',
                                   help='Exam Valuation to which this line belongs.')
    company_id = fields.Many2one(
        'res.company', string='Company',
        default=lambda self: self.env['res.company']._company_default_get(),
        help='Company associated with this record.')

    @api.onchange('mark_scored', 'pass_or_fail')
    def onchange_mark_scored(self):
        """
            Onchange method to validate mark_scored and update pass_or_fail.
        """
        if self.mark_scored > self.valuation_id.mark:
            raise UserError(_('Mark Scored must be less than Max Mark'))
        if self.mark_scored >= self.valuation_id.pass_mark:
            self.pass_or_fail = True
        else:
            self.pass_or_fail = False
