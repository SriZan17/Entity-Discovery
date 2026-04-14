import gradio as gr
import re
from core import Target, IntelligenceReport
from adapters import SearchAdapter, InfrastructureAdapter, ContextualAdapter
from engine import EntityResolver, RiskEngine
from reporter import Reporter
from datetime import datetime
import io
from contextlib import redirect_stdout

def parse_target_string(raw_str: str) -> Target:
    """
    Parses a string like "Travis Haasch, CEO of AIGeeks"
    """
    target = Target(raw_query=raw_str)
    
    # Try to extract Name and Company
    match = re.search(r"([^,]+)(?:,|\s).*(?:of|at)\s+(.*)", raw_str, re.IGNORECASE)
    if match:
        target.name = match.group(1).strip()
        target.company = match.group(2).strip()
    else:
        parts = raw_str.split(" of ")
        if len(parts) == 2:
            target.name = parts[0].split(",")[0].strip()
            target.company = parts[1].strip()
            
    if not target.name and not target.company:
        target.name = raw_str
        
    return target

def run_osint_investigation(target_string: str, location: str = "", industry: str = "") -> tuple:
    """
    Runs the OSINT investigation and returns formatted results.
    """
    try:
        if not target_string.strip():
            return "Error: Please enter a target string", ""
        
        # Capture output
        output_buffer = io.StringIO()
        
        with redirect_stdout(output_buffer):
            # Parse target
            target = parse_target_string(target_string)
            target.location = location
            target.industry = industry
            
            print(f"[*] Initializing OSINT Workflow for: {target_string}")
            
            # Initialize Adapters
            adapters = [
                SearchAdapter(),
                InfrastructureAdapter(),
                ContextualAdapter()
            ]
            
            # Phase I: Acquisition
            raw_data = []
            for adapter in adapters:
                print(f"[*] Running adapter: {adapter.name}...")
                findings = adapter.execute(target)
                raw_data.extend(findings)
                print(f"    - Found {len(findings)} initial records.")
            
            # Phase II: Intelligence Logic
            print("[*] Running Entity Resolution Engine...")
            resolver = EntityResolver(confidence_threshold=40)
            resolved_data = resolver.resolve(target, raw_data)
            
            print("[*] Running Risk Scoring Engine...")
            risk_engine = RiskEngine()
            risk_engine.evaluate(resolved_data)
            
            # Generate Summary
            high_critical_count = len([x for x in resolved_data if x.risk_level in ["High", "Critical"]])
            summary = (
                f"Automated OSINT investigation on {target.raw_query} yielded {len(resolved_data)} "
                f"validated data points from {len(adapters)} distinct source vectors. "
                f"There are {high_critical_count} findings that require immediate attention."
            )
            
            report = IntelligenceReport(
                target=target,
                data_points=resolved_data,
                executive_summary=summary
            )
            
            # Generate markdown report inline
            markdown_report = generate_markdown_report(report)
            
            print("[+] Workflow complete.")
        
        # Get captured console output
        console_output = output_buffer.getvalue()
        
        return markdown_report, console_output
        
    except Exception as e:
        error_msg = f"Error during investigation: {str(e)}"
        return error_msg, str(e)

def generate_markdown_report(report: IntelligenceReport) -> str:
    """
    Generates a markdown report as a string (for web display).
    """
    md = f"# OSINT Intelligence Report\n\n"
    md += f"**Target:** {report.target.raw_query}\n"
    if report.target.name:
        md += f"**Name:** {report.target.name}\n"
    if report.target.company:
        md += f"**Company:** {report.target.company}\n"
    md += f"**Date Generated:** {datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S UTC')}\n\n"
    
    md += f"## Executive Summary\n"
    md += f"{report.executive_summary}\n\n"
    
    md += f"## Discovered Assets by Category\n\n"
    
    if not report.data_points:
        md += "No data points discovered.\n\n"
    else:
        categories = set(dp.category for dp in report.data_points)
        for category in categories:
            md += f"### {category}\n"
            cat_dps = report.get_by_category(category)
            md += "| Value | Description | Risk | Confidence |\n"
            md += "|-------|-------------|------|------------|\n"
            for dp in cat_dps:
                clean_val = dp.value.replace("\r", " ").replace("\n", " ")[:50]
                clean_desc = dp.description.replace("\r", " ").replace("\n", " ")[:50]
                md += f"| {clean_val}... | {clean_desc}... | {dp.risk_level} | {dp.confidence}% |\n"
            md += "\n"
    
    return md

# Create Gradio interface
with gr.Blocks(title="OSINT Investigation Tool") as demo:
    gr.Markdown("# 🔍 OSINT Investigation Tool")
    gr.Markdown("Enter target information to run an automated OSINT investigation. Results are generated in real-time.")
    
    with gr.Row():
        with gr.Column():
            target_input = gr.Textbox(
                label="Target String",
                placeholder="e.g., Travis Haasch, CEO of AIGeeks",
                info="Format: Name, Title of Company"
            )
            location_input = gr.Textbox(
                label="Location (Optional)",
                placeholder="e.g., San Francisco, USA",
                info="Helps decrease false positives"
            )
            industry_input = gr.Textbox(
                label="Industry (Optional)",
                placeholder="e.g., Technology, Finance",
                info="Helps decrease false positives"
            )
            investigate_btn = gr.Button("🚀 Start Investigation", variant="primary")
    
    with gr.Row():
        with gr.Column():
            report_output = gr.Markdown(
                label="Intelligence Report",
                value="Results will appear here..."
            )
        with gr.Column():
            console_output = gr.Textbox(
                label="Investigation Log",
                lines=15,
                interactive=False,
                value="Logs will appear here..."
            )
    
    investigate_btn.click(
        fn=run_osint_investigation,
        inputs=[target_input, location_input, industry_input],
        outputs=[report_output, console_output]
    )
    
    gr.Markdown("""
    ---
    ### About this Tool
    This OSINT tool aggregates data from multiple sources including:
    - **Search Adapter**: Public search engines and databases
    - **Infrastructure Adapter**: DNS, domain, and network information
    - **Contextual Adapter**: Social media and contextual data
    
    The investigation performs entity resolution, confidence scoring, and risk assessment.
    """)

if __name__ == "__main__":
    demo.launch(server_name="0.0.0.0", server_port=7860)
