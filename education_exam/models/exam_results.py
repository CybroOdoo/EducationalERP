# -*- coding: utf-8 -*-
###############################################################################
#    A part of Educational ERP Project <https://www.educationalerp.com>
#
#    Cybrosys Technologies Pvt. Ltd.
#    Copyright (C) 2020-TODAY Cybrosys Technologies (<https://www.cybrosys.com>)
#    Author: Hajaj Roshan (hajaj@cybrosys.in)
#    This program is free software: you can modify
#    it under the terms of the GNU Affero General Public License (AGPL) as
#    published by the Free Software Foundation, either version 3 of the
#    License, or (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Affero General Public License for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with this program.  If not, see <https://www.gnu.org/licenses/>.
#
###############################################################################

from odoo import models, fields, api


class EducationExamResults(models.Model):
    _name = 'education.exam.results'
    _description = 'Exam Results'
    _inherit = ['mail.thread', 'mail.activity.mixin']

    name = fields.Char(string='Name')
    exam_id = fields.Many2one('education.exam', string='Exam')
    class_id = fields.Many2one('education.class', string='Class')
    division_id = fields.Many2one('education.class.division', string='Division')
    student_id = fields.Many2one('education.student', string='Student')
    student_name = fields.Char(string='Student')
    subject_line = fields.One2many('results.subject.line', 'result_id',
                                   string='Subjects')
    academic_year = fields.Many2one('education.academic.year',
                                    string='Academic Year',
                                    related='division_id.academic_year_id',
                                    store=True)
    company_id = fields.Many2one(
        'res.company', string='Company',
        default=lambda self: self.env['res.company']._company_default_get())
    total_pass_mark = fields.Float(string='Total Pass Mark', store=True,
                                   readonly=True, compute='_total_marks_all')
    total_max_mark = fields.Float(string='Total Max Mark', store=True,
                                  readonly=True, compute='_total_marks_all')
    total_mark_scored = fields.Float(string='Total Marks Scored', store=True,
                                     readonly=True, compute='_total_marks_all')
    overall_pass = fields.Boolean(string='Overall Pass/Fail', store=True,
                                  readonly=True, compute='_total_marks_all')

    @api.depends('subject_line.mark_scored')
    def _total_marks_all(self):
        for results in self:
            total_pass_mark = 0
            total_max_mark = 0
            total_mark_scored = 0
            overall_pass = True
            for subjects in results.subject_line:
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
    _name = 'results.subject.line'
    _description = 'Results Subject Line'

    name = fields.Char(string='Name')
    subject_id = fields.Many2one('education.subject', string='Subject')
    max_mark = fields.Float(string='Max Mark')
    pass_mark = fields.Float(string='Pass Mark')
    mark_scored = fields.Float(string='Mark Scored')
    pass_or_fail = fields.Boolean(string='Pass/Fail')
    result_id = fields.Many2one('education.exam.results', string='Result Id')
    exam_id = fields.Many2one('education.exam', string='Exam')
    class_id = fields.Many2one('education.class', string='Class')
    division_id = fields.Many2one('education.class.division', string='Division')
    student_id = fields.Many2one('education.student', string='Student')
    student_name = fields.Char(string='Student')
    academic_year = fields.Many2one('education.academic.year',
                                    string='Academic Year',
                                    related='division_id.academic_year_id',
                                    store=True)
    company_id = fields.Many2one(
        'res.company',
        string='Company',
        default=lambda self: self.env['res.company']._company_default_get())
