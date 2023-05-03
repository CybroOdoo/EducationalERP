# -*- coding: utf-8 -*-
###############################################################################
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
###############################################################################
import base64
from odoo import http
from odoo.http import request


class OnlineAdmission(http.Controller):
    """Controller for taking online admission"""

    @http.route('/online_admission', type='http', auth='public', website=True)
    def online_admission(self):
        """To pass certain default field values to the website registration form."""
        vals = {
            'class': request.env['education.class'].sudo().search([]),
            'year': request.env['education.academic.year'].sudo().search([]),
            'medium': request.env['education.medium'].sudo().search([]),
            'sec_lang': request.env['education.subject'].sudo().search([]),
            'tongue': request.env['education.mother.tongue'].sudo().search([]),
            'doc_type': request.env['document.document'].sudo().search([])
        }
        return request.render('education_student_portal.online_admission', vals)

    @http.route('/admission/submit', type='http', auth='public', website=True)
    def register_admission(self, **vals):
        """ This will create a new record with the values in the back end."""
        if vals:
            guardian = request.env['res.partner'].sudo().create({
                'name': vals.get('father'),
                'is_parent': True
            })
            application = request.env['education.application'].sudo().create({
                'name': vals.get('first_name'),
                'last_name': vals.get('last_name'),
                'mother_name': vals.get('mother'),
                'father_name': vals.get('father'),
                'mobile': vals.get('phone'),
                'email': vals.get('email'),
                'date_of_birth': vals.get('date'),
                'academic_year_id': vals.get('academic_year'),
                'mother_tongue': vals.get('tongue'),
                'medium': vals.get('medium'),
                'sec_lang': vals.get('sec_lang'),
                'admission_class': vals.get('classes'),
                'street': vals.get('communication_address'),
                'per_street': vals.get('communication_address'),
                'guardian_name': guardian.id,
                'image': base64.b64encode((vals.get('image')).read())
            })
            doc_attachment = request.env['ir.attachment'].sudo().create({
                'name': vals.get('doc').filename,
                'res_name': 'Document',
                'type': 'binary',
                'datas': base64.encodebytes((vals.get('doc')).read()),
            })
            request.env['education.documents'].create({
                'document_name': vals.get('doc_type'),
                'doc_attachment_id': doc_attachment,
                'application_ref': application.id
            })
        return request.render("education_student_portal.submit_admission", {})
