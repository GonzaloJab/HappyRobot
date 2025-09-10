"""
FastAPI Shipments Application
"""
import os
import logging
from datetime import datetime
from typing import Dict, List, Optional
from fastapi import FastAPI, HTTPException, status
from fastapi.responses import JSONResponse

from .models import Shipment, ShipmentCreate, ShipmentUpdate, ShipmentFilters, StatusType
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
                    if status_val in ["pending", "completed"]:
                        shipment_data["status"] = status_val
                
                # Check for duplicate load_id
                load_id = shipment_data["load_id"]
                if any(s.load_id == load_id for s in shipments_db.values()):
                    duplicate_count += 1
                    shipment_data["load_id"] = f"{load_id}-DUP{duplicate_count}"
                    logger.warning(f"Duplicate load_id found, renamed to: {shipment_data['load_id']}")
                
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
async def debug_info():
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
    sort_by: str = "created_at",
    sort_order: str = "desc"
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

@app.get("/shipments/{shipment_id}", response_model=Shipment)
async def get_shipment(shipment_id: str):
    """
    Get a specific shipment by ID
    """
    if shipment_id not in shipments_db:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Shipment not found"
        )
    return shipments_db[shipment_id]

@app.post("/shipments", response_model=Shipment, status_code=status.HTTP_201_CREATED)
async def create_shipment(shipment_data: ShipmentCreate):
    """
    Create a new shipment/load
    """
    # Check for duplicate load_id
    if any(s.load_id == shipment_data.load_id for s in shipments_db.values()):
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=f"Load ID '{shipment_data.load_id}' already exists"
        )
    
    shipment = Shipment(**shipment_data.model_dump())
    shipments_db[shipment.id] = shipment
    logger.info(f"Created shipment: {shipment.id} with load_id: {shipment.load_id}")
    return shipment

@app.patch("/shipments/{shipment_id}", response_model=Shipment)
async def update_shipment(shipment_id: str, update_data: ShipmentUpdate):
    """
    Update an existing shipment
    """
    if shipment_id not in shipments_db:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Shipment with id {shipment_id} not found"
        )
    
    shipment = shipments_db[shipment_id]
    
    # Update fields
    update_dict = update_data.model_dump(exclude_unset=True)
    for field, value in update_dict.items():
        setattr(shipment, field, value)
    
    # Update timestamp
    shipment.updated_at = datetime.utcnow()
    
    shipments_db[shipment_id] = shipment
    logger.info(f"Updated shipment: {shipment_id}")
    return shipment

@app.delete("/shipments/{shipment_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_shipment(shipment_id: str):
    """
    Delete a shipment
    """
    if shipment_id not in shipments_db:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Shipment with id {shipment_id} not found"
        )
    
    del shipments_db[shipment_id]
    logger.info(f"Deleted shipment: {shipment_id}")
    return JSONResponse(status_code=status.HTTP_204_NO_CONTENT, content=None)

if __name__ == "__main__":
    import uvicorn
    port = get_port()
    uvicorn.run(app, host="0.0.0.0", port=port)
