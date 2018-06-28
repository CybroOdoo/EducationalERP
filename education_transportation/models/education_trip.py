# -*- coding: utf-8 -*-
from odoo import fields, models, api, _
from odoo.exceptions import ValidationError


class EducationFleetInherit(models.Model):
    _inherit = 'fleet.vehicle'

    vehicle_number = fields.Char(string="Vehicle Code", required=True)


class EducationTrip(models.Model):
    _name = 'education.trip'
    _rec_name = "name"
    _description = "Route"
    _inherit = ['mail.thread', 'mail.activity.mixin']

    name = fields.Char(string='Route', size=32, default='New')
    stop = fields.One2many('education.trip_stop', 'stop_trip_rel', string='Stops')
    src_loc = fields.Many2one('education.stop', string='From', required=True)
    dest_loc = fields.Many2one('education.stop', string='To', required=True)
    total_students = fields.Char(string="Total Students", readonly=True, compute="_document_count")
    color = fields.Integer(string='Color Index')
    vehicle = fields.One2many('edu.vehicle', 'trip_rel', string="Vehicle")
    company_id = fields.Many2one('res.company', string='Company',
                                 default=lambda self: self.env['res.company']._company_default_get())
    academic_year_id = fields.Many2one('education.academic.year', string='Academic Year')

    @api.constrains('src_loc', 'dest_loc')
    def check_locations(self):
        for rec in self:
            if rec.src_loc == rec.dest_loc:
                raise ValidationError(_("Source and Destination Cannot be same Stage"))

    @api.model
    def create(self, vals):
        """Overriding the create method and assigning
                name for the newly creating record"""
        if vals['name'] == 'New':
            src_loc = self.env['education.stop'].browse(vals['src_loc'])
            dest_loc = self.env['education.stop'].browse(vals['dest_loc'])
            vals['name'] = src_loc.stop_name.name + '-->' + dest_loc.stop_name.name
        res = super(EducationTrip, self).create(vals)
        return res

    @api.multi
    def student_view(self):
        self.ensure_one()
        domain = [
            ('trip_id', '=', self.id)]
        return {
            'name': _('Students'),
            'domain': domain,
            'res_model': 'education.student',
            'type': 'ir.actions.act_window',
            'view_id': False,
            'view_mode': 'tree,form',
            'view_type': 'form',
            'context': "{'default_trip_id': '%s'}" % self.id
        }

    @api.multi
    def _document_count(self):
        """Return the count of the students"""
        for rec in self:
            document_ids = self.env['education.student'].search([('trip_id', '=', rec.id)])
            rec.total_students = len(document_ids)


class EducationTrans(models.Model):
    _name = 'edu.vehicle'

    trip_rel = fields.Many2one('education.trip', string="Route")
    vehicle = fields.Many2one('fleet.vehicle', string='Vehicle')
    morning_timing = fields.Float(string="Morning Start Timing")
    evening_timing = fields.Float(string="Evening Start Timing")
    vehicle_no = fields.Char(string="Vehicle Code", related='vehicle.vehicle_number')
    driver = fields.Many2one('res.partner', string="Driver", related='vehicle.driver_id')


class EducationStudentTrans(models.Model):
    _inherit = 'education.student'

    trip_id = fields.Many2one('education.trip', string="Route", track_visibility='onchange')
    location = fields.Many2one('education.stop', string='Location', track_visibility='onchange')
    trans_cost = fields.Float(string="Transportation Fee", related='location.cost', track_visibility='onchange')
    need_transportation_facility = fields.Boolean(string='Need Transportation Facility', default=False)


class StudentTrip(models.Model):
    _inherit = 'education.application'

    need_transportation_facility = fields.Boolean(string='Need Transportation Facility', default=False)

    @api.multi
    def create_student(self):
        for rec in self:
            res = super(StudentTrip, rec).create_student()
            if rec.need_transportation_facility:
                std = self.env['education.student'].search([('application_id', '=', rec.id)])
                if std:
                    std.need_transportation_facility = True
            return res
