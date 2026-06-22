# -*- coding: utf-8 -*-
################################################################################
#
#    Cybrosys Technologies Pvt. Ltd.
#
#    Copyright (C) 2026-TODAY Cybrosys Technologies(<https://www.cybrosys.com>).
#    Author: Cybrosys Technologies (odoo@cybrosys.com)
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
################################################################################
"""This module defines the education application class."""

from odoo import fields, models


class EducationApplication(models.Model):
    """Inherited model 'education.application'"""
    _inherit = 'education.application'

    need_hostel = fields.Boolean(string='Need Hostel Facility',
                                 help='True if need a hostel facility')

    def create_student(self):
        """Creating hostel admission from the student application form"""
        for rec in self:
            res = super().create_student()
            if rec.need_hostel:
                std = self.env['education.student'].search(
                    [('application_id', '=', rec.id)])
                if std:
                    std.need_hostel = True
                    values = {
                        'student_id': std.id,
                        'father_name': std.father_name,
                        'mother_name': std.mother_name,
                        'guardian_name': std.guardian_name.name,
                        'street': std.per_street,
                        'street2': std.per_street2,
                        'city': std.per_city,
                        'state_id': std.per_state_id,
                        'country_id': std.per_country_id,
                        'zip': std.per_zip,
                        'date_of_birth': std.date_of_birth,
                        'blood_group': std.blood_group,
                        'email': std.email,
                        'mobile': std.mobile,
                        'phone': std.phone,
                        'image': std.image_1920,
                        'gender': std.gender,
                    }
                    self.env['education.hostel.member'].create(values)
            return res
