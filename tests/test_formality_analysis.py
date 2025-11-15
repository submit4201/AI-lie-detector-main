#!/usr/bin/env python3
"""
Test formality scoring system to understand how formal vs informal speech is calculated.
"""

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), 'backend'))

from services.linguistic_service import analyze_linguistic_patterns

def test_formality_scoring():
    """Test different speech samples to understand formality scoring"""
    
    test_cases = [
        {
            "name": "Highly Formal Business Speech",
            "text": "Sir, I would respectfully like to thank you for this opportunity. Furthermore, I sincerely believe that this proposal will consequently benefit all stakeholders. Therefore, I kindly request your consideration regarding this matter. In accordance with our previous discussions, I would like to moreover present additional evidence that will undoubtedly support our position.",
            "expected_level": "High (70+)"
        },
        {
            "name": "Moderately Formal Academic Speech", 
            "text": "However, the research indicates that these findings are significant. Nevertheless, we must consider the limitations of this study. Therefore, additional research is needed to confirm these results. The data suggests that there may be underlying factors that we haven't fully examined.",
            "expected_level": "Moderate (40-70)"
        },
        {
            "name": "Casual Conversational Speech",
            "text": "Yeah, I think it's gonna be okay. I mean, we can't really know for sure, but I guess we'll see what happens. It's kinda complicated, you know? I dunno, maybe we should just wait and see.",
            "expected_level": "Low (0-40)"
        },
        {
            "name": "Very Informal Street Speech",
            "text": "Nah, I ain't gonna do that. It's kinda stupid if you ask me. Yeah, I wanna get outta here. This whole thing is sorta messed up, ain't it? I dunno what they're thinking.",
            "expected_level": "Very Low (0-20)"
        },
        {
            "name": "Mixed Formal/Informal",
            "text": "Please understand that I'm gonna need more information. However, I can't really say for sure what's gonna happen. Nevertheless, I think we should proceed carefully. Yeah, it's kinda important that we get this right.",
            "expected_level": "Mixed (30-50)"
        },
        {
            "name": "Legal/Professional Language",
            "text": "Pursuant to our agreement, I hereby respectfully request that you provide the aforementioned documentation. Furthermore, in accordance with the established protocols, we must consequently ensure compliance with all applicable regulations. Therefore, I kindly ask for your cooperation regarding this matter.",
            "expected_level": "Very High (80+)"
        }
    ]
    
    print("=" * 80)
    print("FORMALITY SCORING ANALYSIS")
    print("=" * 80)
    print()
    
    for i, case in enumerate(test_cases, 1):
        print(f"{i}. {case['name']}")
        print(f"Expected Level: {case['expected_level']}")
        print(f"Text: \"{case['text']}\"")
        print()
        
        # Analyze the text
        result = analyze_linguistic_patterns(case['text'], duration=10.0)
        
        # Extract formality-related metrics
        formality_score = result.get('formality_score', 0)
        word_count = result.get('word_count', 0)
        
        # Calculate component breakdown for understanding
        import re
        
        # Count formal words
        formal_pattern = r'\b(sir|madam|please|thank you|kindly|respectfully|sincerely|furthermore|however|nevertheless|therefore|consequently|moreover|additionally|subsequently|accordingly|thus|hence|whereas|albeit|notwithstanding|indeed|pursuant to|in accordance with|with regard to|concerning|regarding)\b'
        formal_words = re.findall(formal_pattern, case['text'], re.IGNORECASE)
        
        # Count informal words  
        informal_pattern = r'\b(yeah|yep|nah|gonna|wanna|gotta|kinda|sorta|dunno|ain\'t|can\'t|won\'t|shouldn\'t|wouldn\'t|couldn\'t|isn\'t|aren\'t|wasn\'t|weren\'t|haven\'t|hasn\'t|hadn\'t|don\'t|doesn\'t|didn\'t)\b'
        informal_words = re.findall(informal_pattern, case['text'], re.IGNORECASE)
        
        # Calculate ratios
        formal_ratio = len(formal_words) / max(word_count, 1)
        informal_ratio = len(informal_words) / max(word_count, 1)
        
        print(f"[DATA] FORMALITY ANALYSIS:")
        print(f"   Final Score: {formality_score}/100")
        print(f"   Word Count: {word_count}")
        print(f"   Formal Words Found: {len(formal_words)} ({formal_words[:5]}{'...' if len(formal_words) > 5 else ''})")
        print(f"   Informal Words Found: {len(informal_words)} ({informal_words[:5]}{'...' if len(informal_words) > 5 else ''})")
        print(f"   Formal Ratio: {formal_ratio:.4f} ({formal_ratio * 100:.2f}%)")
        print(f"   Informal Ratio: {informal_ratio:.4f} ({informal_ratio * 100:.2f}%)")
        print(f"   Net Formality: {(formal_ratio - informal_ratio) * 100:.2f}%")
        
        # Interpretation
        if formality_score >= 80:
            level = "Very High - Professional/Legal"
        elif formality_score >= 60:
            level = "High - Business/Academic"
        elif formality_score >= 40:
            level = "Moderate - Semi-formal"
        elif formality_score >= 20:
            level = "Low - Casual conversation"
        else:
            level = "Very Low - Informal/Slang"
            
        print(f"   Classification: {level}")
        print()
        print("-" * 60)
        print()

