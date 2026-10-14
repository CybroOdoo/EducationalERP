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
from odoo import api, fields, models, _
from odoo.exceptions import ValidationError


class EducationTimetableGenerate(models.TransientModel):
    """Wizard to automatically generate and time timetable slots."""

    _name = "education.timetable.generate"
    _description = "Auto-Generate Timetable Slots"

    # ── Standard Fields: Days selection
    # ────────────────────────────────────────
    mon = fields.Boolean(string="Monday", default=True)
    tue = fields.Boolean(string="Tuesday", default=True)
    wed = fields.Boolean(string="Wednesday", default=True)
    thu = fields.Boolean(string="Thursday", default=True)
    fri = fields.Boolean(string="Friday", default=True)
    sat = fields.Boolean(string="Saturday", default=False)
    sun = fields.Boolean(string="Sunday", default=False)

    # ── Standard Fields: Period Configuration
    # ──────────────────────────────────
    periods_per_day = fields.Integer(
        string="Periods per Day",
        default=8,
        required=True,
    )
    start_time = fields.Float(
        string="Day Start Time",
        default=9.0,
        required=True,
        help="24-hr format, e.g. 9.0 = 09:00, 8.5 = 08:30",
    )
    period_duration = fields.Integer(
        string="Period Duration (minutes)",
        default=45,
        required=True,
    )

    # ── Standard Fields: Breaks & Intervals
    # ────────────────────────────────────
    break_after_period = fields.Integer(
        string="Short Break After Period #",
        default=4,
        help="Set to 0 to disable short break.",
    )
    break_duration = fields.Integer(
        string="Short Break Duration (minutes)",
        default=15,
    )
    lunch_after_period = fields.Integer(
        string="Lunch Break After Period #",
        default=5,
        help="Set to 0 to disable lunch break.",
    )
    lunch_duration = fields.Integer(
        string="Lunch Duration (minutes)",
        default=45,
    )

    # ── Relational Fields
    # ──────────────────────────────────────────────────────
    timetable_id = fields.Many2one(
        comodel_name="education.timetable",
        string="Timetable",
        required=True,
        readonly=True,
    )

    # ── ORM Overrides
    # ──────────────────────────────────────────────────────────
    @api.model
    def default_get(self, fields_list):
        res = super().default_get(fields_list)
        active_id = self.env.context.get("active_id")
        if active_id and "timetable_id" in fields_list:
            res["timetable_id"] = active_id
        return res

    # ── Action Methods
    # ────────────────────────────────────────────────────────
    def action_generate_slots(self):
        self.ensure_one()
        if self.periods_per_day < 1 or self.periods_per_day > 15:
            raise ValidationError(
                _("Periods per day must be between 1 and 15."))
        if self.period_duration < 10:
            raise ValidationError(
                _("Period duration must be at least 10 minutes."))

        timetable = self.timetable_id
        if not timetable:
            raise ValidationError(_("No timetable selected."))

        # 1. Determine selected weekdays
        weekday_map = [
            ("0", self.mon),
            ("1", self.tue),
            ("2", self.wed),
            ("3", self.thu),
            ("4", self.fri),
            ("5", self.sat),
            ("6", self.sun),
        ]
        selected_days = [code for code, selected in weekday_map if selected]
        if not selected_days:
            raise ValidationError(_("Please select at least one day."))

        # 2. Compute start and end times for each period
        curr_time = self.start_time
        period_timings = {}
        for p in range(1, self.periods_per_day + 1):
            p_start = round(curr_time, 4)
            p_end = round(p_start + (self.period_duration / 60.0), 4)
            period_timings[p] = (p_start, p_end)

            curr_time = p_end
            if (self.break_after_period and p == self.break_after_period and
                    self.break_duration > 0):
                curr_time += self.break_duration / 60.0
            if (self.lunch_after_period and p == self.lunch_after_period and
                    self.lunch_duration > 0):
                curr_time += self.lunch_duration / 60.0

        # 3. Clear existing slots and batch-create fresh slots
        timetable.slot_ids.unlink()

        slots_to_create = [
            {
                "timetable_id": timetable.id,
                "weekday": day_code,
                "period_no": p,
                "start_time": period_timings[p][0],
                "end_time": period_timings[p][1],
            }
            for day_code in selected_days
            for p in range(1, self.periods_per_day + 1)
        ]

        if slots_to_create:
            self.env["education.timetable.slot"].create(slots_to_create)

        return {
            "type": "ir.actions.client",
            "tag": "display_notification",
            "params": {
                "title": _("Slots Generated"),
                "message": _(
                    "Successfully configured slots for %(days)s day(s) with "
                    "%(periods)s periods each.",
                    days=len(selected_days),
                    periods=self.periods_per_day,
                ),
                "type": "success",
                "sticky": False,
                "next": {"type": "ir.actions.act_window_close"},
            },
        }
