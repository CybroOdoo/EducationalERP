# -*- coding: utf-8 -*-
from odoo import fields, models, _, api
from odoo.exceptions import ValidationError


class EducationFloors(models.Model):
    _name = 'education.floor'
    _rec_name = "floor_no"
    _description = "Floor"
    _inherit = ['mail.thread', 'mail.activity.mixin']

    floor_no = fields.Char(string="Floor", required=True)
    hostel = fields.Many2one('education.hostel', required=True, string="Hostel")
    responsible = fields.Many2one('education.faculty', string="Responsible Staff", track_visibility='onchange')

    company_id = fields.Many2one('res.company', string='Company',
                                 default=lambda s: s.env['res.company']._company_default_get('ir.sequence'))

    @api.model
    def create(self, vals):
        """check the floor count of hostel"""
        res = super(EducationFloors, self).create(vals)
        if vals['hostel']:
            floor = 0.0
            obj = self.env['education.hostel'].browse(vals['hostel'])
            floor_count = self.search_count([('hostel', '=', vals['hostel']), ('id', '!=', self.id)])
            if obj:
                floor += float(obj.hostel_floors)
                if floor < floor_count:
                    raise ValidationError(_('Floor Count is High'))
        return res


