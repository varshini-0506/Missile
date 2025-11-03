"""
Quick Start Script for Production

This script performs pre-flight checks and starts the pipeline
"""

import sys
import os

# Check Python version
if sys.version_info < (3, 8):
    print("[✗] Python 3.8+ required")
    sys.exit(1)

print("[✓] Python version check passed")

# Check for required modules
required_modules = ['supabase', 'selenium', 'requests']
missing_modules = []

for module in required_modules:
    try:
        __import__(module)
        print(f"[✓] {module} installed")
    except ImportError:
        missing_modules.append(module)
        print(f"[✗] {module} not installed")

if missing_modules:
    print(f"\n[!] Missing modules: {', '.join(missing_modules)}")
    print("[!] Install with: pip install -r requirements.txt")
    response = input("\nContinue anyway? (y/n): ")
    if response.lower() != 'y':
        sys.exit(1)

# Check environment variables
supabase_url = os.getenv("SUPABASE_URL")
supabase_key = os.getenv("SUPABASE_KEY")

if not supabase_url:
    print("[!] SUPABASE_URL not set in environment")
if not supabase_key:
    print("[!] SUPABASE_KEY not set in environment")

if not supabase_url or not supabase_key:
    print("[!] Note: Supabase keys may be hardcoded in files")
    print("[!] Continuing...\n")

# Import and start main
print("\n" + "="*80)
print("STARTING PRODUCTION PIPELINE")
print("="*80 + "\n")

try:
    from main import PipelineManager
    
    manager = PipelineManager()
    manager.start()
    
except KeyboardInterrupt:
    print("\n[!] Interrupted by user")
    sys.exit(0)
except Exception as e:
    print(f"\n[✗] Fatal error: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

