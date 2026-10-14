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
"""education.timetable.slot — Individual period entries within a timetable (
S3-T02).

One slot = one period on one weekday for a class timetable.
Linked to education.timetable (header) via Many2one.
"""
from odoo import api, fields, models, _
from odoo.exceptions import ValidationError


class EducationTimetableSlot(models.Model):
    """A single period slot in a class timetable."""

    _name = "education.timetable.slot"
    _description = "Timetable Slot"
    _order = "weekday, period_no"
    _rec_name = "display_name"

    # ── Standard Fields
    weekday = fields.Selection(
        selection=[
            ("0", "Monday"),
            ("1", "Tuesday"),
            ("2", "Wednesday"),
            ("3", "Thursday"),
            ("4", "Friday"),
            ("5", "Saturday"),
            ("6", "Sunday"),
        ],
        string="Day",
        required=True,
        help="Day of the week on which this period is scheduled.",
    )
    period_no = fields.Integer(
        string="Period",
        required=True,
        help="Period number within the day (1 = first period).",
        aggregator=False,
    )
    start_time = fields.Float(
        string="Start Time",
        help="24-hour format, e.g. 9.5 = 09:30.",
        aggregator=False,
    )
    end_time = fields.Float(
        string="End Time",
        aggregator=False,
        help="Ending time of this period in 24-hour decimal format "
             "(e.g. 10.25 = 10:15).",
    )
    notes = fields.Char(
        string="Notes",
        help="Any remarks about this slot (e.g. combined class, lab session).",
    )

    # ── Relational Fields
    timetable_id = fields.Many2one(
        comodel_name="education.timetable",
        string="Timetable",
        required=True,
        ondelete="cascade",
        index=True,
        help="Parent timetable header to which this slot belongs.",
    )
    subject_id = fields.Many2one(
        comodel_name="education.subject",
        string="Subject",
        domain="[('program_id', '=', program_id)]",
        ondelete="set null",
        help="Subject / Course taught in this slot.",
    )
    teacher_id = fields.Many2one(
        comodel_name="hr.employee",
        string="Teacher",
        ondelete="set null",
        help="Assigned faculty member for this slot.",
    )
    classroom_id = fields.Many2one(
        comodel_name="education.classroom",
        string="Room / Lab",
        ondelete="set null",
        help="Assigned classroom, laboratory, or hall for this slot.",
    )

    # ── Related Fields
    class_id = fields.Many2one(
        comodel_name="education.class",
        string="Class",
        related="timetable_id.class_id",
        store=True,
        readonly=True,
    )
    program_id = fields.Many2one(
        comodel_name="education.program",
        related="class_id.program_id",
        store=True,
        readonly=True,
    )
    academic_year_id = fields.Many2one(
        comodel_name="education.academic.year",
        related="timetable_id.academic_year_id",
        store=True,
        readonly=True,
    )
    company_id = fields.Many2one(
        related="timetable_id.company_id",
    )

    # ── Computed Fields
    display_name = fields.Char(
        string="Display Name",
        compute="_compute_display_name",
        store=True,
        help="Auto-generated: Day + Period + Subject name.",
    )
    is_today = fields.Boolean(
        string="Is Today",
        search="_search_is_today",
        help="for filtering today's slots",
    )

    # ── SQL Constraints
    _slot_timetable_uniq = models.Constraint(
        "UNIQUE(timetable_id, weekday, period_no)",
        "A slot for this day and period already exists in this timetable.",
    )

    # ── Compute Methods
    @api.depends("weekday", "period_no", "subject_id.name")
    def _compute_display_name(self):
        """Build slot display name from weekday, period, and subject."""
        weekday_map = dict(self._fields["weekday"].selection)
        for rec in self:
            day_str = weekday_map.get(rec.weekday, "?") if rec.weekday else ""
            period_str = f"P{rec.period_no}" if rec.period_no else ""
            prefix = f"{day_str} {period_str}".strip() or _("Slot")
            if rec.subject_id:
                rec.display_name = f"{prefix} — {rec.subject_id.name}"
            else:
                rec.display_name = prefix

    def _search_is_today(self, operator, value):
        """Search helper that filters slots matching today's weekday."""
        today_weekday = str(fields.Date.today().weekday())
        positive = (operator == 'in' and bool(value))
        if positive:
            return [("weekday", "=", today_weekday)]
        return [("weekday", "!=", False)]

    # ── Constraints
    @api.constrains("timetable_id", "weekday", "period_no")
    def _check_slot_unique(self):
        """Prevent duplicate slots for the same weekday and period."""
        weekday_map = dict(self._fields["weekday"].selection)
        for rec in self:
            if not rec.timetable_id or not rec.weekday or not rec.period_no:
                continue
            duplicate = self.search([
                ("id", "!=", rec.id),
                ("timetable_id", "=", rec.timetable_id.id),
                ("weekday", "=", rec.weekday),
                ("period_no", "=", rec.period_no),
            ], limit=1)
            if duplicate:
                weekday_label = weekday_map.get(rec.weekday, rec.weekday)
                raise ValidationError(
                    _(
                        "A slot for %(weekday)s, Period %(period)s already "
                        "exists in this timetable.",
                        weekday=weekday_label,
                        period=rec.period_no,
                    )
                )

    @api.constrains("start_time", "end_time")
    def _check_times(self):
        """Ensure end time is strictly after start time for each slot."""
        weekday_map = dict(self._fields["weekday"].selection)
        for rec in self:
            if (rec.start_time and rec.end_time and rec.end_time <=
                    rec.start_time):
                weekday_label = weekday_map.get(rec.weekday, rec.weekday)
                raise ValidationError(
                    _(
                        "End Time must be after Start Time for slot %("
                        "weekday)s P%(period)s.",
                        weekday=weekday_label,
                        period=rec.period_no,
                    )
                )

    @api.constrains("period_no")
    def _check_period_no(self):
        """Ensure period number is at least 1."""
        for rec in self:
            if rec.period_no < 1:
                raise ValidationError(_("Period number must be at least 1."))

    # ── Onchange Methods
    @api.onchange("period_no")
    def _onchange_period_no(self):
        """Auto-populate start/end time from other slots with the same
        period_no or standard 45-min template."""
        if not self.period_no:
            return
        if self.timetable_id:
            matching = self.timetable_id.slot_ids.filtered(
                lambda s: (
                    s.period_no == self.period_no
                    and s._origin.id != self._origin.id
                    and (s.start_time or s.end_time)
                )
            )
            if matching:
                self.start_time = matching[0].start_time
                self.end_time = matching[0].end_time
                return
        if not self.start_time:
            st = 9.0 + (self.period_no - 1) * 0.75
            self.start_time = round(st, 4)
            self.end_time = round(st + 0.75, 4)

    @api.onchange("start_time")
    def _onchange_start_time(self):
        """Auto-set end_time to start_time + 45 minutes if end_time is not
        set."""
        if self.start_time and not self.end_time:
            self.end_time = round(self.start_time + 0.75, 4)
