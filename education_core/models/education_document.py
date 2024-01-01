# -*- coding: utf-8 -*-
##############################################################################
#
#    Cybrosys Technologies Pvt. Ltd.
#
#    Copyright (C) 2023-TODAY Cybrosys Technologies(<https://www.cybrosys.com>)
#    Author: Raneesha M K (odoo@cybrosys.com)
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
##############################################################################
import datetime
from odoo import api, fields, models, _


class EducationDocument(models.Model):
    """For managing student document details and verification"""
    _name = 'education.document'
    _description = "Student Documents"
    _inherit = ['mail.thread']

    @api.model
    def create(self, vals):
        """Overriding the create method to assign
        the sequence for newly creating records"""
        if vals.get('name', _('New')) == _('New'):
            vals['name'] = self.env['ir.sequence'].next_by_code(
                'education.document') or _('New')
        res = super(EducationDocument, self).create(vals)
        return res

    def action_verify_document(self):
        """Return the state to done if the documents are perfect"""
        for rec in self:
            rec.write({
                'verified_by_id': self.env.uid,
                'verified_date': datetime.datetime.now().strftime("%Y-%m-%d"),
                'state': 'done'
            })

    def action_need_correction(self):
        """Return the state to correction if the documents are not perfect"""
        for rec in self:
            rec.write({
                'state': 'correction'
            })

    def action_hard_copy_returned(self):
        """Records who return the documents and when is it returned"""
        for rec in self:
            if rec.state == 'done':
                rec.write({
                    'state': 'returned',
                    'returned_by_id': self.env.uid,
                    'returned_date': datetime.datetime.now().strftime(
                        "%Y-%m-%d")
                })

    name = fields.Char(string='Serial Number', copy=False,
                       help="Serial number of document",
                       default=lambda self: _('New'))
    document_type_id = fields.Many2one('document.document',
                                       string='Document Type', required=True,
                                       help="Choose the type of the Document")
    description = fields.Text(string='Description', copy=False,
                              help="Enter a description about the document")
    has_hard_copy = fields.Boolean(
        string="Hard copy Received",
        help="Tick the field if the hard copy is provided")
    location_id = fields.Many2one(
        'stock.location', 'Location',
        domain="[('usage', '=', 'internal')]",
        help="Location where which the hard copy is stored")
    location_note = fields.Char(string="Location Note",
                                help="Enter some notes about the location")
    submitted_date = fields.Date(string="Submitted Date",
                                 default=fields.Date.today(),
                                 help="Documents are submitted on")
    received_by_id = fields.Many2one('hr.employee',
                                     string="Received By",
                                     help="The Documents are received by")
    returned_by_id = fields.Many2one('hr.employee',
                                     string="Returned By",
                                     help="The Documents are returned by")
    verified_date = fields.Date(string="Verified Date",
                                help="Date at the verification is done")
    returned_date = fields.Date(string="Returned Date", help="Returning date")
    responsible_verified_id = fields.Many2one('hr.employee',
                                              string="Responsible",
                                              help="Responsible person to "
                                                   "verify the document")
    responsible_returned_id = fields.Many2one('hr.employee',
                                              string="Responsible",
                                              help="Responsible person to "
                                                   "verify the returned "
                                                   "document")
    verified_by_id = fields.Many2one('res.users',
                                     string='Verified by',
                                     help="Document is verified by the user")
    application_ref_id = fields.Many2one('education.application',
                                         copy=False, string="Application Ref",
                                         help="Application reference "
                                              "of document")
    doc_attachment_ids = fields.Many2many(
        'ir.attachment', 'education_doc_attach_rel',
        'doc_id', 'attach_id3', string="Attachment", copy=False,
        help='You can attach the copy of your document')
    state = fields.Selection(
        [('draft', 'Draft'), ('correction', 'Correction'),
         ('done', 'Done'), ('returned', 'Returned')], string='State',
        required=True, default='draft',
        track_visibility='onchange', help="Stages of document ")
