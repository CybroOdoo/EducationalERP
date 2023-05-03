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
from odoo import fields, models


class StudentApplication(models.Model):
    """Inheriting education application model for
                        creating a new user for student."""
    _inherit = 'education.application'

    email = fields.Char(string="Email", required=True,
                        help="Enter E-mail id for contact purpose")

    def create_student(self, **kw):
        """ Overrided inorder to create a new user for
                        student while creating student """
        res = super(StudentApplication, self).create_student()
        student = self.env['education.student'].browse(res['res_id'])
        user = self.env['res.users'].create({
            'name': student.name,
            'login': student.email,
            'partner_id': student.partner_id.id,
            'groups_id': [(6, 0, [self.env.ref('base.group_portal').id])]
        })
        student.student_user_id = user
        return res
