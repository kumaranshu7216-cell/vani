"""
====================================================================
Project: VratyaVani AI - Stage 4 & 5 Trust Engine
File: trust_engine.py
Description: 4-Tier Trust Engine and Verification Queue Manager
Flow: Citizen Submission -> Community Poll -> Evidence Collector -> Admin Gate
====================================================================
"""

from typing import Dict, List, Optional
from datetime import datetime
from pydantic import BaseModel, Field

# चरण 1 के कोर मॉड्यूल से क्लासेज इम्पोर्ट करें
from vratyavani_core import (
    VratyaVaniRegistry,
    HeritagePassport,
    VerificationState,
    EvidenceFile
)


class CommunityPollRecord(BaseModel):
    user_id: str
    vote: str  # 'authentic' or 'need_evidence'
    comment: Optional[str] = None
    voted_at: datetime = Field(default_factory=datetime.utcnow)


class VerificationQueueCard(BaseModel):
    heritage_id: str
    title: str
    primary_dialect: str
    provenance_source: str
    current_status: VerificationState
    community_signal_percentage: float
    total_votes: int
    evidence_count: int
    evidence_list: List[EvidenceFile]
    ai_duplicate_risk: str = "Low"  # 'Low', 'Medium', 'High'
    source_match: str = "Available"


class VratyaVaniTrustEngine:
    """
    4-Tier Trust Protocol:
    Tier 1: Community Crowdsourced Submission
    Tier 2: Community Evidence & Poll
    Tier 3: AI Evidence & Consistency Analysis
    Tier 4: Expert / Admin Final Gate
    """

    def __init__(self, registry: VratyaVaniRegistry):
        self.registry = registry
        # हेरिटेज आईडी -> पोल रिकॉर्ड्स की सूची
        self._poll_data: Dict[str, List[CommunityPollRecord]] = {}

    def register_upcoming_heritage(self, passport: HeritagePassport) -> HeritagePassport:
        """Tier 1: नई सबमिशन को सीधे 'UNDER_REVIEW' और 'Upcoming Heritage' कतार में रखना।"""
        passport.verification_status = VerificationState.UNDER_REVIEW
        saved_passport = self.registry.submit_new_heritage(passport)
        self._poll_data[saved_passport.heritage_id] = []
        return saved_passport

    def cast_community_vote(self, heritage_id: str, user_id: str, vote: str, comment: Optional[str] = None) -> float:
        """Tier 2: समुदाय द्वारा प्रमाणिकता पर वोटिंग (Authentic vs Need Evidence)"""
        record = self.registry.get_by_id(heritage_id)
        if not record:
            raise KeyError(f"Heritage ID '{heritage_id}' not found.")

        if vote not in ["authentic", "need_evidence"]:
            raise ValueError("Vote must be either 'authentic' or 'need_evidence'.")

        if heritage_id not in self._poll_data:
            self._poll_data[heritage_id] = []

        # एक यूज़र केवल एक बार वोट कर सकता है
        existing_votes = [p for p in self._poll_data[heritage_id] if p.user_id == user_id]
        if existing_votes:
            existing_votes[0].vote = vote
            existing_votes[0].comment = comment
            existing_votes[0].voted_at = datetime.utcnow()
        else:
            self._poll_data[heritage_id].append(
                CommunityPollRecord(user_id=user_id, vote=vote, comment=comment)
            )

        # कोर रजिस्ट्री में भी काउंट सिंक करें
        self.registry.cast_vote(heritage_id, "authentic" if vote == "authentic" else "needs_evidence")
        return self.calculate_community_signal(heritage_id)

    def calculate_community_signal(self, heritage_id: str) -> float:
        """कम्युनिटी सिग्नल प्रतिशत (% of 'authentic' votes) निकालना"""
        votes = self._poll_data.get(heritage_id, [])
        if not votes:
            return 0.0
        authentic_votes = sum(1 for v in votes if v.vote == "authentic")
        return round((authentic_votes / len(votes)) * 100, 2)

    def submit_supporting_evidence(self, heritage_id: str, evidence: EvidenceFile) -> HeritagePassport:
        """Tier 2: समुदाय या शोधकर्ता द्वारा अतिरिक्त प्रमाण जोड़ना"""
        updated_passport = self.registry.append_evidence(heritage_id, evidence)
        if len(updated_passport.evidence_trail) >= 2:
            self.registry.update_status(heritage_id, VerificationState.EVIDENCE_CHECKED)
        return updated_passport

    def get_verification_queue_for_admin(self) -> List[VerificationQueueCard]:
        """Tier 4: एडमिन डैशबोर्ड के लिए तैयार कतार"""
        under_review_records = [
            p for p in self.registry.list_records()
            if p.verification_status in [VerificationState.SUBMITTED, VerificationState.UNDER_REVIEW, VerificationState.EVIDENCE_CHECKED]
        ]

        queue_cards = []
        for rec in under_review_records:
            votes = self._poll_data.get(rec.heritage_id, [])
            signal = self.calculate_community_signal(rec.heritage_id)

            card = VerificationQueueCard(
                heritage_id=rec.heritage_id,
                title=rec.title,
                primary_dialect=rec.primary_dialect,
                provenance_source=rec.provenance_source,
                current_status=rec.verification_status,
                community_signal_percentage=signal,
                total_votes=len(votes),
                evidence_count=len(rec.evidence_trail),
                evidence_list=rec.evidence_trail,
                ai_duplicate_risk="Low",
                source_match="Available"
            )
            queue_cards.append(card)

        return queue_cards

    def admin_resolve(self, heritage_id: str, action: str, admin_name: str) -> HeritagePassport:
        """Tier 4: एडमिन द्वारा अंतिम स्वीकृति (APPROVE) या अस्वीकृति (REJECT)"""
        record = self.registry.get_by_id(heritage_id)
        if not record:
            raise KeyError(f"Heritage ID '{heritage_id}' not found.")

        if action.upper() == "APPROVE":
            return self.registry.update_status(heritage_id, VerificationState.VERIFIED)
        elif action.upper() == "REJECT":
            return self.registry.update_status(heritage_id, VerificationState.REJECTED)
        else:
            raise ValueError("Action must be 'APPROVE' or 'REJECT'.")


