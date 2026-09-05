import streamlit as st
from pathlib import Path
from datetime import date, datetime
import sqlite3
import csv
import io


# ============================================================
# PAGE CONFIG
# ============================================================

st.set_page_config(
    page_title="Vijayam Publications | Faculty Portal",
    page_icon="🎓",
    layout="wide",
    initial_sidebar_state="expanded"
)


# ============================================================
# PROJECT PATHS
# ============================================================

ROOT_DIR = Path(__file__).parent

LOGO_PATH = ROOT_DIR / "logo.jpg"

DATABASE_PATH = ROOT_DIR / "faculty_portal.db"

UPLOAD_DIR = ROOT_DIR / "faculty_uploads"

UPLOAD_DIR.mkdir(exist_ok=True)


# ============================================================
# SECRETS
# ============================================================

FACULTY_ID = st.secrets["FACULTY_ID"]

COLLEGE_NAME = st.secrets["COLLEGE_NAME"]

PASSWORD = st.secrets["PASSWORD"]


# ============================================================
# DATABASE
# ============================================================

def get_connection():
    connection = sqlite3.connect(
        DATABASE_PATH,
        check_same_thread=False
    )

    connection.row_factory = sqlite3.Row

    return connection


def initialize_database():

    connection = get_connection()

    cursor = connection.cursor()

    cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS classes (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            class_date TEXT NOT NULL,
            class_time TEXT NOT NULL,
            subject TEXT NOT NULL,
            topic TEXT NOT NULL,
            duration TEXT NOT NULL,
            teaching_method TEXT NOT NULL,
            notes TEXT
        )
        """
    )

    cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS students (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            roll_number TEXT,
            course TEXT,
            semester TEXT,
            attendance TEXT,
            performance TEXT,
            notes TEXT
        )
        """
    )

    cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS documents (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT NOT NULL,
            document_type TEXT NOT NULL,
            subject TEXT,
            content TEXT,
            file_name TEXT,
            created_at TEXT NOT NULL
        )
        """
    )

    cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS questions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            subject TEXT NOT NULL,
            question TEXT NOT NULL,
            question_type TEXT NOT NULL,
            answer TEXT,
            created_at TEXT NOT NULL
        )
        """
    )

    connection.commit()

    connection.close()


initialize_database()


# ============================================================
# CLASS DATABASE FUNCTIONS
# ============================================================

def add_class(
    class_date,
    class_time,
    subject,
    topic,
    duration,
    teaching_method,
    notes
):

    connection = get_connection()

    connection.execute(
        """
        INSERT INTO classes (
            class_date,
            class_time,
            subject,
            topic,
            duration,
            teaching_method,
            notes
        )
        VALUES (?, ?, ?, ?, ?, ?, ?)
        """,
        (
            str(class_date),
            str(class_time),
            subject,
            topic,
            duration,
            teaching_method,
            notes
        )
    )

    connection.commit()

    connection.close()


def get_classes():

    connection = get_connection()

    rows = connection.execute(
        """
        SELECT *
        FROM classes
        ORDER BY class_date ASC, class_time ASC
        """
    ).fetchall()

    connection.close()

    return rows


def delete_class(class_id):

    connection = get_connection()

    connection.execute(
        "DELETE FROM classes WHERE id = ?",
        (class_id,)
    )

    connection.commit()

    connection.close()


# ============================================================
# STUDENT DATABASE FUNCTIONS
# ============================================================

def add_student(
    name,
    roll_number,
    course,
    semester,
    attendance,
    performance,
    notes
):

    connection = get_connection()

    connection.execute(
        """
        INSERT INTO students (
            name,
            roll_number,
            course,
            semester,
            attendance,
            performance,
            notes
        )
        VALUES (?, ?, ?, ?, ?, ?, ?)
        """,
        (
            name,
            roll_number,
            course,
            semester,
            attendance,
            performance,
            notes
        )
    )

    connection.commit()

    connection.close()


def get_students():

    connection = get_connection()

    rows = connection.execute(
        """
        SELECT *
        FROM students
        ORDER BY name ASC
        """
    ).fetchall()

    connection.close()

    return rows


def delete_student(student_id):

    connection = get_connection()

    connection.execute(
        "DELETE FROM students WHERE id = ?",
        (student_id,)
    )

    connection.commit()

    connection.close()


