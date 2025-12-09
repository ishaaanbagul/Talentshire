
from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.lib.units import mm
from reportlab.platypus import Table, TableStyle, Paragraph, SimpleDocTemplate, Spacer
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.enums import TA_CENTER, TA_LEFT
from datetime import datetime
from reportlab.graphics.shapes import Drawing
from reportlab.graphics.charts.piecharts import Pie
from reportlab.graphics import renderPDF
import os

def _create_pie_chart(title, obtained, max_marks, color_hex='#4F46E5', dummy_arg=None):
    """Create a clean pie chart drawing without overlapping labels."""
    remaining = max(0, max_marks - obtained)

    # Create drawing with proper dimensions for 3-column layout
    drawing = Drawing(150, 80)

    # Donut-style pie chart - no labels on the chart itself
    pie = Pie()
    pie.x = 15
    pie.y = 5
    pie.width = 80
    pie.height = 80
    pie.data = [obtained, remaining]
    # Remove all labels from pie chart - they'll be shown below
    pie.labels = ["", ""]
    # Turn off sideLabels completely
    try:
        pie.sideLabels = False
        pie.labelRadius = 0
    except Exception:
        pass
    
    # Professional styling
    pie.slices[0].fillColor = colors.HexColor(color_hex)
    pie.slices[1].fillColor = colors.HexColor('#e2e8f0')
    pie.slices[0].strokeColor = colors.HexColor('#ffffff')
    pie.slices[1].strokeColor = colors.HexColor('#ffffff')
    pie.slices[0].strokeWidth = 2
    pie.slices[1].strokeWidth = 2

    drawing.add(pie)

    # Create donut effect with white center circle
    try:
        from reportlab.graphics.shapes import Circle
        cx = pie.x + pie.width / 2
        cy = pie.y + pie.height / 2
        # Donut hole - 40% of radius
        r = min(pie.width, pie.height) * 0.40
        hole = Circle(cx, cy, r, fillColor=colors.white, strokeColor=colors.white)
        drawing.add(hole)
    except Exception:
        pass

    return drawing

