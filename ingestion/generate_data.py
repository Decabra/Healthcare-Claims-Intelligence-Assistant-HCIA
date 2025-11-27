"""
Main data generation orchestrator
Generates all synthetic healthcare claims data
"""

import argparse
import csv
import json
from pathlib import Path
from datetime import datetime
from typing import Dict, List

from .generators.patient_generator import PatientGenerator
from .generators.provider_generator import ProviderGenerator
from .generators.claim_generator import ClaimGenerator
from .generators.note_generator import NoteGenerator
from .generators.lookup_generator import ICD10Generator, CPTGenerator
from .schemas import (
    PatientSchema, ProviderSchema, ClaimSchema, NoteSchema,
    ICD10Schema, CPTSchema
)


class DataGenerator:
    """Main data generation orchestrator"""
    
    def __init__(self, seed: int = 42, output_dir: Path = Path("data/raw")):
        self.seed = seed
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)
        
        # Initialize generators
        self.patient_gen = PatientGenerator(seed=seed)
        self.provider_gen = ProviderGenerator(seed=seed)
        self.claim_gen = ClaimGenerator(seed=seed)
        self.note_gen = NoteGenerator(seed=seed)
        self.icd10_gen = ICD10Generator(seed=seed)
        self.cpt_gen = CPTGenerator(seed=seed)
        
        self.generated_data: Dict[str, List] = {}
    
    def generate_lookup_tables(self):
        """Generate ICD-10 and CPT lookup tables"""
        print("Generating lookup tables...")
        
        icd10_codes = self.icd10_gen.generate_icd10_lookup()
        cpt_codes = self.cpt_gen.generate_cpt_lookup()
        
        self.generated_data['icd10'] = icd10_codes
        self.generated_data['cpt'] = cpt_codes
        
        print(f"  ✓ Generated {len(icd10_codes)} ICD-10 codes")
        print(f"  ✓ Generated {len(cpt_codes)} CPT codes")
        
        return icd10_codes, cpt_codes
    
    def generate_core_data(
        self,
        num_patients: int = 1000,
        num_providers: int = 100,
        claims_per_patient: int = 3,
        notes_per_claim: int = 1
    ):
        """Generate patients, providers, and claims"""
        print(f"\nGenerating core data...")
        print(f"  Patients: {num_patients}")
        print(f"  Providers: {num_providers}")
        print(f"  Claims per patient: {claims_per_patient}")
        print(f"  Notes per claim: {notes_per_claim}")
        
        # Generate patients
        print("\nGenerating patients...")
        patients = self.patient_gen.generate_patients(num_patients)
        self.generated_data['patients'] = patients
        print(f"  ✓ Generated {len(patients)} patients")
        
        # Generate providers
        print("\nGenerating providers...")
        providers = self.provider_gen.generate_providers(num_providers)
        self.generated_data['providers'] = providers
        print(f"  ✓ Generated {len(providers)} providers")
        
        # Get diagnosis and procedure codes
        icd10_codes = [code.code for code in self.generated_data['icd10']]
        cpt_codes = [code.code for code in self.generated_data['cpt']]
        
        # Generate claims
        print("\nGenerating claims...")
        claims = self.claim_gen.generate_claims(
            patients=patients,
            providers=providers,
            diagnosis_codes=icd10_codes,
            procedure_codes=cpt_codes,
            claims_per_patient=claims_per_patient
        )
        self.generated_data['claims'] = claims
        print(f"  ✓ Generated {len(claims)} claims")
        
        # Generate notes
        print("\nGenerating clinical notes...")
        notes = self.note_gen.generate_notes(claims, notes_per_claim=notes_per_claim)
        self.generated_data['notes'] = notes
        print(f"  ✓ Generated {len(notes)} clinical notes")
        
        return patients, providers, claims, notes
    
    def export_to_csv(self):
        """Export all data to CSV files"""
        print("\nExporting data to CSV files...")
        
        # Export lookup tables
        self._export_schema_list('icd10', 'raw_icd10.csv')
        self._export_schema_list('cpt', 'raw_cpt.csv')
        
        # Export core data
        self._export_schema_list('patients', 'raw_patients.csv')
        self._export_schema_list('providers', 'raw_providers.csv')
        self._export_schema_list('claims', 'raw_claims.csv')
        self._export_schema_list('notes', 'raw_notes.csv')
        
        print("  ✓ All data exported to CSV")
    
    def _export_schema_list(self, key: str, filename: str):
        """Export a list of Pydantic schemas to CSV"""
        if key not in self.generated_data:
            return
        
        data = self.generated_data[key]
        if not data:
            return
        
        filepath = self.output_dir / filename
        
        # Get field names from first schema
        field_names = list(data[0].dict().keys())
        
        with open(filepath, 'w', newline='', encoding='utf-8') as f:
            writer = csv.DictWriter(f, fieldnames=field_names)
            writer.writeheader()
            
            for item in data:
                # Convert dates/datetimes to strings
                row = {}
                for field, value in item.dict().items():
                    if isinstance(value, (datetime,)):
                        row[field] = value.isoformat()
                    elif hasattr(value, 'isoformat'):  # date objects
                        row[field] = value.isoformat()
                    else:
                        row[field] = value
                writer.writerow(row)
        
        print(f"  ✓ Exported {len(data)} records to {filename}")
    
    def export_metadata(self):
        """Export generation metadata"""
        metadata = {
            'generation_date': datetime.now().isoformat(),
            'seed': self.seed,
            'counts': {
                'patients': len(self.generated_data.get('patients', [])),
                'providers': len(self.generated_data.get('providers', [])),
                'claims': len(self.generated_data.get('claims', [])),
                'notes': len(self.generated_data.get('notes', [])),
                'icd10_codes': len(self.generated_data.get('icd10', [])),
                'cpt_codes': len(self.generated_data.get('cpt', []))
            }
        }
        
        metadata_path = self.output_dir / 'generation_metadata.json'
        with open(metadata_path, 'w') as f:
            json.dump(metadata, f, indent=2)
        
        print(f"\n✓ Metadata exported to {metadata_path}")
    
    def generate(
        self,
        num_patients: int = 1000,
        num_providers: int = 100,
        claims_per_patient: int = 3,
        notes_per_claim: int = 1
    ):
        """Generate all data"""
        print("=" * 60)
        print("Healthcare Claims Data Generation")
        print("=" * 60)
        
        # Generate lookup tables first
        self.generate_lookup_tables()
        
        # Generate core data
        self.generate_core_data(num_patients, num_providers, claims_per_patient, notes_per_claim)
        
        # Export to CSV
        self.export_to_csv()
        
        # Export metadata
        self.export_metadata()
        
        print("\n" + "=" * 60)
        print("Data generation complete!")
        print("=" * 60)
        print(f"\nOutput directory: {self.output_dir.absolute()}")
        print(f"\nGenerated files:")
        for file in sorted(self.output_dir.glob("*.csv")):
            print(f"  - {file.name}")


