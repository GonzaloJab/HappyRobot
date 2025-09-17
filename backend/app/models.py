"""
Pydantic models for Shipments/Loads API
"""
from datetime import datetime
from typing import Optional, Literal, List
from pydantic import BaseModel, Field, field_validator
import uuid

# Status enum for type safety
StatusType = Literal["pending", "agreed"]

# Phone call enums
CallType = Literal["manual", "agent"]
SentimentType = Literal["positive", "neutral", "negative"]

class ShipmentBase(BaseModel):
    """Base shipment/load model with common fields"""
    # Core/Ops fields
    load_id: str = Field(..., min_length=1, max_length=50, description="Human-readable load ID (e.g., LD-2025-0001)")
    origin: str = Field(..., min_length=1, max_length=200, description="Origin location")
    destination: str = Field(..., min_length=1, max_length=200, description="Destination location")
    pickup_datetime: datetime = Field(..., description="Pickup date and time")
    delivery_datetime: datetime = Field(..., description="Delivery date and time")
    
    # Optional core fields
    equipment_type: Optional[str] = Field(None, max_length=100, description="Equipment type (e.g., Dry Van, Reefer, Flatbed)")
    loadboard_rate: Optional[float] = Field(None, ge=0, description="Listed rate for the load")
    notes: Optional[str] = Field(None, max_length=1000, description="Additional notes")
    weight: Optional[float] = Field(None, ge=0, description="Weight in pounds")
    commodity_type: Optional[str] = Field(None, max_length=100, description="Type of commodity")
    
    # Dashboard/KPI fields
    num_of_pieces: Optional[int] = Field(None, ge=0, description="Number of pieces")
    miles: Optional[float] = Field(None, ge=0, description="Distance in miles")
    dimensions: Optional[str] = Field(None, max_length=200, description="Dimensions (e.g., 48x40x60 in)")
    
    # Agreed/Completed fields (required when status is 'agreed')
    agreed_price: Optional[float] = Field(None, ge=0, description="Agreed price for the load")
    carrier_description: Optional[str] = Field(None, max_length=200, description="Carrier description/name")
    
    # Assignment tracking fields
    assigned_via_url: Optional[bool] = Field(False, description="True if assigned via URL/API, False if assigned manually in frontend")
    time_per_call_seconds: Optional[float] = Field(None, ge=0, description="Actual time per call in seconds (manually input)")
    avg_time_per_call_seconds: Optional[float] = Field(None, ge=0, description="Average time per call in seconds (calculated from time_per_call_seconds)")
    
    # Phone call tracking
    phone_calls: Optional[List['PhoneCall']] = Field(default_factory=list, description="List of phone calls made for this load")
    
    # Status field
    status: Optional[StatusType] = Field(default="pending", description="Load status")

    @field_validator('delivery_datetime')
    @classmethod
    def delivery_after_pickup(cls, v, info):
        """Validate that delivery is after pickup"""
        if info.data and 'pickup_datetime' in info.data and v <= info.data['pickup_datetime']:
            raise ValueError('delivery_datetime must be after pickup_datetime')
        return v
    
    @field_validator('agreed_price')
    @classmethod
    def validate_agreed_price(cls, v, info):
        """Validate agreed_price is provided when status is agreed"""
        if info.data and info.data.get('status') == 'agreed' and v is None:
            raise ValueError('agreed_price is required when status is agreed')
        return v
    
    @field_validator('carrier_description')
    @classmethod
    def validate_carrier_description(cls, v, info):
        """Validate carrier_description is provided when status is agreed"""
        if info.data and info.data.get('status') == 'agreed' and (v is None or v.strip() == ''):
            raise ValueError('carrier_description is required when status is agreed')
        return v

class ShipmentCreate(ShipmentBase):
    """Model for creating new shipments/loads"""
    # All required fields are in ShipmentBase
    pass

class ShipmentUpdate(BaseModel):
    """Model for updating shipments (partial update)"""
    load_id: Optional[str] = Field(None, min_length=1, max_length=50)
    origin: Optional[str] = Field(None, min_length=1, max_length=200)
    destination: Optional[str] = Field(None, min_length=1, max_length=200)
    pickup_datetime: Optional[datetime] = None
    delivery_datetime: Optional[datetime] = None
    equipment_type: Optional[str] = Field(None, max_length=100)
    loadboard_rate: Optional[float] = Field(None, ge=0)
    notes: Optional[str] = Field(None, max_length=1000)
    weight: Optional[float] = Field(None, ge=0)
    commodity_type: Optional[str] = Field(None, max_length=100)
    num_of_pieces: Optional[int] = Field(None, ge=0)
    miles: Optional[float] = Field(None, ge=0)
    dimensions: Optional[str] = Field(None, max_length=200)
    status: Optional[StatusType] = None
    agreed_price: Optional[float] = Field(None, ge=0)
    carrier_description: Optional[str] = Field(None, max_length=200)
    assigned_via_url: Optional[bool] = None
    time_per_call_seconds: Optional[float] = Field(None, ge=0)
    avg_time_per_call_seconds: Optional[float] = Field(None, ge=0)

