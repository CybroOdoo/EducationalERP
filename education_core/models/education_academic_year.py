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


class EducationAcademicYear(models.Model):
    """For managing academic year of institution"""
    _name = 'education.academic.year'
    _description = 'Academic Year'
    _order = 'sequence asc'

    @api.model
    def create(self, vals):
        """Overriding the create method and assigning the
        sequence for the newly creating record"""
        vals['sequence'] = self.env['ir.sequence'].next_by_code(
            'education.academic.year')
        res = super(EducationAcademicYear, self).create(vals)
        return res

    def unlink(self):
        """Return validation error on deleting the academic year"""
        for rec in self:
            raise ValidationError(
                _("Academic Year can not be deleted, You only can "
                  "Archive it."))

    name = fields.Char(string='Name', required=True,
                       help='Name of academic year')
    sequence = fields.Integer(string='Sequence', required=True,
                              help="Sequence of academic year")
    ay_start_date = fields.Date(string='Start date', required=True,
                                help='Starting date of academic year')
    ay_end_date = fields.Date(string='End date', required=True,
                              help='Ending of academic year')
    ay_description = fields.Text(string='Description',
                                 help="Description about the academic year")
    active = fields.Boolean(
        'Active', default=True,
        help="If unchecked, it will allow you to hide the Academic "
             "Year without removing it.")

    @api.constrains('ay_start_date', 'ay_end_date')
    def validate_date(self):
        """Checking the start and end dates of the syllabus,
        raise warning if start date is not anterior"""
        for rec in self:
            if rec.ay_start_date >= rec.ay_end_date:
                raise ValidationError(
                    _('Start date must be Anterior to End date'))
