# main.py

from fastapi import FastAPI, Path, HTTPException, Query
from fastapi.responses import JSONResponse
from pydantic import BaseModel, Field, computed_field
from typing import Annotated, Literal, Optional
import json

app = FastAPI() #Defining app variable from Class

# Defining Pydantic class
class Patient(BaseModel):
    id: Annotated[str, Field(..., description='ID of the patient', examples=['P001'])]
    name: Annotated[str, Field(..., description='Name of the patient')]
    city: Annotated[str, Field(..., description='City where the patient is living')]
    age: Annotated[int, Field(..., gt=0, lt=120, description='Age of the patient')]
    gender: Annotated[Literal['male', 'female', 'others'], Field(..., description='Gender of the patient')]
    height: Annotated[float, Field(..., gt=0, description='Height of the patient in mtrs')]
    weight: Annotated[float, Field(..., gt=0, description='Weight of the patient in kgs')]

    @computed_field
    @property
    def bmi(self) -> float:
        bmi = round(self.weight/(self.height**2),2)
        return bmi
    
    @computed_field
    @property
    def verdict(self) -> str:

        if self.bmi < 18.5:
            return 'Underweight'
        elif self.bmi < 25:
            return 'Normal'
        elif self.bmi < 30:
            return 'Normal'
        else:
            return 'Obese'

# Creating update Pydantic model
class PatientUpdate(BaseModel):
    name: Annotated[Optional[str], Field(default=None)]
    city: Annotated[Optional[str], Field(default=None)]
    age: Annotated[Optional[str], Field(default=None, gt=0)]
    gender: Annotated[Optional[Literal['male', 'female']], Field(default=None)]
    height: Annotated[Optional[float], Field(default=None, gt=0)]
    weight: Annotated[Optional[float], Field(default=None, gt=0)]


# Helper function to retirive patient data from json file
def load_data():
    with open('patients.json', 'r') as f:
        data = json.load(f) 
    return data

def save_data(data): # Function that takes Dict, and dumps to JSON file
    with open('patients.json', 'w') as f:
        json.dump(data, f)

@app.get("/") # Defining Route/Endpoint
def hello():
    return {'message': 'Hello Patient Management System API'} # Defined a Function for the "/" endpoint

@app.get('/about')
def about():
    return {'message': 'A Fully Functional API to manage your patient records'}

@app.get('/view')
def view():
    data = load_data()
    return data

@app.get('/patient/{patient_id}')
def view_patient(patient_id: str):
    # Load all the patients records
    data = load_data() # Defined above

    patient_id = patient_id.upper()  # Make lookup case-insensitive
    
    if patient_id in data:
        return data[patient_id]
    return {'error': 'patient not found'}

# Defining POST | Create Endpoint
@app.post('/create')
def create_patient(patient: Patient): # Input(patient) is Pydantic Model (Patient) -> Input data is Validated data
    
    # Load exisisting data
    data = load_data()

    # Checking if the patient already exists in the DB
    if patient.id in data:
        raise HTTPException(status_code=400, detail='Patient already exists')

    # If not exists then add new patient to the DB
    # We will have to convert the Input data which is Pydatic object to a dictionary (using mode_dump)
    data[patient.id] = patient.model_dump(exclude=['id'])

    # Saving the dict to Json File using save_data()
    save_data(data)

    # Returning a response
    return JSONResponse(status_code=201, content={'message':'patient created successfully'})

# Defining Endpoints to edit the details
