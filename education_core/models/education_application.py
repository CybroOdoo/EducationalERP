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

from odoo import fields, models, _, api
from odoo.exceptions import ValidationError


class StudentApplication(models.Model):
    _name = 'education.application'
    _inherit = ['mail.thread']
    _description = 'Applications for the admission'
    _order = 'id desc'

    @api.model
    def create(self, vals):
        """Overriding the create method and assigning the the sequence for the record"""
        if vals.get('application_no', _('New')) == _('New'):
            vals['application_no'] = self.env['ir.sequence'].next_by_code('education.application') or _('New')
        res = super(StudentApplication, self).create(vals)
        return res

    @api.multi
    def unlink(self):
        """Return warning if the application is not in the reject state"""
        for rec in self:
            if rec.state != 'reject':
                raise ValidationError(_("Application can only be deleted after rejecting it"))

    @api.multi
    def send_to_verify(self):
        """Button action for sending the application for the verification"""
        for rec in self:
            document_ids = self.env['education.documents'].search([('application_ref', '=', rec.id)])
            if not document_ids:
                raise ValidationError(_('No Documents provided'))
            rec.write({
                'state': 'verification'
            })

    @api.multi
    def create_student(self):
        """Create student from the application and data and return the student"""
        for rec in self:
            values = {
                'name': rec.name,
                'last_name': rec.last_name,
                'middle_name': rec.middle_name,
                'application_id': rec.id,
                'father_name': rec.father_name,
                'mother_name': rec.mother_name,
                'guardian_name': rec.guardian_name.id,
                'street': rec.street,
                'street2': rec.street2,
                'city': rec.city,
                'state_id': rec.state_id.id,
                'country_id': rec.country_id.id,
                'zip': rec.zip,
                'is_same_address': rec.is_same_address,
                'per_street': rec.per_street,
                'per_street2': rec.per_street2,
                'per_city': rec.per_city,
                'per_state_id': rec.per_state_id.id,
                'per_country_id': rec.per_country_id.id,
                'per_zip': rec.per_zip,
                'gender': rec.gender,
                'date_of_birth': rec.date_of_birth,
                'blood_group': rec.blood_group,
                'nationality': rec.nationality.id,
                'email': rec.email,
                'mobile': rec.mobile,
                'phone': rec.phone,
                'image': rec.image,
                'is_student': True,
                'medium': rec.medium.id,
                'religion_id': rec.religion_id.id,
                'caste_id': rec.caste_id.id,
                'sec_lang': rec.sec_lang.id,
                'mother_tongue': rec.mother_tongue.id,
                'admission_class': rec.admission_class.id,
                'company_id': rec.company_id.id,
            }
            if not rec.is_same_address:
                pass
            else:
                values.update({
                    'per_street': rec.street,
                    'per_street2': rec.street2,
                    'per_city': rec.city,
                    'per_state_id': rec.state_id.id,
                    'per_country_id': rec.country_id.id,
                    'per_zip': rec.zip,
                })

            student = self.env['education.student'].create(values)
            rec.write({
                'state': 'done'
            })
            return {
                'name': _('Student'),
                'view_type': 'form',
                'view_mode': 'form',
                'res_model': 'education.student',
                'type': 'ir.actions.act_window',
                'res_id': student.id,
                'context': self.env.context
            }

    @api.multi
    def reject_application(self):
        """Rejecting the student application for admission"""
        for rec in self:
            rec.write({
                'state': 'reject'
            })

    @api.multi
    def application_verify(self):
        """Verifying the student application. Return warning if no Documents
         provided or if the provided documents are not in done state"""
        for rec in self:
            document_ids = self.env['education.documents'].search([('application_ref', '=', rec.id)])
            if document_ids:
                doc_status = document_ids.mapped('state')
                if all(state in ('done', 'returned') for state in doc_status):
                    rec.write({
                        'verified_by': self.env.uid,
                        'state': 'approve'
                    })
                else:
                    raise ValidationError(_('All Documents are not Verified Yet, '
                                            'Please complete the verification'))

            else:
                raise ValidationError(_('No Documents provided'))

    @api.multi
    def _document_count(self):
        """Return the count of the documents provided"""
        for rec in self:
            document_ids = self.env['education.documents'].search([('application_ref', '=', rec.id)])
            rec.document_count = len(document_ids)

    @api.multi
    def document_view(self):
        """Return the list of documents provided along with this application"""
        self.ensure_one()
        domain = [
            ('application_ref', '=', self.id)]
        return {
            'name': _('Documents'),
            'domain': domain,
            'res_model': 'education.documents',
            'type': 'ir.actions.act_window',
            'view_id': False,
            'view_mode': 'tree,form',
            'view_type': 'form',
            'help': _('''<p class="oe_view_nocontent_create">
                               Click to Create for New Documents
                            </p>'''),
            'limit': 80,
            'context': "{'default_application_ref': '%s'}" % self.id
        }

    name = fields.Char(string='Name', required=True, help="Enter First name of Student")
    middle_name = fields.Char(string='Middle Name', help="Enter Middle name of Student")
    last_name = fields.Char(string='Last Name', help="Enter Last name of Student")
    prev_school = fields.Many2one('education.institute', string='Previous Institution',
                                  help="Enter the name of previous institution")
    image = fields.Binary(string='Image', help="Provide the image of the Student")
    academic_year_id = fields.Many2one('education.academic.year', string='Academic Year',
                                       help="Choose Academic year for which the admission is choosing")
    medium = fields.Many2one('education.medium', string="Medium", required=True,
                             help="Choose the Medium of class, like English, Hindi etc")
    sec_lang = fields.Many2one('education.subject', string="Second language",
                               required=True, domain=[('is_language', '=', True)],
                               help="Choose the Second language")
    mother_tongue = fields.Many2one('education.mother.tongue', string="Mother Tongue",
                                    required=True, help="Enter Student's Mother Tongue")
    admission_class = fields.Many2one('education.class', string="Class", required=True,
                                      help="Enter Class to which the admission is seeking")
    admission_date = fields.Datetime('Admission Date', default=fields.Datetime.now, required=True)
    application_no = fields.Char(string='Application  No', required=True, copy=False, readonly=True,
                       index=True, default=lambda self: _('New'))
    company_id = fields.Many2one('res.company', string='Company', default=lambda self: self.env.user.company_id)
    email = fields.Char(string="Email", help="Enter E-mail id for contact purpose")
    phone = fields.Char(string="Phone", help="Enter Phone no. for contact purpose")
    mobile = fields.Char(string="Mobile", required=True, help="Enter Mobile num for contact purpose")
    nationality = fields.Many2one('res.country', string='Nationality', ondelete='restrict',
                                  help="Select the Nationality")

    street = fields.Char(string='Street', help="Enter the street")
    street2 = fields.Char(string='Street2', help="Enter the street2")
    zip = fields.Char(change_default=True, string='ZIP code', help="Enter the Zip Code")
    city = fields.Char(string='City', help="Enter the City name")
    state_id = fields.Many2one("res.country.state", string='State', ondelete='restrict',
                               help="Select the State where you are from")
    country_id = fields.Many2one('res.country', string='Country', ondelete='restrict',
                                 help="Select the Country")
    is_same_address = fields.Boolean(string="Permanent Address same as above", default=True,
                                     help="Tick the field if the Present and permanent address is same")
    per_street = fields.Char(string='Street', help="Enter the street")
    per_street2 = fields.Char(string='Street2', help="Enter the street2")
    per_zip = fields.Char(change_default=True, string='ZIP code', help="Enter the Zip Code")
    per_city = fields.Char(string='City', help="Enter the City name")
    per_state_id = fields.Many2one("res.country.state", string='State', ondelete='restrict',
                                   help="Select the State where you are from")
    per_country_id = fields.Many2one('res.country', string='Country', ondelete='restrict',
                                     help="Select the Country")
    date_of_birth = fields.Date(string="Date Of birth", required=True, help="Enter your DOB")
    guardian_name = fields.Many2one('res.partner', string="Guardian", domain=[('is_parent', '=', True)], required=True,
                                    help="Tell us who will take care of you")
    description = fields.Text(string="Note")
    father_name = fields.Char(string="Father", help="Proud to say my father is")
    mother_name = fields.Char(string="Mother", help="My mother's name is")
    religion_id = fields.Many2one('religion.religion', string="Religion", help="My Religion is ")
    caste_id = fields.Many2one('religion.caste', string="Caste", help="My Caste is ")
    class_id = fields.Many2one('education.class.division', string="Class")
    active = fields.Boolean(string='Active', default=True)
    document_count = fields.Integer(compute='_document_count', string='# Documents')
    verified_by = fields.Many2one('res.users', string='Verified by', help="The Document is verified by")
    reject_reason = fields.Many2one('application.reject.reason', string='Reject Reason',
                                    help="Application is rejected because")
    gender = fields.Selection([('male', 'Male'), ('female', 'Female'), ('other', 'Other')],
                              string='Gender', required=True, default='male', track_visibility='onchange',
                              help="Your Gender is ")
    blood_group = fields.Selection([('a+', 'A+'), ('a-', 'A-'), ('b+', 'B+'), ('o+', 'O+'), ('o-', 'O-'),
                                    ('ab-', 'AB-'), ('ab+', 'AB+')],
                                   string='Blood Group', required=True, default='a+', track_visibility='onchange',
                                   help="Your Blood Group is ")
    state = fields.Selection([('draft', 'Draft'), ('verification', 'Verify'),
                              ('approve', 'Approve'), ('reject', 'Reject'), ('done', 'Done')],
                             string='State', required=True, default='draft', track_visibility='onchange')