# ============================================================
# DOCUMENT DATABASE FUNCTIONS
# ============================================================

def add_document(
    title,
    document_type,
    subject,
    content,
    file_name
):

    connection = get_connection()

    connection.execute(
        """
        INSERT INTO documents (
            title,
            document_type,
            subject,
            content,
            file_name,
            created_at
        )
        VALUES (?, ?, ?, ?, ?, ?)
        """,
        (
            title,
            document_type,
            subject,
            content,
            file_name,
            datetime.now().strftime("%Y-%m-%d %H:%M")
        )
    )

    connection.commit()

    connection.close()


def get_documents():

    connection = get_connection()

    rows = connection.execute(
        """
        SELECT *
        FROM documents
        ORDER BY id DESC
        """
    ).fetchall()

    connection.close()

    return rows


# ============================================================
# QUESTION DATABASE FUNCTIONS
# ============================================================

def add_question(
    subject,
    question,
    question_type,
    answer
):

    connection = get_connection()

    connection.execute(
        """
        INSERT INTO questions (
            subject,
            question,
            question_type,
            answer,
            created_at
        )
        VALUES (?, ?, ?, ?, ?)
        """,
        (
            subject,
            question,
            question_type,
            answer,
            datetime.now().strftime("%Y-%m-%d %H:%M")
        )
    )

    connection.commit()

    connection.close()


def get_questions():

    connection = get_connection()

    rows = connection.execute(
        """
        SELECT *
        FROM questions
        ORDER BY id DESC
        """
    ).fetchall()

    connection.close()

    return rows


# ============================================================
# SESSION STATE
# ============================================================

if "authenticated" not in st.session_state:
    st.session_state.authenticated = False

if "subscription_selected" not in st.session_state:
    st.session_state.subscription_selected = False

if "selected_plan" not in st.session_state:
    st.session_state.selected_plan = ""


# ============================================================
# CUSTOM CSS
# ============================================================

st.markdown(
    """
    <style>

    .block-container {
        padding-top: 1rem;
        padding-bottom: 3rem;
        max-width: 1400px;
    }

    .login-title {
        text-align: center;
        font-size: 32px;
        font-weight: 800;
        margin-top: 0;
        margin-bottom: 5px;
    }

    .login-subtitle {
        text-align: center;
        font-size: 17px;
        margin-bottom: 25px;
    }

    .login-heading {
        text-align: center;
        font-size: 28px;
        font-weight: 700;
        margin-bottom: 20px;
    }

    .dashboard-title {
        font-size: 34px;
        font-weight: 800;
        margin-bottom: 5px;
    }

    .dashboard-subtitle {
        font-size: 17px;
        margin-bottom: 20px;
    }

    .plan-card {
        border: 1px solid #dddddd;
        border-radius: 12px;
        padding: 20px;
        text-align: center;
        min-height: 220px;
    }

    .plan-price {
        font-size: 34px;
        font-weight: 800;
        margin: 12px 0;
    }

    .footer {
        text-align: center;
        padding: 20px;
        margin-top: 30px;
        border-top: 1px solid #dddddd;
    }

    </style>
    """,
    unsafe_allow_html=True
)


# ============================================================
# LOGIN PAGE
# ============================================================

