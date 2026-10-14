
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
"""Static specification of the Education Core demo data.

Everything that is *data* (institutions, departments, programs, subjects,
classrooms, name pools ...) lives here; the logic that turns it into
records is in ``education_demo_data.py``.

Existing records of ``demo/education_core_demo.xml`` are referenced by
their xml id (``xmlid``) and topped up; everything else is created.
"""

# ── Name pools ────────────────────────────────────────────────────────────
MALE_NAMES = [
    "Liam", "Noah", "Oliver", "Elijah", "James", "William", "Benjamin",
    "Lucas", "Henry", "Alexander", "Mason", "Ethan", "Daniel", "Jacob",
    "Logan", "Jackson", "Levi", "Sebastian", "Mateo", "Jack", "Owen",
    "Theodore", "Aiden", "Samuel", "Joseph", "Wyatt", "Matthew", "Luke",
    "Asher", "Carter", "Julian", "Grayson", "Leo", "Gabriel", "Isaac",
    "Lincoln", "Anthony", "Hudson", "Dylan", "Ezra", "Thomas", "Charles",
    "Josiah", "Andrew", "Elias", "Joshua", "Nathan", "Caleb", "Ryan",
    "Adrian", "Miles", "Eli", "Nolan", "Aaron", "Cameron", "Arjun",
    "Rohan", "Vikram", "Aarav", "Karan", "Imran", "Omar", "Hiro", "Wei",
]
FEMALE_NAMES = [
    "Olivia", "Emma", "Charlotte", "Amelia", "Sophia", "Isabella", "Ava",
    "Mia", "Evelyn", "Luna", "Harper", "Camila", "Sofia", "Scarlett",
    "Elizabeth", "Eleanor", "Emily", "Chloe", "Mila", "Violet", "Penelope",
    "Gianna", "Aria", "Abigail", "Ella", "Avery", "Hazel", "Nora", "Layla",
    "Lily", "Addison", "Aurora", "Natalie", "Zoey", "Grace", "Leah",
    "Hannah", "Lillian", "Victoria", "Riley", "Brooklyn", "Savannah",
    "Zoe", "Stella", "Maya", "Paisley", "Naomi", "Elena", "Priya",
    "Ananya", "Diya", "Meera", "Fatima", "Yuki", "Mei", "Aisha", "Sana",
    "Isla", "Ruby", "Clara", "Freya",
]
LAST_NAMES = [
    "Smith", "Johnson", "Williams", "Brown", "Jones", "Garcia", "Miller",
    "Davis", "Rodriguez", "Martinez", "Hernandez", "Lopez", "Gonzalez",
    "Wilson", "Anderson", "Thomas", "Taylor", "Moore", "Jackson", "Martin",
    "Lee", "Perez", "Thompson", "White", "Harris", "Sanchez", "Clark",
    "Ramirez", "Lewis", "Robinson", "Walker", "Young", "Allen", "King",
    "Wright", "Scott", "Torres", "Nguyen", "Hill", "Flores", "Green",
    "Adams", "Nelson", "Baker", "Hall", "Rivera", "Campbell", "Mitchell",
    "Carter", "Roberts", "Patel", "Sharma", "Kumar", "Singh", "Gupta",
    "Reddy", "Nair", "Iyer", "Chen", "Wang", "Kim", "Park", "Tanaka",
    "Sato", "Khan", "Hussain", "Ali", "Ahmed", "Cohen", "Fischer", "Rossi",
    "Dubois", "Silva", "Costa", "Novak", "Kowalski", "Ivanov", "Petrov",
]
CITIES = [
    ("Boston", "02108"), ("Chicago", "60601"), ("Austin", "73301"),
    ("Seattle", "98101"), ("Denver", "80202"), ("Atlanta", "30303"),
    ("Portland", "97201"), ("San Diego", "92101"), ("Columbus", "43215"),
    ("Raleigh", "27601"), ("Madison", "53703"), ("Pittsburgh", "15222"),
]
STREETS = [
    "Maple Street", "Oak Avenue", "Cedar Lane", "Pine Road", "Elm Court",
    "Lakeview Drive", "Sunset Boulevard", "Willow Way", "Hillcrest Road",
    "Riverside Avenue", "Park Lane", "Orchard Street",
]
BLOOD_GROUPS = ["a+", "a-", "b+", "b-", "ab+", "ab-", "o+", "o-"]
BLOOD_WEIGHTS = [28, 3, 22, 3, 6, 1, 34, 3]
GUARDIAN_JOBS = [
    "Software Engineer", "Accountant", "Civil Engineer", "Teacher",
    "Physician", "Business Owner", "Bank Manager", "Nurse", "Architect",
    "Sales Manager", "Electrician", "Pharmacist", "Lawyer", "Government "
    "Officer", "Chef", "Logistics Supervisor",
]
ABSENCE_NOTES = [
    "Fever", "Family function", "Not informed", "Medical appointment",
    "Travel", "Unwell", "Personal reasons",
]
LATE_NOTES = [
    "Traffic delay", "Missed the bus", "Arrived after first period",
    "Late arrival", "Transport delay",
]
LEAVE_REASONS = {
    "medical": [
        "Viral fever and cold; rest advised by the doctor.",
        "Dental procedure and recovery.",
        "Routine medical check-up and lab tests.",
        "Minor injury; doctor advised rest.",
    ],
    "personal": [
        "Personal work that cannot be postponed.",
        "Visa and documentation appointment.",
        "Attending a relative's wedding.",
    ],
    "family": [
        "Family function out of town.",
        "Family emergency; need to travel.",
        "Caring for a family member.",
    ],
    "event": [
        "Representing the institution at an inter-college event.",
        "Participation in a regional hackathon.",
        "Attending a professional conference.",
    ],
    "other": [
        "Court summons for a civic duty.",
        "Driving licence test appointment.",
    ],
}
PREVIOUS_SCHOOLS = [
    "Riverdale High School", "Lakeside Academy", "Central Public School",
    "St. Mary's Convent School", "Hillcrest Senior Secondary School",
    "Sunrise International School", "Oakwood Preparatory School",
    "Northfield High School", "Springdale Public School",
    "Westbridge Academy", "Maplewood Junior High", "Cedar Valley School",
]
PREVIOUS_COLLEGES = [
    "State Technical University", "Lakeview College of Engineering",
    "Metropolitan University", "Riverside Institute of Technology",
    "Northern Business School", "Heritage College", "City University",
]
PREVIOUS_EMPLOYERS = [
    "Orbit Systems", "BlueStone Consulting", "Helix Software",
    "Northwind Logistics", "Pinnacle Financial", "Quantum Retail Group",
    "Summit Healthcare IT", "Vertex Telecom", "Atlas Manufacturing",
    "Redwood Insurance", "Cobalt Energy", "Nimbus Cloud Services",
]
FACULTY_UNIVERSITIES = [
    "Princeton University", "Stanford University", "MIT",
    "University of Michigan", "Georgia Tech", "Carnegie Mellon University",
    "University of Texas at Austin", "Purdue University",
    "University of Illinois", "Columbia University", "Cornell University",
]

