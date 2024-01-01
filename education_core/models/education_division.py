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


class EducationDivision(models.Model):
    """Manages institution class divisions"""
    _name = 'education.division'
    _description = "Standard Division"

    name = fields.Char(string='Name', required=True,
                       help="Enter the Name of the Division")
    strength = fields.Integer(string='Class Strength',
                              help="Total strength of the class")
    faculty_id = fields.Many2one('education.faculty',
                                 string='Class Faculty',
                                 help="Class teacher/Faculty")
    class_id = fields.Many2one('education.class', string='Class',
                               help="Class of the division")