class Shipment(ShipmentBase):
    """Complete shipment/load model with all fields"""
    id: str = Field(default_factory=lambda: str(uuid.uuid4()), description="Internal UUID")
    created_at: datetime = Field(default_factory=datetime.utcnow, description="Creation timestamp")
    updated_at: datetime = Field(default_factory=datetime.utcnow, description="Last update timestamp")

    model_config = {
        "json_schema_extra": {
            "examples": [
                {
                    "id": "123e4567-e89b-12d3-a456-426614174000",
                    "load_id": "LD-2025-0001",
                    "origin": "Madrid",
                    "destination": "Paris",
                    "pickup_datetime": "2025-09-11T08:00:00Z",
                    "delivery_datetime": "2025-09-12T18:00:00Z",
                    "equipment_type": "Dry Van",
                    "loadboard_rate": 1800.50,
                    "notes": "Fragile—handle with care",
                    "weight": 2200,
                    "commodity_type": "Electronics",
                    "num_of_pieces": 120,
                    "miles": 765,
                    "dimensions": "48x40x60 in",
                    "agreed_price": None,
                    "carrier_description": None,
                    "assigned_via_url": False,
                    "time_per_call_seconds": None,
                    "avg_time_per_call_seconds": None,
                    "status": "pending",
                    "created_at": "2025-01-01T00:00:00Z",
                    "updated_at": "2025-01-01T00:00:00Z"
                }
            ]
        }
    }

# Filter models for API queries
class ShipmentFilters(BaseModel):
    """Query filters for shipments"""
    status: Optional[StatusType] = None
    equipment_type: Optional[str] = None
    commodity_type: Optional[str] = None
    origin: Optional[str] = None
    destination: Optional[str] = None
    pickup_from: Optional[datetime] = None
    pickup_to: Optional[datetime] = None
    delivery_from: Optional[datetime] = None
    delivery_to: Optional[datetime] = None
    q: Optional[str] = Field(None, description="Search in load_id, origin, destination, commodity_type, notes")
    assigned_via_url: Optional[bool] = Field(None, description="Filter by assignment source: true for URL/API, false for manual")
    sort_by: Optional[str] = Field("created_at", description="Sort field")
    sort_order: Optional[Literal["asc", "desc"]] = Field("desc", description="Sort order")

# Phone Call Models
class PhoneCallBase(BaseModel):
    """Base phone call model"""
    agreed: bool = Field(..., description="Whether the call resulted in an agreement")
    seconds: float = Field(..., ge=0, description="Duration of the call in seconds")
    call_type: CallType = Field(..., description="Type of call: manual or agent")
    call_id: Optional[str] = Field(None, max_length=50, description="ID of the call")
    sentiment: SentimentType = Field(..., description="Sentiment of the caller")
    notes: Optional[str] = Field(None, max_length=500, description="Additional notes about the call")

class PhoneCallCreate(BaseModel):
    """Model for creating new phone calls with flexible input types"""
    agreed: bool = Field(..., description="Whether the call resulted in an agreement")
    seconds: float = Field(..., ge=0, description="Duration of the call in seconds")
    call_type: CallType = Field(..., description="Type of call: manual or agent")
    call_id: Optional[str] = Field(None, max_length=50, description="ID of the call")
    sentiment: SentimentType = Field(..., description="Sentiment of the caller")
    notes: Optional[str] = Field(None, max_length=500, description="Additional notes about the call")
    
    @field_validator('agreed', mode='before')
    @classmethod
    def parse_agreed(cls, v):
        """Parse agreed field from string or boolean"""
        if isinstance(v, bool):
            return v
        if isinstance(v, str):
            v_lower = v.lower().strip()
            if v_lower in ('true', '1', 'yes', 'y'):
                return True
            elif v_lower in ('false', '0', 'no', 'n'):
                return False
            else:
                raise ValueError(f"Invalid boolean value: '{v}'. Expected 'true'/'false', '1'/'0', 'yes'/'no', or 'y'/'n'")
        raise ValueError(f"Invalid type for 'agreed': {type(v)}. Expected bool or str")
    
    @field_validator('seconds', mode='before')
    @classmethod
    def parse_seconds(cls, v):
        """Parse seconds field from string or number"""
        if isinstance(v, (int, float)):
            return float(v)
        if isinstance(v, str):
            try:
                return float(v.strip())
            except ValueError:
                raise ValueError(f"Invalid number format for 'seconds': '{v}'. Expected a valid number")
        raise ValueError(f"Invalid type for 'seconds': {type(v)}. Expected number or str")

class PhoneCall(PhoneCallBase):
    """Complete phone call model with all fields"""
    id: str = Field(default_factory=lambda: str(uuid.uuid4()), description="Internal UUID")
    shipment_id: str = Field(..., description="ID of the shipment this call belongs to")
    created_at: datetime = Field(default_factory=datetime.utcnow, description="Creation timestamp")
    
    # Optional shipment context fields (added when returning all calls)
    shipment_load_id: Optional[str] = Field(None, description="Load ID of the shipment")
    shipment_origin: Optional[str] = Field(None, description="Origin of the shipment")
    shipment_destination: Optional[str] = Field(None, description="Destination of the shipment")

    model_config = {
        "json_schema_extra": {
            "examples": [
                {
                    "id": "123e4567-e89b-12d3-a456-426614174000",
                    "shipment_id": "456e7890-e89b-12d3-a456-426614174001",
                    "agreed": True,
                    "seconds": 930.0,
                    "call_type": "manual",
                    "sentiment": "positive",
                    "notes": "Carrier was very interested and agreed to the rate",
                    "created_at": "2025-01-01T00:00:00Z"
                }
            ]
        }
    }

# Update forward references
ShipmentBase.model_rebuild()
PhoneCallBase.model_rebuild()
PhoneCallCreate.model_rebuild()
PhoneCall.model_rebuild()
