"""
====================================================================
Project: VratyaVani AI - Stage 6: Ground Experience & WebXR Engine
File: experience_engine.py
Description: QR Ingestion, WebXR 360 Scene Config, Persona-Driven AI & Explainable AI
====================================================================
"""

from enum import Enum
from typing import Dict, Any, Optional
from pydantic import BaseModel, Field

# चरण 1 के कोर मॉड्यूल से क्लासेज इम्पोर्ट करें
from vratyavani_core import (
    VratyaVaniRegistry,
    HeritagePassport,
    VerificationState
)


class UserPersona(str, Enum):
    CHILD = "child"              # सरल भाषा, रोचक कहानी और एनिमेशन
    STUDENT = "student"          # कालक्रम, तथ्य, इतिहास और परीक्षा उपयोगी नोट्स
    TOURIST = "tourist"          # त्वरित अनुभव, दर्शनीय स्थल और व्यावहारिक टिप्स
    RESEARCHER = "researcher"    # गहरा संदर्भ, स्रोत, साक्ष्य और अभिलेखीय विवरण


class WebXRScenePayload(BaseModel):
    heritage_id: str
    title: str
    target_dialect: str
    selected_persona: UserPersona
    audio_narrative_script: str
    visual_scene_type: str       # '360_photosphere', '3d_mesh_reconstruction'
    scene_media_url: str
    explainable_ai_source: str   # 'Why this story?' स्रोत सत्यापन
    local_artisan_connection: Optional[str] = None
    offline_cache_enabled: bool = True


class VratyaVaniExperienceEngine:
    """
    VratyaVani Ground Experience Engine
    - Handles physical on-site QR scans
    - Formats WebXR 360-degree interactive spaces
    - Dynamically tailors AI narratives based on user persona
    - Implements Explainable AI ("Why this story?")
    """

    def __init__(self, registry: VratyaVaniRegistry):
        self.registry = registry

    def resolve_qr_code(self, qr_token: str) -> Optional[HeritagePassport]:
        """
        भौतिक स्थल पर लगे QR कोड को स्कैन करके हेरिटेज रिकॉर्ड निकालना।
        प्रारूप: 'VV-QR-<HERITAGE_ID>'
        """
        heritage_id = qr_token.replace("VV-QR-", "").strip()
        record = self.registry.get_by_id(heritage_id)
        return record

    def generate_persona_narrative(self, passport: HeritagePassport, persona: UserPersona) -> Dict[str, str]:
        """
        पर्सोना के आधार पर अलग-अलग कहानी और 'Why this story?' उद्धरण तैयार करना।
        """
        title = passport.title
        history = passport.historical_background
        oral_lore = passport.oral_story_or_tradition

        if persona == UserPersona.CHILD:
            script = (
                f"नमस्ते छोटे दोस्त! क्या आप जानते हैं? यह जो {title} है, "
                f"यह बहुत पुरानी और जादुई जगह है! {oral_lore} "
                f"इसे प्राचीन राजाओं और संतों ने बहुत प्यार से बनाया था!"
            )
            why_story = f"स्रोत: स्थानीय लोककथा एवं सचित्र बाल गाथा (मौखिक परंपरा आधारित)।"

        elif persona == UserPersona.STUDENT:
            script = (
                f"ऐतिहासिक अध्ययन मॉड्यूल: {title}। "
                f"ऐतिहासिक संदर्भ: {history} "
                f"यह स्थल प्राचीन भारतीय इतिहास, वास्तुकला और मौर्य/पाल काल के अध्ययन के लिए महत्वपूर्ण है। "
                f"प्रमुख बिंदु: {oral_lore}"
            )
            why_story = f"स्रोत: {passport.provenance_source} + ऐतिहासिक अभिलेखीय साक्ष्य।"

        elif persona == UserPersona.RESEARCHER:
            evidence_count = len(passport.evidence_trail)
            script = (
                f"अभिलेखीय विश्लेषण: {title} [ID: {passport.heritage_id}]। "
                f"प्राथमिक पुरातात्विक पृष्ठभूमि: {history}। "
                f"प्रलेखित जीवित मौखिक परंपरा: {oral_lore}। "
                f"सत्यापित साक्ष्य रिकॉर्ड्स: {evidence_count} फ़ाइलें संलग्न। "
                f"मूल भाषा/बोली: {passport.primary_dialect}।"
            )
            why_story = (
                f"स्रोत: {passport.provenance_source}। "
                f"सत्यापन स्थिति: {passport.verification_status.value} (4-Tier Trust Engine Verified)।"
            )

        else:  # TOURIST (डिफ़ॉल्ट)
            script = (
                f"स्वागत है! आप इस समय {title} पर खड़े हैं। "
                f"{history} यहां आने पर आपको स्थानीय संस्कृति का जीवंत अनुभव मिलेगा: {oral_lore} "
                f"पास के स्थानीय कलाकारों द्वारा बनाई गई कलाकृतियों को देखना न भूलें!"
            )
            why_story = f"स्रोत: भारतीय पुरातत्व सर्वेक्षण (ASI) बेसलाइन एवं सत्यापित स्थानीय गाइड रिकॉर्ड।"

        return {
            "narrative_script": script,
            "explainable_source": why_story
        }

    def launch_webxr_experience(
        self,
        qr_token: str,
        persona: UserPersona = UserPersona.TOURIST,
        preferred_dialect: str = "Bhojpuri"
    ) -> WebXRScenePayload:
        """
        WebXR 360° व्यू और ऑडियो गाइड का पेलोड तैयार करना।
        """
        record = self.resolve_qr_code(qr_token)
        if not record:
            raise KeyError(f"QR कोड '{qr_token}' से जुड़ी कोई धरोहर नहीं मिली।")

        narrative_pack = self.generate_persona_narrative(record, persona)

        # 360 व्यू या 3D मेश मॉडल का चयन
        scene_url = record.cover_image_url or "https://vratyavani.ai/webxr/default_360_sphere.jpg"

        return WebXRScenePayload(
            heritage_id=record.heritage_id,
            title=record.title,
            target_dialect=preferred_dialect,
            selected_persona=persona,
            audio_narrative_script=narrative_pack["narrative_script"],
            visual_scene_type="360_photosphere",
            scene_media_url=scene_url,
            explainable_ai_source=narrative_pack["explainable_source"],
            local_artisan_connection="वैशाली हस्तशिल्प एवं मंजूषा/सुजनी क्लस्टर से सीधा संपर्क",
            offline_cache_enabled=True
        )


