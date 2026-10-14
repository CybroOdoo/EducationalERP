# -*- coding: utf-8 -*-
###############################################################################
#
#    Cybrosys Technologies Pvt. Ltd.
#
#    Copyright (C) 2026-TODAY Cybrosys Technologies(
#    <https://www.cybrosys.com>).
#    Author: Cybrosys Techno Solutions(<https://www.cybrosys.com>)
#
#    This program is under the terms of the Odoo Proprietary License v1.0 (
#    OPL-1)
#    It is forbidden to publish, distribute, sublicense, or sell copies of the
#    Software or modified copies of the Software.
#
#    THE SOFTWARE IS PROVIDED “AS IS”, WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
#    IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
#    FITNESS FOR A PARTICULAR PURPOSE AND NON INFRINGEMENT. IN NO EVENT SHALL
#    THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM,DAMAGES OR OTHER
#    LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE,ARISING
#    FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER
#    DEALINGS IN THE SOFTWARE.
#
###############################################################################
"""education.portal.password — Wizard to set/reset student portal password.

Lets an education administrator set or reset the portal login password for a
student's portal user.
"""
import secrets
import string

from odoo import api, fields, models, _
from odoo.exceptions import UserError


class EducationPortalPassword(models.TransientModel):
    """Set/reset student portal password with secure auto-generation."""

    _name = "education.portal.password"
    _description = "Set Portal Password"

    # ── Standard Fields
    # ────────────────────────────────────────────────────────
    new_password = fields.Char(
        string="New Password",
        required=True,
        default=lambda self: self._generate_password(),
        help="The student uses this to log in to the portal. Copy it now and "
             "share it securely — it cannot be viewed again once saved.",
    )

    # ── Relational Fields
    # ──────────────────────────────────────────────────────
    enrollment_id = fields.Many2one(
        comodel_name="education.enrollment",
        string="Enrollment",
        required=True,
        readonly=True,
    )
    user_id = fields.Many2one(
        comodel_name="res.users",
        string="Portal User",
        required=True,
        readonly=True,
    )

    # ── Computed / Related Fields
    # ──────────────────────────────────────────────
    login = fields.Char(
        string="Login",
        related="user_id.login",
        readonly=True,
    )

    # ── Helper / Business Methods
    # ─────────────────────────────────────────────
    @api.model
    def _generate_password(self):
        """Return a readable, reasonably strong random password."""
        alphabet = string.ascii_letters + string.digits
        return "".join(secrets.choice(alphabet) for _ in range(10))

    # ── Action Methods
    # ────────────────────────────────────────────────────────
    def action_set_password(self):
        self.ensure_one()
        if not self.new_password or len(self.new_password) < 8:
            raise UserError(_("Password must be at least 8 characters long."))

        # Set user password with elevated sudo rights
        self.user_id.sudo().write({"password": self.new_password})
        self.enrollment_id.sudo().write({"portal_password_set": True})
        self.enrollment_id.message_post(
            body=_(
                "Portal password was reset by %(user)s.",
                user=self.env.user.name,
            )
        )
        return {"type": "ir.actions.act_window_close"}
