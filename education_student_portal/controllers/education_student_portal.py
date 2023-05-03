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
from odoo import http
from odoo.http import request, route
from odoo.addons.portal.controllers.portal import CustomerPortal


class StudentPortal(CustomerPortal):
    """Controller for creating a new portal design for student users"""

    @http.route(['/home'], type='http', auth="user", website=True)
    def student_portal(self):
        """New portal for student users"""
        partner = request.env.user.partner_id
        values = request.env['education.student'].sudo().search(
            [('partner_id', '=', partner.id)])
        full_name = values.name
        if values.middle_name:
            full_name = full_name + ' ' + values.middle_name
        if values.last_name:
            full_name = full_name + ' ' + values.last_name
        if values.gender == 'female':
            gender = 'Female'
        elif values.gender == 'male':
            gender = 'Male'
        else:
            gender = 'Other'
        vals = {
            'full_name': full_name,
            'student': values,
            'gender': gender,
        }
        return request.render("education_student_portal.student_portal",
                              {'values': vals})

    @route(['/my', '/my/home'], type='http', auth="user", website=True)
    def home(self, **kw):
        """ Overrided If the logged in user is a student,
                           they will be directed to the student portal."""
        values = self._prepare_portal_layout_values()
        if not request.env.user.partner_id.is_student:
            return request.render("portal.portal_my_home", values)
        else:
            return request.redirect('/home')
