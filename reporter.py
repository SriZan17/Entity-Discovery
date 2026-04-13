import os
from fpdf import FPDF
from core import IntelligenceReport
from datetime import datetime

class Reporter:
    """
    Generates professional reports in Markdown and PDF formats.
    """
    def __init__(self, output_dir: str = "reports"):
        self.output_dir = output_dir
        if not os.path.exists(output_dir):
            os.makedirs(output_dir)

    def generate_report(self, report: IntelligenceReport):
        self._generate_markdown(report)
        self._generate_pdf(report)

    def _generate_markdown(self, report: IntelligenceReport):
        filename = f"{self.output_dir}/{report.target.name.replace(' ', '_')}_OSINT_Report.md"
        if not report.target.name:
            filename = f"{self.output_dir}/OSINT_Report_{int(datetime.utcnow().timestamp())}.md"
            
        with open(filename, 'w', encoding='utf-8') as f:
            f.write(f"# OSINT Intelligence Report\n\n")
            f.write(f"**Target:** {report.target.raw_query}\n")
            if report.target.name:
                f.write(f"**Name:** {report.target.name}\n")
            if report.target.company:
                f.write(f"**Company:** {report.target.company}\n")
            f.write(f"**Date Generated:** {datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S UTC')}\n\n")
            
            f.write(f"## Executive Summary\n")
            f.write(f"{report.executive_summary}\n\n")
            
            f.write(f"## Discovered Assets by Category\n\n")
            
            # Group by category
            categories = set(dp.category for dp in report.data_points)
            for category in categories:
                f.write(f"### {category}\n")
                cat_dps = report.get_by_category(category)
                f.write("| Value | Description | Risk | Confidence |\n")
                f.write("|-------|-------------|------|------------|\n")
                for dp in cat_dps:
                    clean_val = dp.value.replace("\r", " ").replace("\n", " ")[:50]
                    clean_desc = dp.description.replace("\r", " ").replace("\n", " ")[:50]
                    f.write(f"| {clean_val}... | {clean_desc}... | {dp.risk_level} | {dp.confidence}% |\n")
                f.write("\n")
            
            f.write(f"## Audit Trail\n")
            f.write("| ID | Source URL | Retrieval Timestamp |\n")
            f.write("|----|------------|---------------------|\n")
            for i, dp in enumerate(report.data_points):
                f.write(f"| {i+1} | <{dp.url}> | {dp.timestamp.strftime('%Y-%m-%d %H:%M:%S UTC')} |\n")
            
        print(f"[+] Markdown report generated: {filename}")

    def _generate_pdf(self, report: IntelligenceReport):
        filename = f"{self.output_dir}/{report.target.name.replace(' ', '_')}_OSINT_Report.pdf"
        if not report.target.name:
            filename = f"{self.output_dir}/OSINT_Report_{int(datetime.utcnow().timestamp())}.pdf"
            
        pdf = FPDF()
        pdf.add_page()
        pdf.set_font("Arial", 'B', 16)
        pdf.cell(0, 10, "OSINT Intelligence Report", ln=True, align="C")
        pdf.ln(10)
        
        pdf.set_font("Arial", size=12)
        pdf.cell(0, 10, f"Target: {report.target.raw_query}", ln=True)
        pdf.cell(0, 10, f"Date: {datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S UTC')}", ln=True)
        pdf.ln(10)
        
        pdf.set_font("Arial", 'B', 14)
        pdf.cell(0, 10, "Executive Summary", ln=True)
        pdf.set_font("Arial", size=12)
        pdf.multi_cell(0, 8, report.executive_summary)
        pdf.ln(5)
        
        pdf.set_font("Arial", 'B', 14)
        pdf.cell(0, 10, "Categorized Discovered Assets", ln=True)
        categories = set(dp.category for dp in report.data_points)
        for category in categories:
            pdf.ln(3)
            pdf.set_font("Arial", 'B', 12)
            pdf.cell(0, 8, category, ln=True)
            pdf.set_font("Arial", size=10)
            
            cat_dps = report.get_by_category(category)
            for dp in cat_dps:
                clean_val = dp.value.encode('ascii', 'ignore').decode().replace("\n", " ").strip()
                clean_desc = dp.description.encode('ascii', 'ignore').decode().replace("\n", " ").strip()
                pdf.multi_cell(0, 6, f"> [{dp.risk_level}] {clean_val[:60]}... | {clean_desc[:60]}...")
                
        pdf.ln(10)
        pdf.set_font("Arial", 'B', 14)
        pdf.cell(0, 10, "Audit Trail", ln=True)
        pdf.set_font("Arial", size=10)
        for i, dp in enumerate(report.data_points):
            url = dp.url.encode('ascii', 'ignore').decode()
            time_str = dp.timestamp.strftime('%Y-%m-%d %H:%M:%S UTC')
            pdf.multi_cell(0, 6, f"{i+1}. {time_str} | Source: {url}")
            
        pdf.output(filename)
        print(f"[+] PDF report generated: {filename}")
