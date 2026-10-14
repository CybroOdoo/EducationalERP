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
"""education.classroom — Physical room/hall management.

Rooms used for teaching and examinations. Referenced by timetable slots
and exam seating plans.
"""
from odoo import api, fields, models, _
from odoo.exceptions import ValidationError


class EducationClassroom(models.Model):
    """Physical classroom, lab, or exam hall."""

    _name = "education.classroom"
    _description = "Classroom / Exam Hall"
    _order = "block, room_no"
    _rec_name = "display_name"

    # ── Standard Fields
    # ────────────────────────────────────────────────────────
    room_no = fields.Char(
        string="Room No.",
        required=True,
        help="Unique room number or identifier within the block "
             "(e.g. 101, LAB-A, AH-3).",
    )
    block = fields.Char(
        string="Block / Building",
        help="e.g. A, B, Science Block",
    )
    floor = fields.Char(
        string="Floor",
        help="Floor on which this room is located (e.g. Ground, 1st, 2nd).",
    )
    capacity = fields.Integer(
        string="Capacity (seats)",
        default=30,
        required=True,
        help="Total number of seats available in this room. Used for exam "
             "seating allocation and timetable planning.",
    )
    active = fields.Boolean(
        string="Active",
        default=True,
        help="Uncheck to archive this room. Archived rooms will not appear "
             "in timetable or exam seating selection.",
    )
    notes = fields.Text(
        string="Notes",
        help="Additional notes about the room (e.g. special equipment, "
             "accessibility features).",
    )

    room_type = fields.Many2one(
        comodel_name="education.classroom.type",
        string="Type",
        required=True,
        help="Category of the room (e.g. Lecture Hall, Laboratory, "
             "Seminar Room, Exam Hall).",
    )

    company_id = fields.Many2one(
        comodel_name="res.company",
        string="Institution",
        default=lambda self: self.env.company,
        required=True,
        index=True,
        help="Institution to which this room belongs.",
    )

    # ── Computed Fields
    # ────────────────────────────────────────────────────────
    display_name = fields.Char(
        string="Display Name",
        compute="_compute_display_name",
        store=True,
        help="Auto-generated: Block-RoomNo (e.g. A-101). "
             "Used as the display identifier in forms and dropdowns.",
    )

    # ── SQL Constraints
    # ───────────────────────────────────────────────────────
    _room_no_block_uniq = models.Constraint(
        "UNIQUE(room_no, block)",
        "A room with this number already exists in the same block.",
    )

    # ── Compute Methods
    # ────────────────────────────────────────────────────────
    @api.depends("room_no", "block")
    def _compute_display_name(self):
        """Build display name combining block and room number."""
        for rec in self:
            rec.display_name = (
                f"{rec.block}-{rec.room_no}"
                if rec.block else rec.room_no
                or "?"
            )

    # ── Constraints
    # ───────────────────────────────────────────────────────────
    @api.constrains("capacity")
    def _check_capacity(self):
        """Ensure classroom capacity is at least 1 seat."""
        for rec in self:
            if rec.capacity < 1:
                raise ValidationError(_("Capacity must be at least 1 seat."))


class EducationClassroomType(models.Model):
    """Category of classroom (e.g. Lecture Hall, Laboratory, Exam Hall)."""

    _name = "education.classroom.type"
    _description = "Room Type"
    _order = "name"

    name = fields.Char(
        string="Room Type",
        required=True,
        help="Label for this room category (e.g. Lecture Hall, Computer Lab, "
             "Drawing Hall).",
    )
