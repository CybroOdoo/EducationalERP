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
"""This module defines the education student class."""

from odoo import fields, models


class EducationStudent(models.Model):
    """Inherited model 'education.student'"""
    _inherit = 'education.student'

    need_hostel = fields.Boolean(string='Need Hostel Facility',
                                 help='True if student need hostel')
    hostel_id = fields.Many2one('education.hostel',
                                string="Hostel", tracking=1,
                                help="Hostel of the student.")
    room_id = fields.Many2one('education.room',
                              string="Room", tracking=1,
                              help="Room of the student.")
    hostel_fee = fields.Char(string="Fee", tracking=1,
                             help="Hostel fee of the student.")
    hostel_member = fields.Many2one('education.hostel.member',
                                    string="Hostel Admission No",
                                    help="Hostel Admission number of student.")
