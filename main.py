from fastapi import FastAPI, Request, Form
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from database import get_client
import uuid

app = FastAPI()
app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="templates")

@app.get("/", response_class=HTMLResponse)
async def read_root(request: Request):
    client = get_client()
    vehicles = client.table("vehicles").select("*").eq("is_active", True).execute().data
    parts = client.table("parts").select("*").execute().data
    personnel = client.table("personnel").select("*").execute().data
    vendors = client.table("vendors").select("*").execute().data
    return templates.TemplateResponse(request=request, name="index.html", context={"vehicles": vehicles, "parts": parts, "personnel": personnel, "vendors": vendors})

@app.get("/vehicles/{vehicle_id}", response_class=HTMLResponse)
async def get_vehicle(request: Request, vehicle_id: str):
    client = get_client()
    vehicle = client.table("vehicles").select("*").eq("id", vehicle_id).single().execute().data
    
    fuel_logs = client.table("fuel_logs").select("*").eq("vehicle_id", vehicle_id).order("log_date", desc=True).execute().data
    service_logs = client.table("service_log").select("*").eq("vehicle_id", vehicle_id).order("service_date", desc=True).execute().data
    service_schedule = client.table("service_schedule").select("*").eq("vehicle_id", vehicle_id).execute().data
    
    return templates.TemplateResponse(request=request, name="vehicle_detail.html", context={
        "vehicle": vehicle, 
        "fuel_logs": fuel_logs, 
        "service_logs": service_logs,
        "service_schedule": service_schedule
    })

@app.post("/vehicles/new")
async def create_vehicle(
    vehicle_number: str = Form(...),
    name: str = Form(...),
    model_year: int = Form(None),
    make: str = Form(None),
    model: str = Form(None),
    vin: str = Form(None),
    odometer: float = Form(0),
    color: str = Form(None),
    driver: str = Form(None),
    department: str = Form(None),
    vehicle_type: str = Form(None),
    plate_tag: str = Form(None),
    renewal_date: str = Form(None),
    insurance_company: str = Form(None),
    insurance_account: str = Form(None),
    insurance_premium: float = Form(None),
    insurance_due: str = Form(None),
    engine: str = Form(None),
    transmission: str = Form(None),
    tire_size: str = Form(None),
    notes: str = Form(None)
):
    client = get_client()
    data = {
        "id": str(uuid.uuid4()),
        "vehicle_number": vehicle_number,
        "name": name,
        "model_year": model_year,
        "make": make,
        "model": model,
        "vin": vin,
        "odometer": odometer,
        "color": color,
        "driver": driver,
        "department": department,
        "vehicle_type": vehicle_type,
        "plate_tag": plate_tag,
        "renewal_date": renewal_date,
        "insurance_company": insurance_company,
        "insurance_account": insurance_account,
        "insurance_premium": insurance_premium,
        "insurance_due": insurance_due,
        "engine": engine,
        "transmission": transmission,
        "tire_size": tire_size,
        "notes": notes
    }
    client.table("vehicles").insert(data).execute()
    return RedirectResponse("/", status_code=303)

@app.post("/fuel/add")
async def add_fuel_log(
    vehicle_id: str = Form(...),
    log_date: str = Form(...),
    odometer: float = Form(...),
    gallons: float = Form(...),
    price_per_gallon: float = Form(...),
    total_cost: float = Form(...),
    fuel_type: str = Form(None),
    notes: str = Form(None)
):
    client = get_client()
    data = {
        "vehicle_id": vehicle_id,
        "log_date": log_date,
        "odometer": odometer,
        "gallons": gallons,
        "price_per_gallon": price_per_gallon,
        "total_cost": total_cost,
        "fuel_type": fuel_type,
        "notes": notes
    }
    client.table("fuel_logs").insert(data).execute()
    return RedirectResponse(f"/vehicles/{vehicle_id}", status_code=303)

@app.post("/service/add")
async def add_service_log(
    vehicle_id: str = Form(...),
    service_date: str = Form(...),
    odometer: float = Form(...),
    service_type: str = Form(...),
    vendor: str = Form(None),
    cost: float = Form(None),
    notes: str = Form(None)
):
    client = get_client()
    data = {
        "vehicle_id": vehicle_id,
        "service_date": service_date,
        "odometer": odometer,
        "service_type": service_type,
        "vendor": vendor,
        "cost": cost,
        "notes": notes
    }
    client.table("service_log").insert(data).execute()
    return RedirectResponse(f"/vehicles/{vehicle_id}", status_code=303)
