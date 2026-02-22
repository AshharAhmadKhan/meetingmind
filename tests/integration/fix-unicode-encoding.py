#!/usr/bin/env python3
"""
Fix Unicode encoding issues in test scripts for Windows
Adds UTF-8 encoding declaration to all Python test files
"""

import os
import sys

def fix_file(filepath):
    """Add UTF-8 encoding to a Python file"""
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Check if file already has encoding setup
        if 'sys.stdout.reconfigure' in content or 'PYTHONIOENCODING' in content:
            return False
        
        # Add encoding setup after shebang and docstring
        lines = content.split('\n')
        insert_pos = 0
        
        # Skip shebang
        if lines[0].startswith('#!'):
            insert_pos = 1
        
        # Skip docstring
        in_docstring = False
        for i in range(insert_pos, len(lines)):
            if '"""' in lines[i] or "'''" in lines[i]:
                if not in_docstring:
                    in_docstring = True
                else:
                    insert_pos = i + 1
                    break
        
        # Insert encoding setup
        encoding_code = [
            '',
            '# Fix Unicode encoding for Windows',
            'import sys',
            'if sys.platform == "win32":',
            '    sys.stdout.reconfigure(encoding="utf-8")',
            ''
        ]
        
        lines = lines[:insert_pos] + encoding_code + lines[insert_pos:]
        
        # Write back
        with open(filepath, 'w', encoding='utf-8', newline='\n') as f:
            f.write('\n'.join(lines))
        
        return True
        
    except Exception as e:
        print(f"Error fixing {filepath}: {e}")
        return False

def main():
    print("Fixing Unicode encoding in test scripts...")
    print()
    
    fixed_count = 0
    skipped_count = 0
    
    # Find all Python test files
    test_dirs = [
        'scripts/testing',
        'scripts/testing/core',
        'scripts/testing/api',
        'scripts/testing/features'
    ]
    
    for test_dir in test_dirs:
        if not os.path.exists(test_dir):
            continue
            
        for filename in os.listdir(test_dir):
            if filename.endswith('.py') and not filename.startswith('fix-'):
                filepath = os.path.join(test_dir, filename)
                
                if fix_file(filepath):
                    print(f"✅ Fixed: {filepath}")
                    fixed_count += 1
                else:
                    print(f"⏭️  Skipped: {filepath}")
                    skipped_count += 1
    
    print()
    print(f"Fixed: {fixed_count} files")
    print(f"Skipped: {skipped_count} files")
    print()
    print("✅ Done! Tests should now work on Windows.")

if __name__ == '__main__':
    main()
