from datetime import date, datetime
from io import BytesIO
from xml.sax.saxutils import escape

from django.http import FileResponse
from django.utils import timezone
from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib.units import mm
from reportlab.platypus import (
    CondPageBreak,
    LongTable,
    Paragraph,
    SimpleDocTemplate,
    Spacer,
)

from .models import SubscriptionTracker

NAVY = colors.HexColor("#172033")
PURPLE = colors.HexColor("#7C3AED")
TEXT = colors.HexColor("#334155")
MUTED = colors.HexColor("#64748B")
BORDER = colors.HexColor("#E2E8F0")
PALE = colors.HexColor("#F8FAFC")


def export_subscription_report_pdf():
    today = timezone.localdate()
    buffer = BytesIO()

    page_width, _ = A4
    margin = 18 * mm
    content_width = page_width - (2 * margin)

    document = SimpleDocTemplate(
        buffer,
        pagesize=A4,
        leftMargin=margin,
        rightMargin=margin,
        topMargin=21 * mm,
        bottomMargin=19 * mm,
        title="Active Subscription Report",
    )

    title_style = ParagraphStyle(
        "ReportTitle",
        fontName="Helvetica-Bold",
        fontSize=19,
        leading=24,
        textColor=NAVY,
        spaceAfter=5,
    )

    heading_style = ParagraphStyle(
        "SectionHeading",
        fontName="Helvetica-Bold",
        fontSize=12,
        leading=17,
        textColor=NAVY,
        spaceAfter=6,
    )

    card_title_style = ParagraphStyle(
        "CardTitle",
        fontName="Helvetica-Bold",
        fontSize=11,
        leading=15,
        textColor=colors.white,
    )

    label_style = ParagraphStyle(
        "FieldLabel",
        fontName="Helvetica-Bold",
        fontSize=8,
        leading=11,
        textColor=MUTED,
    )

    value_style = ParagraphStyle(
        "FieldValue",
        fontName="Helvetica",
        fontSize=9,
        leading=13,
        textColor=TEXT,
    )

    small_style = ParagraphStyle(
        "SmallText",
        parent=value_style,
        fontSize=8,
        textColor=MUTED,
    )

    def is_populated(value):
        # Keep meaningful values such as 0 and False.
        return value is not None and not (isinstance(value, str) and not value.strip())

    def format_value(value):
        if isinstance(value, bool):
            return "Yes" if value else "No"

        if isinstance(value, datetime):
            if timezone.is_aware(value):
                value = timezone.localtime(value)
            return value.strftime("%d %b %Y, %I:%M %p")

        if isinstance(value, date):
            return value.strftime("%d %b %Y")

        return str(value)

    def make_paragraph(value, style=value_style):
        safe_text = escape(format_value(value)).replace("\n", "<br/>")
        return Paragraph(safe_text, style)

    story = [
        Paragraph("Subscription Report", title_style),
        Paragraph(
            f"{today:%B %Y} · Generated " f"{timezone.localtime():%d %b %Y, %I:%M %p}",
            small_style,
        ),
        Spacer(1, 9 * mm),
        Paragraph("Active Subscription Details", heading_style),
        Spacer(1, 3 * mm),
    ]

    subscriptions = (
        SubscriptionTracker.objects.filter(status="active")
        .select_related(
            "card_used",
            "currency",
            "payment_timing",
        )
        .order_by("platform", "pk")
    )

    has_subscriptions = False

    for subscription in subscriptions:
        has_subscriptions = True

        fields = [
            ("Platform", subscription.platform),
            ("Status", subscription.get_status_display()),
            ("Email Used", subscription.email_used),
            ("Card Used", subscription.card_used),
            ("Used For", subscription.used_for),
            ("Currency", subscription.currency),
            ("Pricing", subscription.pricing),
            ("Payment Timing", subscription.payment_timing),
            ("Debit Date", subscription.debit_date),
            ("Notes", subscription.notes),
            (
                "Last Debit Processed",
                subscription.last_debit_processed_date,
            ),
            ("Created At", subscription.created_at),
            ("Updated At", subscription.updated_at),
            ("Days Until Debit", subscription.days_until_debit()),
            ("Due Soon", subscription.is_due_soon()),
            ("Overdue", subscription.is_overdue()),
        ]

        fields = [(label, value) for label, value in fields if is_populated(value)]

        story.append(CondPageBreak(38 * mm))

        heading = LongTable(
            [[make_paragraph(subscription.platform, card_title_style)]],
            colWidths=[content_width],
        )
        heading.setStyle(
            [
                ("BACKGROUND", (0, 0), (-1, -1), NAVY),
                ("LINEBEFORE", (0, 0), (0, -1), 4, PURPLE),
                ("LEFTPADDING", (0, 0), (-1, -1), 12),
                ("RIGHTPADDING", (0, 0), (-1, -1), 12),
                ("TOPPADDING", (0, 0), (-1, -1), 9),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 9),
            ]
        )
        story.append(heading)

        # Two label/value pairs on each row.
        rows = []

        for index in range(0, len(fields), 2):
            left_label, left_value = fields[index]

            row = [
                make_paragraph(left_label, label_style),
                make_paragraph(left_value),
            ]

            if index + 1 < len(fields):
                right_label, right_value = fields[index + 1]

                row.extend(
                    [
                        make_paragraph(right_label, label_style),
                        make_paragraph(right_value),
                    ]
                )
            else:
                row.extend(["", ""])

            rows.append(row)

        details = LongTable(
            rows,
            colWidths=[
                29 * mm,
                56 * mm,
                29 * mm,
                content_width - (114 * mm),
            ],
            hAlign="LEFT",
        )
        details.setStyle(
            [
                ("VALIGN", (0, 0), (-1, -1), "TOP"),
                ("BACKGROUND", (0, 0), (0, -1), PALE),
                ("BACKGROUND", (2, 0), (2, -1), PALE),
                ("LINEBELOW", (0, 0), (-1, -1), 0.3, BORDER),
                ("LEFTPADDING", (0, 0), (-1, -1), 6),
                ("RIGHTPADDING", (0, 0), (-1, -1), 6),
                ("TOPPADDING", (0, 0), (-1, -1), 7),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 7),
            ]
        )

        story.extend(
            [
                details,
                Spacer(1, 8 * mm),
            ]
        )

    if not has_subscriptions:
        story.append(Paragraph("No active subscriptions found.", value_style))

    def draw_footer(canvas, doc):
        canvas.saveState()

        canvas.setStrokeColor(BORDER)
        canvas.line(
            margin,
            15 * mm,
            page_width - margin,
            15 * mm,
        )

        canvas.setFont("Helvetica", 8)
        canvas.setFillColor(MUTED)
        canvas.drawString(
            margin,
            10 * mm,
            "Active Subscription Report",
        )
        canvas.drawRightString(
            page_width - margin,
            10 * mm,
            f"Page {doc.page}",
        )

        canvas.restoreState()

    document.build(
        story,
        onFirstPage=draw_footer,
        onLaterPages=draw_footer,
    )

    buffer.seek(0)

    return FileResponse(
        buffer,
        as_attachment=True,
        filename=f"subscription_report_{today:%B_%d_%Y}.pdf",
        content_type="application/pdf",
    )
