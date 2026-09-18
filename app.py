from flask import (
    Flask,
    render_template,
    request,
    redirect,
    url_for,
    session,
    jsonify,
    send_file,
    flash
)

import sqlite3
import os
from datetime import datetime
from reportlab.lib import colors
from reportlab.lib.pagesizes import A4, landscape
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.enums import TA_CENTER
from reportlab.platypus import (
    SimpleDocTemplate,
    Table,
    TableStyle,
    Paragraph,
    Spacer
)

app = Flask(__name__)

app.secret_key = os.environ.get(
    "SECRET_KEY",
    "change-this-secret-key"
)

DATABASE = "database.db"

# ---------------------------------------------------------
# CONFIGURATION
# ---------------------------------------------------------

# Change this number depending on the number of registered
# teams for your event.
TOTAL_TEAMS = int(os.environ.get("TOTAL_TEAMS", "40"))

# Maximum teams allowed for one problem statement
MAX_TEAMS_PER_PROBLEM = 2

# Admin password
ADMIN_PASSWORD = os.environ.get(
    "ADMIN_PASSWORD",
    "admin123"
)

# ---------------------------------------------------------
# PROBLEM STATEMENTS
# ---------------------------------------------------------

PROBLEMS = [
    {
        "code": "PS01",
        "title": "Smarter Resume Creation and Analysis",
        "description": """Students and job seekers often struggle to create professional resumes and understand whether their resumes are suitable for specific job roles. Develop a solution that helps users create structured resumes and analyze them based on skills, keywords, formatting, and job requirements."""
    },
    {
        "code": "PS02",
        "title": "Early Crop Disease Identification",
        "description": """Crop diseases can significantly affect agricultural productivity when they are not identified at an early stage. Develop a solution that helps users identify possible crop diseases from leaf or crop images and provides useful information to support early action."""
    },
    {
        "code": "PS03",
        "title": "Automated Crop Pest Identification",
        "description": """Farmers may find it difficult to identify pests affecting their crops, especially when the symptoms are not easily distinguishable. Develop a solution that identifies possible pests from crop images and provides relevant information to help users understand the infestation."""
    },
    {
        "code": "PS04",
        "title": "Automated Personal Portfolio Creation",
        "description": """Students and professionals often find it difficult to design and maintain an effective online portfolio that presents their skills, achievements, and work. Develop a solution that converts user-provided information into a structured and responsive personal portfolio."""
    },
    {
        "code": "PS05",
        "title": "Intelligent Waste Segregation",
        "description": """Improper segregation of waste at the source creates difficulties in recycling and waste management. Develop a solution that identifies the type of waste from an image or user input and guides users toward the appropriate waste category and disposal method."""
    },
    {
        "code": "PS06",
        "title": "Efficient Queue Management",
        "description": """People often spend considerable time waiting in queues at hospitals, banks, service centres, and other public facilities. Develop a solution that digitally manages queues, allows users to track their position, and helps reduce unnecessary waiting and overcrowding."""
    },
    {
        "code": "PS07",
        "title": "Automated Complaint Prioritization",
        "description": """Organizations receive numerous complaints, but identifying which issues require immediate attention can be challenging. Develop a solution that analyzes incoming complaints, categorizes them, assigns suitable priority levels, and helps organizations manage them efficiently."""
    },
    {
        "code": "PS08",
        "title": "Hands-Free Computer Interaction Using Eye Movement",
        "description": """Traditional mouse-based computer interaction can be difficult for users who have limited hand mobility. Develop a hands-free interaction solution that uses eye movement captured through a camera to perform basic computer operations such as cursor movement and selection."""
    },
    {
        "code": "PS09",
        "title": "Gesture-Based Computer Interaction",
        "description": """Users may need alternative methods of interacting with computers without relying on a physical mouse. Develop a solution that recognizes predefined hand gestures through a camera and converts them into basic mouse operations such as movement, clicking, and scrolling."""
    },
    {
        "code": "PS10",
        "title": "Intelligent Online Exam Monitoring",
        "description": """Conducting examinations remotely makes it challenging to monitor suspicious activities consistently. Develop a solution that analyzes webcam input for predefined indicators such as multiple faces, prolonged absence from the camera, or unusual head movements and presents the observations for review."""
    },
    {
        "code": "PS11",
        "title": "Automated Attendance Using Facial Recognition",
        "description": """Manual attendance recording consumes time and can result in errors or proxy attendance. Develop a solution that identifies registered individuals using facial recognition, automatically records their attendance, and maintains an accessible attendance record."""
    },
    {
        "code": "PS12",
        "title": "Automatic Image Understanding",
        "description": """People may need textual descriptions of images for accessibility, documentation, or content understanding. Develop a solution that analyzes an image and generates a meaningful natural-language description of the important objects, actions, and context present in it."""
    },
    {
        "code": "PS13",
        "title": "Automated Scenario Analysis and Reporting",
        "description": """Analyzing complex scenarios and preparing structured reports can require significant manual effort. Develop a solution that accepts a scenario or set of inputs, identifies important observations, summarizes the situation, and generates a structured report with relevant findings."""
    },
    {
        "code": "PS14",
        "title": "Real-Time Event Crowd Monitoring",
        "description": """Large events can experience overcrowding in specific areas, making it difficult for organizers to respond quickly. Develop a solution that analyzes available camera or event data to identify crowded zones, visualize crowd density, and provide alerts when predefined thresholds are reached."""
    },
    {
        "code": "PS15",
        "title": "Intelligent Task and Reminder Management",
        "description": """People often miss deadlines or forget important tasks because their responsibilities are spread across multiple activities. Develop a solution that helps users organize tasks, set priorities and deadlines, and receive appropriate reminders based on their schedules."""
    },
    {
        "code": "PS16",
        "title": "Context-Aware Text Rewriting",
        "description": """A message that is appropriate in one situation may not be suitable for another audience or communication style. Develop a solution that understands the intended context of a given text and rewrites it according to requirements such as professional, formal, friendly, casual, or concise communication."""
    },
    {
        "code": "PS17",
        "title": "Visual Age and Gender Estimation",
        "description": """Analyzing demographic characteristics from visual data can be useful in certain computer vision applications. Develop a prototype that analyzes an image or camera input and estimates an age group and apparent gender presentation, while clearly displaying the prediction."""
    },
    {
        "code": "PS18",
        "title": "Constraint-Based Timetable Generation",
        "description": """Creating academic timetables manually requires balancing subjects, faculty availability, classrooms, periods, and scheduling constraints. Develop a solution that generates a timetable from the given requirements while minimizing scheduling conflicts and highlighting any constraints that cannot be satisfied."""
    },
    {
        "code": "PS19",
        "title": "Intelligent Internship and Job Matching",
        "description": """Students often spend significant time searching for internships and jobs that match their skills and interests. Develop a solution that compares a user's profile or resume with available opportunities and identifies relevant internships or jobs based on skills, qualifications, interests, and role requirements."""
    },
    {
        "code": "PS20",
        "title": "Intelligent Spam Message Detection",
        "description": """Users receive unwanted messages through email, SMS, and online platforms, making it difficult to distinguish legitimate communication from spam. Develop a solution that analyzes message content and classifies it as spam or legitimate, while providing useful indicators for the classification."""
    }
]


