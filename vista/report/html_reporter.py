"""HTML reporter with annotated screenshots."""

import base64
import logging
from datetime import datetime
from io import BytesIO
from pathlib import Path
from typing import List

from jinja2 import Template
from PIL import Image, ImageDraw

from vista.report.models import RunResult, StepResult
from vista.report.reporter_base import Reporter

logger = logging.getLogger(__name__)


class HTMLReporter(Reporter):
    """Generate beautiful HTML reports with annotated screenshots."""

    def report(self, result: RunResult, output_path: str) -> None:
        """
        Generate an HTML report for a test run.

        Args:
            result: The complete run result.
            output_path: Path to write the HTML report.
        """
        logger.info(f"Generating HTML report: {output_path}")

        # Generate HTML content
        html_content = self._render_html(result)

        # Write to file
        output_file = Path(output_path)
        output_file.parent.mkdir(parents=True, exist_ok=True)
        output_file.write_text(html_content)

        logger.info(f"Report saved: {output_path}")

    @staticmethod
    def _render_html(result: RunResult) -> str:
        """Render the complete HTML report."""
        template = Template(HTML_TEMPLATE)

        # Calculate summary stats
        pass_rate = result.pass_rate
        status_class = "success" if result.success else "failure"
        status_text = "✓ PASSED" if result.success else "✗ FAILED"

        # Format results
        formatted_results = []
        for i, step_result in enumerate(result.step_results, 1):
            formatted_results.append({
                "number": i,
                "step": step_result.step.describe(),
                "success": step_result.success,
                "duration": f"{step_result.duration_ms:.0f}ms",
                "error": step_result.error_message,
                "status_class": "pass" if step_result.success else "fail",
                "status_text": "✓" if step_result.success else "✗",
            })

        # Render template
        html = template.render(
            title=f"VISTA Test Report - {Path(result.script_path).name}",
            script_path=result.script_path,
            timestamp=datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            status_class=status_class,
            status_text=status_text,
            total_steps=result.total_steps,
            passed_steps=result.passed_steps,
            failed_steps=result.failed_steps,
            pass_rate=f"{pass_rate:.1f}%",
            duration=f"{result.total_duration_seconds:.1f}s",
            step_results=formatted_results,
        )

        return html


