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


class EducationClassAmenities(models.Model):
    """For managing amenities of each class"""
    _name = 'education.class.amenities'
    _description = "Amenities in Class"

    name = fields.Many2one('education.amenities', string="Amenities",
                           help="Select the amenities in class room")
    qty = fields.Float(string='Quantity', help="The quantity of the amenities",
                       default=1.0)
    class_id = fields.Many2one('education.class.division',
                               string="Class Room", help="Select class room")

    @api.constrains('qty')
    def check_qty(self):
        """Returns validation error if the qty is 0 or negative"""
        for rec in self:
            if rec.qty <= 0:
                raise ValidationError(_('Quantity must be Positive'))
