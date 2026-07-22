from fastapi import FastAPI, Request, Form, UploadFile, File
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from database import get_client
import uuid
import os

app = FastAPI()
app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="templates")

@app.get("/", response_class=HTMLResponse)
async def read_root(request: Request):
    client = get_client()
    vehicles = client.table("vehicles").select("*").eq("is_active", True).execute().data
    return templates.TemplateResponse(request=request, name="index.html", context={"vehicles": vehicles})

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
    odometer_unit: str = Form("Kilometres"),
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
        "odometer_unit": odometer_unit,
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

@app.post("/vehicles/{vehicle_id}/upload-photo")
async def upload_photo(vehicle_id: str, file: UploadFile = File(...)):
    client = get_client()
    file_ext = file.filename.split(".")[-1]
    file_name = f"{vehicle_id}.{file_ext}"
    file_bytes = await file.read()

    client.storage.from_("vehicle-photos").upload(file_name, file_bytes, {"content-type": file.content_type})

    url = f"{os.environ.get('SUPABASE_URL')}/storage/v1/object/public/vehicle-photos/{file_name}"

    client.table("vehicles").update({"image_url": url}).eq("id", vehicle_id).execute()

    return RedirectResponse(f"/vehicles/{vehicle_id}", status_code=303)

@app.post("/vehicles/{vehicle_id}/delete-photo")
async def delete_photo(vehicle_id: str):
    client = get_client()
    vehicle = client.table("vehicles").select("image_url").eq("id", vehicle_id).single().execute().data
    if vehicle and vehicle.get("image_url"):
        file_name = vehicle["image_url"].split("/")[-1]
        try:
            client.storage.from_("vehicle-photos").remove([file_name])
        except Exception:
            pass
        client.table("vehicles").update({"image_url": None}).eq("id", vehicle_id).execute()
    return RedirectResponse(f"/vehicles/{vehicle_id}", status_code=303)

@app.post("/vehicles/{vehicle_id}/update")
async def update_vehicle(
    vehicle_id: str,
    vehicle_number: str = Form(None),
    name: str = Form(None),
    model_year: int = Form(None),
    make: str = Form(None),
    model: str = Form(None),
    vin: str = Form(None),
    odometer: float = Form(None),
    odometer_unit: str = Form(None),
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
    data = {k: v for k, v in {
        "vehicle_number": vehicle_number,
        "name": name,
        "model_year": model_year,
        "make": make,
        "model": model,
        "vin": vin,
        "odometer": odometer,
        "odometer_unit": odometer_unit,
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
    }.items() if v is not None}
    if data:
        client.table("vehicles").update(data).eq("id", vehicle_id).execute()
    return RedirectResponse(f"/vehicles/{vehicle_id}", status_code=303)

@app.post("/vehicles/{vehicle_id}/set-inactive")
async def set_inactive(vehicle_id: str):
    client = get_client()
    client.table("vehicles").update({"is_active": False}).eq("id", vehicle_id).execute()
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

@app.post("/service/schedule/add")
async def add_service_schedule(
    vehicle_id: str = Form(...),
    service_type: str = Form(...),
    interval_miles: int = Form(None),
    interval_months: int = Form(None),
    last_service_date: str = Form(None),
    last_service_odometer: float = Form(None)
):
    client = get_client()
    data = {
        "vehicle_id": vehicle_id,
        "service_type": service_type,
        "interval_miles": interval_miles,
        "interval_months": interval_months,
        "last_service_date": last_service_date,
        "last_service_odometer": last_service_odometer
    }
    client.table("service_schedule").insert(data).execute()
    return RedirectResponse(f"/vehicles/{vehicle_id}", status_code=303)

@app.get("/personnel", response_class=HTMLResponse)
async def personnel_page(request: Request):
    client = get_client()
    people = client.table("personnel").select("*").execute().data
    return templates.TemplateResponse(request=request, name="personnel.html", context={"personnel": people})

@app.post("/personnel/new")
async def add_personnel(
    name: str = Form(...),
    role: str = Form(None),
    phone: str = Form(None),
    email: str = Form(None)
):
    client = get_client()
    client.table("personnel").insert({"id": str(uuid.uuid4()), "name": name, "role": role, "phone": phone, "email": email}).execute()
    return RedirectResponse("/personnel", status_code=303)

@app.get("/vendors", response_class=HTMLResponse)
async def vendors_page(request: Request):
    client = get_client()
    vendors_list = client.table("vendors").select("*").execute().data
    return templates.TemplateResponse(request=request, name="vendors.html", context={"vendors": vendors_list})

@app.post("/vendors/new")
async def add_vendor(
    name: str = Form(...),
    contact_person: str = Form(None),
    phone: str = Form(None),
    email: str = Form(None),
    address: str = Form(None)
):
    client = get_client()
    client.table("vendors").insert({"id": str(uuid.uuid4()), "name": name, "contact_person": contact_person, "phone": phone, "email": email, "address": address}).execute()
    return RedirectResponse("/vendors", status_code=303)

@app.get("/parts", response_class=HTMLResponse)
async def parts_page(request: Request):
    client = get_client()
    parts_list = client.table("parts").select("*").execute().data
    return templates.TemplateResponse(request=request, name="parts.html", context={"parts": parts_list})

@app.post("/parts/new")
async def add_part(
    name: str = Form(...),
    part_number: str = Form(None),
    quantity: int = Form(0),
    unit_cost: float = Form(0),
    notes: str = Form(None)
):
    client = get_client()
    client.table("parts").insert({"id": str(uuid.uuid4()), "name": name, "part_number": part_number, "quantity": quantity, "unit_cost": unit_cost, "notes": notes}).execute()
    return RedirectResponse("/parts", status_code=303)
