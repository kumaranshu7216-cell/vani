"""
====================================================================
Project: VratyaVani AI - Stage 1 & 2 Core Engine
File: vratyavani_core.py
Description: Structured Heritage Passport & In-Memory Registry Engine
Architectural Model: Place -> History -> Story -> People -> Tradition -> Evidence -> Risk
====================================================================
"""

import uuid
from datetime import datetime
from enum import Enum
from typing import Dict, List, Optional
from pydantic import BaseModel, Field


# --- Enums (Domain Definitions) ---
class HeritagePillar(str, Enum):
    """Dual-Pillar Architecture: Tangible vs Intangible Living Culture"""
    TANGIBLE_MONUMENT = "tangible_monument"
    TANGIBLE_SACRED_SITE = "tangible_sacred_site"
    INTANGIBLE_RITUAL = "intangible_ritual"
    INTANGIBLE_ORAL_LORE = "intangible_oral_lore"
    INTANGIBLE_CRAFT = "intangible_craft"


class VerificationState(str, Enum):
    """4-Tier Trust Lifecycle States"""
    SUBMITTED = "SUBMITTED"
    UNDER_REVIEW = "UNDER_REVIEW"
    EVIDENCE_CHECKED = "EVIDENCE_CHECKED"
    VERIFIED = "VERIFIED"
    REJECTED = "REJECTED"


class PreservationRisk(str, Enum):
    """Preservation Intelligence Scoring Levels"""
    LOW = "LOW"
    MODERATE = "MODERATE"
    HIGH = "HIGH"
    CRITICAL = "CRITICAL"


# --- Core Supporting Schemas ---
class GeoCoordinate(BaseModel):
    latitude: float
    longitude: float
    district: str
    state: str = "Bihar"
    specific_landmark: Optional[str] = None


class EvidenceFile(BaseModel):
    evidence_id: str = Field(default_factory=lambda: f"EVD-{uuid.uuid4().hex[:6].upper()}")
    media_type: str  # 'image', 'field_audio', 'historical_doc', 'video'
    media_url: str
    contributor_name: str
    notes: str
    uploaded_at: datetime = Field(default_factory=datetime.utcnow)


# --- Heritage Passport Model ---
class HeritagePassport(BaseModel):
    """
    VratyaVani Standardized Heritage Passport Record
    Preserves provenance, evidence trail, risk priority, and multilingual context.
    """
    heritage_id: str = Field(default_factory=lambda: f"VV-{uuid.uuid4().hex[:8].upper()}")
    title: str
    pillar: HeritagePillar
    location: GeoCoordinate
    primary_dialect: str = "Hindi"  # e.g., 'Bhojpuri', 'Maithili', 'Bajjika', 'Magahi'

    # Narrative Context
    historical_background: str
    oral_story_or_tradition: str
    associated_communities: List[str] = Field(default_factory=list)

    # Evidence & Media Records
    cover_image_url: Optional[str] = None
    audio_sample_url: Optional[str] = None
    evidence_trail: List[EvidenceFile] = Field(default_factory=list)

    # Trust & Verification Status
    verification_status: VerificationState = VerificationState.SUBMITTED
    provenance_source: str = "Community Submission"  # e.g., 'ASI Baseline', 'Community Field Lore'
    community_votes_authentic: int = 0
    community_votes_needs_evidence: int = 0

    # Preservation Intelligence
    risk_level: PreservationRisk = PreservationRisk.LOW
    risk_reasons: List[str] = Field(default_factory=list)
    suggested_action: Optional[str] = None

    # Timestamps
    created_at: datetime = Field(default_factory=datetime.utcnow)
    last_updated: datetime = Field(default_factory=datetime.utcnow)


