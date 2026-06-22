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
"""This module defines the education room list class."""

from odoo import fields, models


class EducationRoomList(models.Model):
    """Creating model 'education.room_list'"""
    _name = 'education.room_list'
    _description = "Education Roomlist"

    room_mem_rel = fields.Many2one('education.room', string="Room",
                                   help='Room corresponding to the list')
    floor = fields.Many2one('education.floor', string="Floor",
                            related='room_mem_rel.floor',
                            help='Floor corresponding to the list')
    hostel_room_rel2 = fields.Many2one('education.hostel', string="Room",
                                       related='room_mem_rel.hostel_id',
                                       help='Hostel corresponding to the list')
