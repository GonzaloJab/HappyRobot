"""
FastAPI Shipments Application
"""
import os
import logging
from datetime import datetime
from typing import Dict, List, Optional
from fastapi import FastAPI, HTTPException, status, Depends, Header
from fastapi.responses import JSONResponse

from .models import Shipment, ShipmentCreate, ShipmentUpdate, ShipmentFilters, StatusType, PhoneCall, PhoneCallCreate
from .deps import setup_cors, get_port

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# In-memory storage for demo purposes
# TODO: Replace with SQLite/SQLModel for production
# Example SQLModel setup:
# from sqlmodel import SQLModel, create_engine, Session
# engine = create_engine("sqlite:///shipments.db")
# SQLModel.metadata.create_all(engine)
shipments_db: Dict[str, Shipment] = {}
phone_calls_db: Dict[str, PhoneCall] = {}

# API Key configuration
API_KEY = os.getenv("API_KEY", "happyrobot-api-key-2025")  # Default key for development
REQUIRE_API_KEY = os.getenv("REQUIRE_API_KEY", "true").lower() == "true"
#print the first 10 characters of the API_KEY
print("API_KEY:",API_KEY[:10])

def verify_api_key(x_api_key: Optional[str] = Header(None)) -> str:
    """
    Verify API key from request headers
    
    Args:
        x_api_key: API key from X-API-Key header
        
    Returns:
        The verified API key
        
    Raises:
        HTTPException: If API key is missing or invalid
    """
    if not REQUIRE_API_KEY:
        return "development-mode"
    
    if not x_api_key:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="API key required. Please provide X-API-Key header.",
            headers={"WWW-Authenticate": "ApiKey"},
        )
    
    if x_api_key != API_KEY:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid API key",
            headers={"WWW-Authenticate": "ApiKey"},
        )
    
    return x_api_key

def resolve_shipment_id(identifier: str) -> str:
    """
    Resolve shipment identifier to internal UUID.
    Accepts both UUID format and human-readable load_id format.
    
    Args:
        identifier: Either UUID or load_id (e.g., "LD-2025-0002")
        
    Returns:
        The internal UUID for the shipment
        
    Raises:
        HTTPException: If shipment not found
    """
    # First, try direct UUID lookup
    if identifier in shipments_db:
        return identifier
    
    # If not found, search by load_id
    for shipment in shipments_db.values():
        if shipment.load_id == identifier:
            return shipment.id
    
    # If still not found, raise 404
    raise HTTPException(
        status_code=status.HTTP_404_NOT_FOUND,
        detail=f"Shipment with id '{identifier}' not found"
    )

app = FastAPI(
    title="Shipments API",
    description="A simple CRUD API for managing shipments",
    version="1.0.0"
)

# Setup CORS
setup_cors(app)

