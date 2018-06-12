# -*- coding: utf-8 -*-
###################################################################################
#    A part of Educational ERP Project <https://www.educationalerp.com>
#
#    Cybrosys Technologies Pvt. Ltd.
#    Copyright (C) 2018-TODAY Cybrosys Technologies (<https://www.cybrosys.com>).
#    Author: Nikhil krishnan (nikhil@cybrosys.in)
#            Niyas Raphy (niyas@cybrosys.in)
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

from odoo import fields, models


class EducationInstitute(models.Model):
    _inherit = 'res.company'

    affiliation = fields.Char(string='Affiliation')
    register_num = fields.Char(string='Register')

    base_class = fields.Many2one('education.class', string="Lower class")
    higher_class = fields.Many2one('education.class', string="Higher class")


class EducationInstitutes(models.Model):
    _name = 'education.institute'
    _description = "Educational Institutions"

    name = fields.Char(string="School name", required=True)
    affiliation = fields.Char(string='Affiliation')
    register_num = fields.Char(string='Register Number')
    base_class = fields.Many2one('education.class', string="Lower class")
    higher_class = fields.Many2one('education.class', string="Higher class")
    description = fields.Text(string='Description', help="Description about the Other Institute")

    _sql_constraints = [
        ('register_num', 'unique(register_num)', "Another Institute already exists with this code!"),
    ]


class EducationResPartner(models.Model):
    _inherit = 'res.partner'

    is_student = fields.Boolean(string="Is a Student")
    is_parent = fields.Boolean(string="Is a Parent")


class ReligionReligion(models.Model):
    _name = "religion.religion"
    _description = "Religion"

    name = fields.Char(string="Religion", required=True)


class Religion(models.Model):
    _name = 'religion.caste'
    _description = "Caste"

    name = fields.Char(string="Caste", required=True)
