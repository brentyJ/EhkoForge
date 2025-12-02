---
title: "Tier 0 Pre-Annotation Processor Specification"
vault: "EhkoForge"
type: "module"
category: "Data Processing"
status: draft
version: "0.1"
created: 2025-12-01
updated: 2025-12-01
tags: [ehkoforge, tier0, preprocessing, annotation, nlp]
related:
  - "Ingot_System_Schema_v0_1.md"
  - "1_4_Data_Model_v1_3.md"
---

# TIER 0 PRE-ANNOTATION PROCESSOR SPECIFICATION v0.1

## 1. Overview

The Tier 0 processor is a code-based (no LLM) pre-annotation layer that flags signals in raw text before any model touches it. It runs on every message as it arrives, extracting emotion markers, intensity signals, entities, and structural patterns.

### 1.1 Design Goals

1. **Zero LLM cost** — pure Python, regex, keyword matching
2. **Fast** — runs synchronously on message arrival, no batching required
3. **Signal extraction** — identifies emotion markers, intensity, entities, temporal refs, question density
4. **Structured output** — JSON blob stored in `smelt_queue.pre_annotation_json` or `transcript_segments.pre_annotation_json`
5. **Assists Tier 2** — smelt model receives pre-scored text, confirming/expanding rather than cold analysis

### 1.2 Processing Flow

```
Raw Text Input
    ↓
[Word/char counts]
    ↓
[Emotion keyword scan]
    ↓
[Intensity marker detection]
    ↓
[Question analysis]
    ↓
[Temporal reference extraction]
    ↓
[Basic entity extraction]
    ↓
[Structural analysis]
    ↓
[Composite flag computation]
    ↓
JSON Output → Storage
```

---

## 2. Output Schema

```json
{
  "version": "0.1",
  "processed_at": "2025-12-01T14:30:00Z",
  "word_count": 342,
  "char_count": 1847,
  
  "emotion_signals": {
    "keywords_found": ["hate", "proud", "anxious"],
    "keyword_count": 3,
    "keyword_density": 0.0088
  },
  
  "intensity_markers": {
    "exclamations": 2,
    "all_caps_words": 1,
    "repeated_punctuation": 0,
    "intensifiers": ["really", "absolutely"],
    "hedges": ["maybe", "I think"]
  },
  
  "question_analysis": {
    "question_count": 4,
    "question_density": 0.012,
    "self_inquiry": 2,
    "rhetorical_likely": 1
  },
  
  "temporal_references": {
    "past": ["when I was young", "last year"],
    "present": ["now", "currently"],
    "future": ["someday", "planning to"],
    "habitual": ["always", "never", "every time"]
  },
  
  "entities": {
    "people": ["Dad", "Sarah"],
    "places": ["Melbourne", "the old house"],
    "organisations": []
  },
  
  "structural": {
    "paragraph_count": 3,
    "sentence_count": 12,
    "avg_sentence_length": 18.4,
    "longest_sentence": 47,
    "speaker_changes": 0
  },
  
  "flags": {
    "high_emotion": true,
    "self_reflective": true,
    "narrative": false,
    "analytical": false
  }
}
```

---

## 3. Keyword Dictionaries

### 3.1 Emotion Keywords

```python
EMOTION_KEYWORDS = {
    # Negative valence
    "anger": ["hate", "angry", "furious", "resentment", "bitter", "rage", "pissed"],
    "fear": ["scared", "afraid", "terrified", "anxious", "worried", "dread", "panic"],
    "sadness": ["sad", "depressed", "hopeless", "grief", "heartbroken", "miserable", "devastated"],
    "shame": ["ashamed", "embarrassed", "guilty", "humiliated", "worthless", "pathetic"],
    "disgust": ["disgusted", "revolted", "sick of", "repulsed"],
    
    # Positive valence
    "joy": ["happy", "excited", "thrilled", "elated", "joyful", "ecstatic", "delighted"],
    "pride": ["proud", "accomplished", "confident", "capable", "strong"],
    "love": ["love", "adore", "cherish", "devoted", "connected", "close"],
    "gratitude": ["grateful", "thankful", "appreciative", "blessed"],
    "hope": ["hopeful", "optimistic", "looking forward", "excited about"],
    
    # Complex/mixed
    "confusion": ["confused", "lost", "uncertain", "conflicted", "torn"],
    "loneliness": ["lonely", "isolated", "alone", "disconnected", "abandoned"],
    "nostalgia": ["miss", "remember when", "used to", "back then"],
    "ambivalence": ["mixed feelings", "part of me", "on one hand"],
}
```

### 3.2 Intensity Markers

```python
INTENSIFIERS = [
    "very", "really", "extremely", "absolutely", "completely", "totally",
    "incredibly", "deeply", "profoundly", "utterly", "genuinely", "truly",
    "so much", "such a", "the most"
]

HEDGES = [
    "maybe", "perhaps", "I think", "I guess", "sort of", "kind of",
    "probably", "might", "possibly", "I suppose", "not sure if"
]

ABSOLUTES = [
    "always", "never", "every time", "no one", "everyone", "nothing",
    "everything", "completely", "totally", "all", "none"
]
```

