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

from unittest.mock import patch, MagicMock
from odoo.tests.common import TransactionCase, tagged
from odoo import fields

@tagged('post_install', '-at_install')
class TestErpDashboard(TransactionCase):

    def setUp(self):
        super(TestErpDashboard, self).setUp()
        self.dashboard = self.env['erp.dashboard']

    @patch('odoo.models.BaseModel.search')
    def test_erp_data(self, mock_search):
        """Test getting overall module counts."""
        mock_recordset = MagicMock()
        mock_recordset.__len__.return_value = 5
        mock_search.return_value = mock_recordset

        data = self.dashboard.erp_data()

        self.assertEqual(data['applications'], 5)
        self.assertEqual(data['students'], 5)
        self.assertEqual(data['faculties'], 5)
        self.assertEqual(data['amenities'], 5)
        self.assertEqual(data['exams'], 5)
        self.assertEqual(data['promotions'], 5)
        self.assertEqual(data['timetable'], 5)
        self.assertEqual(data['attendance'], 5)

    def test_get_all_applications(self):
        """Test getting applications by academic year."""
        mock_year = MagicMock()
        mock_year.name = '2023-2024'
        
        mock_recordset = MagicMock()
        mock_recordset.mapped.return_value = [mock_year]
        
        with patch('odoo.models.BaseModel.search', return_value=mock_recordset), \
             patch('odoo.models.BaseModel.search_count', return_value=10):
            data = self.dashboard.get_all_applications()
            self.assertEqual(data, {'2023-2024': 10})

    def test_get_rejected_accepted_applications(self):
        """Test getting rejected vs accepted counts."""
        mock_year1 = MagicMock()
        mock_year1.name = '2022-2023'
        from datetime import timedelta
        mock_year1.ay_end_date = fields.Date.today() - timedelta(days=365)
        
        mock_year2 = MagicMock()
        mock_year2.name = '2023-2024'
        mock_year2.ay_end_date = fields.Date.today()
        
        mock_academic_years = [mock_year1, mock_year2]
        
        with patch('odoo.models.BaseModel.search', return_value=mock_academic_years), \
             patch('odoo.models.BaseModel.search_count', side_effect=[2, 8]): # reject, done
            data = self.dashboard.get_rejected_accepted_applications()
            self.assertEqual(data, {'Done': 8, 'Reject': 2})

    @patch('odoo.models.BaseModel.search_count')
    def test_get_exam_result(self, mock_search_count):
        """Test pass/fail exam counts."""
        mock_search_count.side_effect = [15, 5] # pass, fail
        data = self.dashboard.get_exam_result()
        self.assertEqual(data, {'Pass': 15, 'Fail': 5})

    @patch('odoo.models.BaseModel.search_count')
    def test_get_attendance(self, mock_search_count):
        """Test overall attendance presents vs absents."""
        mock_search_count.side_effect = [10, 100] # absents, total
        data = self.dashboard.get_attendance()
        self.assertEqual(data, {'Presents': 90, 'Absents': 10})

    def test_get_student_strength(self):
        """Test student strength count per class."""
        mock_class = MagicMock()
        mock_class.id = 1
        mock_class.name = 'Class 1A'
        
        with patch('odoo.models.BaseModel.search', return_value=[mock_class]), \
             patch('odoo.models.BaseModel.search_count', return_value=30):
            data = self.dashboard.get_student_strength()
            self.assertEqual(data, {'Class 1A': 30})

    def test_get_average_marks(self):
        """Test calculating average marks per class."""
        mock_class = MagicMock()
        mock_class.id = 1
        mock_class.name = 'Class 1A'
        
        mock_student1 = MagicMock()
        mock_student1.id = 1
        mock_student2 = MagicMock()
        mock_student2.id = 2
        
        mock_results1 = MagicMock()
        mock_results1.mapped.return_value = [80]
        mock_results2 = MagicMock()
        mock_results2.mapped.return_value = [90]
        
        def mock_search_side_effect(domain=None, *args, **kwargs):
            if not domain:
                return [mock_class]
            domain_str = str(domain)
            if 'class_division_id' in domain_str:
                return [mock_student1, mock_student2]
            if 'student_id' in domain_str and '1' in domain_str:
                return mock_results1
            if 'student_id' in domain_str and '2' in domain_str:
                return mock_results2
            return []
            
        with patch('odoo.models.BaseModel.search', side_effect=mock_search_side_effect):
            data = self.dashboard.get_average_marks()
            self.assertEqual(data, {'Class 1A': 85.0})

    def test_get_academic_year(self):
        """Test fetching the academic years."""
        mock_year = MagicMock()
        mock_year.id = 1
        mock_year.name = '2023-2024'
        with patch('odoo.models.BaseModel.search', return_value=[mock_year]):
            data = self.dashboard.get_academic_year()
            self.assertEqual(data, {1: '2023-2024'})

    @patch('odoo.models.BaseModel.search_count')
    def test_get_academic_year_exam_result(self, mock_search_count):
        """Test exam results filtered by academic year."""
        mock_search_count.side_effect = [20, 5]
        data = self.dashboard.get_academic_year_exam_result(1)
        self.assertEqual(data, {'Pass': 20, 'Fail': 5})

    def test_get_classes(self):
        """Test fetching classes."""
        mock_class = MagicMock()
        mock_class.id = 1
        mock_class.name = 'Class 1A'
        with patch('odoo.models.BaseModel.search', return_value=[mock_class]):
            data = self.dashboard.get_classes()
            self.assertEqual(data, {1: 'Class 1A'})

    @patch('odoo.models.BaseModel.search_count')
    def test_get_class_attendance_today(self, mock_search_count):
        """Test calculating attendance counts per class."""
        mock_search_count.side_effect = [5, 40] # absents, total
        data = self.dashboard.get_class_attendance_today(1)
        self.assertEqual(data, {'Presents': 35, 'Absents': 5})
