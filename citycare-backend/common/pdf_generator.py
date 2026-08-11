import io
from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, HRFlowable


def generate_prescription_pdf(
    patient_name: str,
    doctor_name: str,
    appointment_date: str,
    slot: str,
    diagnosis: str,
    medicines: str,
    notes: str = "",
) -> bytes:
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(
        buffer,
        pagesize=letter,
        rightMargin=36,
        leftMargin=36,
        topMargin=36,
        bottomMargin=36,
    )
    styles = getSampleStyleSheet()

    title_style = ParagraphStyle(
        'DocTitle',
        parent=styles['Heading1'],
        fontSize=20,
        leading=24,
        textColor=colors.HexColor('#0E6E5C'),
        alignment=0,
    )
    subtitle_style = ParagraphStyle(
        'DocSubtitle',
        parent=styles['Normal'],
        fontSize=10,
        leading=14,
        textColor=colors.HexColor('#64748B'),
    )
    heading_style = ParagraphStyle(
        'SectionHeading',
        parent=styles['Heading2'],
        fontSize=12,
        leading=16,
        textColor=colors.HexColor('#0A5646'),
        spaceBefore=12,
        spaceAfter=6,
    )
    body_style = ParagraphStyle(
        'Body',
        parent=styles['Normal'],
        fontSize=10,
        leading=14,
        textColor=colors.HexColor('#1E293B'),
    )

    elements = []

    # Header
    elements.append(Paragraph("CityCare Medical Clinic", title_style))
    elements.append(Paragraph("Official Medical Prescription", subtitle_style))
    elements.append(Spacer(1, 10))
    elements.append(HRFlowable(width="100%", thickness=1, color=colors.HexColor('#0E6E5C'), spaceAfter=15))

    # Meta Table (Doctor, Patient, Date, Slot)
    meta_data = [
        [
            Paragraph(f"<b>Doctor:</b> {doctor_name}", body_style),
            Paragraph(f"<b>Patient:</b> {patient_name}", body_style),
        ],
        [
            Paragraph(f"<b>Date:</b> {appointment_date}", body_style),
            Paragraph(f"<b>Time Slot:</b> {slot}", body_style),
        ],
    ]
    t_meta = Table(meta_data, colWidths=[270, 270])
    t_meta.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, -1), colors.HexColor('#F8FAFC')),
        ('PADDING', (0, 0), (-1, -1), 8),
        ('VALIGN', (0, 0), (-1, -1), 'TOP'),
    ]))
    elements.append(t_meta)
    elements.append(Spacer(1, 15))

    # Diagnosis
    elements.append(Paragraph("Diagnosis", heading_style))
    elements.append(Paragraph(diagnosis, body_style))
    elements.append(Spacer(1, 15))

    # Medicines
    elements.append(Paragraph("Prescribed Medicines & Dosage", heading_style))
    elements.append(Paragraph(medicines.replace("\n", "<br/>"), body_style))
    elements.append(Spacer(1, 15))

    # Notes
    if notes and notes.strip():
        elements.append(Paragraph("Instructions / Notes", heading_style))
        elements.append(Paragraph(notes.replace("\n", "<br/>"), body_style))
        elements.append(Spacer(1, 15))

    # Footer
    elements.append(Spacer(1, 30))
    elements.append(HRFlowable(width="100%", thickness=0.5, color=colors.HexColor('#CBD5E1'), spaceAfter=10))
    elements.append(Paragraph(f"Digitally signed by <b>{doctor_name}</b>", subtitle_style))

    doc.build(elements)
    pdf_bytes = buffer.getvalue()
    buffer.close()
    return pdf_bytes
