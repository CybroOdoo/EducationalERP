# -*- coding: utf-8 -*-
###################################################################################
#    A part of Educational ERP Project <http://www.educationalerp.com>
#
#    Cybrosys Technologies Pvt. Ltd.
#    Copyright (C) 2018-TODAY Cybrosys Technologies (<https://www.cybrosys.com>).
#    Author: Akhilesh N S(<akhilesh@cybrosys.in>)
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

{
    "name": "Educational Fee Management",
    "version": "11.0.1.0.0",
    "author": "Cybrosys Techno Solutions",
    "category": 'Educational',
    "company": "Cybrosys Techno Solutions",
    "website": "http://www.educationalerp.com",
    'summary': 'Manage students fee',
    'description': """Manage students fee""",
    "depends": ['base', 'account', 'account_invoicing', 'education_core'],
    "data": [
        'data/account_data.xml',
        'security/ir.model.access.csv',
        'views/fee_menu_view.xml',
        'views/fee_register.xml',
        'views/fee_structure.xml',
        'views/fee_types.xml',
        'views/fee_category.xml',
        'views/fee_journal_dashboard_view.xml',
        'views/fee_journal_inherit.xml',
    ],
    "demo": [
        # 'demo/fee_data.xml',
    ],
    'images': ['static/description/banner.jpg'],
    'license': 'AGPL-3',
    "installable": True,
    "auto_install": False,
    'application': True,
}
