from fastapi import FastAPI, Request, Form
from fastapi.staticfiles import StaticFiles
from fastapi.responses import RedirectResponse , HTMLResponse
from fastapi.templating import Jinja2Templates
from starlette.middleware.sessions import SessionMiddleware 
import uvicorn
from dotenv import load_dotenv
from authlib.integrations.starlette_client import OAuth
import sqlite3
import os

app = FastAPI()
load_dotenv()

CLIENT_ID = os.getenv("GOOGLE_CLIENT_ID")
CLIENT_SECRET = os.getenv("GOOGLE_CLIENT_SECRET")
SECRET_KEY = os.getenv("SESSION_SECRET", "super-secret-session-key")

if not CLIENT_ID or not CLIENT_SECRET:
    raise RuntimeError("Set GOOGLE_CLIENT_ID and GOOGLE_CLIENT_SECRET in environment")


oauth = OAuth()
oauth.register(
    name="google",
    client_id=CLIENT_ID,
    client_secret=CLIENT_SECRET,
    server_metadata_url="https://accounts.google.com/.well-known/openid-configuration",
    client_kwargs={"scope": "openid email profile"},
)


# Secret key for session (random strong string use karna)
app.add_middleware(SessionMiddleware, secret_key="SECRET_KEY")

# Mount static folder
app.mount("/static", StaticFiles(directory="static"), name="static")

# Templates folder
templates = Jinja2Templates(directory="templates")


# --- Routes for pages ---
@app.get("/")
async def index_page(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})



@app.get("/login")
async def login(request: Request):
    # Redirect user to Google authorization URL
    redirect_uri = request.url_for("auth")  
    return await oauth.google.authorize_redirect(request, redirect_uri)

@app.get("/auth")
async def auth(request: Request):
    # Google redirects back here after consent
    token = await oauth.google.authorize_access_token(request)
    # fetch userinfo from userinfo endpoint
    userinfo = await oauth.google.parse_id_token(request, token)  # returns id_token claims if present
    # store minimal user in session
    request.session["user"] = {
        "sub": userinfo.get("sub"),
        "email": userinfo.get("email"),
        "name": userinfo.get("name"),
        "picture": userinfo.get("picture"),
    }
    return RedirectResponse(url="/")    



@app.get("/appoinments")
async def appoinments(request: Request):
    user_email = request.session.get("email")   # 👈 session se email nikalo
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

    #  yahan email session me save ho jaayegi
    request.session["email"] = form.get("email")

    return RedirectResponse(url="/appoinments", status_code=303)


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
