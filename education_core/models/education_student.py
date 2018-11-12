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

from odoo import fields, models, api, _


class EducationStudent(models.Model):
    _name = 'education.student'
    _inherit = ['mail.thread']
    _inherits = {'res.partner': 'partner_id'}
    _description = 'Student record'
    _rec_name = 'name'

    @api.multi
    def student_documents(self):
        """Return the documents student submitted
        along with the admission application"""
        self.ensure_one()
        if self.application_id.id:
            documents = self.env['education.documents'].search([('application_ref', '=', self.application_id.id)])
            documents_list = documents.mapped('id')
            return {
                'domain': [('id', 'in', documents_list)],
                'name': _('Documents'),
                'view_type': 'form',
                'view_mode': 'tree,form',
                'res_model': 'education.documents',
                'view_id': False,
                'context': {'default_application_ref': self.application_id.id},
                'type': 'ir.actions.act_window'
            }

    @api.model
    def name_search(self, name, args=None, operator='ilike', limit=100):
        if name:
            recs = self.search([('name', operator, name)] + (args or []), limit=limit)
            if not recs:
                recs = self.search([('ad_no', operator, name)] + (args or []), limit=limit)
            return recs.name_get()
        return super(EducationStudent, self).name_search(name, args=args, operator=operator, limit=limit)

    @api.model
    def create(self, vals):
        """Over riding the create method to assign sequence for the newly creating the record"""
        vals['ad_no'] = self.env['ir.sequence'].next_by_code('education.student')
        res = super(EducationStudent, self).create(vals)
        return res

    partner_id = fields.Many2one(
        'res.partner', string='Partner', required=True, ondelete="cascade")
    middle_name = fields.Char(string='Middle Name')
    last_name = fields.Char(string='Last Name')
    application_no = fields.Char(string="Application No")
    date_of_birth = fields.Date(string="Date Of birth", requird=True)
    guardian_name = fields.Many2one('res.partner', string="Guardian", domain=[('is_parent', '=', True)])
    father_name = fields.Char(string="Father")
    mother_name = fields.Char(string="Mother")
    class_id = fields.Many2one('education.class.division', string="Class")
    admission_class = fields.Many2one('education.class', string="Admission Class")
    ad_no = fields.Char(string="Admission Number", readonly=True)
    gender = fields.Selection([('male', 'Male'), ('female', 'Female'), ('other', 'Other')],
                              string='Gender', required=True, default='male', track_visibility='onchange')
    blood_group = fields.Selection([('a+', 'A+'), ('a-', 'A-'), ('b+', 'B+'), ('o+', 'O+'), ('o-', 'O-'),
                                    ('ab-', 'AB-'), ('ab+', 'AB+')],
                                   string='Blood Group', required=True, default='a+', track_visibility='onchange')
    company_id = fields.Many2one('res.company', string='Company')
    per_street = fields.Char()
    per_street2 = fields.Char()
    per_zip = fields.Char(change_default=True)
    per_city = fields.Char()
    per_state_id = fields.Many2one("res.country.state", string='State', ondelete='restrict')
    per_country_id = fields.Many2one('res.country', string='Country', ondelete='restrict')
    medium = fields.Many2one('education.medium', string="Medium", required=True)
    sec_lang = fields.Many2one('education.subject', string="Second language", required=True, domain=[('is_language', '=', True)])
    mother_tongue = fields.Many2one('education.mother.tongue', string="Mother Tongue", required=True, domain=[('is_language', '=', True)])
    caste_id = fields.Many2one('religion.caste', string="Caste")
    religion_id = fields.Many2one('religion.religion', string="Religion")
    is_same_address = fields.Boolean(string="Is same Address?")
    nationality = fields.Many2one('res.country', string='Nationality', ondelete='restrict')
    application_id = fields.Many2one('education.application', string="Application No")
    class_history_ids = fields.One2many('education.class.history', 'student_id', string="Application No")

    _sql_constraints = [
        ('ad_no', 'unique(ad_no)', "Another Student already exists with this admission number!"),
    ]
