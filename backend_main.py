"""
Society Management System - FastAPI Backend
Run with: uvicorn main:app --reload
Install: pip install fastapi uvicorn python-multipart
"""

from fastapi import FastAPI, HTTPException, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime
import uuid
import json

app = FastAPI(title="Society Management System API")

@app.get("/")
def home():
    return {"message": "Society Management API is running"}

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ─── In-Memory DB (replace with SQLite/PostgreSQL in production) ───

db = {
    "towers": [
        {"id": "t1", "name": "Tower A", "floors": 10, "flats_per_floor": 4, "year_built": 2018, "amenities": ["Gym", "Swimming Pool"]},
        {"id": "t2", "name": "Tower B", "floors": 8, "flats_per_floor": 4, "year_built": 2020, "amenities": ["Parking", "Garden"]}
    ],
    "flats": [
        {"id": "f1", "tower_id": "t1", "flat_number": "A-101", "floor": 1, "status": "owned", "owner_id": "o1", "area_sqft": 1200, "bedrooms": 2},
        {"id": "f2", "tower_id": "t1", "flat_number": "A-102", "floor": 1, "status": "owned", "owner_id": "o2", "area_sqft": 1500, "bedrooms": 3},
        {"id": "f3", "tower_id": "t1", "flat_number": "A-201", "floor": 2, "status": "unsold", "owner_id": None, "area_sqft": 1200, "bedrooms": 2},
        {"id": "f4", "tower_id": "t1", "flat_number": "A-202", "floor": 2, "status": "rented", "owner_id": "o3", "area_sqft": 900, "bedrooms": 1},
        {"id": "f5", "tower_id": "t2", "flat_number": "B-101", "floor": 1, "status": "owned", "owner_id": "o4", "area_sqft": 1800, "bedrooms": 3},
        {"id": "f6", "tower_id": "t2", "flat_number": "B-102", "floor": 1, "status": "unsold", "owner_id": None, "area_sqft": 1200, "bedrooms": 2},
    ],
    "owners": [
        {"id": "o1", "name": "Rajesh Kumar", "phone": "+91-9876543210", "email": "rajesh@email.com", "flat_id": "f1", "move_in": "2019-03-15", "dues": 0},
        {"id": "o2", "name": "Priya Sharma", "phone": "+91-9876543211", "email": "priya@email.com", "flat_id": "f2", "move_in": "2020-01-10", "dues": 2500},
        {"id": "o3", "name": "Amit Singh", "phone": "+91-9876543212", "email": "amit@email.com", "flat_id": "f4", "move_in": "2021-06-01", "dues": 0},
        {"id": "o4", "name": "Sunita Patel", "phone": "+91-9876543213", "email": "sunita@email.com", "flat_id": "f5", "move_in": "2020-11-20", "dues": 5000},
    ],
    "visitors": [
        {"id": "v1", "name": "Ravi Mehta", "phone": "+91-9000000001", "purpose": "Delivery", "flat_id": "f1", "status": "approved", "check_in": "2024-03-13T10:00:00", "check_out": "2024-03-13T10:30:00", "guard_note": "Parcel delivered"},
        {"id": "v2", "name": "Deepika Joshi", "phone": "+91-9000000002", "purpose": "Guest", "flat_id": "f2", "status": "pending", "check_in": None, "check_out": None, "guard_note": ""},
    ],
    "maintenance": [
        {"id": "m1", "title": "Elevator Malfunction", "area": "Tower A", "priority": "high", "status": "open", "reported": "2024-03-12", "assigned_to": "Electrician Team", "description": "Elevator 1 not working on floor 3-5"},
        {"id": "m2", "title": "Water Pump Issue", "area": "Common Area", "priority": "critical", "status": "in_progress", "reported": "2024-03-11", "assigned_to": "Plumber Team", "description": "Low water pressure in Block B"},
        {"id": "m3", "title": "Garden Light Repair", "area": "Garden", "priority": "low", "status": "resolved", "reported": "2024-03-10", "assigned_to": "Electrical", "description": "3 lights not working near gate"},
    ],
    "notices": [
        {"id": "n1", "title": "Water Supply Shutdown", "message": "Water will be shut for maintenance on 15th March 9am-1pm", "date": "2024-03-13", "priority": "high"},
        {"id": "n2", "title": "Society Meeting", "message": "Annual general body meeting on 20th March at 6pm in Community Hall", "date": "2024-03-13", "priority": "normal"},
    ],
    "expenses": [
        {"id": "e1", "category": "Maintenance", "amount": 15000, "date": "2024-03-01", "description": "Monthly elevator maintenance"},
        {"id": "e2", "category": "Security", "amount": 45000, "date": "2024-03-01", "description": "Security staff salaries"},
        {"id": "e3", "category": "Utilities", "amount": 8500, "date": "2024-03-05", "description": "Common area electricity"},
    ]
}


