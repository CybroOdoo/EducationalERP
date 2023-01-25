# -*- coding: utf-8 -*-
from odoo import fields, models, api, _
from odoo.exceptions import ValidationError


class EducationHostel(models.Model):
    _name = 'education.hostel'
    _rec_name = 'hostel_code'
    _description = "Hostel"
    _inherit = ['mail.thread', 'mail.activity.mixin']

    hostel_name = fields.Char(string="Name", required=True, tracking=1)
    hostel_code = fields.Char(string="Code", required=True, tracking=1)
    hostel_capacity = fields.Char(string="Capacity", track_visibility='onchange', compute="_compute_student_total")
    hostel_floors = fields.Char(string="Total Floors")
    hostel_rooms = fields.One2many('education.room_list', 'hostel_room_rel2', string="Rooms")
    hostel_warden = fields.Many2one('education.faculty', required=True, string="Warden", track_visibility='onchange')
    room_rent = fields.Char(string="Room Rent", required=True, tracking=1)
    mess_fee = fields.Char(string="Mess Fee", required=True, tracking=1)
    total_students = fields.Char(string="Students", compute="_compute_student_total")
    vacancy = fields.Char(string="Vacancy", compute="_compute_student_total")
    color = fields.Integer(string='Color Index')
    total = fields.Char(string="Total Fee", compute="_compute_fee_amount")
    total_rooms = fields.Char(string="Total Rooms", compute="_compute_student_total")
    street = fields.Char('Street')
    street2 = fields.Char('Street2')
    zip = fields.Char('Zip', change_default=True)
    city = fields.Char('City')
    state_id = fields.Many2one("res.country.state", string='State')
    country_id = fields.Many2one('res.country', string='Country')
    phone = fields.Char('Phone',required=1)
    mobile = fields.Char('Mobile',required=1)
    email = fields.Char('Email')
    company_id = fields.Many2one('res.company', string='Company',
                                 default=lambda s: s.env['res.company']._company_default_get('ir.sequence'))

    # @api.multi
    def _compute_student_total(self):
        """compute the vacancy,total students and hostel capacity"""
        for dt in self:
            dt.total_rooms = len(dt.hostel_rooms)
            total_vacancy = 0
            allocated = 0
            capacity = 0
            for data in dt.hostel_rooms:
                allocated += int(data.room_mem_rel.allocated_number)
                capacity += int(data.room_mem_rel.room_capacity)
                total_vacancy += int(data.room_mem_rel.vacancy)
            dt.hostel_capacity = capacity
            dt.total_students = allocated
            dt.vacancy = total_vacancy
            if dt.hostel_capacity:
                dt.vacancy = capacity - allocated

    # @api.multi
    def _compute_fee_amount(self):
        """compute the fee amount"""
        for hst in self:
            if hst.room_rent and hst.mess_fee:
                hst.total = str(float(hst.room_rent) + float(hst.mess_fee))

    @api.model
    def create(self, vals):
        """overriding  the create method to show the validation error """
        res = super(EducationHostel, self).create(vals)
        if vals['hostel_floors']:
            raise ValidationError(_('Enter the Total Floors'))
        if not vals['phone']:
            raise ValidationError(_('Enter the Phone Number'))
        if not vals['mobile']:
            raise ValidationError(_('Enter the Mobile Number'))
        return res

    # @api.multi
    def hostel_student_view(self):
        """shows the students in the hostel"""
        self.ensure_one()
        domain = [
            ('hostel', '=', self.id),
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

