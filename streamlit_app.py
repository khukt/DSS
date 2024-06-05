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
def get_ids(names, data, key, name_key):
    return [item[key] for item in data if item[name_key] in names]

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
            "Probability": count / total_symptoms,
            "SymptomIDs": [mapping['SymptomID'] for mapping in symptom_disease_map if mapping['DiseaseID'] == disease_id]
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
st.set_page_config(page_title="Symptom Checker and Disease Predictor", layout="wide")
st.title("Symptom Checker and Disease Predictor")

# Patient information
st.header("Patient Information")
col1, col2, col3 = st.columns(3)
with col1:
    gender = st.selectbox("Gender", ["Male", "Female"])
with col2:
    age = st.number_input("Age", min_value=0, max_value=120, value=25)
with col3:
    weight = st.number_input("Weight (kg)", min_value=0.0, max_value=300.0, value=70.0)
with col1:
    blood_type = st.selectbox("Blood Type", ["A", "B", "AB", "O"])
with col2:
    region = st.selectbox("Region", regions)

# Symptoms
st.header("Symptoms")
symptom = st.selectbox("Symptom", symptoms_list)
if "symptoms" not in st.session_state:
    st.session_state["symptoms"] = []
if st.button("Add Symptom"):
    if symptom not in st.session_state["symptoms"]:
        st.session_state["symptoms"].append(symptom)
        st.success(f"Symptom '{symptom}' added!")
st.write("Symptoms:", ", ".join(st.session_state["symptoms"]))

# Food Allergies
st.header("Food Allergies")
food_allergy = st.selectbox("Food Allergy", food_allergies_list)
if "food_allergies" not in st.session_state:
    st.session_state["food_allergies"] = []
if st.button("Add Food Allergy"):
    if food_allergy not in st.session_state["food_allergies"]:
        st.session_state["food_allergies"].append(food_allergy)
        st.success(f"Food Allergy '{food_allergy}' added!")
st.write("Food Allergies:", ", ".join(st.session_state["food_allergies"]))

# Medicine Allergies
st.header("Medicine Allergies")
medicine_allergy = st.selectbox("Medicine Allergy", medicine_allergies_list)
if "medicine_allergies" not in st.session_state:
    st.session_state["medicine_allergies"] = []
if st.button("Add Medicine Allergy"):
    if medicine_allergy not in st.session_state["medicine_allergies"]:
        st.session_state["medicine_allergies"].append(medicine_allergy)
        st.success(f"Medicine Allergy '{medicine_allergy}' added!")
st.write("Medicine Allergies:", ", ".join(st.session_state["medicine_allergies"]))

# Lifestyle Factors
st.header("Lifestyle Factors")
lifestyle = st.selectbox("Lifestyle", lifestyle_factors_list)
if "lifestyle_factors" not in st.session_state:
    st.session_state["lifestyle_factors"] = []
if st.button("Add Lifestyle Factor"):
    if lifestyle not in st.session_state["lifestyle_factors"]:
        st.session_state["lifestyle_factors"].append(lifestyle)
        st.success(f"Lifestyle Factor '{lifestyle}' added!")
st.write("Lifestyle Factors:", ", ".join(st.session_state["lifestyle_factors"]))

# Medical Conditions
st.header("Medical Conditions")
medical_condition = st.selectbox("Medical Condition", medical_conditions_list)
if "medical_conditions" not in st.session_state:
    st.session_state["medical_conditions"] = []
if st.button("Add Medical Condition"):
    if medical_condition not in st.session_state["medical_conditions"]:
        st.session_state["medical_conditions"].append(medical_condition)
        st.success(f"Medical Condition '{medical_condition}' added!")
st.write("Medical Conditions:", ", ".join(st.session_state["medical_conditions"]))

# Check Conditions
if st.button("Check Conditions"):
    symptom_ids = get_ids(st.session_state["symptoms"], medical_data['Symptoms'], 'SymptomID', 'SymptomName')
    diseases = predict_diseases(symptom_ids, knowledge_base)
    
    st.subheader("Predicted Diseases")
    for disease in diseases:
        disease_name = next(d['DiseaseName'] for d in medical_data['Diseases'] if d['DiseaseID'] == disease['DiseaseID'])
        st.markdown(f"**{disease_name}** (Probability: {disease['Probability']:.2f})")
        explanation = ", ".join(
            [next(symptom['SymptomName'] for symptom in medical_data['Symptoms'] if symptom['SymptomID'] == sym_id) 
             for sym_id in disease['SymptomIDs']]
        )
        st.write(f"*Based on the symptoms: {explanation}*")
    
    medications = suggest_medications(diseases, knowledge_base)
    
    st.subheader("Suggested Medications")
    medication_names = [medication['MedicationName'] for medication in medications]
    st.markdown("\n".join([f"- {med}" for med in medication_names]))
    st.write("*These medications are suggested based on the predicted diseases.*")

