"""
YouTube Video Fetcher Module
Fetches Bloomberg Technology videos and their transcripts from YouTube.
"""

import json
import logging
from datetime import datetime, timedelta
from typing import Dict, Optional, List
import yt_dlp
from youtube_transcript_api import YouTubeTranscriptApi, TranscriptsDisabled, NoTranscriptFound

logger = logging.getLogger(__name__)


class YouTubeFetcher:
    """Handles fetching Bloomberg Technology videos and transcripts."""

    def __init__(self, config: Dict):
        """
        Initialize the YouTube fetcher.

        Args:
            config: Configuration dictionary containing YouTube settings
        """
        self.config = config
        self.channel_id = config['youtube']['channel_id']
        self.channel_name = config['youtube']['channel_name']
        self.search_term = config['youtube']['search_term']
        self.min_duration = config['youtube'].get('video_duration_min', 30)
        self.processed_videos_file = config['output']['video_tracking_file']

    def get_latest_video(self) -> Optional[Dict]:
        """
        Fetch the latest Bloomberg Technology video.

        Returns:
            Dictionary containing video metadata or None if not found
        """
        try:
            logger.info(f"Searching for latest {self.channel_name} video...")

            # yt-dlp options to fetch channel videos
            ydl_opts = {
                'quiet': True,
                'no_warnings': True,
                'extract_flat': True,
                'playlistend': 5,  # Get latest 5 videos
            }

            channel_url = f"https://www.youtube.com/channel/{self.channel_id}/videos"

            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                result = ydl.extract_info(channel_url, download=False)

                if not result or 'entries' not in result:
                    logger.error("No videos found in channel")
                    return None

                # Get the most recent video
                for entry in result['entries']:
                    if entry is None:
                        continue

                    video_id = entry.get('id')
                    if not video_id:
                        continue

                    # Check if already processed
                    if self._is_video_processed(video_id):
                        logger.info(f"Video {video_id} already processed, skipping...")
                        continue

                    # Get full video details
                    video_details = self._get_video_details(video_id)
                    if video_details:
                        logger.info(f"Found new video: {video_details['title']}")
                        return video_details

                logger.info("No new videos found that haven't been processed")
                return None

        except Exception as e:
            logger.error(f"Error fetching latest video: {str(e)}")
            return None

    def _get_video_details(self, video_id: str) -> Optional[Dict]:
        """
        Get detailed information about a specific video.

        Args:
            video_id: YouTube video ID

        Returns:
            Dictionary with video details or None
        """
        try:
            ydl_opts = {
                'quiet': True,
                'no_warnings': True,
            }

            video_url = f"https://www.youtube.com/watch?v={video_id}"

            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                info = ydl.extract_info(video_url, download=False)

                # Check duration (in seconds)
                duration_minutes = info.get('duration', 0) / 60
                if duration_minutes < self.min_duration:
                    logger.info(f"Video {video_id} is too short ({duration_minutes:.1f} min), skipping...")
                    return None

                return {
                    'video_id': video_id,
                    'url': video_url,
                    'title': info.get('title', 'Unknown'),
                    'description': info.get('description', ''),
                    'upload_date': info.get('upload_date', ''),
                    'duration': info.get('duration', 0),
                    'duration_string': info.get('duration_string', ''),
                    'thumbnail': info.get('thumbnail', ''),
                    'channel': info.get('channel', self.channel_name),
                }
        except Exception as e:
            logger.error(f"Error getting video details for {video_id}: {str(e)}")
            return None

    def get_transcript(self, video_id: str) -> Optional[str]:
        """
        Fetch the transcript/captions for a video.

        Args:
            video_id: YouTube video ID

        Returns:
            Full transcript text or None if unavailable
        """
        try:
            logger.info(f"Fetching transcript for video {video_id}...")

            # Create API instance and fetch transcript
            api = YouTubeTranscriptApi()
            transcript_list = api.list(video_id)

            # Try to get manually created English transcript first, then auto-generated
            try:
                transcript = transcript_list.find_manually_created_transcript(['en'])
            except:
                transcript = transcript_list.find_generated_transcript(['en'])

            # Fetch the transcript data
            transcript_data = transcript.fetch()

            # Combine all text segments - using .text attribute instead of dict access
            full_transcript = ' '.join([entry.text for entry in transcript_data])

            logger.info(f"Successfully fetched transcript ({len(full_transcript)} characters)")
            return full_transcript

        except TranscriptsDisabled:
            logger.error(f"Transcripts are disabled for video {video_id}")
            return None
        except NoTranscriptFound:
            logger.error(f"No English transcript found for video {video_id}")
            return None
        except Exception as e:
            logger.error(f"Error fetching transcript: {str(e)}")
            return None

    def _is_video_processed(self, video_id: str) -> bool:
        """
        Check if a video has already been processed.

        Args:
            video_id: YouTube video ID

        Returns:
            True if video was already processed
        """
        try:
            with open(self.processed_videos_file, 'r') as f:
                data = json.load(f)
                return video_id in data.get('processed_videos', [])
        except FileNotFoundError:
            return False
        except Exception as e:
            logger.error(f"Error checking processed videos: {str(e)}")
            return False

    def mark_video_processed(self, video_id: str, video_title: str):
        """
        Mark a video as processed.

        Args:
            video_id: YouTube video ID
            video_title: Video title for reference
        """
        try:
            # Read existing data
            try:
                with open(self.processed_videos_file, 'r') as f:
                    data = json.load(f)
            except FileNotFoundError:
                data = {'processed_videos': [], 'last_updated': None}

            # Add new video
            if video_id not in data['processed_videos']:
                data['processed_videos'].append({
                    'video_id': video_id,
                    'title': video_title,
                    'processed_date': datetime.now().isoformat()
                })

            data['last_updated'] = datetime.now().isoformat()

            # Write back
            with open(self.processed_videos_file, 'w') as f:
                json.dump(data, f, indent=2)

            logger.info(f"Marked video {video_id} as processed")

        except Exception as e:
            logger.error(f"Error marking video as processed: {str(e)}")


def test_fetcher():
    """Test function to verify the fetcher works."""

    # Load config
    with open('../config/config.json', 'r') as f:
        config = json.load(f)

    # Initialize fetcher
    fetcher = YouTubeFetcher(config)

    # Get latest video
    video = fetcher.get_latest_video()
    if video:
        print(f"Found video: {video['title']}")
        print(f"URL: {video['url']}")
        print(f"Upload date: {video['upload_date']}")

        # Get transcript
        transcript = fetcher.get_transcript(video['video_id'])
        if transcript:
            print(f"\nTranscript preview (first 500 chars):")
            print(transcript[:500])
    else:
        print("No new videos found")


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    test_fetcher()