# ─── Models ───

class Tower(BaseModel):
    name: str
    floors: int
    flats_per_floor: int
    year_built: int
    amenities: List[str] = []

class Flat(BaseModel):
    tower_id: str
    flat_number: str
    floor: int
    status: str = "unsold"
    owner_id: Optional[str] = None
    area_sqft: int
    bedrooms: int

class Owner(BaseModel):
    name: str
    phone: str
    email: str
    flat_id: str
    move_in: str
    dues: float = 0

class VisitorRequest(BaseModel):
    name: str
    phone: str
    purpose: str
    flat_id: str
    guard_note: str = ""

class MaintenanceRequest(BaseModel):
    title: str
    area: str
    priority: str
    description: str
    assigned_to: str = ""

class Notice(BaseModel):
    title: str
    message: str
    priority: str = "normal"

class Expense(BaseModel):
    category: str
    amount: float
    description: str


# ─── Tower Routes ───

@app.get("/towers")
def get_towers():
    return db["towers"]

@app.post("/towers")
def add_tower(tower: Tower):
    new = {"id": str(uuid.uuid4())[:8], **tower.dict()}
    db["towers"].append(new)
    return new

@app.delete("/towers/{tower_id}")
def delete_tower(tower_id: str):
    db["towers"] = [t for t in db["towers"] if t["id"] != tower_id]
    return {"ok": True}


# ─── Flat Routes ───

@app.get("/flats")
def get_flats(tower_id: Optional[str] = None):
    flats = db["flats"]
    if tower_id:
        flats = [f for f in flats if f["tower_id"] == tower_id]
    return flats

@app.post("/flats")
def add_flat(flat: Flat):
    new = {"id": str(uuid.uuid4())[:8], **flat.dict()}
    db["flats"].append(new)
    return new

@app.patch("/flats/{flat_id}")
def update_flat(flat_id: str, data: dict):
    for flat in db["flats"]:
        if flat["id"] == flat_id:
            flat.update(data)
            return flat
    raise HTTPException(404, "Flat not found")


# ─── Owner Routes ───

@app.get("/owners")
def get_owners():
    enriched = []
    for o in db["owners"]:
        flat = next((f for f in db["flats"] if f["id"] == o["flat_id"]), None)
        enriched.append({**o, "flat": flat})
    return enriched

@app.post("/owners")
def add_owner(owner: Owner):
    new = {"id": str(uuid.uuid4())[:8], **owner.dict()}
    db["owners"].append(new)
    # Update flat status
    for flat in db["flats"]:
        if flat["id"] == owner.flat_id:
            flat["owner_id"] = new["id"]
            flat["status"] = "owned"
    return new

@app.get("/owners/{owner_id}")
def get_owner(owner_id: str):
    owner = next((o for o in db["owners"] if o["id"] == owner_id), None)
    if not owner:
        raise HTTPException(404, "Owner not found")
    flat = next((f for f in db["flats"] if f["id"] == owner["flat_id"]), None)
    return {**owner, "flat": flat}


# ─── Visitor Routes ───

@app.get("/visitors")
def get_visitors():
    enriched = []
    for v in db["visitors"]:
        flat = next((f for f in db["flats"] if f["id"] == v["flat_id"]), None)
        owner = next((o for o in db["owners"] if flat and o["flat_id"] == flat["id"]), None)
        enriched.append({**v, "flat": flat, "owner": owner})
    return enriched

@app.post("/visitors")
def add_visitor(visitor: VisitorRequest):
    new = {
        "id": str(uuid.uuid4())[:8],
        **visitor.dict(),
        "status": "pending",
        "check_in": None,
        "check_out": None,
        "requested_at": datetime.now().isoformat()
    }
    db["visitors"].append(new)
    return new

@app.patch("/visitors/{visitor_id}/approve")
def approve_visitor(visitor_id: str):
    for v in db["visitors"]:
        if v["id"] == visitor_id:
            v["status"] = "approved"
            v["check_in"] = datetime.now().isoformat()
            return v
    raise HTTPException(404, "Visitor not found")

@app.patch("/visitors/{visitor_id}/deny")
def deny_visitor(visitor_id: str):
    for v in db["visitors"]:
        if v["id"] == visitor_id:
            v["status"] = "denied"
            return v
    raise HTTPException(404, "Visitor not found")

@app.patch("/visitors/{visitor_id}/checkout")
def checkout_visitor(visitor_id: str):
    for v in db["visitors"]:
        if v["id"] == visitor_id:
            v["status"] = "checked_out"
            v["check_out"] = datetime.now().isoformat()
            return v
    raise HTTPException(404, "Visitor not found")


