#!/usr/bin/env python3
"""
Fix Unicode Issues in Test Files
Replaces emoji characters with Windows-compatible alternatives
"""

import os
import re
from pathlib import Path

# Emoji replacements for Windows compatibility
EMOJI_REPLACEMENTS = {
    '🧪': '[TEST]',
    '🚀': '[LAUNCH]', 
    '✅': '[PASS]',
    '❌': '[FAIL]',
    '⚠️': '[WARN]',
    '🎯': '[TARGET]',
    '📊': '[DATA]',
    '🔧': '[TOOL]',
    '📁': '[FILE]',
    '🌐': '[NET]',
    '🏥': '[HEALTH]',
    '📝': '[NOTE]',
    '🎭': '[EMOTION]',
    '🤖': '[AI]',
    '🔍': '[SEARCH]',
    '🎉': '[SUCCESS]',
    '⏱️': '[TIME]',
    '🔢': '[NUM]',
    '🏆': '[WIN]',
    '🎮': '[READY]',
    '✨': '[MAGIC]',
    '🦾': '[STRONG]',
    '🧠': '[BRAIN]',
    '📈': '[PROGRESS]',
    '📨': '[MSG]',
    '🔌': '[CONNECT]',
    '👂': '[LISTEN]',
    '⏰': '[TIMEOUT]',
    '💡': '[IDEA]',
    '🔥': '[HOT]',
    '⚡': '[FAST]',
    '\U0001f680': '[LAUNCH]',
    '\U0001f9ea': '[TEST]',
    '\U0001f9e0': '[BRAIN]',
    '\u2705': '[PASS]',
    '\u274c': '[FAIL]',
}

def fix_unicode_in_file(file_path):
    """Fix unicode issues in a single file"""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        original_content = content
        
        # Replace emoji characters
        for emoji, replacement in EMOJI_REPLACEMENTS.items():
            content = content.replace(emoji, replacement)
        
        # Fix any remaining problematic unicode
        content = re.sub(r'\\U[0-9a-fA-F]{8}', '[EMOJI]', content)
        content = re.sub(r'\\u[0-9a-fA-F]{4}', '[SYMBOL]', content)
        
        if content != original_content:
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(content)
            print(f"[FIXED] {file_path.name}")
            return True
        else:
            print(f"[SKIP] {file_path.name} - no changes needed")
            return False
            
    except Exception as e:
        print(f"[ERROR] Failed to fix {file_path.name}: {e}")
        return False

def fix_all_test_files():
    """Fix unicode issues in all test files"""
    test_dir = Path(__file__).parent
    python_files = list(test_dir.glob("*.py"))
    
    print(f"Fixing unicode issues in {len(python_files)} Python test files...")
    print("=" * 60)
    
    fixed_count = 0
    for file_path in python_files:
        if file_path.name != 'fix_unicode_tests.py':  # Don't fix this file itself
            if fix_unicode_in_file(file_path):
                fixed_count += 1
    
    print("=" * 60)
    print(f"Fixed {fixed_count} files with unicode issues")
    
    return fixed_count

if __name__ == "__main__":
    fix_all_test_files()
