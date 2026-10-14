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
"""education_core.models.res_company
===========================================
Singleton model that stores institution-level settings: name, branding,
contact details, academic calendar parameters and system configuration.

There is exactly ONE res.company record per company (enforced by
_unique_company constraint). Use env['res.company'].get_profile() to
retrieve it.
"""
import base64
import io
import re

from PIL import Image, UnidentifiedImageError
import pytz

from odoo import api, fields, models, _
from odoo.exceptions import ValidationError

HEX_COLOR_REGEX = re.compile(r"^#([A-Fa-f0-9]{6}|[A-Fa-f0-9]{3})$")


class InstitutionProfile(models.Model):
    """Institution-level configuration singleton."""

    _name = "res.company"
    _description = "Institution Profile"
    _inherit = ["res.company", "mail.thread", "mail.activity.mixin"]
    _order = "name"

    short_name = fields.Char(
        string="Short Name / Abbreviation",
        size=20,
        tracking=True,
        help="Acronym or short form used in reports and emails.",
    )
    
    institution_type = fields.Selection(
        selection=[
            ("university", "University"),
            ("college", "College / Institute"),
            ("school", "School (K-12)"),
            ("vocational", "Vocational / Polytechnic"),
            ("corporate", "Corporate Training Centre"),
            ("other", "Other"),
        ],
        string="Institution Type",
        required=True,
        default="university",
        tracking=True,
        help="Category of the institution (e.g. University, College, "
             "School). Used to tailor workflows and reports to the "
             "institution's level.",
    )
    registration_number = fields.Char(
        string="Registration / Accreditation No.",
        tracking=True,
        help="Unique government or accreditation body registration number "
             "assigned to this institution (e.g. REG-2025-001).",
    )
    established_date = fields.Date(
        string="Established Date",
        help="Date the institution was founded.",
    )
    accreditation_body = fields.Char(
        string="Accreditation Body",
        help="e.g. NAAC, UGC, ISO 21001:2018",
    )

    # ── Branding ─────────────────────────────────────────────────────────
    branding_color = fields.Char(
        string="Primary Branding Colour",
        default="#1F3864",
        help="Hex colour used in reports, portal header and email templates.",
    )
    branding_color_secondary = fields.Char(
        string="Secondary Branding Colour",
        default="#2E75B6",
        help="Accent hex colour used alongside the primary colour in "
             "reports, portal pages and email templates (e.g. #2E75B6).",
    )

    phone = fields.Char(
        string="Phone",
        tracking=True,
        help="Primary landline or office phone number of the institution.",
    )
    mobile = fields.Char(
        string="Mobile / WhatsApp",
        help="Mobile or WhatsApp contact number for quick communication with "
             "students, parents and staff.",
    )
    email = fields.Char(
        string="Email",
        tracking=True,
        help="Official email address of the institution used for outgoing "
             "notifications, receipts and correspondence.",
    )
    website = fields.Char(
        string="Website URL",
        help="Public website URL of the institution "
             "(e.g. https://university.edu).",
    )

    # ── System ───────────────────────────────────────────────────────────
    timezone = fields.Selection(
        string="Timezone",
        selection="_tz_get",
        default=lambda self: self.env.user.tz or "UTC",
        required=True,
        help="Timezone used for scheduling academic events, cron jobs, "
             "timetable slots and date-based reports across the institution.",
    )

    # ── Academic Calendar Defaults ───────────────────────────────────────
    academic_year_start_month = fields.Selection(
        selection=[
            ("1", "January"),
            ("2", "February"),
            ("3", "March"),
            ("4", "April"),
            ("5", "May"),
            ("6", "June"),
            ("7", "July"),
            ("8", "August"),
            ("9", "September"),
            ("10", "October"),
            ("11", "November"),
            ("12", "December"),
        ],
        string="Academic Year Start Month",
        default="7",
        help="Month when a new academic year typically starts.",
    )
    working_days = fields.Selection(
        selection=[
            ("5", "Monday – Friday (5 days)"),
            ("6", "Monday – Saturday (6 days)"),
        ],
        string="Working Days per Week",
        default="5",
        help="Number of working days in a standard academic week. Used when "
             "generating timetables and calculating attendance thresholds.",
    )
    max_periods_per_day = fields.Integer(
        string="Max Periods per Day",
        default=8,
        help="Maximum number of teaching periods that can be scheduled in a "
             "single day. Timetable generation will not exceed this limit.",
    )

    # ── Constraints ──────────────────────────────────────────────────────
    @api.constrains("branding_color", "branding_color_secondary")
    def _check_hex_colour(self):
        """Validate that branding colours are valid hex values.

        Raises ValidationError if either primary or secondary branding
        colour does not match the #RRGGBB or #RGB hex format.
        """
        for rec in self:
            for colour in (rec.branding_color, rec.branding_color_secondary):
                if colour and not HEX_COLOR_REGEX.match(colour):
                    raise ValidationError(
                        _("Branding colour '%(colour)s' is not a valid hex "
                          "value (e.g. #1F3864).",
                          colour=colour)
                    )

    @api.constrains("established_date")
    def _check_established_date(self):
        """Ensure the institution's established date is not in the future.

        Raises ValidationError when the date is set to a future date.
        """
        today = fields.Date.today()
        for rec in self:
            if rec.established_date and rec.established_date > today:
                raise ValidationError(
                    _("Established date cannot be in the future."))

    # ── Image Processing Helpers ─────────────────────────────────────────
    _LOGO_MAX_WIDTH = 512
    _LOGO_MAX_HEIGHT = 512
    _LOGO_JPEG_QUALITY = 85
    _LOGO_WEBP_QUALITY = 85

    @classmethod
    def _is_svg(cls, raw):
        """Return True when the uploaded binary contains an SVG document."""
        sample = raw[:4096].lstrip().lower()
        return (sample.startswith(
            b"<?xml") and b"<svg" in sample) or b"<svg" in sample

    @classmethod
    def _optimize_logo(cls, value):
        """Resize/compress raster logo data before it is stored."""
        if not value:
            return value
        try:
            raw = base64.b64decode(value)
        except (ValueError, TypeError):
            return value
        if not raw or cls._is_svg(raw):
            return value
        try:
            with Image.open(io.BytesIO(raw)) as image:
                fmt = (image.format or "").upper()
                is_anim = getattr(image, "is_animated", False)
                if fmt == "GIF" and is_anim:
                    return value

                max_size = (cls._LOGO_MAX_WIDTH, cls._LOGO_MAX_HEIGHT)
                resample = Image.Resampling.LANCZOS
                image.thumbnail(max_size, resample)

                output = io.BytesIO()
                if fmt in ("JPEG", "JPG"):
                    if image.mode not in ("RGB", "L"):
                        bg = Image.new("RGB", image.size, "white")
                        if "A" in image.getbands():
                            mask = image.getchannel("A")
                            bg.paste(image, mask=mask)
                        else:
                            bg.paste(image)
                        image = bg
                    image.save(
                        output,
                        format="JPEG",
                        quality=cls._LOGO_JPEG_QUALITY,
                        optimize=True,
                        progressive=True,
                    )
                elif fmt == "WEBP":
                    image.save(
                        output,
                        format="WEBP",
                        quality=cls._LOGO_WEBP_QUALITY,
                        method=6,
                    )
                else:
                    valid_modes = ("RGB", "RGBA", "L", "LA", "P")
                    if image.mode not in valid_modes:
                        image = image.convert("RGBA")
                    image.save(output, format="PNG", optimize=True)

                opt = output.getvalue()
                if len(opt) < len(raw):
                    return base64.b64encode(opt)
                return value
        except (UnidentifiedImageError, OSError, ValueError):
            return value

    # ── CRUD Overrides ───────────────────────────────────────────────────
    @api.model_create_multi
    def create(self, vals_list):
        """Override create to run logo optimisation before saving.

        Resizes and compresses any uploaded logo image in each value
        dict before delegating to the standard create method.
        """
        for vals in vals_list:
            if vals.get("logo"):
                vals["logo"] = self._optimize_logo(vals["logo"])
        return super().create(vals_list)

    def write(self, vals):
        """Override write to run logo optimisation before saving.

        Resizes and compresses an uploaded logo image in the value dict
        before delegating to the standard write method.
        """
        if vals.get("logo"):
            vals["logo"] = self._optimize_logo(vals["logo"])
        return super().write(vals)

    # ── Action Methods ───────────────────────────────────────────────────
    def action_open_profile(self):
        """Smart button / menu action to open the profile form."""
        self.ensure_one()
        return {
            "type": "ir.actions.act_window",
            "name": _("Institution Profile"),
            "res_model": self._name,
            "res_id": self.id,
            "view_mode": "form",
            "target": "current",
        }

    # ── Business Methods ─────────────────────────────────────────────────
    @api.model
    def _tz_get(self):
        """Return list of (tz, tz) tuples for the timezone Selection field."""
        return [(tz, tz) for tz in
                sorted(pytz.all_timezones, key=lambda z: z.lower())]

    @api.model
    def get_profile(self):
        """Return the singleton profile for the current company.

        Creates a default one if it doesn't exist yet.
        """
        profile = self.search([("company_id", "=", self.env.company.id)],
                              limit=1)
        if not profile:
            profile = self.create({
                "name": self.env.company.name,
                "company_id": self.env.company.id,
                "timezone": self.env.user.tz or "UTC",
                "currency_id": self.env.company.currency_id.id,
            })
        return profile