def load_seed_data(path: str = "data/seed_shipments.xlsx") -> None:
    """
    Load shipment data from Excel or CSV file on startup
    """
    try:
        import pandas as pd
        from datetime import datetime
        
        # Try CSV first, then Excel as fallback
        csv_path = path.replace('.xlsx', '.csv')
        excel_path = path
        
        if os.path.exists(csv_path):
            logger.info(f"Loading seed data from {csv_path}")
            df = pd.read_csv(csv_path)
        elif os.path.exists(excel_path):
            logger.info(f"Loading seed data from {excel_path}")
            df = pd.read_excel(excel_path, engine='openpyxl')
        else:
            logger.info(f"Seed data file not found at {csv_path} or {excel_path}, skipping data load")
            return
        
        # Validate required columns
        required_columns = ["load_id", "origin", "destination", "pickup_datetime", "delivery_datetime"]
        missing_columns = [col for col in required_columns if col not in df.columns]
        if missing_columns:
            logger.error(f"Missing required columns: {missing_columns}")
            return
        
        loaded_count = 0
        duplicate_count = 0
        
        for _, row in df.iterrows():
            try:
                # Skip rows with missing required fields
                if (pd.isna(row.get("load_id")) or not str(row["load_id"]).strip() or
                    pd.isna(row.get("origin")) or not str(row["origin"]).strip() or
                    pd.isna(row.get("destination")) or not str(row["destination"]).strip()):
                    continue
                
                # Create shipment data
                shipment_data = {
                    "load_id": str(row["load_id"]).strip(),
                    "origin": str(row["origin"]).strip(),
                    "destination": str(row["destination"]).strip(),
                    "status": "pending"
                }
                
                # Handle pickup_datetime
                if not pd.isna(row.get("pickup_datetime")):
                    try:
                        if isinstance(row["pickup_datetime"], str):
                            shipment_data["pickup_datetime"] = datetime.fromisoformat(row["pickup_datetime"].replace("Z", "+00:00"))
                        else:
                            shipment_data["pickup_datetime"] = row["pickup_datetime"]
                    except Exception as e:
                        logger.warning(f"Could not parse pickup_datetime: {row.get('pickup_datetime')}, error: {e}")
                        continue
                else:
                    continue
                
                # Handle delivery_datetime (with backward compatibility for eta)
                delivery_dt = None
                if not pd.isna(row.get("delivery_datetime")):
                    try:
                        if isinstance(row["delivery_datetime"], str):
                            delivery_dt = datetime.fromisoformat(row["delivery_datetime"].replace("Z", "+00:00"))
                        else:
                            delivery_dt = row["delivery_datetime"]
                    except Exception as e:
                        logger.warning(f"Could not parse delivery_datetime: {row.get('delivery_datetime')}, error: {e}")
                elif not pd.isna(row.get("eta")):  # Backward compatibility
                    try:
                        if isinstance(row["eta"], str):
                            delivery_dt = datetime.fromisoformat(row["eta"].replace("Z", "+00:00"))
                        else:
                            delivery_dt = row["eta"]
                        logger.info(f"Mapped eta to delivery_datetime for load_id: {shipment_data['load_id']}")
                    except Exception as e:
                        logger.warning(f"Could not parse eta: {row.get('eta')}, error: {e}")
                
                if delivery_dt is None:
                    continue
                shipment_data["delivery_datetime"] = delivery_dt
                
                # Handle optional fields
                optional_fields = [
                    "equipment_type", "loadboard_rate", "notes", "weight", 
                    "commodity_type", "num_of_pieces", "miles", "dimensions"
                ]
                
                for field in optional_fields:
                    if not pd.isna(row.get(field)):
                        value = row[field]
                        if field in ["loadboard_rate", "weight", "miles"]:
                            try:
                                shipment_data[field] = float(value)
                            except (ValueError, TypeError):
                                logger.warning(f"Could not parse {field} as float: {value}")
                        elif field == "num_of_pieces":
                            try:
                                shipment_data[field] = int(value)
                            except (ValueError, TypeError):
                                logger.warning(f"Could not parse {field} as int: {value}")
                        else:
                            shipment_data[field] = str(value).strip()
                
                # Handle status
                if not pd.isna(row.get("status")):
                    status_val = str(row["status"]).lower().strip()
                    if status_val in ["pending", "agreed"]:
                        shipment_data["status"] = status_val
                
                # Check for duplicate load_id
                load_id = shipment_data["load_id"]
                if any(s.load_id == load_id for s in shipments_db.values()):
                    duplicate_count += 1
                    shipment_data["load_id"] = f"{load_id}-DUP{duplicate_count}"
                    logger.warning(f"Duplicate load_id found, renamed to: {shipment_data['load_id']}")
                
                # Set assigned_via_url to False for seed data (historical manual assignments)
                shipment_data['assigned_via_url'] = False
                
                # Add some sample avg_time_per_call_seconds for demo purposes
                if shipment_data.get('status') == 'agreed':
                    # Simulate realistic call times (30-300 seconds)
                    shipment_data['avg_time_per_call_seconds'] = 60 + (hash(shipment_data['load_id']) % 240)
                
                # Create shipment
                shipment = Shipment(**shipment_data)
                shipments_db[shipment.id] = shipment
                loaded_count += 1
                
            except Exception as e:
                logger.error(f"Error processing row {_}: {e}")
                continue
        
        logger.info(f"Successfully loaded {loaded_count} shipments from seed data")
        
    except ImportError:
        logger.error("pandas not available, cannot load seed data")
    except Exception as e:
        logger.error(f"Error loading seed data: {e}")

