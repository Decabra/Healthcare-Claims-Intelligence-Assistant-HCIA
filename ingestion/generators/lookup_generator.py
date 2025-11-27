"""
Lookup table generators for ICD-10 and CPT codes
Generates realistic code sets for development/testing
"""

from typing import List
import random
from faker import Faker

from ingestion.schemas import ICD10Schema, CPTSchema


class ICD10Generator:
    """Generate ICD-10 diagnosis code lookup table"""
    
    def __init__(self, seed: int = None):
        self.fake = Faker()
        if seed:
            Faker.seed(seed)
            random.seed(seed)
        
        # Common ICD-10 code categories with realistic descriptions
        self.icd10_codes = [
            # Diabetes (E10-E14)
            ('E11.9', 'Type 2 diabetes mellitus without complications', 'Endocrine'),
            ('E11.65', 'Type 2 diabetes mellitus with hyperglycemia', 'Endocrine'),
            ('E11.21', 'Type 2 diabetes mellitus with diabetic nephropathy', 'Endocrine'),
            ('E10.9', 'Type 1 diabetes mellitus without complications', 'Endocrine'),
            
            # Hypertension (I10-I16)
            ('I10', 'Essential (primary) hypertension', 'Circulatory'),
            ('I11.9', 'Hypertensive heart disease without heart failure', 'Circulatory'),
            ('I12.9', 'Hypertensive chronic kidney disease', 'Circulatory'),
            
            # Musculoskeletal (M00-M99)
            ('M54.5', 'Low back pain', 'Musculoskeletal'),
            ('M25.561', 'Pain in right knee', 'Musculoskeletal'),
            ('M79.3', 'Panniculitis, unspecified', 'Musculoskeletal'),
            ('M25.511', 'Pain in right shoulder', 'Musculoskeletal'),
            
            # Respiratory (J00-J99)
            ('J44.1', 'Chronic obstructive pulmonary disease with (acute) exacerbation', 'Respiratory'),
            ('J06.9', 'Acute upper respiratory infection, unspecified', 'Respiratory'),
            ('J18.9', 'Pneumonia, unspecified organism', 'Respiratory'),
            ('J45.909', 'Unspecified asthma, uncomplicated', 'Respiratory'),
            
            # Mental Health (F00-F99)
            ('F41.9', 'Anxiety disorder, unspecified', 'Mental Health'),
            ('F32.9', 'Major depressive disorder, single episode, unspecified', 'Mental Health'),
            ('F33.1', 'Major depressive disorder, recurrent, moderate', 'Mental Health'),
            
            # Digestive (K00-K95)
            ('K21.9', 'Gastro-esophageal reflux disease without esophagitis', 'Digestive'),
            ('K59.00', 'Constipation, unspecified', 'Digestive'),
            ('K25.9', 'Gastric ulcer, unspecified as acute or chronic', 'Digestive'),
            
            # Circulatory (I00-I99)
            ('I50.9', 'Heart failure, unspecified', 'Circulatory'),
            ('I25.10', 'Atherosclerotic heart disease of native coronary artery without angina pectoris', 'Circulatory'),
            ('I48.91', 'Unspecified atrial fibrillation', 'Circulatory'),
            
            # Neoplasms (C00-D49)
            ('C50.919', 'Malignant neoplasm of unspecified site of unspecified female breast', 'Neoplasms'),
            ('C78.00', 'Secondary malignant neoplasm of unspecified lung', 'Neoplasms'),
            
            # Injury (S00-T88)
            ('S72.90XA', 'Unspecified fracture of unspecified femur, initial encounter', 'Injury'),
            ('S42.90XA', 'Unspecified fracture of unspecified shoulder girdle, initial encounter', 'Injury'),
            
            # Symptoms (R00-R94)
            ('R50.9', 'Fever, unspecified', 'Symptoms'),
            ('R06.02', 'Shortness of breath', 'Symptoms'),
            ('R51', 'Headache', 'Symptoms'),
            
            # Metabolic (E70-E88)
            ('E78.5', 'Hyperlipidemia, unspecified', 'Metabolic'),
            ('E78.00', 'Pure hypercholesterolemia, unspecified', 'Metabolic'),
            
            # Genitourinary (N00-N99)
            ('N39.0', 'Urinary tract infection, site not specified', 'Genitourinary'),
            ('N18.6', 'End stage renal disease', 'Genitourinary'),
        ]
    
    def generate_icd10_lookup(self) -> List[ICD10Schema]:
        """Generate ICD-10 lookup table"""
        lookup = []
        for code, description, category in self.icd10_codes:
            lookup.append(ICD10Schema(
                code=code,
                description=description,
                category=category,
                is_valid=True
            ))
        return lookup


