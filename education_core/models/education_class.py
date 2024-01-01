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
from odoo import fields, models


class EducationClass(models.Model):
    """For managing classes"""
    _name = 'education.class'
    _description = "Standard"

    name = fields.Char(string='Name', required=True,
                       help="Enter the Name of the Class")
    syllabus_ids = fields.One2many('education.syllabus',
                                   'class_id',
                                   string="Syllabus",
                                   help="Syllabus of the class")
    division_ids = fields.One2many('education.division',
                                   'class_id',
                                   string="Division",
                                   help="Divisions of class")
