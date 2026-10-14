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
"""res.users extension to assign default security groups for educational
faculty."""
from odoo import api, models


class ResUsers(models.Model):
    """Extension of res.users to configure default educational security
    groups."""

    _inherit = "res.users"

    @api.model
    def _default_groups(self):
        """Default security groups for newly created users.

        When created in the context of a faculty member, grants the internal
        user,
        education teacher, and HR user groups.
        """
        if self.env.context.get("is_faculty"):
            group_xml_ids = [
                "base.group_user",
                "education_core.group_education_teacher",
                "hr.group_hr_user",
            ]
            groups = self.env["res.groups"]
            for xml_id in group_xml_ids:
                group = self.env.ref(xml_id, raise_if_not_found=False)
                if group:
                    groups |= group
            return groups

        return super()._default_groups()
