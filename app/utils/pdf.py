from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
from io import BytesIO

def generate_pdf(results):
    buffer = BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=letter)
    styles = getSampleStyleSheet()
    story = []

    # Title
    story.append(Paragraph("Research Results", styles['Title']))
    story.append(Spacer(1, 12))

    for result in results:
        story.append(Paragraph(f"Title: {result['title']}", styles['Heading2']))
        story.append(Spacer(1, 6))
        story.append(Paragraph(f"Summary: {result['summary']}", styles['Normal']))
        story.append(Spacer(1, 6))
        story.append(Paragraph(f"Link: {result['link']}", styles['Normal']))
        story.append(Spacer(1, 12))

    doc.build(story)
    buffer.seek(0)
    return buffer