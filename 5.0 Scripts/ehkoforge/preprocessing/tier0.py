"""
EhkoForge Tier 0 Pre-Annotation Processor v0.1

Zero-LLM-cost signal extraction from raw text.
Runs on every message/segment to flag emotion markers, intensity, 
entities, temporal references, and question patterns.

Output: JSON blob stored in smelt_queue.pre_annotation_json
"""

import re
import json
from datetime import datetime
from typing import Dict, List, Any, Optional


# =============================================================================
# KEYWORD DICTIONARIES
# =============================================================================

EMOTION_KEYWORDS = {
    # Negative valence
    "anger": ["hate", "angry", "furious", "resentment", "bitter", "rage", "pissed", "frustrated", "annoyed"],
    "fear": ["scared", "afraid", "terrified", "anxious", "worried", "dread", "panic", "nervous", "uneasy"],
    "sadness": ["sad", "depressed", "hopeless", "grief", "heartbroken", "miserable", "devastated", "down", "low"],
    "shame": ["ashamed", "embarrassed", "guilty", "humiliated", "worthless", "pathetic", "stupid", "failure"],
    "disgust": ["disgusted", "revolted", "sick of", "repulsed", "gross"],
    
    # Positive valence
    "joy": ["happy", "excited", "thrilled", "elated", "joyful", "ecstatic", "delighted", "pleased", "glad"],
    "pride": ["proud", "accomplished", "confident", "capable", "strong", "successful"],
    "love": ["love", "adore", "cherish", "devoted", "connected", "close", "fond", "care"],
    "gratitude": ["grateful", "thankful", "appreciative", "blessed", "fortunate"],
    "hope": ["hopeful", "optimistic", "looking forward", "excited about", "eager"],
    
    # Complex/mixed
    "confusion": ["confused", "lost", "uncertain", "conflicted", "torn", "unsure", "puzzled"],
    "loneliness": ["lonely", "isolated", "alone", "disconnected", "abandoned", "excluded"],
    "nostalgia": ["miss", "remember when", "used to", "back then", "those days"],
    "ambivalence": ["mixed feelings", "part of me", "on one hand", "not sure if"],
}

INTENSIFIERS = [
    "very", "really", "extremely", "absolutely", "completely", "totally",
    "incredibly", "deeply", "profoundly", "utterly", "genuinely", "truly",
    "so much", "such a", "the most", "fucking", "bloody", "damn"
]

HEDGES = [
    "maybe", "perhaps", "I think", "I guess", "sort of", "kind of",
    "probably", "might", "possibly", "I suppose", "not sure if",
    "I don't know", "I wonder", "seems like"
]

ABSOLUTES = [
    "always", "never", "every time", "no one", "everyone", "nothing",
    "everything", "completely", "totally", "all", "none", "forever"
]

TEMPORAL_PATTERNS = {
    "past": [
        r"when I was \w+",
        r"years ago",
        r"back (then|when)",
        r"used to",
        r"I remember",
        r"growing up",
        r"as a (kid|child|teenager|young)",
        r"last (week|month|year)",
        r"in the past",
        r"before (I|we|that)",
    ],
    "present": [
        r"right now",
        r"currently",
        r"these days",
        r"at the moment",
        r"lately",
        r"nowadays",
        r"today",
    ],
    "future": [
        r"going to",
        r"planning to",
        r"someday",
        r"one day",
        r"eventually",
        r"hoping to",
        r"want to",
        r"will be",
        r"in the future",
    ],
    "habitual": [
        r"\balways\b",
        r"\bnever\b",
        r"every time",
        r"whenever",
        r"constantly",
        r"usually",
        r"often",
    ],
}

SELF_INQUIRY_PATTERNS = [
    r"why do I\b",
    r"why am I\b",
    r"what('s| is) wrong with me",
    r"who am I\b",
    r"what do I (really )?(want|need|feel)",
    r"am I\b.+\?",
    r"should I\b",
    r"how do I\b",
    r"I wonder (if|why|what|whether)",
    r"what if I\b",
    r"do I (really|actually|even)",
]

# Common titles/indicators for people
PEOPLE_TITLES = [
    "Mr", "Mrs", "Ms", "Dr", "Mum", "Mom", "Dad", "Father", "Mother",
    "Uncle", "Aunt", "Grandma", "Grandpa", "Gran", "Pop", "Nan",
    "Brother", "Sister", "Son", "Daughter", "Wife", "Husband",
    "Boss", "Manager", "Teacher", "Coach", "Therapist"
]


# =============================================================================
# PROCESSING FUNCTIONS
# =============================================================================

def preprocess_text(text: str) -> Dict[str, Any]:
    """
    Run Tier 0 pre-annotation on raw text.
    
    Args:
        text: Raw text to analyse
        
    Returns:
        JSON-serialisable dict with extracted signals
    """
    if not text or not text.strip():
        return _empty_result()
    
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
    
    # Run extractors
    result["emotion_signals"] = extract_emotion_signals(text, len(words))
    result["intensity_markers"] = extract_intensity_markers(text)
    result["question_analysis"] = analyse_questions(text, len(words))
    result["temporal_references"] = extract_temporal_refs(text)
    result["entities"] = extract_basic_entities(text)
    result["structural"] = analyse_structure(text)
    
    # Compute composite flags
    result["flags"] = compute_flags(result)
    
    return result


