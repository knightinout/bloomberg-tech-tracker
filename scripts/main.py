#!/usr/bin/env python3
"""
Bloomberg Technology Automation - Main Script
Orchestrates the daily workflow of fetching, analyzing, and reporting.
"""

import os
import sys
import json
import logging
from datetime import datetime
from pathlib import Path
from dotenv import load_dotenv

# Add parent directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from youtube_fetcher import YouTubeFetcher
from gemini_analyzer import GeminiAnalyzer
from markdown_generator import MarkdownGenerator


class BloombergTechAutomation:
    """Main automation class that orchestrates the entire workflow."""

    def __init__(self, config_path: str):
        """
        Initialize the automation system.

        Args:
            config_path: Path to configuration JSON file
        """
        self.config_path = config_path
        self.config = self._load_config()
        self._setup_logging()

        # Initialize modules
        logger.info("Initializing Bloomberg Tech Automation...")
        self.youtube_fetcher = YouTubeFetcher(self.config)
        self.gemini_analyzer = GeminiAnalyzer(self.config)
        self.markdown_generator = MarkdownGenerator(self.config)

        logger.info("Automation system initialized successfully")

    def _load_config(self) -> dict:
        """Load configuration from JSON file."""
        try:
            with open(self.config_path, 'r') as f:
                config = json.load(f)

            # Inject API key from environment (overrides config.json)
            env_api_key = os.environ.get('GEMINI_API_KEY', '').strip()
            if env_api_key:
                config['api_keys']['gemini_api_key'] = env_api_key

            # Validate we have a real key from either source
            if config['api_keys']['gemini_api_key'] == 'YOUR_GEMINI_API_KEY_HERE':
                raise ValueError(
                    "Gemini API key not configured. Set GEMINI_API_KEY in .env "
                    "or add the key to config/config.json"
                )

            return config

        except FileNotFoundError:
            print(f"Error: Config file not found at {self.config_path}")
            sys.exit(1)
        except json.JSONDecodeError as e:
            print(f"Error: Invalid JSON in config file: {e}")
            sys.exit(1)
        except Exception as e:
            print(f"Error loading config: {e}")
            sys.exit(1)

    def _setup_logging(self):
        """Configure logging system."""
        log_config = self.config.get('logging', {})
        log_file = log_config.get('log_file', 'logs/automation.log')
        log_level = getattr(logging, log_config.get('log_level', 'INFO'))

        # Create logs directory if needed
        log_dir = os.path.dirname(log_file)
        if log_dir:
            os.makedirs(log_dir, exist_ok=True)

        # Configure logging
        logging.basicConfig(
            level=log_level,
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler(log_file),
                logging.StreamHandler(sys.stdout)
            ]
        )

        global logger
        logger = logging.getLogger(__name__)

    def run(self) -> bool:
        """
        Execute the main automation workflow.

        Returns:
            True if successful, False otherwise
        """
        try:
            logger.info("="*70)
            logger.info("Starting Bloomberg Technology automation workflow")
            logger.info(f"Timestamp: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
            logger.info("="*70)

            # Step 1: Fetch latest video
            logger.info("Step 1: Fetching latest Bloomberg Technology video...")
            video = self.youtube_fetcher.get_latest_video()

            if not video:
                logger.info("No new videos to process. Exiting.")
                return True

            logger.info(f"Found video: {video['title']}")
            logger.info(f"Video URL: {video['url']}")

            # Step 2: Analyze video directly with Gemini (no transcript needed!)
            logger.info("Step 2: Analyzing video with Gemini AI (using native video understanding)...")
            analysis_results = self.gemini_analyzer.analyze_video(
                video['url'],
                video
            )

            if not analysis_results:
                logger.error("Failed to analyze video. Aborting.")
                return False

            logger.info("Video analysis completed successfully")

            # Step 3: Generate daily report
            logger.info("Step 3: Generating daily markdown report...")
            report_path = self.markdown_generator.generate_daily_report(
                analysis_results
            )
            logger.info(f"Daily report generated: {report_path}")

            # Step 4: Update master doc
            logger.info("Step 4: Updating master weekly review document...")
            self.markdown_generator.update_master_doc(analysis_results)
            logger.info("Master document updated")

            # Step 5: Mark video as processed
            logger.info("Step 5: Marking video as processed...")
            self.youtube_fetcher.mark_video_processed(
                video['video_id'],
                video['title']
            )

            logger.info("="*70)
            logger.info("Automation workflow completed successfully!")
            logger.info("="*70)

            return True

        except Exception as e:
            logger.error(f"Fatal error in automation workflow: {str(e)}", exc_info=True)
            return False

    def test_components(self):
        """Test individual components without running full workflow."""
        logger.info("Running component tests...")

        # Test YouTube fetcher
        logger.info("\n1. Testing YouTube Fetcher...")
        video = self.youtube_fetcher.get_latest_video()
        if video:
            logger.info(f"   ✓ Found video: {video['title']}")
        else:
            logger.warning("   ✗ No video found or already processed")

        # Test Gemini analyzer
        logger.info("\n2. Testing Gemini Analyzer...")
        test_transcript = "Today we discuss AI developments and tech stocks."
        summary = self.gemini_analyzer.generate_quick_summary(test_transcript)
        if summary:
            logger.info(f"   ✓ Gemini API working: {summary[:100]}...")
        else:
            logger.warning("   ✗ Gemini API test failed")

        # Test markdown generator
        logger.info("\n3. Testing Markdown Generator...")
        test_results = {
            'video_metadata': {'title': 'Test', 'url': 'test', 'upload_date': '20260129'},
            'daily_summary': 'Test summary',
            'trading_insights': 'Test insights',
            'key_takeaways': 'Test takeaways',
            'weekly_highlights': 'Test highlights'
        }
        try:
            self.markdown_generator.generate_daily_report(test_results)
            logger.info("   ✓ Markdown generation working")
        except Exception as e:
            logger.warning(f"   ✗ Markdown generation failed: {e}")

        logger.info("\nComponent tests completed")


def main():
    """Main entry point."""
    import argparse

    parser = argparse.ArgumentParser(
        description='Bloomberg Technology Automation System'
    )
    parser.add_argument(
        '--config',
        default='../config/config.json',
        help='Path to configuration file'
    )
    parser.add_argument(
        '--test',
        action='store_true',
        help='Run component tests only'
    )

    args = parser.parse_args()

    # Load .env from project root (parent of scripts/)
    load_dotenv(Path(__file__).parent.parent / '.env')

    # Resolve config path relative to script location
    script_dir = Path(__file__).parent
    config_path = (script_dir / args.config).resolve()

    try:
        automation = BloombergTechAutomation(str(config_path))

        if args.test:
            automation.test_components()
        else:
            success = automation.run()
            sys.exit(0 if success else 1)

    except KeyboardInterrupt:
        print("\n\nAutomation interrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"\nFatal error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
