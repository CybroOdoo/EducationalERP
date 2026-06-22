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
"""This module defines the education room member class."""

from odoo import api, fields, models
from odoo.exceptions import ValidationError


class EducationRoomMember(models.Model):
    """Creating model 'education.room_member'"""
    _name = 'education.room_member'
    _rec_name = 'room_member_id'
    _description = "Room Member"

    room_id = fields.Many2one('education.room',
                              string="Room", help='Room of member')
    allocated_date = fields.Date(string="Allocated Date",
                                 help='Date of allocation',
                                 default=fields.Date.today)
    vacated_date = fields.Date(string="Vacated Date",
                               help='Date of vacating room')
    room_member_id = fields.Many2one('education.hostel.member', string='Member',
                                     help='Corresponding hostel member')
    floor = fields.Many2one('education.floor', string="Floor",
                            related='room_id.floor',
                            help='Floor corresponding to the room member')
    hostel_room_rel = fields.Many2one('education.hostel',
                                      string="Hostel",
                                      related='room_id.hostel_id',
                                      help='Hostel of room member')
    student_id = fields.Many2one('education.student',
                                 string="Student",
                                 help='Student corresponding to the'
                                      ' room member')

    @api.constrains('allocated_date', 'vacated_date')
    def _check_allocated_date(self):
        """Method for validating allocated_date and vacated_date"""
        for rec in self:
            if rec.allocated_date and rec.vacated_date and (
                    rec.vacated_date < rec.allocated_date):
                raise ValidationError(
                    "Vacated date cannot be earlier than allocated date")

    def unlink(self):
        """Keep member and room availability in sync when allocations are deleted."""
        members = self.mapped('room_member_id')
        rooms = self.mapped('room_id')
        res = super().unlink()
        members._sync_allocation_details()
        rooms |= members.mapped('room_id')
        rooms._compute_allocated_number()
        return res
