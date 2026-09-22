"""
====================================================================
Project: VratyaVani AI - Central API Gateway
File: gateway.py
Complete Production Pipeline: Ingestion -> Passport -> Trust -> XR -> Risk -> Economy
====================================================================
"""

from typing import List, Optional, Dict, Any
from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

# कोर इंजनों से क्लास और डेटा मॉडल आयात
from vratyavani_core import (
    VratyaVaniRegistry,
    HeritagePassport,
    HeritagePillar,
    GeoCoordinate,
    EvidenceFile,
    VerificationState
)
from trust import VratyaVaniTrustEngine
from pipline import VratyaVaniAIPipeline
from exprience import VratyaVaniExperienceEngine, UserPersona
from risk import VratyaVaniRiskEngine

app = FastAPI(
    title="VratyaVani AI Core Gateway",
    description="Unified Heritage & Living Culture Engine REST API",
    version="2.0.0"
)

# क्रॉस-ओरिजिन रिक्वेस्ट अनुमति
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# सभी कोर इंजन आरंभ करना
registry = VratyaVaniRegistry()
trust_engine = VratyaVaniTrustEngine(registry)
ai_pipeline = VratyaVaniAIPipeline(registry)
experience_engine = VratyaVaniExperienceEngine(registry)
risk_engine = VratyaVaniRiskEngine(registry)


@app.on_event("startup")
def preload_pilot_records():
    # 1. मूर्त धरोहर पायलट (Kolhua)
    kolhua = HeritagePassport(
        heritage_id="VV-KOLHUA01",
        title="Kolhua Ashokan Pillar & Stupa",
        pillar=HeritagePillar.TANGIBLE_MONUMENT,
        location=GeoCoordinate(
            latitude=25.9928,
            longitude=85.1256,
            district="Vaishali",
            specific_landmark="Kolhua Complex"
        ),
        primary_dialect="Pali / Bajjika",
        historical_background="Monolithic polished sandstone pillar erected by Emperor Ashoka with an intact lion capital.",
        oral_story_or_tradition="Lord Buddha delivered his final sermon here; legend of monkeys offering honey.",
        associated_communities=["Local Licensed Tour Guides", "Vaishali Caretakers"],
        provenance_source="ASI Baseline Record",
        verification_status=VerificationState.VERIFIED,
        cover_image_url="https://images.unsplash.com/photo-1590050752117-238cb0fb12b1?auto=format&fit=crop&w=800&q=80"
    )
    registry.submit_new_heritage(kolhua)
    registry.update_status(kolhua.heritage_id, VerificationState.VERIFIED)

    # 2. जीवित संस्कृति पायलट (Kanwar Dak-Bam)
    dak_bam = HeritagePassport(
        heritage_id="VV-DAKBAM02",
        title="Kanwar Dak-Bam Sacred Living Tradition",
        pillar=HeritagePillar.INTANGIBLE_RITUAL,
        location=GeoCoordinate(
            latitude=26.1209,
            longitude=85.3647,
            district="Muzaffarpur",
            specific_landmark="Baba Garibnath Corridor"
        ),
        primary_dialect="Bhojpuri / Bajjika",
        historical_background="Century-old unbroken fasting and non-stop pedestrian sacred run during Shravan.",
        oral_story_or_tradition="Devotional songs and chants passed down purely orally without written canonical texts.",
        associated_communities=["Dak-Bam Pilgrims", "Local Bhajan Mandalis"],
        provenance_source="Field Oral Submission",
        verification_status=VerificationState.UNDER_REVIEW,
        cover_image_url="https://images.unsplash.com/photo-1544717305-2782549b5136?auto=format&fit=crop&w=800&q=80"
    )
    trust_engine.register_upcoming_heritage(dak_bam)
    trust_engine.cast_community_vote(dak_bam.heritage_id, "user_alpha", "authentic")
    trust_engine.cast_community_vote(dak_bam.heritage_id, "user_beta", "authentic")


# Pydantic मॉडल्स
class HeritageSubmissionRequest(BaseModel):
    title: str
    pillar: HeritagePillar
    latitude: float
    longitude: float
    district: str
    narrative_lore: str
    contributor_name: str
    audio_sample_url: Optional[str] = None
    image_url: Optional[str] = None


class VoteRequest(BaseModel):
    heritage_id: str
    user_id: str
    vote: str
    comment: Optional[str] = None


class AdminDecisionRequest(BaseModel):
    heritage_id: str
    action: str
    admin_name: str


# REST API रूट्स
@app.get("/api/health")
def health_check():
    return {"status": "ONLINE", "engine": "VratyaVani AI Core Gateway", "version": "2.0.0"}


@app.get("/api/heritage/verified")
def get_verified_heritage():
    records = registry.list_records(status=VerificationState.VERIFIED)
    return {"count": len(records), "data": records}


@app.get("/api/heritage/upcoming")
def get_upcoming_heritage():
    cards = trust_engine.get_verification_queue_for_admin()
    return {"count": len(cards), "data": cards}