if not st.session_state.authenticated:

    st.markdown("<br>", unsafe_allow_html=True)

    # --------------------------------------------------------
    # CENTERED LOGO
    # --------------------------------------------------------

    left_logo, center_logo, right_logo = st.columns(
        [1, 2, 1]
    )

    with center_logo:

        if LOGO_PATH.exists():

            st.image(
                str(LOGO_PATH),
                width=280
            )

        else:

            st.error(
                "logo.jpg was not found. Please put logo.jpg in the project folder."
            )

    # --------------------------------------------------------
    # BRAND NAME
    # --------------------------------------------------------

    st.markdown(
        """
        <div class="login-title">
            VIJAYAM PUBLICATIONS
        </div>
        """,
        unsafe_allow_html=True
    )

    st.markdown(
        """
        <div class="login-subtitle">
            Faculty Education & Teaching Portal
        </div>
        """,
        unsafe_allow_html=True
    )

    st.divider()

    # --------------------------------------------------------
    # LOGIN
    # --------------------------------------------------------

    st.markdown(
        """
        <div class="login-heading">
            Faculty Login
        </div>
        """,
        unsafe_allow_html=True
    )

    left, center, right = st.columns(
        [1, 2, 1]
    )

    with center:

        faculty_id_input = st.text_input(
            "Faculty ID",
            placeholder="Enter your Faculty ID"
        )

        college_name_input = st.text_input(
            "College Name",
            placeholder="Enter your College Name"
        )

        password_input = st.text_input(
            "Password",
            type="password",
            placeholder="Enter your Password"
        )

        login_button = st.button(
            "Login",
            type="primary",
            use_container_width=True
        )

        if login_button:

            if (
                faculty_id_input == FACULTY_ID
                and college_name_input == COLLEGE_NAME
                and password_input == PASSWORD
            ):

                st.session_state.authenticated = True

                st.rerun()

            else:

                st.error(
                    "Invalid Faculty ID, College Name, or Password."
                )

    st.divider()

    st.caption(
        "Vijayam Publications | Faculty Education & Teaching Portal"
    )

    st.stop()


# ============================================================
# PAYMENT PAGE
# ============================================================

if not st.session_state.subscription_selected:

    left_logo, center_logo, right_logo = st.columns(
        [1, 2, 1]
    )

    with center_logo:

        if LOGO_PATH.exists():

            st.image(
                str(LOGO_PATH),
                width=220
            )

    st.markdown(
        """
        <div class="login-title">
            VIJAYAM PUBLICATIONS
        </div>
        """,
        unsafe_allow_html=True
    )

    st.subheader(
        "Faculty Membership"
    )

    st.write(
        "Select a membership plan to continue to the faculty dashboard."
    )

    st.info(
        "Demo payment screen. No real payment is processed."
    )

    plan1, plan2, plan3, plan4 = st.columns(4)

    # --------------------------------------------------------
    # MONTHLY
    # --------------------------------------------------------

    with plan1:

        st.markdown(
            """
            <div class="plan-card">
                <h2>Monthly</h2>
                <div class="plan-price">₹299</div>
                <p>1 Month Access</p>
                <p>Faculty Dashboard</p>
                <p>Teaching Tools</p>
            </div>
            """,
            unsafe_allow_html=True
        )

        if st.button(
            "Choose Monthly",
            key="monthly_plan",
            use_container_width=True
        ):

            st.session_state.selected_plan = "Monthly - ₹299"

            st.session_state.subscription_selected = True

            st.rerun()

    # --------------------------------------------------------
    # QUARTERLY
    # --------------------------------------------------------

    with plan2:

        st.markdown(
            """
            <div class="plan-card">
                <h2>Quarterly</h2>
                <div class="plan-price">₹599</div>
                <p>3 Months Access</p>
                <p>Faculty Dashboard</p>
                <p>Teaching Tools</p>
            </div>
            """,
            unsafe_allow_html=True
        )

        if st.button(
            "Choose Quarterly",
            key="quarterly_plan",
            use_container_width=True
        ):

            st.session_state.selected_plan = "Quarterly - ₹599"

            st.session_state.subscription_selected = True

            st.rerun()

    # --------------------------------------------------------
    # YEARLY
    # --------------------------------------------------------

    with plan3:

        st.markdown(
            """
            <div class="plan-card">
                <h2>Yearly</h2>
                <div class="plan-price">₹899</div>
                <p>12 Months Access</p>
                <p>Faculty Dashboard</p>
                <p>Teaching Tools</p>
            </div>
            """,
            unsafe_allow_html=True
        )

        if st.button(
            "Choose Yearly",
            key="yearly_plan",
            use_container_width=True
        ):

            st.session_state.selected_plan = "Yearly - ₹899"

            st.session_state.subscription_selected = True

            st.rerun()

    # --------------------------------------------------------
    # CUSTOM
    # --------------------------------------------------------

    with plan4:

        st.markdown(
            """
            <div class="plan-card">
                <h2>Custom</h2>
                <div class="plan-price">Custom</div>
                <p>Flexible Plan</p>
                <p>Choose Amount</p>
                <p>Faculty Dashboard</p>
            </div>
            """,
            unsafe_allow_html=True
        )

        custom_amount = st.number_input(
            "Custom Amount",
            min_value=1,
            value=999,
            step=100,
            key="custom_amount"
        )

        if st.button(
            "Choose Custom",
            key="custom_plan",
            use_container_width=True
        ):

            st.session_state.selected_plan = (
                f"Custom Plan - ₹{custom_amount}"
            )

            st.session_state.subscription_selected = True

            st.rerun()

    st.stop()


