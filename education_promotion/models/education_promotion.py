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

from dateutil import relativedelta
from odoo import models, fields


class EducationPromotion(models.Model):
    _name = 'education.promotion'
    _description = 'Promotion'

    name = fields.Many2one('education.academic.year', string="Academic Year")
    academic_result = fields.One2many('education.student.final.result', 'closing_id', string="Results")
    state = fields.Selection([('draft', 'Draft'),
                              ('result_computed', 'Result Computed'),
                              ('close', 'Closed')], default='draft')
    company_id = fields.Many2one('res.company', string='Company',
                                 default=lambda self: self.env['res.company']._company_default_get())

    def compute_final_result(self):
        self.state = 'result_computed'
        for i in self.env['education.exam.results'].search([('academic_year', '=', self.name.id)]):
            for student in i.division_id.students_details:
                student.unlink()
        for i in self.env['education.exam.results'].search([('academic_year', '=', self.name.id)]):
            if i.exam_id.exam_type.school_class_division_wise == 'final':
                    if i.overall_pass:
                        self.env['education.student.final.result'].create({
                            'student_id': i.student_id.id,
                            'final_result': 'pass',
                            'division_id': i.division_id.id,
                            'academic_year': i.division_id.academic_year_id.id,
                            'closing_id': self.id,
                        })
                    else:
                        self.env['education.student.final.result'].create({
                            'student_id': i.student_id.id,
                            'final_result': 'fail',
                            'division_id': i.division_id.id,
                            'academic_year': i.division_id.academic_year_id.id,
                            'closing_id': self.id,
                        })

    def close_academic_year(self):
        self.state = 'close'
        new_academic_year = self.env['education.academic.year'].create(
            {
                'name': str(fields.Date.from_string(self.name.ay_end_date).year)+"-" +
                        str(fields.Date.from_string(self.name.ay_end_date).year + 1),
                'ay_code': str(fields.Date.from_string(self.name.ay_end_date).year)+"-" +
                           str(fields.Date.from_string(self.name.ay_end_date).year + 1),
                'sequence': self.name.sequence + 1,
                'ay_start_date': self.name.ay_end_date,
                'ay_end_date': str(fields.Date.from_string(self.name.ay_end_date) +
                                   relativedelta.relativedelta(months=+12))[:10],

            })

        for j in self.env['education.class.division'].search([('academic_year_id', '=', self.name.id)]):
            if j.is_last_class:
                self.env['education.class.division'].create({
                    'name': j.name,
                    'actual_strength': j.actual_strength,
                    'academic_year_id': new_academic_year.id,
                    'class_id': j.class_id.id,
                    'division_id': j.division_id.id,
                    'is_last_class': j.is_last_class,
                    'is_active_academic_year': new_academic_year.active
                })
            else:
                self.env['education.class.division'].create({
                    'name': j.name,
                    'actual_strength': j.actual_strength,
                    'academic_year_id': new_academic_year.id,
                    'class_id': j.class_id.id,
                    'division_id': j.division_id.id,
                    'is_last_class': j.is_last_class,
                    'promote_class': j.promote_class.id,
                    'promote_division': j.promote_division.id,
                    'is_active_academic_year': new_academic_year.active
                })

        for l in self.env['education.class.division'].search([('academic_year_id', '=', new_academic_year.id)]):
                if not l.is_last_class:
                    promote = self.env['education.class.division'].search([('academic_year_id', '=', new_academic_year.id),
                                            ('name', '=', str(l.promote_class.name) + "-" + str(l.promote_division.name))])
                    if not promote:
                        self.env['education.class.division'].create({
                            'name': l.promote_class.name + "-" + l.promote_division.name,
                            'actual_strength': l.actual_strength,
                            'academic_year_id': new_academic_year.id,
                            'class_id': l.promote_class.id,
                            'is_last_class': l.is_last_class,
                            'division_id': l.promote_division.id,
                            'promote_class': l.promote_class.id,
                            'promote_division': l.promote_division.id,
                            'is_active_academic_year': new_academic_year.active
                        })
        for j in self.env['education.class.division'].search([('academic_year_id', '=', self.name.id)]):
            current_class = self.env['education.class.division'].search([
                ('name', '=', j.name), ('academic_year_id', '=', new_academic_year.id)])
            if j.is_last_class:
                promotion_class = False
            else:
                promotion_class = self.env['education.class.division'].search([
                    ('name', '=', j.promote_class.name + "-" + j.promote_division.name),
                    ('academic_year_id', '=', new_academic_year.id)])

            for k in j.students_details:
                if k.final_result == 'pass':
                    k.student_id.class_id = promotion_class
                    self.env['education.student.final.result'].create({
                        'student_id': k.student_id.id,
                        'final_result': 'na',
                        'division_id':  promotion_class.id,
                        'academic_year': promotion_class.academic_year_id.id,

                    })

                elif k.final_result == 'fail':
                    k.student_id.class_id = current_class.id
                    self.env['education.student.final.result'].create({
                        'student_id': k.student_id.id,
                        'final_result': 'na',
                        'division_id': current_class.id,
                        'academic_year': current_class.academic_year_id.id,

                    })
        self.name.active = False