# ---------------------------------------------------------
# DATABASE
# ---------------------------------------------------------

def get_db():
    conn = sqlite3.connect(DATABASE)
    conn.row_factory = sqlite3.Row
    return conn


def init_db():

    conn = get_db()
    cursor = conn.cursor()

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS teams (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            team_no TEXT UNIQUE NOT NULL
        )
    """)

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS problems (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            code TEXT UNIQUE NOT NULL,
            title TEXT NOT NULL,
            description TEXT NOT NULL
        )
    """)

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS selections (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            team_id INTEGER UNIQUE NOT NULL,
            problem_id INTEGER NOT NULL,
            selected_at TEXT NOT NULL,

            FOREIGN KEY(team_id) REFERENCES teams(id),
            FOREIGN KEY(problem_id) REFERENCES problems(id)
        )
    """)

    # Insert problems
    for problem in PROBLEMS:

        cursor.execute("""
            INSERT OR IGNORE INTO problems
            (code, title, description)
            VALUES (?, ?, ?)
        """, (
            problem["code"],
            problem["title"],
            problem["description"]
        ))

    # Generate configured team numbers
    for i in range(1, TOTAL_TEAMS + 1):

        team_no = f"INX {i:02d}"

        cursor.execute("""
            INSERT OR IGNORE INTO teams (team_no)
            VALUES (?)
        """, (team_no,))

    conn.commit()
    conn.close()


# ---------------------------------------------------------
# HOME
# ---------------------------------------------------------

@app.route("/")
def index():

    return render_template(
        "index.html",
        total_teams=TOTAL_TEAMS
    )


# ---------------------------------------------------------
# TEAM LOGIN
# ---------------------------------------------------------

@app.route("/team", methods=["POST"])
def team_login():

    team_no = request.form.get("team_no", "").strip().upper()

    conn = get_db()

    team = conn.execute("""
        SELECT *
        FROM teams
        WHERE team_no = ?
    """, (team_no,)).fetchone()

    conn.close()

    if not team:

        return render_template(
            "index.html",
            total_teams=TOTAL_TEAMS,
            error="Invalid Team Number"
        )

    session["team_id"] = team["id"]
    session["team_no"] = team["team_no"]

    return redirect(url_for("problems"))


# ---------------------------------------------------------
# PROBLEM PAGE
# ---------------------------------------------------------

@app.route("/problems")
def problems():

    if "team_id" not in session:
        return redirect(url_for("index"))

    team_id = session["team_id"]

    conn = get_db()

    existing = conn.execute("""
        SELECT
            selections.id,
            selections.problem_id,
            problems.code,
            problems.title,
            problems.description
        FROM selections
        JOIN problems
        ON selections.problem_id = problems.id
        WHERE selections.team_id = ?
    """, (team_id,)).fetchone()

    if existing:

        conn.close()

        return render_template(
            "confirmation.html",
            team_no=session["team_no"],
            problem=existing
        )

    problems_data = conn.execute("""
        SELECT *
        FROM problems
        ORDER BY id
    """).fetchall()

    conn.close()

    return render_template(
        "problems.html",
        team_no=session["team_no"],
        problems=problems_data,
        max_teams=MAX_TEAMS_PER_PROBLEM
    )


# ---------------------------------------------------------
# API - CURRENT PROBLEM STATUS
# ---------------------------------------------------------

@app.route("/api/problems")
def api_problems():

    if "team_id" not in session:
        return jsonify({
            "error": "Unauthorized"
        }), 401

    conn = get_db()

    problems_data = conn.execute("""
        SELECT
            problems.id,
            problems.code,
            problems.title,
            problems.description,
            COUNT(selections.id) AS selected_count
        FROM problems
        LEFT JOIN selections
        ON problems.id = selections.problem_id
        GROUP BY problems.id
        ORDER BY problems.id
    """).fetchall()

    conn.close()

    result = []

    for p in problems_data:

        count = p["selected_count"]

        result.append({
            "id": p["id"],
            "code": p["code"],
            "title": p["title"],
            "description": p["description"],
            "selected_count": count,
            "locked": count >= MAX_TEAMS_PER_PROBLEM
        })

    return jsonify(result)


# ---------------------------------------------------------
# SELECT PROBLEM
# ---------------------------------------------------------

@app.route("/select-problem", methods=["POST"])
def select_problem():

    if "team_id" not in session:
        return jsonify({
            "success": False,
            "message": "Session expired."
        }), 401

    team_id = session["team_id"]
    problem_id = request.form.get("problem_id")

    if not problem_id:

        return jsonify({
            "success": False,
            "message": "Problem statement not selected."
        }), 400

    conn = get_db()

    try:

        # Important for preventing simultaneous
        # selections from exceeding 2 teams.
        conn.execute("BEGIN IMMEDIATE")

        # Check if team already selected
        existing = conn.execute("""
            SELECT *
            FROM selections
            WHERE team_id = ?
        """, (team_id,)).fetchone()

        if existing:

            conn.rollback()

            return jsonify({
                "success": False,
                "message": "Your team has already selected a problem statement."
            }), 400

        # Check problem exists
        problem = conn.execute("""
            SELECT *
            FROM problems
            WHERE id = ?
        """, (problem_id,)).fetchone()

        if not problem:

            conn.rollback()

            return jsonify({
                "success": False,
                "message": "Invalid problem statement."
            }), 400

        # Count selected teams
        count = conn.execute("""
            SELECT COUNT(*)
            FROM selections
            WHERE problem_id = ?
        """, (problem_id,)).fetchone()[0]

        if count >= MAX_TEAMS_PER_PROBLEM:

            conn.rollback()

            return jsonify({
                "success": False,
                "message": "This problem statement is already locked."
            }), 400

        # Insert selection
        conn.execute("""
            INSERT INTO selections
            (
                team_id,
                problem_id,
                selected_at
            )
            VALUES (?, ?, ?)
        """, (
            team_id,
            problem_id,
            datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        ))

        conn.commit()

        return jsonify({
            "success": True,
            "redirect": url_for("problems")
        })

    except Exception as e:

        conn.rollback()

        print("Selection Error:", e)

        return jsonify({
            "success": False,
            "message": "Something went wrong. Please try again."
        }), 500

    finally:

        conn.close()


# ---------------------------------------------------------
# LOGOUT
# ---------------------------------------------------------

@app.route("/logout")
def logout():

    session.clear()

    return redirect(url_for("index"))


# =========================================================
# ADMIN
# =========================================================

@app.route("/admin/login", methods=["GET", "POST"])
def admin_login():

    if request.method == "POST":

        password = request.form.get("password")

        if password == ADMIN_PASSWORD:

            session["admin"] = True

            return redirect(url_for("admin_dashboard"))

        return render_template(
            "admin_login.html",
            error="Invalid password."
        )

    return render_template("admin_login.html")


@app.route("/admin")
def admin_dashboard():

    if not session.get("admin"):
        return redirect(url_for("admin_login"))

    conn = get_db()

    problems_data = conn.execute("""
        SELECT
            problems.id,
            problems.code,
            problems.title,
            COUNT(selections.id) AS selected_count
        FROM problems
        LEFT JOIN selections
        ON problems.id = selections.problem_id
        GROUP BY problems.id
        ORDER BY problems.id
    """).fetchall()

    allocations = conn.execute("""
        SELECT
            teams.team_no,
            problems.code,
            problems.title,
            selections.selected_at
        FROM selections
        JOIN teams
        ON selections.team_id = teams.id
        JOIN problems
        ON selections.problem_id = problems.id
        ORDER BY teams.team_no
    """).fetchall()

    total_allocated = conn.execute("""
        SELECT COUNT(*)
        FROM selections
    """).fetchone()[0]

    conn.close()

    return render_template(
        "admin.html",
        problems=problems_data,
        allocations=allocations,
        total_teams=TOTAL_TEAMS,
        total_allocated=total_allocated,
        max_teams=MAX_TEAMS_PER_PROBLEM
    )


# ---------------------------------------------------------
# ADMIN LOGOUT
# ---------------------------------------------------------

@app.route("/admin/logout")
def admin_logout():

    session.pop("admin", None)

    return redirect(url_for("admin_login"))


# ---------------------------------------------------------
# RESET ALL ALLOCATIONS
# ---------------------------------------------------------

@app.route("/admin/reset", methods=["POST"])
def reset_allocations():

    if not session.get("admin"):
        return jsonify({
            "success": False
        }), 403

    conn = get_db()

    conn.execute("DELETE FROM selections")

    conn.commit()
    conn.close()

    return redirect(url_for("admin_dashboard"))


# ---------------------------------------------------------
# GENERATE PDF
# ---------------------------------------------------------

@app.route("/admin/pdf")
def generate_pdf():

    if not session.get("admin"):
        return redirect(url_for("admin_login"))

    os.makedirs("generated_pdfs", exist_ok=True)

    pdf_path = os.path.join(
        "generated_pdfs",
        "innovxthon_allocations.pdf"
    )

    conn = get_db()

    allocations = conn.execute("""
        SELECT
            teams.team_no,
            problems.code,
            problems.title,
            selections.selected_at
        FROM selections
        JOIN teams
        ON selections.team_id = teams.id
        JOIN problems
        ON selections.problem_id = problems.id
        ORDER BY teams.team_no
    """).fetchall()

    problem_wise = conn.execute("""
        SELECT
            problems.code,
            problems.title,
            teams.team_no
        FROM selections
        JOIN teams
        ON selections.team_id = teams.id
        JOIN problems
        ON selections.problem_id = problems.id
        ORDER BY problems.code, teams.team_no
    """).fetchall()

    conn.close()

    doc = SimpleDocTemplate(
        pdf_path,
        pagesize=landscape(A4),
        rightMargin=30,
        leftMargin=30,
        topMargin=30,
        bottomMargin=30
    )

    styles = getSampleStyleSheet()

    title_style = ParagraphStyle(
        "TitleCustom",
        parent=styles["Title"],
        alignment=TA_CENTER,
        fontSize=20,
        spaceAfter=10
    )

    subtitle_style = ParagraphStyle(
        "Subtitle",
        parent=styles["Normal"],
        alignment=TA_CENTER,
        fontSize=10,
        spaceAfter=20
    )

    elements = []

    elements.append(
        Paragraph(
            "INNOVXTHON 2026",
            title_style
        )
    )

    elements.append(
        Paragraph(
            "Problem Statement Allocation",
            subtitle_style
        )
    )

    # ----------------------------------------------
    # TEAM-WISE
    # ----------------------------------------------

    elements.append(
        Paragraph(
            "Team-wise Allocation",
            styles["Heading2"]
        )
    )

    team_table_data = [
        [
            "Team No.",
            "PS No.",
            "Problem Statement",
            "Selected At"
        ]
    ]

    for row in allocations:

        team_table_data.append([
            row["team_no"],
            row["code"],
            Paragraph(
                row["title"],
                styles["Normal"]
            ),
            row["selected_at"]
        ])

    if len(team_table_data) == 1:

        team_table_data.append([
            "No allocations yet",
            "",
            "",
            ""
        ])

    team_table = Table(
        team_table_data,
        colWidths=[90, 60, 330, 130]
    )

    team_table.setStyle(
        TableStyle([
            ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#111827")),
            ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
            ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
            ("GRID", (0, 0), (-1, -1), 0.5, colors.grey),
            ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
            ("LEFTPADDING", (0, 0), (-1, -1), 7),
            ("RIGHTPADDING", (0, 0), (-1, -1), 7),
            ("TOPPADDING", (0, 0), (-1, -1), 7),
            ("BOTTOMPADDING", (0, 0), (-1, -1), 7)
        ])
    )

    elements.append(team_table)

    elements.append(Spacer(1, 30))

    # ----------------------------------------------
    # PROBLEM-WISE
    # ----------------------------------------------

    elements.append(
        Paragraph(
            "Problem-wise Allocation",
            styles["Heading2"]
        )
    )

    problem_table_data = [
        [
            "PS No.",
            "Problem Statement",
            "Allocated Teams"
        ]
    ]

    grouped = {}

    for row in problem_wise:

        key = row["code"]

        if key not in grouped:

            grouped[key] = {
                "title": row["title"],
                "teams": []
            }

        grouped[key]["teams"].append(
            row["team_no"]
        )

    for problem in PROBLEMS:

        code = problem["code"]

        teams = grouped.get(
            code,
            {}
        ).get(
            "teams",
            []
        )

        team_text = ", ".join(teams)

        if not team_text:
            team_text = "No team allocated"

        problem_table_data.append([
            code,
            Paragraph(
                problem["title"],
                styles["Normal"]
            ),
            team_text
        ])

    problem_table = Table(
        problem_table_data,
        colWidths=[70, 360, 200]
    )

    problem_table.setStyle(
        TableStyle([
            ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#111827")),
            ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
            ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
            ("GRID", (0, 0), (-1, -1), 0.5, colors.grey),
            ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
            ("LEFTPADDING", (0, 0), (-1, -1), 7),
            ("RIGHTPADDING", (0, 0), (-1, -1), 7),
            ("TOPPADDING", (0, 0), (-1, -1), 6),
            ("BOTTOMPADDING", (0, 0), (-1, -1), 6)
        ])
    )

    elements.append(problem_table)

    elements.append(Spacer(1, 20))

    elements.append(
        Paragraph(
            f"Generated on: {datetime.now().strftime('%d-%m-%Y %H:%M:%S')}",
            styles["Normal"]
        )
    )

    doc.build(elements)

    return send_file(
        pdf_path,
        as_attachment=True,
        download_name="INNOVXTHON_Problem_Allocation.pdf"
    )


# ---------------------------------------------------------
# RUN
# ---------------------------------------------------------

if __name__ == "__main__":

    init_db()

    app.run(
        debug=True,
        host="0.0.0.0",
        port=5000
    )