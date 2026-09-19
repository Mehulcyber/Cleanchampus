from flask import Flask, render_template, request ,redirect,send_from_directory
from werkzeug.utils import secure_filename
import os 
import mysql.connector
import os

app = Flask(
    __name__,
    template_folder=os.path.join(os.path.dirname(__file__), "templates")
)
UPLOAD_FOLDER = 'uploads'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

def get_db_connection():
    return mysql.connector.connect(
        host="localhost",
        user="root",
        password="Mehulkr#143",
        database="clean_campus"
    )


@app.route("/", methods=["GET", "POST"])
def home():
    message = None

    if request.method == "POST":
        waste_type = request.form["waste_type"]
        location = request.form["location"]
        description = request.form["description"]

        photo = request.files.get("photo")
        photo_filename = None

        if photo and photo.filename:
            photo_filename = secure_filename(photo.filename)
            photo.save(
                os.path.join(
                    app.config["UPLOAD_FOLDER"],
                    photo_filename
                )
            )

        conn = get_db_connection()
        cursor = conn.cursor()

        query = """
        INSERT INTO reports (waste_type, location, description, photo)
        VALUES (%s, %s, %s, %s)
        """

        cursor.execute(
            query,
            (waste_type, location, description, photo_filename)
        )

        conn.commit()
        cursor.close()
        conn.close()

        message = "Report submitted successfully! ♻️"

    return render_template("index.html", message=message)
@app.route("/admin")
def admin():
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)

    cursor.execute("SELECT * FROM reports ORDER BY created_at DESC")
    reports = cursor.fetchall()
    pending_count = sum(1 for r in reports if r["status"] == "Pending")
    progress_count = sum(1 for r in reports if r["status"] == "In Progress")
    resolved_count = sum(1 for r in reports if r["status"] == "Resolved")

    total_reports = len(reports)
    pending_reports = sum(1 for r in reports if r["status"] == "Pending")
    resolved_reports = sum(1 for r in reports if r["status"] == "Resolved")

    cursor.close()
    conn.close()

    return render_template("admin.html", reports=reports, pending_count=pending_count, progress_count=progress_count, resolved_count=resolved_count)

@app.route("/update_status/<int:report_id>", methods=["POST"])
def update_status(report_id):
    status = request.form["status"]

    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute(
        "UPDATE reports SET status = %s WHERE id = %s",
        (status, report_id)
    )

    conn.commit()
    cursor.close()
    conn.close()

    return redirect("/admin")
@app.route("/uploads/<filename>")
def uploaded_file(filename):
    return send_from_directory(
        app.config["UPLOAD_FOLDER"],
        filename
    )
if __name__ == "__main__":
     app.run(debug=True)         
