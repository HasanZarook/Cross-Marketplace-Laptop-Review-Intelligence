"""
Laptop Specifications JSON Schema Validator
Validates and normalizes laptop specification data
"""

import json
from typing import Dict, List, Any
from jsonschema import validate, ValidationError, Draft7Validator
from pathlib import Path

# JSON Schema for Laptop Specifications
LAPTOP_SPEC_SCHEMA = {
    "$schema": "http://json-schema.org/draft-07/schema#",
    "title": "Laptop Specifications",
    "description": "Schema for laptop technical specifications extracted from PDFs",
    "type": "array",
    "items": {
        "type": "object",
        "required": ["source_pdf", "brand", "model", "processor", "memory", "storage", "display"],
        "properties": {
            "source_pdf": {
                "type": "string",
                "description": "Source PDF filename"
            },
            "brand": {
                "type": "string",
                "enum": ["HP", "Lenovo", "Dell", "Asus", "Acer", "Unknown"],
                "description": "Laptop manufacturer brand"
            },
            "model": {
                "type": "string",
                "description": "Laptop model name and series"
            },
            "processor": {
                "type": "array",
                "items": {"type": "string"},
                "minItems": 1,
                "description": "Available processor options"
            },
            "memory": {
                "type": "array",
                "items": {"type": "string"},
                "minItems": 1,
                "description": "RAM configurations available"
            },
            "storage": {
                "type": "array",
                "items": {"type": "string"},
                "minItems": 1,
                "description": "Storage options (SSD/HDD)"
            },
            "display": {
                "type": "array",
                "items": {
                    "type": "object",
                    "required": ["size", "resolution"],
                    "properties": {
                        "size": {"type": "string"},
                        "resolution": {"type": "string"},
                        "brightness": {"type": "string"},
                        "touch": {"type": "boolean"},
                        "anti_glare": {"type": "boolean"},
                        "panel_type": {"type": "string"},
                        "refresh_rate": {"type": "string"}
                    }
                },
                "minItems": 1,
                "description": "Display configurations"
            },
            "graphics": {
                "type": "array",
                "items": {"type": "string"},
                "description": "Graphics card options"
            },
            "battery": {
                "type": "array",
                "items": {"type": "string"},
                "description": "Battery specifications"
            },
            "weights": {
                "type": "object",
                "description": "Weight variants based on configuration",
                "patternProperties": {
                    "^variant_\\d+$": {
                        "type": "object",
                        "properties": {
                            "sku_id": {"type": "string"},
                            "top_material": {"type": "string"},
                            "bottom_material": {"type": "string"},
                            "weight": {"type": "string"},
                            "weight_lbs": {"type": "string"}
                        }
                    }
                }
            },
            "dimensions": {
                "type": "string",
                "description": "Physical dimensions (L x W x H)"
            },
            "ports": {
                "type": "array",
                "items": {"type": "string"},
                "description": "Available ports and connectors"
            },
            "wireless": {
                "type": "object",
                "properties": {
                    "wifi_6": {"type": "boolean"},
                    "wifi_6e": {"type": "boolean"},
                    "wifi_5": {"type": "boolean"},
                    "bluetooth": {"type": "boolean"},
                    "bluetooth_version": {"type": "string"}
                }
            },
            "operating_system": {
                "type": "array",
                "items": {"type": "string"},
                "description": "Available OS options"
            },
            "security": {
                "type": "array",
                "items": {"type": "string"},
                "description": "Security features"
            },
            "multi_media": {
                "type": "object",
                "properties": {
                    "camera": {
                        "type": "array",
                        "items": {"type": "string"}
                    },
                    "camera_privacy": {"type": "boolean"},
                    "audio": {
                        "type": "array",
                        "items": {"type": "string"}
                    }
                }
            },
            "monitor": {
                "type": "object",
                "properties": {
                    "max_displays": {"type": "string"},
                    "supported_resolutions": {
                        "type": "array",
                        "items": {"type": "string"}
                    },
                    "hdmi_support": {"type": "string"},
                    "usbc_support": {"type": "string"},
                    "thunderbolt_support": {"type": "string"}
                }
            },
            "chipset": {
                "type": "string",
                "description": "Chipset information"
            },
            "colour": {
                "type": "array",
                "items": {"type": "string"},
                "description": "Available color options"
            },
            "case_material": {
                "type": "string",
                "description": "Chassis material"
            },
            "network": {
                "type": "object",
                "properties": {
                    "ethernet": {"type": "string"},
                    "wwan": {
                        "type": "array",
                        "items": {"type": "string"}
                    },
                    "nfc": {"type": "boolean"}
                }
            },
            "warranty": {
                "type": "array",
                "items": {
                    "type": "object",
                    "properties": {
                        "duration": {"type": "string"},
                        "type": {"type": "string"}
                    }
                }
            },
            "certification": {
                "type": "array",
                "items": {"type": "string"},
                "description": "Environmental and compliance certifications"
            },
            "input_device": {
                "type": "object",
                "properties": {
                    "keyboard": {
                        "type": "array",
                        "items": {"type": "string"}
                    },
                    "touchpad": {"type": "string"},
                    "pointing_device": {"type": "string"}
                }
            },
            "power": {
                "type": "object",
                "properties": {
                    "adapter_wattage": {
                        "type": "array",
                        "items": {"type": "string"}
                    },
                    "power_delivery": {"type": "string"},
                    "rapid_charge": {"type": "string"}
                }
            }
        }
    }
}