# ── Subject helper ────────────────────────────────────────────────────────
# (code, name, is_lab)


def _s(code, name, lab=False):
    """Return a subject tuple (code, name, is_practical)."""
    return (code, name, lab)


# ── College / Institute ──────────────────────────────────────────────────
COLLEGE = {
    "key": "college",
    "company": "base.main_company",
    "email_domain": "apex-institute.edu",
    "contact": {
        "phone": "+1 555-0100",
        "mobile": "+1 555-0199",
        "email": "admissions@apex-institute.edu",
        "website": "https://www.apex-institute.edu",
    },
    "kind": "college",
    "class_capacity": 60,
    "students_per_class": (11, 14),
    "admission_fee": 150.0,
    "titles": [
        "Professor", "Associate Professor", "Assistant Professor",
        "Senior Lecturer",
    ],
    "periods": [
        (9.0, 10.0), (10.0, 11.0), (11.0, 12.0), (12.0, 13.0),
        (14.0, 15.0), (15.0, 16.0), (16.0, 17.0), (17.0, 18.0),
    ],
    "shifts": [[1, 2, 3, 4], [5, 6, 7, 8]],
    "classrooms": [
        # (room_no, block, floor, capacity, type xml id)
        ("301", "Block B", "3rd Floor", 60, "type_classroom"),
        ("302", "Block B", "3rd Floor", 60, "type_classroom"),
        ("303", "Block B", "3rd Floor", 60, "type_classroom"),
        ("304", "Block B", "3rd Floor", 60, "type_classroom"),
        ("401", "Block B", "4th Floor", 60, "type_classroom"),
        ("402", "Block B", "4th Floor", 60, "type_classroom"),
        ("403", "Block B", "4th Floor", 60, "type_classroom"),
        ("404", "Block B", "4th Floor", 60, "type_classroom"),
        ("ECE-LAB-1", "Electronics Block", "Ground Floor", 40, "type_lab"),
        ("ECE-LAB-2", "Electronics Block", "Ground Floor", 40, "type_lab"),
        ("VLSI-LAB-1", "Electronics Block", "1st Floor", 30, "type_lab"),
        ("MECH-WS-1", "Workshop Block", "Ground Floor", 40, "type_lab"),
        ("MECH-WS-2", "Workshop Block", "Ground Floor", 40, "type_lab"),
        ("SEM-HALL-2", "Admin Block", "2nd Floor", 100, "type_seminar"),
        ("AUD-1", "Admin Block", "Ground Floor", 400, "type_auditorium"),
        ("EXAM-HALL-1", "Admin Block", "1st Floor", 120, "type_exam_hall"),
    ],
    "departments": [
        {
            "xmlid": "dept_cse",
            "name": "Computer Science & Engineering", "code": "CSE",
            "faculty_target": 5,
            "specializations": [
                "Artificial Intelligence & Machine Learning",
                "Distributed Systems & Cloud Computing",
                "Database Systems & Data Mining",
                "Cybersecurity & Cryptography",
                "Software Engineering & Agile Methods",
            ],
            "programs": [
                {
                    "xmlid": "prog_btech_cs", "sections": ["A", "B"],
                    "age": (18, 20), "extra_subjects": [],
                },
                {
                    "xmlid": "prog_mtech_ai", "sections": ["A", "B"],
                    "age": (22, 25),
                    "extra_subjects": [
                        _s("AI203", "Natural Language Processing"),
                        _s("AI204", "Computer Vision & Image Analytics",
                           True),
                        _s("AI205", "Reinforcement Learning & Robotics",
                           True),
                    ],
                },
            ],
        },
        {
            "xmlid": "dept_mbs",
            "name": "Management & Business Studies", "code": "MBS",
            "faculty_target": 4,
            "specializations": [
                "Corporate Finance & Investment Banking",
                "Marketing & Consumer Behavior",
                "Operations & Supply Chain Management",
                "Human Resources & Organizational Behavior",
            ],
            "programs": [
                {
                    "xmlid": "prog_mba", "sections": ["A", "B"],
                    "age": (23, 28),
                    "extra_subjects": [
                        _s("MBA103", "Marketing Management & Consumer "
                           "Insight"),
                        _s("MBA104", "Operations & Supply Chain "
                           "Management"),
                        _s("MBA105", "Business Analytics & Decision "
                           "Science", True),
                    ],
                },
                {
                    "xmlid": None,
                    "name": "Bachelor of Business Administration",
                    "code": "BBA", "degree": "bachelor", "years": 3,
                    "semesters": 2, "sections": ["A", "B"],
                    "age": (18, 20),
                    "eligibility": "10+2 in any stream with minimum 55% "
                                   "aggregate marks.",
                    "description": "Foundation program in management, "
                                   "accounting, economics and "
                                   "entrepreneurship.",
                    "extra_subjects": [
                        _s("BB101", "Principles of Management"),
                        _s("BB102", "Financial Accounting"),
                        _s("BB103", "Business Economics"),
                        _s("BB104", "Business Communication"),
                        _s("BB105", "Marketing Fundamentals"),
                    ],
                },
            ],
        },
        {
            "xmlid": None,
            "name": "Electronics & Communication Engineering",
            "code": "ECE",
            "description": "Electronics, communication systems, embedded "
                           "systems and VLSI design.",
            "faculty_target": 4,
            "specializations": [
                "VLSI Design & Embedded Systems",
                "Wireless & Mobile Communication",
                "Signal Processing & Image Analysis",
                "Power Electronics & Control Systems",
            ],
            "programs": [
                {
                    "xmlid": None,
                    "name": "Bachelor of Technology — Electronics & "
                            "Communication",
                    "code": "BTECH-ECE", "degree": "bachelor", "years": 4,
                    "semesters": 2, "sections": ["A", "B"],
                    "age": (18, 20),
                    "eligibility": "10+2 with Physics, Mathematics and "
                                   "Chemistry with minimum 60% aggregate.",
                    "description": "Undergraduate program in analog and "
                                   "digital electronics, communication "
                                   "systems and embedded design.",
                    "extra_subjects": [
                        _s("EC101", "Basic Electrical & Electronics "
                           "Engineering"),
                        _s("EC102", "Network Analysis & Circuit Theory"),
                        _s("EC103", "Analog Electronic Circuits", True),
                        _s("EC104", "Digital Logic Design & "
                           "Microprocessors", True),
                        _s("EC105", "Signals & Systems"),
                        _s("EC106", "Electromagnetic Field Theory"),
                    ],
                },
                {
                    "xmlid": None,
                    "name": "Master of Technology — VLSI & Embedded "
                            "Systems",
                    "code": "MTECH-VLSI", "degree": "master", "years": 2,
                    "semesters": 2, "sections": ["A", "B"],
                    "age": (22, 25),
                    "eligibility": "B.Tech / B.E. in Electronics or "
                                   "allied branch with minimum 60%.",
                    "description": "Postgraduate program in CMOS design, "
                                   "embedded architectures and hardware "
                                   "security.",
                    "extra_subjects": [
                        _s("VL201", "CMOS VLSI Design", True),
                        _s("VL202", "Embedded Systems Architecture"),
                        _s("VL203", "Digital System Design with HDL", True),
                        _s("VL204", "Low-Power VLSI Design"),
                        _s("VL205", "Hardware Security & Testing"),
                    ],
                },
            ],
        },
        {
            "xmlid": None,
            "name": "Mechanical & Automation Engineering",
            "code": "MECH",
            "description": "Mechanical design, manufacturing, robotics "
                           "and industrial automation.",
            "faculty_target": 4,
            "specializations": [
                "Thermal Engineering & Energy Systems",
                "Manufacturing & Industrial Engineering",
                "Robotics & Mechatronics",
                "Machine Design & CAD/CAM",
            ],
            "programs": [
                {
                    "xmlid": None,
                    "name": "Bachelor of Technology — Mechanical "
                            "Engineering",
                    "code": "BTECH-ME", "degree": "bachelor", "years": 4,
                    "semesters": 2, "sections": ["A", "B"],
                    "age": (18, 20),
                    "eligibility": "10+2 with Physics, Mathematics and "
                                   "Chemistry with minimum 60% aggregate.",
                    "description": "Undergraduate program in design, "
                                   "thermal sciences and manufacturing.",
                    "extra_subjects": [
                        _s("ME101", "Engineering Mechanics"),
                        _s("ME102", "Thermodynamics"),
                        _s("ME103", "Fluid Mechanics & Machinery", True),
                        _s("ME104", "Manufacturing Processes", True),
                        _s("ME105", "Strength of Materials"),
                        _s("ME106", "Engineering Drawing & CAD", True),
                    ],
                },
                {
                    "xmlid": None,
                    "name": "Diploma in Industrial Automation",
                    "code": "DIP-AUTO", "degree": "diploma", "years": 3,
                    "semesters": 2, "sections": ["A", "B"],
                    "age": (17, 19),
                    "eligibility": "10th pass with Mathematics and "
                                   "Science.",
                    "description": "Hands-on diploma in PLC programming, "
                                   "instrumentation and robotics basics.",
                    "extra_subjects": [
                        _s("AU101", "Industrial Automation & PLC "
                           "Programming", True),
                        _s("AU102", "Hydraulics & Pneumatics", True),
                        _s("AU103", "Sensors & Instrumentation"),
                        _s("AU104", "Robotics & Mechatronics Basics"),
                        _s("AU105", "Workshop Practice & Safety", True),
                    ],
                },
            ],
        },
    ],
}

