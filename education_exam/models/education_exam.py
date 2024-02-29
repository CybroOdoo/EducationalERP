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
from odoo.exceptions import UserError, ValidationError


class EducationExam(models.Model):
    """
        Model representing Education Exams.

        This model stores information about education exams, including details like exam name,
        associated class, division, exam type, start and end dates, and related subjects.
    """
    _name = 'education.exam'
    _description = 'Education Exam'
    _inherit = ['mail.thread', 'mail.activity.mixin']

    name = fields.Char(
        string='Name', default='New', help='Name of the education exam.')
    class_id = fields.Many2one(
        'education.class', string='Class',
        help='Class associated with the exam.')
    division_id = fields.Many2one(
        'education.class.division', string='Division',
        help='Division associated with the exam.')
    exam_type = fields.Many2one(
        'education.exam.type', string='Type', required=True,
        help='Type of the education exam.')
    school_class_division_wise = fields.Selection(
        [('school', 'School'), ('class', 'Class'), ('division', 'Division')],
        related='exam_type.school_class_division_wise', string='School/Class/Division Wise',
        help='Specifies whether the exam is school, class, or division-wise.')
    class_division_hider = fields.Char(
        string='Class Division Hider', help='Hider field for class and division.')
    start_date = fields.Date(
        string='Start Date', required=True, help='Start date of the education exam.')
    end_date = fields.Date(
        string='End Date', required=True, help='End date of the education exam.')
    subject_line_ids = fields.One2many(
        'education.subject.line', 'exam_id',
        string='Subjects', help='Subjects associated with the exam.')
    state = fields.Selection(
        [('draft', 'Draft'), ('ongoing', 'Ongoing'),
         ('close', 'Closed'), ('cancel', 'Canceled')],
        default='draft', help='Current state of the education exam.')
    academic_year_id = fields.Many2one(
        'education.academic.year', string='Academic Year',
        related='division_id.academic_year_id', store=True,
        help='Academic year associated with the division.')
    company_id = fields.Many2one(
        'res.company', string='Company',
        default=lambda self: self.env['res.company']._company_default_get(),
        help='Company associated with the exam.')

    @api.model
    def create(self, vals):
        """
            Create method for Education Exam.
        """
        res = super(EducationExam, self).create(vals)
        if res.division_id:
            res.class_id = res.division_id.class_id.id
        return res

    @api.onchange('class_division_hider')
    def onchange_class_division_hider(self):
        """
            Onchange method for Class Division Hider.

            Updates the school_class_division_wise field based on the class_division_hider value.
        """
        self.school_class_division_wise = 'school'

    @api.constrains('start_date', 'end_date')
    def check_dates(self):
        """
           Constraint method to check start and end dates.

           Raises a ValidationError if the start date is greater than the end date.
        """
        for rec in self:
            if rec.start_date > rec.end_date:
                raise ValidationError(
                    _("Start date must be Anterior to end date"))

    def close_exam(self):
        """
            Sets the state of the exam to 'close'.
        """
        self.state = 'close'

    def cancel_exam(self):
        """
            Sets the state of the exam to 'cancel'.
        """
        self.state = 'cancel'

    def confirm_exam(self):
        """
            Confirm the exam.

            Validates the exam, sets the name based on exam type, start date, and division/class,
            and sets the state to 'ongoing'.

            :raises: UserError if no subjects are added.
        """
        if len(self.subject_line_ids) < 1:
            raise UserError(_('Please Add Subjects'))
        name = str(self.exam_type.name) + '-' + str(self.start_date)[0:10]
        if self.division_id:
            name = name + ' (' + str(self.division_id.name) + ')'
        elif self.class_id:
            name = name + ' (' + str(self.class_id.name) + ')'
        self.name = name
        self.state = 'ongoing'


class SubjectLine(models.Model):
    """
        Model representing Education Subject Line.
        This model stores information about subjects associated with an education exam, including
        details like subject, date, time, marks, associated exam, and company.
    """

    _name = 'education.subject.line'
    _description = 'Subject Line'

    subject_id = fields.Many2one(
        'education.subject', string='Subject', required=True,
        help='Subject associated with the subject line.')
    date = fields.Date(
        string='Date', required=True,
        help='Date of the subject line.')
    time_from = fields.Float(
        string='Time From', required=True, help='Start time of the subject.')
    time_to = fields.Float(
        string='Time To', required=True, help='End time of the subject.')
    mark = fields.Integer(
        string='Mark', help='Mark associated with the subject.')
    exam_id = fields.Many2one(
        'education.exam', string='Exam',
        help='Exam associated with the subject line.')
    company_id = fields.Many2one(
        'res.company', string='Company',
        default=lambda self: self.env['res.company']._company_default_get(),
        help='Company associated with the subject line.')


class EducationExamType(models.Model):
    """
        Model representing Education Exam Type.

        This model stores information about different types of education exams, including
        details like the name of the exam type, whether it's school, class, division-wise,
        or a final exam that promotes students to the next class.
    """

    _name = 'education.exam.type'
    _description = 'Education Exam Type'

    name = fields.Char(
        string='Name', required=True, help='Name of the education exam type.')
    school_class_division_wise = fields.Selection(
        [('school', 'School'), ('class', 'Class'), ('division', 'Division'),
         ('final', 'Final Exam (Exam that promotes students to the next class)')],
        string='Exam Type', default='class', help='Type of education exam.')
    company_id = fields.Many2one(
        'res.company', string='Company',
        default=lambda self: self.env['res.company']._company_default_get(),
        help='Company associated with the education exam type.')
