#!/usr/bin/env python3
"""
Quick server start script for hackathon demo
"""
import os
import sys

def start_server():
    """Start the FoodLens AI server"""
    print("🚀 Starting FoodLens AI Server for Hackathon Demo")
    print("=" * 60)
    
    # Set environment
    os.environ['PYTHONPATH'] = '.'
    
    # Start server
    print("📡 Server starting on http://localhost:8000")
    print("🎯 Ready for demo with all fixes applied!")
    print("\n✅ Key Features Ready:")
    print("   - Health Analysis with proper scoring")
    print("   - User tiers (Premium vs Free)")
    print("   - AI-powered alternatives (Premium only)")
    print("   - Smart chatbot with Gemini AI (Premium only)")
    print("   - Indian market focus")
    print("\n🏆 Press Ctrl+C to stop server")
    print("-" * 60)
    
    # Import and run
    try:
        import uvicorn
        from api.main import app
        uvicorn.run(app, host="0.0.0.0", port=8000)
    except Exception as e:
        print(f"❌ Server error: {e}")
        print("💡 Make sure environment is activated and dependencies installed")

if __name__ == "__main__":
    start_server()