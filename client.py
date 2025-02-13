import requests
from fastapi import FastAPI, HTTPException, Query
from pydantic import BaseModel
import json
import os
from fastapi.middleware.cors import CORSMiddleware
from typing import Optional, List
import uvicorn

app = FastAPI()
FILE_PATH = "client.json"  # JSON data file

# Allow frontend requests
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://127.0.0.1:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Load Data from JSON
def load_data():
    if os.path.exists(FILE_PATH):
        with open(FILE_PATH, "r") as file:
            return json.load(file)
    return {"items": []}

# Pydantic Models
class Component(BaseModel):
    id: str
    name: str
    href: str

class Fault(BaseModel):
    code: str
    scope: str
    display_code: str
    fault_name: str
    fault_translation_id: str
    severity: int
    status: dict

class Update(BaseModel):
    operationId: str
    enabled_status: bool

SERVER_BASE_URL = "https://server-client-trial-1.onrender.com"

def fetch_components():
    response = requests.get(f"{SERVER_BASE_URL}/components")
    if response.status_code == 200:
        print("\nComponents:")
        for item in response.json().get("items", []):
            print(f"  - ID: {item['id']}, Name: {item['name']}, Href: {item['href']}")
    else:
        print("\nFailed to fetch components:", response.status_code)

def fetch_operations(component_id):
    response = requests.get(f"{SERVER_BASE_URL}/operations", params={"component_id": component_id})
    if response.status_code == 200:
        print(f"\nEnabled/Disabled Status:")
        for update in response.json().get("items", []):
            if update["enabled_status"]:
                print(f"  - {update['operationId']} is enabled")
                print(f" {update['enabled_status']}")
            else:
                print(f"  - {update['operationId']} is disabled")
    else:
        print(f"\nFailed to fetch operations for {component_id}:", response.status_code, response.json())

@app.get("/faults")
def get_faults(component_id: str = Query(..., description="Component ID")):
    data = load_data()
    component = next((item for item in data["items"] if item["id"] == component_id), None)

    if not component or "faults" not in component:
        raise HTTPException(status_code=404, detail="Component or faults not found")
    
    for item in component["faults"]:
        print(f"  - ID: {item['display_code']}, Name: {item['fault_name']}, Severity: {item['severity']}")
    return {"items": component["faults"]}


if __name__ == "__main__":
    uvicorn.run(app, host="127.0.0.1", port=8001)
    fetch_components()
    fetch_operations("engine")
    get_faults("engine")
