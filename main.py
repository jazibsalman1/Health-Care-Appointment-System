from fastapi import FastAPI, Request, Form
from fastapi.staticfiles import StaticFiles
from fastapi.responses import RedirectResponse, HTMLResponse
from fastapi.templating import Jinja2Templates
from starlette.middleware.sessions import SessionMiddleware
import uvicorn
import sqlite3

app = FastAPI()
app.add_middleware(SessionMiddleware, secret_key="supersecretkey")

# Static + Templates
app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="templates")

# --- DB setup ---
with sqlite3.connect("hospital.db") as conn:
    conn.execute("""
        CREATE TABLE IF NOT EXISTS appointments (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            firstName TEXT NOT NULL,
            lastName TEXT NOT NULL,
            email TEXT NOT NULL,
            phone TEXT NOT NULL,
            dob TEXT NOT NULL,
            gender TEXT,
            address TEXT,
            appointmentDate TEXT NOT NULL,
            doctor TEXT,
            timeSlot TEXT NOT NULL,
            appointmentType TEXT NOT NULL,
            symptoms TEXT,
            medications TEXT,
            allergies TEXT,
            insurance TEXT,
            visitType TEXT,
            notes TEXT,
            consent INTEGER NOT NULL,
            reminders INTEGER
        )
    """)

# --- Routes ---
@app.get("/")
async def index_page(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})

@app.get("/login")
async def login_page(request: Request):
    return templates.TemplateResponse("login.html", {"request": request})






@app.get("/signup")
async def signup_page(request: Request):
    return templates.TemplateResponse("signup.html", {"request": request})

@app.get("/appoinments")
async def appoinments(request: Request):
    user_email = request.session.get("email")
    appointments = []
    if user_email:
        with sqlite3.connect("hospital.db") as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM appointments WHERE email = ?", (user_email,))
            appointments = cursor.fetchall()
    return templates.TemplateResponse(
        "appoinments.html",
        {"request": request, "appointments": appointments}
    )

@app.get("/find_doctor")
async def find_doctor(request: Request):
    return templates.TemplateResponse("find_doctors.html", {"request": request})

@app.get("/book_appoinment")
async def book_appointment(request: Request):
    return templates.TemplateResponse("book_appoinment.html", {"request": request})

# --- Insert new appointment ---
@app.post("/submit_booking")
async def submit_booking(request: Request):
    form = await request.form()
    with sqlite3.connect("hospital.db") as conn:
        conn.execute("""
            INSERT INTO appointments (
                firstName, lastName, email, phone, dob, gender, address,
                appointmentDate, doctor, timeSlot, appointmentType,
                symptoms, medications, allergies, insurance,
                visitType, notes, consent, reminders
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            form.get("firstName"),
            form.get("lastName"),
            form.get("email"),
            form.get("phone"),
            form.get("dob"),
            form.get("gender"),
            form.get("address"),
            form.get("appointmentDate"),
            form.get("doctor"),
            form.get("timeSlot"),
            form.get("appointmentType"),
            form.get("symptoms"),
            form.get("medications"),
            form.get("allergies"),
            form.get("insurance"),
            form.get("visitType"),
            form.get("notes"),
            1 if form.get("consent") else 0,
            1 if form.get("reminders") else 0
        ))
        conn.commit()
    request.session["email"] = form.get("email")
    return RedirectResponse(url="/appoinments", status_code=303)





# --- Show update form ---
@app.get("/update_booking/{id}")
async def update_booking_form(request: Request, id: int):
    user_email = request.session.get("email")
    if not user_email:
        return RedirectResponse("/login", status_code=303)

    with sqlite3.connect("hospital.db") as conn:
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        cursor.execute(
            "SELECT * FROM appointments WHERE id = ? AND email = ?",
            (id, user_email),
        )
        appointment = cursor.fetchone()

    if not appointment:
        return HTMLResponse("<h3>Appointment not found or not yours!</h3>")

    return templates.TemplateResponse(
        "update_appoinment.html",
        {"request": request, "appointment": appointment}
    )

# --- Handle update submit ---
@app.post("/update_booking/{id}")
async def update_booking_submit(
    request: Request,
    id: int,
    appointmentDate: str = Form(...),
    doctor: str = Form(""),
    timeSlot: str = Form(...),
    appointmentType: str = Form(...),
):
    user_email = request.session.get("email")
    if not user_email:
        return RedirectResponse("/login", status_code=303)

    with sqlite3.connect("hospital.db") as conn:
        conn.execute(
            """
            UPDATE appointments
            SET appointmentDate=?, doctor=?, timeSlot=?, appointmentType=?
            WHERE id=? AND email=?
            """,
            (appointmentDate, doctor, timeSlot, appointmentType, id, user_email),
        )
        conn.commit()

    return RedirectResponse(url="/appoinments", status_code=303)




# admin panel route


@app.get("/admin", response_class=HTMLResponse)
async def admin_page(request: Request):
    conn = sqlite3.connect("hospital.db")
    conn.row_factory = sqlite3.Row  
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM appointments")
    rows = cursor.fetchall()
    conn.close()

    return templates.TemplateResponse("admin/admin.html", {
        "request": request,
        "appointments": rows
    })


@app.post("/up-con")
async def update_status(id: int = Form(...)):
    conn = sqlite3.connect("hospital.db")
    cur = conn.cursor()
    cur.execute("UPDATE appointments SET status = ? WHERE id = ?", ("Confirmed", id))
    conn.commit()
    conn.close()
    return RedirectResponse(url="/admin", status_code=303)
@app.post("/up-can")
async def update_status(id: int = Form(...)):
    conn = sqlite3.connect("hospital.db")
    cur = conn.cursor()
    cur.execute("UPDATE appointments SET status = ? WHERE id = ?", ("Cancelled", id))
    conn.commit()
    conn.close()
    return RedirectResponse(url="/admin", status_code=303)    




# signup 

# Function to create DB if not exists
with sqlite3.connect("hospital.db") as conn:
    conn = sqlite3.connect("hospital.db")
    cur = conn.cursor()
    cur.execute("""
        CREATE TABLE IF NOT EXISTS signupusers (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT NOT NULL,
            email TEXT NOT NULL UNIQUE,
            password TEXT NOT NULL
        )
    """)
    conn.commit()
    conn.close()



@app.post("/signup-form")
async def signup(
    request: Request,
    username: str = Form(...),
    email: str = Form(...),
    password: str = Form(...),
    confirm: str = Form(...)
):
    if password != confirm:
        return {"status": "error", "message": "❌ Passwords do not match"}

    try:
        conn = sqlite3.connect("hospital.db")
        cur = conn.cursor()
        cur.execute("INSERT INTO signupusers (username, email, password) VALUES (?, ?, ?)",
                    (username, email, password))
        conn.commit()
        conn.close()
    except sqlite3.IntegrityError:
        return {"status": "error", "message": "⚠️ Email already exists"}

    return RedirectResponse(url="/login", status_code=303)

#login 
@app.post("/login_form")
async def login_form(request: Request, email: str = Form(...), password: str = Form(...)):
    conn = sqlite3.connect("hospital.db")
    cur = conn.cursor()
    cur.execute("SELECT * FROM signupusers WHERE email = ? AND password = ?", (email, password))
    user = cur.fetchone()
    conn.close()

    if user:
        request.session["email"] = email
        request.session["password"]=password
        return RedirectResponse(url="/appoinments", status_code=303)
    else:
        return {"status": "error", "message": "Invalid email or password"}


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
