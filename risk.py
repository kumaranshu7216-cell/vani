"""
====================================================================
Project: VratyaVani AI - Stage 7: Preservation Intelligence & Risk Engine
File: risk_engine.py
Description: Cultural Heritage Risk Scoring, Vulnerability Analysis & Action Matrix
Flow: Heritage Passport -> Factor Weighting -> Risk Score -> Action Directive
====================================================================
"""

from typing import Dict, List, Optional
from datetime import datetime
from pydantic import BaseModel, Field

# चरण 1 के कोर मॉड्यूल से क्लासेज इम्पोर्ट करें
from vratyavani_core import (
    VratyaVaniRegistry,
    HeritagePassport,
    PreservationRisk,
    HeritagePillar
)


class RiskAssessmentReport(BaseModel):
    heritage_id: str
    title: str
    composite_risk_score: float  # 0.0 से 100.0 तक
    assigned_risk_level: PreservationRisk
    identified_vulnerabilities: List[str]
    immediate_action_plan: str
    target_stakeholders: List[str]
    evaluated_at: datetime = Field(default_factory=datetime.utcnow)


class VratyaVaniRiskEngine:
    """
    Preservation Intelligence Engine
    Scoring Criteria (Measurable Indicators):
    1. Documentation Deficit (प्रलेखन और साक्ष्य की कमी)
    2. Generational / Tradition Continuity (युवा पीढ़ी का जुड़ाव / अभ्यास की आवृत्ति)
    3. Exposure & Physical Vulnerability (पर्यावरणीय क्षरण या अतिक्रमण)
    4. Community Engagement Signal (स्थानीय समुदाय की सक्रिय भागीदारी)
    """

    def __init__(self, registry: VratyaVaniRegistry):
        self.registry = registry

    def evaluate_heritage_risk(
        self,
        heritage_id: str,
        is_active_practice: bool = True,
        native_speakers_declining: bool = False,
        physical_damage_reported: bool = False,
        has_academic_citations: bool = False
    ) -> RiskAssessmentReport:
        """धरोहर का बहु-कारक जोखिम विश्लेषण (Multi-Factor Risk Assessment)"""
        record = self.registry.get_by_id(heritage_id)
        if not record:
            raise KeyError(f"Heritage ID '{heritage_id}' not found.")

        score = 0.0
        vulnerabilities = []

        # 1. प्रलेखन विश्लेषण (Documentation & Evidence Depth)
        evidence_count = len(record.evidence_trail)
        if evidence_count == 0:
            score += 30.0
            vulnerabilities.append("गंभीर प्रलेखन कमी: कोई डिजिटल या फील्ड साक्ष्य संलग्न नहीं है।")
        elif evidence_count < 2:
            score += 15.0
            vulnerabilities.append("सीमित साक्ष्य: स्वतंत्र अभिलेखीय पुष्टि की आवश्यकता है।")

        # 2. अमूर्त संस्कृति का निरंतरता कारक (Tradition Continuity)
        if record.pillar in [HeritagePillar.INTANGIBLE_RITUAL, HeritagePillar.INTANGIBLE_ORAL_LORE, HeritagePillar.INTANGIBLE_CRAFT]:
            if not is_active_practice:
                score += 35.0
                vulnerabilities.append("निष्क्रिय परंपरा: अनुष्ठान/कला का दैनिक या वार्षिक अभ्यास बंद होने की कगार पर है।")
            if native_speakers_declining:
                score += 20.0
                vulnerabilities.append("भाषाई संकट: मूल बोली/गीतों के वक्ताओं की संख्या में तीव्र गिरावट।")
        else:
            # 3. मूर्त स्मारकों का भौतिक विश्लेषण (Physical Exposure)
            if physical_damage_reported:
                score += 35.0
                vulnerabilities.append("भौतिक क्षरण: संरचनात्मक क्षति या पर्यावरणीय अनावरण की सूचना।")

        # 4. शैक्षणिक और सामुदायिक सत्यापन की कमी
        if not has_academic_citations and record.provenance_source == "Community Submission":
            score += 15.0
            vulnerabilities.append("अपुष्ट स्रोत: ऐतिहासिक या पुरातात्विक संदर्भों से मिलान शेष है।")

        # स्कोर का सामान्यीकरण (Max 100.0)
        final_score = min(round(score, 2), 100.0)

        # जोखिम स्तर का निर्धारण
        if final_score >= 70.0:
            level = PreservationRisk.CRITICAL
            action = "तत्काल फील्ड दस्तावेजीकरण, उच्च-रिज़ॉल्यूशन ऑडियो/3D स्कैनिंग, और राज्य संस्कृति विभाग को अलर्ट।"
            stakeholders = ["State Heritage Directorate", "Linguistic Experts", "Local Administration"]
        elif final_score >= 45.0:
            level = PreservationRisk.HIGH
            action = "स्थानीय बुजुर्गों के साथ फील्ड वर्कशॉप, मौखिक गीतों की रिकॉर्डिंग, और कम्युनिटी आर्काइव निर्माण।"
            stakeholders = ["Local Folklorists", "NGO Partners", "District Youth Clubs"]
        elif final_score >= 20.0:
            level = PreservationRisk.MODERATE
            action = "नियमित डिजिटल अपडेट, WebXR टूरिज्म गाइड का निर्माण, और कारीगर आजीविका से जुड़ाव।"
            stakeholders = ["Tourism Board", "Artisan Guilds", "Local Guides"]
        else:
            level = PreservationRisk.LOW
            action = "सत्यापित स्थिति बनाए रखना, आवधिक समीक्षा और शैक्षिक आउटरीच।"
            stakeholders = ["Educational Institutions", "Tourists", "Researchers"]

        # कोर रिकॉर्ड को अपडेट करना
        record.risk_level = level
        record.risk_reasons = vulnerabilities
        record.suggested_action = action
        record.last_updated = datetime.utcnow()

        return RiskAssessmentReport(
            heritage_id=record.heritage_id,
            title=record.title,
            composite_risk_score=final_score,
            assigned_risk_level=level,
            identified_vulnerabilities=vulnerabilities,
            immediate_action_plan=action,
            target_stakeholders=stakeholders
        )


