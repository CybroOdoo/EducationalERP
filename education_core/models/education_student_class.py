# -*- coding: utf-8 -*-
###################################################################################
#    A part of Educational ERP Project <https://www.educationalerp.com>
#
#    Cybrosys Technologies Pvt. Ltd.
#    Copyright (C) 2018-TODAY Cybrosys Technologies (<https://www.cybrosys.com>).
#    Author: Nikhil krishnan (nikhil@cybrosys.in)
#            Niyas Raphy (niyas@cybrosys.in)
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

from odoo import fields, models, api, _
from odoo.exceptions import ValidationError


class EducationStudentClass(models.Model):
    _name = 'education.student.class'
    _description = 'Assign the Students to Class'
    _inherit = ['mail.thread']
    _rec_name = 'class_id'

    class_id = fields.Many2one('education.class', string='Class')
    student_list = fields.One2many('education.student.list', 'connect_id', string="Students")
    admitted_class = fields.Many2one('education.class.division', string="Admitted Class")
    assigned_by = fields.Many2one('res.users', string='Assigned By', default=lambda self: self.env.uid)
    state = fields.Selection([('draft', 'Draft'), ('done', 'Done')],
                             string='State', required=True, default='draft', track_visibility='onchange')

    @api.multi
    def unlink(self):
        """Return warning if the Record is in done state"""
        for rec in self:
            if rec.state == 'done':
                raise ValidationError(_("Cannot delete Record in Done state"))

    @api.multi
    def get_student_list(self):
        """returns the list of students applied to join the selected class"""
        for rec in self:
            for line in rec.student_list:
                line.unlink()
            students = self.env['education.student'].search([
                ('admission_class', '=', rec.class_id.id),
                ('class_id', '=', False)])
            if not students:
                raise ValidationError(_('No Students Available.. !'))
            values = []
            for stud in students:
                stud_line = {
                    'class_id': rec.class_id.id,
                    'student_id': stud.id,
                    'connect_id': rec.id
                }
                values.append(stud_line)
            for line in values:
                rec.student_line = self.env['education.student.list'].create(line)


class EducationStudentList(models.Model):
    _name = 'education.student.list'
    _inherit = ['mail.thread']

    connect_id = fields.Many2one('education.student.class', string='Class')
    student_id = fields.Many2one('education.student', string='Student')
    class_id = fields.Many2one('education.class', string='Class')
