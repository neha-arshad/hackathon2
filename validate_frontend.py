"""
Quick validation script for the Frontend components
"""
import os

frontend_path = os.path.join(os.path.dirname(__file__), 'frontend')

try:
    # Check if essential frontend files exist
    essential_files = [
        'package.json',
        'app/page.tsx',
        'app/chat/page.tsx',
        'app/dashboard/page.tsx',
        'app/layout.tsx'
    ]

    print("[OK] Frontend validation started")

    all_files_exist = True
    for file in essential_files:
        file_path = os.path.join(frontend_path, file)
        if os.path.exists(file_path):
            print(f"[OK] Found: {file}")
        else:
            print(f"[MISSING] {file}")
            all_files_exist = False

    if all_files_exist:
        print("[OK] All essential frontend files are present")
    else:
        print("[WARNING] Some essential frontend files are missing")

    # Check if chat page exists
    chat_page_path = os.path.join(frontend_path, 'app', 'chat', 'page.tsx')
    if os.path.exists(chat_page_path):
        print("[OK] AI Chat interface exists")
    else:
        print("[ERROR] AI Chat interface missing")

    print("\n[OK] Frontend validation completed")

except Exception as e:
    print(f"[ERROR] Frontend validation failed: {e}")