#!/usr/bin/env python3
"""
Test script to verify POC setup and configuration
"""
import os
import sys
from loguru import logger

def test_environment():
    """Test environment variables"""
    print("🔍 Testing Environment Configuration")
    print("-" * 40)
    
    required_vars = {
        "DATABRICKS_HOST": "Databricks workspace URL",
        "DATABRICKS_TOKEN": "Databricks personal access token",
        "AZURE_OPENAI_ENDPOINT": "Azure OpenAI endpoint",
        "AZURE_OPENAI_API_KEY": "Azure OpenAI API key",
        "AZURE_OPENAI_DEPLOYMENT": "Azure OpenAI deployment name"
    }
    
    missing_vars = []
    
    for var, description in required_vars.items():
        value = os.getenv(var)
        if value:
            # Mask sensitive values
            if "TOKEN" in var or "KEY" in var:
                masked_value = value[:8] + "..." + value[-4:] if len(value) > 12 else "***"
                print(f"✅ {var}: {masked_value}")
            else:
                print(f"✅ {var}: {value}")
        else:
            print(f"❌ {var}: Missing ({description})")
            missing_vars.append(var)
    
    if missing_vars:
        print(f"\n❌ Missing {len(missing_vars)} required environment variables")
        return False
    else:
        print(f"\n✅ All environment variables configured")
        return True


def test_imports():
    """Test Python imports"""
    print("\n🔍 Testing Python Dependencies")
    print("-" * 40)
    
    required_modules = [
        ("databricks.sdk", "Databricks SDK"),
        ("openai", "OpenAI Python client"),
        ("flask", "Flask web framework"),
        ("pydantic", "Pydantic data validation"),
        ("loguru", "Loguru logging"),
        ("dotenv", "Python dotenv")
    ]
    
    missing_modules = []
    
    for module, description in required_modules:
        try:
            __import__(module)
            print(f"✅ {module}: Available ({description})")
        except ImportError:
            print(f"❌ {module}: Missing ({description})")
            missing_modules.append(module)
    
    if missing_modules:
        print(f"\n❌ Missing {len(missing_modules)} required modules")
        print("Run: pip install -r requirements.txt")
        return False
    else:
        print(f"\n✅ All dependencies available")
        return True


def test_databricks_connection():
    """Test Databricks connection (basic connectivity)"""
    print("\n🔍 Testing Databricks Connection")
    print("-" * 40)
    
    try:
        from databricks.sdk import WorkspaceClient
        from config import settings
        
        client = WorkspaceClient(
            host=settings.databricks_host,
            token=settings.databricks_token
        )
        
        # Try to list Genie spaces (basic connectivity test)
        spaces = client.genie.list_spaces()
        space_count = len(spaces.spaces) if spaces.spaces else 0
        
        print(f"✅ Connected to Databricks workspace")
        print(f"✅ Found {space_count} Genie spaces")
        
        if space_count == 0:
            print("⚠️  No Genie spaces found - you may need to create one")
        
        return True
        
    except Exception as e:
        print(f"❌ Databricks connection failed: {e}")
        return False


def test_azure_openai_connection():
    """Test Azure OpenAI connection"""
    print("\n🔍 Testing Azure OpenAI Connection")
    print("-" * 40)
    
    try:
        from chatgpt_client import ChatGPTClient
        
        client = ChatGPTClient()
        
        # Test with a simple completion
        response = client.client.chat.completions.create(
            model=client.model,
            messages=[{"role": "user", "content": "Say 'Azure OpenAI connected successfully!'"}],
            max_completion_tokens=15
        )
        
        result = response.choices[0].message.content.strip()
        print(f"✅ Azure OpenAI connection successful")
        print(f"✅ Deployment: {client.model}")
        print(f"✅ Test response: {result}")
        
        return True
        
    except Exception as e:
        print(f"❌ Azure OpenAI connection failed: {e}")
        return False


def main():
    """Run all tests"""
    print("🚀 Genie to Chart POC - Setup Test")
    print("=" * 50)
    
    # Load environment
    try:
        from dotenv import load_dotenv
        load_dotenv()
    except ImportError:
        print("❌ python-dotenv not available - install dependencies first")
        sys.exit(1)
    
    tests = [
        ("Environment", test_environment),
        ("Dependencies", test_imports),
        ("Databricks", test_databricks_connection),
        ("Azure OpenAI", test_azure_openai_connection)
    ]
    
    results = {}
    
    for test_name, test_func in tests:
        try:
            results[test_name] = test_func()
        except Exception as e:
            print(f"❌ {test_name} test failed with exception: {e}")
            results[test_name] = False
    
    # Summary
    print("\n" + "=" * 50)
    print("📊 Test Summary")
    print("-" * 20)
    
    passed = sum(1 for result in results.values() if result)
    total = len(results)
    
    for test_name, result in results.items():
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{test_name:15} {status}")
    
    print(f"\nResults: {passed}/{total} tests passed")
    
    if passed == total:
        print("\n🎉 All tests passed! POC is ready to use.")
        print("\nNext steps:")
        print("1. Run: python main_demo.py  (command line demo)")
        print("2. Run: python web_app.py    (web interface)")
        print("3. Run: ./start_demo.sh      (guided setup)")
    else:
        print(f"\n❌ {total - passed} tests failed. Please fix the issues above.")
        sys.exit(1)


if __name__ == "__main__":
    main()

