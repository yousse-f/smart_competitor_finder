"""
Advanced Excel Report Generator for Smart Competitor Finder
Generates comprehensive Excel reports with keyword, semantic, and sector analysis data
"""

import pandas as pd
from openpyxl import Workbook
from openpyxl.styles import Font, Fill, PatternFill, Alignment, Border, Side
from openpyxl.chart import BarChart, Reference
from openpyxl.utils.dataframe import dataframe_to_rows
from openpyxl.utils import get_column_letter
from openpyxl.formatting.rule import ColorScaleRule
from datetime import datetime
from typing import List, Dict, Any
import os


class ReportGenerator:
    """Advanced Excel report generator with professional formatting and multiple sheets"""
    
    def __init__(self):
        self.workbook = None
        self.styles = self._init_styles()
    
    def _init_styles(self) -> Dict[str, Any]:
        """Initialize Excel styling configurations"""
        return {
            'header': {
                'font': Font(bold=True, color='FFFFFF', size=12),
                'fill': PatternFill(start_color='366092', end_color='366092', fill_type='solid'),
                'alignment': Alignment(horizontal='center', vertical='center')
            },
            'subheader': {
                'font': Font(bold=True, color='366092', size=11),
                'fill': PatternFill(start_color='E6F2FF', end_color='E6F2FF', fill_type='solid'),
                'alignment': Alignment(horizontal='center', vertical='center')
            },
            'data': {
                'font': Font(size=10),
                'alignment': Alignment(horizontal='left', vertical='center', wrap_text=True)
            },
            'number': {
                'font': Font(size=10),
                'alignment': Alignment(horizontal='center', vertical='center'),
                'number_format': '0.0%'
            },
            'border': Border(
                left=Side(style='thin'),
                right=Side(style='thin'),
                top=Side(style='thin'),
                bottom=Side(style='thin')
            )
        }
    
    def generate_comprehensive_report(
        self,
        client_url: str,
        client_keywords: List[str],
        analysis_results: List[Dict],
        output_path: str = None
    ) -> str:
        """
        Generate comprehensive Excel report with multiple sheets
        
        Args:
            client_url: The analyzed client website URL
            client_keywords: Selected keywords for analysis
            analysis_results: List of competitor analysis results
            output_path: Custom output file path
            
        Returns:
            str: Path to generated Excel file
        """
        # Create workbook
        self.workbook = Workbook()
        
        # Remove default sheet
        if 'Sheet' in [ws.title for ws in self.workbook.worksheets]:
            self.workbook.remove(self.workbook['Sheet'])
        
        # Generate different sheets
        self._create_summary_sheet(client_url, client_keywords, analysis_results)
        self._create_detailed_results_sheet(analysis_results)
        self._create_sector_analysis_sheet(analysis_results)
        self._create_keyword_analysis_sheet(analysis_results, client_keywords)
        self._create_semantic_analysis_sheet(analysis_results)
        
        # Generate output path if not provided
        if not output_path:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            output_path = f"reports/competitor_analysis_{timestamp}.xlsx"
        
        # Create reports directory if it doesn't exist
        os.makedirs(os.path.dirname(output_path), exist_ok=True)
        
        # Save workbook
        self.workbook.save(output_path)
        
        return output_path
    
    def _create_summary_sheet(
        self,
        client_url: str,
        client_keywords: List[str],
        analysis_results: List[Dict]
    ):
        """Create executive summary sheet"""
        ws = self.workbook.create_sheet("Executive Summary", 0)
        
        # Title and metadata
        ws['A1'] = "Smart Competitor Finder - Analysis Report"
        ws['A1'].font = Font(bold=True, size=16, color='366092')
        ws.merge_cells('A1:F1')
        
        ws['A3'] = f"Client Website: {client_url}"
        ws['A4'] = f"Analysis Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
        ws['A5'] = f"Keywords Analyzed: {', '.join(client_keywords)}"
        ws['A6'] = f"Total Competitors Analyzed: {len(analysis_results)}"
        
        # Summary statistics
        relevant_competitors = [r for r in analysis_results if r.get('is_relevant', True)]
        high_match_competitors = [r for r in relevant_competitors if r.get('total_score', 0) >= 0.5]
        
        ws['A8'] = "ANALYSIS SUMMARY"
        ws['A8'].font = Font(bold=True, size=14, color='366092')
        
        summary_data = [
            ["Metric", "Value"],
            ["Relevant Competitors Found", len(relevant_competitors)],
            ["High Match Competitors (≥50%)", len(high_match_competitors)],
            ["Average Match Score", f"{sum(r.get('total_score', 0) for r in relevant_competitors) / len(relevant_competitors) * 100:.1f}%" if relevant_competitors else "0%"],
            ["Best Match Score", f"{max(r.get('total_score', 0) for r in relevant_competitors) * 100:.1f}%" if relevant_competitors else "0%"]
        ]
        
        for row_idx, row_data in enumerate(summary_data, 10):
            for col_idx, value in enumerate(row_data, 1):
                cell = ws.cell(row=row_idx, column=col_idx, value=value)
                if row_idx == 10:  # Header row
                    cell.font = self.styles['header']['font']
                    cell.fill = self.styles['header']['fill']
                    cell.alignment = self.styles['header']['alignment']
                cell.border = self.styles['border']
        
        # Top 10 competitors
        ws['A16'] = "TOP 10 COMPETITORS"
        ws['A16'].font = Font(bold=True, size=14, color='366092')
        
        # Sort by total score and take top 10
        top_competitors = sorted(
            relevant_competitors,
            key=lambda x: x.get('total_score', 0),
            reverse=True
        )[:10]
        
        headers = ["Rank", "Website", "Match Score", "Sector", "Relevance"]
        for col_idx, header in enumerate(headers, 1):
            cell = ws.cell(row=18, column=col_idx, value=header)
            cell.font = self.styles['header']['font']
            cell.fill = self.styles['header']['fill']
            cell.alignment = self.styles['header']['alignment']
            cell.border = self.styles['border']
        
        for row_idx, competitor in enumerate(top_competitors, 19):
            row_data = [
                row_idx - 18,
                competitor.get('url', 'N/A'),
                f"{competitor.get('total_score', 0) * 100:.1f}%",
                competitor.get('sector', 'Unknown'),
                "Yes" if competitor.get('is_relevant', True) else "No"
            ]
            
            for col_idx, value in enumerate(row_data, 1):
                cell = ws.cell(row=row_idx, column=col_idx, value=value)
                cell.font = self.styles['data']['font']
                cell.alignment = self.styles['data']['alignment']
                cell.border = self.styles['border']
                
                # Special formatting for match score
                if col_idx == 3:
                    cell.alignment = self.styles['number']['alignment']
        
        # Auto-adjust column widths
        self._auto_adjust_columns(ws)
    
    def _create_detailed_results_sheet(self, analysis_results: List[Dict]):
        """Create detailed results sheet with all competitor data"""
        ws = self.workbook.create_sheet("Detailed Results")
        
        # Headers
        headers = [
            "URL", "Total Score", "Keyword Score", "Semantic Score",
            "Sector", "Is Relevant", "Keywords Found", "Keyword Count",
            "Semantic Similarity", "Relevance Label", "Analysis Notes"
        ]
        
        for col_idx, header in enumerate(headers, 1):
            cell = ws.cell(row=1, column=col_idx, value=header)
            cell.font = self.styles['header']['font']
            cell.fill = self.styles['header']['fill']
            cell.alignment = self.styles['header']['alignment']
            cell.border = self.styles['border']
        
        # Data rows
        for row_idx, result in enumerate(analysis_results, 2):
            row_data = [
                result.get('url', 'N/A'),
                result.get('total_score', 0),
                result.get('keyword_score', 0),
                result.get('semantic_score', 0),
                result.get('sector', 'Unknown'),
                "Yes" if result.get('is_relevant', True) else "No",
                ', '.join(result.get('keywords_found', [])),
                len(result.get('keywords_found', [])),
                result.get('semantic_similarity', 0),
                result.get('relevance_label', 'Unknown'),
                result.get('analysis_notes', '')
            ]
            
            for col_idx, value in enumerate(row_data, 1):
                cell = ws.cell(row=row_idx, column=col_idx, value=value)
                cell.border = self.styles['border']
                
                # Apply specific formatting based on column type
                if col_idx in [2, 3, 4, 9]:  # Score columns
                    cell.number_format = '0.0%'
                    cell.alignment = self.styles['number']['alignment']
                elif col_idx == 8:  # Count column
                    cell.alignment = Alignment(horizontal='center')
                else:
                    cell.font = self.styles['data']['font']
                    cell.alignment = self.styles['data']['alignment']
        
        # Apply conditional formatting for scores
        score_range = f"B2:B{len(analysis_results) + 1}"
        color_scale = ColorScaleRule(
            start_type='min', start_color='F8696B',
            mid_type='percentile', mid_value=50, mid_color='FFEB9C',
            end_type='max', end_color='63BE7B'
        )
        ws.conditional_formatting.add(score_range, color_scale)
        
        # Auto-adjust column widths
        self._auto_adjust_columns(ws)
    
    def _create_sector_analysis_sheet(self, analysis_results: List[Dict]):
        """Create sector analysis breakdown sheet"""
        ws = self.workbook.create_sheet("Sector Analysis")
        
        # Count competitors by sector
        sector_counts = {}
        sector_avg_scores = {}
        
        for result in analysis_results:
            sector = result.get('sector', 'Unknown')
            if sector not in sector_counts:
                sector_counts[sector] = 0
                sector_avg_scores[sector] = []
            
            sector_counts[sector] += 1
            if result.get('total_score'):
                sector_avg_scores[sector].append(result['total_score'])
        
        # Calculate average scores
        for sector in sector_avg_scores:
            if sector_avg_scores[sector]:
                sector_avg_scores[sector] = sum(sector_avg_scores[sector]) / len(sector_avg_scores[sector])
            else:
                sector_avg_scores[sector] = 0
        
        # Create sector summary table
        ws['A1'] = "SECTOR DISTRIBUTION ANALYSIS"
        ws['A1'].font = Font(bold=True, size=14, color='366092')
        
        headers = ["Sector", "Count", "Avg Score", "Relevance"]
        for col_idx, header in enumerate(headers, 1):
            cell = ws.cell(row=3, column=col_idx, value=header)
            cell.font = self.styles['header']['font']
            cell.fill = self.styles['header']['fill']
            cell.alignment = self.styles['header']['alignment']
            cell.border = self.styles['border']
        
        row_idx = 4
        for sector in sorted(sector_counts.keys()):
            relevant_count = len([r for r in analysis_results 
                                if r.get('sector') == sector and r.get('is_relevant', True)])
            
            row_data = [
                sector,
                sector_counts[sector],
                sector_avg_scores[sector],
                f"{relevant_count}/{sector_counts[sector]}"
            ]
            
            for col_idx, value in enumerate(row_data, 1):
                cell = ws.cell(row=row_idx, column=col_idx, value=value)
                cell.border = self.styles['border']
                
                if col_idx == 3:  # Average score
                    cell.number_format = '0.0%'
                    cell.alignment = self.styles['number']['alignment']
                else:
                    cell.font = self.styles['data']['font']
                    cell.alignment = self.styles['data']['alignment']
            
            row_idx += 1
        
        # Auto-adjust column widths
        self._auto_adjust_columns(ws)
    
    def _create_keyword_analysis_sheet(self, analysis_results: List[Dict], client_keywords: List[str]):
        """Create keyword analysis breakdown sheet"""
        ws = self.workbook.create_sheet("Keyword Analysis")
        
        # Keyword frequency analysis
        keyword_frequency = {}
        for result in analysis_results:
            for keyword in result.get('keywords_found', []):
                if keyword.lower() in [k.lower() for k in client_keywords]:
                    if keyword not in keyword_frequency:
                        keyword_frequency[keyword] = 0
                    keyword_frequency[keyword] += 1
        
        ws['A1'] = "KEYWORD FREQUENCY ANALYSIS"
        ws['A1'].font = Font(bold=True, size=14, color='366092')
        
        headers = ["Keyword", "Frequency", "Percentage"]
        for col_idx, header in enumerate(headers, 1):
            cell = ws.cell(row=3, column=col_idx, value=header)
            cell.font = self.styles['header']['font']
            cell.fill = self.styles['header']['fill']
            cell.alignment = self.styles['header']['alignment']
            cell.border = self.styles['border']
        
        total_competitors = len(analysis_results)
        row_idx = 4
        
        for keyword in sorted(keyword_frequency.keys(), key=keyword_frequency.get, reverse=True):
            frequency = keyword_frequency[keyword]
            percentage = frequency / total_competitors if total_competitors > 0 else 0
            
            row_data = [keyword, frequency, percentage]
            
            for col_idx, value in enumerate(row_data, 1):
                cell = ws.cell(row=row_idx, column=col_idx, value=value)
                cell.border = self.styles['border']
                
                if col_idx == 3:  # Percentage
                    cell.number_format = '0.0%'
                    cell.alignment = self.styles['number']['alignment']
                else:
                    cell.font = self.styles['data']['font']
                    cell.alignment = self.styles['data']['alignment']
            
            row_idx += 1
        
        # Auto-adjust column widths
        self._auto_adjust_columns(ws)
    
    def _create_semantic_analysis_sheet(self, analysis_results: List[Dict]):
        """Create semantic analysis details sheet"""
        ws = self.workbook.create_sheet("Semantic Analysis")
        
        ws['A1'] = "SEMANTIC SIMILARITY ANALYSIS"
        ws['A1'].font = Font(bold=True, size=14, color='366092')
        
        # Filter results that have semantic analysis data
        semantic_results = [r for r in analysis_results if r.get('semantic_similarity') is not None]
        
        if not semantic_results:
            ws['A3'] = "No semantic analysis data available"
            return
        
        headers = ["URL", "Semantic Score", "Sector Match", "Content Summary"]
        for col_idx, header in enumerate(headers, 1):
            cell = ws.cell(row=3, column=col_idx, value=header)
            cell.font = self.styles['header']['font']
            cell.fill = self.styles['header']['fill']
            cell.alignment = self.styles['header']['alignment']
            cell.border = self.styles['border']
        
        # Sort by semantic score
        semantic_results.sort(key=lambda x: x.get('semantic_similarity', 0), reverse=True)
        
        for row_idx, result in enumerate(semantic_results, 4):
            row_data = [
                result.get('url', 'N/A'),
                result.get('semantic_similarity', 0),
                "Yes" if result.get('is_relevant', True) else "No",
                result.get('content_summary', 'N/A')[:100] + "..." if len(result.get('content_summary', '')) > 100 else result.get('content_summary', 'N/A')
            ]
            
            for col_idx, value in enumerate(row_data, 1):
                cell = ws.cell(row=row_idx, column=col_idx, value=value)
                cell.border = self.styles['border']
                
                if col_idx == 2:  # Semantic score
                    cell.number_format = '0.0%'
                    cell.alignment = self.styles['number']['alignment']
                else:
                    cell.font = self.styles['data']['font']
                    cell.alignment = self.styles['data']['alignment']
        
        # Auto-adjust column widths
        self._auto_adjust_columns(ws)
    
    def _auto_adjust_columns(self, worksheet):
        """Auto-adjust column widths based on content"""
        for column in worksheet.columns:
            max_length = 0
            column_letter = get_column_letter(column[0].column)
            
            for cell in column:
                try:
                    if len(str(cell.value)) > max_length:
                        max_length = len(str(cell.value))
                except:
                    pass
            
            adjusted_width = min(max_length + 2, 50)  # Cap at 50 characters
            worksheet.column_dimensions[column_letter].width = adjusted_width


