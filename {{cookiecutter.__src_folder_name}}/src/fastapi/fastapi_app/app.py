import os
import pathlib

from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
{% if "postgres" in cookiecutter.db_resource %}
from sqlmodel import Session, select

from .models import Cruise, Destination, InfoRequest, engine
{% endif %}
{% if "mongodb" in cookiecutter.db_resource %}
from .models import Cruise, Destination, InfoRequest, init_db
{% endif %}

{% if "mongodb" in cookiecutter.db_resource %}
if os.environ.get("RUNNING_IN_PRODUCTION"):
    DATABASE_URI = os.environ.get("AZURE_COSMOS_CONNECTION_STRING")
else:
    dbuser = os.environ["MONGODB_USERNAME"]
    dbpass = os.environ["MONGODB_PASSWORD"]
    dbhost = os.environ["MONGODB_HOST"]
    dbname = os.environ["MONGODB_DATABASE"]
    DATABASE_URI  = f"mongodb://{dbuser}:{dbpass}@{dbhost}/{dbname}?authSource=admin"
{% endif %}

app = FastAPI()
{% if "mongodb" in cookiecutter.db_resource %}
@app.on_event("startup")
async def startup():
    await init_db()
{% endif %}

parent_path = pathlib.Path(__file__).parent.parent
app.mount("/mount", StaticFiles(directory=parent_path / "static"), name="static")
templates = Jinja2Templates(directory=parent_path / "templates")
templates.env.globals["prod"] = os.environ.get("RUNNING_IN_PRODUCTION", False)


@app.get("/", response_class=HTMLResponse)
def index(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})


@app.get("/about", response_class=HTMLResponse)
def about(request: Request):
    return templates.TemplateResponse("about.html", {"request": request})


@app.get("/destinations", response_class=HTMLResponse)
def destinations(request: Request):
    {% if "postgres" in cookiecutter.db_resource %}
    with Session(engine) as session:
        all_destinations = session.exec(select(Destination)).all()
    {% endif %}
    {% if "mongodb" in cookiecutter.db_resource %}
    all_destinations = await Destination.all()
    {% endif %}
    return templates.TemplateResponse("destinations.html", {"request": request, "destinations": all_destinations})


@app.get("/destination/{pk}", response_class=HTMLResponse)
def destination_detail(request: Request, pk: any):
    {% if "postgres" in cookiecutter.db_resource %}
    with Session(engine) as session:
        destination = session.exec(select(Destination).where(Destination.id == pk)).first()
    {% endif %}
    {% if "mongo" in cookiecutter.db_resource %}
    destination = await Destination.get(pk) 
    {% endif %}
    return templates.TemplateResponse("destination_detail.html", {"request": request, "destination": destination})


@app.get("/cruise/{pk}")
def cruise_detail(request: Request, pk: any):
    {% if "postgres" in cookiecutter.db_resource %}
    with Session(engine) as session:
        cruise = session.exec(select(Cruise).where(Cruise.id == pk)).first()
    {% endif %}
    {% if "mongo" in cookiecutter.db_resource %}
    cruise = await Cruise.get(pk) 
    {% endif %}

    return templates.TemplateResponse("cruise_detail.html", {"request": request, "cruise": cruise})
@app.get("/info_request/", response_class=HTMLResponse)
def info_request(request: Request):
    return templates.TemplateResponse("info_request_create.html", {"request": request})


@app.post("/info_request/", response_model=InfoRequest)
def create_info_request(info_request: InfoRequest):
    {% if "postgres" in cookiecutter.db_resource %}
    with Session(engine) as session:
        db_info_request = InfoRequest.from_orm(info_request)
        session.add(db_info_request)
        session.commit()
        session.refresh(db_info_request)
    {% endif %}
    {% if "mongo" in cookiecutter.db_resource %}
    db_info_request = await InfoRequest.create(**info_request)
    {% endif %}
    return db_info_request