# ─── Maintenance Routes ───

@app.get("/maintenance")
def get_maintenance():
    return db["maintenance"]

@app.post("/maintenance")
def add_maintenance(req: MaintenanceRequest):
    new = {
        "id": str(uuid.uuid4())[:8],
        **req.dict(),
        "status": "open",
        "reported": datetime.now().strftime("%Y-%m-%d")
    }
    db["maintenance"].append(new)
    return new

@app.patch("/maintenance/{req_id}")
def update_maintenance(req_id: str, data: dict):
    for m in db["maintenance"]:
        if m["id"] == req_id:
            m.update(data)
            return m
    raise HTTPException(404, "Request not found")


# ─── Notice Routes ───

@app.get("/notices")
def get_notices():
    return db["notices"]

@app.post("/notices")
def add_notice(notice: Notice):
    new = {
        "id": str(uuid.uuid4())[:8],
        **notice.dict(),
        "date": datetime.now().strftime("%Y-%m-%d")
    }
    db["notices"].append(new)
    return new


# ─── Expense Routes ───

@app.get("/expenses")
def get_expenses():
    return db["expenses"]

@app.post("/expenses")
def add_expense(expense: Expense):
    new = {
        "id": str(uuid.uuid4())[:8],
        **expense.dict(),
        "date": datetime.now().strftime("%Y-%m-%d")
    }
    db["expenses"].append(new)
    return new


# ─── AI / Analytics Endpoints ───

@app.get("/ai/insights")
def get_ai_insights():
    """AI-powered society health analysis"""
    total_flats = len(db["flats"])
    unsold = len([f for f in db["flats"] if f["status"] == "unsold"])
    critical_maintenance = [m for m in db["maintenance"] if m["priority"] == "critical" and m["status"] != "resolved"]
    pending_visitors = [v for v in db["visitors"] if v["status"] == "pending"]
    overdue_dues = [o for o in db["owners"] if o["dues"] > 0]
    open_maintenance = [m for m in db["maintenance"] if m["status"] == "open"]

    insights = []

    if critical_maintenance:
        insights.append({
            "type": "critical",
            "icon": "alert",
            "title": f"{len(critical_maintenance)} Critical Maintenance Issue(s)",
            "detail": ", ".join([m["title"] for m in critical_maintenance]),
            "action": "View Maintenance"
        })

    if pending_visitors:
        insights.append({
            "type": "warning",
            "icon": "visitor",
            "title": f"{len(pending_visitors)} Visitor(s) Awaiting Approval",
            "detail": "Pending gate entry requests need attention",
            "action": "Review Visitors"
        })

    if overdue_dues:
        total_dues = sum(o["dues"] for o in overdue_dues)
        insights.append({
            "type": "warning",
            "icon": "money",
            "title": f"₹{total_dues:,} in Outstanding Dues",
            "detail": f"{len(overdue_dues)} resident(s) have pending payments",
            "action": "View Owners"
        })

    if unsold > 0:
        pct = round((unsold / total_flats) * 100)
        insights.append({
            "type": "info",
            "icon": "flat",
            "title": f"{unsold} Unsold Flat(s) ({pct}% vacant)",
            "detail": "Consider marketing these units",
            "action": "View Flats"
        })

    if open_maintenance:
        insights.append({
            "type": "info",
            "icon": "tool",
            "title": f"{len(open_maintenance)} Open Maintenance Request(s)",
            "detail": "Areas requiring repair attention",
            "action": "View Maintenance"
        })

    if not insights:
        insights.append({
            "type": "success",
            "icon": "check",
            "title": "Society is running smoothly!",
            "detail": "No critical issues detected",
            "action": None
        })

    return {
        "insights": insights,
        "health_score": max(0, 100 - len(critical_maintenance)*30 - len(pending_visitors)*5 - len(open_maintenance)*10),
        "generated_at": datetime.now().isoformat()
    }

@app.get("/dashboard/stats")
def get_dashboard_stats():
    total_flats = len(db["flats"])
    return {
        "total_towers": len(db["towers"]),
        "total_flats": total_flats,
        "occupied_flats": len([f for f in db["flats"] if f["status"] in ["owned", "rented"]]),
        "unsold_flats": len([f for f in db["flats"] if f["status"] == "unsold"]),
        "total_residents": len(db["owners"]),
        "pending_visitors": len([v for v in db["visitors"] if v["status"] == "pending"]),
        "open_maintenance": len([m for m in db["maintenance"] if m["status"] == "open"]),
        "critical_issues": len([m for m in db["maintenance"] if m["priority"] == "critical" and m["status"] != "resolved"]),
        "total_dues": sum(o["dues"] for o in db["owners"]),
        "monthly_expenses": sum(e["amount"] for e in db["expenses"]),
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
