# -*- coding: utf-8 -*-
#############################################################################
#
#    Cybrosys Technologies Pvt. Ltd.
#
#    Copyright (C) 2026-TODAY Cybrosys Technologies (<https://www.cybrosys.com>).
#    Author: Cybrosys Techno Solutions (<https://www.cybrosys.com>)
#
#    This program is free software: you can modify it under the terms of the
#    GNU AFFERO GENERAL PUBLIC LICENSE (AGPL v3), Version 3.
#
#    This program is distributed in the hope that it will be useful, but
#    WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
#    GNU AFFERO GENERAL PUBLIC LICENSE (AGPL v3) for more details.
#
#    You should have received a copy of the GNU AFFERO GENERAL PUBLIC LICENSE
#    (AGPL v3) along with this program.
#    If not, see <http://www.gnu.org/licenses/>.
#
#############################################################################

from odoo.tests import TransactionCase
from odoo.exceptions import ValidationError
import datetime

class TestHostelLeave(TransactionCase):

    def setUp(self):
        super(TestHostelLeave, self).setUp()
        
        # Create a faculty for member
        self.faculty = self.env['education.faculty'].create({
            'name': 'Faculty',
            'last_name': 'Member',
            'gender': 'male',
        })
        
        # Create a hostel member
        self.member = self.env['education.hostel.member'].create({
            'member_type': 'is_faculty',
            'faculty_id': self.faculty.id,
        })
        
        self.today = datetime.datetime.now()
        self.tomorrow = self.today + datetime.timedelta(days=1)
        self.yesterday = self.today - datetime.timedelta(days=1)

    def test_leave_creation_and_days_computation(self):
        """Test leave creation, sequence, and days computation."""
        leave = self.env['education.hostel_leave'].create({
            'name': self.member.id,
            'leave_from': self.today,
            'leave_to': self.tomorrow,
            'reason': 'Personal reason',
        })
        
        self.assertTrue(leave.id)
        self.assertNotEqual(leave.request, 'New')
        self.assertEqual(leave.state, 'draft')
        
        # Number of days should be 1 (since it's exactly 24 hours difference in datetime)
        self.assertGreater(leave.number_of_days, 0)

    def test_leave_date_validation(self):
        """Test from and to date validation."""
        with self.assertRaises(ValidationError):
            self.env['education.hostel_leave'].create({
                'name': self.member.id,
                'leave_from': self.today,
                'leave_to': self.yesterday,
                'reason': 'Invalid dates',
            })

    def test_leave_workflow(self):
        """Test leave workflow states."""
        leave = self.env['education.hostel_leave'].create({
            'name': self.member.id,
            'leave_from': self.today,
            'leave_to': self.tomorrow,
            'reason': 'Sick leave',
        })
        
        # Draft -> Confirm
        leave.action_confirm()
        self.assertEqual(leave.state, 'confirm')
        
        # Confirm -> Validate
        leave.action_validate()
        self.assertEqual(leave.state, 'validate')
        
        # Test Refuse
        leave2 = self.env['education.hostel_leave'].create({
            'name': self.member.id,
            'leave_from': self.today,
            'leave_to': self.tomorrow,
            'reason': 'Sick leave',
        })
        leave2.action_confirm()
        leave2.action_refuse()
        # Refuse sets state to 'cancel'
        self.assertEqual(leave2.state, 'cancel')
