# -*- coding: utf-8 -*-
###################################################################################
#    A part of Educational ERP Project <https://www.educationalerp.com>
#
#    Cybrosys Technologies Pvt. Ltd.
#    Copyright (C) 2018-TODAY Cybrosys Technologies (<https://www.cybrosys.com>).
#    Author: Nikhil krishnan (nikhil@cybrosys.in)
#            Niyas Raphy (niyas@cybrosys.in)
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
    'name': 'Educational ERP Core',
    'version': '11.0.1.0.1',
    'summary': """Core Module of Educational ERP""",
    'description': 'Core Module of Educational ERP',
    'category': 'Educational',
    'author': 'Cybrosys Techno Solutions',
    'company': 'Cybrosys Techno Solutions',
    'website': "http://www.educationalerp.com",
    'depends': ['base', 'mail', 'stock', 'education_theme', 'hr_recruitment'],
    'data': [
        'security/education_security.xml',
        'security/ir.model.access.csv',
        'views/education_main_menu.xml',
        'views/education_res_partner.xml',
        'views/education_application_reject.xml',
        'views/education_academic_year.xml',
        'views/application_reject_reason.xml',
        'views/education_recruitment.xml',
        'views/education_class_wizard.xml',
        'views/education_admission.xml',
        'views/education_class.xml',
        'views/education_class_division.xml',
        'views/education_student.xml',
        'views/education_student_class.xml',
        'views/education_faculty.xml',
        'views/education_documents.xml',
        'views/education_document_type.xml',
        'views/sequence.xml',
        'views/education_res_company.xml',
        'views/education_division.xml',
        'views/education_subject.xml',
        'views/education_syllabus.xml',
        'views/education_amenities.xml',
        'views/application_analysis.xml',
        'reports/report.xml',
        'reports/student_id_card.xml',
        'reports/student_application_report.xml',
        'reports/faculty_id_card.xml',
    ],
    'demo': [
        'demo/education_data.xml',
    ],
    'images': ['static/description/banner.jpg'],
    'license': 'AGPL-3',
    'installable': True,
    'auto_install': False,
    'application': True,
}