# ============================================================
# SIDEBAR
# ============================================================

with st.sidebar:

    if LOGO_PATH.exists():

        st.image(
            str(LOGO_PATH),
            width=190
        )

    st.markdown(
        "## Vijayam Publications"
    )

    st.caption(
        "Faculty Education & Teaching Portal"
    )

    st.divider()

    st.write("**Faculty ID**")

    st.write(
        FACULTY_ID
    )

    st.write("**College**")

    st.write(
        COLLEGE_NAME
    )

    st.write("**Plan**")

    st.write(
        st.session_state.selected_plan
    )

    st.divider()

    st.markdown(
        "### Faculty Tools"
    )

    st.write("📅 Class Planner")

    st.write("📚 Teaching Library")

    st.write("📝 Assessment")

    st.write("👨‍🎓 Students")

    st.write("📰 Medical Updates")

    st.divider()

    if st.button(
        "Logout",
        use_container_width=True
    ):

        st.session_state.authenticated = False

        st.session_state.subscription_selected = False

        st.session_state.selected_plan = ""

        st.rerun()


# ============================================================
# DASHBOARD HEADER
# ============================================================

st.markdown(
    """
    <div class="dashboard-title">
        Faculty Dashboard
    </div>
    """,
    unsafe_allow_html=True
)

st.markdown(
    """
    <div class="dashboard-subtitle">
        Vijayam Publications Faculty Education & Teaching Portal
    </div>
    """,
    unsafe_allow_html=True
)


# ============================================================
# DASHBOARD DATA
# ============================================================

today = date.today()

all_classes = get_classes()

all_students = get_students()

all_documents = get_documents()

all_questions = get_questions()

upcoming_classes = [
    item
    for item in all_classes
    if item["class_date"] >= str(today)
]


# ============================================================
# DASHBOARD METRICS
# ============================================================

metric1, metric2, metric3, metric4 = st.columns(4)

with metric1:

    st.metric(
        "Upcoming Classes",
        len(upcoming_classes)
    )

with metric2:

    st.metric(
        "Students",
        len(all_students)
    )

with metric3:

    st.metric(
        "Teaching Materials",
        len(all_documents)
    )

with metric4:

    st.metric(
        "Question Bank",
        len(all_questions)
    )


st.divider()


# ============================================================
# TABS
# ============================================================

tab1, tab2, tab3, tab4, tab5, tab6 = st.tabs(
    [
        "🏠 Home",
        "📰 Medical Updates",
        "📅 Class Planner",
        "📚 Teaching Library",
        "📝 Assessment",
        "👨‍🎓 Students"
    ]
)


# ============================================================
# HOME
# ============================================================

with tab1:

    st.subheader(
        "Today's Teaching Workspace"
    )

    if len(upcoming_classes) == 0:

        st.info(
            "No upcoming classes have been scheduled."
        )

        st.write(
            "Go to the Class Planner tab to schedule your lectures."
        )

    else:

        st.write(
            "### Upcoming Classes"
        )

        for item in upcoming_classes[:5]:

            with st.container(border=True):

                col1, col2, col3 = st.columns(3)

                with col1:

                    st.write(
                        f"**{item['subject']}**"
                    )

                    st.write(
                        item["topic"]
                    )

                with col2:

                    st.write(
                        f"Date: {item['class_date']}"
                    )

                    st.write(
                        f"Time: {item['class_time']}"
                    )

                with col3:

                    st.write(
                        f"Method: {item['teaching_method']}"
                    )

                    st.write(
                        f"Duration: {item['duration']}"
                    )

    st.divider()

    st.subheader(
        "Faculty Workspace"
    )

    col1, col2, col3 = st.columns(3)

    with col1:

        st.write(
            "### 📅 Plan Classes"
        )

        st.write(
            "Schedule lectures, practicals, tutorials, seminars and revision sessions."
        )

    with col2:

        st.write(
            "### 📚 Organize Teaching"
        )

        st.write(
            "Create lecture notes, lesson plans, assignments and study material."
        )

    with col3:

        st.write(
            "### 📝 Assess Students"
        )

        st.write(
            "Create questions and maintain a reusable question bank."
        )


