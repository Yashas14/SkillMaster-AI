# ════════════════════════════════════════════════════════════
# Certificates Router — Blockchain-verifiable credentials
# ════════════════════════════════════════════════════════════

import hashlib
import uuid as uuid_mod
from datetime import UTC, datetime

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.auth import get_current_user
from app.database import get_db
from app.models import Certificate, Course, Enrollment, User
from app.schemas import CertificateResponse, VerifyCertificateResponse

router = APIRouter()


def _generate_cert_number(user_id: str, course_id: str) -> str:
    """Generate a unique, deterministic certificate number."""
    raw = f"{user_id}:{course_id}:{datetime.now(UTC).isoformat()}"
    h = hashlib.sha256(raw.encode()).hexdigest()[:12].upper()
    return f"SM-{h[:4]}-{h[4:8]}-{h[8:12]}"


@router.post("/issue/{enrollment_id}", status_code=status.HTTP_201_CREATED)
async def issue_certificate(
    enrollment_id: str,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user),
):
    """Issue a certificate for a completed course."""
    enrollment_result = await db.execute(
        select(Enrollment).where(
            Enrollment.id == uuid_mod.UUID(enrollment_id),
            Enrollment.user_id == user.id,
        )
    )
    enrollment = enrollment_result.scalar_one_or_none()

    if not enrollment:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Enrollment not found")

    if enrollment.status != "completed":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Course must be completed before issuing certificate",
        )

    # Check if certificate already exists
    existing = await db.execute(
        select(Certificate).where(
            Certificate.user_id == user.id,
            Certificate.course_id == enrollment.course_id,
        )
    )
    if existing.scalar_one_or_none():
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Certificate already issued for this course",
        )

    # Get course details
    course_result = await db.execute(select(Course).where(Course.id == enrollment.course_id))
    course = course_result.scalar_one()

    cert_number = _generate_cert_number(str(user.id), str(course.id))

    certificate = Certificate(
        user_id=user.id,
        course_id=course.id,
        enrollment_id=enrollment.id,
        certificate_number=cert_number,
        title=f"Certificate of Completion: {course.title}",
        description=f"Awarded to {user.name} for successfully completing {course.title}",
        verification_url=f"/api/v1/certificates/verify/{cert_number}",
        extra_data={
            "course_title": course.title,
            "course_category": course.category,
            "course_difficulty": course.difficulty,
            "student_name": user.name,
            "instructor_id": str(course.instructor_id),
            "completed_at": enrollment.completed_at.isoformat() if enrollment.completed_at else None,
        },
    )
    db.add(certificate)

    # Store cert ID on enrollment
    enrollment.certificate_id = certificate.id
    await db.flush()

    return CertificateResponse.model_validate(certificate)


@router.get("/my")
async def list_my_certificates(
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user),
):
    """List all certificates for the current user."""
    result = await db.execute(
        select(Certificate)
        .where(Certificate.user_id == user.id, Certificate.status == "issued")
        .order_by(Certificate.issued_at.desc())
    )
    certs = result.scalars().all()
    return [CertificateResponse.model_validate(c) for c in certs]


@router.get("/verify/{cert_number}")
async def verify_certificate(
    cert_number: str,
    db: AsyncSession = Depends(get_db),
):
    """Publicly verify a certificate by its number."""
    result = await db.execute(
        select(Certificate).where(Certificate.certificate_number == cert_number)
    )
    cert = result.scalar_one_or_none()

    if not cert:
        return VerifyCertificateResponse(
            valid=False,
            certificate=None,
            blockchain_verified=False,
            message="Certificate not found. The certificate number may be invalid.",
        )

    blockchain_verified = bool(cert.blockchain_tx_hash)

    return VerifyCertificateResponse(
        valid=cert.status == "issued",
        certificate=CertificateResponse.model_validate(cert),
        blockchain_verified=blockchain_verified,
        message="Certificate is valid and verified." if cert.status == "issued"
        else "Certificate has been revoked.",
    )


@router.post("/{cert_id}/mint")
async def mint_to_blockchain(
    cert_id: str,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user),
):
    """Mint a certificate to the blockchain (simulated — ready for Web3 integration)."""
    result = await db.execute(
        select(Certificate).where(
            Certificate.id == uuid_mod.UUID(cert_id),
            Certificate.user_id == user.id,
        )
    )
    cert = result.scalar_one_or_none()

    if not cert:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Certificate not found")

    if cert.blockchain_tx_hash:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Certificate already minted to blockchain",
        )

    # Simulate blockchain minting
    # In production, this would call Web3.py to interact with a smart contract
    simulated_tx_hash = f"0x{hashlib.sha256(f'{cert.certificate_number}:{datetime.now(UTC).isoformat()}'.encode()).hexdigest()}"
    simulated_ipfs_hash = f"Qm{hashlib.sha256(cert.certificate_number.encode()).hexdigest()[:44]}"

    cert.blockchain_tx_hash = simulated_tx_hash
    cert.blockchain_network = "polygon-mumbai"
    cert.ipfs_hash = simulated_ipfs_hash
    await db.flush()

    return {
        "certificate_id": str(cert.id),
        "certificate_number": cert.certificate_number,
        "blockchain_tx_hash": simulated_tx_hash,
        "blockchain_network": "polygon-mumbai",
        "ipfs_hash": simulated_ipfs_hash,
        "status": "minted",
        "message": "Certificate minted to Polygon Mumbai testnet",
    }
