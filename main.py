import os
from fastapi import FastAPI, Request, Form, Depends
from fastapi.responses import HTMLResponse, RedirectResponse, JSONResponse
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
from sqlalchemy.orm import Session
from starlette.middleware.sessions import SessionMiddleware

from database import Base, engine, SessionLocal
from auth import register_user, authenticate_user
from models import User, UserSettings

# --------------------------------------------------
# APP
# --------------------------------------------------

app = FastAPI()

app.add_middleware(
    SessionMiddleware,
    secret_key="super-secret-key-change-this"
)

# --------------------------------------------------
# PATHS
# --------------------------------------------------

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
STATIC_DIR = os.path.join(BASE_DIR, "static")
TEMPLATE_DIR = os.path.join(BASE_DIR, "templates")

if os.path.isdir(STATIC_DIR):
    app.mount("/static", StaticFiles(directory=STATIC_DIR), name="static")

templates = Jinja2Templates(directory=TEMPLATE_DIR)

# --------------------------------------------------
# DATABASE
# --------------------------------------------------

Base.metadata.create_all(bind=engine)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# --------------------------------------------------
# PAGES (GET)
# --------------------------------------------------

@app.get("/", response_class=HTMLResponse)
def login_page(request: Request):
    return templates.TemplateResponse(
        "login.html",
        {"request": request, "error": None}
    )

@app.get("/register", response_class=HTMLResponse)
def register_page(request: Request):
    return templates.TemplateResponse(
        "register.html",
        {"request": request, "error": None}
    )

@app.get("/dashboard", response_class=HTMLResponse)
def dashboard_page(request: Request, db: Session = Depends(get_db)):
    user_id = request.session.get("user_id")
    if not user_id:
        return RedirectResponse(url="/", status_code=302)

    settings = db.query(UserSettings).filter(
        UserSettings.user_id == user_id
    ).first()

    return templates.TemplateResponse(
        "dashboard.html",
        {
            "request": request,
            "groq_key": settings.groq_api_key if settings else "",
            "resume_text": settings.resume_text if settings else ""
        }
    )

# --------------------------------------------------
# AUTH (POST)
# --------------------------------------------------

@app.post("/register")
def register(
    request: Request,
    name: str = Form(...),
    email: str = Form(...),
    password: str = Form(...),
    db: Session = Depends(get_db)
):
    if db.query(User).filter(User.email == email).first():
        return templates.TemplateResponse(
            "register.html",
            {"request": request, "error": "User already exists"}
        )

    register_user(db, name, email, password)
    return RedirectResponse(url="/", status_code=302)

@app.post("/login")
def login(
    request: Request,
    email: str = Form(...),
    password: str = Form(...),
    db: Session = Depends(get_db)
):
    user = authenticate_user(db, email, password)
    if not user:
        return templates.TemplateResponse(
            "login.html",
            {"request": request, "error": "Invalid email or password"}
        )

    request.session["user_id"] = user.id
    return RedirectResponse(url="/dashboard", status_code=302)

@app.get("/logout")
def logout(request: Request):
    request.session.clear()   # ❗ does NOT delete DB data
    return RedirectResponse(url="/", status_code=302)

# --------------------------------------------------
# USER SETTINGS (POST)
# --------------------------------------------------

@app.post("/save-groq-key")
def save_groq_key(
    request: Request,
    key: str = Form(...),
    db: Session = Depends(get_db)
):
    user_id = request.session.get("user_id")
    if not user_id:
        return JSONResponse({"error": "unauthorized"}, status_code=401)

    settings = db.query(UserSettings).filter(
        UserSettings.user_id == user_id
    ).first()

    if not settings:
        settings = UserSettings(user_id=user_id)

    settings.groq_api_key = key
    db.add(settings)
    db.commit()

    return {"status": "ok"}


@app.post("/delete-groq-key")
def delete_groq_key(request: Request, db: Session = Depends(get_db)):
    user_id = request.session["user_id"]

    settings = db.query(UserSettings).filter(
        UserSettings.user_id == user_id
    ).first()

    if settings:
        settings.groq_api_key = None
        db.commit()

    return {"status": "ok"}


@app.post("/save-resume")
def save_resume(
    request: Request,
    resume: str = Form(...),
    db: Session = Depends(get_db)
):
    user_id = request.session.get("user_id")
    if not user_id:
        return JSONResponse({"error": "unauthorized"}, status_code=401)

    settings = db.query(UserSettings).filter(
        UserSettings.user_id == user_id
    ).first()

    if not settings:
        settings = UserSettings(user_id=user_id)

    settings.resume_text = resume
    db.add(settings)
    db.commit()

    return {"status": "ok"}


@app.post("/save-groq-key")
def save_groq_key(
    request: Request,
    key: str = Form(...),
    db: Session = Depends(get_db)
):
    user_id = request.session["user_id"]

    settings = db.query(UserSettings).filter(
        UserSettings.user_id == user_id
    ).first()

    if not settings:
        settings = UserSettings(user_id=user_id)

    settings.groq_api_key = key
    db.add(settings)
    db.commit()

    return {"status": "ok"}





@app.post("/delete-resume")
def delete_resume(
    request: Request,
    db: Session = Depends(get_db)
):
    user_id = request.session.get("user_id")
    if not user_id:
        return JSONResponse({"error": "unauthorized"}, status_code=401)

    settings = db.query(UserSettings).filter(
        UserSettings.user_id == user_id
    ).first()

    if settings:
        settings.resume_text = None
        db.commit()

    return {"status": "deleted"}
