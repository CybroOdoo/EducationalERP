# -*- coding: utf-8 -*-
##############################################################################
#
#    Cybrosys Technologies Pvt. Ltd.
#
#    Copyright (C) 2024-TODAY Cybrosys Technologies(<https://www.cybrosys.com>)
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
{
    'name': 'Educational Attendance Management',
    'version': '17.0.1.0.0',
    'category': 'Industries',
    'summary': "Openerp to Student Attendance Management System "
               "for Educational ERP",
    'description': """An easy and efficient management tool to manage and 
     track student attendance. Enables different types of filtration to 
     generate the adequate reports""",
    'author': 'Cybrosys Techno Solutions',
    'company': 'Cybrosys Techno Solutions',
    'maintainer': 'Cybrosys Techno Solutions',
    'website': "http://www.educationalerp.com",
    'depends': ['education_core'],
    'data': [
        'security/ir.model.access.csv',
        'views/education_attendance_line_views.xml',
        'views/education_attendance_views.xml',
        'views/education_class_division_views.xml',
        'views/education_student_views.xml',
    ],
    'assets': {
        'web.assets_backend': [
            '/education_attendances/static/src/css/attendance.css'
        ],
    },
    'images': ['static/description/banner.jpg'],
    'license': 'AGPL-3',
    'installable': True,
    'auto_install': False,
    'application': True,
}
