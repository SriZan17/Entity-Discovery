---
title: OSINT Investigation Tool
emoji: 🔍
colorFrom: blue
colorTo: green
sdk: gradio
sdk_version: 4.0.0
app_file: app.py
pinned: false
license: mit
---

# OSINT Prototype Tool

A prototype automated OSINT capability based on the Modular Adapter Pattern. It aggregates and cross-references data from disparate open sources and generates a professional report.

## 🚀 Quick Start (Web Interface)

This Space runs a **Gradio interface** for easy web-based access. Simply:

1. Enter a target string (e.g., "Travis Haasch, CEO of AIGeeks")
2. Optionally specify location and industry to reduce false positives
3. Click "Start Investigation"
4. View the intelligence report and investigation logs

## 📋 Setup Instructions (Local Development)

1. **Install Dependencies**

   ```bash
   pip install -r requirements.txt
   ```

2. **Run the Web Interface Locally**

   ```bash
   python app.py
   ```

   Then open `http://localhost:7860` in your browser.

3. **Run the CLI Tool**
   For command-line usage, the tool takes a single input string specifying the target. For best results, use the format: `"<Name>, <Title> of <Company>"`.

   ```bash
   python main.py "Travis Haasch, CEO of AIGeeks"
   ```

   Optional flags:

   ```bash
   python main.py "Travis Haasch, CEO of AIGeeks" --location "San Francisco" --industry "Technology"
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