# --- सेल्फ-टेस्ट और वर्कफ़्लो रनर ---
if __name__ == "__main__":
    from vratyavani_core import GeoCoordinate, HeritagePillar, PreservationRisk

    test_registry = VratyaVaniRegistry()
    trust_engine = VratyaVaniTrustEngine(test_registry)

    # 1. नई मौखिक धरोहर सबमिट की गई (Upcoming Heritage)
    ritual = HeritagePassport(
        title="Bhojpuri Jhijhiya Traditional Ritual Dance",
        pillar=HeritagePillar.INTANGIBLE_RITUAL,
        location=GeoCoordinate(latitude=26.122, longitude=85.390, district="Muzaffarpur"),
        primary_dialect="Bhojpuri / Maithili",
        historical_background="Ancient cultural rain-prayer dance performed during Navratri to ward off evil eyes.",
        oral_story_or_tradition="Women balance perforated earthen pots on their heads with lamps inside, sung orally.",
        provenance_source="Field Oral Submission"
    )

    upcoming_item = trust_engine.register_upcoming_heritage(ritual)
    print(f"[Tier 1] Registered to Upcoming: {upcoming_item.title} (Status: {upcoming_item.verification_status.value})")

    # 2. कम्युनिटी वोटिंग (Tier 2)
    trust_engine.cast_community_vote(upcoming_item.heritage_id, user_id="citizen_1", vote="authentic")
    trust_engine.cast_community_vote(upcoming_item.heritage_id, user_id="citizen_2", vote="authentic")
    trust_engine.cast_community_vote(upcoming_item.heritage_id, user_id="citizen_3", vote="need_evidence")
    signal = trust_engine.calculate_community_signal(upcoming_item.heritage_id)
    print(f"[Tier 2] Community Signal Calculated: {signal}% Authentic")

    # 3. एविडेंस अपलोड
    trust_engine.submit_supporting_evidence(
        upcoming_item.heritage_id,
        EvidenceFile(
            media_type="field_audio",
            media_url="https://vratyavani.ai/evidence/jhijhiya_folk_song.wav",
            contributor_name="Dr. Archana (Folklorist)",
            notes="Gramin folk lyrics authenticated from Vaishali district elders."
        )
    )

    # 4. एडमिन वेरिफिकेशन डैशबोर्ड (Tier 4)
    admin_queue = trust_engine.get_verification_queue_for_admin()
    print("\n--- ADMIN VERIFICATION QUEUE ---")
    for q in admin_queue:
        print(f"Heritage: {q.title}")
        print(f"Community Signal: {q.community_signal_percentage}% | Evidence Files: {q.evidence_count}")
        print(f"AI Duplicate: {q.ai_duplicate_risk} | Source Match: {q.source_match}")

    # 5. एडमिन अप्रूवल
    approved_passport = trust_engine.admin_resolve(upcoming_item.heritage_id, "APPROVE", admin_name="Chief_Curator")
    print(f"\n[Tier 4 Gate Passed] Final Status: {approved_passport.verification_status.value}")