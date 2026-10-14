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
"""Date-relative demo data generator for Education Core.

The XML demo (``education_core_demo.xml``) only creates a handful of
records. This generator tops it up so that *every* institution has a
complete, realistic data set whose dates are anchored to the day the
module is installed:

* each institution: >= 3 departments, each with >= 2 programs, each
  program with >= 2 classes and >= 5 subjects, faculty, classrooms,
  timetables and two academic years;
* each class: at least 10 enrollments, each with an application,
  documents (some expiring soon / already expired) and a student partner;
* each enrollment: 30 attendance records, one for each of the 30 days
  before the installation date;
* leave requests and fresh applications around the installation date;
* the default administrator is allowed to work in all institutions.
"""
import base64
import logging
import os
import random
from collections import defaultdict
from datetime import timedelta

from dateutil.relativedelta import relativedelta

from odoo import Command, fields

from .demo_specs import (
    ABSENCE_NOTES, BLOOD_GROUPS, BLOOD_WEIGHTS, CITIES, FACULTY_UNIVERSITIES,
    FEMALE_NAMES, GUARDIAN_JOBS, INSTITUTIONS, LAST_NAMES, LATE_NOTES,
    LEAVE_REASONS, MALE_NAMES, PREVIOUS_COLLEGES, PREVIOUS_EMPLOYERS,
    PREVIOUS_SCHOOLS, STREETS,
)

_logger = logging.getLogger(__name__)

PARAM_KEY = "education_core.demo_data_loaded"
STRICT_ENV = "EDUCATION_DEMO_STRICT"
ATTENDANCE_DAYS = 30
SCHOOL_DAYS_PER_WEEK = 5
CHUNK = 1500

# Minimal valid-looking attachments used for demo documents.
PDF_FILE = base64.b64encode(
    b"%PDF-1.4\n1 0 obj<</Type/Catalog/Pages 2 0 R>>endobj\n"
    b"2 0 obj<</Type/Pages/Kids[3 0 R]/Count 1>>endobj\n"
    b"3 0 obj<</Type/Page/Parent 2 0 R/MediaBox[0 0 200 100]>>endobj\n"
    b"trailer<</Root 1 0 R>>\n%%EOF\n")
PNG_FILE = (
    "iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAQAAAC1HAwCAAAAC0lEQVR42mNkYAAAAAYAA"
    "jCB0C8AAAAASUVORK5CYII=").encode()


def load_demo_data(env):
    """Entry point of the post-install hook.

    Nothing happens unless the module was installed with demo data, and
    the data is generated only once.
    """
    env.cr.execute(
        "SELECT demo FROM ir_module_module WHERE name = %s",
        ("education_core",))
    row = env.cr.fetchone()
    if not (row and row[0]):
        return
    params = env["ir.config_parameter"].sudo()
    if params.get_param(PARAM_KEY):
        return
    generator = DemoGenerator(env, strict=bool(os.environ.get(STRICT_ENV)))
    generator.run()
    generator.register_xml_ids()
    params.set_param(PARAM_KEY, "1")
    marker = params.search([("key", "=", PARAM_KEY)])
    env["ir.model.data"].sudo().create({
        "module": "education_core", "name": "demo_data_loaded_marker",
        "model": "ir.config_parameter", "res_id": marker.id,
        "noupdate": True,
    })


class _Institution:
    """State collected while building one institution."""

    def __init__(self, spec, company, env):
        """Bind the institution spec to its company and environment."""
        self.spec = spec
        self.company = company
        self.env = env(context=dict(
            env.context, allowed_company_ids=[company.id]))
        self.year = None
        self.prev_year = None
        self.rooms = None
        self.faculty = {}            # department id -> hr.employee
        self.programs = []           # (program, program spec, dept)
        self.classes = None
        self.new_enrollments = self.env["education.enrollment"]
        self.leave_days = defaultdict(set)   # enrollment id -> dates