@app.on_event("startup")
async def startup_event():
    """Load seed data on application startup"""
    logger.info("Starting up application...")
    load_seed_data()
    logger.info(f"Application startup complete. Loaded {len(shipments_db)} shipments.")

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy", "timestamp": datetime.utcnow().isoformat()}

@app.get("/debug")
async def debug_info(api_key: str = Depends(verify_api_key)):
    """Debug endpoint to check database state"""
    return {
        "shipments_count": len(shipments_db),
        "shipments": list(shipments_db.values()),
        "data_files": {
            "csv_exists": os.path.exists("data/seed_shipments.csv"),
            "excel_exists": os.path.exists("data/seed_shipments.xlsx")
        }
    }

@app.get("/shipments", response_model=List[Shipment])
async def get_shipments(
    status: Optional[StatusType] = None,
    equipment_type: Optional[str] = None,
    commodity_type: Optional[str] = None,
    origin: Optional[str] = None,
    destination: Optional[str] = None,
    pickup_from: Optional[datetime] = None,
    pickup_to: Optional[datetime] = None,
    delivery_from: Optional[datetime] = None,
    delivery_to: Optional[datetime] = None,
    q: Optional[str] = None,
    assigned_via_url: Optional[bool] = None,
    sort_by: str = "created_at",
    sort_order: str = "desc",
    api_key: str = Depends(verify_api_key)
):
    """
    Get all shipments with optional filtering and sorting
    """
    shipments = list(shipments_db.values())
    
    # Apply filters
    if status:
        shipments = [s for s in shipments if s.status == status]
    
    if equipment_type:
        shipments = [s for s in shipments if s.equipment_type and equipment_type.lower() in s.equipment_type.lower()]
    
    if commodity_type:
        shipments = [s for s in shipments if s.commodity_type and commodity_type.lower() in s.commodity_type.lower()]
    
    if origin:
        shipments = [s for s in shipments if origin.lower() in s.origin.lower()]
    
    if destination:
        shipments = [s for s in shipments if destination.lower() in s.destination.lower()]
    
    if pickup_from:
        shipments = [s for s in shipments if s.pickup_datetime >= pickup_from]
    
    if pickup_to:
        shipments = [s for s in shipments if s.pickup_datetime <= pickup_to]
    
    if delivery_from:
        shipments = [s for s in shipments if s.delivery_datetime >= delivery_from]
    
    if delivery_to:
        shipments = [s for s in shipments if s.delivery_datetime <= delivery_to]
    
    if assigned_via_url is not None:
        shipments = [s for s in shipments if s.assigned_via_url == assigned_via_url]
    
    # Text search
    if q:
        q_lower = q.lower()
        shipments = [s for s in shipments if (
            q_lower in s.load_id.lower() or
            q_lower in s.origin.lower() or
            q_lower in s.destination.lower() or
            (s.commodity_type and q_lower in s.commodity_type.lower()) or
            (s.notes and q_lower in s.notes.lower())
        )]
    
    # Sort
    reverse = sort_order.lower() == "desc"
    if sort_by == "pickup_datetime":
        shipments.sort(key=lambda x: x.pickup_datetime, reverse=reverse)
    elif sort_by == "delivery_datetime":
        shipments.sort(key=lambda x: x.delivery_datetime, reverse=reverse)
    elif sort_by == "loadboard_rate":
        shipments.sort(key=lambda x: x.loadboard_rate or 0, reverse=reverse)
    elif sort_by == "miles":
        shipments.sort(key=lambda x: x.miles or 0, reverse=reverse)
    else:  # default to created_at
        shipments.sort(key=lambda x: x.created_at, reverse=reverse)
    
    return shipments

