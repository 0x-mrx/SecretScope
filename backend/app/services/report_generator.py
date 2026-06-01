import os
from typing import List, Dict, Any
from jinja2 import Template
from sqlalchemy.orm import Session
from datetime import datetime

from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, PageBreak, Image
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle

from app.core.config import settings
from app.services.storage_manager import storage_manager
from app.models.finding import Finding
from app.models.project import Project
from app.models.report import Report
from app.models.user import User

# HTML Template
HTML_REPORT_TEMPLATE = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <title>SecretScope Security Compliance Report - {{ project_name }}</title>
    <style>
        body { font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; background-color: #0f172a; color: #f8fafc; margin: 0; padding: 40px; }
        .container { max-width: 1000px; margin: 0 auto; background-color: #1e293b; border-radius: 12px; padding: 40px; box-shadow: 0 4px 6px -1px rgba(0,0,0,0.5); }
        h1 { color: #f43f5e; border-bottom: 2px solid #334155; padding-bottom: 15px; margin-top: 0; }
        h2 { color: #38bdf8; margin-top: 30px; }
        .summary-grid { display: grid; grid-template-columns: repeat(4, 1fr); gap: 20px; margin-bottom: 30px; }
        .stat-card { background-color: #0f172a; border-radius: 8px; padding: 20px; text-align: center; border: 1px solid #334155; }
        .stat-val { font-size: 32px; font-weight: bold; margin-bottom: 5px; }
        .stat-label { font-size: 14px; color: #94a3b8; text-transform: uppercase; }
        .CRITICAL { color: #f43f5e; }
        .HIGH { color: #f97316; }
        .MEDIUM { color: #eab308; }
        .LOW { color: #3b82f6; }
        table { width: 100%; border-collapse: collapse; margin-top: 20px; }
        th, td { padding: 12px; text-align: left; border-bottom: 1px solid #334155; }
        th { background-color: #0f172a; color: #94a3b8; }
        .badge { display: inline-block; padding: 4px 8px; border-radius: 4px; font-size: 12px; font-weight: bold; text-transform: uppercase; }
        .badge-crit { background-color: #f43f5e; color: #ffffff; }
        .badge-high { background-color: #f97316; color: #ffffff; }
        .badge-med { background-color: #eab308; color: #000000; }
        .badge-low { background-color: #3b82f6; color: #ffffff; }
    </style>
</head>
<body>
    <div class="container">
        <h1>SecretScope Executive Compliance Report</h1>
        <p><strong>Project:</strong> {{ project_name }}</p>
        <p><strong>Generated At:</strong> {{ generated_at }}</p>
        
        <h2>Summary Statistics</h2>
        <div class="summary-grid">
            <div class="stat-card"><div class="stat-val CRITICAL">{{ stats.critical }}</div><div class="stat-label">Critical</div></div>
            <div class="stat-card"><div class="stat-val HIGH">{{ stats.high }}</div><div class="stat-label">High</div></div>
            <div class="stat-card"><div class="stat-val MEDIUM">{{ stats.medium }}</div><div class="stat-label">Medium</div></div>
            <div class="stat-card"><div class="stat-val LOW">{{ stats.low }}</div><div class="stat-label">Low</div></div>
        </div>

        <h2>Detailed Findings</h2>
        <table>
            <thead>
                <tr>
                    <th>ID</th>
                    <th>Secret Type</th>
                    <th>Severity</th>
                    <th>Risk Score</th>
                    <th>Location / Asset</th>
                </tr>
            </thead>
            <tbody>
                {% for finding in findings %}
                <tr>
                    <td>#{{ finding.id }}</td>
                    <td>{{ finding.secret_type }}</td>
                    <td>
                        {% if finding.severity == 'CRITICAL' %}
                        <span class="badge badge-crit">Critical</span>
                        {% elif finding.severity == 'HIGH' %}
                        <span class="badge badge-high">High</span>
                        {% elif finding.severity == 'MEDIUM' %}
                        <span class="badge badge-med">Medium</span>
                        {% else %}
                        <span class="badge badge-low">Low</span>
                        {% endif %}
                    </td>
                    <td>{{ finding.risk_score }}</td>
                    <td><code>{{ finding.file_path_or_url }}</code></td>
                </tr>
                {% endfor %}
            </tbody>
        </table>
    </div>
</body>
</html>
"""

# MD Template
MD_REPORT_TEMPLATE = """# SecretScope Security Compliance Report: {{ project_name }}
Generated on: {{ generated_at }}

## Executive Summary
| Severity | Count |
| --- | --- |
| Critical | {{ stats.critical }} |
| High | {{ stats.high }} |
| Medium | {{ stats.medium }} |
| Low | {{ stats.low }} |
| **Total** | **{{ findings|length }}** |

## Detailed Findings
{% for finding in findings %}
### Finding #{{ finding.id }}: {{ finding.secret_type }}
* **Severity:** {{ finding.severity }}
* **Risk Score:** {{ finding.risk_score }}
* **Exposure Risk:** {{ finding.exposure_risk }}
* **Compliance Risk:** {{ finding.compliance_risk }}
* **Operational Risk:** {{ finding.operational_risk }}
* **Location:** `{{ finding.file_path_or_url }}`
* **Status:** {{ finding.status }}
* **Remediation Notes:** {{ finding.remediation_notes or "N/A" }}

---
{% endfor %}
"""

class ReportGenerator:
    @staticmethod
    def generate_html_report(project_name: str, findings: List[Dict], stats: Dict) -> str:
        template = Template(HTML_REPORT_TEMPLATE)
        return template.render(
            project_name=project_name,
            findings=findings,
            stats=stats,
            generated_at=datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S UTC")
        )

    @staticmethod
    def generate_markdown_report(project_name: str, findings: List[Dict], stats: Dict) -> str:
        template = Template(MD_REPORT_TEMPLATE)
        return template.render(
            project_name=project_name,
            findings=findings,
            stats=stats,
            generated_at=datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S UTC")
        )

    @staticmethod
    def generate_pdf_report(project_name: str, findings: List[Dict], stats: Dict, output_path: str):
        doc = SimpleDocTemplate(
            output_path, 
            pagesize=letter,
            rightMargin=30, leftMargin=30, topMargin=30, bottomMargin=30
        )
        
        styles = getSampleStyleSheet()
        # Custom styles for Dark / Secure theme look on paper
        title_style = ParagraphStyle(
            'ReportTitle',
            parent=styles['Heading1'],
            textColor=colors.HexColor('#f43f5e'),
            fontSize=24,
            spaceAfter=15
        )
        subtitle_style = ParagraphStyle(
            'ReportSubtitle',
            parent=styles['Normal'],
            textColor=colors.HexColor('#475569'),
            fontSize=12,
            spaceAfter=30
        )
        heading_style = ParagraphStyle(
            'SectionHeading',
            parent=styles['Heading2'],
            textColor=colors.HexColor('#0284c7'),
            fontSize=16,
            spaceBefore=15,
            spaceAfter=10
        )
        body_style = ParagraphStyle(
            'Body',
            parent=styles['BodyText'],
            fontSize=10,
            leading=14
        )

        elements = []
        
        # Cover/Header
        elements.append(Paragraph("SecretScope Compliance Report", title_style))
        elements.append(Paragraph(f"Project: {project_name} | Generated At: {datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S UTC')}", subtitle_style))
        elements.append(Spacer(1, 10))

        # Metrics Card table
        summary_data = [
            ["Critical", "High", "Medium", "Low"],
            [str(stats.get("critical", 0)), str(stats.get("high", 0)), str(stats.get("medium", 0)), str(stats.get("low", 0))]
        ]
        t_summary = Table(summary_data, colWidths=[130, 130, 130, 130])
        t_summary.setStyle(TableStyle([
            ('BACKGROUND', (0,0), (-1,0), colors.HexColor('#0f172a')),
            ('TEXTCOLOR', (0,0), (-1,0), colors.white),
            ('ALIGN', (0,0), (-1,-1), 'CENTER'),
            ('FONTNAME', (0,0), (-1,0), 'Helvetica-Bold'),
            ('BOTTOMPADDING', (0,0), (-1,0), 8),
            ('BACKGROUND', (0,1), (-1,1), colors.HexColor('#f1f5f9')),
            ('GRID', (0,0), (-1,-1), 1, colors.HexColor('#cbd5e1')),
            ('FONTSIZE', (0,1), (-1,1), 16),
            ('TEXTCOLOR', (0,1), (0,1), colors.HexColor('#f43f5e')), # Critical = red
            ('TEXTCOLOR', (1,1), (1,1), colors.HexColor('#f97316')), # High = orange
        ]))
        elements.append(t_summary)
        elements.append(Spacer(1, 20))

        # Table of Findings
        elements.append(Paragraph("Detailed Findings", heading_style))
        
        findings_table_data = [
            ["ID", "Secret Type", "Severity", "Risk Score", "File / Asset URL"]
        ]
        
        for f in findings:
            findings_table_data.append([
                f"#{f.get('id', 'N/A')}",
                f.get('secret_type', 'N/A'),
                f.get('severity', 'N/A'),
                str(f.get('risk_score', 0)),
                Paragraph(f.get('file_path_or_url', 'N/A'), body_style)
            ])
            
        t_findings = Table(findings_table_data, colWidths=[40, 110, 70, 60, 260])
        t_findings.setStyle(TableStyle([
            ('BACKGROUND', (0,0), (-1,0), colors.HexColor('#0f172a')),
            ('TEXTCOLOR', (0,0), (-1,0), colors.white),
            ('ALIGN', (0,0), (-1,-1), 'LEFT'),
            ('VALIGN', (0,0), (-1,-1), 'TOP'),
            ('GRID', (0,0), (-1,-1), 0.5, colors.HexColor('#cbd5e1')),
            ('TOPPADDING', (0,0), (-1,-1), 6),
            ('BOTTOMPADDING', (0,0), (-1,-1), 6),
        ]))
        
        elements.append(t_findings)

        doc.build(elements)

    @classmethod
    def build_and_store_report(cls, project_id: int, format_type: str, db: Session, user_id: int = None) -> Report:
        """
        Gathers database findings for a project, renders to chosen format, stores in selected backend,
        and logs the record in the Report table.
        """
        project = db.query(Project).filter(Project.id == project_id).first()
        if not project:
            raise Exception("Project not found")

        # Fetch findings for assets in this project
        # Joint query
        raw_findings = db.query(Finding).join(Finding.scan_id).filter(
            Finding.scan_id.has(asset_id=project.id)
        ).all()
        # Wait, scan table has asset_id, asset table has project_id
        # Let's write the correct join query:
        from app.models.scan import Scan
        from app.models.asset import Asset
        from app.models.secret_type import SecretType
        
        findings_query = db.query(Finding, SecretType.name).join(Scan).join(Asset).join(SecretType).filter(
            Asset.project_id == project_id
        ).all()

        findings_list = []
        stats = {"critical": 0, "high": 0, "medium": 0, "low": 0}
        
        for finding, type_name in findings_query:
            findings_list.append({
                "id": finding.id,
                "secret_type": type_name,
                "severity": finding.severity,
                "risk_score": finding.risk_score,
                "exposure_risk": finding.exposure_risk,
                "compliance_risk": finding.compliance_risk,
                "operational_risk": finding.operational_risk,
                "file_path_or_url": finding.file_path_or_url,
                "status": finding.status,
                "remediation_notes": finding.remediation_notes
            })
            sev_lower = finding.severity.lower()
            if sev_lower in stats:
                stats[sev_lower] += 1

        timestamp = datetime.utcnow().strftime("%Y%m%d_%H%M%S")
        filename = f"report_project_{project_id}_{timestamp}.{format_type.lower()}"
        
        if format_type.upper() == "HTML":
            content_str = cls.generate_html_report(project.name, findings_list, stats)
            content_bytes = content_str.encode('utf-8')
            mime = "text/html"
        elif format_type.upper() == "MD":
            content_str = cls.generate_markdown_report(project.name, findings_list, stats)
            content_bytes = content_str.encode('utf-8')
            mime = "text/markdown"
        else: # PDF
            # Write to a temporary file, then read
            temp_path = os.path.join(tempfile.gettempdir(), filename)
            try:
                cls.generate_pdf_report(project.name, findings_list, stats, temp_path)
                with open(temp_path, "rb") as f:
                    content_bytes = f.read()
            finally:
                if os.path.exists(temp_path):
                    os.remove(temp_path)
            mime = "application/pdf"

        # Upload using Storage Manager
        storage_url = storage_manager.upload_file(filename, content_bytes, mime)

        # Save to DB
        import json
        db_report = Report(
            project_id=project_id,
            type=format_type.upper(),
            file_path=storage_url,
            generated_by_user_id=user_id,
            summary_stats=json.dumps(stats)
        )
        db.add(db_report)
        db.commit()
        db.refresh(db_report)
        return db_report