# --- Registry & Storage Engine ---
class VratyaVaniRegistry:
    """Core in-memory repository implementing validation and query methods."""

    def __init__(self):
        self._store: Dict[str, HeritagePassport] = {}

    def submit_new_heritage(self, passport: HeritagePassport) -> HeritagePassport:
        """New submission enters the system at SUBMITTED status."""
        if passport.heritage_id in self._store:
            raise ValueError(f"Passport ID {passport.heritage_id} already exists.")
        passport.verification_status = VerificationState.SUBMITTED
        self._store[passport.heritage_id] = passport
        return passport

    def get_by_id(self, heritage_id: str) -> Optional[HeritagePassport]:
        return self._store.get(heritage_id)

    def list_records(self, status: Optional[VerificationState] = None) -> List[HeritagePassport]:
        if status:
            return [p for p in self._store.values() if p.verification_status == status]
        return list(self._store.values())

    def append_evidence(self, heritage_id: str, evidence: EvidenceFile) -> HeritagePassport:
        record = self.get_by_id(heritage_id)
        if not record:
            raise KeyError(f"Heritage ID '{heritage_id}' not found.")
        record.evidence_trail.append(evidence)
        record.last_updated = datetime.utcnow()
        return record

    def update_status(self, heritage_id: str, new_status: VerificationState) -> HeritagePassport:
        record = self.get_by_id(heritage_id)
        if not record:
            raise KeyError(f"Heritage ID '{heritage_id}' not found.")
        record.verification_status = new_status
        record.last_updated = datetime.utcnow()
        return record

    def cast_vote(self, heritage_id: str, vote_type: str) -> HeritagePassport:
        """Community voting poll: 'authentic' or 'needs_evidence'"""
        record = self.get_by_id(heritage_id)
        if not record:
            raise KeyError(f"Heritage ID '{heritage_id}' not found.")
        
        if vote_type == "authentic":
            record.community_votes_authentic += 1
        elif vote_type == "needs_evidence":
            record.community_votes_needs_evidence += 1
        else:
            raise ValueError("Vote type must be 'authentic' or 'needs_evidence'.")

        record.last_updated = datetime.utcnow()
        return record


# --- Self-Executing Test Harness (No external bugs) ---
if __name__ == "__main__":
    registry = VratyaVaniRegistry()

    # 1. Pilot Tangible Heritage (Kolhua Ashokan Pillar)
    kolhua_pillar = HeritagePassport(
        title="Kolhua Ashokan Pillar",
        pillar=HeritagePillar.TANGIBLE_MONUMENT,
        location=GeoCoordinate(
            latitude=25.9928,
            longitude=85.1256,
            district="Vaishali/Muzaffarpur",
            specific_landmark="Kolhua Archeological Enclosure"
        ),
        primary_dialect="Pali / Bajjika",
        historical_background="Polished sandstone monolith erected by Emperor Ashoka with an intact lion capital.",
        oral_story_or_tradition="Marks the location where Lord Buddha delivered his final sermon.",
        associated_communities=["Local Licensed Tour Guides", "Vaishali Heritage Caretakers"],
        provenance_source="ASI Baseline Record",
        cover_image_url="https://images.unsplash.com/photo-1590050752117-238cb0fb12b1",
        risk_level=PreservationRisk.LOW,
        suggested_action="Routine environmental monitoring and WebXR tourist interpretation."
    )
    kolhua_record = registry.submit_new_heritage(kolhua_pillar)
    registry.update_status(kolhua_record.heritage_id, VerificationState.VERIFIED)

    # 2. Pilot Intangible Heritage (Living Oral Tradition / Ritual)
    dak_bam_ritual = HeritagePassport(
        title="Kanwar Dak-Bam Living Tradition",
        pillar=HeritagePillar.INTANGIBLE_RITUAL,
        location=GeoCoordinate(
            latitude=26.1209,
            longitude=85.3647,
            district="Muzaffarpur",
            specific_landmark="Garib Sthan Route"
        ),
        primary_dialect="Bhojpuri / Bajjika",
        historical_background="Century-old unbroken fasting and non-stop pedestrian sacred journey during Shravan.",
        oral_story_or_tradition="Devotional songs, sacred chants, and barefoot endurance passed down orally without codified books.",
        associated_communities=["Dak-Bam Pilgrims", "Local Bhajan Mandalis"],
        provenance_source="Field Oral Submission",
        risk_level=PreservationRisk.HIGH,
        risk_reasons=["Oral chants lack digital audio recording", "Younger generation disconnected from native dialect lyrics"],
        suggested_action="Field audio recording of oral songs + expert linguistic review."
    )
    dak_bam_record = registry.submit_new_heritage(dak_bam_ritual)

    # 3. Add supporting evidence
    registry.append_evidence(
        dak_bam_record.heritage_id,
        EvidenceFile(
            media_type="field_audio",
            media_url="https://storage.vratyavani.ai/audio/dak_bam_chant_01.mp3",
            contributor_name="Dr. R. Mishra (Linguistic Researcher)",
            notes="Raw 48kHz recording of traditional 5-stanza prayer in Bajjika dialect."
        )
    )
    registry.cast_vote(dak_bam_record.heritage_id, "authentic")

    print(f"[*] Total Records Loaded: {len(registry.list_records())}")
    print(f"[*] Verified Monument: {kolhua_record.title} [{kolhua_record.verification_status.value}]")
    print(f"[*] Upcoming Tradition: {dak_bam_record.title} [{dak_bam_record.verification_status.value}]")
    print(f"[*] Evidence Items for '{dak_bam_record.title}': {len(dak_bam_record.evidence_trail)}")