def _empty_result() -> Dict[str, Any]:
    """Return empty result structure for empty/null input."""
    return {
        "version": "0.1",
        "processed_at": datetime.utcnow().isoformat() + "Z",
        "word_count": 0,
        "char_count": 0,
        "emotion_signals": {"keywords_found": [], "keyword_count": 0, "keyword_density": 0.0},
        "intensity_markers": {"exclamations": 0, "all_caps_words": 0, "repeated_punctuation": 0, "intensifiers": [], "hedges": []},
        "question_analysis": {"question_count": 0, "question_density": 0.0, "self_inquiry": 0, "rhetorical_likely": 0},
        "temporal_references": {"past": [], "present": [], "future": [], "habitual": []},
        "entities": {"people": [], "places": [], "organisations": []},
        "structural": {"paragraph_count": 0, "sentence_count": 0, "avg_sentence_length": 0, "longest_sentence": 0, "speaker_changes": 0},
        "flags": {"high_emotion": False, "self_reflective": False, "narrative": False, "analytical": False},
    }


def extract_emotion_signals(text: str, word_count: int) -> Dict:
    """Find emotion keywords and calculate density."""
    text_lower = text.lower()
    found = []
    categories_found = set()
    
    for category, keywords in EMOTION_KEYWORDS.items():
        for kw in keywords:
            # Use word boundary matching for single words
            if " " in kw:
                if kw in text_lower:
                    found.append(kw)
                    categories_found.add(category)
            else:
                if re.search(rf"\b{re.escape(kw)}\b", text_lower):
                    found.append(kw)
                    categories_found.add(category)
    
    return {
        "keywords_found": list(set(found)),
        "categories": list(categories_found),
        "keyword_count": len(found),
        "keyword_density": len(found) / max(word_count, 1),
    }


def extract_intensity_markers(text: str) -> Dict:
    """Find intensity indicators."""
    text_lower = text.lower()
    
    # Punctuation-based
    exclamations = text.count("!")
    all_caps = len([w for w in text.split() if w.isupper() and len(w) > 2 and w.isalpha()])
    repeated_punct = len(re.findall(r"[!?]{2,}", text))
    
    # Word-based
    intensifiers_found = []
    for i in INTENSIFIERS:
        if i.lower() in text_lower:
            intensifiers_found.append(i)
    
    hedges_found = []
    for h in HEDGES:
        if h.lower() in text_lower:
            hedges_found.append(h)
    
    absolutes_found = []
    for a in ABSOLUTES:
        if re.search(rf"\b{re.escape(a.lower())}\b", text_lower):
            absolutes_found.append(a)
    
    return {
        "exclamations": exclamations,
        "all_caps_words": all_caps,
        "repeated_punctuation": repeated_punct,
        "intensifiers": list(set(intensifiers_found)),
        "hedges": list(set(hedges_found)),
        "absolutes": list(set(absolutes_found)),
    }


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
        q_words = len(q.split())
        if q_words < 5 or "really" in q.lower() or "right?" in q.lower():
            rhetorical += 1
    
    return {
        "question_count": question_count,
        "question_density": question_count / max(word_count, 1),
        "self_inquiry": self_inquiry,
        "rhetorical_likely": rhetorical,
    }


def extract_temporal_refs(text: str) -> Dict:
    """Extract temporal reference patterns."""
    result = {"past": [], "present": [], "future": [], "habitual": []}
    
    for category, patterns in TEMPORAL_PATTERNS.items():
        for pattern in patterns:
            matches = re.findall(pattern, text, re.IGNORECASE)
            # Flatten any tuple matches from groups
            for match in matches:
                if isinstance(match, tuple):
                    result[category].append(" ".join(match))
                else:
                    result[category].append(match)
        # Dedupe and cap
        result[category] = list(set(result[category]))[:5]
    
    return result


def extract_basic_entities(text: str) -> Dict:
    """
    Basic entity extraction without NLP library.
    Catches capitalised words mid-sentence and title-preceded names.
    """
    sentences = re.split(r"[.!?]", text)
    people = []
    
    for sentence in sentences:
        words = sentence.split()
        for i, word in enumerate(words):
            if i == 0:
                continue  # Skip sentence starters
            
            clean = re.sub(r"[^a-zA-Z']", "", word)
            if not clean:
                continue
                
            # Check if capitalised
            if clean[0].isupper():
                # Check if preceded by title
                if i > 0:
                    prev = re.sub(r"[^a-zA-Z]", "", words[i-1])
                    if prev in PEOPLE_TITLES:
                        people.append(clean)
                        continue
                
                # Check if it IS a title
                if clean in PEOPLE_TITLES:
                    people.append(clean)
                    continue
                
                # Generic capitalised word - likely a name
                # Filter out common non-name capitals
                if clean not in ["I", "I'm", "I've", "I'll", "I'd"]:
                    people.append(clean)
    
    return {
        "people": list(set(people))[:10],
        "places": [],  # Would need NER for reliable place detection
        "organisations": [],
    }


