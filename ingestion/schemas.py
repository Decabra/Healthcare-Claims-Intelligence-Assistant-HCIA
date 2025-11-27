"""
Schema definitions for healthcare claims data
Pydantic models for validation and type safety
"""

from datetime import date, datetime
from typing import Optional, List
from pydantic import BaseModel, Field, validator
import re


class PatientSchema(BaseModel):
    """Patient demographic data (HIPAA-compliant, de-identified)"""
    patient_id: str = Field(..., description="Unique patient identifier")
    date_of_birth: date = Field(..., description="Date of birth (de-identified)")
    gender: str = Field(..., description="Gender: M, F, O, U")
    zip_code: str = Field(..., description="ZIP code (first 3 digits for privacy)")
    state: str = Field(..., description="State code (2 letters)")
    created_at: datetime = Field(default_factory=datetime.now)
    
    @validator('gender')
    def validate_gender(cls, v):
        assert v in ['M', 'F', 'O', 'U'], "Gender must be M, F, O, or U"
        return v
    
    @validator('zip_code')
    def validate_zip(cls, v):
        assert re.match(r'^\d{3}', v), "ZIP code must start with 3 digits"
        return v[:3]


class ProviderSchema(BaseModel):
    """Healthcare provider information"""
    provider_id: str = Field(..., description="Unique provider identifier")
    npi: str = Field(..., description="National Provider Identifier (10 digits)")
    provider_name: str = Field(..., description="Provider name")
    provider_type: str = Field(..., description="Provider type (e.g., PHYSICIAN, HOSPITAL)")
    specialty: Optional[str] = Field(None, description="Medical specialty")
    address: str = Field(..., description="Provider address")
    city: str = Field(..., description="City")
    state: str = Field(..., description="State code")
    zip_code: str = Field(..., description="ZIP code")
    created_at: datetime = Field(default_factory=datetime.now)
    
    @validator('npi')
    def validate_npi(cls, v):
        assert len(v) == 10 and v.isdigit(), "NPI must be 10 digits"
        return v


class ClaimSchema(BaseModel):
    """Healthcare claim data"""
    claim_id: str = Field(..., description="Unique claim identifier")
    patient_id: str = Field(..., description="Patient identifier")
    provider_id: str = Field(..., description="Provider identifier")
    claim_date: date = Field(..., description="Date of service")
    admission_date: Optional[date] = Field(None, description="Admission date (if inpatient)")
    discharge_date: Optional[date] = Field(None, description="Discharge date (if inpatient)")
    claim_type: str = Field(..., description="Claim type: INPATIENT, OUTPATIENT, EMERGENCY, etc.")
    total_charge: float = Field(..., description="Total charge amount")
    total_paid: float = Field(..., description="Total amount paid")
    claim_status: str = Field(..., description="Status: APPROVED, DENIED, PENDING, PARTIAL")
    denial_reason: Optional[str] = Field(None, description="Denial reason code if denied")
    primary_diagnosis_code: str = Field(..., description="Primary ICD-10 diagnosis code")
    primary_procedure_code: Optional[str] = Field(None, description="Primary CPT procedure code")
    created_at: datetime = Field(default_factory=datetime.now)
    
    @validator('claim_type')
    def validate_claim_type(cls, v):
        valid_types = ['INPATIENT', 'OUTPATIENT', 'EMERGENCY', 'AMBULATORY', 'PHYSICIAN']
        assert v in valid_types, f"Claim type must be one of {valid_types}"
        return v
    
    @validator('claim_status')
    def validate_status(cls, v):
        valid_statuses = ['APPROVED', 'DENIED', 'PENDING', 'PARTIAL', 'REJECTED']
        assert v in valid_statuses, f"Status must be one of {valid_statuses}"
        return v
    
    @validator('total_charge', 'total_paid')
    def validate_amounts(cls, v):
        assert v >= 0, "Amounts must be non-negative"
        return round(v, 2)


class NoteSchema(BaseModel):
    """Clinical notes associated with claims"""
    note_id: str = Field(..., description="Unique note identifier")
    claim_id: str = Field(..., description="Associated claim identifier")
    note_type: str = Field(..., description="Note type: ADMISSION, DISCHARGE, PROGRESS, PROCEDURE")
    note_text: str = Field(..., description="Clinical note text")
    created_at: datetime = Field(default_factory=datetime.now)
    
    @validator('note_type')
    def validate_note_type(cls, v):
        valid_types = ['ADMISSION', 'DISCHARGE', 'PROGRESS', 'PROCEDURE', 'DIAGNOSIS']
        assert v in valid_types, f"Note type must be one of {valid_types}"
        return v


class ICD10Schema(BaseModel):
    """ICD-10 diagnosis code"""
    code: str = Field(..., description="ICD-10 code")
    description: str = Field(..., description="Code description")
    category: str = Field(..., description="Category/chapter")
    is_valid: bool = Field(True, description="Whether code is currently valid")


class CPTSchema(BaseModel):
    """CPT procedure code"""
    code: str = Field(..., description="CPT code")
    description: str = Field(..., description="Code description")
    category: str = Field(..., description="Category")
    is_valid: bool = Field(True, description="Whether code is currently valid")

