# -*- coding: utf-8 -*-
################################################################################
#
#    Cybrosys Technologies Pvt. Ltd.
#
#    Copyright (C) 2024-TODAY Cybrosys Technologies(<https://www.cybrosys.com>).
#    Author: Jumana Haseen (odoo@cybrosys.com)
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
################################################################################
import logging
import re
from datetime import datetime
import lxml
from odoo import api, fields, models, _

_logger = logging.getLogger(__name__)
image_re = re.compile(r"data:(image/[A-Za-z]+);base64,(.*)")


class SchoolAnnouncement(models.Model):
    """Create a model 'school.announcement' and add fields"""
    _name = 'school.announcement'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _description = 'School Announcement'

    name = fields.Char(
        string='Code No:',
        default=lambda x: _('New'), help="Code for the announcement.")
    announcement_subject = fields.Char(
        string='Subject',
        required=True,
        readonly=False,
        help="Title or Subject of the Announcement")
    state = fields.Selection(
        [('draft', 'Draft'),
         ('to_send', 'Confirmed'),
         ('pending', 'Pending'),
         ('done', 'Done'),
         ('failed', 'Failed'),
         ('expired', 'Expired')],
        string='Status', default='draft',
        help="State of the announcement")
    scheduled_date = fields.Date(
        'Scheduled Date',
        help="If set, the queue manager will send the email after the date. "
             "If not set, the email will be send as soon as possible.")
    requested_date = fields.Date(
        string='Send Date',
        default=datetime.now().strftime('%Y-%m-%d'),
        help="Requested date of announcement")
    body_html = fields.Html(string='Body converted to be sent by mail',
                            sanitize_attributes=False,
                            help="Body converted to be sent by mail.")
    attachment_ids = fields.Many2many(
        'ir.attachment', 'doc_warning_rel',
        'doc_id', 'attach_id4',
        string="Attachment",
        help='You can attach document with the mail.')
    expiry_date = fields.Date(
        string='Expiry Date', required=True,
        help="Expiry date of announcement.")
    to_assign = fields.Selection(
        [('general', 'General'),
         ('student', 'Student'),
         ('staff', 'Staff')],
        string='Recipients',
        required=True,
        help="To whom the announcement is assigned.")
    failure_reason = fields.Text(
        string='Failure Reason',
        compute="_compute_failure_reason",
        help="Mention the failure reason.")
    mail_id = fields.Many2one('mail.mail', string="Mail")

    def expire_date(self):
        """Calculate the date is expired or not."""
        announcements = self.search(
            [('expiry_date', '<=', datetime.today()),
             ('state', 'not in', ['expired', 'done'])])
        for rec in announcements:
            rec.state = 'expired'

    def to_send(self):
        """Change the state to 'to_send' on clicking confirm button"""
        self.state = 'to_send'

    def undo(self):
        """Change state to draft"""
        self.state = 'draft'

    @api.model
    def create(self, vals):
        """Create sequence for announcement"""
        vals['name'] = self.env['ir.sequence'].next_by_code(
            'school.announcement') or _('New')
        return super(SchoolAnnouncement, self).create(vals)

    def mail_send(self):
        """Function to send mail to student, staff or general"""
        recipients = []
        if not self.mail_id:
            if self.to_assign == 'student':
                students = self.env['education.student'].search([]).mapped(
                    'email')
                recipients += students
            elif self.to_assign == 'staff':
                faculty = self.env['education.faculty'].search([]).mapped(
                    'email')
                recipients += faculty
            elif self.to_assign == 'general':
                students = self.env['education.student'].search([]).mapped(
                    'email')
                recipients += students
                faculty = self.env['education.faculty'].search([]).mapped(
                    'email')
                recipients += faculty
            mail_content = self._convert_inline_images_to_urls(self.body_html)
            main_content = {
                'subject': self.announcement_subject,
                'author_id': self.env.user.partner_id.id,
                'body_html': mail_content,
                'email_to': ','.join(filter(bool, recipients))
            }
            self.mail_id = self.env['mail.mail'].create(main_content)
        self.mail_id.send()
        if self.mail_id.state == 'sent':
            self.write({'state': 'done'})
        if self.mail_id.state == 'exception':
            self.write({'state': 'failed'})

    def mail_schedule(self):
        """Function to schedule mail for the recipients"""
        recipients = []
        if self.to_assign == 'student':
            students = self.env['education.student'].search([]).mapped('email')
            recipients += students
        elif self.to_assign == 'staff':
            faculty = self.env['education.faculty'].search([]).mapped('email')
            recipients += faculty
        elif self.to_assign == 'general':
            students = self.env['education.student'].search([]).mapped('email')
            recipients += students
            faculty = self.env['education.faculty'].search([]).mapped('email')
            recipients += faculty
        mail_content = self._convert_inline_images_to_urls(self.body_html)
        main_content = {
            'subject': self.announcement_subject,
            'author_id': self.env.user.partner_id.id,
            'body_html': mail_content,
            'scheduled_date': str(self.scheduled_date),
            'email_to': ','.join(filter(bool, recipients))
        }
        self.mail_id = self.env['mail.mail'].create(main_content)
        self.write({'state': 'pending'})

    def mail_resend(self):
        """Function to resend the mail"""
        self.mail_id.send()

    @api.depends('mail_id.state', 'mail_id.failure_reason')
    def _compute_failure_reason(self):
        """Function to compute the failure reason"""
        for rec in self:
            rec.failure_reason = rec.mail_id.failure_reason
            if rec.mail_id.state == 'exception':
                rec.write({'state': 'failed'})
            elif rec.mail_id.state == 'sent':
                rec.write({'state': 'done'})

    def _convert_inline_images_to_urls(self, body_html):
        """
        Find inline base64 encoded images, make an attachement out of
        them and replace the inline image with an url to the attachement.
        """

        def _image_to_url(b64image: bytes):
            """Store an image in an attachment and returns an url"""
            attachment = self.env['ir.attachment'].create({
                'datas': b64image,
                'name': "cropped_image_mailing_{}".format(self.id),
                'type': 'binary', })

            attachment.generate_access_token()

            return '/web/image/%s?access_token=%s' % (
                attachment.id, attachment.access_token)

        modified = False
        root = lxml.html.fromstring(body_html)
        for node in root.iter('img'):
            match = image_re.match(node.attrib.get('src', ''))
            if match:
                mime = match.group(1)  # unsed
                image = match.group(2).encode()  # base64 image as bytes

                node.attrib['src'] = _image_to_url(image)
                modified = True

        if modified:
            return lxml.html.tostring(root)
        return body_html
