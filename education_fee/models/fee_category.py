# -*- coding: utf-8 -*-
###################################################################################
#    A part of Educational ERP Project <http://www.educationalerp.com>
#
#    Cybrosys Technologies Pvt. Ltd.
#    Copyright (C) 2021-TODAY Cybrosys Technologies (<https://www.cybrosys.com>).
#    Author: Akhilesh N S(<akhilesh@cybrosys.in>)
#
#    This program is free software: you can modify
#    it under the terms of the GNU Affero General Public License (AGPL) as
#    published by the Free Software Foundation, either version 3 of the
#    License, or (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See theDefault Debit Account
#    GNU Affero General Public License for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with this program.  If not, see <https://www.gnu.org/licenses/>.
#
###################################################################################

from odoo import models, fields, api


class FeeCategory(models.Model):
    _name = 'education.fee.category'

    name = fields.Char('Name', required=True, help='Create a fee category suitable for your institution.'
                                                   ' Like Institutuinal, Hostel, Transportation, Arts and Sports, etc')
    journal_id = fields.Many2one('account.journal', string='Journal', required=True,
                                 default=lambda self: self.env['account.journal'].search(
                                     [('code', '=', 'IFEE')], limit=1) if self.env['account.journal'].search(
                                     [('code', '=', 'IFEE')], limit=1) else False,
                                 help='Setting up of unique journal for each category help to distinguish '
                                      'account entries of each category ')
    fee_structure = fields.Boolean('Have a fee structure?', required=True, default=False,
                                   help='If any fee structure want to be included in this category you must click here.'
                                        'For an example Institution category have different kind of fee structures '
                                        'for different syllabuses')


