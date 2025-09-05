from fastapi import FastAPI, Request
from fastapi.staticfiles import StaticFiles
from fastapi.responses import RedirectResponse
from fastapi.templating import Jinja2Templates
import uvicorn
import sqlite3


app = FastAPI()

# Mount static folder
app.mount("/static", StaticFiles(directory="static"), name="static")

# Templates folder
templates = Jinja2Templates(directory="templates")

# --- Routes for pages ---
@app.get("/")
async def index_page(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})

@app.get("/login")
async def login_page(request: Request):
    return templates.TemplateResponse("login.html", {"request": request})

@app.get("/signup")
async def signup_page(request: Request):
    return templates.TemplateResponse("signup.html", {"request": request})

@app.get("/profile")
async def profile(request: Request):
    return templates.TemplateResponse("profile.html", {"request": request})

@app.get("/appoinments")
async def appointments(request: Request):
    return templates.TemplateResponse("appoinments.html", {"request": request})

@app.get("/find_doctor")
async def find_doctor(request: Request):
    return templates.TemplateResponse("find_doctors.html", {"request": request})

@app.get("/book_appoinment")
async def book_appointment(request: Request):
    return templates.TemplateResponse("book_appoinment.html", {"request": request})




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


# --- Form submit ---
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

    return RedirectResponse(url="/appoinments", status_code=303)


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
