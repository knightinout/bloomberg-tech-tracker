"""
Gemini AI Analyzer Module
Analyzes Bloomberg Technology transcripts using Google's Gemini API.
"""

import logging
import time
from typing import Dict, Optional
from google import genai

logger = logging.getLogger(__name__)


class GeminiAnalyzer:
    """Handles AI analysis of video transcripts using Gemini."""

    def __init__(self, config: Dict):
        """
        Initialize the Gemini analyzer.

        Args:
            config: Configuration dictionary containing Gemini settings
        """
        self.config = config
        self.api_key = config['api_keys']['gemini_api_key']
        self.model_name = config['gemini']['model']
        self.temperature = config['gemini']['temperature']
        self.max_tokens = config['gemini']['max_tokens']
        self.system_prompt = config['gemini']['system_prompt']
        self.analysis_prompts = config['gemini']['analysis_prompts']
        self.retry_attempts = config['automation'].get('retry_attempts', 3)
        self.retry_delay = config['automation'].get('retry_delay_seconds', 60)

        # Configure Gemini with new API
        self.client = genai.Client(api_key=self.api_key)

        logger.info(f"Initialized Gemini analyzer with model: {self.model_name}")

    def analyze_video(self, video_url: str, video_metadata: Dict) -> Optional[Dict]:
        """
        Perform concise analysis of a YouTube video using native video understanding.

        Args:
            video_url: YouTube video URL
            video_metadata: Dictionary with video information

        Returns:
            Dictionary containing all analysis results or None on failure
        """
        try:
            logger.info("Starting concise video analysis using native video understanding...")

            analysis_results = {
                'video_metadata': video_metadata,
                'daily_summary': self._generate_video_analysis(
                    video_url,
                    self.analysis_prompts['daily_summary'],
                    "Daily Summary"
                ),
                'trading_insights': self._generate_video_analysis(
                    video_url,
                    self.analysis_prompts['trading_insights'],
                    "Trading Insights"
                ),
                'mini_summary': self._generate_video_analysis(
                    video_url,
                    self.analysis_prompts['mini_summary'],
                    "Mini Summary"
                ),
            }

            logger.info("Completed concise video analysis")
            return analysis_results

        except Exception as e:
            logger.error(f"Error during video analysis: {str(e)}")
            return None

    def analyze_transcript(self, transcript: str, video_metadata: Dict) -> Optional[Dict]:
        """
        Analyze a video using its text transcript.

        Args:
            transcript: Full video transcript text
            video_metadata: Dictionary with video information

        Returns:
            Dictionary containing all analysis results or None on failure
        """
        try:
            logger.info("Starting transcript-based video analysis...")

            analysis_results = {
                'video_metadata': video_metadata,
                'daily_summary': self._generate_analysis(
                    transcript,
                    self.analysis_prompts['daily_summary'],
                    "Daily Summary"
                ),
                'trading_insights': self._generate_analysis(
                    transcript,
                    self.analysis_prompts['trading_insights'],
                    "Trading Insights"
                ),
            }

            logger.info("Completed transcript-based video analysis")
            return analysis_results

        except Exception as e:
            logger.error(f"Error during transcript analysis: {str(e)}")
            return None

    def _generate_video_analysis(
        self,
        video_url: str,
        prompt: str,
        analysis_type: str
    ) -> Optional[str]:
        """
        Generate analysis using native video understanding from YouTube URL.

        Args:
            video_url: YouTube video URL
            prompt: Specific analysis prompt
            analysis_type: Name of analysis for logging

        Returns:
            Analysis text or None on failure
        """
        for attempt in range(self.retry_attempts):
            try:
                logger.info(f"Generating {analysis_type} from video URL (attempt {attempt + 1}/{self.retry_attempts})...")

                # Construct full prompt with context
                full_prompt = f"""{self.system_prompt}

{prompt}

Please analyze the YouTube video and provide your analysis:"""

                # Generate content using YouTube URL with correct format
                response = self.client.models.generate_content(
                    model=self.model_name,
                    contents=[
                        {
                            "parts": [
                                {"text": full_prompt},
                                {"file_data": {"file_uri": video_url}}
                            ]
                        }
                    ],
                    config={
                        'temperature': self.temperature,
                        'max_output_tokens': self.max_tokens,
                    }
                )

                if response and response.text:
                    logger.info(f"Successfully generated {analysis_type}")
                    return response.text.strip()
                else:
                    logger.warning(f"Empty response for {analysis_type}")
                    return None

            except Exception as e:
                logger.error(f"Error generating {analysis_type} (attempt {attempt + 1}): {str(e)}")

                if attempt < self.retry_attempts - 1:
                    logger.info(f"Retrying in {self.retry_delay} seconds...")
                    time.sleep(self.retry_delay)
                else:
                    logger.error(f"Failed to generate {analysis_type} after {self.retry_attempts} attempts")
                    return None

        return None

    def _generate_analysis(
        self,
        transcript: str,
        prompt: str,
        analysis_type: str
    ) -> Optional[str]:
        """
        Generate a specific type of analysis using Gemini.

        Args:
            transcript: Full video transcript
            prompt: Specific analysis prompt
            analysis_type: Name of analysis for logging

        Returns:
            Analysis text or None on failure
        """
        for attempt in range(self.retry_attempts):
            try:
                logger.info(f"Generating {analysis_type} (attempt {attempt + 1}/{self.retry_attempts})...")

                # Construct full prompt with context
                full_prompt = f"""{self.system_prompt}

{prompt}

Video Transcript:
{transcript}

Please provide your analysis:"""

                # Generate content using new API
                response = self.client.models.generate_content(
                    model=self.model_name,
                    contents=full_prompt,
                    config={
                        'temperature': self.temperature,
                        'max_output_tokens': self.max_tokens,
                    }
                )

                if response and response.text:
                    logger.info(f"Successfully generated {analysis_type}")
                    return response.text.strip()
                else:
                    logger.warning(f"Empty response for {analysis_type}")
                    return None

            except Exception as e:
                logger.error(f"Error generating {analysis_type} (attempt {attempt + 1}): {str(e)}")

                if attempt < self.retry_attempts - 1:
                    logger.info(f"Retrying in {self.retry_delay} seconds...")
                    time.sleep(self.retry_delay)
                else:
                    logger.error(f"Failed to generate {analysis_type} after {self.retry_attempts} attempts")
                    return None

        return None

    def generate_quick_summary(self, transcript: str) -> Optional[str]:
        """
        Generate a quick summary without full analysis.

        Args:
            transcript: Video transcript

        Returns:
            Quick summary text or None
        """
        try:
            prompt = """Provide a brief 3-5 sentence summary of the key points discussed in this Bloomberg Technology episode."""

            full_prompt = f"""{self.system_prompt}

{prompt}

Transcript:
{transcript}"""

            response = self.client.models.generate_content(
                model=self.model_name,
                contents=full_prompt
            )

            if response and response.text:
                return response.text.strip()
            return None

        except Exception as e:
            logger.error(f"Error generating quick summary: {str(e)}")
            return None

    def extract_stock_mentions(self, transcript: str) -> Optional[str]:
        """
        Extract specific stock/company mentions from transcript.

        Args:
            transcript: Video transcript

        Returns:
            List of stock mentions with context
        """
        try:
            prompt = """Extract all company and stock ticker mentions from this transcript.
For each mention, provide:
- Company/Stock name
- Ticker symbol (if mentioned)
- Brief context of why it was discussed
- Sentiment (positive/negative/neutral)

Format as a bullet list."""

            full_prompt = f"""{self.system_prompt}

{prompt}

Transcript:
{transcript}"""

            response = self.client.models.generate_content(
                model=self.model_name,
                contents=full_prompt
            )

            if response and response.text:
                return response.text.strip()
            return None

        except Exception as e:
            logger.error(f"Error extracting stock mentions: {str(e)}")
            return None


def test_analyzer():
    """Test function to verify the analyzer works."""
    import json

    # Load config
    with open('../config/config.json', 'r') as f:
        config = json.load(f)

    # Check if API key is set
    if config['api_keys']['gemini_api_key'] == 'YOUR_GEMINI_API_KEY_HERE':
        print("Error: Please set your Gemini API key in config.json")
        return

    # Initialize analyzer
    analyzer = GeminiAnalyzer(config)

    # Test with sample text
    sample_transcript = """
    Today on Bloomberg Technology, we're discussing the latest developments in artificial intelligence.
    OpenAI announced a new partnership with Microsoft, investing heavily in AI infrastructure.
    Tech stocks saw mixed results today with NVIDIA up 3% while Tesla dropped 2%.
    Analysts are predicting strong growth in the semiconductor sector.
    """

    # Generate analysis
    quick_summary = analyzer.generate_quick_summary(sample_transcript)
    if quick_summary:
        print("Quick Summary:")
        print(quick_summary)
        print("\n" + "="*50 + "\n")

    stock_mentions = analyzer.extract_stock_mentions(sample_transcript)
    if stock_mentions:
        print("Stock Mentions:")
        print(stock_mentions)


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    test_analyzer()
