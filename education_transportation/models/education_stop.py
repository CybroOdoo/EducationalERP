# -*- coding: utf-8 -*-
from odoo import fields, models


class EducationStop(models.Model):
    _name = 'education.stop'
    _rec_name = "stop_name"
    _order = 'stop_sequence'
    _description = "Stage"

    stop_name = fields.Many2one('edu.stop', string="Stage Name", required=True)
    stop_sequence = fields.Integer(string='Sequence')
    cost = fields.Float(string="Cost")
    company_id = fields.Many2one('res.company', string='Company',
                                 default=lambda s: s.env['res.company']._company_default_get('ir.sequence'))


class EduStop(models.Model):
    _name = 'edu.stop'
    _rec_name = "name"
    _description = "Stage"

    name = fields.Char(string="Name", required=True)


class EducationTripStop(models.Model):
    _name = 'education.trip_stop'
    _rec_name = "stop_name"
    _order = 'stop_sequence'

    stop_name = fields.Many2one('education.stop', string="Name", required=True)
    stop_sequence = fields.Integer(string='Sequence', related='stop_name.stop_sequence')
    cost = fields.Float(string="Cost", related='stop_name.cost')
    stop_trip_rel = fields.Many2one('education.trip', string="Trip")
    morning_timing = fields.Float(string="Duration from Source")
    evening_timing = fields.Float(string="Duration from Destination")
