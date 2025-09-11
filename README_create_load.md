# Load Creation Script

This Python script (`create_load.py`) allows you to create new loads/shipments to your HappyRobot backend API running on port 8000.

## Features

- ✅ Health check to verify backend connectivity
- ✅ Create loads with required and optional fields
- ✅ Interactive mode for guided input
- ✅ Command line interface
- ✅ Sample load creation
- ✅ List existing loads
- ✅ **Update load status to agreed**
- ✅ **Update any load field (origin, destination, equipment, etc.)**
- ✅ Proper error handling and validation

## Usage

### 1. Basic Usage - Create a Sample Load

```bash
python create_load.py --sample
```

This creates a sample load with all fields populated.

### 2. Interactive Mode (Recommended for beginners)

```bash
python create_load.py --interactive
```

This guides you through entering all the load details step by step.

### 3. Command Line Mode

```bash
python create_load.py \
  --load-id "LD-2025-0001" \
  --origin "Los Angeles, CA" \
  --destination "New York, NY" \
  --pickup "2025-01-15T08:00:00Z" \
  --delivery "2025-01-16T18:00:00Z" \
  --equipment "Dry Van" \
  --rate 2500.50 \
  --weight 1500.0 \
  --miles 2800.0 \
  --notes "Fragile cargo"
```

### 4. List Existing Loads

```bash
python create_load.py --list
```

### 5. Assign a Load (Update Status to agreed)

```bash
# Simple assign (status only)
python create_load.py --assign "LD-2025-0001"

# Assign with agreed price and carrier
python create_load.py --assign "LD-2025-0001" --agreed-price 2500.00 --carrier "ABC Transport Co."
```

### 6. Update Load Fields

```bash
# Update status only
python create_load.py --update-load-id "LD-2025-0001" --update-status "agreed"

# Update multiple fields
python create_load.py --update-load-id "LD-2025-0001" \
  --update-origin "Updated Origin" \
  --update-destination "Updated Destination" \
  --update-equipment "Reefer" \
  --update-rate 3000.00 \
  --update-agreed-price 2800.00 \
  --update-carrier "XYZ Logistics" \
  --update-notes "Updated notes"
```

### 7. Health Check

The script automatically performs a health check before any operations.

## Required Fields

- `load_id`: Human-readable load ID (e.g., "LD-2025-0001")
- `origin`: Origin location
- `destination`: Destination location
- `pickup_datetime`: Pickup date and time (ISO format)
- `delivery_datetime`: Delivery date and time (ISO format)

## Optional Fields

- `equipment_type`: Equipment type (e.g., "Dry Van", "Reefer", "Flatbed")
- `loadboard_rate`: Listed rate for the load
- `notes`: Additional notes
- `weight`: Weight in pounds
- `commodity_type`: Type of commodity
- `num_of_pieces`: Number of pieces
- `miles`: Distance in miles
- `dimensions`: Dimensions (e.g., "48x40x60 in")
- `agreed_price`: Agreed price for the load (required when status is agreed)
- `carrier_description`: Carrier description/name (required when status is agreed)

## Examples

### Example 1: Minimal Load
```bash
python create_load.py \
  --load-id "LD-MIN-001" \
  --origin "Chicago, IL" \
  --destination "Detroit, MI" \
  --pickup "2025-01-20T09:00:00Z" \
  --delivery "2025-01-20T17:00:00Z"
```

### Example 2: Complete Load
```bash
python create_load.py \
  --load-id "LD-COMPLETE-001" \
  --origin "Miami, FL" \
  --destination "Seattle, WA" \
  --pickup "2025-01-25T06:00:00Z" \
  --delivery "2025-01-28T20:00:00Z" \
  --equipment "Reefer" \
  --rate 4500.00 \
  --weight 2500.0 \
  --commodity_type "Food Products" \
  --num_of_pieces 200 \
  --miles 3200.0 \
  --dimensions "53x102x108 in" \
  --notes "Temperature controlled - maintain 35°F"
```

### Example 3: Using Different Backend URL
```bash
python create_load.py --url "http://192.168.1.100:8000" --sample
```

### Example 4: Assign a Load
```bash
# Simple assign
python create_load.py --assign "LD-2025-0001"

# Assign with agreed price and carrier
python create_load.py --assign "LD-2025-0001" --agreed-price 2500.00 --carrier "ABC Transport Co."
```

### Example 5: Update Load Status
```bash
python create_load.py --update-load-id "LD-2025-0001" --update-status "agreed"
```

### Example 6: Update Multiple Load Fields
```bash
python create_load.py --update-load-id "LD-2025-0001" \
  --update-origin "New York, NY" \
  --update-destination "Miami, FL" \
  --update-equipment "Reefer" \
  --update-rate 3500.00 \
  --update-agreed-price 3200.00 \
  --update-carrier "Miami Express" \
  --update-notes "Updated route and equipment"
```

## Error Handling

The script handles various error scenarios:

- ❌ Backend not running or unreachable
- ❌ Invalid datetime formats
- ❌ Missing required fields
- ❌ Duplicate load IDs
- ❌ Validation errors from the API

## API Endpoints Used

- `GET /health` - Health check
- `POST /shipments` - Create new load
- `GET /shipments` - List all loads
- `GET /shipments/{id}` - Get specific load
- `PATCH /shipments/{id}` - Update existing load

## Requirements

- Python 3.6+
- `requests` library

Install requirements:
```bash
pip install requests
```

## Backend Requirements

Make sure your backend is running on port 8000 with the following endpoints available:
- Health check endpoint at `/health`
- Shipments endpoint at `/shipments`

The script expects the backend to be running at `http://localhost:8000` by default.