@app.get("/shipments/stats", response_model=Dict)
async def get_shipments_stats(
    status: Optional[StatusType] = None,
    equipment_type: Optional[str] = None,
    commodity_type: Optional[str] = None,
    origin: Optional[str] = None,
    destination: Optional[str] = None,
    pickup_from: Optional[datetime] = None,
    pickup_to: Optional[datetime] = None,
    delivery_from: Optional[datetime] = None,
    delivery_to: Optional[datetime] = None,
    q: Optional[str] = None,
    assigned_via_url: Optional[bool] = None,
    api_key: str = Depends(verify_api_key)
):
    """
    Get statistics for shipments split by assignment source (Manual vs URL/API)
    """
    shipments = list(shipments_db.values())
    
    # Apply the same filters as get_shipments
    if status:
        shipments = [s for s in shipments if s.status == status]
    
    if equipment_type:
        shipments = [s for s in shipments if s.equipment_type and equipment_type.lower() in s.equipment_type.lower()]
    
    if commodity_type:
        shipments = [s for s in shipments if s.commodity_type and commodity_type.lower() in s.commodity_type.lower()]
    
    if origin:
        shipments = [s for s in shipments if origin.lower() in s.origin.lower()]
    
    if destination:
        shipments = [s for s in shipments if destination.lower() in s.destination.lower()]
    
    if pickup_from:
        shipments = [s for s in shipments if s.pickup_datetime >= pickup_from]
    
    if pickup_to:
        shipments = [s for s in shipments if s.pickup_datetime <= pickup_to]
    
    if delivery_from:
        shipments = [s for s in shipments if s.delivery_datetime >= delivery_from]
    
    if delivery_to:
        shipments = [s for s in shipments if s.delivery_datetime <= delivery_to]
    
    if assigned_via_url is not None:
        shipments = [s for s in shipments if s.assigned_via_url == assigned_via_url]
    
    # Text search
    if q:
        q_lower = q.lower()
        shipments = [s for s in shipments if (
            q_lower in s.load_id.lower() or
            q_lower in s.origin.lower() or
            q_lower in s.destination.lower() or
            (s.commodity_type and q_lower in s.commodity_type.lower()) or
            (s.notes and q_lower in s.notes.lower())
        )]
    
    # Split by assignment source
    manual_shipments = [s for s in shipments if not s.assigned_via_url]
    url_api_shipments = [s for s in shipments if s.assigned_via_url]
    
    def calculate_stats(shipment_list):
        # Only count and calculate stats for ASSIGNED loads (status = "agreed")
        assigned_shipments = [s for s in shipment_list if s.status == 'agreed']
        
        count = len(assigned_shipments)
        total_agreed_price = sum(s.agreed_price or 0 for s in assigned_shipments)
        total_agreed_minus_loadboard = sum((s.agreed_price or 0) - (s.loadboard_rate or 0) for s in assigned_shipments)
        
        # Calculate average time per call using actual time_per_call_seconds values
        total_time_seconds = 0
        valid_time_count = 0
        
        for s in assigned_shipments:
            if s.time_per_call_seconds is not None and s.time_per_call_seconds > 0:
                total_time_seconds += s.time_per_call_seconds
                valid_time_count += 1
        
        avg_time_per_call = total_time_seconds / valid_time_count if valid_time_count > 0 else 0
        
        # Calculate phone call statistics split by call type (manual vs agent)
        manual_phone_calls = 0
        manual_agreed_calls = 0
        manual_total_minutes = 0.0
        
        agent_phone_calls = 0
        agent_agreed_calls = 0
        agent_total_minutes = 0.0
        
        for s in shipment_list:  # Count phone calls for all shipments, not just assigned ones
            if s.phone_calls:
                for call in s.phone_calls:
                    if call.call_type == "manual":
                        manual_phone_calls += 1
                        manual_total_minutes += call.minutes
                        if call.agreed:
                            manual_agreed_calls += 1
                    elif call.call_type == "agent":
                        agent_phone_calls += 1
                        agent_total_minutes += call.minutes
                        if call.agreed:
                            agent_agreed_calls += 1
        
        return {
            "count": count,
            "total_agreed_price": total_agreed_price,
            "total_agreed_minus_loadboard": total_agreed_minus_loadboard,
            "avg_time_per_call_seconds": avg_time_per_call,
            "phone_calls": {
                "manual": {
                    "total_calls": manual_phone_calls,
                    "agreed_calls": manual_agreed_calls,
                    "total_minutes": round(manual_total_minutes, 1)
                },
                "agent": {
                    "total_calls": agent_phone_calls,
                    "agreed_calls": agent_agreed_calls,
                    "total_minutes": round(agent_total_minutes, 1)
                }
            }
        }
    
    # Calculate combined phone call stats for all shipments
    all_shipments = shipments  # Use the filtered shipments list
    
    # Calculate phone call statistics split by call type (manual vs agent)
    manual_phone_calls = 0
    manual_agreed_calls = 0
    manual_total_minutes = 0.0
    
    agent_phone_calls = 0
    agent_agreed_calls = 0
    agent_total_minutes = 0.0
    
    for s in all_shipments:  # Count phone calls for all shipments
        if s.phone_calls:
            for call in s.phone_calls:
                if call.call_type == "manual":
                    manual_phone_calls += 1
                    manual_total_minutes += call.minutes
                    if call.agreed:
                        manual_agreed_calls += 1
                elif call.call_type == "agent":
                    agent_phone_calls += 1
                    agent_total_minutes += call.minutes
                    if call.agreed:
                        agent_agreed_calls += 1
    
    # Create combined phone call stats
    combined_phone_stats = {
        "manual": {
            "total_calls": manual_phone_calls,
            "agreed_calls": manual_agreed_calls,
            "total_minutes": round(manual_total_minutes, 1)
        },
        "agent": {
            "total_calls": agent_phone_calls,
            "agreed_calls": agent_agreed_calls,
            "total_minutes": round(agent_total_minutes, 1)
        }
    }
    
    # Get assignment-based stats
    manual_assignment_stats = calculate_stats(manual_shipments)
    url_api_assignment_stats = calculate_stats(url_api_shipments)
    
    return {
        "manual": {
            **manual_assignment_stats,
            "phone_calls": combined_phone_stats
        },
        "url_api": {
            **url_api_assignment_stats,
            "phone_calls": combined_phone_stats
        }
    }

