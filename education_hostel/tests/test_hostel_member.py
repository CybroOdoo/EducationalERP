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

class TestHostelMember(TransactionCase):

    def setUp(self):
        super(TestHostelMember, self).setUp()
        
        # Create a student
        self.student = self.env['education.student'].create({
            'name': 'John',
            'last_name': 'Doe',
            'gender': 'male',
            'need_hostel': True,
        })
        
        # Create a faculty
        self.faculty = self.env['education.faculty'].create({
            'name': 'Dr.',
            'last_name': 'Smith',
            'gender': 'male',
        })
        
        # Create a hostel
        self.hostel = self.env['education.hostel'].create({
            'hostel_name': 'Student Hostel',
            'hostel_code': 'SH01',
            'hostel_floors': '1',
            'hostel_warden_id': self.faculty.id,
            'room_rent': '1000',
            'mess_fee': '500',
            'phone': '1234567890',
            'mobile': '0987654321',
        })
        
        # Create a floor and room
        self.floor = self.env['education.floor'].create({
            'floor_no': 'Ground Floor',
            'hostel_id': self.hostel.id,
        })
        self.room = self.env['education.room'].create({
            'hostel_id': self.hostel.id,
            'room_name': 'Room 101',
            'room_code': 'R101',
            'floor': self.floor.id,
            'room_capacity': '2',
        })

    def test_member_creation_and_name_generation(self):
        """Test member creation from student."""
        member = self.env['education.hostel.member'].create({
            'member_type': 'is_student',
            'student_id': self.student.id,
        })
        
        self.assertTrue(member.id)
        # Assuming name is computed as "name last_name" or "name  last_name"
        self.assertIn('John', member.name)
        self.assertIn('Doe', member.name)

    def test_phone_mobile_validation(self):
        """Test phone format validation."""
        member = self.env['education.hostel.member'].create({
            'member_type': 'is_student',
            'student_id': self.student.id,
        })
        
        with self.assertRaises(ValidationError):
            member.write({'phone': 'invalid_phone'})
            
        with self.assertRaises(ValidationError):
            member.write({'mobile': 'invalid_mobile'})
            
        # Valid format
        member.write({'phone': '+1 (234) 567-890'})
        self.assertEqual(member.phone, '+1 (234) 567-890')

    def test_room_allocation_and_vacation(self):
        """Test member allocation to a room and vacating."""
        member = self.env['education.hostel.member'].create({
            'member_type': 'is_student',
            'student_id': self.student.id,
        })
        
        # Add allocation detail
        allocation = self.env['education.room_member'].create({
            'room_member_id': member.id,
            'room_id': self.room.id,
            'allocated_date': '2023-01-01',
            'student_id': self.student.id,
        })
        
        # Allocate
        member.action_allocate_member()
        self.assertEqual(member.state, 'allocated')
        self.assertEqual(member.room_id.id, self.room.id)
        self.assertEqual(self.student.room_id.id, self.room.id)
        
        # Test vacated date constraints
        with self.assertRaises(ValidationError):
            allocation.write({'vacated_date': '2022-01-01'}) # Before allocated_date
            
        # Set valid vacated date
        allocation.write({'vacated_date': '2023-12-31'})
        
        # Vacate
        member.action_vacate_member()
        self.assertEqual(member.state, 'vacated')
        self.assertFalse(self.student.hostel_id.id)
