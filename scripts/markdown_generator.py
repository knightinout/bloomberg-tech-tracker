"""
Markdown Report Generator Module
Generates daily reports and updates the master weekly review document.
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
        self.master_doc_path = config['output']['master_doc_path']
        self.date_format = config['output']['date_format']
        self.filename_format = config['output']['report_filename_format']

        # Ensure directories exist
        os.makedirs(self.daily_reports_dir, exist_ok=True)
        os.makedirs(os.path.dirname(self.master_doc_path), exist_ok=True)

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

    def update_master_doc(self, analysis_results: Dict, date: datetime = None):
        """
        Update the master weekly review document with mini-summary.

        Args:
            analysis_results: Dictionary containing analysis data
            date: Date for the entry (defaults to today)
        """
        try:
            if date is None:
                date = datetime.now()

            date_str = date.strftime(self.date_format)
            logger.info(f"Updating master doc for {date_str}")

            # Extract mini-summary (5 lines)
            metadata = analysis_results.get('video_metadata', {})
            mini_summary = analysis_results.get('mini_summary', '')

            # Create entry content
            entry = self._build_master_doc_entry(
                date_str,
                metadata,
                mini_summary
            )

            # Check if master doc exists
            if not os.path.exists(self.master_doc_path):
                # Create new master doc with header
                self._create_new_master_doc()

            # Append entry to master doc
            with open(self.master_doc_path, 'a', encoding='utf-8') as f:
                f.write('\n' + entry + '\n')

            logger.info("Master doc updated successfully")

        except Exception as e:
            logger.error(f"Error updating master doc: {str(e)}")
            raise

    def _build_master_doc_entry(
        self,
        date_str: str,
        metadata: Dict,
        mini_summary: str
    ) -> str:
        """Build a concise entry for the master document - 5 lines only."""

        entry = f"""## {date_str} - [{metadata.get('title', 'N/A')}]({metadata.get('url', '#')})

{mini_summary}

---
"""
        return entry

    def _create_new_master_doc(self):
        """Create a new master document with header."""

        header = f"""# Bloomberg Technology - Weekly Review Master Document

This document contains important points and highlights from Bloomberg Technology episodes for weekly review.

**Last Updated:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

---

"""
        with open(self.master_doc_path, 'w', encoding='utf-8') as f:
            f.write(header)

        logger.info("Created new master document")

    def get_weekly_summary(self, start_date: datetime = None) -> str:
        """
        Extract entries from the last week for review.

        Args:
            start_date: Start date for weekly summary (defaults to 7 days ago)

        Returns:
            Formatted weekly summary
        """
        try:
            if not os.path.exists(self.master_doc_path):
                return "No master document found."

            with open(self.master_doc_path, 'r', encoding='utf-8') as f:
                content = f.read()

            # For simplicity, return the entire document
            # In a more sophisticated version, we could parse dates and filter
            return content

        except Exception as e:
            logger.error(f"Error generating weekly summary: {str(e)}")
            return f"Error: {str(e)}"


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

    # Update master doc
    generator.update_master_doc(sample_results)
    print(f"Updated master doc: {generator.master_doc_path}")


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    test_generator()
