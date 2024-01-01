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


class EducationSyllabus(models.Model):
    """Manages syllabus of every subjects"""
    _name = 'education.syllabus'
    _description = 'Syllabus Details'

    name = fields.Char('Name', required=True, help="Name of the syllabus")
    class_id = fields.Many2one('education.class', string='Class',
                               help="Enter the class for syllabus")
    subject_id = fields.Many2one('education.subject',
                                 string='Subject', help="Select subjects")
    total_hours = fields.Float(string='Total Hours',
                               help="Total hours need for the subject")
    description = fields.Text(string='Syllabus Modules',
                              help="Note about the syllabus")

    @api.constrains('total_hours')
    def validate_time(self):
        """Returns validation error if the hours is not a positive value"""
        for rec in self:
            if rec.total_hours <= 0:
                raise ValidationError(_('Hours must be greater than Zero'))
