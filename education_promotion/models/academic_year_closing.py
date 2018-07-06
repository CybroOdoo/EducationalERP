# -*- coding: utf-8 -*-
###################################################################################
#    A part of Educational ERP Project <https://www.educationalerp.com>
#
#    Cybrosys Technologies Pvt. Ltd.
#    Copyright (C) 2018-TODAY Cybrosys Technologies (<https://www.cybrosys.com>).
#    Author: Treesa Maria Jude(treesa@cybrosys.in)
#
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
###################################################################################

from odoo import models, fields, api, _


class AcademicYearClosing(models.Model):
    _inherit = 'education.class.division'

    is_last_class = fields.Boolean(string="Is Last Class", help="Enable this option to set this class as last class")
    promote_class = fields.Many2one('education.class', string='Promotion Class')
    promote_division = fields.Many2one('education.division', string='Promotion Division')
    students_details = fields.One2many('education.student.final.result', 'division_id', string='Student Final Result')


class EducationStudentFinalResult(models.Model):
    _name = 'education.student.final.result'

    student_id = fields.Many2one('education.student', string="Student")
    final_result = fields.Selection([
        ('na', 'Not Applicable'),
        ('pass', 'Pass'),
        ('fail', 'Fail'), ],
        string="Final Result", default='na')
    division_id = fields.Many2one('education.class.division', string="Class")
    academic_year = fields.Many2one('education.academic.year', string='Academic Year')
    closing_id = fields.Many2one('education.promotion', string='Academic Year')


class StudentPromotion(models.Model):
    _inherit = 'education.student'

    final_result = fields.Selection([
        ('na', 'Not Applicable'),
        ('pass', 'Pass'),
        ('fail', 'Fail'), ],
        string="Final Result", default='na')