# ============================================================
# MEDICAL NEWS
# ============================================================

with tab2:

    st.subheader(
        "📰 Medical & Healthcare Updates"
    )

    st.write(
        "Demo medical news for faculty reference."
    )

    news_items = [
        (
            "Medical Education",
            "New Approaches to Interactive Medical Teaching",
            "Medical educators are increasingly using case-based discussions, simulation and interactive classroom activities to improve student engagement."
        ),
        (
            "Healthcare",
            "Digital Health Continues to Expand",
            "Digital health tools are becoming an important part of modern healthcare education, including telemedicine, electronic records and remote learning."
        ),
        (
            "Medical Research",
            "Research Skills Gain Importance in Healthcare Education",
            "Healthcare education programs continue to place greater emphasis on evidence-based practice, research literacy and critical evaluation of studies."
        ),
        (
            "Clinical Education",
            "Simulation-Based Learning Supports Practical Training",
            "Simulation activities can give healthcare students opportunities to practise clinical decision-making and communication in controlled environments."
        ),
        (
            "Faculty Development",
            "Technology Is Changing the Modern Classroom",
            "Faculty members are increasingly combining traditional teaching methods with digital resources, multimedia content and online assessment tools."
        )
    ]

    for category, title, description in news_items:

        with st.container(border=True):

            st.caption(
                category
            )

            st.subheader(
                title
            )

            st.write(
                description
            )

    st.caption(
        "Demo content only. No live news service is connected."
    )


# ============================================================
# CLASS PLANNER
# ============================================================

with tab3:

    st.subheader(
        "📅 Class Planner"
    )

    st.write(
        "Schedule lectures, practicals, tutorials and revision sessions."
    )

    with st.form(
        "class_form"
    ):

        col1, col2 = st.columns(2)

        with col1:

            class_date = st.date_input(
                "Class Date",
                value=date.today()
            )

        with col2:

            class_time = st.time_input(
                "Class Time"
            )

        col1, col2 = st.columns(2)

        with col1:

            subject = st.text_input(
                "Subject",
                placeholder="Example: Anatomy"
            )

        with col2:

            topic = st.text_input(
                "Lecture Topic",
                placeholder="Example: Upper Limb"
            )

        duration = st.selectbox(
            "Duration",
            [
                "30 minutes",
                "45 minutes",
                "60 minutes",
                "90 minutes",
                "120 minutes"
            ]
        )

        teaching_method = st.selectbox(
            "Teaching Method",
            [
                "Lecture",
                "Practical",
                "Tutorial",
                "Seminar",
                "Case Discussion",
                "Revision",
                "Assessment"
            ]
        )

        notes = st.text_area(
            "Teaching Notes",
            placeholder="Add objectives, preparation notes or reminders."
        )

        submit_class = st.form_submit_button(
            "Add Class",
            type="primary"
        )

        if submit_class:

            if subject.strip() and topic.strip():

                add_class(
                    class_date,
                    class_time,
                    subject.strip(),
                    topic.strip(),
                    duration,
                    teaching_method,
                    notes.strip()
                )

                st.success(
                    "Class added successfully."
                )

                st.rerun()

            else:

                st.error(
                    "Please enter both Subject and Lecture Topic."
                )

    st.divider()

    st.subheader(
        "Scheduled Classes"
    )

    classes = get_classes()

    if len(classes) == 0:

        st.info(
            "No classes scheduled yet."
        )

    else:

        for item in classes:

            with st.container(border=True):

                col1, col2, col3 = st.columns(
                    [2, 2, 1]
                )

                with col1:

                    st.write(
                        f"### {item['subject']}"
                    )

                    st.write(
                        f"Topic: {item['topic']}"
                    )

                with col2:

                    st.write(
                        f"Date: {item['class_date']}"
                    )

                    st.write(
                        f"Time: {item['class_time']}"
                    )

                    st.write(
                        f"Method: {item['teaching_method']}"
                    )

                with col3:

                    st.write(
                        item["duration"]
                    )

                    if st.button(
                        "Delete",
                        key=f"class_delete_{item['id']}"
                    ):

                        delete_class(
                            item["id"]
                        )

                        st.rerun()

                if item["notes"]:

                    st.write(
                        f"Notes: {item['notes']}"
                    )