def analyse_structure(text: str) -> Dict:
    """Analyse text structure."""
    paragraphs = [p for p in text.split("\n\n") if p.strip()]
    sentences = re.split(r"[.!?]+", text)
    sentences = [s.strip() for s in sentences if s.strip()]
    
    sentence_lengths = [len(s.split()) for s in sentences]
    
    # Count speaker changes (for chat transcripts)
    speaker_changes = 0
    speaker_patterns = [
        r"\*\*Me:\*\*", r"\*\*Ehko:\*\*", r"\*\*User:\*\*", r"\*\*Assistant:\*\*",
        r"^Me:", r"^You:", r"^Ehko:"
    ]
    for pattern in speaker_patterns:
        speaker_changes += len(re.findall(pattern, text, re.MULTILINE))
    
    return {
        "paragraph_count": len(paragraphs),
        "sentence_count": len(sentences),
        "avg_sentence_length": round(sum(sentence_lengths) / max(len(sentence_lengths), 1), 1),
        "longest_sentence": max(sentence_lengths) if sentence_lengths else 0,
        "speaker_changes": speaker_changes,
    }


def compute_flags(result: Dict) -> Dict:
    """Compute composite flags from extracted data."""
    emotion = result["emotion_signals"]
    questions = result["question_analysis"]
    intensity = result["intensity_markers"]
    temporal = result["temporal_references"]
    structural = result["structural"]
    
    return {
        "high_emotion": (
            emotion["keyword_count"] >= 2 or
            intensity["exclamations"] >= 2 or
            intensity["all_caps_words"] >= 1 or
            len(intensity.get("absolutes", [])) >= 2
        ),
        "self_reflective": (
            questions["self_inquiry"] >= 1 or
            questions["question_density"] > 0.02
        ),
        "narrative": (
            len(temporal["past"]) >= 2 or
            structural["paragraph_count"] >= 3
        ),
        "analytical": (
            len(intensity["hedges"]) >= 2 and
            questions["question_count"] >= 2
        ),
    }


# =============================================================================
# UTILITY FUNCTIONS
# =============================================================================

def summarise_for_prompt(pre_annotation: Dict) -> str:
    """
    Generate a human-readable summary of pre-annotation for LLM prompts.
    
    Args:
        pre_annotation: Output from preprocess_text()
        
    Returns:
        Formatted string for inclusion in Tier 2 prompts
    """
    parts = []
    
    # Emotion signals
    if pre_annotation.get("emotion_signals", {}).get("keywords_found"):
        keywords = pre_annotation["emotion_signals"]["keywords_found"][:5]
        parts.append(f"Emotion keywords: {', '.join(keywords)}")
    
    if pre_annotation.get("emotion_signals", {}).get("categories"):
        cats = pre_annotation["emotion_signals"]["categories"][:3]
        parts.append(f"Emotion categories: {', '.join(cats)}")
    
    # Flags
    flags = pre_annotation.get("flags", {})
    active_flags = [k.replace("_", " ") for k, v in flags.items() if v]
    if active_flags:
        parts.append(f"Flags: {', '.join(active_flags)}")
    
    # Temporal
    if pre_annotation.get("temporal_references", {}).get("past"):
        past_refs = pre_annotation["temporal_references"]["past"][:3]
        parts.append(f"Past references: {', '.join(past_refs)}")
    
    # People
    if pre_annotation.get("entities", {}).get("people"):
        people = pre_annotation["entities"]["people"][:5]
        parts.append(f"People mentioned: {', '.join(people)}")
    
    # Intensity
    intensity = pre_annotation.get("intensity_markers", {})
    if intensity.get("exclamations", 0) >= 2:
        parts.append(f"High exclamation count: {intensity['exclamations']}")
    if intensity.get("absolutes"):
        parts.append(f"Absolute statements: {', '.join(intensity['absolutes'][:3])}")
    
    # Questions
    questions = pre_annotation.get("question_analysis", {})
    if questions.get("self_inquiry", 0) >= 1:
        parts.append(f"Self-inquiry questions: {questions['self_inquiry']}")
    
    if not parts:
        return "No significant signals detected."
    
    return "\n".join(f"- {p}" for p in parts)


def to_json(pre_annotation: Dict) -> str:
    """Serialise pre-annotation to JSON string for database storage."""
    return json.dumps(pre_annotation, ensure_ascii=False)


def from_json(json_str: str) -> Optional[Dict]:
    """Deserialise pre-annotation from JSON string."""
    if not json_str:
        return None
    try:
        return json.loads(json_str)
    except json.JSONDecodeError:
        return None


# =============================================================================
# MODULE EXPORTS
# =============================================================================

__all__ = [
    "preprocess_text",
    "summarise_for_prompt",
    "to_json",
    "from_json",
    "EMOTION_KEYWORDS",
    "INTENSIFIERS",
    "HEDGES",
    "ABSOLUTES",
]
