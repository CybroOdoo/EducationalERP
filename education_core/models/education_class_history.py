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


class EducationClassDivisionHistory(models.Model):
    """Used for managing student previous class details """
    _name = 'education.class.history'
    _description = "Class room history"
    _rec_name = 'class_id'

    academic_year_id = fields.Many2one('education.academic.year',
                                       string='Academic Year',
                                       help="Select the Academic Year")
    class_id = fields.Many2one('education.class.division',
                               string='Class', help="Select the class")
    student_id = fields.Many2one('education.student',
                                 string='Students',
                                 help="Select Student of class")