@app.get("/shipments/random", response_model=Shipment)
async def get_random_shipment(
    origin: Optional[str] = None,
    api_key: str = Depends(verify_api_key)
):
    """
    Get a random shipment/load with pending status. Optionally filter by origin.
    """
    import random
    
    # Only get shipments with pending status
    shipments = [s for s in shipments_db.values() if s.status == "pending"]
    
    # Filter by origin if provided
    if origin:
        shipments = [s for s in shipments if origin.lower() in s.origin.lower()]
    
    if not shipments:
        origin_msg = f" with origin containing '{origin}'" if origin else ""
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"No pending shipments found{origin_msg}"
        )
    
    # Return a random pending shipment
    return random.choice(shipments)

@app.get("/shipments/{shipment_id}", response_model=Shipment)
async def get_shipment(shipment_id: str, api_key: str = Depends(verify_api_key)):
    """
    Get a specific shipment by ID (accepts both UUID and load_id format)
    """
    resolved_id = resolve_shipment_id(shipment_id)
    return shipments_db[resolved_id]

@app.post("/shipments", response_model=Shipment, status_code=status.HTTP_201_CREATED)
async def create_shipment(shipment_data: ShipmentCreate, api_key: str = Depends(verify_api_key)):
    """
    Create a new shipment/load
    """
    # Check for duplicate load_id
    if any(s.load_id == shipment_data.load_id for s in shipments_db.values()):
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=f"Load ID '{shipment_data.load_id}' already exists"
        )
    
    # Set assigned_via_url to True for API-based creation
    shipment_dict = shipment_data.model_dump()
    shipment_dict['assigned_via_url'] = True
    
    # Add some sample avg_time_per_call_seconds for API-created shipments
    if shipment_dict.get('status') == 'agreed':
        # API calls are typically faster (10-120 seconds)
        shipment_dict['avg_time_per_call_seconds'] = 30 + (hash(shipment_dict['load_id']) % 90)
    
    shipment = Shipment(**shipment_dict)
    shipments_db[shipment.id] = shipment
    logger.info(f"Created shipment: {shipment.id} with load_id: {shipment.load_id} (assigned_via_url=True)")
    return shipment

