# -*- coding: utf-8 -*-
from datetime import datetime
from odoo import models, fields, api


class SchoolAnnouncementTable(models.Model):
    _name = 'school.announcement'
    _description = 'School Announcement'

    name = fields.Char(string='Code No:')
    announcement_reason = fields.Text(string='Title', states={'draft': [('readonly', False)]}, required=True,
                                      readonly=True)
    state = fields.Selection([('draft', 'Draft'),
                              ('to_send', 'sent'),
                              ('expired', 'Expired')],
                             string='Status', default='draft',
                             track_visibility='always')
    requested_date = fields.Date(string='Send Date', default=datetime.now().strftime('%Y-%m-%d'))
    is_announcement = fields.Boolean(string='General Announcement?')

    announcement = fields.Html(string='Letter', states={'draft': [('readonly', False)]}, readonly=True)
    attachment_id = fields.Many2many('ir.attachment', 'doc_warning_rel', 'doc_id', 'attach_id4',
                                     string="Attachment", help='You can attach the copy of your Letter')
    expiry_date = fields.Date(string='Expiry Date', required=True)
    to_assign = fields.Selection([('student', 'Student'),
                                  ('staff', 'Staff')],
                                 string='To Email', )

    def expire_date(self):

        anou = self.search([('expiry_date', '=', datetime.now().strftime("%Y-%m-%d")),
                            ('state', '!=', 'expired')])
        if anou.expiry_date == datetime.now().strftime("%Y-%m-%d"):
            anou.state = 'expired'

    @api.multi
    def to_send(self):
        self.state = 'to_send'

    @api.multi
    def undo(self):
        self.state = 'draft'

    @api.model
    def create(self, vals):
        vals['name'] = self.env['ir.sequence'].next_by_code('school.announcement')
        return super(SchoolAnnouncementTable, self).create(vals)

    def mail_send(self):
        if self.to_assign == 'student':
            students = self.env['education.student'].search([])
            for std in students:
                mail_content = self.announcement
                main_content = {
                    'subject': self.announcement_reason,
                    'author_id': self.env.user.partner_id.id,
                    'body_html': mail_content,
                    'attachment': self.attachment_id,
                    'email_to': std.email,
                }
                self.env['mail.mail'].create(main_content).send()

        elif self.to_assign == 'staff':
            faculty = self.env['education.faculty'].search([])
            for staff in faculty:
                mail_content = self.announcement
                main_content = {
                    'subject': self.announcement_reason,
                    'author_id': self.env.user.partner_id.id,
                    'body_html': mail_content,
                    'attachment': self.attachment_id,
                    'email_to': staff.email,
                }
                self.env['mail.mail'].create(main_content).send()

        else:
            partners = self.env['education.student'].search([])
            for partner in partners:
                mail_content = self.announcement
                main_content = {
                    'subject': self.announcement_reason,
                    'author_id': self.env.user.partner_id.id,
                    'body_html': mail_content,
                    'attachment': self.attachment_id,
                    'email_to': partner.email,
                }
                self.env['mail.mail'].create(main_content).send()

            fac = self.env['education.faculty'].search([])
            for p in fac:
                mail_content = self.announcement
                main_content = {
                    'subject': self.announcement_reason,
                    'author_id': self.env.user.partner_id.id,
                    'body_html': mail_content,
                    'email_to': p.email,
                }
                self.env['mail.mail'].create(main_content).send()

