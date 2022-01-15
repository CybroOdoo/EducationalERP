# -*- coding: utf-8 -*-
###############################################################################
#    A part of Educational ERP Project <https://www.educationalerp.com>
#
#    Cybrosys Technologies Pvt. Ltd.
#    Copyright (C) 2021-TODAY Cybrosys Technologies (<https://www.cybrosys.com>)
#    Author: Hajaj Roshan(hajaj@cybrosys.in)
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
###############################################################################

from dateutil import relativedelta
from odoo import models, fields, _
from odoo.exceptions import UserError


class EducationPromotion(models.Model):
    _name = 'education.promotion'
    _description = 'Promotion'

    name = fields.Many2one('education.academic.year', string="Academic Year",
                           required=True)
    academic_result = fields.One2many(
        'education.student.final.result',
        'closing_id', string="Results")
    state = fields.Selection(
        [('draft', 'Draft'),
         ('result_computed', 'Result Computed'),
         ('close', 'Closed')], default='draft')
    company_id = fields.Many2one(
        'res.company', string='Company',
        default=lambda self: self.env['res.company']._company_default_get())

    def compute_final_result(self):
        self.state = 'result_computed'
        exam_result_env = self.env['education.exam.results']
        for result in exam_result_env.search(
                [('academic_year', '=', self.name.id)]):
            for student in result.division_id.students_details:
                student.unlink()
        for i in exam_result_env.search(
                [('academic_year', '=', self.name.id)]).filtered(
            lambda l: l.exam_id.exam_type.school_class_division_wise == 'final'):
            self.env['education.student.final.result'].create({
                'student_id': i.student_id.id,
                'final_result': 'pass' if i.overall_pass else 'fail',
                'division_id': i.division_id.id,
                'academic_year': i.division_id.academic_year_id.id,
                'closing_id': self.id,
            })

    def close_academic_year(self):
        self.state = 'close'
        division_obj = self.env['education.class.division']
        new_academic_year = self.env['education.academic.year'].create(
            {'name': str(
                fields.Date.from_string(self.name.ay_end_date).year) + "-" +
                     str(fields.Date.from_string(
                         self.name.ay_end_date).year + 1),
             'ay_code': str(
                 fields.Date.from_string(self.name.ay_end_date).year) + "-" +
                        str(fields.Date.from_string(
                            self.name.ay_end_date).year + 1),
             'sequence': self.name.sequence + 1,
             'ay_start_date': self.name.ay_end_date,
             'ay_end_date': str(
                 fields.Date.from_string(self.name.ay_end_date) +
                 relativedelta.relativedelta(months=+12))[:10],

             })

        for div in division_obj.search(
                [('academic_year_id', '=', self.name.id)]):
            division_obj.create({
                'name': div.name,
                'actual_strength': div.actual_strength,
                'academic_year_id': new_academic_year.id,
                'class_id': div.class_id.id,
                'division_id': div.division_id.id,
                'is_last_class': div.is_last_class,
            })

        for new_div in division_obj.search(
                [('academic_year_id', '=', new_academic_year.id)]):
            if not new_div.is_last_class:
                promote = division_obj.search(
                    [('academic_year_id', '=', new_academic_year.id),
                     ('name', '=', str(new_div.class_id.name) + "-" + str(
                         new_div.promote_division.name))])
                if not promote:
                    division_obj.create({
                        'name': new_div.class_id.name + "-" + new_div.division_id.name,
                        'actual_strength': new_div.actual_strength,
                        'academic_year_id': new_academic_year.id,
                        'class_id': new_div.class_id.id,
                        'is_last_class': new_div.is_last_class,
                        'division_id': new_div.division_id.id,
                        'promote_class': new_div.class_id.id,
                        'promote_division': new_div.division_id.id,
                    })
        for div in division_obj.search(
                [('academic_year_id', '=', self.name.id)]):
            current_class = division_obj.search([
                ('name', '=', div.name),
                ('academic_year_id', '=', new_academic_year.id)])
            if div.is_last_class:
                promotion_class = False
            else:
                if div.promote_class and div.promote_division:
                    promotion_class = division_obj.search([
                        ('name', '=',
                         div.promote_class.name + "-" + div.promote_division.name),
                        ('academic_year_id', '=', new_academic_year.id)])
                else:
                    raise UserError(_(
                        'There is no promotion class is set for the class %s.'
                        '\nIf it is the last class, Please mark the Check box '
                        'in the Class Division', div.name))

            for k in div.students_details:
                if k.final_result == 'pass':
                    if not promotion_class:
                        k.student_id.active = False
                    elif promotion_class:
                        for rec in promotion_class:
                            k.student_id.class_id = rec
                            self.env['education.student.final.result'].create({
                                'student_id': k.student_id.id,
                                'final_result': 'na',
                                'division_id': rec.id,
                                'academic_year': rec.academic_year_id.id,
                            })

                elif k.final_result == 'fail':
                    for current in current_class:
                        k.student_id.class_id = current.id
                        self.env['education.student.final.result'].create({
                            'student_id': k.student_id.id,
                            'final_result': 'na',
                            'division_id': current.id,
                            'academic_year': current.academic_year_id.id,

                        })
            if div.academic_year_id != new_academic_year:
                div.active = False
        self.name.active = False