@app.patch("/shipments/{shipment_id}", response_model=Shipment)
async def update_shipment(shipment_id: str, update_data: ShipmentUpdate, api_key: str = Depends(verify_api_key)):
    """
    Update an existing shipment (API-based update - sets assigned_via_url to True)
    Accepts both UUID and load_id format
    """
    resolved_id = resolve_shipment_id(shipment_id)
    shipment = shipments_db[resolved_id]
    
    # Update fields
    update_dict = update_data.model_dump(exclude_unset=True)
    for field, value in update_dict.items():
        setattr(shipment, field, value)
    
    # Set assigned_via_url to True for API-based updates
    shipment.assigned_via_url = True
    
    # Set avg_time_per_call_seconds from the provided time_per_call_seconds
    if update_dict.get('time_per_call_seconds') is not None:
        shipment.time_per_call_seconds = update_dict['time_per_call_seconds']
        shipment.avg_time_per_call_seconds = update_dict['time_per_call_seconds']
    elif update_dict.get('status') == 'agreed' and not shipment.avg_time_per_call_seconds:
        # Fallback: if no time_per_call_seconds provided, use a default for API calls
        shipment.avg_time_per_call_seconds = 30.0  # Default 30 seconds for API calls
    
    # Update timestamp
    shipment.updated_at = datetime.utcnow()
    
    shipments_db[resolved_id] = shipment
    logger.info(f"Updated shipment: {resolved_id} (assigned_via_url=True)")
    return shipment

@app.patch("/shipments/{shipment_id}/manual", response_model=Shipment)
async def update_shipment_manual(shipment_id: str, update_data: ShipmentUpdate, api_key: str = Depends(verify_api_key)):
    """
    Update an existing shipment via manual frontend assignment (sets assigned_via_url to False)
    Accepts both UUID and load_id format
    """
    resolved_id = resolve_shipment_id(shipment_id)
    shipment = shipments_db[resolved_id]
    
    # Update fields
    update_dict = update_data.model_dump(exclude_unset=True)
    for field, value in update_dict.items():
        setattr(shipment, field, value)
    
    # Set assigned_via_url to False for manual frontend updates
    shipment.assigned_via_url = False
    
    # Set avg_time_per_call_seconds from the provided time_per_call_seconds
    if update_dict.get('time_per_call_seconds') is not None:
        shipment.time_per_call_seconds = update_dict['time_per_call_seconds']
        shipment.avg_time_per_call_seconds = update_dict['time_per_call_seconds']
    elif update_dict.get('status') == 'agreed' and not shipment.avg_time_per_call_seconds:
        # Fallback: if no time_per_call_seconds provided, use a default for manual calls
        shipment.avg_time_per_call_seconds = 120.0  # Default 2 minutes for manual calls
    
    # Update timestamp
    shipment.updated_at = datetime.utcnow()
    
    shipments_db[resolved_id] = shipment
    logger.info(f"Updated shipment: {resolved_id} (assigned_via_url=False)")
    return shipment

