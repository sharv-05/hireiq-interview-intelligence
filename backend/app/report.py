from io import BytesIO
from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, PageBreak
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch

def build_report(session):
    out=BytesIO(); doc=SimpleDocTemplate(out,pagesize=letter,rightMargin=.55*inch,leftMargin=.55*inch,topMargin=.5*inch,bottomMargin=.5*inch)
    styles=getSampleStyleSheet(); styles.add(ParagraphStyle(name='Small',parent=styles['BodyText'],fontSize=8,leading=10))
    story=[Paragraph('HireIQ | Candidate Evaluation Report',styles['Title']),Paragraph(f'<b>{session.candidate_name}</b> · {session.role} · {session.created_at:%Y-%m-%d}',styles['Heading3']),Spacer(1,8),Paragraph(f'<b>Overall score:</b> {session.overall_score or 0:.1f}/10 &nbsp;&nbsp; <b>Recommendation:</b> {session.recommendation or "Pending"}',styles['Heading2']),Spacer(1,12)]
    rows=[['Question','Score','Sentiment','Confidence']]
    for r in session.responses: rows.append([r.question.prompt[:75],f'{r.score:.1f}/10',f'{r.sentiment:+.2f}',f'{r.confidence:.0%}'])
    t=Table(rows,colWidths=[4.2*inch,.7*inch,.8*inch,.8*inch]); t.setStyle(TableStyle([('BACKGROUND',(0,0),(-1,0),colors.HexColor('#15263f')),('TEXTCOLOR',(0,0),(-1,0),colors.white),('GRID',(0,0),(-1,-1),.3,colors.HexColor('#cbd5e1')),('VALIGN',(0,0),(-1,-1),'TOP'),('FONTSIZE',(0,0),(-1,-1),8),('ROWBACKGROUNDS',(0,1),(-1,-1),[colors.white,colors.HexColor('#f1f5f9')])]))
    story += [t,Spacer(1,16),Paragraph('Response breakdown',styles['Heading2'])]
    for i,r in enumerate(session.responses,1):
        story += [Paragraph(f'{i}. {r.question.prompt}',styles['Heading3']),Paragraph(f'<b>Score {r.score:.1f}/10</b> · Keywords: {", ".join(r.keywords or [])}',styles['Small']),Paragraph(f'<b>Transcript:</b> {r.transcript}',styles['BodyText']),Paragraph(f'<b>Evaluation:</b> {r.rationale}',styles['Small']),Spacer(1,10)]
    story += [Spacer(1,10),Paragraph('AI-assisted decision support. A trained hiring panel must review the evidence and may override this recommendation. Do not use protected attributes or proxies in scoring.',styles['Small'])]
    doc.build(story); out.seek(0); return out
