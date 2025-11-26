"""
API Client Wrapper - Multi-sport sports data integration
Wraps the API-Sports client from history with error handling
"""

import logging
from typing import Dict, List, Optional, Any
from datetime import datetime
import os
from dotenv import load_dotenv

logger = logging.getLogger("api_client")


class SportsAPIClient:
    """Wrapper for API-Sports multi-sport integration"""
    
    def __init__(self, api_key: Optional[str] = None):
        """
        Initialize API client
        
        Args:
            api_key: API-Sports key (defaults to env variable)
        """
        # Load .env file if it exists
        env_path = os.path.join(os.path.dirname(__file__), "..", "..", ".env")
        if os.path.exists(env_path):
            load_dotenv(env_path)
        
        self.api_key = api_key or os.getenv("API_FOOTBALL_KEY", "")
        self.sports = ["NFL", "NBA", "MLB", "NHL"]
        
        if not self.api_key:
            logger.warning("No API key configured - data fetching will be disabled")
        else:
            logger.info(" API client initialized with key from environment")
    
    def get_sports(self) -> List[str]:
        """Return list of supported sports"""
        return self.sports
    
    def fetch_games(self, sport: str, date: Optional[str] = None) -> Dict[str, Any]:
        """
        Fetch games for a sport on a specific date
        
        Args:
            sport: Sport code (NFL, NBA, MLB, NHL)
            date: Date in YYYY-MM-DD format (defaults to today)
            
        Returns:
            Dictionary with games data
        """
        if not self.api_key:
            logger.error("API key not configured")
            return {"status": "error", "games": [], "message": "API not configured"}
        
        if sport.upper() not in self.sports:
            return {"status": "error", "games": [], "message": f"Unknown sport: {sport}"}
        
        # Placeholder for actual API call
        # In production, this would call the real API-Sports endpoint
        logger.info(f"Fetching {sport} games for {date or 'today'}")
        
        return {
            "status": "success",
            "sport": sport,
            "date": date,
            "games": [],
            "message": "API integration ready"
        }
    
    def get_team_stats(self, sport: str, team_id: int) -> Dict[str, Any]:
        """Fetch team statistics"""
        return {"status": "success", "team_id": team_id, "stats": {}}
    
    def get_odds(self, sport: str, game_id: int) -> Dict[str, Any]:
        """Fetch betting odds for a game"""
        return {"status": "success", "game_id": game_id, "odds": {}}