# --- सेल्फ-टेस्ट और वर्कफ़्लो रनर ---
if __name__ == "__main__":
    from vratyavani_core import GeoCoordinate, HeritagePillar, VerificationState

    registry = VratyaVaniRegistry()
    risk_engine = VratyaVaniRiskEngine(registry)

    # 1. परीक्षण हेरिटेज: लुप्तप्राय लोकगाथा (Intangible Oral Lore)
    endangered_lore = HeritagePassport(
        title="Vaishali Champaran Migrant Lore & Work Songs",
        pillar=HeritagePillar.INTANGIBLE_ORAL_LORE,
        location=GeoCoordinate(latitude=26.11, longitude=85.15, district="Vaishali"),
        primary_dialect="Bajjika",
        historical_background="Century-old agricultural harvesting songs recounting historic river floods.",
        oral_story_or_tradition="Sang only by senior village elders during paddy plantation.",
        provenance_source="Community Submission"
    )
    registry.submit_new_heritage(endangered_lore)

    # जोखिम मूल्यांकन चलाएँ
    assessment = risk_engine.evaluate_heritage_risk(
        heritage_id=endangered_lore.heritage_id,
        is_active_practice=False,             # अब नियमित अभ्यास में नहीं है
        native_speakers_declining=True,      # वक्ताओं की संख्या घट रही है
        has_academic_citations=False         # कोई लिखित संदर्भ नहीं
    )

    print("\n================ PRESERVATION INTELLIGENCE REPORT ================")
    print(f"Heritage: {assessment.title} [ID: {assessment.heritage_id}]")
    print(f"Composite Risk Score: {assessment.composite_risk_score} / 100")
    print(f"Preservation Priority: {assessment.assigned_risk_level.value.upper()}")
    print("\nIdentified Vulnerabilities:")
    for v in assessment.identified_vulnerabilities:
        print(f"  - {v}")
    print(f"\nActionable Roadmap:\n  {assessment.immediate_action_plan}")
    print(f"Involved Stakeholders: {', '.join(assessment.target_stakeholders)}")
    print("==================================================================")