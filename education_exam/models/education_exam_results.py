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

from odoo import api, fields, models


class EducationExamResults(models.Model):
    """
        Model to store and manage Education Exam Results.
        """
    _name = 'education.exam.results'
    _description = 'Exam Results'
    _inherit = ['mail.thread', 'mail.activity.mixin']

    name = fields.Char(string='Name', help='Name associated with the exam result entry.')
    exam_id = fields.Many2one('education.exam', string='Exam', help='Select the exam associated with the result.')
    class_id = fields.Many2one('education.class', string='Class',
                               help='Select the class for which the exam result is recorded.')
    division_id = fields.Many2one('education.class.division', string='Division',
                                  help='Select the division within the class.')
    student_id = fields.Many2one('education.student', string='Student',
                                 help='Select the student for whom the result is recorded.')
    student_name = fields.Char(string='Student', help='Name of the student associated with the exam result.')
    subject_line_ids = fields.One2many('results.subject.line', 'result_id',
                                       string='Subjects',
                                       help='List of subjects and their corresponding results for the exam.')
    academic_year_id = fields.Many2one('education.academic.year',
                                       string='Academic Year',
                                       related='division_id.academic_year_id',
                                       store=True,
                                       help='Academic year associated with the division.')
    company_id = fields.Many2one(
        'res.company', string='Company',
        default=lambda self: self.env['res.company']._company_default_get(),
        help='Company associated with the exam results.'
    )
    total_pass_mark = fields.Float(string='Total Pass Mark', store=True,
                                   readonly=True, compute='_total_marks_all',
                                   help='Total pass marks obtained by the student.')
    total_max_mark = fields.Float(string='Total Max Mark', store=True,
                                  readonly=True, compute='_total_marks_all',
                                  help='Total maximum marks for the exam.')
    total_mark_scored = fields.Float(string='Total Marks Scored', store=True,
                                     readonly=True, compute='_total_marks_all',
                                     help='Total marks scored by the student.')
    overall_pass = fields.Boolean(string='Overall Pass/Fail', store=True,
                                  readonly=True, compute='_total_marks_all',
                                  help='Overall pass or fail status based on subject results.')

    @api.depends('subject_line_ids.mark_scored')
    def _total_marks_all(self):
        """
            Compute total pass marks, total max marks, total marks scored,
            and overall pass/fail status for the exam results.
            """
        for results in self:
            total_pass_mark = 0
            total_max_mark = 0
            total_mark_scored = 0
            overall_pass = True
            for subjects in results.subject_line_ids:
                total_pass_mark += subjects.pass_mark
                total_max_mark += subjects.max_mark
                total_mark_scored += subjects.mark_scored
                if not subjects.pass_or_fail:
                    overall_pass = False
            results.total_pass_mark = total_pass_mark
            results.total_max_mark = total_max_mark
            results.total_mark_scored = total_mark_scored
            results.overall_pass = overall_pass


class ResultsSubjectLine(models.Model):
    """
        Model to store individual subject results for exams.
        """
    _name = 'results.subject.line'
    _description = 'Results Subject Line'

    name = fields.Char(string='Name', help='Name associated with the subject result entry.')
    subject_id = fields.Many2one('education.subject', string='Subject',
                                 help='Select the subject for which the result is recorded.')
    max_mark = fields.Float(string='Max Mark', help='Maximum marks achievable for the subject.')
    pass_mark = fields.Float(string='Pass Mark', help='Passing marks for the subject.')
    mark_scored = fields.Float(string='Mark Scored', help='Marks obtained by the student in the subject.')
    pass_or_fail = fields.Boolean(string='Pass/Fail', help='Pass or fail status for the subject result.')
    result_id = fields.Many2one('education.exam.results', string='Result Id',
                                help='Reference to the parent exam result.')
    exam_id = fields.Many2one('education.exam', string='Exam',
                              help='Reference to the exam associated with the subject result.')
    class_id = fields.Many2one('education.class', string='Class',
                               help='Reference to the class associated with the subject result.')
    division_id = fields.Many2one('education.class.division', string='Division',
                                  help='Reference to the division within the class.')
    student_id = fields.Many2one('education.student', string='Student',
                                 help='Reference to the student associated with the subject result.')
    student_name = fields.Char(string='Student', help='Name of the student associated with the subject result.')
    academic_year_id = fields.Many2one('education.academic.year', string='Academic Year',
                                       related='division_id.academic_year_id', store=True,
                                       help='Academic year associated with the subject result.')
    company_id = fields.Many2one(
        'res.company', string='Company',
        default=lambda self: self.env['res.company']._company_default_get(),
        help='Company associated with the subject result.')
