"""
Initiative Viewer PDF Generator
Generates modern, professional PDF reports with statistics and visualizations.

Author: Pietro Maffi
"""

from reportlab.lib import colors
from reportlab.lib.pagesizes import A4, A3, landscape
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.platypus import (
    SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer, 
    PageBreak, Image, KeepTogether
)
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_RIGHT, TA_JUSTIFY
from reportlab.graphics.shapes import Drawing, Rect, String
from reportlab.graphics.charts.piecharts import Pie
from reportlab.graphics.charts.barcharts import VerticalBarChart
from datetime import datetime
import io
from typing import List, Dict


class InitiativeViewerPDFGenerator:
    """Generate comprehensive PDF reports for Initiative Viewer data."""
    
    # Risk color mapping (1=Green/Low, 5=Red/High)
    RISK_COLORS = {
        1: colors.Color(0.2, 0.8, 0.2),  # Green
        2: colors.Color(0.6, 0.9, 0.3),  # Light green
        3: colors.Color(1.0, 0.8, 0.0),  # Yellow/Orange
        4: colors.Color(1.0, 0.5, 0.0),  # Orange
        5: colors.Color(0.9, 0.2, 0.2),  # Red
        None: colors.Color(0.9, 0.9, 0.9)  # Gray for undefined
    }
    
    # Completed status highlight color (bright green)
    COMPLETED_COLOR = colors.Color(0.2, 0.9, 0.4)
    
    def __init__(self, initiatives: List[Dict], fix_version: str, all_areas: List[str], query: str = '', page_format: str = 'A4', jira_url: str = '', is_limited: bool = False, limit_count: int = None, original_count: int = None, completed_statuses: List[str] = None):
        """
        Initialize PDF generator.
        
        Args:
            initiatives: List of initiative data structures
            fix_version: Program Increment / Fix Version
            all_areas: List of all unique areas/projects
            query: JQL query used to fetch initiatives
            page_format: Page format - 'A4' (default), 'A3', or 'wide'
            jira_url: Base URL for Jira instance (for creating clickable links)
            is_limited: Whether initiative count was limited
            limit_count: Number of initiatives limited to
            original_count: Original number of initiatives before limiting
            completed_statuses: List of status values that indicate completion
        """
        self.initiatives = initiatives
        self.fix_version = fix_version
        self.all_areas = sorted(all_areas)
        self.query = query
        self.page_format = page_format
        self.jira_url = jira_url.rstrip('/')  # Remove trailing slash if present
        self.is_limited = is_limited
        self.limit_count = limit_count
        self.original_count = original_count
        self.completed_statuses = completed_statuses or ['done', 'closed', 'completed', 'resolved', 'proddeployed']
        self.styles = getSampleStyleSheet()
        self._setup_custom_styles()
        
    def _setup_custom_styles(self):
        """Create custom paragraph styles for the PDF."""
        # Title style
        self.styles.add(ParagraphStyle(
            name='CustomTitle',
            parent=self.styles['Heading1'],
            fontSize=28,
            textColor=colors.HexColor('#667eea'),
            spaceAfter=20,
            alignment=TA_CENTER,
            fontName='Helvetica-Bold'
        ))
        
        # Subtitle style
        self.styles.add(ParagraphStyle(
            name='CustomSubtitle',
            parent=self.styles['Normal'],
            fontSize=16,
            textColor=colors.HexColor('#4a5568'),
            spaceAfter=12,
            alignment=TA_CENTER,
            fontName='Helvetica-Bold'
        ))
        
        # Info text style
        self.styles.add(ParagraphStyle(
            name='InfoText',
            parent=self.styles['Normal'],
            fontSize=11,
            textColor=colors.HexColor('#2d3748'),
            spaceAfter=8,
            alignment=TA_LEFT,
            fontName='Helvetica'
        ))
        
        # Purpose box style
        self.styles.add(ParagraphStyle(
            name='PurposeText',
            parent=self.styles['Normal'],
            fontSize=11,
            textColor=colors.HexColor('#2d3748'),
            spaceAfter=6,
            alignment=TA_LEFT,
            fontName='Helvetica',
            leading=16
        ))
        
        # Section header style
        self.styles.add(ParagraphStyle(
            name='SectionHeader',
            parent=self.styles['Heading2'],
            fontSize=16,
            textColor=colors.HexColor('#2d3748'),
            spaceAfter=12,
            spaceBefore=20,
            fontName='Helvetica-Bold'
        ))
        
        # Initiative header style
        self.styles.add(ParagraphStyle(
            name='InitiativeHeader',
            parent=self.styles['Heading3'],
            fontSize=13,
            textColor=colors.HexColor('#667eea'),
            spaceAfter=6,
            fontName='Helvetica-Bold'
        ))
        
        # Epic post-it style (small text for post-its)
        self.styles.add(ParagraphStyle(
            name='EpicPostIt',
            parent=self.styles['Normal'],
            fontSize=7,
            textColor=colors.HexColor('#2d3748'),
            alignment=TA_LEFT,
            fontName='Helvetica',
            leading=9
        ))
    
    def generate(self) -> io.BytesIO:
        """
        Generate the complete PDF report.
        
        Returns:
            io.BytesIO: PDF file buffer
        """
        # Determine page size based on format
        if self.page_format == 'A3':
            pagesize = landscape(A3)
        elif self.page_format == 'wide':
            # Custom wide format (A3 is 16.54" x 11.69" in landscape)
            # Use even wider for many areas
            pagesize = (20 * inch, 11.69 * inch)
        else:
            pagesize = landscape(A4)
        
        buffer = io.BytesIO()
        doc = SimpleDocTemplate(
            buffer,
            pagesize=pagesize,
            rightMargin=20,
            leftMargin=20,
            topMargin=20,
            bottomMargin=50,  # Extra space for footer
            title=f"Initiative Hierarchy Report - {self.fix_version}",
            author="Pietro Maffi",
            subject=f"Initiative Hierarchy for {self.fix_version}",
        )
        
        # Build the story (content)
        story = []
        
        # Title page with explanation
        story.extend(self._create_title_page())
        story.append(PageBreak())
        
        # Initiative tables with post-it style epics
        story.extend(self._create_initiative_tables())
        
        # Build PDF with custom page template for footer
        doc.build(story, onFirstPage=self._add_page_footer, onLaterPages=self._add_page_footer)
        buffer.seek(0)
        return buffer
    
    def _add_page_footer(self, canvas, doc):
        """Add footer with page number and copyright to each page."""
        canvas.saveState()
        page_width, page_height = landscape(A4)
        
        # Set font for footer
        canvas.setFont('Helvetica', 9)
        canvas.setFillColor(colors.HexColor('#718096'))
        
        # Left side: Copyright
        copyright_text = "© 2026 Pietro Maffi - Initiative Hierarchy Report"
        canvas.drawString(30, 20, copyright_text)
        
        # Right side: Page number
        page_num = canvas.getPageNumber()
        page_text = f"Page {page_num}"
        canvas.drawRightString(page_width - 30, 20, page_text)
        
        # Draw a line above footer
        canvas.setStrokeColor(colors.HexColor('#e2e8f0'))
        canvas.setLineWidth(0.5)
        canvas.line(30, 35, page_width - 30, 35)
        
        canvas.restoreState()
    
    def _create_title_page(self) -> List:
        """Create the title page with purpose, date, and query information."""
        elements = []
        
        # Main title
        title = Paragraph("📋 Initiative Hierarchy Report", self.styles['CustomTitle'])
        elements.append(title)
        elements.append(Spacer(1, 0.3 * inch))
        
        # Purpose section in a box
        purpose_data = [
            [Paragraph("<b>📋 Hierarchy Structure</b>", self.styles['PurposeText'])],
            [Paragraph("Business Initiative → Feature → Sub-Feature → Epic", self.styles['PurposeText'])],
            [Paragraph("", self.styles['PurposeText'])],
            [Paragraph("<b>🎯 Report Characteristics:</b>", self.styles['PurposeText'])],
            [Paragraph("• Filtered by Fix Version / Program Increment", self.styles['PurposeText'])],
            [Paragraph("• Organized by Area/Project (columns)", self.styles['PurposeText'])],
            [Paragraph("• Color-coded by Risk Probability (1=Low/Green → 5=High/Red)", self.styles['PurposeText'])],
            [Paragraph("• <b>Completed Epics highlighted in Bright Green</b>", self.styles['PurposeText'])],
        ]
        
        purpose_table = Table(purpose_data, colWidths=[7 * inch])
        purpose_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, -1), colors.HexColor('#f7fafc')),
            ('BOX', (0, 0), (-1, -1), 2, colors.HexColor('#667eea')),
            ('TOPPADDING', (0, 0), (-1, -1), 12),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 12),
            ('LEFTPADDING', (0, 0), (-1, -1), 20),
            ('RIGHTPADDING', (0, 0), (-1, -1), 20),
        ]))
        elements.append(purpose_table)
        elements.append(Spacer(1, 0.4 * inch))
        
        # Calculate initiatives with data
        initiatives_with_data = [
            init for init in self.initiatives 
            if init.get('features') and len(init['features']) > 0
        ]
        
        # Report metadata
        metadata_data = [
            ['Program Increment / Fix Version:', f'<b>{self.fix_version}</b>'],
            ['Generated Date:', f'<b>{datetime.now().strftime("%B %d, %Y at %H:%M")}</b>'],
            ['Total Initiatives Found:', f'<b>{len(self.initiatives)}</b>'],
            ['Initiatives with Features:', f'<b>{len(initiatives_with_data)}</b>'],
            ['Total Areas/Projects:', f'<b>{len(self.all_areas)}</b>'],
        ]
        
        if self.is_limited and self.original_count:
            metadata_data.insert(3, ['Initiatives Limit Applied:', f'<b><font color="#d97706">Limited to {self.limit_count} of {self.original_count} initiatives</font></b>'])
        
        if self.query:
            metadata_data.append(['JQL Query:', f'<font size="9">{self.query}</font>'])
        
        metadata_rows = [[
            Paragraph(row[0], self.styles['InfoText']),
            Paragraph(row[1], self.styles['InfoText'])
        ] for row in metadata_data]
        
        metadata_table = Table(metadata_rows, colWidths=[2.5 * inch, 5 * inch])
        metadata_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (0, -1), colors.HexColor('#edf2f7')),
            ('BACKGROUND', (1, 0), (1, -1), colors.white),
            ('BOX', (0, 0), (-1, -1), 1, colors.HexColor('#cbd5e0')),
            ('GRID', (0, 0), (-1, -1), 1, colors.HexColor('#e2e8f0')),
            ('TOPPADDING', (0, 0), (-1, -1), 8),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
            ('LEFTPADDING', (0, 0), (-1, -1), 12),
            ('RIGHTPADDING', (0, 0), (-1, -1), 12),
            ('VALIGN', (0, 0), (-1, -1), 'TOP'),
        ]))
        elements.append(metadata_table)
        elements.append(Spacer(1, 0.4 * inch))
        
        # Legend
        elements.append(Paragraph("<b>Risk Probability Legend:</b>", self.styles['InfoText']))
        elements.append(Spacer(1, 0.1 * inch))
        
        legend_data = [[
            self._create_color_box(self.RISK_COLORS[1], "1 - Low Risk"),
            self._create_color_box(self.RISK_COLORS[2], "2 - Low-Medium"),
            self._create_color_box(self.RISK_COLORS[3], "3 - Medium"),
            self._create_color_box(self.RISK_COLORS[4], "4 - Medium-High"),
            self._create_color_box(self.RISK_COLORS[5], "5 - High Risk"),
        ], [
            self._create_color_box(self.COMPLETED_COLOR, "✓ Completed Epic"),
            self._create_color_box(self.RISK_COLORS[None], "No Risk Data"),
            '', '', ''
        ]]
        
        legend_table = Table(legend_data, colWidths=[1.5 * inch] * 5)
        legend_table.setStyle(TableStyle([
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
            ('TOPPADDING', (0, 0), (-1, -1), 6),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
        ]))
        elements.append(legend_table)
        
        return elements
    
    def _create_color_box(self, color, text) -> Paragraph:
        """Create a colored box with text for the legend."""
        if not text:
            return ''
        # Using HTML-like styling
        box_html = f'<para align="center"><font size="9">⬛ {text}</font></para>'
        return Paragraph(box_html, self.styles['InfoText'])
    
    def _create_initiative_tables(self) -> List:
        """Create tables for each initiative with post-it style epics."""
        elements = []
        
        # Filter out initiatives without any features
        initiatives_with_data = [
            init for init in self.initiatives 
            if init.get('features') and len(init['features']) > 0
        ]
        
        if not initiatives_with_data:
            elements.append(Paragraph("<i>No initiatives with features found.</i>", self.styles['InfoText']))
            return elements
        
        for idx, initiative in enumerate(initiatives_with_data):
            if idx > 0:
                elements.append(PageBreak())
            
            # Initiative title
            initiative_title = f"🎯 {initiative['key']}: {initiative['summary']}"
            elements.append(Paragraph(initiative_title, self.styles['InitiativeHeader']))
            elements.append(Spacer(1, 0.15 * inch))
            
            # Check if we need to split into multiple views for many areas
            num_areas = len(self.all_areas)
            MAX_AREAS_PER_VIEW = 5  # Maximum areas to show in one table for A4
            
            # For wide formats, show all areas in one table
            if self.page_format in ['A3', 'wide']:
                # Build single table with all areas
                table_data, style_commands = self._build_initiative_table(initiative, self.all_areas)
                
                if table_data and len(table_data) > 1:
                    # Calculate column widths based on page format
                    if self.page_format == 'A3':
                        available_width = 16 * inch  # A3 landscape
                    else:  # wide
                        available_width = 19.5 * inch
                    
                    feature_col_width = 2.5 * inch
                    area_total_width = available_width - feature_col_width
                    area_col_width = area_total_width / num_areas if num_areas > 0 else 2 * inch
                    col_widths = [feature_col_width] + [area_col_width] * num_areas
                    
                    initiative_table = Table(table_data, colWidths=col_widths)
                    initiative_table.setStyle(TableStyle(style_commands))
                    elements.append(initiative_table)
            elif num_areas > MAX_AREAS_PER_VIEW:
                # Split into multiple views for A4
                elements.extend(self._create_split_initiative_tables(initiative, MAX_AREAS_PER_VIEW))
            else:
                # Build single table for this initiative
                table_data, style_commands = self._build_initiative_table(initiative, self.all_areas)
                
                if table_data and len(table_data) > 1:  # Has header and at least one row
                    # Calculate column widths
                    if num_areas > 0:
                        # Narrower columns for better fit
                        available_width = 10.5 * inch
                        feature_col_width = 2.2 * inch
                        area_total_width = available_width - feature_col_width
                        area_col_width = area_total_width / num_areas if num_areas > 0 else 2 * inch
                        col_widths = [feature_col_width] + [area_col_width] * num_areas
                    else:
                        col_widths = [8 * inch]
                    
                    initiative_table = Table(table_data, colWidths=col_widths)
                    initiative_table.setStyle(TableStyle(style_commands))
                    elements.append(initiative_table)
                else:
                    elements.append(Paragraph("<i>No features or epics found for this initiative.</i>", self.styles['InfoText']))
            
            elements.append(Spacer(1, 0.2 * inch))
        
        return elements
    
    def _create_split_initiative_tables(self, initiative: Dict, max_areas: int) -> List:
        """Create multiple tables for an initiative when there are too many areas."""
        elements = []
        
        # Split areas into chunks
        area_chunks = [self.all_areas[i:i + max_areas] for i in range(0, len(self.all_areas), max_areas)]
        
        for chunk_idx, area_chunk in enumerate(area_chunks):
            if chunk_idx > 0:
                elements.append(Spacer(1, 0.2 * inch))
            
            # Add view indicator
            view_label = f"<i>View {chunk_idx + 1} of {len(area_chunks)}: Areas {', '.join(area_chunk)}</i>"
            elements.append(Paragraph(view_label, self.styles['InfoText']))
            elements.append(Spacer(1, 0.1 * inch))
            
            # Build table for this chunk of areas
            table_data, style_commands = self._build_initiative_table(initiative, area_chunk)
            
            if table_data and len(table_data) > 1:
                # Calculate column widths
                available_width = 10.5 * inch
                feature_col_width = 2.2 * inch
                area_total_width = available_width - feature_col_width
                area_col_width = area_total_width / len(area_chunk)
                col_widths = [feature_col_width] + [area_col_width] * len(area_chunk)
                
                initiative_table = Table(table_data, colWidths=col_widths)
                initiative_table.setStyle(TableStyle(style_commands))
                elements.append(initiative_table)
        
        return elements
    
    def _build_initiative_table(self, initiative: Dict, areas: List[str] = None) -> tuple:
        """
        Build table data for a single initiative.
        
        Args:
            initiative: Initiative data
            areas: List of areas to include (default: all areas)
        
        Returns: (table_data, style_commands)
        """
        if areas is None:
            areas = self.all_areas
        
        # Header row with area names
        header_row = ['Feature / Sub-Feature'] + [area for area in areas]
        table_data = [header_row]
        
        style_commands = [
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#667eea')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
            ('ALIGN', (0, 0), (-1, 0), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 10),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 10),
            ('TOPPADDING', (0, 0), (-1, 0), 10),
            ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor('#e2e8f0')),
            ('VALIGN', (0, 0), (-1, -1), 'TOP'),
            ('LEFTPADDING', (0, 0), (-1, -1), 8),
            ('RIGHTPADDING', (0, 0), (-1, -1), 8),
            ('TOPPADDING', (0, 1), (-1, -1), 10),
            ('BOTTOMPADDING', (0, 1), (-1, -1), 10),
        ]
        
        current_row = 1
        feature_start_row = 1
        
        for feature_idx, feature in enumerate(initiative.get('features', [])):
            feature_start_row = current_row
            
            # Add feature row (only in first column)
            feature_key = feature['key']
            feature_summary = feature['summary']
            
            # For wide format, show full summary; otherwise truncate
            if self.page_format in ['A3', 'wide']:
                summary_text = feature_summary
            else:
                summary_text = f"{feature_summary[:45]}..." if len(feature_summary) > 45 else feature_summary
            
            # Create clickable link if jira_url is available
            if self.jira_url:
                feature_link = f'<link href="{self.jira_url}/browse/{feature_key}">{feature_key}</link>'
            else:
                feature_link = feature_key
            
            feature_text = f"<b>🔹 FEATURE:</b> {feature_link}<br/><font size='8'><b>{summary_text}</b></font>"
            feature_row = [Paragraph(feature_text, self.styles['InfoText'])]
            
            # Empty cells for areas in feature row (using the provided areas list)
            for area in areas:
                feature_row.append('')
            
            table_data.append(feature_row)
            
            # Style for feature row - more prominent
            style_commands.append(('BACKGROUND', (0, current_row), (-1, current_row), colors.HexColor('#d6e4ff')))
            style_commands.append(('FONTNAME', (0, current_row), (0, current_row), 'Helvetica-Bold'))
            style_commands.append(('FONTSIZE', (0, current_row), (0, current_row), 8))  # Smaller font for better fit
            
            current_row += 1
            
            # Add sub-feature rows with epics
            for sub_feature in feature.get('sub_features', []):
                # Indented sub-feature text - more compact
                sub_key = sub_feature['key']
                sub_summary = sub_feature['summary']
                
                # For wide format, show full summary; otherwise truncate
                if self.page_format in ['A3', 'wide']:
                    sub_summary_text = sub_summary
                else:
                    sub_summary_text = f"{sub_summary[:30]}..." if len(sub_summary) > 30 else sub_summary
                
                # Create clickable link if jira_url is available
                if self.jira_url:
                    sub_link = f'<link href="{self.jira_url}/browse/{sub_key}">{sub_key}</link>'
                else:
                    sub_link = sub_key
                
                sub_feature_text = f"<b>    ↳ Sub:</b> {sub_link}<br/>    <font size='6'>{sub_summary_text}</font>"
                row = [Paragraph(sub_feature_text, self.styles['InfoText'])]
                
                # Get epics by area for this sub-feature
                epics_by_area = sub_feature.get('epics_by_area', {})
                
                # Add epic post-its for each area (only the specified areas)
                for area in areas:
                    epics_in_area = epics_by_area.get(area, [])
                    if epics_in_area:
                        # Limit epics per cell to prevent overflow
                        MAX_EPICS_PER_CELL = 8 if self.page_format == 'wide' else 6
                        
                        # Create post-it style cells for epics
                        epic_paragraphs = []
                        for idx, epic in enumerate(epics_in_area[:MAX_EPICS_PER_CELL]):
                            epic_text = self._create_epic_postit(epic)
                            # Extract background color from the text
                            if '---BGCOLOR:' in epic_text:
                                parts = epic_text.split('---BGCOLOR:')
                                clean_text = parts[0]
                                bg_hex = parts[1]
                                
                                # Create a custom style for this epic with background color
                                epic_style = ParagraphStyle(
                                    'EpicCell',
                                    parent=self.styles['EpicPostIt'],
                                    backColor=bg_hex,
                                    borderColor='#2d3748',
                                    borderWidth=1,
                                    borderPadding=4,
                                    spaceBefore=3,
                                    spaceAfter=3
                                )
                                epic_paragraphs.append(Paragraph(clean_text, epic_style))
                            else:
                                epic_paragraphs.append(Paragraph(epic_text, self.styles['EpicPostIt']))
                        
                        # Add indicator if there are more epics
                        if len(epics_in_area) > MAX_EPICS_PER_CELL:
                            more_count = len(epics_in_area) - MAX_EPICS_PER_CELL
                            more_text = f'<font size="6"><i>... and {more_count} more epic(s)</i></font>'
                            epic_paragraphs.append(Paragraph(more_text, self.styles['InfoText']))
                        
                        # Combine paragraphs in a single cell (they will stack vertically)
                        row.append(epic_paragraphs)
                    else:
                        row.append('')
                
                table_data.append(row)
                
                # Light background for sub-feature rows (first column only)
                style_commands.append(('BACKGROUND', (0, current_row), (0, current_row), colors.HexColor('#f7fafc')))
                # Keep epic cells with white background - colors are now in individual post-its
                style_commands.append(('BACKGROUND', (1, current_row), (-1, current_row), colors.white))
                
                current_row += 1
            
            # Add thick line after each feature group (double border)
            if current_row > feature_start_row + 1:  # Only if there were sub-features
                style_commands.append(
                    ('LINEBELOW', (0, current_row - 1), (-1, current_row - 1), 2.5, colors.HexColor('#667eea'))
                )
                # Add extra padding after feature group
                style_commands.append(
                    ('BOTTOMPADDING', (0, current_row - 1), (-1, current_row - 1), 12)
                )
        
        return table_data, style_commands
    
    def _create_epic_postit(self, epic: Dict) -> str:
        """Create a post-it style representation of an epic with its own background color."""
        key = epic.get('key', 'N/A')
        summary = epic.get('summary', 'No summary')
        status = epic.get('status', 'Unknown')
        
        # For wide format, show full summary; otherwise truncate
        if self.page_format in ['A3', 'wide']:
            summary_text = summary
        else:
            summary_text = summary[:30] if len(summary) > 30 else summary
        
        # Determine background color for this specific epic
        if self._is_completed(epic):
            bg_color = self.COMPLETED_COLOR
            status_icon = '✓'
        else:
            risk = epic.get('risk_probability')
            bg_color = self.RISK_COLORS.get(risk, self.RISK_COLORS[None])
            status_icon = '○'
        
        # Convert color to hex for HTML
        bg_hex = f'#{int(bg_color.red*255):02x}{int(bg_color.green*255):02x}{int(bg_color.blue*255):02x}'
        
        # Create clickable link if jira_url is available
        if self.jira_url:
            key_link = f'<link href="{self.jira_url}/browse/{key}">{key}</link>'
        else:
            key_link = key
        
        # Create post-it with smaller font
        postit = f'<font size="7"><b>{status_icon} {key_link}</b><br/>{summary_text}<br/><font size="5">{status}</font></font>---BGCOLOR:{bg_hex}'
        return postit
    
    def _is_completed(self, epic: Dict) -> bool:
        """Check if an epic is completed based on its status."""
        status = epic.get('status', '').lower()
        return status in self.completed_statuses
