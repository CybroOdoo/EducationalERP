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
"""This module defines the education room and its corresponding models."""

from odoo import _, api, fields, models
from odoo.exceptions import ValidationError


class EducationRoom(models.Model):
    """Creating a model 'education.room' with fields"""
    _name = 'education.room'
    _rec_name = 'room_name'
    _description = "Room"
    _inherit = ['mail.thread', 'mail.activity.mixin']

    hostel_id = fields.Many2one('education.hostel', required=True,
                                string="Hostel",
                                help='Hostel corresponding to the room')
    room_name = fields.Char(string="Room Name", required=True,
                            help='Name of room')
    room_code = fields.Char(string="Room Code", required=True,
                            help='Room code of room')
    floor = fields.Many2one('education.floor', required=True, string="Floor")
    responsible_id = fields.Many2one('education.faculty',
                                     string="Responsible Staff",
                                     related='floor.responsible_id',
                                     help='Faculty corresponding to the room')
    room_capacity = fields.Char(string="Capacity", required=True,
                                help='Capacity of the room')
    room_member_ids = fields.One2many('education.room_member',
                                      "room_id",
                                      string='Members', help='Room members')
    amenity_ids = fields.One2many('room.amenity', 'amenity_rel_id',
                                  string='Amenity', help='Room amenities')
    allocated_number = fields.Char(string="Allocated Students",
                                   compute='_compute_allocated_number',
                                   help='Students allocated to the room')
    vacancy = fields.Char(string="Vacancy", compute='_compute_allocated_number',
                          store=True, help='Vacancy in the room')
    company_id = fields.Many2one('res.company', string='Company',
                                 default=lambda self: self.env.company,
                                 help='Company corresponding to the hostel')

    @api.onchange('hostel_id')
    def _onchange_hostel_id(self):
        """Clear floor when hostel changes"""
        if self.floor and getattr(self.floor, 'hostel_id', False) != self.hostel_id:
            self.floor = False

    @api.depends('room_member_ids')
    def _compute_allocated_number(self):
        """Counting the allocated and vacancy for room"""
        for std in self:
            std_count = self.env['education.hostel.member'].search_count(
                [('room_id', '=', std.id),
                 ('state', '=', 'allocated'),
                 ('vacated_date', '=', False)])
            if std_count > int(std.room_capacity):
                raise ValidationError(_('Room Capacity is Over'))
            std.allocated_number = std_count
            std.vacancy = int(std.room_capacity) - std_count

    @api.model
    def create(self, vals):
        """Function to create education room list"""
        res = super().create(vals)
        if 'hostel_id' in vals and vals['hostel_id']:
            self.env['education.room_list'].create({
                'room_mem_rel': res.id,
                'floor': res.floor.id,
                'hostel_room_rel2': vals['hostel_id']
            })
        return res

    def action_view_students(self):
        """Get the students allocated in the room"""
        self.ensure_one()
        domain = [
            ('room_id', '=', self.id),
            ('state', '=', 'allocated'),
            ('vacated_date', '=', False)]
        return {
            'name': _('Students'),
            'domain': domain,
            'res_model': 'education.hostel.member',
            'type': 'ir.actions.act_window',
            'view_id': False,
            'view_mode': 'list,form',
            'context': f"{{'default_room': {self.id}}}"
        }


class EduAmenity(models.Model):
    """Model created  'edu.amenity'"""
    _name = 'edu.amenity'
    _description = "Amenity"

    name = fields.Char(string="Amenity", help='Name of amenity')
