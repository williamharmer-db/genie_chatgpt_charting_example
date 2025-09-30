#!/usr/bin/env python3
"""
Script to check available Azure OpenAI deployments
"""
import os
from openai import AzureOpenAI
from dotenv import load_dotenv

load_dotenv()

def check_deployments():
    """Check what deployments are available in your Azure OpenAI resource"""
    
    print("🔍 Checking Azure OpenAI Deployments")
    print("=" * 50)
    
    endpoint = os.getenv('AZURE_OPENAI_ENDPOINT')
    api_key = os.getenv('AZURE_OPENAI_API_KEY')
    api_version = os.getenv('AZURE_OPENAI_API_VERSION', '2024-02-01')
    
    if not endpoint or not api_key:
        print("❌ Missing Azure OpenAI configuration")
        return
    
    print(f"🌐 Endpoint: {endpoint}")
    print(f"📅 API Version: {api_version}")
    print()
    
    try:
        client = AzureOpenAI(
            azure_endpoint=endpoint,
            api_key=api_key,
            api_version=api_version
        )
        
        # Try a few common deployment names
        common_names = [
            'gpt-35-turbo',
            'gpt-4',
            'gpt-35-turbo-16k',
            'gpt-4-32k',
            'aweaver-azure-oai',
            'gpt35turbo',
            'gpt4'
        ]
        
        print("🧪 Testing common deployment names...")
        print("-" * 40)
        
        working_deployments = []
        
        for deployment_name in common_names:
            try:
                print(f"Testing: {deployment_name}...", end=" ")
                
                response = client.chat.completions.create(
                    model=deployment_name,
                    messages=[{"role": "user", "content": "Hello"}],
                    max_completion_tokens=5
                )
                
                print("✅ WORKS!")
                working_deployments.append(deployment_name)
                
            except Exception as e:
                error_msg = str(e)
                if 'DeploymentNotFound' in error_msg:
                    print("❌ Not found")
                elif 'quota' in error_msg.lower():
                    print("⚠️  Found but quota exceeded")
                    working_deployments.append(deployment_name)
                else:
                    print(f"❌ Error: {error_msg[:50]}...")
        
        print()
        print("📊 Summary:")
        print("-" * 20)
        
        if working_deployments:
            print("✅ Working deployments found:")
            for deployment in working_deployments:
                print(f"   - {deployment}")
            
            print()
            print("💡 To use one of these, update your .env file:")
            print(f"AZURE_OPENAI_DEPLOYMENT={working_deployments[0]}")
            
        else:
            print("❌ No working deployments found.")
            print()
            print("💡 Tips:")
            print("1. Check your Azure OpenAI portal for actual deployment names")
            print("2. Make sure deployments are fully deployed (not 'Creating')")
            print("3. Try different API versions: 2023-12-01-preview, 2024-02-01")
            
    except Exception as e:
        print(f"❌ Connection failed: {e}")
        print()
        print("💡 Possible issues:")
        print("- Incorrect endpoint URL")
        print("- Invalid API key")
        print("- Wrong API version")


if __name__ == "__main__":
    check_deployments()
