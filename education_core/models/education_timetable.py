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
"""education.timetable — Timetable header model.

Full timetable slot lines are implemented in Sprint 3 (Attendance & Faculty).
Establishes the model structure, validity dates, grid layout, and printing.
"""
from collections import defaultdict

from odoo import api, fields, models, _
from odoo.exceptions import ValidationError

WEEKDAY_SELECTION = [
    ("0", "Monday"),
    ("1", "Tuesday"),
    ("2", "Wednesday"),
    ("3", "Thursday"),
    ("4", "Friday"),
    ("5", "Saturday"),
    ("6", "Sunday"),
]


class EducationTimetable(models.Model):
    """Timetable header — one per class per academic year."""

    _name = "education.timetable"
    _description = "Class Timetable"
    _inherit = ["mail.thread"]
    _order = "academic_year_id desc, class_id"

    # ── Standard Fields
    state = fields.Selection(
        selection=[
            ("draft", "Draft"),
            ("published", "Published"),
            ("archived", "Archived"),
        ],
        string="Status",
        default="draft",
        tracking=True,
        help="Lifecycle status of the timetable. Only Published timetables "
             "are used for attendance and portal display.",
    )
    effective_from = fields.Date(
        string="Effective From",
        help="Date from which this timetable is active.",
    )
    effective_to = fields.Date(
        string="Effective To",
        help="Leave blank if there is no fixed end date.",
    )
    notes = fields.Text(
        string="Notes",
        help="Internal notes or remarks about this timetable.",
    )
    active = fields.Boolean(
        string="Active",
        default=True,
        help="Uncheck to archive this timetable without deleting it.",
    )

    # ── Relational Fields
    class_id = fields.Many2one(
        comodel_name="education.class",
        string="Class",
        required=True,
        ondelete="cascade",
        tracking=True,
        index=True,
        help="Class/section for which this timetable is being prepared.",
    )
    academic_year_id = fields.Many2one(
        comodel_name="education.academic.year",
        string="Academic Year",
        required=True,
        ondelete="restrict",
        tracking=True,
        index=True,
        help="Academic year to which this timetable applies.",
    )
    slot_ids = fields.One2many(
        comodel_name="education.timetable.slot",
        inverse_name="timetable_id",
        string="Timetable Slots",
        help="Individual period entries (day + period + subject + teacher) "
             "that make up this timetable.",
    )
    company_id = fields.Many2one(
        related="class_id.company_id"
    )

    # ── Computed Fields
    name = fields.Char(
        string="Timetable Reference",
        compute="_compute_name",
        store=True,
        help="Auto-generated reference: TT/<ClassName>/<YearCode>.",
    )
    slot_count = fields.Integer(
        string="# Slots",
        compute="_compute_slot_count",
        help="Total number of period slots defined in this timetable.",
    )

    # ── SQL Constraints
    _class_year_uniq = models.Constraint(
        "UNIQUE(class_id, academic_year_id)",
        "A timetable for this class and academic year already exists.",
    )

    # ── Compute Methods
    @api.depends("class_id", "academic_year_id")
    def _compute_name(self):
        """Auto-generate timetable name from class and academic year."""
        for rec in self:
            rec.name = (
                f"TT/{rec.class_id.name or ''}"
                f"/{rec.academic_year_id.code or ''}"
            )

    @api.depends("slot_ids")
    def _compute_slot_count(self):
        """Batched calculation of timetable slots without hydrating child
        records."""
        timetable_ids = self.ids
        if not timetable_ids:
            for rec in self:
                rec.slot_count = 0
            return

        slot_data = self.env["education.timetable.slot"]._read_group(
            domain=[("timetable_id", "in", timetable_ids)],
            groupby=["timetable_id"],
            aggregates=["__count"],
        )
        counts = {timetable.id: count for timetable, count in slot_data}
        for rec in self:
            rec.slot_count = counts.get(rec.id, 0)

    # ── Constraints
    @api.constrains("slot_ids")
    def _check_slot_ids_unique(self):
        """Ensure no duplicate weekday/period combinations in slot list."""
        weekday_map = dict(WEEKDAY_SELECTION)
        for rec in self:
            seen = set()
            for slot in rec.slot_ids:
                if not slot.weekday or not slot.period_no:
                    continue
                key = (slot.weekday, slot.period_no)
                if key in seen:
                    weekday_label = weekday_map.get(slot.weekday, slot.weekday)
                    raise ValidationError(
                        _(
                            "Duplicate slot: %(weekday)s Period %(period)s "
                            "is defined more than once.",
                            weekday=weekday_label,
                            period=slot.period_no,
                        )
                    )
                seen.add(key)

    @api.constrains("effective_from", "effective_to")
    def _check_effective_dates(self):
        """Ensure Effective To date is on or after Effective From."""
        for rec in self:
            if (rec.effective_from and rec.effective_to and rec.effective_to
                    < rec.effective_from):
                raise ValidationError(
                    _("Effective To date must be on or after Effective From "
                      "date."))

    # ── Action Methods
    def action_publish(self):
        """Publish the timetable, making it visible to faculty and students."""
        self.write({"state": "published"})

    def action_reset_draft(self):
        """Reset a published timetable back to draft for editing."""
        self.write({"state": "draft"})

    def action_print_timetable(self):
        """Trigger the PDF report action for this timetable."""
        self.ensure_one()
        return self.env.ref(
            "education_core.action_report_education_timetable"
        ).report_action(self, config=False)

    def action_open_generate_wizard(self):
        """Open the auto-generate wizard to create timetable slots."""
        self.ensure_one()
        return {
            "name": _("Auto-Generate Timetable Slots"),
            "type": "ir.actions.act_window",
            "res_model": "education.timetable.generate",
            "view_mode": "form",
            "target": "new",
            "context": {"default_timetable_id": self.id},
        }

    # ── Grid Helper Methods
    def _get_timetable_grid_data(self):
        """Construct the formatted grid structure for web and PDF reporting."""
        self.ensure_one()
        all_periods = sorted(
            list({s.period_no for s in self.slot_ids if s.period_no}))
        if not all_periods:
            all_periods = [1, 2, 3, 4, 5, 6, 7, 8]

        # Pre-index slots by (weekday, period_no) and period_no for O(1)
        # lookups
        slot_map = {}
        slots_by_period = defaultdict(list)
        subject_teachers = defaultdict(set)
        subject_details = {}

        for slot in self.slot_ids:
            slot_map[(slot.weekday, slot.period_no)] = slot
            if slot.start_time or slot.end_time:
                slots_by_period[slot.period_no].append(slot)
            if slot.subject_id:
                sub = slot.subject_id
                subject_details[sub.id] = (sub.code or "—", sub.name)
                if slot.teacher_id:
                    subject_teachers[sub.id].add(slot.teacher_id.name)

        # Extract timing ranges per period
        period_times = {}
        period_raw_times = {}
        for p in all_periods:
            slots_for_p = slots_by_period.get(p, [])
            if slots_for_p:
                first_slot = slots_for_p[0]
                st = self._format_time(first_slot.start_time)
                et = self._format_time(first_slot.end_time)
                period_times[p] = f"{st} – {et}" if st and et else (
                        st or et or "")
                period_raw_times[p] = (first_slot.start_time or 0.0,
                                       first_slot.end_time or 0.0)
            else:
                period_times[p] = ""
                period_raw_times[p] = (0.0, 0.0)

        # Build columns (periods + detected breaks between periods)
        columns = []
        for i, p in enumerate(all_periods):
            columns.append({
                "type": "period",
                "period_no": p,
                "time": period_times.get(p, ""),
            })
            if i < len(all_periods) - 1:
                next_p = all_periods[i + 1]
                curr_end = period_raw_times.get(p, (0.0, 0.0))[1]
                next_start = period_raw_times.get(next_p, (0.0, 0.0))[0]
                if curr_end and next_start and (next_start - curr_end) >= 0.05:
                    gap_mins = int(round((next_start - curr_end) * 60))
                    label = "LUNCH" if gap_mins >= 30 else "BREAK"
                    columns.append({
                        "type": "break",
                        "label": label,
                        "label_chars": list(label),
                        "time": f"{self._format_time(curr_end)} – "
                                f"{self._format_time(next_start)}",
                        "duration": gap_mins,
                    })

        # Build day rows
        weekday_dict = dict(WEEKDAY_SELECTION)
        used_weekdays = {s.weekday for s in self.slot_ids if s.weekday}
        days_to_show = ["0", "1", "2", "3", "4"]
        for extra_day in ["5", "6"]:
            if extra_day in used_weekdays:
                days_to_show.append(extra_day)

        day_rows = []
        for d_code in days_to_show:
            d_name = weekday_dict.get(d_code, "")
            row_slots = {p: slot_map.get((d_code, p)) for p in all_periods}
            day_rows.append({
                "code": d_code,
                "name": d_name,
                "slots": row_slots,
            })

        # Summary of subjects and faculty
        subject_summary = []
        for sub_id, (code, name) in subject_details.items():
            teachers = sorted(subject_teachers.get(sub_id, []))
            subject_summary.append({
                "code": code,
                "name": name,
                "teachers": ", ".join(teachers) if teachers else "Unassigned",
            })

        return {
            "periods": all_periods,
            "columns": columns,
            "period_times": period_times,
            "days": day_rows,
            "subject_summary": subject_summary,
        }

    @api.model
    def _format_time(self, val):
        """Format a float time value (hours) as 'HH: MM' string."""
        if val is None or val is False:
            return ""
        hours = int(val)
        minutes = int(round((val - hours) * 60))
        if minutes >= 60:
            hours += 1
            minutes = 0
        return f"{hours: 02d}: {minutes: 02d}"
