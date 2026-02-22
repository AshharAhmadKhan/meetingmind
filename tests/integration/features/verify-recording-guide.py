#!/usr/bin/env python3
"""
Issue #10: Verify Recording Best Practices Documentation
Checks that the recording guide exists and contains all required sections
"""

import sys
if sys.platform == "win32":
    sys.stdout.reconfigure(encoding="utf-8")

import os

print("="*70)
print("ISSUE #10: RECORDING BEST PRACTICES DOCUMENTATION")
print("="*70)
print()

# Check if guide exists
guide_path = "docs/guides/RECORDING_BEST_PRACTICES.md"

if not os.path.exists(guide_path):
    print(f"❌ Guide not found: {guide_path}")
    sys.exit(1)

print(f"✅ Guide exists: {guide_path}")
print()

# Read guide content
with open(guide_path, 'r', encoding='utf-8') as f:
    content = f.read()

# Required sections
required_sections = [
    "Critical Rule: Explicitly Mention Names",
    "Recording Guidelines",
    "Common Mistakes to Avoid",
    "Recording Checklist",
    "Example: Perfect Meeting Recording",
    "Troubleshooting",
    "Tips for Better Results",
    "Quick Reference Card"
]

print("Checking required sections...")
print("-"*70)

all_present = True
for section in required_sections:
    if section in content:
        print(f"✅ {section}")
    else:
        print(f"❌ Missing: {section}")
        all_present = False

print()

# Check for examples
print("Checking for examples...")
print("-"*70)

if "❌ Bad Example" in content and "✅ Good Example" in content:
    print("✅ Contains bad and good examples")
else:
    print("❌ Missing example comparisons")
    all_present = False

if "Ashhar" in content and "Alishba" in content and "Aayush" in content:
    print("✅ Contains realistic team member examples")
else:
    print("❌ Missing team member examples")
    all_present = False

print()

# Check word count (should be comprehensive)
word_count = len(content.split())
print(f"Documentation length: {word_count} words")

if word_count < 500:
    print("⚠️  Documentation seems too short")
    all_present = False
elif word_count > 2000:
    print("✅ Comprehensive documentation")
else:
    print("✅ Adequate documentation length")

print()
print("="*70)

if all_present:
    print("✅ ISSUE #10: Recording guide complete and comprehensive")
    print("="*70)
    print()
    print("MANUAL VERIFICATION STEPS:")
    print("1. Open docs/guides/RECORDING_BEST_PRACTICES.md")
    print("2. Verify all sections are clear and helpful")
    print("3. Check examples make sense")
    print("4. Confirm checklist is actionable")
    print()
    sys.exit(0)
else:
    print("❌ ISSUE #10: Recording guide incomplete")
    print("="*70)
    sys.exit(1)
