from fastapi import FastAPI, Form, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates

from security import verify_recaptcha, check_fingerprint

from db import run_query
from tasks import insert_user

app = FastAPI()
templates = Jinja2Templates(directory="templates")


@app.get("/")
def hello_world():
    return {"message": "Hello, World!"}


@app.get("/form_sync", response_class=HTMLResponse)
def form_sync_get(request: Request):
    return templates.TemplateResponse(request=request, name="form_sync.html")


@app.post('/form_sync')
def form_sync_post(fname: str = Form(...), lname: str = Form(...), website: str = Form(None),
                   fingerprint: str = Form(None), captcha: str = Form(..., alias="g-recaptcha-response")):
    if website:
        return {"error": "Bot detected"}
    if not verify_recaptcha(captcha):
        return {"error": "Invalid CAPTCHA"}
    if fingerprint and not check_fingerprint(fingerprint):
        return {"error": "Too many submissions from this device, are you a bot?"}
    run_query("INSERT INTO users (first_name, last_name, fingerprint_js) VALUES (%s, %s, %s)",
              (fname, lname, fingerprint))
    return {"message": f"{fname} {lname} successfully inserted"}


@app.get('/form_async', response_class=HTMLResponse)
def form_async_get(request: Request):
    return templates.TemplateResponse(request=request, name="form_async.html")


@app.post('/form_async')
def form_async_post(fname: str = Form(...), lname: str = Form(...), website: str = Form(None),
                    fingerprint: str = Form(None), captcha: str = Form(..., alias="g-recaptcha-response")):
    print("Captcha token received:", repr(captcha))
    if website:
        return {"error": "Bot detected"}
    if not verify_recaptcha(captcha):
        return {"error": "Invalid CAPTCHA"}
    if fingerprint and not check_fingerprint(fingerprint):
        return {"error": "Too many submissions from this device, are you a bot?"}
    insert_user.delay(fname, lname, fingerprint)
    return {"message": f"{fname} {lname} queued for insertion"}