# ============================================================
# TEACHING LIBRARY
# ============================================================

with tab4:

    st.subheader(
        "📚 Teaching Library"
    )

    st.write(
        "Create and save lecture notes, lesson plans and teaching resources."
    )

    document_title = st.text_input(
        "Document Title",
        placeholder="Example: Anatomy Lecture Notes"
    )

    document_type = st.selectbox(
        "Document Type",
        [
            "Lecture Notes",
            "Lesson Plan",
            "Study Material",
            "Practical Notes",
            "Revision Material",
            "Assignment",
            "Faculty Notes"
        ]
    )

    document_subject = st.text_input(
        "Subject",
        placeholder="Example: Anatomy"
    )

    document_content = st.text_area(
        "Teaching Material",
        height=250,
        placeholder="Write your teaching material here."
    )

    uploaded_file = st.file_uploader(
        "Attach a file",
        type=[
            "pdf",
            "doc",
            "docx",
            "ppt",
            "pptx",
            "txt",
            "csv"
        ]
    )

    if st.button(
        "Save Teaching Material",
        type="primary"
    ):

        if document_title.strip():

            saved_file_name = ""

            if uploaded_file is not None:

                saved_file_name = uploaded_file.name

                safe_name = (
                    datetime.now().strftime("%Y%m%d%H%M%S")
                    + "_"
                    + uploaded_file.name
                )

                file_path = UPLOAD_DIR / safe_name

                with open(
                    file_path,
                    "wb"
                ) as file:

                    file.write(
                        uploaded_file.getbuffer()
                    )

            add_document(
                document_title.strip(),
                document_type,
                document_subject.strip(),
                document_content.strip(),
                saved_file_name
            )

            st.success(
                "Teaching material saved successfully."
            )

            st.rerun()

        else:

            st.error(
                "Please enter a document title."
            )

    st.divider()

    st.subheader(
        "Saved Teaching Materials"
    )

    documents = get_documents()

    if len(documents) == 0:

        st.info(
            "No teaching materials have been created yet."
        )

    else:

        for document in documents:

            with st.expander(
                document["title"]
            ):

                st.write(
                    f"Type: {document['document_type']}"
                )

                st.write(
                    f"Subject: {document['subject']}"
                )

                st.write(
                    f"Created: {document['created_at']}"
                )

                if document["content"]:

                    st.write(
                        document["content"]
                    )

                    st.download_button(
                        "Download Notes",
                        document["content"],
                        file_name=(
                            document["title"]
                            + ".txt"
                        ),
                        mime="text/plain",
                        key=(
                            f"document_download_"
                            f"{document['id']}"
                        )
                    )

                if document["file_name"]:

                    st.write(
                        f"Attached file: {document['file_name']}"
                    )


# ============================================================
# ASSESSMENT
# ============================================================

with tab5:

    st.subheader(
        "📝 Assessment & Question Bank"
    )

    st.write(
        "Create questions for assignments, revision, tests and examinations."
    )

    question_subject = st.text_input(
        "Subject",
        placeholder="Example: Pharmacology"
    )

    question_type = st.selectbox(
        "Question Type",
        [
            "MCQ",
            "Short Answer",
            "Long Answer",
            "Case Study",
            "True / False",
            "Viva Question"
        ]
    )

    question_text = st.text_area(
        "Question",
        placeholder="Enter your question."
    )

    answer_text = st.text_area(
        "Answer / Key Points",
        placeholder="Enter the answer or marking points."
    )

    if st.button(
        "Add Question",
        type="primary"
    ):

        if (
            question_subject.strip()
            and question_text.strip()
        ):

            add_question(
                question_subject.strip(),
                question_text.strip(),
                question_type,
                answer_text.strip()
            )

            st.success(
                "Question added successfully."
            )

            st.rerun()

        else:

            st.error(
                "Please enter the subject and question."
            )

    st.divider()

    st.subheader(
        "Question Bank"
    )

    questions = get_questions()

    if len(questions) == 0:

        st.info(
            "No questions have been added yet."
        )

    else:

        for number, question in enumerate(
            questions,
            start=1
        ):

            with st.expander(
                f"{number}. {question['subject']} - "
                f"{question['question_type']}"
            ):

                st.write(
                    f"Question: {question['question']}"
                )

                if question["answer"]:

                    st.write(
                        f"Answer / Key Points: "
                        f"{question['answer']}"
                    )

    if len(questions) > 0:

        csv_buffer = io.StringIO()

        writer = csv.writer(
            csv_buffer
        )

        writer.writerow(
            [
                "Subject",
                "Question Type",
                "Question",
                "Answer"
            ]
        )

        for question in questions:

            writer.writerow(
                [
                    question["subject"],
                    question["question_type"],
                    question["question"],
                    question["answer"]
                ]
            )

        st.download_button(
            "Download Question Bank",
            csv_buffer.getvalue(),
            file_name="vijayam_question_bank.csv",
            mime="text/csv"
        )


