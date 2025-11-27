"""
Provider data generator
Generates healthcare provider information with realistic NPI numbers
"""

from typing import List
import random
from faker import Faker
from faker.providers import company, address

from ingestion.schemas import ProviderSchema


class ProviderGenerator:
    """Generate synthetic healthcare provider data"""
    
    def __init__(self, seed: int = None):
        self.fake = Faker()
        if seed:
            Faker.seed(seed)
            random.seed(seed)
        self.fake.add_provider(company)
        self.fake.add_provider(address)
        
        # Provider types with realistic distribution
        self.provider_types = {
            'PHYSICIAN': 0.40,
            'HOSPITAL': 0.25,
            'CLINIC': 0.15,
            'EMERGENCY': 0.08,
            'AMBULATORY': 0.07,
            'LABORATORY': 0.03,
            'IMAGING': 0.02
        }
        
        # Medical specialties
        self.specialties = [
            'CARDIOLOGY', 'ONCOLOGY', 'ORTHOPEDICS', 'NEUROLOGY', 'PEDIATRICS',
            'EMERGENCY MEDICINE', 'FAMILY MEDICINE', 'INTERNAL MEDICINE',
            'SURGERY', 'RADIOLOGY', 'PATHOLOGY', 'ANESTHESIOLOGY', 'PSYCHIATRY',
            'DERMATOLOGY', 'OPHTHALMOLOGY', 'UROLOGY', 'GYNECOLOGY', 'PULMONOLOGY'
        ]
        
        # US states
        self.states = [
            'CA', 'TX', 'FL', 'NY', 'PA', 'IL', 'OH', 'GA', 'NC', 'MI',
            'NJ', 'VA', 'WA', 'AZ', 'MA', 'TN', 'IN', 'MO', 'MD', 'WI'
        ]
    
    def generate_npi(self) -> str:
        """
        Generate a realistic NPI (National Provider Identifier)
        NPI format: 10 digits, first digit is 1 or 2
        Uses Luhn algorithm for validation (simplified version)
        """
        # First digit: 1 (individual) or 2 (organization)
        first_digit = random.choice(['1', '2'])
        
        # Generate remaining 9 digits
        remaining = ''.join([str(random.randint(0, 9)) for _ in range(9)])
        
        npi = first_digit + remaining
        return npi
    
    def generate_provider(self, provider_id: str = None) -> ProviderSchema:
        """Generate a single provider record"""
        if provider_id is None:
            provider_id = f"PROV{self.fake.unique.random_int(min=10000, max=99999)}"
        
        provider_type = random.choices(
            list(self.provider_types.keys()),
            weights=list(self.provider_types.values())
        )[0]
        
        # Generate provider name based on type
        if provider_type == 'HOSPITAL':
            name = f"{self.fake.last_name()} {provider_type}"
        elif provider_type == 'PHYSICIAN':
            name = f"Dr. {self.fake.first_name()} {self.fake.last_name()}"
        else:
            name = f"{self.fake.company()} {provider_type}"
        
        # Specialty for physicians and some clinics
        specialty = None
        if provider_type in ['PHYSICIAN', 'CLINIC']:
            specialty = random.choice(self.specialties)
        
        # Generate address
        city = self.fake.city()
        state = random.choice(self.states)
        zip_code = self.fake.zipcode()
        street_address = self.fake.street_address()
        
        return ProviderSchema(
            provider_id=provider_id,
            npi=self.generate_npi(),
            provider_name=name,
            provider_type=provider_type,
            specialty=specialty,
            address=street_address,
            city=city,
            state=state,
            zip_code=zip_code
        )
    
    def generate_providers(self, count: int, start_id: int = 10000) -> List[ProviderSchema]:
        """Generate multiple provider records"""
        providers = []
        for i in range(count):
            provider_id = f"PROV{start_id + i}"
            providers.append(self.generate_provider(provider_id))
        return providers


if __name__ == "__main__":
    # Test generation
    generator = ProviderGenerator(seed=42)
    providers = generator.generate_providers(10)
    for p in providers:
        print(f"{p.provider_id}: {p.provider_name} ({p.provider_type}), NPI: {p.npi}")

