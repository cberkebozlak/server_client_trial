from fastapi import Body, FastAPI, HTTPException, Query
from pydantic import BaseModel
import json
import os
from fastapi.middleware.cors import CORSMiddleware
from typing import Optional, List
import requests
import uvicorn

app = FastAPI()
FILE_PATH = "server.json"  # JSON data file

# Frontend requestleri için izin verir
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allow all origins (for testing; restrict in production)
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# server.json dosyasındaki datanın tümünü döndüren bir fonksiyon
def load_data():
    if os.path.exists(FILE_PATH):
        with open(FILE_PATH, "r") as file:
            return json.load(file)
    return {"items": []}

def save_data(data):
    with open(FILE_PATH, "w") as file:
        json.dump(data, file, indent=2)

# Pydantic Models, aracın özelliklerinin formatı için bir base
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

class OperationUpdate(BaseModel):
    operationId: str
    enabled_status: bool

CLIENT_BASE_URL = "https://server-client-trial.onrender.com"


@app.put("/operations")
def update_operations(
    component_id: str = Query(..., description="Component ID"),
    update: OperationUpdate = Body(...),
):
    data = load_data()
    component = next((item for item in data["items"] if item["id"] == component_id), None)
    
    if not component or "operation_update" not in component:
        raise HTTPException(status_code=404, detail="Component or operation update not found")
    
    # Find and update the specific operation
    operation = next(
        (op for op in component["operation_update"] if op["operationId"] == update.operationId),
        None
    )
    
    if not operation:
        raise HTTPException(status_code=404, detail="Operation not found")
    
    operation["enabled_status"] = update.enabled_status
    save_data(data)
    
    return {"message": "Operation updated successfully", "operation": operation}

@app.get("/components")
def get_components(component_id: Optional[str] = Query(None, description="Component ID (optional)")):
    data = load_data()

    #tüm componentler için 
    filtered_components = [
        {"id": item["id"], "name": item["name"], "href": item["href"]}
        for item in data["items"]
    ]

    if not component_id:
        return {"items": filtered_components}

    # id belirtilen component için
    component = next((item for item in filtered_components if item["id"] == component_id), None)
    if not component:
        raise HTTPException(status_code=404, detail="Component not found")

    return component


#operation update server.json'dan alınacağı için client.py'a erişmeye gerek yok
@app.get("/operations")
def get_operations(component_id: str = Query(..., description="Component ID")):
    data = load_data()
    component = next((item for item in data["items"] if item["id"] == component_id), None)

    if not component or "operation_update" not in component:
        raise HTTPException(status_code=404, detail="Component or operation update not found")

    return {"items": component["operation_update"]}

@app.get("/faults")
def get_faults(component_id: str = Query(..., description="Component ID")):
    response = requests.get(f"{CLIENT_BASE_URL}/faults", params={"component_id": component_id})
    #faults client.json'dan client.py ile çekilir sonrasında request fonks ile server.py'a yollanır. server API'ı UI'da veriyi gösterir
    if response.status_code == 200:
        return response.json()
    else:
        raise HTTPException(status_code=response.status_code, detail="Failed to fetch faults from client")

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)


