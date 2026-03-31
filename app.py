import os
from flask import Flask, render_template, request, redirect, flash, session
from dotenv import load_dotenv
import sib_api_v3_sdk
from sib_api_v3_sdk.rest import ApiException
import psycopg2
from urllib.parse import urlparse
from functools import wraps

# Load environment variables
load_dotenv()

app = Flask(__name__)
app.secret_key = os.getenv("SECRET_KEY")

# ================= DATABASE =================

def get_db_connection():
    url = urlparse(os.getenv("DATABASE_URL"))

    conn = psycopg2.connect(
        host=url.hostname,
        database=url.path[1:],
        user=url.username,
        password=url.password,
        port=url.port
    )
    return conn

def init_db():
    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS enquiries (
            id SERIAL PRIMARY KEY,
            studentName TEXT,
            dob TEXT,
            age INTEGER,
            parentName TEXT,
            phone TEXT,
            email TEXT,
            address TEXT,
            program TEXT,
            message TEXT
        )
    """)

    conn.commit()
    cursor.close()
    conn.close()


try:
    init_db()
    print("Database connected ✅")
except Exception as e:
    print("Database error ❌:", e)

# ================= BREVO EMAIL FUNCTION =================

def send_enquiry_email(studentName, dob, age, parentName, phone, email, address, program, message):

    configuration = sib_api_v3_sdk.Configuration()
    configuration.api_key['api-key'] = os.getenv("BREVO_API_KEY")

    api_instance = sib_api_v3_sdk.TransactionalEmailsApi(
        sib_api_v3_sdk.ApiClient(configuration)
    )

    email_content = f"""
    <h2>New Admission Enquiry</h2>
    <p><b>Student Name:</b> {studentName}</p>
    <p><b>Date of Birth:</b> {dob}</p>
    <p><b>Age:</b> {age}</p>
    <p><b>Parent Name:</b> {parentName}</p>
    <p><b>Phone:</b> {phone}</p>
    <p><b>Email:</b> {email}</p>
    <p><b>Program:</b> {program}</p>
    <p><b>Address:</b> {address}</p>
    <p><b>Message:</b> {message}</p>
    """

    send_smtp_email = sib_api_v3_sdk.SendSmtpEmail(
        to=[{"email": "mykidszone.preschool.pune@gmail.com"}],
        sender={
            "email": "mykidszone.preschool.pune@gmail.com",
            "name": "My Kids Zone"
        },
        subject="New Admission Enquiry",
        html_content=email_content
    )

    try:
        api_instance.send_transac_email(send_smtp_email)
    except ApiException as e:
        print("Brevo Email Error:", e)

# ================= ADMIN AUTH =================

ADMIN_USERNAME = os.getenv("ADMIN_USERNAME")
ADMIN_PASSWORD = os.getenv("ADMIN_PASSWORD")

def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not session.get("admin_logged_in"):
            return redirect("/admin/login")
        return f(*args, **kwargs)
    return decorated_function

# ================= ROUTES =================

@app.route("/")
def home():
    return render_template("home.html")

@app.route("/about")
def about():
    return render_template("about.html")

@app.route("/programs")
def programs():
    return render_template("programs.html")

@app.route("/program/<program_name>")
def program_detail(program_name):
    folder_path = os.path.join("static/programs", program_name)
    images = []
    videos = []

    if os.path.exists(folder_path):
        for file in os.listdir(folder_path):
            if file.lower().endswith((".jpg", ".jpeg", ".png")):
                images.append(file)
            elif file.lower().endswith(".mp4"):
                videos.append(file)

    quotes = [
        "Tiny steps today, big dreams tomorrow 🌈",
        "Where curiosity turns into confidence ✨",
        "Learning made joyful every single day 🎨",
        "Little hands creating big futures 📚",
        "Play, learn and grow together 💛",
        "Every smile tells a story 😊",
        "Building bright minds with love 🌟",
        "Exploring, imagining and discovering 🚀",
        "Confidence begins in childhood 🧠",
        "Joyful learning in action 🎉"
    ]

    return render_template(
        "program_detail.html",
        program=program_name,
        images=images,
        videos=videos,
        quotes=quotes
    )

@app.route("/mission")
def mission():
    return render_template("mission.html")

@app.route("/reviews")
def reviews():
    folder_path = os.path.join("static/reviews")
    video_files = []

    if os.path.exists(folder_path):
        for file in os.listdir(folder_path):
            if file.lower().endswith(".mp4"):
                video_files.append(file)

    return render_template("reviews.html", videos=video_files)

# ================= ENQUIRY =================

@app.route("/enquiry", methods=["GET", "POST"])
def enquiry():

    if request.method == "POST":

        studentName = request.form["studentName"]
        dob = request.form["dob"]
        age = request.form["age"]
        parentName = request.form["parentName"]
        phone = request.form["phone"]
        email = request.form["email"]
        address = request.form["address"]
        program = request.form["program"]
        message = request.form["message"]

        conn = get_db_connection()
        cursor = conn.cursor()

        cursor.execute("""
            INSERT INTO enquiries
            (studentName, dob, age, parentName, phone, email, address, program, message)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
        """, (studentName, dob, age, parentName, phone, email, address, program, message))

        conn.commit()
        cursor.close()
        conn.close()

        send_enquiry_email(studentName, dob, age, parentName, phone, email, address, program, message)

        flash("Enquiry Submitted Successfully 🎉")
        return redirect("/enquiry")

    return render_template("enquiry.html")

# ================= ADMIN =================

@app.route("/admin/login", methods=["GET", "POST"])
def admin_login():
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]

        if username == ADMIN_USERNAME and password == ADMIN_PASSWORD:
            session["admin_logged_in"] = True
            return redirect("/admin/dashboard")
        else:
            flash("Invalid Credentials")

    return render_template("admin_login.html")


@app.route("/admin/logout")
def admin_logout():
    session.pop("admin_logged_in", None)
    return redirect("/admin/login")


@app.route("/admin/dashboard")
@login_required
def admin_dashboard():

    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute("SELECT * FROM enquiries ORDER BY id DESC")
    enquiries = cursor.fetchall()

    cursor.close()
    conn.close()

    return render_template("admin_dashboard.html", enquiries=enquiries)


@app.route("/admin/delete/<int:id>")
@login_required
def delete_enquiry(id):
    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute("DELETE FROM enquiries WHERE id=%s", (id,))

    conn.commit()
    cursor.close()
    conn.close()

    return redirect("/admin/dashboard")

# ================= RUN =================

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 5000)))