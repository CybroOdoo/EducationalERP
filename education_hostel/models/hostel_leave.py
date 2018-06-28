# -*- coding: utf-8 -*-
from odoo import fields, models, api, _
import math
from odoo.exceptions import ValidationError


class EducationHostel(models.Model):
    _name = 'education.hostel_leave'
    _rec_name = 'name'
    _description = "Leave Request"
    _inherit = ['mail.thread', 'mail.activity.mixin']

    request_id = fields.Char(string='Request ID', required=True, copy=False, readonly=True,
                             index=True, default=lambda self: _('New'))
    name = fields.Many2one('education.host_std', string="Member", required=True)
    hostel = fields.Many2one('education.hostel', string="Hostel", required=True, related='name.hostel')
    leave_from = fields.Datetime(string="Date From", required=True)
    leave_to = fields.Datetime(string="Date To", required=True)
    reason = fields.Text(String="Reason", required=True)
    number_of_days = fields.Float('Number of Days', compute='_get_number_of_days', store=True, track_visibility='onchange',
                                  readonly=True)

    company_id = fields.Many2one('res.company', string='Company',
                                 default=lambda s: s.env['res.company']._company_default_get('ir.sequence'))
    state = fields.Selection([
        ('draft', 'To Submit'),
        ('cancel', 'Cancelled'),
        ('confirm', 'To Approve'),
        ('refuse', 'Refused'),
        ('validate', 'Approved')
    ], string='Status', readonly=True, track_visibility='onchange', copy=False, default='confirm',
        help="The status is set to 'To Submit', when a leave request is created." +
             "\nThe status is 'To Approve', when leave request is confirmed by user." +
             "\nThe status is 'Refused', when leave request is refused by manager." +
             "\nThe status is 'Approved', when leave request is approved by manager.")

    @api.multi
    @api.depends('leave_from', 'leave_to')
    def _get_number_of_days(self):
        """compute the total leave days"""
        for holiday in self:
            if holiday.leave_from and holiday.leave_to:
                from_dt = fields.Datetime.from_string(holiday.leave_from)
                to_dt = fields.Datetime.from_string(holiday.leave_to)
                time_delta = to_dt - from_dt
                holiday.number_of_days = math.ceil(time_delta.days + float(time_delta.seconds) / 86400)

    @api.multi
    def action_confirm(self):
        """confirm the leave request"""
        return self.write({'state': 'confirm'})

    @api.multi
    def action_validate(self):
        """validate the leave request"""
        for holiday in self:
            holiday.write({'state': 'validate'})

    @api.multi
    def action_refuse(self):
        """refuse the leave request"""
        for holiday in self:
            holiday.write({'state': 'cancel'})

    @api.constrains('leave_from', 'leave_to')
    def check_dates(self):
        for rec in self:
            if rec.leave_from >= rec.leave_to:
                raise ValidationError(_('From date must be anterior to To date'))

    @api.model
    def create(self, vals):
        """Overriding the create method and assigning the the request id for the record"""
        if vals.get('request_id', _('New')) == _('New'):
            vals['request_id'] = self.env['ir.sequence'].next_by_code('hostel.leave') or _('New')
        res = super(EducationHostel, self).create(vals)
        return res
