"""
Patient data generator
Generates HIPAA-compliant, de-identified patient demographics
"""

from datetime import date, timedelta
from typing import List
import random
from faker import Faker
from faker.providers import date_time, person

from ingestion.schemas import PatientSchema


class PatientGenerator:
    """Generate synthetic patient data"""
    
    def __init__(self, seed: int = None):
        self.fake = Faker()
        if seed:
            Faker.seed(seed)
            random.seed(seed)
        self.fake.add_provider(date_time)
        self.fake.add_provider(person)
        
        # US states for realistic distribution
        self.states = [
            'CA', 'TX', 'FL', 'NY', 'PA', 'IL', 'OH', 'GA', 'NC', 'MI',
            'NJ', 'VA', 'WA', 'AZ', 'MA', 'TN', 'IN', 'MO', 'MD', 'WI',
            'CO', 'MN', 'SC', 'AL', 'LA', 'KY', 'OR', 'OK', 'CT', 'IA'
        ]
        
        # Gender distribution (realistic healthcare distribution)
        self.gender_weights = {'M': 0.48, 'F': 0.50, 'O': 0.01, 'U': 0.01}
    
    def generate_patient(self, patient_id: str = None) -> PatientSchema:
        """Generate a single patient record"""
        if patient_id is None:
            patient_id = f"PAT{self.fake.unique.random_int(min=100000, max=999999)}"
        
        # Generate date of birth (ages 0-100)
        birth_date = self.fake.date_between(
            start_date='-100y',
            end_date='today'
        )
        
        # Realistic gender distribution
        gender = random.choices(
            list(self.gender_weights.keys()),
            weights=list(self.gender_weights.values())
        )[0]
        
        # Generate ZIP (first 3 digits for privacy - HIPAA compliant)
        zip_code = self.fake.zipcode()[:3]
        state = random.choice(self.states)
        
        return PatientSchema(
            patient_id=patient_id,
            date_of_birth=birth_date,
            gender=gender,
            zip_code=zip_code,
            state=state
        )
    
    def generate_patients(self, count: int, start_id: int = 100000) -> List[PatientSchema]:
        """Generate multiple patient records"""
        patients = []
        for i in range(count):
            patient_id = f"PAT{start_id + i}"
            patients.append(self.generate_patient(patient_id))
        return patients


if __name__ == "__main__":
    # Test generation
    generator = PatientGenerator(seed=42)
    patients = generator.generate_patients(10)
    for p in patients:
        print(f"{p.patient_id}: {p.gender}, DOB: {p.date_of_birth}, State: {p.state}")

