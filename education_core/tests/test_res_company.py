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
"""
education_config — Institution Profile Tests
============================================
Covers: singleton constraint, get_profile(), hex colour validation,
        field defaults, and action_open_profile return value.
"""
from odoo.tests.common import TransactionCase, tagged
from odoo.exceptions import ValidationError


@tagged("post_install", "-at_install")
class TestInstitutionProfile(TransactionCase):
    """Test suite for the InstitutionProfile (res.company) model.

    Covers singleton constraint, get_profile(), hex colour validation,
    field defaults, _tz_get(), and action_open_profile().
    """

    def setUp(self):
        """Set up test fixtures — remove any existing profile for isolation."""
        super().setUp()
        self.Profile = self.env["res.company"]
        # Remove any existing profile for the current company so tests are
        # isolated
        self.Profile.search(
            [("company_id", "=", self.env.company.id)]).unlink()

    # ── get_profile ────────────────────────────────────────────────────────

    def test_get_profile_creates_when_missing(self):
        """get_profile() must create a default profile when none exists."""
        profile = self.Profile.get_profile()
        self.assertTrue(profile.id)
        self.assertEqual(profile.company_id, self.env.company)
        self.assertEqual(profile.name, self.env.company.name)

    def test_get_profile_returns_existing(self):
        """get_profile() must return the same record on repeated calls."""
        p1 = self.Profile.get_profile()
        p2 = self.Profile.get_profile()
        self.assertEqual(p1.id, p2.id)

    def test_get_profile_count_is_one(self):
        """Only one profile should exist per company after multiple
        get_profile calls."""
        self.Profile.get_profile()
        self.Profile.get_profile()
        count = self.Profile.search_count(
            [("company_id", "=", self.env.company.id)])
        self.assertEqual(count, 1)

    # ── Singleton constraint ───────────────────────────────────────────────

    def test_duplicate_company_raises(self):
        """Creating a second profile for the same company must raise."""
        self.Profile.create({
            "name": "First Profile",
            "company_id": self.env.company.id,
            "timezone": "UTC",
            "currency_id": self.env.company.currency_id.id,
        })
        with self.assertRaises(Exception):
            self.Profile.create({
                "name": "Second Profile",
                "company_id": self.env.company.id,
                "timezone": "UTC",
                "currency_id": self.env.company.currency_id.id,
            })

    # ── Hex colour constraint ──────────────────────────────────────────────

    def test_valid_hex_colour_accepted(self):
        """Valid 6-digit and 3-digit hex colours must not raise."""
        profile = self.Profile.get_profile()
        profile.write({"branding_color": "#AABBCC"})
        profile.write({"branding_color": "#ABC"})

    def test_invalid_hex_colour_raises(self):
        """Non-hex branding colour must raise ValidationError."""
        profile = self.Profile.get_profile()
        with self.assertRaises(ValidationError):
            profile.write({"branding_color": "red"})

    def test_invalid_hex_missing_hash_raises(self):
        """Hex without leading # must raise ValidationError."""
        profile = self.Profile.get_profile()
        with self.assertRaises(ValidationError):
            profile.write({"branding_color": "1F3864"})

    # ── Field defaults ─────────────────────────────────────────────────────

    def test_default_institution_type(self):
        """Default institution_type must be 'university'."""
        profile = self.Profile.get_profile()
        self.assertEqual(profile.institution_type, "university")

    def test_default_working_days(self):
        """Default working_days must be '5' (Mon–Fri)."""
        profile = self.Profile.create({
            "name": "Defaults Test",
            "company_id": self.env.company.id,
            "timezone": "UTC",
            "currency_id": self.env.company.currency_id.id,
        })
        self.assertEqual(profile.working_days, "5")

    def test_default_max_periods(self):
        """Default max_periods_per_day must be 8."""
        profile = self.Profile.get_profile()
        self.assertEqual(profile.max_periods_per_day, 8)

    # ── Timezone list ──────────────────────────────────────────────────────

    def test_tz_get_returns_list_of_tuples(self):
        """_tz_get() must return a non-empty list of (str, str) tuples."""
        tzs = self.Profile._tz_get()
        self.assertIsInstance(tzs, list)
        self.assertTrue(len(tzs) > 0)
        first = tzs[0]
        self.assertIsInstance(first, tuple)
        self.assertEqual(len(first), 2)
        self.assertEqual(first[0], first[1])

    def test_tz_get_contains_utc(self):
        """_tz_get() must include UTC."""
        tzs = self.Profile._tz_get()
        tz_names = [t[0] for t in tzs]
        self.assertIn("UTC", tz_names)

    # ── action_open_profile ────────────────────────────────────────────────

    def test_action_open_profile_returns_act_window(self):
        """action_open_profile() must return an ir.actions.act_window dict."""
        profile = self.Profile.get_profile()
        action = profile.action_open_profile()
        self.assertEqual(action["type"], "ir.actions.act_window")
        self.assertEqual(action["res_model"], "res.company")
        self.assertEqual(action["res_id"], profile.id)