### 3.3 Temporal Patterns

```python
TEMPORAL_PATTERNS = {
    "past": [
        r"when I was \w+",
        r"years ago",
        r"back (then|when)",
        r"used to",
        r"I remember",
        r"growing up",
        r"as a (kid|child|teenager)",
        r"last (week|month|year)",
    ],
    "present": [
        r"right now",
        r"currently",
        r"these days",
        r"at the moment",
        r"lately",
    ],
    "future": [
        r"going to",
        r"planning to",
        r"someday",
        r"one day",
        r"eventually",
        r"hoping to",
    ],
    "habitual": [
        r"always",
        r"never",
        r"every time",
        r"whenever",
        r"constantly",
    ],
}
```

### 3.4 Self-Inquiry Patterns

```python
SELF_INQUIRY_PATTERNS = [
    r"why do I\b",
    r"why am I\b",
    r"what('s| is) wrong with me",
    r"who am I\b",
    r"what do I (really )?(want|need|feel)",
    r"am I\b.+\?",
    r"should I\b",
    r"how do I\b",
    r"I wonder (if|why|what)",
]
```

---

## 4. Processing Functions

### 4.1 Main Processor

```python
import re
import json
from datetime import datetime
from typing import Dict, List, Any


def preprocess_text(text: str) -> Dict[str, Any]:
    """
    Run Tier 0 pre-annotation on raw text.
    Returns JSON-serialisable dict for storage.
    """
    result = {
        "version": "0.1",
        "processed_at": datetime.utcnow().isoformat() + "Z",
        "word_count": 0,
        "char_count": len(text),
        "emotion_signals": {},
        "intensity_markers": {},
        "question_analysis": {},
        "temporal_references": {},
        "entities": {},
        "structural": {},
        "flags": {},
    }
    
    # Basic counts
    words = text.split()
    result["word_count"] = len(words)
    
    # Emotion signals
    result["emotion_signals"] = extract_emotion_signals(text, len(words))
    
    # Intensity markers
    result["intensity_markers"] = extract_intensity_markers(text)
    
    # Question analysis
    result["question_analysis"] = analyse_questions(text, len(words))
    
    # Temporal references
    result["temporal_references"] = extract_temporal_refs(text)
    
    # Entities (basic — proper NER would be Tier 1)
    result["entities"] = extract_basic_entities(text)
    
    # Structural analysis
    result["structural"] = analyse_structure(text)
    
    # Composite flags
    result["flags"] = compute_flags(result)
    
    return result
```

### 4.2 Emotion Signal Extraction

```python
def extract_emotion_signals(text: str, word_count: int) -> Dict:
    """Find emotion keywords and calculate density."""
    text_lower = text.lower()
    found = []
    
    for category, keywords in EMOTION_KEYWORDS.items():
        for kw in keywords:
            if kw in text_lower:
                found.append(kw)
    
    return {
        "keywords_found": list(set(found)),
        "keyword_count": len(found),
        "keyword_density": len(found) / max(word_count, 1),
    }
```

### 4.3 Intensity Marker Extraction

```python
def extract_intensity_markers(text: str) -> Dict:
    """Find intensity indicators."""
    text_lower = text.lower()
    
    # Punctuation-based
    exclamations = text.count("!")
    all_caps = len([w for w in text.split() if w.isupper() and len(w) > 2])
    repeated_punct = len(re.findall(r"[!?]{2,}", text))
    
    # Word-based
    intensifiers_found = [i for i in INTENSIFIERS if i in text_lower]
    hedges_found = [h for h in HEDGES if h in text_lower]
    
    return {
        "exclamations": exclamations,
        "all_caps_words": all_caps,
        "repeated_punctuation": repeated_punct,
        "intensifiers": intensifiers_found,
        "hedges": hedges_found,
    }
```

### 4.4 Question Analysis

```python
def analyse_questions(text: str, word_count: int) -> Dict:
    """Analyse question patterns."""
    questions = re.findall(r"[^.!?]*\?", text)
    question_count = len(questions)
    
    # Self-inquiry detection
    self_inquiry = 0
    for pattern in SELF_INQUIRY_PATTERNS:
        self_inquiry += len(re.findall(pattern, text, re.IGNORECASE))
    
    # Rhetorical detection (heuristic: short questions, or containing "really")
    rhetorical = 0
    for q in questions:
        if len(q.split()) < 5 or "really" in q.lower():
            rhetorical += 1
    
    return {
        "question_count": question_count,
        "question_density": question_count / max(word_count, 1),
        "self_inquiry": self_inquiry,
        "rhetorical_likely": rhetorical,
    }
```

### 4.5 Temporal Reference Extraction

```python
def extract_temporal_refs(text: str) -> Dict:
    """Extract temporal reference patterns."""
    result = {"past": [], "present": [], "future": [], "habitual": []}
    
    for category, patterns in TEMPORAL_PATTERNS.items():
        for pattern in patterns:
            matches = re.findall(pattern, text, re.IGNORECASE)
            result[category].extend(matches)
        result[category] = list(set(result[category]))[:5]  # Cap at 5 per category
    
    return result
```

