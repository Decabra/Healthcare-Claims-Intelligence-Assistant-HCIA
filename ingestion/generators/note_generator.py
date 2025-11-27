"""
Clinical note generator
Generates realistic clinical notes with medical terminology
"""

from datetime import datetime
from typing import List, Optional
import random
from faker import Faker

from ingestion.schemas import NoteSchema, ClaimSchema


class NoteGenerator:
    """Generate synthetic clinical notes with coherent context"""
    
    def __init__(self, seed: int = None):
        self.fake = Faker()
        if seed:
            Faker.seed(seed)
            random.seed(seed)
        
        # Coherence mappings for context-aware notes
        self.diagnosis_symptoms = {
            'E11.9': ['elevated blood glucose', 'increased thirst', 'frequent urination', 'fatigue'],
            'E10.9': ['elevated blood glucose', 'weight loss', 'increased thirst'],
            'I10': ['elevated blood pressure', 'headache', 'dizziness'],
            'M54.5': ['lower back pain', 'radiating pain', 'stiffness'],
            'M25.561': ['right knee pain', 'swelling', 'limited range of motion'],
            'J44.1': ['shortness of breath', 'chronic cough', 'wheezing', 'chest tightness'],
            'J18.9': ['fever', 'cough', 'shortness of breath', 'chest pain'],
            'F41.9': ['anxiety', 'restlessness', 'difficulty concentrating', 'sleep disturbances'],
            'F32.9': ['depressed mood', 'loss of interest', 'fatigue', 'sleep disturbances'],
        }
        
        self.diagnosis_treatments = {
            'E11.9': ['blood glucose monitoring', 'diabetes medication', 'dietary counseling'],
            'E10.9': ['insulin therapy', 'blood glucose monitoring', 'diabetes education'],
            'I10': ['antihypertensive medication', 'blood pressure monitoring', 'lifestyle counseling'],
            'M54.5': ['pain management', 'physical therapy', 'imaging studies'],
            'M25.561': ['pain medication', 'knee imaging', 'orthopedic consultation'],
            'J44.1': ['bronchodilator therapy', 'oxygen therapy', 'pulmonary function tests'],
            'J18.9': ['antibiotic therapy', 'chest imaging', 'supportive care'],
            'F41.9': ['anxiety medication', 'counseling', 'psychiatric evaluation'],
            'F32.9': ['antidepressant medication', 'psychotherapy', 'psychiatric evaluation'],
        }
        
        self.denial_explanations = {
            'INSUFFICIENT_INFO': 'Claim denied due to missing or incomplete documentation required for processing.',
            'NOT_MEDICALLY_NECESSARY': 'Services were determined not to be medically necessary based on clinical guidelines.',
            'DUPLICATE_CLAIM': 'Claim denied as duplicate of previously submitted claim.',
            'AUTHORIZATION_REQUIRED': 'Prior authorization was required but not obtained before service delivery.',
            'PRE_AUTH_REQUIRED': 'Pre-authorization was required but not obtained.',
            'TIMELY_FILING': 'Claim submitted outside of timely filing window.',
        }
        
        self.assessments = [
            "stable condition", "improving", "deteriorating", "critical", "guarded",
            "fair", "good", "poor", "acute", "chronic", "subacute"
        ]
        
        self.vital_signs_templates = [
            "BP {systolic}/{diastolic}, HR {hr}, RR {rr}, Temp {temp}F, O2 Sat {o2}%",
            "Vitals: {systolic}/{diastolic} mmHg, {hr} bpm, {temp}F",
            "Blood pressure {systolic}/{diastolic}, heart rate {hr}, temperature {temp}F"
        ]
    
    def generate_vital_signs(self) -> dict:
        """Generate realistic vital signs"""
        return {
            'systolic': random.randint(90, 160),
            'diastolic': random.randint(60, 100),
            'hr': random.randint(60, 100),
            'rr': random.randint(12, 20),
            'temp': round(random.uniform(97.0, 99.5), 1),
            'o2': random.randint(95, 100)
        }
    
    def generate_admission_note(self, claim: ClaimSchema) -> str:
        """Generate admission note with coherent context"""
        vitals = self.generate_vital_signs()
        symptoms_list = self.diagnosis_symptoms.get(claim.primary_diagnosis_code, ['generalized symptoms'])
        treatments_list = self.diagnosis_treatments.get(claim.primary_diagnosis_code, ['symptomatic treatment'])
        symptom = random.choice(symptoms_list)
        treatment = random.choice(treatments_list)
        assessment = random.choice(self.assessments)
        
        denial_context = ""
        if claim.claim_status == 'DENIED' and claim.denial_reason:
            denial_explanation = self.denial_explanations.get(claim.denial_reason, "Claim was denied.")
            denial_context = f"\n\nCLAIM STATUS:\nThis claim was denied. Reason: {denial_explanation}"
        
        note = f"""ADMISSION NOTE

Patient admitted on {claim.admission_date.strftime('%Y-%m-%d') if claim.admission_date else claim.claim_date.strftime('%Y-%m-%d')}.

CHIEF COMPLAINT:
Patient presents with {symptom}.

VITAL SIGNS:
{self.vital_signs_templates[0].format(**vitals)}

ASSESSMENT:
Patient is in {assessment} condition. Primary diagnosis: {claim.primary_diagnosis_code}.
{denial_context}

PLAN:
{treatment}. Continue monitoring and reassess as needed."""
        
        return note
    
    def generate_discharge_note(self, claim: ClaimSchema) -> str:
        """Generate discharge note with coherent context"""
        assessment = random.choice(self.assessments)
        treatments_list = self.diagnosis_treatments.get(claim.primary_diagnosis_code, ['symptomatic treatment'])
        treatment_provided = random.choice(treatments_list)
        procedure_info = f" Procedure performed: CPT {claim.primary_procedure_code}." if claim.primary_procedure_code else ""
        
        denial_context = ""
        if claim.claim_status == 'DENIED' and claim.denial_reason:
            denial_explanation = self.denial_explanations.get(claim.denial_reason, "Claim was denied.")
            denial_context = f"\n\nCLAIM STATUS:\nThis claim was denied. Reason: {denial_explanation}"
        
        note = f"""DISCHARGE SUMMARY

Patient discharged on {claim.discharge_date.strftime('%Y-%m-%d') if claim.discharge_date else claim.claim_date.strftime('%Y-%m-%d')}.

HOSPITAL COURSE:
Patient was admitted for treatment of {claim.primary_diagnosis_code}.{procedure_info}
During hospitalization, patient received {treatment_provided} and showed improvement.

DISCHARGE CONDITION:
Patient is in {assessment} condition at time of discharge.{denial_context}

DISCHARGE INSTRUCTIONS:
Follow-up with primary care provider within 7-10 days. Continue medications as prescribed.
Return to emergency department if symptoms worsen."""
        
        return note
    
    def generate_progress_note(self, claim: ClaimSchema) -> str:
        """Generate progress note with coherent context"""
        vitals = self.generate_vital_signs()
        assessment = random.choice(self.assessments)
        symptoms_list = self.diagnosis_symptoms.get(claim.primary_diagnosis_code, ['generalized symptoms'])
        treatments_list = self.diagnosis_treatments.get(claim.primary_diagnosis_code, ['symptomatic treatment'])
        symptom_status = "improvement" if random.random() > 0.3 else "persistent " + random.choice(symptoms_list)
        treatment = random.choice(treatments_list)
        
        denial_context = ""
        if claim.claim_status == 'DENIED' and claim.denial_reason:
            denial_explanation = self.denial_explanations.get(claim.denial_reason, "Claim was denied.")
            denial_context = f"\n\nCLAIM STATUS:\nThis claim was denied. Reason: {denial_explanation}"
        
        note = f"""PROGRESS NOTE - {claim.claim_date.strftime('%Y-%m-%d')}

SUBJECTIVE:
Patient reports {symptom_status} in symptoms related to {claim.primary_diagnosis_code}.

OBJECTIVE:
Vital signs: {self.vital_signs_templates[1].format(**vitals)}

ASSESSMENT:
Patient condition is {assessment}. Diagnosis: {claim.primary_diagnosis_code}.{denial_context}

PLAN:
Continue {treatment}. Monitor response and reassess as needed."""
        
        return note
    
    def generate_procedure_note(self, claim: ClaimSchema) -> str:
        """Generate procedure note with coherent context"""
        procedure_code = claim.primary_procedure_code or "N/A"
        symptoms_list = self.diagnosis_symptoms.get(claim.primary_diagnosis_code, ['generalized symptoms'])
        indication_symptom = random.choice(symptoms_list)
        
        denial_context = ""
        if claim.claim_status == 'DENIED' and claim.denial_reason:
            denial_explanation = self.denial_explanations.get(claim.denial_reason, "Claim was denied.")
            denial_context = f"\n\nCLAIM STATUS:\nThis claim was denied. Reason: {denial_explanation}"
        
        note = f"""PROCEDURE NOTE - {claim.claim_date.strftime('%Y-%m-%d')}

PROCEDURE:
CPT Code: {procedure_code}

INDICATION:
Procedure performed for diagnosis and treatment of {claim.primary_diagnosis_code}. 
Patient presented with {indication_symptom}.

PROCEDURE DESCRIPTION:
Procedure was performed successfully without complications. Patient tolerated procedure well.{denial_context}

POST-PROCEDURE:
Patient is stable. Monitor for any complications. Follow-up as indicated for {claim.primary_diagnosis_code}."""
        
        return note
    
    def generate_denial_note(self, claim: ClaimSchema) -> str:
        """Generate a denial explanation note"""
        if not claim.denial_reason:
            return self.generate_progress_note(claim)
        
        denial_explanation = self.denial_explanations.get(claim.denial_reason, "Claim was denied.")
        
        # Get diagnosis context
        diagnosis_info = f"Diagnosis: {claim.primary_diagnosis_code}"
        if claim.primary_procedure_code:
            diagnosis_info += f", Procedure: CPT {claim.primary_procedure_code}"
        
        note = f"""CLAIM DENIAL NOTICE - {claim.claim_date.strftime('%Y-%m-%d')}

CLAIM INFORMATION:
Claim ID: {claim.claim_id}
{diagnosis_info}
Claim Type: {claim.claim_type}
Total Charge: ${claim.total_charge:,.2f}

DENIAL REASON:
{denial_explanation}

DETAILS:
This claim was reviewed and denied based on the above reason. 
{diagnosis_info} was submitted for this claim.

NEXT STEPS:
Provider may submit additional documentation or appeal this denial if additional 
information is available that supports medical necessity or addresses the denial reason."""
        
        return note
    
    def generate_note(
        self,
        note_id: str,
        claim: ClaimSchema,
        note_type: Optional[str] = None
    ) -> NoteSchema:
        """Generate a clinical note"""
        if note_type is None:
            # If claim is denied, sometimes generate a denial note
            if claim.claim_status == 'DENIED' and random.random() < 0.3:
                note_type = 'DIAGNOSIS'  # Use DIAGNOSIS type for denial notes
            # Determine note type based on claim type
            elif claim.claim_type == 'INPATIENT':
                note_type = random.choice(['ADMISSION', 'DISCHARGE', 'PROGRESS'])
            elif claim.primary_procedure_code:
                note_type = 'PROCEDURE'
            else:
                note_type = 'PROGRESS'
        
        # Generate note text based on type
        if note_type == 'ADMISSION':
            note_text = self.generate_admission_note(claim)
        elif note_type == 'DISCHARGE':
            note_text = self.generate_discharge_note(claim)
        elif note_type == 'PROCEDURE':
            note_text = self.generate_procedure_note(claim)
        elif note_type == 'DIAGNOSIS' and claim.claim_status == 'DENIED':
            # Use DIAGNOSIS type for denial explanation notes
            note_text = self.generate_denial_note(claim)
        else:  # PROGRESS
            note_text = self.generate_progress_note(claim)
        
        return NoteSchema(
            note_id=note_id,
            claim_id=claim.claim_id,
            note_type=note_type,
            note_text=note_text
        )
    
    def generate_notes(
        self,
        claims: List[ClaimSchema],
        notes_per_claim: int = 1,
        start_id: int = 100000
    ) -> List[NoteSchema]:
        """Generate notes for multiple claims"""
        notes = []
        note_counter = start_id
        
        for claim in claims:
            # Generate exactly notes_per_claim notes for each claim
            for _ in range(notes_per_claim):
                note_id = f"NOTE{note_counter}"
                note = self.generate_note(note_id, claim)
                notes.append(note)
                note_counter += 1
        
        return notes


if __name__ == "__main__":
    # Test generation
    from claim_generator import ClaimGenerator
    from patient_generator import PatientGenerator
    from provider_generator import ProviderGenerator
    
    patient_gen = PatientGenerator(seed=42)
    provider_gen = ProviderGenerator(seed=42)
    claim_gen = ClaimGenerator(seed=42)
    note_gen = NoteGenerator(seed=42)
    
    patients = patient_gen.generate_patients(2)
    providers = provider_gen.generate_providers(2)
    diagnosis_codes = ['E11.9', 'I10']
    procedure_codes = ['99213', '99214']
    
    claims = claim_gen.generate_claims(
        patients, providers, diagnosis_codes, procedure_codes, claims_per_patient=1
    )
    
    notes = note_gen.generate_notes(claims)
    
    for note in notes:
        print(f"\n{note.note_id} ({note.note_type}):\n{note.note_text[:200]}...")

