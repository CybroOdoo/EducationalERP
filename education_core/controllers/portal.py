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
"""education_core — Portal Controller (S2-T12).

Student self-service portal: own profile, enrolled courses, and leave requests.
URL scheme:
    /student                    — dashboard
    /student/enrollment/<id>    — enrollment detail
    /student/leave              — leave history
    /student/leave/request      — submit leave application
"""
import base64

from odoo import http, _
from odoo.addons.portal.controllers.portal import CustomerPortal
from odoo.http import request


class EducationPortal(CustomerPortal):
    """Extend CustomerPortal with student-specific self-service pages."""

    def _prepare_home_portal_values(self, counters):
        """Add active enrollment count to the portal home counters."""
        values = super()._prepare_home_portal_values(counters)
        if "enrollment_count" in counters:
            partner = request.env.user.partner_id
            values["enrollment_count"] = request.env[
                "education.enrollment"].sudo().search_count([
                ("student_partner_id", "=", partner.id),
                ("state", "=", "active"),
            ])
        return values

    # ── Student Dashboard
    # ──────────────────────────────────────────────────────
    @http.route(["/student", "/student/page/<int:page>"], type="http",
                auth="user", website=True)
    def student_dashboard(self, page=1, **kw):
        """Display student dashboard with enrollments and document
        completion."""
        partner = request.env.user.partner_id
        enrollments = request.env["education.enrollment"].sudo().search([
            ("student_partner_id", "=", partner.id),
        ])
        return request.render(
            "education_core.portal_student_dashboard",
            {
                "enrollments": enrollments,
                "page_name": "student_dashboard",
            },
        )

    # ── Enrollment Detail
    # ──────────────────────────────────────────────────────
    @http.route(
        ["/student/enrollment/<int:enrollment_id>"],
        type="http",
        auth="user",
        website=True,
    )
    def student_enrollment_detail(self, enrollment_id, **kw):
        """Show a single enrollment with its document checklist."""
        partner = request.env.user.partner_id
        enrollment = request.env["education.enrollment"].sudo().search([
            ("id", "=", enrollment_id),
            ("student_partner_id", "=", partner.id),
        ], limit=1)

        # Access check: redirect if enrollment doesn't exist or doesn't
        # belong to current student
        if not enrollment:
            return request.redirect("/student")

        return request.render(
            "education_core.portal_student_enrollment",
            {
                "enrollment": enrollment,
                "documents": enrollment.document_ids,
                "page_name": "student_enrollment",
            },
        )

    # ── Student Leave
    # ──────────────────────────────────────────────────────────
    @http.route(["/student/leave"], type="http", auth="user", website=True)
    def student_leave(self, **kw):
        """Show student's leave requests history and active enrollment
        status."""
        partner = request.env.user.partner_id
        enrollment = request.env["education.enrollment"].sudo().search([
            ("student_partner_id", "=", partner.id),
            ("state", "=", "active"),
        ], limit=1)

        leaves = request.env["education.leave.request"].search([
            ("enrollment_id.student_partner_id", "=", partner.id),
        ])

        return request.render(
            "education_core.portal_student_leave",
            {
                "enrollment": enrollment,
                "leaves": leaves,
                "enrollment_status": kw.get("enrollment"),
                "page_name": "student_leave_list",
            },
        )

    # ── Student Leave Request Form
    # ─────────────────────────────────────────────
    @http.route(
        ["/student/leave/request"],
        type="http",
        auth="user",
        website=True,
        methods=["GET", "POST"],
    )
    def student_leave_request(self, **kw):
        """Handle rendering and submission of student leave applications."""
        partner = request.env.user.partner_id
        enrollment = request.env["education.enrollment"].sudo().search([
            ("student_partner_id", "=", partner.id),
            ("state", "=", "active"),
        ], limit=1)

        # Redirect if student has no active enrollment
        if not enrollment:
            return request.redirect("/student/leave?enrollment=notfound")

        # GET: Display leave application form
        if request.httprequest.method == "GET":
            return request.render(
                "education_core.portal_student_leave_request",
                {
                    "enrollment": enrollment,
                    "page_name": "student_leave_request",
                },
            )

        # POST: Process leave application submission
        vals = {
            "enrollment_id": enrollment.id,
            "leave_type": kw.get("leave_type"),
            "date_from": kw.get("date_from"),
            "date_to": kw.get("date_to"),
            "reason": kw.get("reason"),
        }

        # Handle optional supporting document attachment
        uploaded_file = request.httprequest.files.get("supporting_document")
        if uploaded_file and uploaded_file.filename:
            vals.update({
                "supporting_document": base64.b64encode(uploaded_file.read()),
                "supporting_document_name": uploaded_file.filename,
            })

        leave = request.env["education.leave.request"].sudo().create(vals)
        leave.action_submit()

        return request.redirect("/student/leave")
