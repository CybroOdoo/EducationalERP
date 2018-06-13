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

from odoo.exceptions import ValidationError
from odoo import fields, models, api, _


class EducationClass(models.Model):
    _name = 'education.class'
    _description = "Standard"

    name = fields.Char(string='Name', required=True, help="Enter the Name of the Class")
    syllabus_ids = fields.One2many('education.syllabus', 'class_id')
    division_ids = fields.One2many('education.division', 'class_id')


class EducationDivision(models.Model):
    _name = 'education.division'
    _description = "Standard Division"

    name = fields.Char(string='Name', required=True, help="Enter the Name of the Division")
    strength = fields.Integer(string='Class Strength', help="Total strength of the class")
    faculty_id = fields.Many2one('education.faculty', string='Class Faculty', help="Class teacher/Faculty")
    class_id = fields.Many2one('education.class', string='Class')


class EducationClassDivision(models.Model):
    _name = 'education.class.division'
    _description = "Class room"

    @api.model
    def create(self, vals):
        """Return the name as a str of class + division"""
        # res = super(EducationClassDivision, self).create(vals)
        class_id = self.env['education.class'].browse(vals['class_id'])
        division_id = self.env['education.division'].browse(vals['division_id'])
        name = str(class_id.name + '-' + division_id.name)
        vals['name'] = name
        return super(EducationClassDivision, self).create(vals)

    @api.multi
    def view_students(self):
        """Return the list of current students in this class"""
        self.ensure_one()
        students = self.env['education.student'].search([('class_id', '=', self.id)])
        students_list = students.mapped('id')
        return {
            'domain': [('id', 'in', students_list)],
            'name': _('Students'),
            'view_type': 'form',
            'view_mode': 'tree,form',
            'res_model': 'education.student',
            'view_id': False,
            'context': {'default_class_id': self.id},
            'type': 'ir.actions.act_window'
        }

    def _get_student_count(self):
        """Return the number of students in the class"""
        for rec in self:
            students = self.env['education.student'].search([('class_id', '=', rec.id)])
            student_count = len(students) if students else 0
            rec.update({
                'student_count': student_count
            })

    name = fields.Char(string='Name', readonly=True)
    actual_strength = fields.Integer(string='Class Strength', help="Total strength of the class")
    faculty_id = fields.Many2one('education.faculty', string='Class Faculty', help="Class teacher/Faculty")
    academic_year_id = fields.Many2one('education.academic.year', string='Academic Year',
                                       help="Select the Academic Year", required=True)
    class_id = fields.Many2one('education.class', string='Class', required=True,
                               help="Select the Class")
    division_id = fields.Many2one('education.division', string='Division', required=True,
                                  help="Select the Division")
    student_ids = fields.One2many('education.student', 'class_id', string='Students')
    amenities_ids = fields.One2many('education.class.amenities', 'class_id', string='Amenities')
    student_count = fields.Integer(string='Students Count', compute='_get_student_count')

    @api.constrains('actual_strength')
    def validate_strength(self):
        """Return Validation error if the students strength is not a non-zero number"""
        for rec in self:
            if rec.actual_strength <= 0:
                raise ValidationError(_('Strength must be a Non-Zero value'))


class EducationClassDivisionHistory(models.Model):
    _name = 'education.class.history'
    _description = "Class room history"
    _rec_name = 'class_id'

    academic_year_id = fields.Many2one('education.academic.year', string='Academic Year',
                                       help="Select the Academic Year")
    class_id = fields.Many2one('education.class.division', string='Class',
                               help="Select the class")
    student_id = fields.Many2one('education.student', string='Students')


class EducationClassAmenities(models.Model):
    _name = 'education.class.amenities'
    _description = "Amenities in Class"

    name = fields.Many2one('education.amenities', string="Amenities",
                           help="Select the amenities in class room")
    qty = fields.Float(string='Quantity', help="The quantity of the amenities", default=1.0)
    class_id = fields.Many2one('education.class.division', string="Class Room")

    @api.constrains('qty')
    def check_qty(self):
        """returns validation error if the qty is 0 or negative"""
        for rec in self:
            if rec.qty <= 0:
                raise ValidationError(_('Quantity must be Positive'))
