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
@app.put('/edit/{patient_id}')
def update_patient(patient_id: str, patient_update: PatientUpdate):


    data = load_data() # Using prev defined utility func

    if patient_id not in data:
        raise HTTPException(status_code = 404, detail='Patient Not Found')
    
    existing_patient_info = data[patient_id] # Dictionary

    # Need to udpate Pydantic object (patient_update) to Dict using dump
    updated_patient_info = patient_update.model_dump(exclude_unset=True) # Using exclude to get specific info

    for key, value in updated_patient_info.items(): # Extracting key, value from dict
        existing_patient_info[key] = value # Making changes in exisiting dict

    # 1. Updating existing patient info to Pydantic object
    # NO id Field, add id key
    existing_patient_info['id'] = patient_id
    patient_pydantic_obj = Patient(**existing_patient_info) 
    
    # 2. From Pydantic object, form a Dict
    existing_patient_info = patient_pydantic_obj.model_dump(exclude='id')

    # 3. Add this dict to data
    data[patient_id] = existing_patient_info

        # bmi and verdict also needs to be updated as per weight
        # Need to have updated compute values

    # 4. Save Data
    save_data(data)

    # Sucess json response
    return JSONResponse(status_code=200, content={'message': 'patient updated'})


# Delete Endpoint
@app.delete('/delete/{patient_id}')
def delete_patient(patient_id: str):

    # load data
    data = load_data()

    if patient_id not in data:
        raise HTTPException(status_code=404, detail='Patient not found')
    
    del data[patient_id]

    save_data(data)

    return JSONResponse(status_code=200, content={'message': 'patient deleted'})