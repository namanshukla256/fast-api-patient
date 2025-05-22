from fastapi import FastAPI
import json

app = FastAPI() #Defining app variable from Class

# Helper function to retirive patient data from json file
def load_data():
    with open('patients.json', 'r') as f:
        data = json.load(f) 
    return data

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

@app.get('/')