"""
Claim data generator
Generates healthcare claims with realistic patterns
"""

from datetime import date, timedelta
from typing import List, Optional
import random
from faker import Faker

from ingestion.schemas import ClaimSchema, PatientSchema, ProviderSchema


class ClaimGenerator:
    """Generate synthetic healthcare claim data with coherent relationships"""
    
    def __init__(self, seed: int = None):
        self.fake = Faker()
        if seed:
            Faker.seed(seed)
            random.seed(seed)
        
        # Coherence mappings for logical denial reasons
        self.diagnosis_denial_map = {
            'E11.9': ['NOT_MEDICALLY_NECESSARY', 'PRE_AUTH_REQUIRED', 'INSUFFICIENT_INFO'],
            'E10.9': ['NOT_MEDICALLY_NECESSARY', 'PRE_AUTH_REQUIRED'],
            'I10': ['NOT_MEDICALLY_NECESSARY', 'INSUFFICIENT_INFO'],
            'M54.5': ['AUTHORIZATION_REQUIRED', 'PRE_AUTH_REQUIRED', 'NOT_MEDICALLY_NECESSARY'],
            'M25.561': ['AUTHORIZATION_REQUIRED', 'PRE_AUTH_REQUIRED'],
            'J44.1': ['INSUFFICIENT_INFO', 'DUPLICATE_CLAIM'],
            'J18.9': ['INSUFFICIENT_INFO', 'TIMELY_FILING'],
            'F41.9': ['PRE_AUTH_REQUIRED', 'AUTHORIZATION_REQUIRED', 'NOT_MEDICALLY_NECESSARY'],
            'F32.9': ['PRE_AUTH_REQUIRED', 'AUTHORIZATION_REQUIRED'],
        }
        
        self.claim_type_denial_map = {
            'INPATIENT': ['AUTHORIZATION_REQUIRED', 'PRE_AUTH_REQUIRED', 'NOT_MEDICALLY_NECESSARY'],
            'OUTPATIENT': ['NOT_MEDICALLY_NECESSARY', 'INSUFFICIENT_INFO', 'PRE_AUTH_REQUIRED'],
            'EMERGENCY': ['INSUFFICIENT_INFO', 'TIMELY_FILING'],
            'PHYSICIAN': ['NOT_MEDICALLY_NECESSARY', 'INSUFFICIENT_INFO'],
            'AMBULATORY': ['AUTHORIZATION_REQUIRED', 'PRE_AUTH_REQUIRED'],
        }
        
        # Claim type distribution
        self.claim_type_weights = {
            'OUTPATIENT': 0.50,
            'PHYSICIAN': 0.25,
            'EMERGENCY': 0.10,
            'INPATIENT': 0.10,
            'AMBULATORY': 0.05
        }
        
        # Claim status distribution (will be overridden by coherence logic)
        self.status_weights = {
            'APPROVED': 0.75,
            'DENIED': 0.15,
            'PARTIAL': 0.05,
            'PENDING': 0.04,
            'REJECTED': 0.01
        }
        
        # Charge amount ranges by claim type (in USD)
        self.charge_ranges = {
            'INPATIENT': (5000, 50000),
            'EMERGENCY': (500, 5000),
            'OUTPATIENT': (200, 3000),
            'PHYSICIAN': (100, 2000),
            'AMBULATORY': (300, 4000)
        }
    
    def generate_claim(
        self,
        claim_id: str,
        patient: PatientSchema,
        provider: ProviderSchema,
        diagnosis_code: str,
        procedure_code: Optional[str] = None,
        claim_date: Optional[date] = None
    ) -> ClaimSchema:
        """Generate a single claim record"""
        
        # Generate claim date (within last 2 years)
        if claim_date is None:
            claim_date = self.fake.date_between(
                start_date='-2y',
                end_date='today'
            )
        
        # Select claim type
        claim_type = random.choices(
            list(self.claim_type_weights.keys()),
            weights=list(self.claim_type_weights.values())
        )[0]
        
        # Generate admission/discharge dates for inpatient
        admission_date = None
        discharge_date = None
        if claim_type == 'INPATIENT':
            admission_date = claim_date
            # Length of stay: 1-14 days
            los = random.randint(1, 14)
            discharge_date = admission_date + timedelta(days=los)
        
        # Generate charge amount based on claim type
        min_charge, max_charge = self.charge_ranges[claim_type]
        total_charge = round(random.uniform(min_charge, max_charge), 2)
        
        # Determine if claim should be denied (coherent logic)
        should_deny = False
        if total_charge > 10000 and claim_type in ['INPATIENT', 'AMBULATORY']:
            should_deny = random.random() < 0.25
        elif diagnosis_code in ['E11.9', 'M54.5', 'F41.9', 'F32.9']:
            should_deny = random.random() < 0.20
        elif claim_type == 'EMERGENCY':
            should_deny = random.random() < 0.05
        else:
            should_deny = random.random() < 0.15
        
        # Generate status with coherent denial reasons
        if should_deny:
            # Get contextually appropriate denial reason
            diag_reasons = self.diagnosis_denial_map.get(diagnosis_code, ['INSUFFICIENT_INFO', 'NOT_MEDICALLY_NECESSARY'])
            type_reasons = self.claim_type_denial_map.get(claim_type, ['INSUFFICIENT_INFO', 'NOT_MEDICALLY_NECESSARY'])
            candidate_reasons = list(set(diag_reasons) & set(type_reasons)) or diag_reasons
            denial_reason = random.choice(candidate_reasons)
            claim_status = 'DENIED'
        else:
            non_denied_weights = {'APPROVED': 0.80, 'PARTIAL': 0.10, 'PENDING': 0.08, 'REJECTED': 0.02}
            claim_status = random.choices(list(non_denied_weights.keys()), weights=list(non_denied_weights.values()))[0]
            denial_reason = None
        
        # Calculate paid amount based on status
        if claim_status == 'APPROVED':
            # Approved: pay 70-95% of charge
            total_paid = round(total_charge * random.uniform(0.70, 0.95), 2)
        elif claim_status == 'PARTIAL':
            # Partial: pay 30-60% of charge
            total_paid = round(total_charge * random.uniform(0.30, 0.60), 2)
        elif claim_status == 'DENIED':
            # Denied: no payment
            total_paid = 0.0
        elif claim_status == 'PENDING':
            # Pending: no payment yet
            total_paid = 0.0
        else:  # REJECTED
            total_paid = 0.0
        
        return ClaimSchema(
            claim_id=claim_id,
            patient_id=patient.patient_id,
            provider_id=provider.provider_id,
            claim_date=claim_date,
            admission_date=admission_date,
            discharge_date=discharge_date,
            claim_type=claim_type,
            total_charge=total_charge,
            total_paid=total_paid,
            claim_status=claim_status,
            denial_reason=denial_reason,
            primary_diagnosis_code=diagnosis_code,
            primary_procedure_code=procedure_code
        )
    
    def generate_claims(
        self,
        patients: List[PatientSchema],
        providers: List[ProviderSchema],
        diagnosis_codes: List[str],
        procedure_codes: List[str],
        claims_per_patient: int = 3,
        start_id: int = 1000000
    ) -> List[ClaimSchema]:
        """Generate multiple claim records"""
        claims = []
        claim_counter = start_id
        
        for patient in patients:
            # Generate exactly claims_per_patient claims for each patient
            for _ in range(claims_per_patient):
                provider = random.choice(providers)
                diagnosis = random.choice(diagnosis_codes)
                procedure = random.choice(procedure_codes) if random.random() > 0.3 else None
                
                claim_id = f"CLM{claim_counter}"
                claim = self.generate_claim(
                    claim_id=claim_id,
                    patient=patient,
                    provider=provider,
                    diagnosis_code=diagnosis,
                    procedure_code=procedure
                )
                claims.append(claim)
                claim_counter += 1
        
        return claims


if __name__ == "__main__":
    # Test generation (would need actual patients/providers)
    from patient_generator import PatientGenerator
    from provider_generator import ProviderGenerator
    
    patient_gen = PatientGenerator(seed=42)
    provider_gen = ProviderGenerator(seed=42)
    claim_gen = ClaimGenerator(seed=42)
    
    patients = patient_gen.generate_patients(5)
    providers = provider_gen.generate_providers(3)
    diagnosis_codes = ['E11.9', 'I10', 'M54.5', 'J44.1', 'E78.5']
    procedure_codes = ['99213', '99214', '36415', '80053', '93000']
    
    claims = claim_gen.generate_claims(
        patients, providers, diagnosis_codes, procedure_codes, claims_per_patient=2
    )
    
    for c in claims[:5]:
        print(f"{c.claim_id}: {c.claim_type} - ${c.total_charge:.2f} ({c.claim_status})")