# ── School (K-12) ─────────────────────────────────────────────────────────
SCHOOL = {
    "key": "school",
    "company": "education_core.company_school",
    "email_domain": "greenwood.k12.edu",
    "contact": {
        "phone": "+1 555-0200",
        "mobile": "+1 555-0299",
        "email": "office@greenwood.k12.edu",
        "website": "https://www.greenwood-school.edu",
    },
    "kind": "school",
    "class_capacity": 40,
    "students_per_class": (11, 14),
    "admission_fee": 75.0,
    "titles": [
        "Senior Teacher", "Post Graduate Teacher", "Trained Graduate "
        "Teacher", "Subject Coordinator",
    ],
    "periods": [
        (8.5, 9.5), (9.5, 10.5), (10.75, 11.75), (11.75, 12.75),
        (13.25, 14.25), (14.25, 15.25), (15.25, 16.0),
    ],
    "shifts": [[1, 2, 3, 4, 5, 6]],
    "classrooms": [
        ("102", "Main Building", "1st Floor", 40, "type_classroom"),
        ("103", "Main Building", "1st Floor", 40, "type_classroom"),
        ("104", "Main Building", "1st Floor", 40, "type_classroom"),
        ("105", "Main Building", "1st Floor", 40, "type_classroom"),
        ("106", "Main Building", "1st Floor", 40, "type_classroom"),
        ("202", "Main Building", "2nd Floor", 40, "type_classroom"),
        ("203", "Main Building", "2nd Floor", 40, "type_classroom"),
        ("204", "Main Building", "2nd Floor", 40, "type_classroom"),
        ("205", "Main Building", "2nd Floor", 40, "type_classroom"),
        ("206", "Main Building", "2nd Floor", 40, "type_classroom"),
        ("301", "Main Building", "3rd Floor", 40, "type_classroom"),
        ("302", "Main Building", "3rd Floor", 40, "type_classroom"),
        ("Physics-Lab", "Science Wing", "Ground Floor", 40, "type_lab"),
        ("Chemistry-Lab", "Science Wing", "Ground Floor", 40, "type_lab"),
        ("Biology-Lab", "Science Wing", "1st Floor", 40, "type_lab"),
        ("Computer-Lab", "Science Wing", "1st Floor", 40, "type_lab"),
        ("Art-Studio", "Arts Wing", "Ground Floor", 40, "type_lab"),
        ("Music-Room", "Arts Wing", "1st Floor", 40, "type_lab"),
        ("Sports-Hall", "Sports Complex", "Ground Floor", 200,
         "type_seminar"),
        ("Exam Hall", "Main Building", "Ground Floor", 120,
         "type_exam_hall"),
    ],
    "departments": [
        {
            "xmlid": "dept_sch_science",
            "name": "Natural Sciences & Mathematics", "code": "SCI",
            "faculty_target": 5,
            "specializations": [
                "Mathematics", "Physics", "Chemistry", "Biology",
                "Computer Science",
            ],
            "programs": [
                {
                    "xmlid": "prog_sch_high", "sections": ["A", "B"],
                    "age": (14, 16),
                    "extra_subjects": [
                        _s("SCH-IT10", "Grade 10 Computer Applications",
                           True),
                    ],
                },
                {
                    "xmlid": "prog_sch_senior_sci",
                    "sections": ["A", "B"], "age": (16, 18),
                    "extra_subjects": [
                        _s("SCH-CHE11", "Grade 11 Chemistry", True),
                        _s("SCH-BIO11", "Grade 11 Biology", True),
                        _s("SCH-MAT11", "Grade 11 Mathematics"),
                        _s("SCH-ENG11", "Grade 11 English Core"),
                    ],
                },
            ],
        },
        {
            "xmlid": "dept_sch_humanities",
            "name": "Languages & Social Studies", "code": "HUM",
            "faculty_target": 5,
            "specializations": [
                "English Literature", "Second Language (Spanish)",
                "History & Civics", "Geography & Economics",
                "Political Science",
            ],
            "programs": [
                {
                    "xmlid": None,
                    "name": "Middle School Languages & Humanities "
                            "(Grades 6-8)",
                    "code": "SCH-G6-8", "degree": "other", "years": 3,
                    "semesters": 2, "sections": ["A", "B"],
                    "age": (11, 13),
                    "eligibility": "Completion of Grade 5 with minimum "
                                   "50% marks.",
                    "description": "Middle school curriculum focusing on "
                                   "language, humanities and life skills.",
                    "extra_subjects": [
                        _s("SCH-ENG6", "Grade 6-8 English Language & "
                           "Literature"),
                        _s("SCH-SPA6", "Grade 6-8 Spanish Language"),
                        _s("SCH-HIS6", "Grade 6-8 History & Civics"),
                        _s("SCH-GEO6", "Grade 6-8 Geography"),
                        _s("SCH-MOR6", "Grade 6-8 Life Skills & Ethics"),
                    ],
                },
                {
                    "xmlid": None,
                    "name": "Senior Secondary Commerce & Humanities "
                            "Stream (Grades 11-12)",
                    "code": "SCH-G11-COM", "degree": "other", "years": 2,
                    "semesters": 2, "sections": ["A", "B"],
                    "age": (16, 18),
                    "eligibility": "Grade 10 pass with minimum 60% marks.",
                    "description": "Commerce and humanities stream "
                                   "preparing students for higher studies.",
                    "extra_subjects": [
                        _s("SCH-ACC11", "Grade 11 Accountancy"),
                        _s("SCH-BUS11", "Grade 11 Business Studies"),
                        _s("SCH-ECO11", "Grade 11 Economics"),
                        _s("SCH-POL11", "Grade 11 Political Science"),
                        _s("SCH-ENG11C", "Grade 11 English Core "
                           "(Commerce)"),
                    ],
                },
            ],
        },
        {
            "xmlid": None,
            "name": "Arts, Sports & Wellbeing", "code": "ASW",
            "description": "Visual and performing arts, sports and "
                           "student wellbeing programs.",
            "faculty_target": 4,
            "specializations": [
                "Visual Arts & Design", "Music & Performing Arts",
                "Physical Education & Sports Science",
                "Yoga & Student Wellbeing",
            ],
            "programs": [
                {
                    "xmlid": None,
                    "name": "Visual & Performing Arts Programme "
                            "(Grades 6-10)",
                    "code": "SCH-ARTS", "degree": "certificate",
                    "years": 3, "semesters": 2, "sections": ["A", "B"],
                    "age": (11, 15),
                    "eligibility": "Open to all students; audition "
                                   "recommended.",
                    "description": "Co-curricular arts track covering "
                                   "painting, music, dance and drama.",
                    "extra_subjects": [
                        _s("ART-DRW", "Drawing & Painting", True),
                        _s("ART-MUS", "Music — Vocal & Instrumental",
                           True),
                        _s("ART-DAN", "Dance & Drama", True),
                        _s("ART-CRF", "Craft & Design Thinking", True),
                        _s("ART-HIS", "Art History & Appreciation"),
                    ],
                },
                {
                    "xmlid": None,
                    "name": "Sports & Wellness Excellence Programme "
                            "(Grades 6-10)",
                    "code": "SCH-SPORT", "degree": "certificate",
                    "years": 3, "semesters": 2, "sections": ["A", "B"],
                    "age": (11, 15),
                    "eligibility": "Fitness assessment and parental "
                                   "consent.",
                    "description": "Structured athletics, team sports and "
                                   "wellness training.",
                    "extra_subjects": [
                        _s("SPT-ATH", "Athletics & Track Events", True),
                        _s("SPT-TEM", "Team Sports — Football & "
                           "Basketball", True),
                        _s("SPT-YOG", "Yoga & Mindfulness", True),
                        _s("SPT-SCI", "Sports Science & Nutrition"),
                        _s("SPT-SWM", "Swimming & Water Safety", True),
                    ],
                },
            ],
        },
    ],
}

