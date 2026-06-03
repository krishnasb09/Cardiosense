import io

from fastapi import APIRouter, Depends
from fastapi.responses import StreamingResponse
from reportlab.lib import colors
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.platypus import Paragraph, SimpleDocTemplate, Spacer, Table, TableStyle

from backend.models.schemas import AuthUser, ReportRequest
from backend.utils.security import require_role

router = APIRouter()


@router.post("/pdf")
async def generate_pdf(
    payload: ReportRequest,
    user: AuthUser = Depends(require_role("doctor", "admin")),
):
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=letter, rightMargin=36, leftMargin=36, topMargin=36, bottomMargin=36)
    styles = getSampleStyleSheet()
    elements = [
        Paragraph("CardioSense CAD Prediction Report", styles["Title"]),
        Spacer(1, 12),
        Paragraph(f"Patient: {payload.patient.patient_name}", styles["Heading2"]),
        Paragraph(f"Doctor: {payload.doctor_name}", styles["Normal"]),
        Paragraph(f"Risk Level: {payload.prediction.status}", styles["Heading3"]),
        Paragraph(f"Risk Percentage: {payload.prediction.risk_percentage}%", styles["Normal"]),
        Paragraph(f"Confidence Score: {payload.prediction.confidence_score}%", styles["Normal"]),
        Spacer(1, 12),
    ]

    vitals = [["Clinical Field", "Value"]]
    for key, value in payload.patient.model_dump().items():
        if key not in {"doctor_notes"}:
            vitals.append([key.replace("_", " ").title(), str(value)])
    table = Table(vitals, hAlign="LEFT")
    table.setStyle(
        TableStyle(
            [
                ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#0f766e")),
                ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
                ("GRID", (0, 0), (-1, -1), 0.4, colors.HexColor("#d7e3ea")),
                ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, colors.HexColor("#f6fbfd")]),
                ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
                ("PADDING", (0, 0), (-1, -1), 8),
            ]
        )
    )
    elements.append(table)
    elements.append(Spacer(1, 14))
    elements.append(Paragraph("Key Contributing Factors", styles["Heading3"]))
    for item in payload.prediction.feature_importance[:6]:
        elements.append(Paragraph(f"{item.feature}: {item.direction} ({item.importance})", styles["Normal"]))
    elements.append(Spacer(1, 10))
    elements.append(Paragraph("Clinical Recommendations", styles["Heading3"]))
    for suggestion in payload.prediction.recommendations:
        elements.append(Paragraph(f"- {suggestion}", styles["Normal"]))

    doc.build(elements)
    buffer.seek(0)
    return StreamingResponse(
        buffer,
        media_type="application/pdf",
        headers={"Content-Disposition": "attachment; filename=cardiosense-report.pdf"},
    )
