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

class TestHostelMess(TransactionCase):

    def setUp(self):
        super(TestHostelMess, self).setUp()
        
        # Create a hostel
        self.faculty = self.env['education.faculty'].create({
            'name': 'Warden',
            'last_name': 'Test',
            'gender': 'male',
        })
        
        self.hostel = self.env['education.hostel'].create({
            'hostel_name': 'Mess Hostel',
            'hostel_code': 'MH01',
            'hostel_floors': '1',
            'hostel_warden_id': self.faculty.id,
            'room_rent': '1000',
            'mess_fee': '500',
            'phone': '1234567890',
            'mobile': '0987654321',
        })
        
        # Create food items
        self.food1 = self.env['food.item'].create({'name': 'Pancakes'})
        self.food2 = self.env['food.item'].create({'name': 'Pasta'})

    def test_mess_and_food_creation(self):
        """Test creating a mess and assigning food menus."""
        # Create mess
        mess = self.env['education.mess'].create({
            'mess_name': 'Main Mess',
            'mess_code': 'MM01',
            'hostel_id': self.hostel.id,
        })
        self.assertTrue(mess.id)
        self.assertEqual(mess.mess_name, 'Main Mess')
        
        # Create food menu
        mess_food = self.env['mess.food'].create({
            'mess_id': mess.id,
            'break_fast_id': self.food1.id,
            'lunch_id': self.food2.id,
            'week_list': 'MO',
        })
        
        self.assertTrue(mess_food.id)
        self.assertEqual(mess_food.break_fast_id.id, self.food1.id)
        self.assertIn(mess_food, mess.food_menu_ids)
