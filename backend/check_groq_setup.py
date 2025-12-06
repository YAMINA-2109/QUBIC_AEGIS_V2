"""
Script to verify Groq API key configuration
"""
import os
from pathlib import Path
from dotenv import load_dotenv

print("=" * 60)
print("GROQ API KEY VERIFICATION")
print("=" * 60)

# Check all possible .env locations
env_locations = [
    Path(__file__).parent / '.env',  # backend/.env
    Path(__file__).parent.parent / '.env',  # root/.env
    Path.cwd() / '.env',
    Path.cwd().parent / '.env',
]

found_env = None
for env_loc in env_locations:
    if env_loc.exists():
        print(f"✅ Found .env at: {env_loc}")
        load_dotenv(dotenv_path=env_loc, override=True)
        found_env = env_loc
        break

if not found_env:
    print("⚠️  No .env file found in common locations")
    print("   Searched locations:")
    for loc in env_locations:
        print(f"   - {loc}")
    load_dotenv(override=True)

# Check for GROQ_API_KEY
api_key = os.getenv("GROQ_API_KEY")
if api_key:
    masked_key = api_key[:10] + "..." + api_key[-4:] if len(api_key) > 14 else "***"
    print(f"\n✅ GROQ_API_KEY found: {masked_key}")
    print(f"   Length: {len(api_key)} characters")
    
    # Test Groq import
    try:
        from groq import Groq
        print("✅ groq package is installed")
        
        # Test connection
        try:
            client = Groq(api_key=api_key)
            test_response = client.chat.completions.create(
                model="llama-3.3-70b-versatile",
                messages=[{"role": "user", "content": "test"}],
                max_tokens=5
            )
            print("✅ Groq API connection successful!")
            print(f"   Model test: {test_response.model}")
        except Exception as e:
            print(f"❌ Groq API connection failed: {e}")
            print("\n   Possible issues:")
            print("   - Invalid API key")
            print("   - Network connection problem")
            print("   - Groq service temporarily unavailable")
    except ImportError:
        print("❌ groq package not installed")
        print("   Install with: pip install groq")
else:
    print("\n❌ GROQ_API_KEY not found in environment")
    print("\n   To fix:")
    print("   1. Create a .env file in backend/ directory")
    print("   2. Add: GROQ_API_KEY=your_api_key_here")
    print("   3. Get API key from: https://console.groq.com/keys")

print("\n" + "=" * 60)

