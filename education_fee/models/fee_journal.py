# -*- coding: utf-8 -*-
###################################################################################
#    A part of Educational ERP Project <http://www.educationalerp.com>
#
#    Cybrosys Technologies Pvt. Ltd.
#    Copyright (C) 2018-TODAY Cybrosys Technologies (<https://www.cybrosys.com>).
#    Author: Akhilesh N S(<akhilesh@cybrosys.in>)
#
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
###################################################################################

from odoo import models, fields, api, _


class InheritJournal(models.Model):
    _inherit = 'account.journal'

    is_fee = fields.Boolean('Is Educational fee?', default=False)

    @api.multi
    def action_create_new_fee(self):
        view = self.env.ref('education_fee.receipt_form')
        ctx = self._context.copy()
        ctx.update({'journal_id': self.id, 'default_journal_id': self.id})
        return {
            'view_type': 'form',
            'view_mode': 'form',
            'views': [(view.id, 'form')],
            'res_model': 'account.invoice',
            'view_id': view.id,
            'context': ctx,
            'type': 'ir.actions.act_window',
        }
