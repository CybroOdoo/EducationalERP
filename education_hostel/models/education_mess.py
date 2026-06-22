# -*- coding: utf-8 -*-
################################################################################
#
#    Cybrosys Technologies Pvt. Ltd.
#
#    Copyright (C) 2026-TODAY Cybrosys Technologies(<https://www.cybrosys.com>).
#    Author: Cybrosys Technologies (odoo@cybrosys.com)
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
################################################################################
"""This module defines the education mess class."""

from odoo import fields, models


class EducationMess(models.Model):
    """Create model 'education.mess'"""
    _name = 'education.mess'
    _rec_name = "mess_code"
    _description = "Mess"

    mess_name = fields.Char(string="Name", required="True",
                            help="Mess name.")
    mess_code = fields.Char(string="Code", required="True",
                            help='Code of mess')
    food_menu_ids = fields.One2many('mess.food', 'mess_id',
                                    string="Food Menu", help="Menu as list")
    hostel_id = fields.Many2one('education.hostel', string="Hostel",
                                required="True", help="Mention the hostel.")
    company_id = fields.Many2one('res.company', string='Company',
                                 default=lambda self: self.env.company,
                                 readonly=True,
                                 help='Company corresponding to the mess')
