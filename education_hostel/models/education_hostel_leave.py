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
"""This module defines the education hostel leave class."""

import math
from odoo import _, api, fields, models
from odoo.exceptions import ValidationError


class EducationHostelLeave(models.Model):
    """Created model 'education.hostel_leave' """
    _name = 'education.hostel_leave'
    _description = "Leave Request"
    _inherit = ['mail.thread', 'mail.activity.mixin']

    request = fields.Char(string='Request ID', required=True, copy=False,
                          readonly=True,
                          index=True, default=lambda self: _('New'))
    name = fields.Many2one('education.hostel.member', string="Member",
                           required=True, help="Sequence of member.")
    hostel_id = fields.Many2one('education.hostel', string="Hostel",
                                related='name.hostel_id',
                                help="Name of hostel.")
    leave_from = fields.Datetime(string="Date From", required=True,
                                 help="Date from which leave starts.")
    leave_to = fields.Datetime(string="Date To", required=True,
                               help="Date at which leave ends.")
    reason = fields.Text(string="Reason", required=True,
                         help="Leave reason.")
    number_of_days = fields.Float('Number of Days',
                                  compute='_compute_number_of_days',
                                  store=True,
                                  readonly=True,
                                  help="Number of leave days computed.")
    company_id = fields.Many2one('res.company', string='Company',
                                 default=lambda self: self.env.company,
                                 readonly=True)
    state = fields.Selection([
        ('draft', 'To Submit'),
        ('cancel', 'Cancelled'),
        ('confirm', 'To Approve'),
        ('refuse', 'Refused'),
        ('validate', 'Approved')
    ], string='Status', readonly=True, copy=False,
        default='draft',
        help="The status is set to 'To Submit', when a leave request is "
             "created." +
             "\nThe status is 'To Approve', when leave request is confirmed"
             " by user." +
             "\nThe status is 'Refused', when leave request is refused by"
             " manager." +
             "\nThe status is 'Approved', when leave request is approved by "
             "manager.")

    @api.depends('leave_from', 'leave_to')
    def _compute_number_of_days(self):
        """ Compute the total leave days"""
        for holiday in self:
            if holiday.leave_from and holiday.leave_to:
                from_dt = fields.Datetime.from_string(holiday.leave_from)
                to_dt = fields.Datetime.from_string(holiday.leave_to)
                time_delta = to_dt - from_dt
                holiday.number_of_days = math.ceil(
                    time_delta.days + float(time_delta.seconds) / 86400)

    def action_confirm(self):
        """Confirm the leave request"""
        return self.write({'state': 'confirm'})

    def action_validate(self):
        """Validate the leave request"""
        for holiday in self:
            holiday.write({'state': 'validate'})

    def action_refuse(self):
        """Refuse the leave request"""
        for holiday in self:
            holiday.write({'state': 'cancel'})

    @api.constrains('leave_from', 'leave_to')
    def _check_dates(self):
        """Validation for dates"""
        for rec in self:
            if rec.leave_from >= rec.leave_to:
                raise ValidationError(
                    _('From date must be anterior to To date'))

    @api.model
    def create(self, vals):
        """Overriding the create method and assigning the the request id
        for the record"""
        if vals.get('request', _('New')) == _('New'):
            vals['request'] = self.env['ir.sequence'].next_by_code(
                'hostel.leave') or _('New')
        res = super().create(vals)
        return res
