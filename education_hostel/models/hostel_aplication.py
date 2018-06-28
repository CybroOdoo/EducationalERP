from odoo import fields, models, _, api


class StudentApplicationInherit(models.Model):
    _inherit = 'education.application'

    need_hostel = fields.Boolean(string='Need Hostel Facility', default=False)

    @api.multi
    def create_student(self):
        """creating hostel admission from the student application form"""
        for rec in self:
            res = super(StudentApplicationInherit, rec).create_student()
            if rec.need_hostel:
                std = self.env['education.student'].search([('application_id', '=', rec.id)])
                if std:
                    std.need_hostel = True
                    values = {
                        'member_std_name': std.id,
                        'father_name': std.father_name,
                        'mother_name': std.mother_name,
                        'guardian_name': std.guardian_name.name,
                        'street': std.per_street,
                        'street2': std.per_street2,
                        'city': std.per_city,
                        'state_id': std.per_state_id,
                        'country': std.per_country_id,
                        'zip': std.per_zip,
                        'date_of_birth': std.date_of_birth,
                        'blood_group': std.blood_group,
                        'email': std.email,
                        'mobile': std.mobile,
                        'phone': std.phone,
                        'image': std.image,
                        'gender': std.gender,
                    }
                    self.env['education.host_std'].create(values)
            return res


class StudentInherit(models.Model):
    _inherit = 'education.student'

    need_hostel = fields.Boolean(string='Need Hostel Facility', default=False)
    hostel = fields.Many2one('education.hostel', string="Hostel", track_visibility='onchange')
    room = fields.Many2one('education.room', string="Room", track_visibility='onchange')
    hostel_fee = fields.Char(string="Fee", track_visibility='onchange')
    hostel_member = fields.Many2one('education.host_std', string="Hostel Admission No")