@app.post("/api/heritage/submit")
def submit_heritage(req: HeritageSubmissionRequest):
    ai_report = ai_pipeline.process_field_submission(
        title=req.title,
        raw_audio_text=req.narrative_lore
    )

    passport = HeritagePassport(
        title=req.title,
        pillar=req.pillar,
        location=GeoCoordinate(
            latitude=req.latitude,
            longitude=req.longitude,
            district=req.district
        ),
        primary_dialect=ai_report.primary_dialect,
        historical_background=f"AI Ingestion: Classified as {ai_report.classified_category.value}.",
        oral_story_or_tradition=req.narrative_lore,
        associated_communities=[req.contributor_name],
        provenance_source=f"Citizen Field Record ({req.contributor_name})",
        cover_image_url=req.image_url or "https://images.unsplash.com/photo-1544717305-2782549b5136?auto=format&fit=crop&w=800&q=80"
    )

    registered = trust_engine.register_upcoming_heritage(passport)

    return {
        "success": True,
        "heritage_id": registered.heritage_id,
        "status": registered.verification_status,
        "ai_report": ai_report
    }


@app.post("/api/trust/vote")
def cast_community_vote(vote_req: VoteRequest):
    try:
        new_signal = trust_engine.cast_community_vote(
            heritage_id=vote_req.heritage_id,
            user_id=vote_req.user_id,
            vote=vote_req.vote,
            comment=vote_req.comment
        )
        return {"success": True, "heritage_id": vote_req.heritage_id, "updated_community_signal": f"{new_signal}%"}
    except KeyError:
        raise HTTPException(status_code=404, detail="Heritage ID not found")
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@app.post("/api/admin/resolve")
def admin_resolve_submission(dec: AdminDecisionRequest):
    try:
        resolved = trust_engine.admin_resolve(
            heritage_id=dec.heritage_id,
            action=dec.action,
            admin_name=dec.admin_name
        )
        return {"success": True, "heritage_id": resolved.heritage_id, "new_status": resolved.verification_status}
    except KeyError:
        raise HTTPException(status_code=404, detail="Heritage ID not found")


@app.get("/api/experience/webxr")
def get_webxr_experience(
    qr_token: str = Query(..., description="QR Token format: VV-QR-<ID>"),
    persona: UserPersona = Query(UserPersona.TOURIST)
):
    try:
        payload = experience_engine.launch_webxr_experience(qr_token=qr_token, persona=persona)
        return {"success": True, "experience_payload": payload}
    except KeyError:
        raise HTTPException(status_code=404, detail="Heritage associated with this QR code not found")


@app.get("/api/preservation/risk/{heritage_id}")
def assess_risk(heritage_id: str):
    try:
        report = risk_engine.evaluate_heritage_risk(heritage_id=heritage_id)
        return {"success": True, "risk_report": report}
    except KeyError:
        raise HTTPException(status_code=404, detail="Heritage ID not found")


# Phase 8: Artisan & Guide Economic Directory
@app.get("/api/heritage/{heritage_id}/artisans-guides")
def get_artisans_and_guides(heritage_id: str):
    directory = {
        "VV-KOLHUA01": {
            "artisans": [
                {
                    "name": "रामबाबू शर्मा (हस्तशिल्प कलाकार)",
                    "craft": "टेराकोटा एवं पत्थर नक्काशी (वैशाली प्रतिकृति)",
                    "contact": "+91-9876543210",
                    "location": "बसाढ़ ग्राम क्लस्टर, वैशाली"
                }
            ],
            "guides": [
                {
                    "name": "राजेश कुमार सिंह",
                    "badge_no": "ASI-LIC-BR-402",
                    "languages": ["बज्जिका", "हिंदी", "English"],
                    "rating": "4.9 ★",
                    "speciality": "बौद्ध इतिहास एवं अशोकन अभिलेख"
                }
            ]
        },
        "VV-DAKBAM02": {
            "artisans": [
                {
                    "name": "मुज़फ़्फ़रपुर कांवर शिल्पी संघ",
                    "craft": "हस्तनिर्मित काँवर व पीतल पूजन पात्र",
                    "contact": "+91-9876543211",
                    "location": "पुरानी बाज़ार, मुज़फ़्फ़रपुर"
                }
            ],
            "guides": [
                {
                    "name": "संजय शास्त्री",
                    "badge_no": "EXP-TR-788",
                    "languages": ["भोजपुरी", "हिंदी"],
                    "rating": "4.8 ★",
                    "speciality": "श्रावणी मेला एवं मौखिक भजन परंपरा"
                }
            ]
        }
    }

    data = directory.get(heritage_id, {
        "artisans": [
            {
                "name": "महिला विकास स्वावलंबी समिति",
                "craft": "सुजनी कढ़ाई एवं पारंपरिक वस्त्र हस्तशिल्प",
                "contact": "+91-9431200000",
                "location": "कांटी क्लस्टर, मुज़फ़्फ़रपुर"
            }
        ],
        "guides": [
            {
                "name": "अमित कुमार (कम्युनिटी हेरिटेज वाकर)",
                "badge_no": "COMM-GUIDE-104",
                "languages": ["बज्जिका", "हिंदी"],
                "rating": "4.7 ★",
                "speciality": "मौखिक इतिहास व ग्रामीण लोक कला"
            }
        ]
    })

    return {"success": True, "heritage_id": heritage_id, "data": data}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=8000)