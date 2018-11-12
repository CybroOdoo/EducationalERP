# -*- coding: utf-8 -*-
###################################################################################
#    A part of Educational ERP Project <https://www.educationalerp.com>
#
#    Cybrosys Technologies Pvt. Ltd.
#    Copyright (C) 2018-TODAY Cybrosys Technologies (<https://www.cybrosys.com>).
#    Author: Niyas Raphy (niyas@cybrosys.in)
#            Nikhil krishnan (nikhil@cybrosys.in)
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
from odoo import fields, models, api, _
from datetime import date


class EducationDocuments(models.Model):
    _name = 'education.documents'
    _description = "Student Documents"
    _inherit = ['mail.thread']

    @api.model
    def create(self, vals):
        """Over riding the create method to assign
        the sequence for newly creating records"""
        if vals.get('name', _('New')) == _('New'):
            vals['name'] = self.env['ir.sequence'].next_by_code('education.documents') or _('New')
        res = super(EducationDocuments, self).create(vals)
        return res

    @api.multi
    def verify_document(self):
        """Return the state to done if the documents are perfect"""
        for rec in self:
            rec.write({
                'verified_by': self.env.uid,
                'verified_date': datetime.datetime.now().strftime("%Y-%m-%d"),
                'state': 'done'
            })

    @api.multi
    def need_correction(self):
        """Return the state to correction if the documents are not perfect"""
        for rec in self:
            rec.write({
                'state': 'correction'
            })

    @api.multi
    def hard_copy_returned(self):
        """Records who return the documents and when is it returned"""
        for rec in self:
            if rec.state == 'done':
                rec.write({
                    'state': 'returned',
                    'returned_by': self.env.uid,
                    'returned_date': datetime.datetime.now().strftime("%Y-%m-%d")
                })

    name = fields.Char(string='Serial Number', copy=False, default=lambda self: _('New'))
    document_name = fields.Many2one('document.document', string='Document Type', required=True,
                                    help="Choose the type of the Document")
    description = fields.Text(string='Description', copy=False,
                              help="Enter a description about the document")
    has_hard_copy = fields.Boolean(string="Hard copy Received",
                                   help="Tick the field if the hard copy is provided")
    location_id = fields.Many2one('stock.location', 'Location', domain="[('usage', '=', 'internal')]",
                                  help="Location where which the hard copy is stored")
    location_note = fields.Char(string="Location Note", help="Enter some notes about the location")
    submitted_date = fields.Date(string="Submitted Date", default=date.today(),
                                 help="Documents are submitted on")
    received_by = fields.Many2one('hr.employee', string="Received By",
                                  help="The Documents are received by")
    returned_by = fields.Many2one('hr.employee', string="Returned By",
                                  help="The Documents are returned by")
    verified_date = fields.Date(string="Verified Date", help="Date at the verification is done")
    returned_date = fields.Date(string="Returned Date", help="Returning date")
    reference = fields.Char(string='Document Number', required=True, copy=False)
    responsible_verified = fields.Many2one('hr.employee', string="Responsible")
    responsible_returned = fields.Many2one('hr.employee', string="Responsible")

    verified_by = fields.Many2one('res.users', string='Verified by')
    application_ref = fields.Many2one('education.application', invisible=1, copy=False)
    doc_attachment_id = fields.Many2many('ir.attachment', 'doc_attach_rel', 'doc_id', 'attach_id3', string="Attachment",
                                         help='You can attach the copy of your document', copy=False)
    state = fields.Selection([('draft', 'Draft'), ('correction', 'Correction'), ('done', 'Done'),
                              ('returned', 'Returned')],
                             string='State', required=True, default='draft', track_visibility='onchange')


class HrEmployeeAttachment(models.Model):
    _inherit = 'ir.attachment'

    doc_attach_rel = fields.Many2many('education.documents', 'doc_attachment_id', 'attach_id3', 'doc_id',
                                      string="Attachment", invisible=1)


class DocumentDocument(models.Model):
    _name = 'document.document'
    _description = "Documents Type"

    name = fields.Char(string='Name', required=True)
    description = fields.Char(string='Description')
