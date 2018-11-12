# -*- coding: utf-8 -*-
###################################################################################
#
#
#    Cybrosys Technologies Pvt. Ltd.
#    Copyright (C) 2018-TODAY Cybrosys Technologies (<https://www.cybrosys.com>).
#    Author: Niyas Raphy (<https://www.cybrosys.com>)
#            Nikhil krishnan (nikhil@cybrosys.in)
#    This program is free software: you can modify
#    it under the terms of the GNU Affero General Public License (AGPL) as
#    published by the Free Software Foundation, either version 3 of the
#    License, or (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Affero General Public License for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with this program.  If not, see <https://www.gnu.org/licenses/>.
#
####################################################################################

from odoo import fields, models, api


class ApplicationReject(models.TransientModel):
    _name = 'application.reject'
    _description = 'Choose Reject Reason'

    reject_reason_id = fields.Many2one('application.reject.reason', string="Reason",
                                       help="Select Reason for rejecting the Applications")

    @api.multi
    def action_reject_reason_apply(self):
        """Write the reject reason of the application"""
        for rec in self:
            application = self.env['education.application'].browse(self.env.context.get('active_ids'))
            application.write({'reject_reason': rec.reject_reason_id.id})
            return application.reject_application()


class ApplicationRejectReason(models.Model):
    _name = 'application.reject.reason'
    _description = 'Reject ReasonS'

    name = fields.Char(string="Reason", required=True,
                       help="Possible Reason for rejecting the Applications")
