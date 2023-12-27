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
{
    'name': 'Educational ERP Theme',
    'version': '17.0.1.0.0',
    "category": "Theme/Backend",
    'summary': """Attractive and unique red-teal combination of backend-end 
     theme for Education ERP""",
    'description': """In trio combination of red, teal and white Educational 
     ERP opens the new gate way for management""",
    'author': 'Cybrosys Techno Solutions',
    'company': 'Cybrosys Techno Solutions',
    'maintainer': 'Cybrosys Techno Solutions',
    'website': "https://www.educationalerp.com",
    'depends': ['base'],
    'data': [
        'data/logo_data.xml',
        'views/shortcut_icon_templates.xml',
    ],
    'assets': {
        'web.assets_backend': [
            'education_theme/static/src/scss/education_backend.scss',
            'education_theme/static/src/js/sidebar_menu.js',
            'education_theme/static/src/xml/sidebar.xml'
        ],
    },
    'images': [
        'static/description/banner.jpg',
        'static/description/theme_screenshot.jpg',
    ],
    'license': 'AGPL-3',
    'installable': True,
    'auto_install': False,
    'application': False,
}
