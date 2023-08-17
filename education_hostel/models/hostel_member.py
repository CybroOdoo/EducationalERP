# -*- coding: utf-8 -*-
from odoo import fields, models, api, _
from odoo.exceptions import ValidationError


class EducationHostelMember(models.Model):
    _name = 'education.host_std'
    _rec_name = 'hostel_admission_no'
    _description = "Hostel Member"

    member_std_name = fields.Many2one('education.student', string="Admission No",
                                      domain=[('need_hostel','=',True),('hostel','=',False)])
    member_fac_name = fields.Many2one('education.faculty', string="Name")
    name = fields.Char(string="Name")
    member_type = fields.Selection(string='Member Type',
                                   selection=[('is_faculty', 'Faculty'), ('is_student', 'Student')],
                                   default='is_student')
    email = fields.Char(string="Email", related='member_std_name.email')
    hostel_admission_no = fields.Char(string="Hostel Admission No", required=True, copy=False, readonly=True,
                                      index=True, default=lambda self: _('New'))
    phone = fields.Char(string="Phone", related='member_std_name.phone')
    mobile = fields.Char(string="Mobile", related='member_std_name.mobile')
    image = fields.Binary("Image", attachment=True,
                          help="This field holds the image used as avatar for this contact, limited to 1024x1024px")
    date_of_birth = fields.Date(string="Date Of birth", related='member_std_name.date_of_birth')
    guardian_name = fields.Char(string="Guardian", related='member_std_name.guardian_name.name')
    father_name = fields.Char(string="Father", related='member_std_name.father_name')
    mother_name = fields.Char(string="Mother", related='member_std_name.mother_name')
    gender = fields.Selection([('male', 'Male'), ('female', 'Female'), ('other', 'Other')],
                              string='Gender', required=True, default='male', track_visibility='onchange',
                              related='member_std_name.gender')
    blood_group = fields.Selection([('a+', 'A+'), ('a-', 'A-'), ('b+', 'B+'), ('o+', 'O+'), ('o-', 'O-'),
                                    ('ab-', 'AB-'), ('ab+', 'AB+')],
                                   string='Blood Group', required=True, default='a+', track_visibility='onchange')
    street = fields.Char('Street', related='member_std_name.per_street')
    street2 = fields.Char('Street2', related='member_std_name.per_street2')
    zip = fields.Char('Zip', change_default=True, related='member_std_name.per_zip')
    city = fields.Char('City', related='member_std_name.per_city')
    state_id = fields.Many2one("res.country.state", string='State', related='member_std_name.per_state_id')
    country_id = fields.Many2one('res.country', string='Country', related='member_std_name.per_country_id')
    allocation_detail = fields.One2many('education.room_member', 'room_member', string="Allocation_details")
    hostel = fields.Many2one('education.hostel', string="Hostel")
    room = fields.Many2one('education.room', string="Room")
    company_id = fields.Many2one('res.company', string='Company',
                                 default=lambda self: self.env['res.company']._company_default_get())
    state = fields.Selection([('draft', 'Draft'), ('allocated', 'Allocated'), ('vacated', 'Vacated')],
                             string='Status', default='draft')
    vacated_date = fields.Date(string="Vacated Date")

    @api.model
    def create(self, vals):
        """computing the name of the member"""
        if vals.get('hostel_admission_no', _('New')) == _('New'):
            vals['hostel_admission_no'] = self.env['ir.sequence'].next_by_code('education.host_std') or _('New')
        if vals.get('member_std_name'):
            obj = self.env['education.student'].search([('id', '=', vals.get('member_std_name'))])
            if obj.middle_name:
                vals['name'] = obj.name + '  ' + obj.middle_name + '  ' + obj.last_name
            else:
                vals['name'] = obj.name + '  ' + obj.last_name
        elif vals.get('member_fac_name'):
            obj = self.env['education.student'].search([('id', '=', vals.get('member_fac_name'))])
            if obj.middle_name:
                vals['name'] = obj.name + '  ' + obj.middle_name + '  ' + obj.last_name
            else:
                vals['name'] = obj.name + '  ' + obj.last_name
        res = super(EducationHostelMember, self).create(vals)
        return res

    @api.onchange('member_std_name', 'member_fac_name')
    def name_change(self):
        """computing the name of the member"""
        for d in self:
            if d.member_std_name:
                d.image = d.member_std_name.image_1920
                d.name = str(str(d.member_std_name.name) + ' ' + str(d.member_std_name.last_name))
            if d.member_fac_name:
                d.name = str(d.member_fac_name.name + ' ' + d.member_fac_name.last_name)


    @api.constrains('allocation_detail')
    def _check_capacity(self):
        """getting the current room and Hostel"""
        if len(self.allocation_detail) != 0:
            self.hostel = self.allocation_detail[len(self.allocation_detail)-1].hostel_room_rel.id
            self.room = self.allocation_detail[len(self.allocation_detail)-1].room_member_rel.id
            self.vacated_date = self.allocation_detail[len(self.allocation_detail)-1].vacated_date
            self.member_std_name.hostel_member = self.id
            self.member_std_name.hostel = self.hostel.id
            self.member_std_name.room = self.room.id
            self.member_std_name.hostel_fee = self.hostel.total


    def allocate_member(self):
        self.ensure_one()
        print("33333333")
        if self.allocation_detail:
            print("1234567812345678")
            length = len(self.allocation_detail)
            print("12345678345678")
            if not self.allocation_detail[length-1].allocated_date:
                raise ValidationError(_('Enter the Allocated Date'))
        return self.write({'state': 'allocated'})


    def vacate_member(self):
        self.ensure_one()
        if self.allocation_detail:
            length = len(self.allocation_detail)
            if not self.allocation_detail[length - 1].vacated_date:
                raise ValidationError(_('Enter the Vacated Date'))
        return self.write({'state': 'vacated'})


    def reallocate(self):
        return self.write({'state': 'draft'})





