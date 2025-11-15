"""
FORMALITY SCORING SYSTEM DOCUMENTATION
======================================

## Overview
The formality scoring system quantifies how formal or informal a person's speech is on a scale from 0-100. This is crucial for lie detection analysis as speech formality often changes under stress or deception.

## Algorithm Details

### Formal Indicators (Positive Weight: 1000x)
These words/phrases increase the formality score:

**Politeness Markers:**
- sir, madam, please, thank you, kindly

**Professional Language:**
- respectfully, sincerely, pursuant to

**Academic/Formal Transitions:**
- furthermore, however, nevertheless, therefore, consequently
- moreover, additionally, subsequently, accordingly
- thus, hence, whereas, albeit, notwithstanding, indeed

**Formal References:**
- in accordance with, with regard to, concerning, regarding

### Informal Indicators (Negative Weight: 500x)
These words/phrases decrease the formality score:

**Casual Responses:**
- yeah, yep, nah

**Contractions:**
- gonna, wanna, gotta, kinda, sorta, dunno

**Negative Contractions:**
- ain't, can't, won't, shouldn't, wouldn't, couldn't

**Common Contractions:**
- isn't, aren't, wasn't, weren't, haven't, hasn't, hadn't
- don't, doesn't, didn't

### Calculation Formula
```
formal_ratio = formal_word_count / total_word_count
informal_penalty = informal_word_count / total_word_count
raw_score = (formal_ratio × 1000) - (informal_penalty × 500)
final_score = max(0, min(100, raw_score))
```

### Score Interpretation
- **80-100:** Very High Formality (Professional/Legal language)
- **60-79:** High Formality (Business/Academic discourse)
- **40-59:** Moderate Formality (Semi-formal conversation)
- **20-39:** Low Formality (Casual everyday speech)
- **0-19:** Very Low Formality (Informal/Slang heavy)

## Behavioral Analysis Applications

### Deception Detection Indicators
1. **Sudden Formality Increase:** May indicate rehearsed or prepared responses
2. **Formality Decrease:** Could signal stress, nervousness, or loss of composure
3. **Inconsistent Formality:** Rapid changes may indicate cognitive load from deception

### Baseline Establishment
- Compare current formality to person's normal speaking pattern
- Consider context (formal interview vs casual conversation)
- Account for cultural and educational background

### Stress Indicators
- Formal speakers becoming informal under pressure
- Informal speakers becoming overly formal when nervous
- Mixed formal/informal patterns indicating uncertainty

## Technical Implementation Notes

### Why 1000x/500x Weighting?
- Formal words are typically rare but highly impactful
- Informal words are common but should still affect score
- 2:1 ratio allows for natural speech mixing both styles
- 1% formal words = 10 points, 1% informal words = -5 points

### Pattern Matching
- Case-insensitive matching for natural speech variations
- Word boundary matching to avoid partial word matches
- Multi-word phrase support for complex formal expressions

### Limitations
- Cultural context not considered
- Professional jargon may not be captured
- Sarcasm/irony detection not implemented
- Regional dialect variations not accounted for

## Future Enhancements
1. Context-aware scoring (meeting vs casual chat)
2. Personal baseline learning
3. Industry-specific formal vocabulary
4. Cultural formality norms
5. Temporal formality change detection
6. Integration with other linguistic indicators
"""
