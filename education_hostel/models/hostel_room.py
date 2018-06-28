# -*- coding: utf-8 -*-
from odoo import fields, models, api, _
from odoo.exceptions import ValidationError


class EducationRooms(models.Model):
    _name = 'education.room'
    _rec_name = 'room_name'
    _description = "Room"
    _inherit = ['mail.thread', 'mail.activity.mixin']

    hostel = fields.Many2one('education.hostel', required=True, string="Hostel")
    room_name = fields.Char(string="Room Name", required=True, track_visibility='onchange')
    room_code = fields.Char(string="Room Code", required=True, track_visibility='onchange')
    floor = fields.Many2one('education.floor', required=True, string="Floor")
    responsible = fields.Many2one('education.faculty', string="Responsible Staff", related='floor.responsible')
    room_capacity = fields.Char(string="Capacity", required=True, track_visibility='onchange')
    room_members = fields.One2many('education.room_member', "room_member_rel", track_visibility='onchange')
    room_amenity = fields.One2many('room.amenity', 'amenity_rel', track_visibility='onchange')
    allocated_number = fields.Char(string="Allocated Students", compute='get_total_allocated')
    vacancy = fields.Char(string="Vacancy", compute='get_total_allocated')
    company_id = fields.Many2one('res.company', string='Company',
                                 default=lambda self: self.env['res.company']._company_default_get())

    @api.onchange('hostel', 'floor')
    def get_rooms(self):
        """adding domain for floors"""
        hostel = None
        if self.hostel:
            hostel = self.hostel.id
        return {
            'domain': {
                'floor': [('hostel', '=', hostel)]
            }
        }

    @api.constrains('room_members')
    def get_total_allocated(self):
        """counting the allocated and vacancy for room"""
        for std in self:
            std_count = self.env['education.host_std'].search_count([('room', '=', std.id),
                                                                     ('state', '!=', 'vacated'),
                                                                     ('vacated_date', '=', False)])
            if std_count > int(std.room_capacity):
                raise ValidationError(_('Room Capacity is Over'))
            std.allocated_number = std_count
            std.vacancy = int(std.room_capacity)-std_count

    @api.model
    def create(self, vals):
        res = super(EducationRooms, self).create(vals)
        if 'hostel' in vals and vals['hostel']:
            self.env['education.room_list'].create({
                                'room_mem_rel': res.id,
                                'floor': res.floor.id,
                                'hostel_room_rel2': vals['hostel']
                             })
        return res

    @api.multi
    def student_view(self):
        """get the students allocated in the room"""
        self.ensure_one()
        domain = [
            ('room', '=', self.id),
            ('state', '=', 'allocated'),
            ('vacated_date', '=', False)]
        return {
            'name': _('Students'),
            'domain': domain,
            'res_model': 'education.host_std',
            'type': 'ir.actions.act_window',
            'view_id': False,
            'view_mode': 'tree,form',
            'view_type': 'form',
            'context': "{'default_room': '%s'}" % self.id
        }


class EducationRoomMem(models.Model):
    _name = 'education.room_list'

    room_mem_rel = fields.Many2one('education.room', string="Room")
    floor = fields.Many2one('education.floor', string="Floor", related='room_mem_rel.floor')
    hostel_room_rel2 = fields.Many2one('education.hostel', string="Room", related='room_mem_rel.hostel')


class EducationRoomMember(models.Model):
    _name = 'education.room_member'
    _rec_name = 'room_member'
    _description = "Room Member"

    room_member_rel = fields.Many2one('education.room', string="Room")
    allocated_date = fields.Date(string="Allocated Date")
    vacated_date = fields.Date(string="Vacated Date")
    room_member = fields.Many2one('education.host_std')
    floor = fields.Many2one('education.floor', string="Floor", related='room_member_rel.floor')
    hostel_room_rel = fields.Many2one('education.hostel', string="Hostel", related='room_member_rel.hostel')
    student_id = fields.Many2one('education.student', string="Student")

    @api.onchange('hostel_room_rel')
    def get_rooms(self):
        """adding domain for room"""
        hostel = None
        if self.hostel_room_rel:
            hostel = self.hostel_room_rel.id
        return {
            'domain': {
                'room_member_rel': [('hostel', '=', hostel)]
            }
        }


class EducationRoomAmenity(models.Model):
    _name = 'room.amenity'
    _description = "Amenity"

    amenity = fields.Many2one('education.amenities', string="Amenity", required=True)
    qty = fields.Integer(string="Quantity")
    amenity_rel = fields.Many2one('education.room')

    @api.constrains('qty')
    def check_qty(self):
        for rec in self:
            if rec.qty <= 0:
                raise ValidationError(_('Quantity must be positive'))


class EduAmen(models.Model):
    _name = 'edu.amenity'
    _description = "Amenity"

    name = fields.Char(string="Amenity")





