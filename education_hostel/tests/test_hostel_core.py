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

class TestHostelCore(TransactionCase):
    
    def setUp(self):
        super(TestHostelCore, self).setUp()
        
        # Create an amenities record (assumed from education_core)
        self.amenity = self.env['education.amenities'].create({
            'name': 'Test Amenity',
        })
        
        # Create a faculty record (assumed from education_core) for warden
        self.faculty = self.env['education.faculty'].create({
            'name': 'Test Warden',
            'last_name': 'Warden Last',
            'gender': 'male',
        })
        
        # Create a hostel
        self.hostel = self.env['education.hostel'].create({
            'hostel_name': 'Test Hostel',
            'hostel_code': 'TH01',
            'hostel_floors': '2',
            'hostel_warden_id': self.faculty.id,
            'room_rent': '1000',
            'mess_fee': '500',
            'phone': '1234567890',
            'mobile': '0987654321',
        })

    def test_hostel_creation_constraints(self):
        """Test the constraints on hostel creation."""
        # Test missing floor
        with self.assertRaises(ValidationError):
            self.env['education.hostel'].create({
                'hostel_name': 'Invalid Hostel 1',
                'hostel_code': 'IH01',
                'hostel_floors': '',
                'hostel_warden_id': self.faculty.id,
                'room_rent': '1000',
                'mess_fee': '500',
                'phone': '1234567890',
                'mobile': '0987654321',
            })
            
        # Test missing phone
        with self.assertRaises(ValidationError):
            self.env['education.hostel'].create({
                'hostel_name': 'Invalid Hostel 2',
                'hostel_code': 'IH02',
                'hostel_floors': '1',
                'hostel_warden_id': self.faculty.id,
                'room_rent': '1000',
                'mess_fee': '500',
                'phone': '',
                'mobile': '0987654321',
            })

    def test_hostel_fee_amount(self):
        """Test the computation of total fee."""
        self.assertEqual(self.hostel.total, '1500.0', "Total fee should be room_rent + mess_fee.")

    def test_floor_creation(self):
        """Test floor creation and floor count validation."""
        floor_1 = self.env['education.floor'].create({
            'floor_no': 'Floor 1',
            'hostel_id': self.hostel.id,
        })
        self.assertTrue(floor_1, "Floor 1 should be created successfully")
        
        floor_2 = self.env['education.floor'].create({
            'floor_no': 'Floor 2',
            'hostel_id': self.hostel.id,
        })
        self.assertTrue(floor_2, "Floor 2 should be created successfully")
        
        # Test exceeding floor count (hostel_floors is '2')
        with self.assertRaises(ValidationError):
            self.env['education.floor'].create({
                'floor_no': 'Floor 3',
                'hostel_id': self.hostel.id,
            })

    def test_room_creation_and_amenity(self):
        """Test room creation and amenity constraints."""
        floor = self.env['education.floor'].create({
            'floor_no': 'Floor 1',
            'hostel_id': self.hostel.id,
        })
        
        room = self.env['education.room'].create({
            'hostel_id': self.hostel.id,
            'room_name': 'Room 101',
            'room_code': 'R101',
            'floor': floor.id,
            'room_capacity': '2',
        })
        
        self.assertTrue(room.id, "Room should be created successfully")
        self.assertEqual(room.vacancy, 2, "Initial vacancy should equal room capacity")
        self.assertEqual(room.allocated_number, 0, "Initial allocated number should be 0")
        
        # Test room list creation on room creation
        room_list = self.env['education.room_list'].search([('room_mem_rel', '=', room.id)])
        self.assertTrue(room_list, "education.room_list record should be created when a room is created.")
        self.assertEqual(room_list.hostel_room_rel2.id, self.hostel.id)
        
        # Test valid amenity quantity
        amenity = self.env['room.amenity'].create({
            'amenity_id': self.amenity.id,
            'qty': 2,
            'amenity_rel_id': room.id,
        })
        self.assertEqual(amenity.qty, 2)
        
        # Test invalid amenity quantity
        with self.assertRaises(ValidationError):
            self.env['room.amenity'].create({
                'amenity_id': self.amenity.id,
                'qty': 0,
                'amenity_rel_id': room.id,
            })
