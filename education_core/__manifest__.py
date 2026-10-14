# -*- coding: utf-8 -*-
###############################################################################
#
#    Cybrosys Technologies Pvt. Ltd.
#
#    Copyright (C) 2026-TODAY Cybrosys Technologies(
#    <https://www.cybrosys.com>).
#    Author: Cybrosys Techno Solutions(<https://www.cybrosys.com>)
#
#    This program is under the terms of the Odoo Proprietary License v1.0 (
#    OPL-1)
#    It is forbidden to publish, distribute, sublicense, or sell copies of the
#    Software or modified copies of the Software.
#
#    THE SOFTWARE IS PROVIDED “AS IS”, WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
#    IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
#    FITNESS FOR A PARTICULAR PURPOSE AND NON INFRINGEMENT. IN NO EVENT SHALL
#    THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM,DAMAGES OR OTHER
#    LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE,ARISING
#    FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER
#    DEALINGS IN THE SOFTWARE.
#
###############################################################################
{
    "name": "Education ERP — Core",
    "version": "19.0.1.0.0",
    "category": "Education",
    "summary": "Student management, enrollment, attendance, timetable, "
               "programs, classes",
    "description": """
Education ERP — Core
====================

Sprint 1: Departments, Academic Years, Programs, Classes, Timetable.
Sprint 2: Student Applications, Enrollment, Documents, Portal Accounts, 
Email Templates.
Sprint 3: Timetable Slots, Attendance (per-period), Leave Requests, 
75% Threshold Cron,
          PDF Attendance Report, Faculty Module.
Sprint 4: Classroom / Exam Hall management (education.classroom).
Reporting menu: Attendance Summary Report and Attendance Analysis
          (list / pivot / graph).

Part of the Educational ERP — LMS System built on Odoo 19 Community Edition
by Cybrosys Techno Solutions.

Version: 19.0.1.0.0  |  License: OPL-1
    """,
    "author": "Cybrosys Techno Solutions",
    "company": "Cybrosys Techno Solutions",
    "maintainer": "Cybrosys Techno Solutions",
    "website": "https://www.cybrosys.com",
    "license": "OPL-1",
    "live_test_url": "https://education-erp-v19.easyinstance.com/web/login?redirect=%2Fodoo%3F",
    "depends": [
        "base",
        "web",
        "account",
        "hr",
        "mail",
        "phone_validation",
        "portal",
    ],
    "external_dependencies": {
        "python": ["phonenumbers"],
        "apt": {
            "phonenumbers": "python3-phonenumbers",
        },
    },
    "data": [
        # Security
        "security/education_security_groups.xml",
        "security/ir.model.access.csv",
        "security/record_rules.xml",
        # Master & Config Data
        "data/ir_sequence.xml",
        "data/education_core_data.xml",
        "data/mail_templates.xml",
        "data/ir_cron.xml",
        # Views
        "views/education_department_views.xml",
        "views/education_academic_year_views.xml",
        "views/education_program_views.xml",
        "views/education_class_views.xml",
        "views/education_subject_views.xml",
        "views/education_classroom_views.xml",
        "views/education_timetable_views.xml",
        "views/education_timetable_slot_views.xml",
        "views/education_document_type_views.xml",
        "views/education_application_views.xml",
        "views/education_enrollment_views.xml",
        "views/education_attendance_views.xml",
        "views/education_attendance_report_views.xml",
        "views/education_leave_request_views.xml",
        "views/account_move_views.xml",
        "views/hr_employee_views.xml",
        "views/res_company_views.xml",
        "views/portal_templates.xml",
        "views/dashboard_actions.xml",
        "views/education_analytics_views.xml",
        # Wizards
        "wizard/education_attendance_summary_views.xml",
        "wizard/education_application_approve_views.xml",
        "wizard/education_application_reject_views.xml",
        "wizard/education_portal_password_views.xml",
        "wizard/education_timetable_generate_views.xml",
        # Reports
        "report/application_report.xml",
        "report/attendance_report.xml",
        "report/faculty_report.xml",
        "report/timetable_report.xml",
        # Menus
        "views/menus.xml",
    ],
    "demo": [
        "demo/education_core_demo.xml",
    ],
    "assets": {
        "web.assets_frontend": [
            "education_core/static/src/scss/portal.scss",
        ],
        "web.assets_backend": [
            "education_core/static/src/js/restricted_menu_dialog.js",
            "education_core/static/src/xml/restricted_menu_dialog.xml",
            "education_core/static/src/scss/dashboard.scss",
            # Shared base class + reusable components (load first)
            "education_core/static/src/js/dashboard_common.js",
            "education_core/static/src/js/dashboard_components.js",
            "education_core/static/src/xml/dashboard_components.xml",
            # Admin dashboard
            "education_core/static/src/js/admin_dashboard.js",
            "education_core/static/src/xml/admin_dashboard.xml",
            # Faculty dashboard (admin view + faculty view)
            "education_core/static/src/js/faculty_dashboard.js",
            "education_core/static/src/xml/faculty_dashboard.xml",

        ],
    },
    "images": ["static/description/banner.jpg"],
    "pre_init_hook": "pre_init_hook",
    "post_init_hook": "post_init_hook",
    "installable": True,
    "application": True,
    "auto_install": False,
    "sequence": 1,
}