# ============================================================
# STUDENTS
# ============================================================

with tab6:

    st.subheader(
        "👨‍🎓 Student Management"
    )

    st.write(
        "Maintain student information, attendance and performance notes."
    )

    with st.form(
        "student_form"
    ):

        student_name = st.text_input(
            "Student Name"
        )

        student_roll = st.text_input(
            "Roll Number"
        )

        student_course = st.text_input(
            "Course"
        )

        student_semester = st.text_input(
            "Semester"
        )

        student_attendance = st.selectbox(
            "Attendance",
            [
                "Excellent",
                "Good",
                "Needs Attention",
                "Critical"
            ]
        )

        student_performance = st.selectbox(
            "Performance",
            [
                "Excellent",
                "Good",
                "Average",
                "Needs Support"
            ]
        )

        student_notes = st.text_area(
            "Faculty Notes"
        )

        submit_student = st.form_submit_button(
            "Add Student",
            type="primary"
        )

        if submit_student:

            if student_name.strip():

                add_student(
                    student_name.strip(),
                    student_roll.strip(),
                    student_course.strip(),
                    student_semester.strip(),
                    student_attendance,
                    student_performance,
                    student_notes.strip()
                )

                st.success(
                    "Student added successfully."
                )

                st.rerun()

            else:

                st.error(
                    "Please enter the student name."
                )

    st.divider()

    st.subheader(
        "Student List"
    )

    students = get_students()

    if len(students) == 0:

        st.info(
            "No students have been added yet."
        )

    else:

        for student in students:

            with st.container(border=True):

                col1, col2, col3 = st.columns(
                    [2, 2, 1]
                )

                with col1:

                    st.write(
                        f"### {student['name']}"
                    )

                    st.write(
                        f"Roll Number: {student['roll_number']}"
                    )

                    st.write(
                        f"Course: {student['course']}"
                    )

                with col2:

                    st.write(
                        f"Semester: {student['semester']}"
                    )

                    st.write(
                        f"Attendance: {student['attendance']}"
                    )

                    st.write(
                        f"Performance: {student['performance']}"
                    )

                with col3:

                    if st.button(
                        "Delete",
                        key=f"student_delete_{student['id']}"
                    ):

                        delete_student(
                            student["id"]
                        )

                        st.rerun()

                if student["notes"]:

                    st.write(
                        f"Faculty Notes: {student['notes']}"
                    )

    if len(students) > 0:

        student_csv = io.StringIO()

        student_writer = csv.writer(
            student_csv
        )

        student_writer.writerow(
            [
                "Name",
                "Roll Number",
                "Course",
                "Semester",
                "Attendance",
                "Performance",
                "Notes"
            ]
        )

        for student in students:

            student_writer.writerow(
                [
                    student["name"],
                    student["roll_number"],
                    student["course"],
                    student["semester"],
                    student["attendance"],
                    student["performance"],
                    student["notes"]
                ]
            )

        st.download_button(
            "Download Student List",
            student_csv.getvalue(),
            file_name="vijayam_student_list.csv",
            mime="text/csv"
        )


# ============================================================
# FOOTER
# ============================================================

st.divider()

st.markdown(
    """
    <div class="footer">
        <strong>VIJAYAM PUBLICATIONS</strong><br>
        Faculty Education & Teaching Portal<br>
        Teaching • Planning • Assessment • Resources • Student Support
    </div>
    """,
    unsafe_allow_html=True
)