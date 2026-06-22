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
"""This module defines the mess food class."""

from odoo import fields, models


class MessFood(models.Model):
    """Created model 'mess.food' """
    _name = 'mess.food'
    _description = 'Food Order'

    mess_id = fields.Many2one('education.mess', string="MESS",
                              help='Mess corresponding to the food item')
    break_fast_id = fields.Many2one('food.item', string="Break Fast",
                                    help="Mention the breakfast item.")
    lunch_id = fields.Many2one('food.item', string="Lunch",
                               help="Mention the lunch item.")
    snack_id = fields.Many2one('food.item', string="Snack",
                               help="Mention the snack item.")
    supper_id = fields.Many2one('food.item', string="Supper",
                                help="Mention the supper item.")
    week_list = fields.Selection([
        ('MO', 'Monday'),
        ('TU', 'Tuesday'),
        ('WE', 'Wednesday'),
        ('TH', 'Thursday'),
        ('FR', 'Friday'),
        ('SA', 'Saturday'),
        ('SU', 'Sunday')
    ], string='Weekday', help="Mention the day from the week.")