# ── Corporate Training Centre ────────────────────────────────────────────
CORPORATE = {
    "key": "corporate",
    "company": "education_core.company_corporate",
    "email_domain": "nexgen-academy.corp",
    "contact": {
        "phone": "+1 555-0300",
        "mobile": "+1 555-0399",
        "email": "enroll@nexgen-academy.corp",
        "website": "https://www.nexgen-academy.corp",
    },
    "kind": "corporate",
    "class_capacity": 30,
    "students_per_class": (11, 14),
    "admission_fee": 0.0,
    "titles": [
        "Principal Trainer", "Senior Trainer", "Lead Instructor",
        "Certified Trainer",
    ],
    "periods": [
        (9.0, 11.0), (11.0, 13.0), (14.0, 16.0), (16.0, 18.0),
    ],
    "shifts": [[1, 2], [3, 4]],
    "classrooms": [
        ("Training Room 1", "Learning Centre", "1st Floor", 30,
         "type_classroom"),
        ("Training Room 2", "Learning Centre", "1st Floor", 30,
         "type_classroom"),
        ("Training Room 3", "Learning Centre", "2nd Floor", 30,
         "type_classroom"),
        ("Training Room 4", "Learning Centre", "2nd Floor", 30,
         "type_classroom"),
        ("Cloud-Sandbox-2", "Tech Lab Wing", "Ground Floor", 30,
         "type_lab"),
        ("Cyber-Range-Lab", "Tech Lab Wing", "Ground Floor", 30,
         "type_lab"),
        ("Data-Lab-1", "Tech Lab Wing", "1st Floor", 30, "type_lab"),
        ("Boardroom", "Learning Centre", "3rd Floor", 20, "type_seminar"),
        ("Workshop Hall B", "Learning Centre", "Ground Floor", 60,
         "type_seminar"),
    ],
    "departments": [
        {
            "xmlid": "dept_corp_cloud",
            "name": "Cloud Engineering & Architecture", "code": "CLOUD",
            "faculty_target": 4,
            "specializations": [
                "Cloud Architecture & Migration",
                "Kubernetes & Container Platforms",
                "Site Reliability Engineering",
                "Infrastructure Automation",
            ],
            "programs": [
                {
                    "xmlid": "prog_corp_cloud", "sections": ["Q1", "Q2"],
                    "age": (26, 42),
                    "extra_subjects": [
                        _s("CLD-SEC", "Cloud Security & Identity "
                           "Management", True),
                        _s("CLD-SVL", "Serverless & Microservices "
                           "Architecture", True),
                        _s("CLD-IAC", "Infrastructure as Code with "
                           "Terraform", True),
                    ],
                },
                {
                    "xmlid": None,
                    "name": "DevOps & Site Reliability Engineering "
                            "Bootcamp",
                    "code": "CORP-SRE", "degree": "corporate", "years": 1,
                    "semesters": 2, "sections": ["Q1", "Q2"],
                    "age": (25, 40),
                    "eligibility": "2+ years of IT operations or "
                                   "development experience.",
                    "description": "Intensive bootcamp on automation, "
                                   "observability and reliability.",
                    "extra_subjects": [
                        _s("SRE-LNX", "Linux Systems & Shell Automation",
                           True),
                        _s("SRE-CICD", "CI/CD with Jenkins & GitHub "
                           "Actions", True),
                        _s("SRE-K8S", "Containers & Kubernetes "
                           "Operations", True),
                        _s("SRE-OBS", "Observability & Incident "
                           "Response", True),
                        _s("SRE-CHA", "Chaos Engineering & Reliability "
                           "Patterns"),
                    ],
                },
            ],
        },
        {
            "xmlid": "dept_corp_agile",
            "name": "Enterprise Leadership & Agile Transformation",
            "code": "AGILE",
            "faculty_target": 3,
            "specializations": [
                "Executive Coaching & Leadership",
                "Agile Transformation at Scale",
                "Product Management",
            ],
            "programs": [
                {
                    "xmlid": "prog_corp_agile", "sections": ["Q1", "Q2"],
                    "age": (28, 48),
                    "extra_subjects": [
                        _s("AGL-PRT", "Lean Portfolio & OKR Management"),
                        _s("AGL-PO", "Product Ownership & Backlog "
                           "Strategy"),
                        _s("AGL-COA", "Coaching Skills for Agile "
                           "Leaders"),
                    ],
                },
                {
                    "xmlid": None,
                    "name": "Executive Leadership & Change Management",
                    "code": "CORP-ELC", "degree": "corporate", "years": 1,
                    "semesters": 2, "sections": ["Q1", "Q2"],
                    "age": (32, 52),
                    "eligibility": "5+ years of people-management "
                                   "experience.",
                    "description": "Leadership development for managers "
                                   "leading large-scale change.",
                    "extra_subjects": [
                        _s("ELC-CHG", "Leading Through Change"),
                        _s("ELC-DEC", "Strategic Decision Making"),
                        _s("ELC-TEA", "High-Performance Team Building"),
                        _s("ELC-NEG", "Negotiation & Stakeholder "
                           "Influence"),
                        _s("ELC-PRE", "Executive Presence & "
                           "Communication"),
                    ],
                },
            ],
        },
        {
            "xmlid": None,
            "name": "Data, AI & Cybersecurity", "code": "DAS",
            "description": "Data engineering, analytics and "
                           "cybersecurity professional programs.",
            "faculty_target": 4,
            "specializations": [
                "Data Engineering & Analytics",
                "Applied Machine Learning",
                "Security Operations & Threat Detection",
                "Governance, Risk & Compliance",
            ],
            "programs": [
                {
                    "xmlid": None,
                    "name": "Data Engineering & Analytics Professional",
                    "code": "CORP-DEA", "degree": "corporate", "years": 1,
                    "semesters": 2, "sections": ["Q1", "Q2"],
                    "age": (25, 42),
                    "eligibility": "Working knowledge of SQL and one "
                                   "programming language.",
                    "description": "Professional track on pipelines, "
                                   "warehousing and analytics delivery.",
                    "extra_subjects": [
                        _s("DEA-SQL", "SQL & Data Modeling", True),
                        _s("DEA-ETL", "ETL Pipelines & Spark", True),
                        _s("DEA-DWH", "Data Warehousing & Lakehouse"),
                        _s("DEA-VIZ", "Data Visualization & Storytelling",
                           True),
                        _s("DEA-MLO", "MLOps Foundations"),
                    ],
                },
                {
                    "xmlid": None,
                    "name": "Cybersecurity & Compliance Specialist",
                    "code": "CORP-CSC", "degree": "corporate", "years": 1,
                    "semesters": 2, "sections": ["Q1", "Q2"],
                    "age": (26, 45),
                    "eligibility": "Background in IT infrastructure or "
                                   "software development.",
                    "description": "Hands-on program covering SOC "
                                   "operations, cloud security and "
                                   "compliance.",
                    "extra_subjects": [
                        _s("CSC-NET", "Network & Application Security",
                           True),
                        _s("CSC-SOC", "Threat Detection & SOC Operations",
                           True),
                        _s("CSC-CSP", "Cloud Security Posture "
                           "Management", True),
                        _s("CSC-GRC", "Governance, Risk & Compliance "
                           "(ISO 27001)"),
                        _s("CSC-IR", "Incident Response & Forensics",
                           True),
                    ],
                },
            ],
        },
    ],
}

INSTITUTIONS = [COLLEGE, SCHOOL, CORPORATE]