### 4.6 Basic Entity Extraction

```python
def extract_basic_entities(text: str) -> Dict:
    """
    Basic entity extraction without NLP library.
    Catches capitalised words that aren't sentence starters.
    """
    # Simple heuristic: capitalised words mid-sentence
    sentences = re.split(r"[.!?]", text)
    people = []
    places = []
    
    # Common titles suggesting people
    people_titles = ["Mr", "Mrs", "Ms", "Dr", "Mum", "Mom", "Dad", "Uncle", "Aunt", "Grandma", "Grandpa"]
    
    for sentence in sentences:
        words = sentence.split()
        for i, word in enumerate(words):
            if i == 0:
                continue  # Skip sentence starters
            clean = re.sub(r"[^a-zA-Z]", "", word)
            if clean and clean[0].isupper():
                # Check if preceded by title
                if i > 0 and any(words[i-1].startswith(t) for t in people_titles):
                    people.append(clean)
                elif clean in people_titles:
                    people.append(clean)
                else:
                    # Could be place or person — add to both for now
                    people.append(clean)
    
    return {
        "people": list(set(people))[:10],
        "places": list(set(places))[:10],
        "organisations": [],
    }
```

### 4.7 Structural Analysis

```python
def analyse_structure(text: str) -> Dict:
    """Analyse text structure."""
    paragraphs = [p for p in text.split("\n\n") if p.strip()]
    sentences = re.split(r"[.!?]+", text)
    sentences = [s.strip() for s in sentences if s.strip()]
    
    sentence_lengths = [len(s.split()) for s in sentences]
    
    return {
        "paragraph_count": len(paragraphs),
        "sentence_count": len(sentences),
        "avg_sentence_length": sum(sentence_lengths) / max(len(sentence_lengths), 1),
        "longest_sentence": max(sentence_lengths) if sentence_lengths else 0,
        "speaker_changes": text.count("**Me:**") + text.count("**Ehko:**"),
    }
```

### 4.8 Composite Flag Computation

```python
def compute_flags(result: Dict) -> Dict:
    """Compute composite flags from extracted data."""
    emotion = result["emotion_signals"]
    questions = result["question_analysis"]
    intensity = result["intensity_markers"]
    temporal = result["temporal_references"]
    
    return {
        "high_emotion": (
            emotion["keyword_count"] >= 2 or
            intensity["exclamations"] >= 2 or
            intensity["all_caps_words"] >= 1
        ),
        "self_reflective": (
            questions["self_inquiry"] >= 1 or
            questions["question_density"] > 0.02
        ),
        "narrative": (
            len(temporal["past"]) >= 2 or
            result["structural"]["paragraph_count"] >= 3
        ),
        "analytical": (
            len(intensity["hedges"]) >= 2 and
            questions["question_count"] >= 2
        ),
    }
```

---

## 5. Integration Points

### 5.1 When Called

| Trigger | Action |
|---------|--------|
| Chat message saved | `preprocess_text()` → attach to message or queue entry |
| Transcript uploaded | Segment if needed → `preprocess_text()` on each segment |
| Smelt queue entry created | Pre-annotation JSON attached to entry |

### 5.2 Storage Locations

| Source Type | Storage Field |
|-------------|---------------|
| Chat session | `smelt_queue.pre_annotation_json` |
| Transcript segment | `transcript_segments.pre_annotation_json` |

### 5.3 Consumption by Tier 2

The smelt model receives pre-annotation JSON alongside raw text. Example prompt inclusion:

```
The following signals were detected by automated analysis:
- Emotion keywords: hate, proud, anxious (density: 0.88%)
- High emotion flag: TRUE
- Self-reflective flag: TRUE
- Temporal references: past (when I was young, last year)
- Entities: Dad, Sarah

Confirm, expand, or override these signals based on your analysis.
```

---

## 6. Configuration (Future)

```yaml
# tier0_config.yaml
emotion_keywords_path: "lexicon/emotion_keywords.yaml"
custom_keywords:
  project_terms:
    - "EhkoForge"
    - "Mirrorwell"
    - "ingot"
    - "forge"
entity_extraction:
  use_spacy: false  # future enhancement
  people_titles_path: "lexicon/people_titles.yaml"
segmentation:
  max_words_per_segment: 2000
  prefer_natural_breaks: true
flags:
  high_emotion_threshold:
    keyword_count: 2
    exclamations: 2
  self_reflective_threshold:
    self_inquiry: 1
    question_density: 0.02
```

---

## 7. Module Location

**Recommended file path:** `EhkoForge/5.0 Scripts/ehkoforge/preprocessing/tier0.py`

**Imports:**
```python
from ehkoforge.preprocessing.tier0 import preprocess_text
```

---

## 8. Open Items

- [ ] spaCy integration for better NER (Tier 0.5?)
- [ ] Custom keyword dictionaries per user/vault
- [ ] Sentiment polarity scoring (positive/negative beyond keywords)
- [ ] Language detection for non-English support
- [ ] Australian English spelling variants in dictionaries

---

**Changelog**
- v0.1 — 2025-12-01 — Initial specification
