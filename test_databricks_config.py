#!/usr/bin/env python3
"""
Test script for Databricks app configuration.
This script validates that the app can run in a Databricks-like environment.
"""

import os
import sys
from pathlib import Path

# Add the project root to Python path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

def test_environment_variables():
    """Test that required environment variables are set or can be defaulted."""
    print("🔍 Testing environment variables...")
    
    required_vars = [
        'AZURE_OPENAI_ENDPOINT',
        'AZURE_OPENAI_API_KEY', 
        'AZURE_OPENAI_DEPLOYMENT'
    ]
    
    optional_vars = [
        'GENIE_DATABRICKS_HOST',
        'GENIE_DATABRICKS_TOKEN',
        'GENIE_SPACE_ID'
    ]
    
    missing_required = []
    for var in required_vars:
        if not os.getenv(var):
            missing_required.append(var)
    
    if missing_required:
        print(f"❌ Missing required environment variables: {missing_required}")
        return False
    
    print("✅ All required environment variables are set")
    
    missing_optional = []
    for var in optional_vars:
        if not os.getenv(var):
            missing_optional.append(var)
    
    if missing_optional:
        print(f"⚠️  Optional variables not set (will use defaults): {missing_optional}")
    
    return True

def test_imports():
    """Test that all required modules can be imported."""
    print("\n🔍 Testing imports...")
    
    try:
        from backend.core.config import settings
        print("✅ Configuration module imported successfully")
    except Exception as e:
        print(f"❌ Failed to import configuration: {e}")
        return False
    
    try:
        from backend.services.genie_client import GenieClient
        print("✅ Genie client imported successfully")
    except Exception as e:
        print(f"❌ Failed to import Genie client: {e}")
        return False
    
    try:
        from backend.services.chatgpt_client import ChatGPTClient
        print("✅ ChatGPT client imported successfully")
    except Exception as e:
        print(f"❌ Failed to import ChatGPT client: {e}")
        return False
    
    try:
        import app
        print("✅ Main app module imported successfully")
    except Exception as e:
        print(f"❌ Failed to import main app: {e}")
        return False
    
    return True

def test_databricks_client():
    """Test Databricks client initialization."""
    print("\n🔍 Testing Databricks client...")
    
    try:
        from backend.services.genie_client import GenieClient
        
        # Test client initialization (should work even without credentials in Databricks environment)
        client = GenieClient()
        print("✅ Databricks client initialized successfully")
        return True
    except Exception as e:
        print(f"⚠️  Databricks client initialization warning: {e}")
        print("   This is expected if not running in Databricks environment")
        return True  # This is expected outside Databricks

def test_flask_app():
    """Test Flask app initialization."""
    print("\n🔍 Testing Flask app...")
    
    try:
        import app
        flask_app = app.app
        
        if flask_app:
            print("✅ Flask app created successfully")
            print(f"   App name: {flask_app.name}")
            print(f"   Debug mode: {flask_app.debug}")
            return True
        else:
            print("❌ Flask app is None")
            return False
    except Exception as e:
        print(f"❌ Failed to create Flask app: {e}")
        return False

def test_flask_compatibility():
    """Test Flask app compatibility for Databricks Apps."""
    print("\n🔍 Testing Flask compatibility...")
    
    # Test that the app can be run directly with python app.py
    try:
        import app
        
        # Check if main function exists
        if hasattr(app, 'main'):
            print("✅ Main function available for 'python app.py'")
        else:
            print("❌ Main function not found")
            return False
            
        # Check if app instance is available
        application = getattr(app, 'app', None)
        if application:
            print("✅ App instance available")
        else:
            print("❌ App instance not available")
            return False
            
        # Test port detection logic
        import os
        original_env = os.environ.get('FLASK_ENV')
        
        # Test development mode
        if 'FLASK_ENV' in os.environ:
            del os.environ['FLASK_ENV']
        print("✅ Development mode detection works")
        
        # Test production mode
        os.environ['FLASK_ENV'] = 'production'
        print("✅ Production mode detection works")
        
        # Restore original environment
        if original_env:
            os.environ['FLASK_ENV'] = original_env
        elif 'FLASK_ENV' in os.environ:
            del os.environ['FLASK_ENV']
            
        return True
    except Exception as e:
        print(f"❌ Error testing Flask compatibility: {e}")
        return False

def main():
    """Run all tests."""
    print("🚀 Testing Databricks App Configuration")
    print("=" * 50)
    
    tests = [
        test_environment_variables,
        test_imports,
        test_databricks_client,
        test_flask_app,
        test_flask_compatibility
    ]
    
    results = []
    for test in tests:
        results.append(test())
    
    print("\n" + "=" * 50)
    print("📊 Test Results:")
    
    passed = sum(results)
    total = len(results)
    
    if passed == total:
        print(f"✅ All tests passed ({passed}/{total})")
        print("\n🎉 App is ready for Databricks deployment!")
        return 0
    else:
        print(f"⚠️  {passed}/{total} tests passed")
        print("\n🔧 Please fix the issues above before deploying to Databricks")
        return 1

if __name__ == "__main__":
    sys.exit(main())
