import streamlit as st
import json

# Load the JSON files
with open('knowledge_base.json', 'r') as f:
    knowledge_base = json.load(f)

with open('patient_database.json', 'r') as f:
    patient_database = json.load(f)

with open('medical_data.json', 'r') as f:
    medical_data = json.load(f)

# Extract options from medical_data
regions = ['Canada', 'USA', 'UK', 'Australia']
food_allergies_list = [allergy['AllergyName'] for allergy in medical_data['Allergies']]
medicine_allergies_list = [allergy['AllergyName'] for allergy in medical_data['Allergies']]
symptoms_list = [symptom['SymptomName'] for symptom in medical_data['Symptoms']]
lifestyle_factors_list = [factor['LifestyleFactorName'] for factor in medical_data['LifestyleFactors']]
medical_conditions_list = [condition['MedicalConditionName'] for condition in medical_data['MedicalConditions']]

# Function to get IDs from names
def get_ids(names, data, key):
    return [item[key] for item in data if item[next(iter(item.values()))] in names]

# Function to predict diseases based on symptoms
def predict_diseases(symptoms, knowledge_base):
    symptom_disease_map = knowledge_base['SymptomDiseaseMapping']
    disease_counts = {}
    
    for symptom_id in symptoms:
        for mapping in symptom_disease_map:
            if mapping['SymptomID'] == symptom_id:
                disease_id = mapping['DiseaseID']
                if disease_id in disease_counts:
                    disease_counts[disease_id] += 1
                else:
                    disease_counts[disease_id] = 1
    
    # Convert disease counts to list of dictionaries with probabilities
    total_symptoms = len(symptoms)
    disease_predictions = [
        {
            "DiseaseID": disease_id,
            "Probability": count / total_symptoms
        }
        for disease_id, count in disease_counts.items()
    ]
    
    return disease_predictions

# Function to suggest medications based on diseases
def suggest_medications(diseases, knowledge_base):
    disease_medication_map = knowledge_base['DiseaseMedicationMapping']
    medication_ids = set()
    
    for disease in diseases:
        for mapping in disease_medication_map:
            if mapping['DiseaseID'] == disease['DiseaseID']:
                medication_ids.add(mapping['MedicationID'])
    
    medications = [
        medication for medication in medical_data['Medications']
        if medication['MedicationID'] in medication_ids
    ]
    
    return medications

# Streamlit app
st.title("Symptom Checker and Disease Predictor")

# Patient information
st.header("Patient Information")
gender = st.selectbox("Gender", ["Male", "Female"])
age = st.number_input("Age", min_value=0, max_value=120, value=25)
weight = st.number_input("Weight (kg)", min_value=0.0, max_value=300.0, value=70.0)
blood_type = st.selectbox("Blood Type", ["A", "B", "AB", "O"])
region = st.selectbox("Region", regions)

# Symptoms
st.header("Symptoms")
symptom = st.selectbox("Symptom", symptoms_list)
if "symptoms" not in st.session_state:
    st.session_state["symptoms"] = []
if st.button("Add Symptom"):
    st.session_state["symptoms"].append(symptom)
st.write("Symptoms:", st.session_state["symptoms"])

# Food Allergies
st.header("Food Allergies")
food_allergy = st.selectbox("Food Allergy", food_allergies_list)
if "food_allergies" not in st.session_state:
    st.session_state["food_allergies"] = []
if st.button("Add Food Allergy"):
    st.session_state["food_allergies"].append(food_allergy)
st.write("Food Allergies:", st.session_state["food_allergies"])

# Medicine Allergies
st.header("Medicine Allergies")
medicine_allergy = st.selectbox("Medicine Allergy", medicine_allergies_list)
if "medicine_allergies" not in st.session_state:
    st.session_state["medicine_allergies"] = []
if st.button("Add Medicine Allergy"):
    st.session_state["medicine_allergies"].append(medicine_allergy)
st.write("Medicine Allergies:", st.session_state["medicine_allergies"])

# Lifestyle Factors
st.header("Lifestyle Factors")
lifestyle = st.selectbox("Lifestyle", lifestyle_factors_list)
if "lifestyle_factors" not in st.session_state:
    st.session_state["lifestyle_factors"] = []
if st.button("Add Lifestyle Factor"):
    st.session_state["lifestyle_factors"].append(lifestyle)
st.write("Lifestyle Factors:", st.session_state["lifestyle_factors"])

# Medical Conditions
st.header("Medical Conditions")
medical_condition = st.selectbox("Medical Condition", medical_conditions_list)
if "medical_conditions" not in st.session_state:
    st.session_state["medical_conditions"] = []
if st.button("Add Medical Condition"):
    st.session_state["medical_conditions"].append(medical_condition)
st.write("Medical Conditions:", st.session_state["medical_conditions"])

# Check Conditions
if st.button("Check Conditions"):
    symptom_ids = get_ids(st.session_state["symptoms"], medical_data['Symptoms'], 'SymptomID')
    diseases = predict_diseases(symptom_ids, knowledge_base)
    
    st.subheader("Predicted Diseases")
    for disease in diseases:
        disease_name = next(d['DiseaseName'] for d in medical_data['Diseases'] if d['DiseaseID'] == disease['DiseaseID'])
        st.write(f"{disease_name} (Probability: {disease['Probability']:.2f})")
    
    medications = suggest_medications(diseases, knowledge_base)
    
    st.subheader("Suggested Medications")
    for medication in medications:
        st.write(medication['MedicationName'])