#!/usr/bin/env python3
"""
Test fuzzy name matching functionality
"""

from difflib import SequenceMatcher

def fuzzy_match_owner(ai_owner, team_members, threshold=0.6):
    """
    Match AI-extracted owner name to team member names using fuzzy matching.
    """
    if not ai_owner or ai_owner == 'Unassigned' or not team_members:
        return ai_owner
    
    ai_owner_lower = ai_owner.lower().strip()
    best_match = None
    best_ratio = 0.0
    
    for member_name in team_members:
        member_lower = member_name.lower().strip()
        
        # Check for exact match first
        if ai_owner_lower == member_lower:
            return member_name
        
        # Check if AI name is a word in member name (e.g., "Zeeshan" in "Abdul Zeeshan")
        member_words = member_lower.split()
        if ai_owner_lower in member_words:
            print(f"✓ Matched '{ai_owner}' → '{member_name}' (word match)")
            return member_name
        
        # Check if AI name is a substring of any word in member name
        for word in member_words:
            if ai_owner_lower in word or word in ai_owner_lower:
                ratio = SequenceMatcher(None, ai_owner_lower, word).ratio()
                if ratio > best_ratio:
                    best_ratio = ratio
                    best_match = member_name
        
        # Also check overall similarity
        overall_ratio = SequenceMatcher(None, ai_owner_lower, member_lower).ratio()
        if overall_ratio > best_ratio:
            best_ratio = overall_ratio
            best_match = member_name
    
    # Return best match if above threshold
    if best_match and best_ratio >= threshold:
        print(f"✓ Matched '{ai_owner}' → '{best_match}' (ratio: {best_ratio:.2f})")
        return best_match
    
    # No good match found
    print(f"✗ No match for '{ai_owner}' (best ratio: {best_ratio:.2f})")
    return ai_owner

def test_fuzzy_matching():
    """Test various fuzzy matching scenarios"""
    
    team_members = [
        "Abdul Zeeshan",
        "Ashhar Ahmad Khan",
        "Muhammad Ali"
    ]
    
    test_cases = [
        # (AI extracted name, expected match)
        ("Zeeshan", "Abdul Zeeshan"),
        ("Abdul", "Abdul Zeeshan"),
        ("Ashhar", "Ashhar Ahmad Khan"),
        ("Khan", "Ashhar Ahmad Khan"),
        ("Ali", "Muhammad Ali"),
        ("Muhammad", "Muhammad Ali"),
        ("Unassigned", "Unassigned"),
        ("John", "John"),  # No match
        ("Abdul Zeeshan", "Abdul Zeeshan"),  # Exact match
    ]
    
    print("=" * 60)
    print("FUZZY NAME MATCHING TEST")
    print("=" * 60)
    print(f"\nTeam Members: {team_members}\n")
    
    passed = 0
    failed = 0
    
    for ai_name, expected in test_cases:
        result = fuzzy_match_owner(ai_name, team_members)
        status = "PASS" if result == expected else "FAIL"
        
        if status == "PASS":
            passed += 1
        else:
            failed += 1
            
        print(f"[{status}] AI: '{ai_name}' → Result: '{result}' (Expected: '{expected}')")
    
    print("\n" + "=" * 60)
    print(f"RESULTS: {passed} passed, {failed} failed")
    print("=" * 60)
    
    return failed == 0

if __name__ == "__main__":
    success = test_fuzzy_matching()
    exit(0 if success else 1)
