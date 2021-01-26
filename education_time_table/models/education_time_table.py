# -*- coding: utf-8 -*-
################################################################################
#    A part of Educational ERP Project <https://www.educationalerp.com>
#
#    Cybrosys Technologies Pvt. Ltd.
#    Copyright (C) 2020-TODAY Cybrosys Technologies (<https://www.cybrosys.com>)
#    Author: Hajaj Roshan(hajaj@cybrosys.in)
#
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
###############################################################################

from odoo import models, fields, api


class EducationTimeTable(models.Model):
    _name = 'education.timetable'
    _description = 'Timetable'
    _inherit = ['mail.thread', 'mail.activity.mixin']

    active = fields.Boolean('Active', default=True)
    name = fields.Char(compute='get_name')
    class_division = fields.Many2one('education.class.division',
                                     string='Class',
                                     required=True)
    class_name = fields.Many2one('education.class', string="Standard")
    division_name = fields.Many2one('education.division', string='Division')
    academic_year = fields.Many2one('education.academic.year',
                                    string='Academic Year', readonly=True)
    timetable_mon = fields.One2many('education.timetable.schedule',
                                    'timetable_id',
                                    domain=[('week_day', '=', '0')])
    timetable_tue = fields.One2many('education.timetable.schedule',
                                    'timetable_id',
                                    domain=[('week_day', '=', '1')])
    timetable_wed = fields.One2many('education.timetable.schedule',
                                    'timetable_id',
                                    domain=[('week_day', '=', '2')])
    timetable_thur = fields.One2many('education.timetable.schedule',
                                     'timetable_id',
                                     domain=[('week_day', '=', '3')])
    timetable_fri = fields.One2many('education.timetable.schedule',
                                    'timetable_id',
                                    domain=[('week_day', '=', '4')])
    timetable_sat = fields.One2many('education.timetable.schedule',
                                    'timetable_id',
                                    domain=[('week_day', '=', '5')])
    timetable_sun = fields.One2many('education.timetable.schedule',
                                    'timetable_id',
                                    domain=[('week_day', '=', '6')])
    company_id = fields.Many2one(
        'res.company', string='Company',
        default=lambda self: self.env['res.company']._company_default_get())

    def get_name(self):
        """generate name for the model"""
        for rec in self:
            rec.name = False
            if rec.class_division and rec.academic_year:
                rec.name = "/".join([rec.class_division.class_id.name,
                                     rec.class_division.name,
                                     rec.academic_year.name])

    @api.onchange('class_division')
    @api.constrains('class_division')
    def onchange_class_division(self):
        """get class and division details from Class Division model"""
        for rec in self:
            rec.class_name = rec.class_division.class_id
            rec.division_name = rec.class_division.division_id
            rec.academic_year = rec.class_division.academic_year_id


class EducationTimeTableSchedule(models.Model):
    _name = 'education.timetable.schedule'
    _description = 'Timetable Schedule'
    _rec_name = 'period_id'

    period_id = fields.Many2one('timetable.period', string="Period",
                                required=True, )
    time_from = fields.Float(string='From', required=True,
                             index=True, help="Start and End time of Period.")
    time_till = fields.Float(string='Till', required=True)
    subject = fields.Many2one('education.subject', string='Subjects',
                              required=True)
    faculty_id = fields.Many2one('education.faculty', string='Faculty',
                                 required=True)
    week_day = fields.Selection([
        ('0', 'Monday'),
        ('1', 'Tuesday'),
        ('2', 'Wednesday'),
        ('3', 'Thursday'),
        ('4', 'Friday'),
        ('5', 'Saturday'),
        ('6', 'Sunday'),
    ], 'Week', required=True)
    timetable_id = fields.Many2one('education.timetable', required=True, )
    class_division = fields.Many2one('education.class.division', string='Class',
                                     readonly=True)
    company_id = fields.Many2one(
        'res.company', string='Company',
        default=lambda self: self.env['res.company']._company_default_get())

    @api.model
    def create(self, vals):
        """Automatically stores division details fetched from timetable"""
        res = super(EducationTimeTableSchedule, self).create(vals)
        res.class_division = res.timetable_id.class_division.id
        return res

    @api.onchange('period_id')
    def onchange_period_id(self):
        """Gets the start and end time of the period"""
        for i in self:
            i.time_from = i.period_id.time_from
            i.time_till = i.period_id.time_to


class TimetablePeriod(models.Model):
    _name = 'timetable.period'
    _description = 'Timetable Period'

    name = fields.Char(string="Name", required=True, )
    time_from = fields.Float(string='From', required=True,
                             index=True, help="Start and End time of Period.")
    time_to = fields.Float(string='To', required=True)
    company_id = fields.Many2one(
        'res.company', string='Company',
        default=lambda self: self.env['res.company']._company_default_get())
