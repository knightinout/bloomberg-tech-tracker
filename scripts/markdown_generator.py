"""
Markdown Report Generator Module
Generates daily reports from Bloomberg Technology video analysis.
"""

import os
import logging
from datetime import datetime
from typing import Dict

logger = logging.getLogger(__name__)


class MarkdownGenerator:
    """Handles generation of markdown reports."""

    def __init__(self, config: Dict):
        """
        Initialize the markdown generator.

        Args:
            config: Configuration dictionary
        """
        self.config = config
        self.daily_reports_dir = config['output']['daily_reports_dir']
        self.date_format = config['output']['date_format']
        self.filename_format = config['output']['report_filename_format']

        # Ensure directory exists
        os.makedirs(self.daily_reports_dir, exist_ok=True)

    def generate_daily_report(self, analysis_results: Dict, date: datetime = None) -> str:
        """
        Generate a daily markdown report.

        Args:
            analysis_results: Dictionary containing analysis data
            date: Date for the report (defaults to today)

        Returns:
            Path to the generated report file
        """
        try:
            if date is None:
                date = datetime.now()

            date_str = date.strftime(self.date_format)
            filename = self.filename_format.format(date=date_str)
            filepath = os.path.join(self.daily_reports_dir, filename)

            logger.info(f"Generating daily report: {filepath}")

            # Extract metadata
            metadata = analysis_results.get('video_metadata', {})

            # Build markdown content
            content = self._build_daily_report_content(
                date_str,
                metadata,
                analysis_results
            )

            # Write to file
            with open(filepath, 'w', encoding='utf-8') as f:
                f.write(content)

            logger.info(f"Daily report saved: {filepath}")
            return filepath

        except Exception as e:
            logger.error(f"Error generating daily report: {str(e)}")
            raise

    def _build_daily_report_content(
        self,
        date_str: str,
        metadata: Dict,
        analysis_results: Dict
    ) -> str:
        """Build the markdown content for daily report - CONCISE VERSION."""

        content = f"""# Bloomberg Technology - Daily Report
## {date_str}

**Video:** [{metadata.get('title', 'N/A')}]({metadata.get('url', 'N/A')})
**Duration:** {metadata.get('duration_string', 'N/A')} | **Upload:** {metadata.get('upload_date', 'N/A')}

---

## Key Moments (with Timestamps)

{analysis_results.get('daily_summary', 'No summary available.')}

---

## Trading Insights (10 Lines)

{analysis_results.get('trading_insights', 'No trading insights available.')}

---

*Report Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}*
"""

        return content



def test_generator():
    """Test function to verify the generator works."""
    import json

    # Load config
    with open('../config/config.json', 'r') as f:
        config = json.load(f)

    # Initialize generator
    generator = MarkdownGenerator(config)

    # Create sample analysis results
    sample_results = {
        'video_metadata': {
            'title': 'Bloomberg Technology - January 29, 2026',
            'url': 'https://www.youtube.com/watch?v=sample',
            'upload_date': '20260129',
            'duration_string': '44:30',
            'channel': 'Bloomberg Technology',
        },
        'daily_summary': 'Sample daily summary content...',
        'trading_insights': 'Sample trading insights content...',
        'key_takeaways': '- Takeaway 1\n- Takeaway 2\n- Takeaway 3',
        'weekly_highlights': 'Sample weekly highlights content...',
    }

    # Generate daily report
    report_path = generator.generate_daily_report(sample_results)
    print(f"Generated daily report: {report_path}")


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    test_generator()
