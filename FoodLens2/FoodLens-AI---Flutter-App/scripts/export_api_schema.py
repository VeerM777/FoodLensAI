"""
Export OpenAPI schema for Flutter/frontend integration
Run this script to generate api_schema.json
"""
import json
import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from api.main import app

def export_openapi_schema():
    """Export OpenAPI schema to JSON file"""
    try:
        schema = app.openapi()
        
        # Write to file
        output_path = os.path.join(os.path.dirname(__file__), 'api_schema.json')
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(schema, f, indent=2, ensure_ascii=False)
        
        print(f"✅ OpenAPI schema exported to: {output_path}")
        print(f"\n📊 API Summary:")
        print(f"   - Title: {schema['info']['title']}")
        print(f"   - Version: {schema['info']['version']}")
        print(f"   - Endpoints: {len(schema['paths'])} paths")
        
        # List all endpoints
        print(f"\n📋 Available Endpoints:")
        for path, methods in schema['paths'].items():
            for method in methods.keys():
                if method != 'parameters':
                    print(f"   - {method.upper():6} {path}")
        
        return True
    except Exception as e:
        print(f"❌ Error exporting schema: {e}")
        return False

if __name__ == "__main__":
    export_openapi_schema()