def create_sample_report():
    """Create a sample report for testing"""
    generator = ReportGenerator()
    
    # Sample data
    client_url = "https://example-agency.com"
    client_keywords = ["digital marketing", "web design", "SEO", "advertising"]
    
    sample_results = [
        {
            "url": "https://competitor1.com",
            "total_score": 0.85,
            "keyword_score": 0.75,
            "semantic_score": 0.90,
            "sector": "Digital Marketing",
            "is_relevant": True,
            "keywords_found": ["digital marketing", "SEO"],
            "semantic_similarity": 0.90,
            "relevance_label": "Highly Relevant",
            "analysis_notes": "Strong competitor in digital marketing space"
        },
        {
            "url": "https://competitor2.com",
            "total_score": 0.45,
            "keyword_score": 0.30,
            "semantic_score": 0.55,
            "sector": "Web Development",
            "is_relevant": True,
            "keywords_found": ["web design"],
            "semantic_similarity": 0.55,
            "relevance_label": "Moderately Relevant",
            "analysis_notes": "Focuses more on development than marketing"
        }
    ]
    
    return generator.generate_comprehensive_report(
        client_url, client_keywords, sample_results, "sample_report.xlsx"
    )


if __name__ == "__main__":
    # Test the report generator
    report_path = create_sample_report()
    print(f"Sample report generated: {report_path}")