def generate_pdf_report(data, out_path):
    """Generate a comprehensive PDF report with full dashboard details"""
    # Allow natural page breaks - content can flow to multiple pages
    doc = SimpleDocTemplate(
        out_path, 
        pagesize=A4, 
        topMargin=12*mm, 
        bottomMargin=12*mm, 
        leftMargin=12*mm, 
        rightMargin=12*mm
    )
    styles = getSampleStyleSheet()
    story = []
    
    # Professional color scheme
    PRIMARY_COLOR = '#1e3a5f'  # Deep navy blue
    SECONDARY_COLOR = '#2d5a87'  # Medium blue
    ACCENT_COLOR = '#0ea5e9'  # Sky blue accent
    SUCCESS_COLOR = '#059669'  # Emerald green
    DANGER_COLOR = '#dc2626'  # Red
    TEXT_DARK = '#1f2937'  # Dark gray
    TEXT_LIGHT = '#6b7280'  # Medium gray
    BG_LIGHT = '#f8fafc'  # Light gray background
    BG_MEDIUM = '#e2e8f0'  # Medium gray background
    BORDER_COLOR = '#cbd5e1'  # Border gray
    
    # Custom styles
    title_style = ParagraphStyle(
        'CustomTitle',
        parent=styles['Heading1'],
        fontSize=22,
        textColor=colors.HexColor(PRIMARY_COLOR),
        spaceAfter=6,
        alignment=TA_CENTER,
        fontName='Helvetica-Bold',
        letterSpacing=0.5
    )
    
    heading_style = ParagraphStyle(
        'CustomHeading',
        parent=styles['Heading2'],
        fontSize=11,
        textColor=colors.HexColor(PRIMARY_COLOR),
        spaceAfter=8,
        spaceBefore=14,
        fontName='Helvetica-Bold',
        letterSpacing=0.8
    )
    
    normal_style = ParagraphStyle(
        'CustomNormal',
        parent=styles['Normal'],
        fontSize=9,
        alignment=TA_LEFT,
        leading=13,
        textColor=colors.HexColor(TEXT_DARK),
        spaceAfter=3
    )

    label_style = ParagraphStyle(
        'ChartLabel',
        parent=styles['Normal'],
        fontSize=8,
        alignment=TA_CENTER,
        textColor=colors.HexColor(TEXT_DARK)
    )
    
    cand = data.get('candidate', {})
    mcq = data.get('mcq', {})
    coding = data.get('coding', {})
    
    # Helper function
    def pct_str(obt, mx):
        try:
            if mx and mx > 0:
                return f"{(obt/mx*100):.2f}%"
            return "0.00%"
        except (ZeroDivisionError, TypeError):
            return "0.00%"
    
    # ========== HEADER ==========
    # Add a professional header with border
    header_table = Table([[Paragraph("EXAMINATION REPORT", title_style)]], colWidths=[186*mm])
    header_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, -1), colors.HexColor(PRIMARY_COLOR)),
        ('TEXTCOLOR', (0, 0), (-1, -1), colors.white),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 12),
        ('TOPPADDING', (0, 0), (-1, -1), 12),
        ('BOX', (0, 0), (-1, -1), 0, colors.HexColor(PRIMARY_COLOR)),
    ]))
    story.append(header_table)
    story.append(Spacer(1, 8))
    
    # ========== CANDIDATE INFO ==========
    # Use two-column layout for candidate info to save space
    cand_info_left = [
        ["Name", cand.get('name', '-')],
        ["Email", cand.get('email', '-')],
        ["Candidate ID", cand.get('id', '-')]
    ]
    cand_info_right = [
        ["Exam", cand.get('exam', '-')],
        ["Date", cand.get('date', '-')],
        ["Duration", cand.get('duration', '-')]
    ]
    
    t_left = Table(cand_info_left, colWidths=[35*mm, 55*mm])
    t_right = Table(cand_info_right, colWidths=[35*mm, 55*mm])
    
    table_style = TableStyle([
        ('BACKGROUND', (0, 0), (0, -1), colors.HexColor(BG_MEDIUM)),
        ('TEXTCOLOR', (0, 0), (0, -1), colors.HexColor(PRIMARY_COLOR)),
        ('TEXTCOLOR', (1, 0), (1, -1), colors.HexColor(TEXT_DARK)),
        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
        ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, -1), 8),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 7),
        ('TOPPADDING', (0, 0), (-1, -1), 7),
        ('LEFTPADDING', (0, 0), (-1, -1), 8),
        ('RIGHTPADDING', (0, 0), (-1, -1), 8),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor(BORDER_COLOR)),
        ('LINEBELOW', (0, -1), (-1, -1), 0.5, colors.HexColor(BORDER_COLOR)),
    ])
    t_left.setStyle(table_style)
    t_right.setStyle(table_style)
    
    # Combine in two columns
    cand_table = Table([[t_left, t_right]], colWidths=[95*mm, 95*mm])
    cand_table.setStyle(TableStyle([
        ('VALIGN', (0, 0), (-1, -1), 'TOP'),
    ]))
    story.append(cand_table)
    story.append(Spacer(1, 6))
    
    # ========== VISUAL REPORT ==========
    total_marks = mcq.get('max_marks', 0) + coding.get('max_marks', 0)
    total_obtained = mcq.get('marks_obtained', 0) + coding.get('marks_obtained', 0)
    total_pct = pct_str(total_obtained, total_marks)

    # Scores summary table
    scores = [
        ["Section", "Max Marks", "Marks Obtained", "Percentage"],
        ["MCQ", str(mcq.get('max_marks', 0)), str(mcq.get('marks_obtained', 0)), pct_str(mcq.get('marks_obtained', 0), mcq.get('max_marks', 1))],
        ["Coding", str(coding.get('max_marks', 0)), str(coding.get('marks_obtained', 0)), pct_str(coding.get('marks_obtained', 0), coding.get('max_marks', 1))],
        ["TOTAL", str(total_marks), str(total_obtained), total_pct]
    ]
    # Scores table with proper spacing
    st = Table(scores, colWidths=[45*mm, 45*mm, 45*mm, 45*mm])
    st.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor(PRIMARY_COLOR)),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
        ('BACKGROUND', (0, -1), (-1, -1), colors.HexColor(BG_MEDIUM)),
        ('TEXTCOLOR', (0, -1), (-1, -1), colors.HexColor(PRIMARY_COLOR)),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTNAME', (0, -1), (-1, -1), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, -1), 8),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
        ('TOPPADDING', (0, 0), (-1, -1), 8),
        ('LEFTPADDING', (0, 0), (-1, -1), 4),
        ('RIGHTPADDING', (0, 0), (-1, -1), 4),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor(BORDER_COLOR)),
        ('LINEBELOW', (0, 0), (-1, 0), 1, colors.HexColor(PRIMARY_COLOR)),
    ]))
    story.append(st)
    story.append(Spacer(1, 20))  # Increased spacing between table and charts

    # ========== CHARTS (Professional layout with proper spacing) ==========
    # Create clean charts without overlapping labels
    mcq_chart = _create_pie_chart("MCQ", mcq.get('marks_obtained', 0), mcq.get('max_marks', 1), color_hex='#2d5a87')
    coding_chart = _create_pie_chart("Coding", coding.get('marks_obtained', 0), coding.get('max_marks', 1), color_hex='#0ea5e9')
    
    # Calculate proctoring compliance score (100 - focus deviation = compliance)
    proctoring_data = data.get('proctoring', {}) or {}
    include_proctoring = data.get('include_proctoring', True)
    
    # Always create proctoring chart if include_proctoring is True
    if include_proctoring:
        # Get focus deviation, default to 0 if not available
        focus_deviation = float(proctoring_data.get('focus_deviation_percent', 0))
        compliance_score = max(0, min(100, 100 - focus_deviation))  # Invert: lower deviation = higher compliance
        proctoring_chart = _create_pie_chart("Proctoring", compliance_score, 100, color_hex='#f59e0b')
        proctoring_pct = f"{compliance_score:.1f}%"
        proctoring_label_text = f"<b style='font-size:10'>{proctoring_pct}</b><br/><font size='7' color='{TEXT_LIGHT}'>Compliance</font><br/><font size='6'>Deviation: {focus_deviation:.1f}%</font>"
        proctoring_label = Paragraph(proctoring_label_text, label_style)
    else:
        # Don't create chart or label if proctoring is disabled
        proctoring_chart = Drawing(0, 0)  # Empty drawing with 0 size
        proctoring_label = Paragraph("", label_style)  # Empty paragraph instead of None

    # Professional labels with clear spacing - no overlapping
    mcq_pct = pct_str(mcq.get('marks_obtained', 0), mcq.get('max_marks', 1))
    coding_pct = pct_str(coding.get('marks_obtained', 0), coding.get('max_marks', 1))
    
    # Create label paragraphs with proper spacing and hierarchy
    mcq_label_text = f"<b style='font-size:10'>{mcq_pct}</b><br/><font size='7' color='{TEXT_LIGHT}'>MCQ Section</font><br/><font size='6'>{mcq.get('marks_obtained',0)} / {mcq.get('max_marks',0)} marks</font>"
    coding_label_text = f"<b style='font-size:10'>{coding_pct}</b><br/><font size='7' color='{TEXT_LIGHT}'>Coding Section</font><br/><font size='6'>{coding.get('marks_obtained',0)} / {coding.get('max_marks',0)} marks</font>"
    
    mcq_label = Paragraph(mcq_label_text, label_style)
    coding_label = Paragraph(coding_label_text, label_style)

    # Build chart table based on whether proctoring is included
    if include_proctoring:
        # 3-column layout with proctoring
        chart_table = Table([
            [mcq_chart, coding_chart, proctoring_chart],
            [Spacer(1, 8), Spacer(1, 8), Spacer(1, 8)],  # Increased spacer row for breathing room
            [mcq_label, coding_label, proctoring_label]
        ], colWidths=[60*mm, 60*mm, 60*mm], rowHeights=[32*mm, 5*mm, 18*mm])  # Increased spacer and label row heights
    else:
        # 2-column layout without proctoring
        chart_table = Table([
            [mcq_chart, coding_chart],
            [Spacer(1, 8), Spacer(1, 8)],  # Spacer row for breathing room
            [mcq_label, coding_label]
        ], colWidths=[60*mm, 60*mm], rowHeights=[32*mm, 5*mm, 18*mm])
    
    chart_table.setStyle(TableStyle([
        ('ALIGN',(0,0),(-1,-1),'CENTER'),
        ('VALIGN',(0,0),(-1,0),'MIDDLE'),  # Charts centered vertically
        ('VALIGN',(0,2),(-1,2),'TOP'),     # Labels aligned to top
        ('LEFTPADDING',(0,0),(-1,-1),3),
        ('RIGHTPADDING',(0,0),(-1,-1),3),
        ('TOPPADDING',(0,0),(-1,0),6),     # Increased top padding for charts
        ('BOTTOMPADDING',(0,0),(-1,0),6),  # Increased bottom padding for charts
        ('TOPPADDING',(0,2),(-1,2),2),     # Increased top padding for labels
    ]))
    
    story.append(chart_table)
    story.append(Spacer(1, 12))  # Increased spacing after charts

    # Add coding questions section (compact format)
    if coding.get('questions'):
        story.append(Spacer(1, 4))  # Extra space before questions section
        story.append(Paragraph("CODING QUESTIONS", heading_style))
        for i, q in enumerate(coding.get('questions', []), 1):
            # Header with title, difficulty, marks, and status in one line
            status_icon = "✓" if q.get('output_correct') else "✗"
            status_color = SUCCESS_COLOR if q.get('output_correct') else DANGER_COLOR
            header_text = f"<b>Q{q.get('id', i)}: {q.get('title', '')}</b> | <i>{q.get('difficulty', 'N/A')}</i> | Marks: {q.get('marks', 0)} | <font color='{status_color}'>{status_icon}</font>"
            story.append(Paragraph(header_text, normal_style))
            story.append(Spacer(1, 3))
            
            # Description (compact)
            desc_text = q.get('description', '')
            if len(desc_text) > 200:
                desc_text = desc_text[:200] + "..."
            story.append(Paragraph(f"<b>Desc:</b> {desc_text}", normal_style))
            story.append(Spacer(1, 3))
            
            # Solution code (compact, truncated if too long)
            code_text = q.get('given_answer', '').replace('<', '&lt;').replace('>', '&gt;')
            # Truncate very long code solutions
            if len(code_text) > 500:
                code_text = code_text[:500] + "\n... (truncated)"
            story.append(Paragraph(f"<b>Solution:</b>", normal_style))
            story.append(Spacer(1, 2))
            story.append(Paragraph(f"<font name='Courier' size='6'><pre>{code_text}</pre></font>", normal_style))
            story.append(Spacer(1, 6))

    # Add MCQ questions section (compact format)
    if mcq.get('questions'):
        story.append(Paragraph("MCQ QUESTIONS", heading_style))
        for i, q in enumerate(mcq.get('questions', []), 1):
            # Question with status and marks in header
            status_icon = "✓" if q.get('is_correct') else "✗"
            status_color = SUCCESS_COLOR if q.get('is_correct') else DANGER_COLOR
            question_text = f"<b>Q{q.get('id', i)}:</b> {q.get('question', '')} | <font color='{status_color}'>{status_icon}</font> | Marks: {q.get('marks', 0)}"
            story.append(Paragraph(question_text, normal_style))
            story.append(Spacer(1, 3))
            
            # Options in compact table
            options_data = []
            for idx, opt in enumerate(q.get('options', []), 1):
                is_correct = opt == q.get('correct')
                is_given = opt == q.get('given_answer')
                marker = ""
                if is_correct:
                    marker = " ✓"
                elif is_given:
                    marker = " ✗"
                options_data.append([f"{chr(64+idx)}.", f"{opt}{marker}"])
            opt_table = Table(options_data, colWidths=[12*mm, 158*mm])
            opt_table.setStyle(TableStyle([
                ('FONTSIZE', (0, 0), (-1, -1), 7),
                ('ALIGN', (0, 0), (0, -1), 'LEFT'),
                ('TOPPADDING', (0, 0), (-1, -1), 3),
                ('BOTTOMPADDING', (0, 0), (-1, -1), 3),
                ('LEFTPADDING', (0, 0), (-1, -1), 4),
                ('RIGHTPADDING', (0, 0), (-1, -1), 4),
            ]))
            story.append(opt_table)
            story.append(Spacer(1, 5))
    
    # ========== PROCTORING ==========
    if data.get('include_proctoring', True) and data.get('proctoring'):
        story.append(Spacer(1, 4))
        story.append(Paragraph("PROCTORING INFORMATION", heading_style))
        p = data.get('proctoring', {})
        # Use two-column layout for proctoring data
        proc_data_left = [
            ["Flagged Faces", str(p.get('flagged_faces', 0))],
            ["Focus Deviation", f"{p.get('focus_deviation_percent', 0)}%"]
        ]
        proc_data_right = [
            ["Cheating Events", str(p.get('cheating_events', 0))],
            ["Unusual Activity", str(p.get('unusual_activity', 'None'))[:30]]
        ]
        
        pt_left = Table(proc_data_left, colWidths=[45*mm, 45*mm])
        pt_right = Table(proc_data_right, colWidths=[45*mm, 45*mm])
        proc_style = TableStyle([
            ('BACKGROUND', (0, 0), (0, -1), colors.HexColor(BG_MEDIUM)),
            ('TEXTCOLOR', (0, 0), (0, -1), colors.HexColor(PRIMARY_COLOR)),
            ('TEXTCOLOR', (1, 0), (1, -1), colors.HexColor(TEXT_DARK)),
            ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, -1), 7),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
            ('TOPPADDING', (0, 0), (-1, -1), 6),
            ('LEFTPADDING', (0, 0), (-1, -1), 8),
            ('RIGHTPADDING', (0, 0), (-1, -1), 8),
            ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor(BORDER_COLOR)),
        ])
        pt_left.setStyle(proc_style)
        pt_right.setStyle(proc_style)
        
        proc_table = Table([[pt_left, pt_right]], colWidths=[95*mm, 95*mm])
        proc_table.setStyle(TableStyle([('VALIGN', (0, 0), (-1, -1), 'TOP')]))
        story.append(proc_table)
        story.append(Spacer(1, 4))
    
    # ========== FOOTER ==========
    story.append(Spacer(1, 8))
    footer_style = ParagraphStyle(
        'Footer',
        parent=normal_style,
        fontSize=7,
        textColor=colors.HexColor(TEXT_LIGHT),
        alignment=TA_CENTER
    )
    footer_text = f"© 2025 Online Test Platform | Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
    story.append(Paragraph(footer_text, footer_style))
    
    doc.build(story)