class DemoGenerator:
    """Create the demo data of every institution described in the specs."""

    def __init__(self, env, strict=False):
        """Prepare a quiet environment and a reproducible random source."""
        context = dict(
            env.context, tracking_disable=True, mail_create_nolog=True,
            mail_notrack=True, mail_auto_subscribe_no_notify=True,
            no_reset_password=True)
        self.env = env(context=context)
        self.strict = strict
        self.today = fields.Date.today()
        self.rng = random.Random(20260101)
        self.admin = (self.env.ref("base.user_admin", False)
                      or self.env.user)
        self.used_names = set()
        self.used_emails = set()
        self.phone_seq = 2000
        self.lab_codes = set()
        self.partner_ids = []
        self.employee_ids = []

    # ── Orchestration ───────────────────────────────────────────────────
    def run(self):
        """Build every institution, then link them to the administrator."""
        for spec in INSTITUTIONS:
            self._step(spec["key"], self._build_institution, spec)
        self._step("administrator", self._link_administrator)

    def _step(self, label, method, *args):
        """Run one step in a savepoint; log (or raise when strict)."""
        try:
            with self.env.cr.savepoint():
                method(*args)
        except Exception:
            if self.strict:
                raise
            _logger.exception(
                "Education demo data: step '%s' failed and was skipped.",
                label)

    def _build_institution(self, spec):
        """Create all the data of one institution."""
        company = self.env.ref(spec["company"])
        inst = _Institution(spec, company, self.env)
        _logger.info("Education demo data: building %s ...", company.name)
        for step in (
                self._company_profile, self._academic_years, self._rooms,
                self._structure, self._students, self._extra_applications,
                self._leaves, self._timetables, self._attendance):
            step(inst)
            self.env.flush_all()

    # ── Small helpers ───────────────────────────────────────────────────
    def _day(self, offset):
        """The date ``offset`` days from the installation date."""
        return self.today + timedelta(days=offset)

    def _next_phone(self):
        """A unique demo phone number."""
        self.phone_seq += 1
        return "+1 555-%04d" % self.phone_seq

    def _unique_email(self, first, last, domain):
        """A unique, lower-case e-mail address."""
        base = "%s.%s" % (first, last)
        email = "%s@%s" % (base, domain)
        n = 1
        while email.lower() in self.used_emails:
            n += 1
            email = "%s%d@%s" % (base, n, domain)
        self.used_emails.add(email.lower())
        return email.lower()

    def _name(self, gender=None):
        """A unique (first name, last name, gender) combination."""
        for _attempt in range(200):
            gender_ = gender or self.rng.choice(["male", "female"])
            pool = MALE_NAMES if gender_ == "male" else FEMALE_NAMES
            first, last = self.rng.choice(pool), self.rng.choice(LAST_NAMES)
            if (first, last) not in self.used_names:
                self.used_names.add((first, last))
                return first, last, gender_
        raise RuntimeError("Name pool exhausted")

    def _year_start(self, month, back=0):
        """Start date of the academic year ``back`` years before the
        current one, for an academic year starting in ``month``."""
        months = (self.today.month - month) % 12 + 12 * back
        return (self.today - relativedelta(months=months)).replace(day=1)

    # ── 1. Institution profile ──────────────────────────────────────────
    def _company_profile(self, inst):
        """Fill the contact details of the institution when missing."""
        company = inst.company
        values = {key: value for key, value in inst.spec["contact"].items()
                  if not company[key]}
        if values:
            company.write(values)

    # ── 2. Academic years ───────────────────────────────────────────────
    def _academic_years(self, inst):
        """Make sure the institution has a current and a previous year.

        Years start in the institution's ``academic_year_start_month``
        and last exactly twelve months (e.g. 1 Jul - 30 Jun).
        """
        company = inst.company
        Year = inst.env["education.academic.year"].with_context(
            active_test=False)
        years = Year.search([("company_id", "=", company.id)])
        current = years.filtered("is_current")[:1] or years.filtered(
            lambda y: y.date_start <= self.today <= y.date_end)[:1]
        month = int(company.academic_year_start_month or 1)
        if not current:
            current = self._create_year(inst, month, 0, True)
        previous = years.filtered(
            lambda y: y.date_end < current.date_start)[:1]
        if not previous:
            previous = self._create_year(inst, month, 1, False)
        inst.year, inst.prev_year = current, previous

    def _create_year(self, inst, month, back, is_current):
        """Create the academic year starting ``back`` years ago."""
        start = self._year_start(month, back)
        end = start + relativedelta(years=1, days=-1)
        label = ("%d-%d" % (start.year, end.year) if start.year != end.year
                 else "FY %d" % start.year)
        return inst.env["education.academic.year"].create({
            "name": label,
            "code": "AY%s%s" % (str(start.year)[-2:], str(end.year)[-2:]),
            "date_start": start, "date_end": end,
            "is_current": is_current, "sequence": 10 + 10 * (2 - back),
            "company_id": inst.company.id,
        })

    # ── 3. Classrooms ───────────────────────────────────────────────────
    def _rooms(self, inst):
        """Create the missing classrooms, labs and halls."""
        Room = inst.env["education.classroom"].with_context(
            active_test=False)
        values = []
        for room_no, block, floor, capacity, type_xml in (
                inst.spec["classrooms"]):
            if Room.search_count(
                    [("room_no", "=", room_no), ("block", "=", block)]):
                continue
            values.append({
                "room_no": room_no, "block": block, "floor": floor,
                "capacity": capacity, "company_id": inst.company.id,
                "room_type": self.env.ref(
                    "education_core." + type_xml).id,
            })
        Room.create(values)
        inst.rooms = Room.search([("company_id", "=", inst.company.id)])

    # ── 4. Departments, programs, subjects, faculty, classes ────────────
    def _structure(self, inst):
        """Create departments with their faculty, programs and classes."""
        Class = inst.env["education.class"]
        for dspec in inst.spec["departments"]:
            dept = self._department(inst, dspec)
            inst.faculty[dept.id] = self._faculty(inst, dept, dspec)
            if not dept.head_id:
                dept.head_id = inst.faculty[dept.id][:1]
            for pspec in dspec["programs"]:
                program = self._program(inst, dept, pspec)
                self._subjects(program, pspec)
                self._classes(inst, dept, program, pspec)
                inst.programs.append((program, pspec, dept))
        inst.classes = Class.search(
            [("program_id.company_id", "=", inst.company.id),
             ("academic_year_id", "=", inst.year.id)],
            order="program_id, section")

    def _department(self, inst, dspec):
        """Find (xml id or code) or create a department."""
        Department = inst.env["education.department"].with_context(
            active_test=False)
        dept = self.env.ref(
            "education_core." + dspec["xmlid"], False
        ) if dspec.get("xmlid") else Department.browse()
        dept = dept or Department.search([
            ("code", "=", dspec["code"]),
            ("company_id", "=", inst.company.id)], limit=1)
        if not dept:
            dept = Department.create({
                "name": dspec["name"], "code": dspec["code"],
                "description": dspec.get("description"),
                "sequence": 10 * (len(inst.faculty) + 1),
                "company_id": inst.company.id,
            })
        return dept

    def _program(self, inst, dept, pspec):
        """Find (xml id or code) or create a program."""
        Program = inst.env["education.program"].with_context(
            active_test=False)
        program = self.env.ref(
            "education_core." + pspec["xmlid"], False
        ) if pspec.get("xmlid") else Program.browse()
        program = program or Program.search([
            ("code", "=", pspec["code"]),
            ("department_id.company_id", "=", inst.company.id)], limit=1)
        if not program:
            program = Program.create({
                "name": pspec["name"], "code": pspec["code"],
                "degree_type": pspec["degree"],
                "duration_years": pspec["years"],
                "semesters_per_year": pspec["semesters"],
                "eligibility": pspec["eligibility"],
                "description": "<p>%s</p>" % pspec["description"],
                "department_id": dept.id,
                "sequence": 10 * (len(inst.programs) + 1),
            })
        return program

    def _subjects(self, program, pspec):
        """Create the missing subjects of a program."""
        Subject = self.env["education.subject"].with_context(
            active_test=False)
        existing = set(program.subject_ids.mapped("code"))
        values = []
        for sequence, (code, name, lab) in enumerate(
                pspec["extra_subjects"], start=50):
            if lab:
                self.lab_codes.add(code)
            if code not in existing:
                values.append({
                    "name": name, "code": code, "program_id": program.id,
                    "sequence": sequence})
        Subject.create(values)

    def _faculty(self, inst, dept, dspec):
        """Top the department up to its target number of faculty."""
        Employee = inst.env["hr.employee"]
        faculty = Employee.search([
            ("is_faculty", "=", True), ("edu_department_id", "=", dept.id)])
        missing = dspec["faculty_target"] - len(faculty)
        if missing > 0:
            faculty |= self._create_faculty(
                inst, dept, dspec, missing, len(faculty))
        return faculty

    def _create_faculty(self, inst, dept, dspec, count, offset):
        """Create ``count`` faculty members and their qualifications."""
        spec = inst.spec
        values = []
        for i in range(count):
            first, last, _gender = self._name()
            senior = (offset + i) < 2
            title = spec["titles"][0 if senior else (offset + i) % len(
                spec["titles"])]
            doctor = title.startswith(("Professor", "Principal")) or (
                self.rng.random() < 0.25)
            joined = self.today - relativedelta(
                years=self.rng.randint(1, 14),
                days=self.rng.randint(0, 300))
            email = self._unique_email(first, last, spec["email_domain"])
            values.append({
                "name": "%s%s %s" % ("Dr. " if doctor else "", first, last),
                "is_faculty": True, "designation": title,
                "edu_department_id": dept.id,
                "specialization": dspec["specializations"][
                    (offset + i) % len(dspec["specializations"])],
                "edu_employment_type": self.rng.choices(
                    ["permanent", "contract", "visiting", "part_time"],
                    [72, 14, 9, 5])[0],
                "date_joined": joined,
                "blood_group": self.rng.choices(
                    BLOOD_GROUPS, BLOOD_WEIGHTS)[0],
                "work_email": email, "work_phone": self._next_phone(),
                "company_id": inst.company.id,
                "_doctor": doctor,
            })
        doctors = [v.pop("_doctor") for v in values]
        faculty = inst.env["hr.employee"].create(values)
        self.employee_ids += faculty.ids
        qualifications = []
        for member, doctor, vals in zip(faculty, doctors, values):
            field = vals["specialization"]
            year = self.today.year - self.rng.randint(4, 24)
            qualifications.append({
                "faculty_id": member.id, "degree": "master",
                "field_of_study": field,
                "institution": self.rng.choice(FACULTY_UNIVERSITIES),
                "year_obtained": year,
                "grade": self.rng.choice(["Distinction", "First Class",
                                          "A", "A-"]),
            })
            if doctor:
                qualifications.append({
                    "faculty_id": member.id, "degree": "phd",
                    "field_of_study": field,
                    "institution": self.rng.choice(FACULTY_UNIVERSITIES),
                    "year_obtained": year + self.rng.randint(3, 5),
                    "grade": self.rng.choice(["Summa Cum Laude",
                                              "Magna Cum Laude", "A"]),
                })
        inst.env["education.faculty.qualification"].create(qualifications)
        return faculty

    def _classes(self, inst, dept, program, pspec):
        """Create the missing sections of a program for the current year."""
        Class = inst.env["education.class"]
        existing = Class.search([
            ("program_id", "=", program.id),
            ("academic_year_id", "=", inst.year.id)])
        have = set(existing.mapped("section"))
        pool = inst.faculty[dept.id]
        values = []
        for index, section in enumerate(pspec["sections"]):
            if section in have:
                continue
            values.append({
                "program_id": program.id, "academic_year_id": inst.year.id,
                "section": section, "capacity": inst.spec["class_capacity"],
                "class_teacher_id": pool[
                    (len(inst.programs) + index) % len(pool)].id
                if pool else False,
                "notes": "%s — Section %s." % (program.name, section),
            })
        Class.create(values)

    # ── 5. Applications, students, enrollments, documents ───────────────
    def _students(self, inst):
        """Enroll students so that every class has at least ten of them."""
        low, high = inst.spec["students_per_class"]
        specs = {program.id: pspec for program, pspec, _d in inst.programs}
        for klass in inst.classes:
            wanted = self.rng.randint(low, high) - len(klass.enrollment_ids)
            if wanted > 0:
                self._enroll(inst, klass, specs.get(klass.program_id.id),
                             wanted)
        suspended = inst.new_enrollments.filtered(
            lambda e: len(e.class_id.enrollment_ids) > 12)[:2]
        suspended.write({"state": "suspended"})

    def _enrollment_date(self, inst):
        """An enrollment date within the last ~3 months.

        It is never later than the day before the attendance window
        opens (so attendance never predates the enrollment) and never
        earlier than the start of the academic year, unless the year
        only just started (early admissions).
        """
        latest = self._day(-(ATTENDANCE_DAYS + 1))
        date = latest - timedelta(days=self.rng.randint(0, 75))
        if date < inst.year.date_start:
            date = min(inst.year.date_start + timedelta(
                days=self.rng.randint(0, 10)), latest)
        return date

    def _person(self, inst, pspec):
        """Random personal data of an applicant."""
        kind = inst.spec["kind"]
        first, last, gender = self._name()
        low, high = pspec["age"] if pspec else (18, 21)
        age = self.rng.randint(low, high)
        city, zip_code = self.rng.choice(CITIES)
        person = {
            "first_name": first, "last_name": last, "gender": gender,
            "date_of_birth": self.today - relativedelta(
                years=age, days=self.rng.randint(0, 364)),
            "email": self._unique_email(
                first, last, "example.com"),
            "phone": self._next_phone(),
            "blood_group": self.rng.choices(
                BLOOD_GROUPS, BLOOD_WEIGHTS)[0],
            "address": "%d %s" % (self.rng.randint(10, 990),
                                  self.rng.choice(STREETS)),
            "city": city, "zip_code": zip_code,
            "last_percentage": round(self.rng.uniform(58, 96), 2),
        }
        if kind == "corporate":
            years = max(age - 22, 1)
            mgr_first = self.rng.choice(MALE_NAMES + FEMALE_NAMES)
            mgr_last = self.rng.choice(LAST_NAMES)
            person.update({
                "last_school": self.rng.choice(PREVIOUS_EMPLOYERS),
                "last_qualification": "%d years of professional "
                                      "experience" % years,
                "last_percentage": 0.0,
                "guardian_name": "%s %s (Reporting Manager)" % (
                    mgr_first, mgr_last),
                "guardian_relation": "other",
                "guardian_occupation": "Engineering Manager",
                "guardian_phone": self._next_phone(),
                "guardian_email": self._unique_email(
                    mgr_first, mgr_last, "example.com"),
            })
            return person
        parent_gender = self.rng.choice(["male", "female"])
        parent_pool = MALE_NAMES if parent_gender == "male" else FEMALE_NAMES
        parent_first = self.rng.choice(parent_pool)
        if kind == "school":
            last_school = self.rng.choice(PREVIOUS_SCHOOLS)
            qualification = "Grade %d Annual Report" % max(age - 6, 1)
        elif age >= 22:
            last_school = self.rng.choice(PREVIOUS_COLLEGES)
            qualification = "Bachelor's Degree"
        else:
            last_school = self.rng.choice(PREVIOUS_SCHOOLS)
            qualification = "Higher Secondary (12th)"
        person.update({
            "last_school": last_school, "last_qualification": qualification,
            "guardian_name": "%s %s" % (parent_first, last),
            "guardian_relation": "father" if parent_gender == "male"
            else "mother",
            "guardian_occupation": self.rng.choice(GUARDIAN_JOBS),
            "guardian_phone": self._next_phone(),
            "guardian_email": self._unique_email(
                parent_first, last, "example.com"),
        })
        return person

    def _application_vals(self, inst, person, program, year, state, date):
        """Values of an education.application."""
        values = dict(person)
        values.update({
            "program_id": program.id, "academic_year_id": year.id,
            "state": state, "date_application": date,
            "admission_fee": inst.spec["admission_fee"],
        })
        return values

    def _enroll(self, inst, klass, pspec, count):
        """Create ``count`` approved applications with their enrollment,
        student partner and documents in ``klass``."""
        dates = [self._enrollment_date(inst) for _i in range(count)]
        people = [self._person(inst, pspec) for _i in range(count)]
        apps = inst.env["education.application"].create([
            self._application_vals(
                inst, person, klass.program_id, klass.academic_year_id,
                "approved",
                date - timedelta(days=self.rng.randint(12, 45)))
            for person, date in zip(people, dates)])
        partners = inst.env["res.partner"].create([{
            "name": "%s %s" % (p["first_name"], p["last_name"]),
            "email": p["email"], "phone": p["phone"],
            "is_company": False, "company_id": inst.company.id,
        } for p in people])
        self.partner_ids += partners.ids
        enrollments = inst.env["education.enrollment"].create([{
            "application_id": app.id, "program_id": klass.program_id.id,
            "academic_year_id": klass.academic_year_id.id,
            "class_id": klass.id, "state": "active",
            "enrollment_date": date, "student_partner_id": partner.id,
        } for app, date, partner in zip(apps, dates, partners)])
        for app, enrollment in zip(apps, enrollments):
            app.enrollment_id = enrollment.id
        self._documents(inst, apps, enrollments)
        inst.new_enrollments |= enrollments

    def _documents(self, inst, apps, enrollments):
        """Verify / upload the mandatory documents of the new students.

        Government ID proofs get validity dates around today so that some
        are expired, some expire soon and the rest are valid; address
        proofs (optional) are short-lived utility bills.
        """
        admin = self.admin.id
        for app, enrollment in zip(apps, enrollments):
            for doc in app.document_ids:
                vals = self._document_state(doc, enrollment, admin)
                code = doc.document_type_id.code
                if code == "ID_PROOF":
                    expiry = self._day(self.rng.randint(-90, 540))
                    vals.update({
                        "issue_date": expiry - timedelta(days=3650),
                        "expiry_date": expiry})
                doc.write(vals)
            if self.rng.random() < 0.35:
                issue = self._day(-self.rng.randint(5, 85))
                vals = {
                    "document_type_id": self.env.ref(
                        "education_core.doc_type_address_proof").id,
                    "application_id": app.id,
                    "issue_date": issue,
                    "expiry_date": issue + timedelta(days=90)}
                vals.update(self._document_state(
                    self.env["education.document"], enrollment, admin,
                    force="verified", code="ADDRESS_PROOF"))
                inst.env["education.document"].create(vals)

    def _document_state(self, doc, enrollment, admin, force=None,
                        code=None):
        """Review state, attachment and verification of one document."""
        code = code or doc.document_type_id.code or "DOC"
        roll = self.rng.random()
        state = force or (
            "verified" if roll < 0.86 else "uploaded" if roll < 0.93
            else "pending" if roll < 0.97 else "rejected")
        values = {"enrollment_id": enrollment.id, "state": state}
        if state in ("verified", "uploaded"):
            photo = code == "PHOTO"
            values.update({
                "file": PNG_FILE if photo else PDF_FILE,
                "file_name": "%s_%s.%s" % (
                    code.lower(), enrollment.id, "png" if photo else "pdf"),
            })
        if state == "verified":
            values.update({
                "verified_by_id": admin,
                "verified_date": enrollment.enrollment_date + timedelta(
                    days=self.rng.randint(0, 10)),
            })
        if state == "rejected":
            values["remarks"] = ("Scan is unclear; please upload a "
                                 "readable copy.")
        return values

    # ── 6. Fresh applications around the installation date ──────────────
    def _extra_applications(self, inst):
        """Draft, submitted and rejected applications of the last weeks."""
        programs = inst.programs
        states = ["draft"] * 3 + ["submitted"] * 3 + ["rejected"] * 3
        values = []
        for index, state in enumerate(states):
            program, pspec, _dept = programs[index % len(programs)]
            date = self._day(-self.rng.randint(1, 25))
            vals = self._application_vals(
                inst, self._person(inst, pspec), program, inst.year, state,
                date)
            if state == "rejected":
                vals.update({
                    "rejection_reason": self.rng.choice([
                        "Eligibility criteria not met.",
                        "Incomplete documents submitted.",
                        "Applicant did not clear the entrance screening.",
                    ]),
                    "rejection_date": min(
                        date + timedelta(days=self.rng.randint(2, 7)),
                        self.today),
                    "rejected_by_id": self.admin.id,
                })
            values.append(vals)
        apps = inst.env["education.application"].create(values)
        for app in apps.filtered(lambda a: a.state == "submitted"):
            for doc in app.document_ids[:3]:
                doc.write({
                    "state": "uploaded", "file": PDF_FILE,
                    "file_name": "%s_%s.pdf" % (
                        (doc.document_type_id.code or "doc").lower(),
                        app.id)})

    # ── 7. Leave requests ───────────────────────────────────────────────
    def _leaves(self, inst):
        """Leave requests: approved ones in the past month (attendance is
        then 'excused'), rejected ones, and upcoming requests."""
        enrollments = inst.env["education.enrollment"].search([
            ("program_id.company_id", "=", inst.company.id),
            ("state", "=", "active")])
        total = max(12, int(len(enrollments) * 0.07))
        chosen = self.rng.sample(list(enrollments),
                                 min(total, len(enrollments)))
        plan = (["approved_past"] * (total - 9) + ["rejected_past"] * 2
                + ["submitted"] * 3 + ["draft"] * 2
                + ["approved_future"] * 2)
        types = ["medical", "personal", "family", "event", "other"]
        weights = [40, 20, 20, 15, 5]
        values = []
        for enrollment, kind in zip(chosen, plan):
            leave_type = self.rng.choices(types, weights)[0]
            length = self.rng.randint(1, 3)
            if kind in ("approved_past", "rejected_past"):
                start = self._day(-self.rng.randint(4, 27))
                end = min(start + timedelta(days=length - 1), self._day(-2))
            else:
                start = self._day(self.rng.randint(2, 18))
                end = start + timedelta(days=length - 1)
            vals = {
                "enrollment_id": enrollment.id, "leave_type": leave_type,
                "date_from": start, "date_to": end,
                "reason": self.rng.choice(LEAVE_REASONS[leave_type]),
                "state": "approved" if kind.startswith("approved") else (
                    "rejected" if kind == "rejected_past" else kind),
            }
            if vals["state"] == "approved":
                vals.update({
                    "approved_by_id": self.admin.id,
                    "approval_date": min(
                        start - timedelta(days=1), self.today)})
            if vals["state"] == "rejected":
                vals.update({
                    "approved_by_id": self.admin.id,
                    "rejection_reason": "Insufficient notice / supporting "
                                        "documents not provided.",
                    "approval_date": min(start, self.today)})
            if leave_type == "medical":
                vals.update({
                    "supporting_document": PDF_FILE,
                    "supporting_document_name": "medical_certificate.pdf"})
            if kind == "approved_past":
                day = start
                while day <= end:
                    inst.leave_days[enrollment.id].add(day)
                    day += timedelta(days=1)
            values.append(vals)
        inst.env["education.leave.request"].create(values)

    # ── 8. Timetables ───────────────────────────────────────────────────
    def _is_lab(self, subject):
        """Whether a subject is practical and needs a lab."""
        name = (subject.name or "").lower()
        return subject.code in self.lab_codes or any(
            word in name for word in ("lab", "practical", "workshop"))

    def _timetables(self, inst):
        """Published timetable for every class: Monday to Friday, with no
        teacher or room used twice in the same period."""
        Slot = inst.env["education.timetable.slot"]
        Timetable = inst.env["education.timetable"]
        periods, shifts = inst.spec["periods"], inst.spec["shifts"]
        busy_teacher, busy_room = defaultdict(set), defaultdict(set)
        for slot in Slot.search([("timetable_id.class_id", "in",
                                  inst.classes.ids)]):
            key = (int(slot.weekday), slot.period_no)
            busy_teacher[key].add(slot.teacher_id.id)
            busy_room[key].add(slot.classroom_id.id)
        class_type = self.env.ref("education_core.type_classroom")
        lab_type = self.env.ref("education_core.type_lab")
        general = inst.rooms.filtered(lambda r: r.room_type == class_type)
        labs = inst.rooms.filtered(lambda r: r.room_type == lab_type)
        company_faculty = inst.env["hr.employee"].browse(
            [f for fac in inst.faculty.values() for f in fac.ids])
        main_teacher = {}
        per_shift = defaultdict(int)
        slot_values = []
        for index, klass in enumerate(inst.classes):
            timetable = Timetable.search([
                ("class_id", "=", klass.id),
                ("academic_year_id", "=", inst.year.id)], limit=1)
            taken = {(int(s.weekday), s.period_no)
                     for s in timetable.slot_ids}
            if not timetable:
                timetable = Timetable.create({
                    "class_id": klass.id,
                    "academic_year_id": inst.year.id,
                    "state": "published",
                    "effective_from": inst.year.date_start,
                    "effective_to": inst.year.date_end,
                    "notes": "Weekly timetable of %s." % klass.display_name,
                })
            first = min((p for _d, p in taken), default=None)
            shift = next((s for s in shifts if first in s),
                         shifts[index % len(shifts)])
            shift_no = shifts.index(shift)
            home = general[per_shift[shift_no] % len(general)]
            per_shift[shift_no] += 1
            dept = klass.program_id.department_id
            pool = inst.faculty.get(dept.id) or company_faculty
            subjects = klass.program_id.subject_ids.sorted(
                lambda s: (s.sequence, s.id))
            if not subjects:
                continue
            for number, subject in enumerate(subjects):
                main_teacher.setdefault(
                    (klass.program_id.id, subject.id),
                    pool[number % len(pool)])
            for weekday in range(SCHOOL_DAYS_PER_WEEK):
                for position, period in enumerate(shift):
                    key = (weekday, period)
                    if key in taken:
                        continue
                    subject = subjects[
                        (weekday * 2 + position + index) % len(subjects)]
                    teachers = [main_teacher[(klass.program_id.id,
                                              subject.id)]] + list(
                        pool) + list(company_faculty)
                    teacher = next(
                        (t for t in teachers
                         if t.id not in busy_teacher[key]), None)
                    rooms = (list(labs) + list(general)
                             if self._is_lab(subject)
                             else [home] + list(general))
                    room = next((r for r in rooms
                                 if r.id not in busy_room[key]), None)
                    start, end = periods[period - 1]
                    slot_values.append({
                        "timetable_id": timetable.id,
                        "weekday": str(weekday), "period_no": period,
                        "start_time": start, "end_time": end,
                        "subject_id": subject.id,
                        "teacher_id": teacher.id if teacher else False,
                        "classroom_id": room.id if room else False,
                    })
                    if teacher:
                        busy_teacher[key].add(teacher.id)
                    if room:
                        busy_room[key].add(room.id)
        for start in range(0, len(slot_values), CHUNK):
            Slot.create(slot_values[start:start + CHUNK])

    # ── 9. Attendance ───────────────────────────────────────────────────
    def _attendance(self, inst):
        """One attendance record for each of the 30 days before today."""
        company = inst.company
        Attendance = inst.env["education.attendance"]
        enrollments = inst.env["education.enrollment"].search(
            [("program_id.company_id", "=", company.id)])
        first_day = self._day(-ATTENDANCE_DAYS)
        days = [first_day + timedelta(days=i)
                for i in range(ATTENDANCE_DAYS)]
        weekly_off = {5, 6} if company.working_days != "6" else {6}
        # one institution-wide holiday: the latest Wednesday that is not
        # among the last few days
        holiday = next(d for d in reversed(days[:-5]) if d.weekday() == 2)
        done = defaultdict(set)
        for rec in Attendance.search_read(
                [("enrollment_id", "in", enrollments.ids),
                 ("date", ">=", first_day)], ["enrollment_id", "date"]):
            done[rec["enrollment_id"][0]].add(rec["date"])
        values = []
        for enrollment in enrollments:
            absent_rate, late_rate = self.rng.choices(
                [(0.02, 0.03), (0.06, 0.05), (0.15, 0.08)],
                [60, 30, 10])[0]
            for day in days:
                if day in done[enrollment.id]:
                    continue
                state, note = self._attendance_state(
                    day, weekly_off, holiday, absent_rate, late_rate,
                    inst.leave_days.get(enrollment.id, ()))
                values.append({
                    "enrollment_id": enrollment.id, "date": day,
                    "state": state, "notes": note,
                    "marked_by_id": self.admin.id})
        for start in range(0, len(values), CHUNK):
            Attendance.create(values[start:start + CHUNK])
            self.env.flush_all()

    def _attendance_state(self, day, weekly_off, holiday, absent_rate,
                          late_rate, leave_days):
        """State and note of one student on one day."""
        if day.weekday() in weekly_off:
            return "holiday", "Weekly off"
        if day == holiday:
            return "holiday", "Institution holiday"
        if day in leave_days:
            return "excused", "Approved leave"
        roll = self.rng.random()
        if roll < absent_rate:
            return "absent", self.rng.choice(ABSENCE_NOTES)
        if roll < absent_rate + late_rate:
            return "late", self.rng.choice(LATE_NOTES)
        return "present", False

    def register_xml_ids(self):
        """Give the generated student partners and faculty an xml id, so
        that uninstalling the module removes them like the XML demo."""
        values = [
            {"module": "education_core", "noupdate": True,
             "name": "demo_%s_%d" % (prefix, res_id), "model": model,
             "res_id": res_id}
            for prefix, model, ids in (
                ("student", "res.partner", self.partner_ids),
                ("faculty", "hr.employee", self.employee_ids))
            for res_id in ids]
        self.env["ir.model.data"].sudo().create(values)

    # ── 10. Administrator ───────────────────────────────────────────────
    def _link_administrator(self):
        """Allow the default administrator to work in every institution."""
        companies = self.env["res.company"]
        for spec in INSTITUTIONS:
            companies |= self.env.ref(spec["company"])
        self.admin.write({
            "company_ids": [Command.link(c.id) for c in companies]})
