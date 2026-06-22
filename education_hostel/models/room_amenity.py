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
"""This module defines the room amenity class."""

from odoo import _, api, fields, models
from odoo.exceptions import ValidationError


class RoomAmenity(models.Model):
    """Creating model 'room.amenity'"""
    _name = 'room.amenity'
    _description = "Amenity"

    amenity_id = fields.Many2one('education.amenities',
                                 string="Amenity", required=True)
    qty = fields.Integer(string="Quantity", help='Quantity of amenity')
    amenity_rel_id = fields.Many2one('education.room', string='Room',
                                 help='Room corresponding to the amenity')

    @api.constrains('qty')
    def check_qty(self):
        """Function to check quantity"""
        for rec in self:
            if rec.qty <= 0:
                raise ValidationError(_('Quantity must be positive'))