# --- सेल्फ-टेस्ट और वर्कफ़्लो रनर ---
if __name__ == "__main__":
    from vratyavani_core import GeoCoordinate, HeritagePillar

    registry = VratyaVaniRegistry()
    experience_engine = VratyaVaniExperienceEngine(registry)

    # 1. सत्यापित धरोहर को डेटाबेस में लोड करें
    kolhua_pillar = HeritagePassport(
        heritage_id="VV-KOLHUA01",
        title="Kolhua Ashokan Pillar & Stupa",
        pillar=HeritagePillar.TANGIBLE_MONUMENT,
        location=GeoCoordinate(latitude=25.9928, longitude=85.1256, district="Vaishali"),
        primary_dialect="Pali / Bajjika",
        historical_background="Sandstone monolith erected by Emperor Ashoka with polished finish and inverted lotus capital.",
        oral_story_or_tradition="Monkeys offered honey to Gautama Buddha at this sacred spot.",
        provenance_source="ASI Baseline Record",
        verification_status=VerificationState.VERIFIED,
        cover_image_url="https://images.unsplash.com/photo-1590050752117-238cb0fb12b1"
    )
    registry.submit_new_heritage(kolhua_pillar)
    registry.update_status("VV-KOLHUA01", VerificationState.VERIFIED)

    # 2. ऑन-साइट QR स्कैन का अनुकरण (Simulation)
    test_qr_code = "VV-QR-VV-KOLHUA01"
    print(f"[*] QR Code Scanned at physical site: {test_qr_code}")

    # 3. Persona 1: Child Experience
    child_exp = experience_engine.launch_webxr_experience(test_qr_code, persona=UserPersona.CHILD)
    print("\n--- [PERSONA: CHILD] ---")
    print(f"Script: {child_exp.audio_narrative_script}")
    print(f"Explainable AI: {child_exp.explainable_ai_source}")

    # 4. Persona 2: Researcher Experience
    researcher_exp = experience_engine.launch_webxr_experience(test_qr_code, persona=UserPersona.RESEARCHER)
    print("\n--- [PERSONA: RESEARCHER] ---")
    print(f"Script: {researcher_exp.audio_narrative_script}")
    print(f"Explainable AI: {researcher_exp.explainable_ai_source}")
    print(f"Artisan/Economy Node: {researcher_exp.local_artisan_connection}")