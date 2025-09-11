#!/usr/bin/env python3
"""
Backfill script for assigned_via_url field

This script demonstrates how to backfill the assigned_via_url field for existing data.
Since the current implementation uses in-memory storage, this is primarily for demonstration
and would need to be adapted for a real database implementation.

Usage:
    python backfill_assigned_via_url.py [--dry-run]
"""

import argparse
import logging
from typing import Dict, List
from datetime import datetime

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def backfill_assigned_via_url(shipments_db: Dict, dry_run: bool = False) -> Dict[str, int]:
    """
    Backfill assigned_via_url field for existing shipments
    
    Args:
        shipments_db: Dictionary containing shipment data
        dry_run: If True, only log what would be changed without making changes
        
    Returns:
        Dictionary with counts of affected rows
    """
    stats = {
        'total_shipments': len(shipments_db),
        'already_set': 0,
        'set_to_false': 0,
        'set_to_true': 0,
        'errors': 0
    }
    
    logger.info(f"Starting backfill for {stats['total_shipments']} shipments")
    
    for shipment_id, shipment in shipments_db.items():
        try:
            # Check if assigned_via_url is already set
            if hasattr(shipment, 'assigned_via_url') and shipment.assigned_via_url is not None:
                stats['already_set'] += 1
                logger.debug(f"Shipment {shipment_id} already has assigned_via_url set")
                continue
            
            # Determine assignment source based on available data
            # In a real implementation, this would use audit logs, request paths, etc.
            assigned_via_url = determine_assignment_source(shipment)
            
            if not dry_run:
                # Update the shipment
                shipment.assigned_via_url = assigned_via_url
                shipment.updated_at = datetime.utcnow()
            
            if assigned_via_url:
                stats['set_to_true'] += 1
                logger.info(f"Set shipment {shipment_id} assigned_via_url=True (API/URL assignment)")
            else:
                stats['set_to_false'] += 1
                logger.info(f"Set shipment {shipment_id} assigned_via_url=False (Manual assignment)")
                
        except Exception as e:
            stats['errors'] += 1
            logger.error(f"Error processing shipment {shipment_id}: {e}")
    
    return stats

def determine_assignment_source(shipment) -> bool:
    """
    Determine if a shipment was assigned via URL/API or manually
    
    This is a simplified heuristic. In a real implementation, you would:
    1. Check audit logs for the assignment event
    2. Look at request paths (API vs web UI)
    3. Check user agent strings
    4. Examine service account usage
    5. Review webhook signatures
    
    Args:
        shipment: Shipment object
        
    Returns:
        True if assigned via URL/API, False if assigned manually
    """
    # Heuristic: If the shipment has specific patterns that suggest API usage
    # This is just for demonstration - real logic would be more sophisticated
    
    # Check if load_id follows API pattern (e.g., contains "API" or specific prefixes)
    if hasattr(shipment, 'load_id') and shipment.load_id:
        if 'API' in shipment.load_id.upper() or shipment.load_id.startswith('API-'):
            return True
    
    # Check if created recently (newer shipments more likely to be API)
    if hasattr(shipment, 'created_at') and shipment.created_at:
        # If created in the last 30 days, assume API (this is just for demo)
        days_old = (datetime.utcnow() - shipment.created_at).days
        if days_old < 30:
            return True
    
    # Check if has specific carrier descriptions that suggest automation
    if hasattr(shipment, 'carrier_description') and shipment.carrier_description:
        automated_indicators = ['BOT', 'AUTO', 'SYSTEM', 'API']
        if any(indicator in shipment.carrier_description.upper() for indicator in automated_indicators):
            return True
    
    # Default to manual assignment for historical data
    return False

def main():
    parser = argparse.ArgumentParser(description='Backfill assigned_via_url field')
    parser.add_argument('--dry-run', action='store_true', 
                       help='Show what would be changed without making changes')
    args = parser.parse_args()
    
    # In a real implementation, you would load from your database
    # For this demo, we'll simulate loading existing data
    logger.info("Loading existing shipments...")
    
    # Simulate shipments database (in real implementation, load from database)
    shipments_db = {}
    
    # Add some sample data for demonstration
    from app.models import Shipment
    from datetime import datetime, timedelta
    
    sample_shipments = [
        {
            "load_id": "LD-2025-0001",
            "origin": "Madrid",
            "destination": "Paris",
            "pickup_datetime": datetime.utcnow() + timedelta(days=1),
            "delivery_datetime": datetime.utcnow() + timedelta(days=2),
            "status": "pending",
            "carrier_description": "Manual Transport Co."
        },
        {
            "load_id": "API-LD-2025-0002",
            "origin": "Barcelona",
            "destination": "Lyon",
            "pickup_datetime": datetime.utcnow() + timedelta(days=1),
            "delivery_datetime": datetime.utcnow() + timedelta(days=2),
            "status": "agreed",
            "carrier_description": "AUTO-BOT Transport"
        },
        {
            "load_id": "LD-2025-0003",
            "origin": "Seville",
            "destination": "Marseille",
            "pickup_datetime": datetime.utcnow() + timedelta(days=1),
            "delivery_datetime": datetime.utcnow() + timedelta(days=2),
            "status": "agreed",
            "carrier_description": "Traditional Carrier"
        }
    ]
    
    for shipment_data in sample_shipments:
        shipment = Shipment(**shipment_data)
        shipments_db[shipment.id] = shipment
    
    logger.info(f"Loaded {len(shipments_db)} shipments for backfill")
    
    # Run backfill
    stats = backfill_assigned_via_url(shipments_db, dry_run=args.dry_run)
    
    # Report results
    logger.info("Backfill completed!")
    logger.info(f"Total shipments: {stats['total_shipments']}")
    logger.info(f"Already set: {stats['already_set']}")
    logger.info(f"Set to False (Manual): {stats['set_to_false']}")
    logger.info(f"Set to True (API/URL): {stats['set_to_true']}")
    logger.info(f"Errors: {stats['errors']}")
    
    if args.dry_run:
        logger.info("DRY RUN - No changes were made")
    else:
        logger.info("Changes have been applied")

if __name__ == "__main__":
    main()
