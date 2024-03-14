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


class EducationTimeTable(models.Model):
    """Model representing the Timetable for classes."""
    _name = 'education.timetable'
    _description = 'Timetable'
    _inherit = ['mail.thread', 'mail.activity.mixin']

    active = fields.Boolean('Active', default=True,
                            help="Set to False to deactivate the timetable.")
    name = fields.Char(compute='_compute_get_name',
                       help="Generated name based on class, division, "
                            "and academic year.")
    class_division_id = fields.Many2one('education.class.division',
                                        string='Class', required=True,
                                        help="Select the class and division for"
                                             "the timetable."
                                        )
    class_name_id = fields.Many2one('education.class',
                                    string="Standard",
                                    help="Standard associated with the "
                                         "timetable.")
    division_name_id = fields.Many2one('education.division',
                                       string='Division', help="Division of "
                                                               "the class")
    academic_year_id = fields.Many2one('education.academic.year',
                                       string='Academic Year', readonly=True,
                                       help="Academic year of the class")
    timetable_mon_ids = fields.One2many('education.timetable.schedule',
                                        'timetable_id',
                                        domain=[('week_day', '=', '0')],
                                        help="Timetable schedules for Monday.")
    timetable_tue_ids = fields.One2many('education.timetable.schedule',
                                        'timetable_id',
                                        domain=[('week_day', '=', '1')],
                                        help="Timetable schedules for Tuesday.")
    timetable_wed_ids = fields.One2many('education.timetable.schedule',
                                        'timetable_id',
                                        domain=[('week_day', '=', '2')],
                                        help="Timetable schedules for "
                                             "Wednesday.")
    timetable_thur_ids = fields.One2many('education.timetable.schedule',
                                         'timetable_id',
                                         domain=[('week_day', '=', '3')],
                                         help="Timetable schedules for "
                                              "Thursday.")
    timetable_fri_ids = fields.One2many('education.timetable.schedule',
                                        'timetable_id',
                                        domain=[('week_day', '=', '4')],
                                        help="Timetable schedules for Friday.")
    timetable_sat_ids = fields.One2many('education.timetable.schedule',
                                        'timetable_id',
                                        domain=[('week_day', '=', '5')],
                                        help="Timetable schedules for "
                                             "Saturday.")
    timetable_sun_ids = fields.One2many('education.timetable.schedule',
                                        'timetable_id',
                                        domain=[('week_day', '=', '6')],
                                        help="Timetable schedules for Sunday.")
    company_id = fields.Many2one(
        'res.company', string='Company',
        default=lambda self: self.env['res.company']._company_default_get(),
        help="Company associated with the timetable.")

    def _compute_get_name(self):
        """Generate name for the model"""
        for rec in self:
            rec.name = False
            if rec.class_division_id and rec.academic_year_id:
                rec.name = "/".join([rec.class_division_id.class_id.name,
                                     rec.class_division_id.name,
                                     rec.academic_year_id.name])

    @api.onchange('class_division_id')
    @api.constrains('class_division_id')
    def _onchange_class_division_id(self):
        """Get class and division details from Class Division model"""
        for rec in self:
            rec.class_name_id = rec.class_division_id.class_id
            rec.division_name_id = rec.class_division_id.division_id
            rec.academic_year_id = rec.class_division_id.academic_year_id
