import requests
from fastapi import FastAPI, HTTPException, Query
from pydantic import BaseModel
import json
import os
from fastapi.middleware.cors import CORSMiddleware
from typing import Optional, List
import uvicorn

app = FastAPI()
FILE_PATH = "client.json"

app.add_middleware(
    CORSMiddleware,
    allow_origins=["https://server-client-trial.onrender.com", "https://server-client-trial-1.onrender.com"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

SERVER_BASE_URL = "https://server-client-trial.onrender.com"

def load_data():
    if os.path.exists(FILE_PATH):
        with open(FILE_PATH, "r") as file:
            return json.load(file)
    return {"items": []}

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
            print(f"  - {update['operationId']} is {'enabled' if update['enabled_status'] else 'disabled'}")
    else:
        print(f"\nFailed to fetch operations for {component_id}:", response.status_code, response.json())

@app.get("/faults")
def get_faults(component_id: str = Query(..., description="Component ID")):
    data = load_data()
    component = next((item for item in data["items"] if item["id"] == component_id), None)

    if not component or "faults" not in component:
        raise HTTPException(status_code=404, detail="Component or faults not found")
    
    return {"items": component["faults"]}

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=10001)
    fetch_components()
    fetch_operations("engine")
    get_faults("engine")
