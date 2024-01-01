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


class ResCompany(models.Model):
    """Inheriting res_company for adding field related to an
        education institution"""
    _inherit = 'res.company'

    affiliation = fields.Char(string='Affiliation', help="Affiliation details")
    register_num = fields.Char(string='Register', help="Registration details")
    base_class_id = fields.Many2one('education.class',
                                    string="Lower class",
                                    help="Smallest class of institute")
    higher_class_id = fields.Many2one('education.class',
                                      string="Higher class",
                                      help="Highest class of institute")
