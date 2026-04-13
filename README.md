# OSINT Prototype Tool

A prototype automated OSINT capability based on the Modular Adapter Pattern. It aggregates and cross-references data from disparate open sources and generates a professional report.

## Setup Instructions

1. **Install Dependencies**
   ```bash
   pip install -r requirements.txt
   ```

2. **Run the Tool**
   The tool takes a single input string specifying the target. For best results, use the format: `"<Name>, <Title> of <Company>"`.
   ```bash
   python main.py "Travis Haasch, CEO of AIGeeks"
   ```

## Architecture Details

- **Modular Adapter Pattern**: Each data source lives as a standalone module inside the `adapters/` directory, subclassing `BaseAdapter`. This allows developers to easily hot-swap or add new sources (like Shodan, HaveIBeenPwned) without altering the main orchestration flow.
- **Entity Resolution Engine**: Uses fuzzy string matching (`thefuzz`) to perform basic disambiguation, cross-checking findings against the target company and name to drop low-confidence entries.
- **Risk Scoring**: Implements custom logic rules to classify discovered data points as Low, Medium, High, or Critical.
- **OPSEC Considerations**: Adapters feature configurable delays (jitter) and rotating `User-Agent` headers to masquerade as standard browser traffic, mitigating blocks and IP bans.

## Output
Reports are generated in the `reports/` directory in both Markdown and PDF formats. They contain:
- Executive Summary
- Structured Asset Tables
- OSINT Audit Trail