@app.delete("/shipments/{shipment_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_shipment(shipment_id: str, api_key: str = Depends(verify_api_key)):
    """
    Delete a shipment (accepts both UUID and load_id format)
    """
    resolved_id = resolve_shipment_id(shipment_id)
    del shipments_db[resolved_id]
    logger.info(f"Deleted shipment: {resolved_id}")
    return JSONResponse(status_code=status.HTTP_204_NO_CONTENT, content=None)

# Phone Call Endpoints
@app.post("/shipments/{shipment_id}/phone-calls", response_model=PhoneCall, status_code=status.HTTP_201_CREATED)
async def add_phone_call(
    shipment_id: str, 
    phone_call_data: PhoneCallCreate,
    api_key: str = Depends(verify_api_key)
):
    """
    Add a phone call to a shipment
    """
    resolved_id = resolve_shipment_id(shipment_id)
    
    if resolved_id not in shipments_db:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Shipment not found: {shipment_id}"
        )
    
    # Create the phone call
    phone_call = PhoneCall(
        shipment_id=resolved_id,
        **phone_call_data.model_dump()
    )
    
    # Store in phone calls database
    phone_calls_db[phone_call.id] = phone_call
    
    # Add to shipment's phone calls list
    shipment = shipments_db[resolved_id]
    if shipment.phone_calls is None:
        shipment.phone_calls = []
    shipment.phone_calls.append(phone_call)
    
    # Update shipment's updated_at timestamp
    shipment.updated_at = datetime.utcnow()
    
    logger.info(f"Added phone call {phone_call.id} to shipment {resolved_id}")
    return phone_call

@app.delete("/shipments/{shipment_id}/phone-calls", status_code=status.HTTP_204_NO_CONTENT)
async def delete_all_phone_calls(
    shipment_id: str,
    api_key: str = Depends(verify_api_key)
):
    """
    Delete all phone calls for a shipment
    """
    resolved_id = resolve_shipment_id(shipment_id)
    
    if resolved_id not in shipments_db:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Shipment not found: {shipment_id}"
        )
    
    shipment = shipments_db[resolved_id]
    
    if shipment.phone_calls:
        # Remove phone calls from phone_calls_db
        for phone_call in shipment.phone_calls:
            if phone_call.id in phone_calls_db:
                del phone_calls_db[phone_call.id]
        
        # Clear phone calls from shipment
        shipment.phone_calls = []
        shipment.updated_at = datetime.utcnow()
        
        logger.info(f"Deleted all phone calls for shipment {resolved_id}")
    
    return JSONResponse(status_code=status.HTTP_204_NO_CONTENT, content=None)

@app.get("/shipments/{shipment_id}/phone-calls", response_model=List[PhoneCall])
async def get_phone_calls(
    shipment_id: str,
    api_key: str = Depends(verify_api_key)
):
    """
    Get all phone calls for a shipment
    """
    resolved_id = resolve_shipment_id(shipment_id)
    
    if resolved_id not in shipments_db:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Shipment not found: {shipment_id}"
        )
    
    shipment = shipments_db[resolved_id]
    return shipment.phone_calls or []

@app.get("/phone-calls", response_model=List[PhoneCall])
async def get_all_phone_calls(
    call_type: Optional[str] = None,
    agreed: Optional[bool] = None,
    sentiment: Optional[str] = None,
    api_key: str = Depends(verify_api_key)
):
    """
    Get all phone calls across all shipments with optional filtering
    """
    all_phone_calls = []
    
    # Collect all phone calls from all shipments
    for shipment in shipments_db.values():
        if shipment.phone_calls:
            for call in shipment.phone_calls:
                # Add shipment info to the call for context
                call_with_shipment = call.model_copy()
                call_with_shipment.shipment_load_id = shipment.load_id
                call_with_shipment.shipment_origin = shipment.origin
                call_with_shipment.shipment_destination = shipment.destination
                all_phone_calls.append(call_with_shipment)
    
    # Apply filters
    if call_type:
        all_phone_calls = [call for call in all_phone_calls if call.call_type == call_type]
    
    if agreed is not None:
        all_phone_calls = [call for call in all_phone_calls if call.agreed == agreed]
    
    if sentiment:
        all_phone_calls = [call for call in all_phone_calls if call.sentiment == sentiment]
    
    # Sort by creation date (newest first)
    all_phone_calls.sort(key=lambda x: x.created_at, reverse=True)
    
    return all_phone_calls

if __name__ == "__main__":
    import uvicorn
    port = get_port()
    uvicorn.run(app, host="0.0.0.0", port=port)
