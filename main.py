import sys
import re
import argparse
from core import Target, IntelligenceReport
from adapters import SearchAdapter, InfrastructureAdapter, ContextualAdapter
from engine import EntityResolver, RiskEngine
from reporter import Reporter

def parse_target_string(raw_str: str) -> Target:
    """
    Parses a string like "Travis Haasch, CEO of AIGeeks"
    """
    target = Target(raw_query=raw_str)
    
    # Try to extract Name and Company
    # e.g. "Name, Title of/at Company" or "Name CEO of Company"
    match = re.search(r"([^,]+)(?:,|\s).*(?:of|at)\s+(.*)", raw_str, re.IGNORECASE)
    if match:
        target.name = match.group(1).strip()
        target.company = match.group(2).strip()
    else:
        # Fallback: just split by spaces and try to guess, or treat as one big blob
        parts = raw_str.split(" of ")
        if len(parts) == 2:
            target.name = parts[0].split(",")[0].strip()
            target.company = parts[1].strip()
            
    # Default to raw if both missing
    if not target.name and not target.company:
        target.name = raw_str
        
    print(f"[*] Target interpreted as -> Name: '{target.name}', Company: '{target.company}'")
    return target

def main():
    parser = argparse.ArgumentParser(description="OSINT Prototype Tool")
    parser.add_argument("target_string", help="Target string (e.g., 'Travis Haasch, CEO of AIGeeks')")
    parser.add_argument("--location", help="Provide a location to decrease false positives", default="")
    parser.add_argument("--industry", help="Provide an industry to decrease false positives", default="")
    args = parser.parse_args()
        
    raw_query = args.target_string
    print(f"[*] Initializing OSINT Workflow for: {raw_query}")
    
    # Initialize Core Structures
    target = parse_target_string(raw_query)
    target.location = args.location
    target.industry = args.industry
    
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
    
    # Phase III: Reporting
    print("[*] Generating Professional Reports...")
    reporter = Reporter()
    reporter.generate_report(report)
    
    print("[+] Workflow complete.")

if __name__ == "__main__":
    main()
