#!/usr/bin/env python3
"""
Test enhanced formality scoring system with comprehensive patterns
"""

import sys
from pathlib import Path
sys.path.append(str(Path(__file__).parent.parent))

from backend.services.linguistic_service import analyze_linguistic_patterns

def test_enhanced_formality():
    """Test the enhanced formality scoring with various speech patterns"""
    
    test_cases = [
        {
            "name": "Ultra-Formal Legal Speech",
            "text": "Your Honor, pursuant to the aforementioned documentation, I respectfully submit that the evidence herein demonstrates, notwithstanding the defendant's contentions, that we have substantially proven our case. Furthermore, in accordance with established precedent, I humbly request the court's consideration of these materials.",
            "expected": "95-100"
        },
        {
            "name": "Business Professional Speech",
            "text": "Allow me to express my sincere appreciation for this opportunity. I would like to convey that our proposal will significantly benefit all stakeholders. Consequently, I feel compelled to emphasize the substantial advantages of this partnership.",
            "expected": "80-95"
        },
        {
            "name": "Academic Presentation",
            "text": "The research indicates that these findings are particularly significant. Nevertheless, we must consider the limitations. Therefore, additional investigation is needed to comprehensively understand the underlying mechanisms.",
            "expected": "60-80"
        },
        {
            "name": "Semi-Formal Conversation",
            "text": "I think we should probably proceed carefully. However, I'm not entirely sure what the best approach would be. Maybe we could consider some alternatives that might work better.",
            "expected": "40-60"
        },
        {
            "name": "Casual Friendly Chat",
            "text": "Yeah, that sounds pretty cool. I'm totally on board with that idea. It's gonna be awesome if we can pull it off. No biggie if it doesn't work out though.",
            "expected": "10-30"
        },
        {
            "name": "Very Informal/Slang Heavy",
            "text": "Dude, that's so totally awesome! I'm like, yeah, whatever, you know what I mean? It's gonna be sweet, bro. No way that's not gonna work out, man.",
            "expected": "0-15"
        },
        {
            "name": "Mixed Professional/Casual",
            "text": "I'd like to thank you for the opportunity, but honestly, I think we're gonna need more time. It's kinda complicated, you know? Nevertheless, I'm confident we can figure it out.",
            "expected": "25-45"
        },
        {
            "name": "Standard Contractions (Moderate Impact)",
            "text": "I don't think we should proceed without more information. It's important that we understand what we're dealing with. I'm sure we can find a solution that works for everyone.",
            "expected": "35-55"
        }
    ]
    
    print("=" * 90)
    print("ENHANCED FORMALITY SCORING TEST")
    print("=" * 90)
    print()
    
    for i, case in enumerate(test_cases, 1):
        print(f"{i}. {case['name']}")
        print(f"Expected Range: {case['expected']}")
        print(f"Text: \"{case['text'][:100]}{'...' if len(case['text']) > 100 else ''}\"")
        print()
        
        # Analyze the text
        result = analyze_linguistic_patterns(case['text'], duration=10.0)
        formality_score = result.get('formality_score', 0)
        word_count = result.get('word_count', 0)
        
        # Manual pattern analysis for verification
        import re
        
        # Count different types of formal patterns
        formal_transitions = len(re.findall(r'\b(furthermore|however|nevertheless|therefore|consequently|moreover|additionally|subsequently|accordingly|thus|hence|whereas|albeit|notwithstanding|indeed|inasmuch as|insofar as|heretofore|henceforth)\b', case['text'], re.IGNORECASE))
        
        formal_courtesy = len(re.findall(r'\b(sir|madam|please|thank you|kindly|respectfully|sincerely|cordially|graciously|humbly|your honor|your excellency|distinguished|esteemed)\b', case['text'], re.IGNORECASE))
        
        formal_legal = len(re.findall(r'\b(pursuant to|in accordance with|with regard to|concerning|regarding|herein|thereof|whereby|wherein|whereof|heretofore|aforementioned|subsequent to|prior to|in lieu of|notwithstanding)\b', case['text'], re.IGNORECASE))
        
        formal_academic = len(re.findall(r'\b(substantially|significantly|predominantly|fundamentally|essentially|particularly|specifically|generally|typically|consistently|primarily|principally|ultimately|comprehensively)\b', case['text'], re.IGNORECASE))
        
        # Count different types of informal patterns
        casual_informal = len(re.findall(r'\b(yeah|yep|nah|yup|uh-huh|mm-hmm|nope|sure thing|no way|for real|totally|whatever|awesome|cool|sweet|nice|dude|buddy|man|bro|sis|gonna|wanna|gotta|kinda|sorta|dunno|ok|okay|alright|right on|no biggie|no prob|my bad)\b', case['text'], re.IGNORECASE))
        
        standard_contractions = len(re.findall(r'\b(ain\'t|can\'t|won\'t|shouldn\'t|wouldn\'t|couldn\'t|isn\'t|aren\'t|wasn\'t|weren\'t|haven\'t|hasn\'t|hadn\'t|don\'t|doesn\'t|didn\'t|I\'m|you\'re|he\'s|she\'s|it\'s|we\'re|they\'re|I\'ve|you\'ve|we\'ve|they\'ve|I\'ll|you\'ll|he\'ll|she\'ll|we\'ll|they\'ll|I\'d|you\'d|he\'d|she\'d|we\'d|they\'d)\b', case['text'], re.IGNORECASE))
        
        total_formal = formal_transitions + formal_courtesy + formal_legal + formal_academic
        
        print(f"[DATA] DETAILED ANALYSIS:")
        print(f"   Final Score: {formality_score}/100")
        print(f"   Word Count: {word_count}")
        print(f"   ")
        print(f"   FORMAL INDICATORS ({total_formal} total):")
        print(f"     • Academic/Transitions: {formal_transitions}")
        print(f"     • Courtesy/Politeness: {formal_courtesy}")
        print(f"     • Legal/Professional: {formal_legal}")
        print(f"     • Academic Qualifiers: {formal_academic}")
        print(f"   ")
        print(f"   INFORMAL INDICATORS:")
        print(f"     • Casual/Slang: {casual_informal} (heavy penalty)")
        print(f"     • Standard Contractions: {standard_contractions} (light penalty)")
        print(f"   ")
          # Calculate contribution breakdown
        formal_ratio = total_formal / max(word_count, 1)
        casual_ratio = casual_informal / max(word_count, 1)
        standard_ratio = standard_contractions / max(word_count, 1)

        formal_points = formal_ratio * 500
        casual_penalty = casual_ratio * 250
        standard_penalty = standard_ratio * 100
        print(f"   SCORE BREAKDOWN:")
        print(f"     • Baseline: +50.0 points")
        print(f"     • Formal boost: +{formal_points:.1f} points")
        print(f"     • Casual penalty: -{casual_penalty:.1f} points")
        print(f"     • Standard penalty: -{standard_penalty:.1f} points")
        print(f"     • Net calculation: 50 + {formal_points:.1f} - {casual_penalty:.1f} - {standard_penalty:.1f} = {50 + formal_points - casual_penalty - standard_penalty:.1f}")
        print()
        
        # Classification
        if formality_score >= 90:
            level = "🏛️ Ultra-Formal (Legal/Academic)"
        elif formality_score >= 75:
            level = "👔 Highly Formal (Professional Business)"
        elif formality_score >= 60:
            level = "📋 Formal (Business/Academic)"
        elif formality_score >= 45:
            level = "🗣️ Semi-Formal (Professional Casual)"
        elif formality_score >= 30:
            level = "💬 Casual (Everyday Conversation)"
        elif formality_score >= 15:
            level = "🗨️ Informal (Friendly Chat)"
        else:
            level = "💭 Very Informal (Slang/Colloquial)"
            
        print(f"   Classification: {level}")
        print()
        print("-" * 70)
        print()

if __name__ == "__main__":
    test_enhanced_formality()
    print("[PASS] Enhanced formality analysis complete!")