class CPTGenerator:
    """Generate CPT procedure code lookup table"""
    
    def __init__(self, seed: int = None):
        self.fake = Faker()
        if seed:
            Faker.seed(seed)
            random.seed(seed)
        
        # Common CPT codes with realistic descriptions
        self.cpt_codes = [
            # Evaluation and Management (99201-99499)
            ('99213', 'Office or other outpatient visit for the evaluation and management of an established patient', 'E&M'),
            ('99214', 'Office or other outpatient visit for the evaluation and management of an established patient', 'E&M'),
            ('99215', 'Office or other outpatient visit for the evaluation and management of an established patient', 'E&M'),
            ('99203', 'Office or other outpatient visit for the evaluation and management of a new patient', 'E&M'),
            ('99204', 'Office or other outpatient visit for the evaluation and management of a new patient', 'E&M'),
            ('99284', 'Emergency department visit for the evaluation and management of a patient', 'E&M'),
            ('99285', 'Emergency department visit for the evaluation and management of a patient', 'E&M'),
            
            # Laboratory (80047-89398)
            ('80053', 'Comprehensive metabolic panel', 'Laboratory'),
            ('85027', 'Complete blood count (CBC)', 'Laboratory'),
            ('85610', 'Prothrombin time', 'Laboratory'),
            ('81001', 'Urinalysis, by dip stick or tablet reagent', 'Laboratory'),
            ('80061', 'Lipid panel', 'Laboratory'),
            
            # Radiology (70010-79999)
            ('73060', 'Radiologic examination, knee; 1 or 2 views', 'Radiology'),
            ('72141', 'Magnetic resonance imaging, cervical spine', 'Radiology'),
            ('70450', 'Computed tomography, head or brain; without contrast material', 'Radiology'),
            ('71020', 'Radiologic examination, chest, 2 views', 'Radiology'),
            
            # Surgery (10021-69990)
            ('27447', 'Arthroplasty, knee, condyle and plateau; medial AND lateral compartments', 'Surgery'),
            ('45378', 'Colonoscopy, flexible; diagnostic', 'Surgery'),
            ('47562', 'Laparoscopy, surgical; cholecystectomy', 'Surgery'),
            
            # Medicine (90281-99607)
            ('36415', 'Routine venipuncture for collection of specimen(s)', 'Medicine'),
            ('93000', 'Electrocardiogram, routine ECG with at least 12 leads', 'Medicine'),
            ('94640', 'Noninvasive ventilation', 'Medicine'),
            
            # Pathology (88000-89398)
            ('88304', 'Level III - Surgical pathology, gross and microscopic examination', 'Pathology'),
            ('88305', 'Level IV - Surgical pathology, gross and microscopic examination', 'Pathology'),
        ]
    
    def generate_cpt_lookup(self) -> List[CPTSchema]:
        """Generate CPT lookup table"""
        lookup = []
        for code, description, category in self.cpt_codes:
            lookup.append(CPTSchema(
                code=code,
                description=description,
                category=category,
                is_valid=True
            ))
        return lookup


if __name__ == "__main__":
    # Test generation
    icd10_gen = ICD10Generator(seed=42)
    cpt_gen = CPTGenerator(seed=42)
    
    icd10_codes = icd10_gen.generate_icd10_lookup()
    cpt_codes = cpt_gen.generate_cpt_lookup()
    
    print(f"Generated {len(icd10_codes)} ICD-10 codes")
    print(f"Generated {len(cpt_codes)} CPT codes")
    
    print("\nSample ICD-10 codes:")
    for code in icd10_codes[:5]:
        print(f"  {code.code}: {code.description}")
    
    print("\nSample CPT codes:")
    for code in cpt_codes[:5]:
        print(f"  {code.code}: {code.description}")

