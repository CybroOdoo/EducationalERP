# -*- coding: utf-8 -*-
##############################################################################
#    A part of Educational ERP Project <https://www.educationalerp.com>

#    Cybrosys Technologies Pvt. Ltd.
#
#    Copyright (C) 2024-TODAY Cybrosys Technologies(<https://www.cybrosys.com>)
#    Author: Subina P (odoo@cybrosys.com)
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
from odoo import api, fields, models


class EducationTimeTableSchedule(models.Model):
    """Model representing the Timetable Schedule for specific periods."""
    _name = 'education.timetable.schedule'
    _description = 'Timetable Schedule'
    _rec_name = 'period_id'

    period_id = fields.Many2one('timetable.period', string="Period",
                                required=True, help="Select the period for the "
                                                    "timetable schedule.")
    time_from = fields.Float(string='From', required=True,
                             index=True, help="Start time of Period.")
    time_till = fields.Float(string='Till', required=True,
                             help="End time of Period.")
    subject_id = fields.Many2one('education.subject',
                                 string='Subjects',
                                 required=True,
                                 help="Subject associated with the schedule")
    faculty_id = fields.Many2one('education.faculty',
                                 string='Faculty',
                                 required=True, help="Faculty assigned with "
                                                     "the schedule")
    week_day = fields.Selection([
        ('0', 'Monday'),
        ('1', 'Tuesday'),
        ('2', 'Wednesday'),
        ('3', 'Thursday'),
        ('4', 'Friday'),
        ('5', 'Saturday'),
        ('6', 'Sunday'),
    ], 'Week', required=True,  help="Day of the week for the schedule.")
    timetable_id = fields.Many2one('education.timetable',
                                   required=True, help="Timetable associated "
                                                       "with the schedule.")
    class_division_id = fields.Many2one('education.class.division',
                                        string='Class', readonly=True,
                                        help="Class division associated with"
                                             "the timetable schedule.")
    company_id = fields.Many2one(
        'res.company', string='Company',
        default=lambda self: self.env['res.company']._company_default_get(),
        help="Company associated with timetable schedule")

    @api.model
    def create(self, vals):
        """Automatically stores division details fetched from timetable"""
        res = super(EducationTimeTableSchedule, self).create(vals)
        res.class_division_id = res.timetable_id.class_division_id.id
        return res

    @api.onchange('period_id')
    def _onchange_period_id(self):
        """Gets the start and end time of the period"""
        for period in self:
            period.time_from = period.period_id.time_from
            period.time_till = period.period_id.time_to
