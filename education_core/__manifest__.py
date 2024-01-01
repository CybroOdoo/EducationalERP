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
{
    'name': 'Educational ERP Core',
    'version': '17.0.1.0.0',
    'category': 'Industries',
    'summary': """Core Module of Educational ERP""",
    'description': """A strong and complete user-friendly ERP solution designed 
     specifically for school administration is Educational ERP. 
     Details such as student entrance, enrollment information, faculty records, 
     class management, and subject administration are simple to administer.""",
    'author': 'Cybrosys Techno Solutions',
    'company': 'Cybrosys Techno Solutions',
    'website': "https://www.educationalerp.com",
    'depends': ['stock', 'hr_recruitment', 'education_theme'],
    'data': [
        'security/education_security.xml',
        'security/ir.model.access.csv',
        'data/ir_sequence_data.xml',
        'wizard/application_reject_views.xml',
        'views/education_main_menu.xml',
        'views/res_partner_views.xml',
        'views/education_academic_year_views.xml',
        'views/education_application_views.xml',
        'views/education_class_views.xml',
        'views/education_class_division_views.xml',
        'views/education_student_views.xml',
        'views/education_faculty_views.xml',
        'views/education_document_views.xml',
        'views/document_document_views.xml',
        'views/education_division_views.xml',
        'views/education_subject_views.xml',
        'views/education_syllabus_views.xml',
        'views/education_amenities_views.xml',
        'views/res_company_views.xml',
        'views/hr_applicant_views.xml',
        'views/application_reject_reason_views.xml',
        'report/student_id_card_reports.xml',
        'report/student_application_reports.xml',
        'report/faculty_id_card_reports.xml',
    ],
    'images': ['static/description/banner.jpg'],
    'license': 'AGPL-3',
    'installable': True,
    'auto_install': False,
    'application': True,
}