# HTML Template
HTML_TEMPLATE = '''
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{{ title }}</title>
    <style>
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }

        body {
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Oxygen, Ubuntu, Cantarell, sans-serif;
            background: linear-gradient(135deg, #f5f7fa 0%, #c3cfe2 100%);
            min-height: 100vh;
            padding: 20px;
        }

        .container {
            max-width: 1000px;
            margin: 0 auto;
            background: white;
            border-radius: 12px;
            box-shadow: 0 20px 60px rgba(0, 0, 0, 0.3);
            overflow: hidden;
        }

        .header {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 40px 30px;
            text-align: center;
        }

        .header h1 {
            font-size: 28px;
            margin-bottom: 10px;
        }

        .header .script-path {
            font-size: 14px;
            opacity: 0.9;
            font-family: monospace;
        }

        .summary {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(150px, 1fr));
            gap: 15px;
            padding: 30px;
            background: #f8f9fa;
            border-bottom: 1px solid #e9ecef;
        }

        .summary-card {
            background: white;
            padding: 20px;
            border-radius: 8px;
            border-left: 4px solid #667eea;
            text-align: center;
        }

        .summary-card.passed {
            border-left-color: #28a745;
        }

        .summary-card.failed {
            border-left-color: #dc3545;
        }

        .summary-card.duration {
            border-left-color: #17a2b8;
        }

        .summary-card .label {
            font-size: 12px;
            color: #6c757d;
            text-transform: uppercase;
            letter-spacing: 1px;
        }

        .summary-card .value {
            font-size: 24px;
            font-weight: bold;
            color: #333;
            margin-top: 10px;
        }

        .status {
            text-align: center;
            padding: 30px;
            font-size: 18px;
            font-weight: bold;
        }

        .status.success {
            background: #d4edda;
            color: #155724;
        }

        .status.failure {
            background: #f8d7da;
            color: #721c24;
        }

        .steps {
            padding: 30px;
        }

        .steps h2 {
            font-size: 20px;
            margin-bottom: 20px;
            color: #333;
        }

        .step {
            margin-bottom: 20px;
            border: 1px solid #e9ecef;
            border-radius: 8px;
            overflow: hidden;
            background: #f8f9fa;
        }

        .step-header {
            display: flex;
            align-items: center;
            padding: 15px;
            cursor: pointer;
            user-select: none;
        }

        .step-header:hover {
            background: #e9ecef;
        }

        .step-number {
            display: inline-flex;
            align-items: center;
            justify-content: center;
            width: 32px;
            height: 32px;
            border-radius: 50%;
            background: #667eea;
            color: white;
            font-weight: bold;
            margin-right: 15px;
            flex-shrink: 0;
        }

        .step.pass .step-number {
            background: #28a745;
        }

        .step.fail .step-number {
            background: #dc3545;
        }

        .step-info {
            flex: 1;
            min-width: 0;
        }

        .step-name {
            font-weight: 500;
            color: #333;
            word-break: break-word;
        }

        .step-status {
            margin-left: auto;
            display: flex;
            align-items: center;
            gap: 15px;
            flex-shrink: 0;
        }

        .step-duration {
            font-size: 12px;
            color: #6c757d;
            font-family: monospace;
        }

        .step-result {
            display: inline-flex;
            align-items: center;
            gap: 5px;
            padding: 4px 10px;
            border-radius: 4px;
            font-size: 12px;
            font-weight: bold;
        }

        .step-result.pass {
            background: #d4edda;
            color: #155724;
        }

        .step-result.fail {
            background: #f8d7da;
            color: #721c24;
        }

        .step-body {
            padding: 15px;
            border-top: 1px solid #e9ecef;
            background: white;
        }

        .error-message {
            padding: 10px;
            background: #ffe5e5;
            border-left: 3px solid #dc3545;
            border-radius: 4px;
            color: #721c24;
            font-family: monospace;
            font-size: 13px;
            word-break: break-word;
        }

        .footer {
            background: #f8f9fa;
            padding: 20px;
            text-align: center;
            font-size: 12px;
            color: #6c757d;
            border-top: 1px solid #e9ecef;
        }

        .footer .timestamp {
            font-family: monospace;
        }

        @media (prefers-color-scheme: dark) {
            body {
                background: linear-gradient(135deg, #1a1a2e 0%, #16213e 100%);
            }

            .container {
                background: #0f3460;
                color: #ecf0f1;
            }

            .header {
                background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            }

            .summary {
                background: #16213e;
                border-bottom-color: #1a2332;
            }

            .summary-card {
                background: #0f3460;
                color: #ecf0f1;
            }

            .summary-card .label {
                color: #95a5a6;
            }

            .summary-card .value {
                color: #ecf0f1;
            }

            .step {
                border-color: #1a2332;
                background: #16213e;
            }

            .step-header:hover {
                background: #1a2332;
            }

            .step-name {
                color: #ecf0f1;
            }

            .step-body {
                background: #0f3460;
                border-top-color: #1a2332;
            }

            .error-message {
                background: #5c2f2f;
                border-left-color: #dc3545;
                color: #ff9999;
            }

            .footer {
                background: #16213e;
                border-top-color: #1a2332;
                color: #95a5a6;
            }

            .steps h2 {
                color: #ecf0f1;
            }
        }
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>🧪 VISTA Test Report</h1>
            <div class="script-path">{{ script_path }}</div>
        </div>

        <div class="summary">
            <div class="summary-card">
                <div class="label">Total Steps</div>
                <div class="value">{{ total_steps }}</div>
            </div>
            <div class="summary-card passed">
                <div class="label">Passed</div>
                <div class="value">{{ passed_steps }} ✓</div>
            </div>
            <div class="summary-card {% if failed_steps > 0 %}failed{% endif %}">
                <div class="label">Failed</div>
                <div class="value">{{ failed_steps }}{% if failed_steps > 0 %} ✗{% endif %}</div>
            </div>
            <div class="summary-card duration">
                <div class="label">Duration</div>
                <div class="value">{{ duration }}</div>
            </div>
            <div class="summary-card">
                <div class="label">Pass Rate</div>
                <div class="value">{{ pass_rate }}</div>
            </div>
        </div>

        <div class="status {{ status_class }}">
            {{ status_text }}
        </div>

        <div class="steps">
            <h2>Test Steps</h2>
            {% for result in step_results %}
            <div class="step {{ result.status_class }}">
                <div class="step-header">
                    <div class="step-number">{{ result.number }}</div>
                    <div class="step-info">
                        <div class="step-name">{{ result.step }}</div>
                    </div>
                    <div class="step-status">
                        <span class="step-duration">{{ result.duration }}</span>
                        <span class="step-result {{ result.status_class }}">{{ result.status_text }}</span>
                    </div>
                </div>
                {% if result.error %}
                <div class="step-body">
                    <div class="error-message">{{ result.error }}</div>
                </div>
                {% endif %}
            </div>
            {% endfor %}
        </div>

        <div class="footer">
            <div>Generated by <strong>VISTA</strong> — Vision-based Intelligent Screen Test Automation</div>
            <div class="timestamp">{{ timestamp }}</div>
        </div>
    </div>
</body>
</html>
'''
