from fastapi import FastAPI, Request
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from fastapi.templating import Jinja2Templates
import uvicorn

app = FastAPI()

# Mount static folder
app.mount("/static", StaticFiles(directory="static"), name="static")

# Templates folder
templates = Jinja2Templates(directory="templates")

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
async def appoinments(request: Request):
    return templates.TemplateResponse("appoinments.html", {"request": request})

@app.get("/find_doctor")
async def find_doctor(request: Request):
    return templates.TemplateResponse("find_doctors.html", {"request": request})

    

@app.get("/book_appoinment")
async def book_appoinment(request: Request):
    return templates.TemplateResponse("book_appoinment.html", {"request": request})





if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
