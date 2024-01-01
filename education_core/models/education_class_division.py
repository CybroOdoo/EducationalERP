# -*- coding: utf-8 -*-
##############################################################################
#
#    Cybrosys Technologies Pvt. Ltd.
#
#    Copyright (C) 2023-TODAY Cybrosys Technologies(<https://www.cybrosys.com>)
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
from odoo.exceptions import ValidationError


class EducationClassDivision(models.Model):
    """Manages class division details"""
    _name = 'education.class.division'
    _description = "Class room"
    _inherit = ['mail.thread']

    @api.model
    def create(self, vals):
        """Return the name as a str of class + division"""
        class_id = self.env['education.class'].browse(vals['class_id'])
        division_id = self.env['education.division'].browse(
            vals['division_id'])
        name = str(class_id.name + '-' + division_id.name)
        vals['name'] = name
        return super(EducationClassDivision, self).create(vals)

    def action_view_students(self):
        """Return the list of current students in this class"""
        self.ensure_one()
        students = self.env['education.student'].search(
            [('class_division_id', '=', self.id)])
        students_list = students.mapped('id')
        return {
            'domain': [('id', 'in', students_list)],
            'name': _('Students'),
            'view_mode': 'tree,form',
            'res_model': 'education.student',
            'view_id': False,
            'context': {'default_class_id': self.id},
            'type': 'ir.actions.act_window'
        }

    def _compute_student_count(self):
        """Return the number of students in the class"""
        for rec in self:
            students = self.env['education.student'].search(
                [('class_division_id', '=', rec.id)])
            student_count = len(students) if students else 0
            rec.update({
                'student_count': student_count
            })

    name = fields.Char(string='Name', readonly=True,
                       help="Name of the Class division")
    actual_strength = fields.Integer(string='Class Strength',
                                     help="Total strength of the class")
    faculty_id = fields.Many2one('education.faculty',
                                 string='Class Faculty', required=True,
                                 help="Class teacher/Faculty")
    academic_year_id = fields.Many2one('education.academic.year',
                                       string='Academic Year',
                                       help="Select the Academic Year",
                                       required=True)
    class_id = fields.Many2one('education.class', string='Class',
                               required=True, help="Select the Class")
    division_id = fields.Many2one('education.division',
                                  string='Division', required=True,
                                  help="Select the Division")
    student_ids = fields.One2many('education.student',
                                  'class_division_id',
                                  string='Students',
                                  help="Students under this division")
    amenities_ids = fields.One2many('education.class.amenities',
                                    'class_id', string='Amenities',
                                    help="Amenities of this division")
    student_count = fields.Integer(string='Students Count',
                                   help="Count of the students in the "
                                        "division",
                                   compute='_compute_student_count')

    @api.constrains('actual_strength')
    def validate_strength(self):
        """Return Validation error if
            the students strength is not a non-zero number"""
        for rec in self:
            if rec.actual_strength <= 0:
                raise ValidationError(_('Strength must be a Non-Zero value'))
