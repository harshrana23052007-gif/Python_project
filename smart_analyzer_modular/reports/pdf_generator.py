"""
PDF report generation for Smart Expense Analyzer
Handles PDF export functionality
"""

from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer, PageBreak, Image
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.lib import colors
import calendar
import matplotlib.pyplot as plt
from io import BytesIO
import os
from datetime import datetime


def export_report_to_pdf(file_path, categories_data, year, month, total_expenses):
    """Export expense report to PDF with charts"""
    
    # Create PDF document
    doc = SimpleDocTemplate(file_path, pagesize=letter)
    story = []
    
    # Get styles
    styles = getSampleStyleSheet()
    title_style = ParagraphStyle(
        'CustomTitle',
        parent=styles['Heading1'],
        fontSize=24,
        textColor=colors.HexColor('#0078d4'),
        spaceAfter=30
    )
    
    # Add title
    story.append(Paragraph("Smart Expense Analyzer - Report", title_style))
    story.append(Spacer(1, 0.3*inch))
    
    # Add month info
    story.append(Paragraph(f"Report for: {calendar.month_name[month]} {year}", styles['Heading2']))
    story.append(Spacer(1, 0.2*inch))
    
    # Summary section
    story.append(Paragraph("Summary", styles['Heading3']))
    summary_data = [
        ['Total Expenses', f"${total_expenses:.2f}"],
        ['Categories', str(len(categories_data))],
        ['Average per Category', f"${total_expenses/len(categories_data):.2f}" if categories_data else "$0.00"]
    ]
    
    summary_table = Table(summary_data, colWidths=[3*inch, 2*inch])
    summary_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, -1), colors.beige),
        ('TEXTCOLOR', (0, 0), (-1, -1), colors.black),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('FONTNAME', (0, 0), (-1, -1), 'Helvetica'),
        ('FONTSIZE', (0, 0), (-1, -1), 10),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 12),
    ]))
    story.append(summary_table)
    story.append(Spacer(1, 0.3*inch))
    
    # Add Pie Chart
    if categories_data:
        story.append(Paragraph("Spending Distribution", styles['Heading3']))
        pie_img = _create_pie_chart(categories_data)
        story.append(Image(pie_img, width=4*inch, height=4*inch))
        story.append(Spacer(1, 0.2*inch))
    
    # Page break before category table
    story.append(PageBreak())
    
    # Add Bar Chart
    if categories_data:
        story.append(Paragraph("Category Breakdown Chart", styles['Heading3']))
        bar_img = _create_bar_chart(categories_data)
        story.append(Image(bar_img, width=5*inch, height=3.5*inch))
        story.append(Spacer(1, 0.3*inch))
    
    # Category breakdown table
    story.append(Paragraph("Detailed Category Breakdown", styles['Heading3']))
    table_data = [['Category', 'Amount', 'Percentage']]
    
    for category, amount in categories_data:
        percentage = (amount / total_expenses * 100) if total_expenses > 0 else 0
        table_data.append([category, f"${amount:.2f}", f"{percentage:.1f}%"])
    
    table = Table(table_data, colWidths=[2*inch, 1.5*inch, 1.5*inch])
    table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, 0), 11),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
        ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
        ('GRID', (0, 0), (-1, -1), 1, colors.black)
    ]))
    story.append(table)
    
    # Build PDF
    doc.build(story)


def _create_pie_chart(categories_data):
    """Create a pie chart for spending distribution"""
    fig, ax = plt.subplots(figsize=(6, 6))
    
    categories = [cat[0] for cat in categories_data]
    amounts = [cat[1] for cat in categories_data]
    
    colors_palette = plt.cm.Set3(range(len(categories)))
    wedges, texts, autotexts = ax.pie(
        amounts,
        labels=categories,
        autopct='%1.1f%%',
        startangle=90,
        colors=colors_palette
    )
    
    # Make percentage text bold and readable
    for autotext in autotexts:
        autotext.set_color('black')
        autotext.set_fontweight('bold')
        autotext.set_fontsize(9)
    
    ax.set_title('Spending Distribution by Category', fontsize=14, fontweight='bold', pad=20)
    
    # Save to BytesIO
    img_buffer = BytesIO()
    plt.savefig(img_buffer, format='png', dpi=100, bbox_inches='tight')
    img_buffer.seek(0)
    plt.close()
    
    return img_buffer


def _create_bar_chart(categories_data):
    """Create a bar chart for category amounts"""
    fig, ax = plt.subplots(figsize=(8, 5))
    
    categories = [cat[0] for cat in categories_data]
    amounts = [cat[1] for cat in categories_data]
    
    colors_palette = plt.cm.Set3(range(len(categories)))
    bars = ax.bar(categories, amounts, color=colors_palette, edgecolor='black', linewidth=1.2)
    
    # Add value labels on bars
    for bar in bars:
        height = bar.get_height()
        ax.text(
            bar.get_x() + bar.get_width()/2., height,
            f'${height:.2f}',
            ha='center', va='bottom', fontsize=9, fontweight='bold'
        )
    
    ax.set_xlabel('Category', fontsize=11, fontweight='bold')
    ax.set_ylabel('Amount ($)', fontsize=11, fontweight='bold')
    ax.set_title('Spending by Category', fontsize=14, fontweight='bold', pad=20)
    ax.grid(axis='y', alpha=0.3, linestyle='--')
    
    # Rotate x-axis labels if needed
    plt.setp(ax.xaxis.get_majorticklabels(), rotation=45, ha='right')
    
    # Save to BytesIO
    img_buffer = BytesIO()
    plt.savefig(img_buffer, format='png', dpi=100, bbox_inches='tight')
    img_buffer.seek(0)
    plt.close()
    
    return img_buffer
