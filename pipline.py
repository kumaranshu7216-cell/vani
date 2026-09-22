"""
====================================================================
Project: VratyaVani AI - AI Pipeline & Dialect Detection
File: pipline.py
Stage 3: Indic Dialect Tagging, Classification & Duplicate Detection
====================================================================
"""

import re
from typing import List, Dict, Any, Optional
from pydantic import BaseModel

# vratyavani_core से सही क्लास नाम (HeritagePassport) इम्पोर्ट
from vratyavani_core import (
    VratyaVaniRegistry,
    HeritagePassport,
    HeritagePillar,
    VerificationState
)


class AIAnalysisReport(BaseModel):
    primary_dialect: str
    classified_category: HeritagePillar
    extracted_entities: List[str]
    duplicate_match_percentage: float
    duplicate_risk_level: str
    suggested_tags: List[str]


class VratyaVaniAIPipeline:
    def __init__(self, registry: VratyaVaniRegistry):
        self.registry = registry

        # Indic बोली पहचान हेतु कीवर्ड डिक्शनरी
        self.dialect_markers = {
            "Bajjika": ["हमार", "तोहार", "बाटे", "कथि", "अपन", "गाछ", "पोखरा", "वैशाली", "मुज़फ़्फ़रपुर"],
            "Bhojpuri": ["रउआ", "का बा", "बानि", "होइ", "गइल", "गाँव", "मेला", "गंगा"],
            "Maithili": ["अहाँ", "छल", "गेल", "मिथिला", "हमार", "मधुबनी", "पावनी"],
            "Magahi": ["हथिन", "हलइ", "गेलई", "मगध", "पटना", "गया"]
        }

    def detect_dialect(self, text: str) -> str:
        """पाठ में शब्दों के आधार पर स्थानीय बोली की पहचान"""
        scores = {dialect: 0 for dialect in self.dialect_markers}
        lower_text = text.lower()

        for dialect, markers in self.dialect_markers.items():
            for word in markers:
                if word in lower_text:
                    scores[dialect] += 1

        best_dialect = max(scores, key=scores.get)
        return best_dialect if scores[best_dialect] > 0 else "Bajjika / Hindi"

    def classify_pillar(self, text: str) -> HeritagePillar:
        """पाठ के संदर्भ के आधार पर धरोहर की श्रेणी निर्धारित करना"""
        craft_words = ["कढ़ाई", "शिल्प", "कपड़ा", "सुजनी", "मिट्टी", "मूर्ति", "धागा", "craft"]
        ritual_words = ["पूजा", "मेला", "व्रत", "कांवर", "डक-बम", "अनुष्ठान", "ritual", "fasting"]
        lore_words = ["कथा", "कहानी", "बुजुर्ग", "गाथा", "मौखिक", "गीत", "lore"]

        lower = text.lower()
        if any(w in lower for w in craft_words):
            return HeritagePillar.INTANGIBLE_CRAFT
        if any(w in lower for w in ritual_words):
            return HeritagePillar.INTANGIBLE_RITUAL
        if any(w in lower for w in lore_words):
            return HeritagePillar.INTANGIBLE_ORAL_LORE

        return HeritagePillar.TANGIBLE_MONUMENT

    def check_duplicates(self, title: str, narrative: str) -> Dict[str, Any]:
        """रजिस्ट्री में पहले से मौजूद रिकॉर्ड्स से सिमेंटिक समानता जाँचना"""
        existing = self.registry.list_records()
        if not existing:
            return {"percentage": 0.0, "level": "LOW"}

        highest_match = 0.0
        words_new = set(re.findall(r'\w+', (title + " " + narrative).lower()))

        for record in existing:
            words_old = set(re.findall(r'\w+', (record.title + " " + record.oral_story_or_tradition).lower()))
            if not words_old or not words_new:
                continue
            intersection = words_new.intersection(words_old)
            similarity = (len(intersection) / len(words_new.union(words_old))) * 100.0
            if similarity > highest_match:
                highest_match = similarity

        risk_level = "HIGH" if highest_match > 60 else ("MODERATE" if highest_match > 30 else "LOW")
        return {"percentage": round(highest_match, 1), "level": risk_level}

    def process_field_submission(self, title: str, raw_audio_text: str) -> AIAnalysisReport:
        """सबमिशन का संपूर्ण AI विश्लेषण निष्पादित करना"""
        dialect = self.detect_dialect(raw_audio_text)
        pillar = self.classify_pillar(raw_audio_text)
        dup_info = self.check_duplicates(title, raw_audio_text)

        # बुनियादी एंटिटी निष्कर्षण
        entities = [w for w in re.findall(r'\b[A-Za-z\u0900-\u097F]{4,}\b', raw_audio_text)[:5]]

        return AIAnalysisReport(
            primary_dialect=dialect,
            classified_category=pillar,
            extracted_entities=entities,
            duplicate_match_percentage=dup_info["percentage"],
            duplicate_risk_level=dup_info["level"],
            suggested_tags=["LivingCulture", dialect, pillar.value]
        )