from fastapi import FastAPI, Form, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates

from db import get_connection, run_query
from tasks import insert_user

app = FastAPI()
templates = Jinja2Templates(directory="templates")


@app.get("/")
def hello_world():
    return {"message": "Hello, World!"}


@app.get("/form_sync", response_class=HTMLResponse)
def form_sync_get(request: Request):
    print("TEMPLATE OK:", templates)
    return templates.TemplateResponse(request=request, name="form_sync.html")


@app.post('/form_sync')
def form_sync_post(fname: str = Form(...), lname: str = Form(...)):
    run_query("INSERT INTO users (first_name, last_name) VALUES (%s, %s)", (fname, lname))
    return {"message": f"{fname} {lname} successfully inserted"}


@app.get('/form_async', response_class=HTMLResponse)
def form_async_get(request: Request):
    return templates.TemplateResponse(request=request, name="form_async.html")


@app.post('/form_async')
def form_async_post(fname: str = Form(...), lname: str = Form(...)):
    insert_user.delay(fname, lname)
    return {"message": f"{fname} {lname} queued for insertion"}