def main():
    parser = argparse.ArgumentParser(
        description='Generate synthetic healthcare claims data'
    )
    parser.add_argument(
        '--patients',
        type=int,
        default=1000,
        help='Number of patients to generate (default: 1000)'
    )
    parser.add_argument(
        '--providers',
        type=int,
        default=100,
        help='Number of providers to generate (default: 100)'
    )
    parser.add_argument(
        '--claims-per-patient',
        type=int,
        default=3,
        help='Average number of claims per patient (default: 3)'
    )
    parser.add_argument(
        '--notes-per-claim',
        type=int,
        default=1,
        help='Average number of notes per claim (default: 1)'
    )
    parser.add_argument(
        '--seed',
        type=int,
        default=42,
        help='Random seed for reproducibility (default: 42)'
    )
    parser.add_argument(
        '--output-dir',
        type=str,
        default='data/raw',
        help='Output directory for generated files (default: data/raw)'
    )
    
    args = parser.parse_args()
    
    generator = DataGenerator(seed=args.seed, output_dir=Path(args.output_dir))
    generator.generate(
        num_patients=args.patients,
        num_providers=args.providers,
        claims_per_patient=args.claims_per_patient,
        notes_per_claim=args.notes_per_claim
    )


if __name__ == "__main__":
    main()