def explain_formality_algorithm():
    """Explain how the formality scoring algorithm works"""
    
    print("=" * 80)
    print("FORMALITY SCORING ALGORITHM EXPLANATION")
    print("=" * 80)
    print()
    
    print("📋 ALGORITHM BREAKDOWN:")
    print()
    print("1. FORMAL INDICATORS (Positive Score):")
    print("   • Politeness: sir, madam, please, thank you, kindly")
    print("   • Professional: respectfully, sincerely, pursuant to")
    print("   • Academic: furthermore, however, nevertheless, therefore")
    print("   • Transition: consequently, moreover, additionally, subsequently")
    print("   • Logical: accordingly, thus, hence, whereas, albeit")
    print("   • Emphasis: indeed, notwithstanding")
    print("   • References: in accordance with, with regard to, concerning")
    print()
    
    print("2. INFORMAL INDICATORS (Negative Score):")
    print("   • Casual responses: yeah, yep, nah")
    print("   • Contractions: gonna, wanna, gotta, kinda, sorta, dunno")
    print("   • Negative contractions: ain't, can't, won't, shouldn't, etc.")
    print("   • Common contractions: isn't, aren't, wasn't, weren't, etc.")
    print("   • Auxiliary contractions: haven't, hasn't, hadn't, don't, etc.")
    print()
    
    print("3. CALCULATION FORMULA:")
    print("   formal_ratio = formal_word_count / total_words")
    print("   informal_penalty = informal_word_count / total_words")
    print("   formality_score = (formal_ratio × 1000) - (informal_penalty × 500)")
    print("   final_score = max(0, min(100, formality_score))")
    print()
    
    print("4. SCORING INTERPRETATION:")
    print("   • 80-100: Very High (Professional/Legal language)")
    print("   • 60-79:  High (Business/Academic discourse)")
    print("   • 40-59:  Moderate (Semi-formal conversation)")
    print("   • 20-39:  Low (Casual everyday speech)")
    print("   • 0-19:   Very Low (Informal/Slang heavy)")
    print()
    
    print("5. WEIGHTING RATIONALE:")
    print("   • Formal words get 10x weight (1000x ratio) - rare but impactful")
    print("   • Informal words get 5x penalty (500x ratio) - common but degrading")
    print("   • This means 1% formal words = 10 points")
    print("   • This means 1% informal words = -5 points")
    print("   • Balance allows for mixed speech patterns")
    print()

if __name__ == "__main__":
    print("Testing Formality Scoring System")
    print("=" * 50)
    
    # First explain the algorithm
    explain_formality_algorithm()
    
    # Then test with examples
    test_formality_scoring()
    
    print("[PASS] Formality analysis testing complete!")