def validate_laptop_specs(data: List[Dict], schema: Dict) -> tuple[bool, List[str]]:
    """
    Validate laptop specifications against schema
    Returns: (is_valid, list_of_errors)
    """
    errors = []
    validator = Draft7Validator(schema)
    
    try:
        validate(instance=data, schema=schema)
        print("✓ Data is valid against schema!")
        return True, []
    except ValidationError as e:
        errors.append(f"Validation Error: {e.message}")
        
        # Get all validation errors
        for error in validator.iter_errors(data):
            error_path = " -> ".join(str(p) for p in error.path)
            errors.append(f"  Path: {error_path}")
            errors.append(f"  Error: {error.message}\n")
        
        return False, errors


def normalize_data(data: List[Dict]) -> List[Dict]:
    """
    Normalize and clean the data
    """
    normalized = []
    
    for laptop in data:
        # Ensure all boolean values are proper booleans
        if 'display' in laptop:
            for display in laptop['display']:
                if 'touch' in display and isinstance(display['touch'], str):
                    display['touch'] = display['touch'].lower() in ['yes', 'true', 'multi touch']
                if 'anti_glare' in display and isinstance(display['anti_glare'], str):
                    display['anti_glare'] = display['anti_glare'].lower() in ['yes', 'true']
        
        # Normalize weights structure
        if 'weight' in laptop and not 'weights' in laptop:
            laptop['weights'] = {
                'variant_1': {
                    'sku_id': f"{laptop['brand']}-Standard",
                    'top_material': 'Not specified',
                    'bottom_material': 'Not specified',
                    'weight': laptop.pop('weight'),
                    'weight_lbs': 'Not specified'
                }
            }
        
        # Ensure arrays for certain fields
        array_fields = ['battery', 'colour']
        for field in array_fields:
            if field in laptop and isinstance(laptop[field], str):
                laptop[field] = [laptop[field]]
        
        # Ensure network structure
        if 'network' in laptop:
            if 'wwan' in laptop['network'] and isinstance(laptop['network']['wwan'], str):
                if laptop['network']['wwan'].lower() in ['no support', 'not specified']:
                    laptop['network']['wwan'] = []
                else:
                    laptop['network']['wwan'] = [laptop['network']['wwan']]
        
        normalized.append(laptop)
    
    return normalized


def generate_summary_report(data: List[Dict]) -> str:
    """
    Generate a summary report of the data
    """
    report = []
    report.append("=" * 80)
    report.append("LAPTOP SPECIFICATIONS SUMMARY REPORT")
    report.append("=" * 80)
    report.append(f"\nTotal Laptops: {len(data)}\n")
    
    for idx, laptop in enumerate(data, 1):
        report.append(f"\n{idx}. {laptop['brand']} - {laptop['model']}")
        report.append(f"   Source: {laptop['source_pdf']}")
        report.append(f"   Processors: {len(laptop['processor'])} options")
        report.append(f"   Memory: {', '.join(laptop['memory'])}")
        report.append(f"   Storage: {len(laptop['storage'])} options")
        report.append(f"   Display Variants: {len(laptop['display'])}")
        report.append(f"   Graphics: {', '.join(laptop['graphics'][:2])}")
        report.append(f"   Weight: {laptop['weights']['variant_1']['weight']}")
        report.append(f"   OS Options: {len(laptop['operating_system'])}")
        report.append(f"   Certifications: {len(laptop['certification'])}")
    
    report.append("\n" + "=" * 80)
    report.append("FIELD COMPLETENESS ANALYSIS")
    report.append("=" * 80 + "\n")
    
    # Analyze field completeness
    fields_to_check = ['chipset', 'case_material', 'warranty', 'certification', 
                       'power', 'network', 'security']
    
    for field in fields_to_check:
        specified_count = sum(1 for laptop in data 
                             if field in laptop and 
                             str(laptop[field]) != 'Not specified' and
                             laptop[field] not in ['', [], {}])
        report.append(f"{field.replace('_', ' ').title()}: {specified_count}/{len(data)} laptops")
    
    return "\n".join(report)


def export_schema_to_file(schema: Dict, output_path: str):
    """Export schema to a JSON file"""
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(schema, f, indent=2)
    print(f"✓ Schema exported to: {output_path}")


def main():
    # Load your JSON data
    input_file = 'laptop_specs_complete.json'
    
    print("Loading data...")
    with open(input_file, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    print(f"✓ Loaded {len(data)} laptop specifications\n")
    
    # Normalize data
    print("Normalizing data...")
    normalized_data = normalize_data(data)
    print("✓ Data normalized\n")
    
    # Validate against schema
    print("Validating against schema...")
    is_valid, errors = validate_laptop_specs(normalized_data, LAPTOP_SPEC_SCHEMA)
    
    if not is_valid:
        print("✗ Validation failed with errors:")
        for error in errors:
            print(error)
    else:
        print("✓ All data is valid!\n")
    
    # Save normalized data
    output_file = 'laptop_specs_normalized.json'
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(normalized_data, f, indent=2, ensure_ascii=False)
    print(f"✓ Normalized data saved to: {output_file}\n")
    
    # Export schema
    schema_file = 'laptop_specs_schema.json'
    export_schema_to_file(LAPTOP_SPEC_SCHEMA, schema_file)
    print()
    
    # Generate summary report
    print("Generating summary report...")
    report = generate_summary_report(normalized_data)
    print("\n" + report)
    
    # Save report
    report_file = 'laptop_specs_report.txt'
    with open(report_file, 'w', encoding='utf-8') as f:
        f.write(report)
    print(f"\n✓ Report saved to: {report_file}")


if __name__ == "__main__":
    main()