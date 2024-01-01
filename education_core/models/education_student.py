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
from odoo import api, fields, models, _


class EducationStudent(models.Model):
    """For managing student records"""
    _name = 'education.student'
    _inherit = ['mail.thread']
    _inherits = {'res.partner': 'partner_id'}
    _description = 'Student record'

    def action_student_documents(self):
        """Return the documents student submitted
        along with the admission application"""
        self.ensure_one()
        if self.application_id.id:
            documents = self.env['education.documents'].search(
                [('application_ref_id', '=', self.application_id.id)])
            documents_list = documents.mapped('id')
            return {
                'domain': [('id', 'in', documents_list)],
                'name': _('Documents'),
                'view_mode': 'tree,form',
                'res_model': 'education.document',
                'view_id': False,
                'context': {
                    'default_application_ref_id': self.application_id.id},
                'type': 'ir.actions.act_window'
            }

    @api.model
    def name_search(self, name, args=None, operator='ilike', limit=100):
        if name:
            recs = self.search(
                [('name', operator, name)] + (args or []), limit=limit)
            if not recs:
                recs = self.search(
                    [('ad_no', operator, name)] + (args or []), limit=limit)
            return recs.name_get()
        return super(EducationStudent, self).name_search(
            name, args=args, operator=operator, limit=limit)

    @api.model
    def create(self, vals):
        """Overriding the create method to assign
        sequence for the newly creating the record"""
        vals['ad_no'] = self.env['ir.sequence'].next_by_code(
            'education.student')
        res = super(EducationStudent, self).create(vals)
        return res

    partner_id = fields.Many2one(
        'res.partner', string='Partner', required=True,
        ondelete="cascade", help="Related partner of the student")
    middle_name = fields.Char(string='Middle Name', help="Enter middle name")
    last_name = fields.Char(string='Last Name', help="Enter last name")
    date_of_birth = fields.Date(string="Date of Birth", requird=True,
                                help="Enter date of birth of student")
    guardian_id = fields.Many2one('res.partner', string="Guardian",
                                  domain=[('is_parent', '=', True)],
                                  help="Select guardian of the student")
    father_name = fields.Char(string="Father", help="Father of the student")
    mother_name = fields.Char(string="Mother", help="Mother of the student")
    class_division_id = fields.Many2one('education.class.division',
                                        string="Class",
                                        help="Class of the student")
    admission_class_id = fields.Many2one('education.class',
                                         string="Admission Class",
                                         help="Admission taken class")
    ad_no = fields.Char(string="Admission Number", readonly=True,
                        help="Admission number of student")
    gender = fields.Selection([('male', 'Male'), ('female', 'Female'),
                               ('other', 'Other')], string='Gender',
                              required=True, default='male',
                              track_visibility='onchange',
                              help="Gender details")
    blood_group = fields.Selection(
        [('a+', 'A+'), ('a-', 'A-'), ('b+', 'B+'), ('o+', 'O+'),
         ('o-', 'O-'), ('ab-', 'AB-'), ('ab+', 'AB+')],
        string='Blood Group', required=True, help="Blood group of student",
        default='a+', track_visibility='onchange')
    company_id = fields.Many2one('res.company', string='Company',
                                 help="Current company")
    per_street = fields.Char(string="Street", help="Enter the street")
    per_street2 = fields.Char(string="Street2", help="Enter the street2")
    per_zip = fields.Char(change_default=True, string='ZIP code',
                          help="Enter the Zip Code")
    per_city = fields.Char(string='City', help="Enter the City name")
    per_state_id = fields.Many2one("res.country.state",
                                   string='State', ondelete='restrict',
                                   help="Select the State where you are from")
    per_country_id = fields.Many2one('res.country',
                                     string='Country', ondelete='restrict',
                                     help="Select the Country")
    medium_id = fields.Many2one('education.medium',
                                string="Medium", required=True,
                                help="Choose the Medium of class,"
                                     " like English, Hindi etc")
    sec_lang_id = fields.Many2one('education.subject',
                                  string="Second language",
                                  required=True,
                                  help="Choose the Second language",
                                  domain=[('is_language', '=', True)])
    mother_tongue = fields.Char(string="Mother Tongue", required=True,
                                domain=[('is_language', '=', True)],
                                help="Enter Student's Mother Tongue")
    caste = fields.Char(string="Caste", help="My Caste is ")
    religion = fields.Char(string="Religion", help="My Religion is ")
    is_same_address = fields.Boolean(string="Is same Address?",
                                     help="Tick the field if the Present and "
                                          "permanent address is same")
    nationality_id = fields.Many2one('res.country',
                                     string='Nationality', ondelete='restrict',
                                     help="Select the Nationality")
    application_id = fields.Many2one('education.application',
                                     string="Application No",
                                     help="Application number of student")
    class_history_ids = fields.One2many('education.class.history',
                                        'student_id',
                                        string="Class Details",
                                        help="Previous class history details")

    _sql_constraints = [
        ('ad_no', 'unique(ad_no)',
         "Another Student already exists with this admission number!"),
    ]
