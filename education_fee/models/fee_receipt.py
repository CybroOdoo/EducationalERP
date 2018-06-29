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

import datetime
from odoo import models, fields, api, _


class FeeReceipts(models.Model):
    _inherit = 'account.invoice'

    @api.onchange('fee_structure')
    def _get_fee_lines(self):
        """Set default fee lines based on selected fee structure"""
        lines = []
        for item in self:
            for line in item.fee_structure.fee_type_ids:
                name = line.fee_type.product_id.description_sale
                if not name:
                    name = line.fee_type.product_id.name
                fee_line = {
                    'price_unit': line.fee_amount,
                    'quantity': 1.00,
                    'product_id': line.fee_type.product_id,
                    'name': name,
                    'account_id': item.journal_id.default_debit_account_id
                }
                lines.append((0, 0, fee_line))
            item.invoice_line_ids = lines

    @api.onchange('student_id', 'fee_category_id', 'payed_from_date', 'payed_to_date')
    def _get_partner_details(self):
        """Student_id is inherited from res_partner. Set partner_id from student_id """
        self.ensure_one()
        lines = []
        for item in self:
            item.invoice_line_ids = lines
            item.partner_id = item.student_id.partner_id
            item.class_division_id = item.student_id.class_id
            date_today = datetime.date.today()
            company = self.env.user.company_id
            from_date = item.payed_from_date
            to_date = item.payed_to_date
            if not from_date:
                from_date = company.compute_fiscalyear_dates(date_today)['date_from']
            if not to_date:
                to_date = date_today
            if item.partner_id and item.fee_category_id:
                invoice_ids = self.env['account.invoice'].search([('partner_id', '=', item.partner_id.id),
                                                                  ('date_invoice', '>=', from_date),
                                                                  ('date_invoice', '<=', to_date),
                                                                  ('fee_category_id', '=', item.fee_category_id.id)])
                invoice_line_list = []
                for invoice in invoice_ids:
                    for line in invoice.invoice_line_ids:
                        fee_line = {
                            'price_unit': line.price_unit,
                            'quantity': line.quantity,
                            'product_id': line.product_id,
                            'price_subtotal': line.price_subtotal,
                            'invoice_line_tax_ids': line.invoice_line_tax_ids,
                            'discount': line.discount,
                            'date': line.invoice_id.date_invoice,
                            'receipt_no': line.invoice_id.number
                        }
                        invoice_line_list.append((0, 0, fee_line))
                item.payed_line_ids = invoice_line_list

    @api.onchange('fee_category_id')
    def _get_fee_structure(self):
        """ Set domain for fee structure based on category"""
        self.journal_id = self.fee_category_id.journal_id
        self.invoice_line_ids = None
        return {
            'domain': {
                'fee_structure': [('category_id', '=', self.fee_category_id.id)]
            }
        }

    student_id = fields.Many2one('education.student', string='Admission No')
    student_name = fields.Char(string='Name', related='student_id.partner_id.name', store=True)
    class_division_id = fields.Many2one('education.class.division', string='Class')
    fee_structure = fields.Many2one('education.fee.structure', string='Fee Structure')
    is_fee = fields.Boolean(string='Is Fee', store=True, default=False)
    fee_category_id = fields.Many2one('education.fee.category', string='Category', required=True,
                                      default=lambda self: self.env['education.fee.category'].search([], limit=1))
    is_fee_structure = fields.Boolean('Have a fee structure?', related='fee_category_id.fee_structure')
    payed_line_ids = fields.One2many('payed.lines', 'partner_id', string='Payments Done',
                                   readonly=True, store=False)
    payed_from_date = fields.Date(string='From Date')
    payed_to_date = fields.Date(string='To Date')

    @api.model
    def create(self, vals):
        """ Adding two field to invoice. is_fee use to display fee items only in fee tree view"""
        partner_id = self.env['res.partner'].browse(vals['partner_id'])
        vals.update({
            'is_fee': True,
            'student_name': partner_id.name
        })
        res = super(FeeReceipts, self).create(vals)
        return res


class InvoiceLineInherit(models.Model):
    _inherit = 'account.invoice.line'

    @api.onchange('product_id')
    def _get_category_domain(self):
        """Set domain for invoice lines depend on selected category"""
        if self.invoice_id.fee_category_id:
            fee_types = self.env['education.fee.type'].search([('category_id', '=',  self.invoice_id.fee_category_id.id)])
            fee_list = []
            for fee in fee_types:
                fee_list.append(fee.product_id.id)
            vals = {
                'domain': {
                    'product_id': [('id', 'in', tuple(fee_list))]
                }
            }
            return vals


class PayedLinens(models.Model):
    _name = 'payed.lines'
    _inherit = 'account.invoice.line'

    date = fields.Date(string='Date', readonly=True)
    receipt_no = fields.Char('Receipt No')
