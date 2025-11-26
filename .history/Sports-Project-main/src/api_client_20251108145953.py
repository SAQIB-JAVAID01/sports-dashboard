import requests
import aiohttp
import logging
import time
from typing import Dict, Any, List, Optional, Union
from datetime import datetime, timedelta
import asyncio
import re
import sys
from collections import Counter

# --- Configure logger for src.api_client ---
logging.basicConfig(level=logging.INFO, format='%(levelname)s:%(name)s:%(message)s', stream=sys.stdout)
logger = logging.getLogger('src.api_client')
logger.setLevel(logging.DEBUG) 
logger.error("!!! API_CLIENT_VERSION_7.18_FINAL_ODDS_RETENTION_LOADED !!!") 

class APIFootballClient:
    """Client for interacting with API-Sports (api-sports.io) API - Multi-sport support"""

    SPORT_BASE_URLS = {
        'NFL': 'https://v1.american-football.api-sports.io',
        'NBA': 'https://v1.basketball.api-sports.io',
        'MLB': 'https://v1.baseball.api-sports.io',
        'NHL': 'https://v1.hockey.api-sports.io'
    }

    SPORT_ENDPOINTS = {
        'NFL': {'games': '/games', 'leagues': '/leagues', 'odds': '/odds'},
        'NBA': {'games': '/games', 'leagues': '/leagues', 'odds': '/odds'},
        'MLB': {'games': '/games', 'leagues': '/leagues', 'odds': '/odds'},
        'NHL': {'games': '/games', 'leagues': '/leagues', 'odds': '/odds'}
    }

    SPORT_LEAGUE_IDS = {
        'NFL': 1,      # NFL
        'NBA': 12,     # NBA (League ID for the primary NBA competition)
        'MLB': 1,      # MLB
        'NHL': 57      # NHL
    }

    def __init__(self, api_key: str, sport: str = "NFL"):
        self.api_key = api_key
        self.current_sport = sport.upper()
        self.base_url = self.SPORT_BASE_URLS.get(self.current_sport, self.SPORT_BASE_URLS['NFL']).rstrip('/')
        self._season_cache = {}
        logger.info(f"API client initialized for {self.current_sport} using base URL: {self.base_url}")

    def set_sport(self, sport: str):
        """Change the current sport"""
        sport = sport.upper()
        if sport in self.SPORT_BASE_URLS:
            self.current_sport = sport
            self.base_url = self.SPORT_BASE_URLS[sport].rstrip('/')
            self._season_cache.pop(sport, None)
            logger.info(f"API client switched to {sport} using base URL: {self.base_url}")
        else:
            logger.warning(f"Unknown sport: {sport}, keeping {self.current_sport}")

    def _make_request(self, endpoint: str, params: Optional[Dict] = None, retries: int = 3) -> Optional[Union[List, Dict]]:
        """Make a GET request to the API with retry logic (Synchronous)"""
        url = f"{self.base_url}{endpoint}"
        request_headers = {'x-apisports-key': self.api_key}

        for attempt in range(retries):
            try:
                logger.debug(f"SYNC REQUEST: {url} | Params: {params} (Attempt {attempt + 1}/{retries})")
                response = requests.get(url, headers=request_headers, params=params, timeout=15)
                response.raise_for_status()
                data = response.json()
                
                logger.debug(f"SYNC RESPONSE: Raw data received:\n{data}")
                
                if 'errors' in data and data['errors']:
                    error_message = f"API returned errors: {data['errors']}"
                    logger.error(error_message)
                    if 'message' in str(data['errors']) and 'No games found' in str(data['errors']):
                        return []
                    return None
                
                return data.get('response', [])
            except requests.exceptions.HTTPError as e:
                logger.error(f"HTTP error for {url}: {e.response.status_code} - {e.response.text}")
                if attempt + 1 < retries:
                    logger.info(f"Retrying in {2 ** attempt} seconds...")
                    time.sleep(2 ** attempt)
                else:
                    logger.error(f"All {retries} attempts failed for {url}")
                    return None
            except requests.exceptions.RequestException as e:
                logger.error(f"API request failed: {e}")
                if attempt + 1 < retries:
                    logger.info(f"Retrying in {2 ** attempt} seconds...")
                    time.sleep(2 ** attempt)
                else:
                    logger.error(f"All {retries} attempts failed for {url}")
                    return None
        return None

    async def _make_request_async(self, session: aiohttp.ClientSession, endpoint: str, params: Optional[Dict] = None) -> Optional[List]:
        """Make an asynchronous GET request to the API"""
        url = f"{self.base_url}{endpoint}"
        request_headers = {'x-apisports-key': self.api_key}

        for attempt in range(3):
            try:
                logger.debug(f"ASYNC REQUEST: {url} | Params: {params} (Attempt {attempt + 1}/3)")
                async with session.get(url, headers=request_headers, params=params, timeout=aiohttp.ClientTimeout(total=15)) as response:
                    response.raise_for_status()
                    data = await response.json()
                    
                    logger.debug(f"ASYNC RESPONSE: Raw data received:\n{data}")
                    
                    if 'errors' in data and data['errors']:
                        error_message = f"API returned errors: {data['errors']}"
                        return data.get('response', [])
                    
                    return data.get('response', [])
            except Exception as e:
                logger.error(f"Async API request failed: {str(e)}")
                if attempt + 1 < 3:
                    logger.info(f"Retrying async request in {2 ** attempt} seconds...")
                    await asyncio.sleep(2 ** attempt)
                else:
                    logger.error(f"All 3 async attempts failed for {url}")
                    return None
        return None

    def fetch_historical_data_range(self, sport: str, start_date_str: str, end_date_str: str) -> List[Dict]:
        """Fetches historical data for a specified date range (synchronous/blocking call)."""
        self.set_sport(sport)
        
        try:
            start_date = datetime.strptime(start_date_str, '%Y-%m-%d').date()
            end_date = datetime.strptime(end_date_str, '%Y-%m-%d').date()
        except ValueError:
            logger.error("Invalid date format provided for historical fetch. Use YYYY-MM-DD.")
            return []
        
        all_games = []
        current_date = end_date
        season = self.get_current_season()

        if season is None:
              logger.error("Could not determine season for historical fetch.")
              return []
        
        while current_date >= start_date:
            date_to_fetch = current_date.strftime('%Y-%m-%d')
            logger.info(f"Fetching historical games for date: {date_to_fetch} (Season: {season})")
            
            params = {
                'date': date_to_fetch,  
                'league': self.SPORT_LEAGUE_IDS.get(sport, 1),  
                'season': season
            }
            
            endpoint = self.SPORT_ENDPOINTS[sport]['games']
            games_raw = self._make_request(endpoint, params)
            
            if games_raw and isinstance(games_raw, list):
                parsed_games = [self.parse_game_data(game, season) for game in games_raw if isinstance(game, dict)]
                all_games.extend([g for g in parsed_games if g.get('status') != 'Error/Unknown'])
                logger.debug(f"Received {len(parsed_games)} raw elements for {date_to_fetch}.")
            
            time.sleep(1.5)    
            current_date -= timedelta(days=1)

        logger.info(f"Finished historical fetch. Total games retrieved: {len(all_games)}")
        return all_games

    def get_current_season(self) -> Optional[Union[str, int]]:
        """
        Calculates the current season based on the date, as API lookup often fails.
        """
        if self.current_sport in self._season_cache:
            return self._season_cache[self.current_sport]
        
        current_year = datetime.now().year
        current_month = datetime.now().month
        
        # --- SEASON BYPASS LOGIC ---
        season_result = None
        if self.current_sport in ['NBA', 'NHL']:
            # NBA/NHL are cross-year and start in autumn (Sept/Oct)
            start_year = current_year if current_month >= 9 else current_year - 1
            season_result = f"{start_year}-{start_year + 1}"
        else:
            # NFL/MLB usually use a single integer year
            season_result = current_year
            
        logger.debug(f"Using predicted season: {season_result} for {self.current_sport}.")
        # --- END SEASON BYPASS LOGIC ---

        # Coerce cross-year string format (e.g., 2025-2026) to an integer year (2025)  
        # for APIs that expect integer years for NHL/NFL/MLB.
        if self.current_sport in ['NHL', 'MLB', 'NFL'] and isinstance(season_result, str) and '-' in str(season_result):
              try:
                year_part = int(str(season_result).split('-')[0])
                season_result = year_part
                logger.debug(f"Coerced cross-year season to integer year {year_part} for {self.current_sport} API request.")
              except Exception:
                  logger.warning(f"Could not coerce season to integer for {self.current_sport}. Using raw value: {season_result}")
              
        self._season_cache[self.current_sport] = season_result
        return season_result

    def get_current_week(self) -> Optional[int]:
        if self.current_sport != 'NFL':
              return None
              
        season = self.get_current_season()
        endpoint = self.SPORT_ENDPOINTS['NFL']['games']
        params = {'season': season, 'date': datetime.now().strftime('%Y-%m-%d'), 'league': self.SPORT_LEAGUE_IDS['NFL']}
        data = self._make_request(endpoint, params)
        
        if data and isinstance(data, list) and len(data) > 0:
              round_info = data[0].get('game', {}).get('week', 'Regular Season - Week 1')
              match = re.search(r'Week\s*(\d+)', round_info)
              if match:
                  return int(match.group(1))
              
        return 1

    async def get_live_scores(self) -> List[Dict]:
        async with aiohttp.ClientSession() as session:
            sport_id = self.SPORT_LEAGUE_IDS.get(self.current_sport, 1)
            season = self.get_current_season()
            
            if season is None:
                  logger.error(f"Cannot fetch live scores. Season is None for {self.current_sport}")
                  return []
            
            # Fetch Today and Tomorrow to maximize live/scheduled games
            today = datetime.now().strftime('%Y-%m-%d')
            tomorrow = (datetime.now() + timedelta(days=1)).strftime('%Y-%m-%d')
            
            dates_to_fetch = [today]
            if self.current_sport in ['NFL', 'NBA', 'MLB', 'NHL']:  
                  dates_to_fetch.append(tomorrow)
                  
            all_raw_results = []
            
            for date_to_fetch in dates_to_fetch:
                params = {'date': date_to_fetch, 'league': sport_id, 'season': season}
                endpoint = self.SPORT_ENDPOINTS[self.current_sport]['games']
                logger.info(f"Fetching {self.current_sport} scores for date: {date_to_fetch} (Season: {season})")
                
                result = await self._make_request_async(session, endpoint, params)
                
                if result and isinstance(result, list):
                    all_raw_results.extend(result)
            
            if not all_raw_results:
                logger.warning(f"API returned no games for requested dates {dates_to_fetch}.")
                return []
                
            logger.info(f"API returned total {len(all_raw_results)} scheduled/live/finished games.")
            
            # Parse results
            parsed_results = [self.parse_game_data(game_raw, season) for game_raw in all_raw_results if isinstance(game_raw, dict)]
            
            # Filter to remove games with parsing errors
            if parsed_results:
                return [g for g in parsed_results if g.get('status') != 'Error/Unknown']
            else:
                logger.warning(f"No games found for requested dates {dates_to_fetch}. Returning empty list.")
                return []


    def get_team_stats(self, season: Union[str, int]) -> Optional[List[Dict]]:
        endpoint = '/statistics'
        params = {'season': season, 'league': self.SPORT_LEAGUE_IDS.get(self.current_sport, 1)}
        return self._make_request(endpoint, params)

    def parse_game_data(self, game: Any, season: Union[str, int]) -> Dict:
        """
        Parse and extract relevant game information (sport-aware).
        """
        if not isinstance(game, dict):
              logger.error(f"Parser received non-dictionary input: {game}. Returning empty game dict.")
              return {
                  'game_id': 'N/A', 'sport': self.current_sport, 'status': 'Error/Unknown',  
                  'date': 'N/A', 'away_team': 'N/A', 'home_team': 'N/A', 'away_score': 0,  
                  'home_score': 0, 'current_total': 0, 'quarter': None,  
                  'time_remaining': None, 'ou_line': 0.0, 'spread': 0.0,  
                  'away_team_name': 'N/A', 'home_team_name': 'N/A', 'stadium': 'N/A', 'weather': None
              }

        if self.current_sport == 'NFL':
            return self._parse_american_football_game_data(game, season)
        else:
            return self._parse_other_sport_game_data(game, season)

    def get_game_odds(self, game_id: int) -> Optional[List]:
        endpoint = self.SPORT_ENDPOINTS[self.current_sport]['odds']
        params = {'game': game_id}
        
        game_id_str = str(game_id)  

        logger.info(f"ODDS FETCH: Requesting odds for game ID {game_id_str} for {self.current_sport}...")
        
        response = self._make_request(endpoint, params) 
        if response is None or not response:
              logger.warning(f"ODDS FETCH: No odds data or failed request returned for game {game_id_str}. (Possible API restriction or game in progress)")
        else:
            # Only log a summary if the response is too large
            if len(str(response)) > 2000:
                logger.debug(f"ODDS FETCH: Raw odds response for game {game_id_str}: [Truncated, {len(response)} bookmakers]")
            else:
                logger.debug(f"ODDS FETCH: Raw odds response for game {game_id_str}: {response}")
        return response

    def _parse_american_football_game_data(self, game: Dict, season: Union[str, int]) -> Dict:
        """Parse American Football (NFL) game data from API-Sports response."""
        
        game_data = game.get('game', {})
        teams = game.get('teams', {})
        scores = game.get('scores', {})
        venue_data_raw = game_data.get('venue', {})

        away_team = teams.get('away', {}).get('name', 'AWAY')
        home_team = teams.get('home', {}).get('name', 'HOME')
        
        status_short = game_data.get('status', {}).get('short', '')

        status_map = {
             'TBD': 'Scheduled', 'NS': 'Scheduled', '1Q': 'InProgress', '2Q': 'InProgress', '3Q': 'InProgress', 
             '4Q': 'InProgress', 'HT': 'Halftime', 'OT': 'Overtime', 'AOT': 'FinalOvertime', 'FT': 'Final', 
             'SUSP': 'Suspended', 'PST': 'Postponed', 'CANC': 'Canceled', 'FIN': 'Final'
        }
        parsed_status = status_map.get(status_short, game_data.get('status', {}).get('long', 'Unknown'))

        period = None
        if status_short in ['1Q', '2Q', '3Q', '4Q']:
              period = int(status_short[0])
        elif status_short in ['OT', 'AOT']:
              period = 5  
              
        time_remaining = game_data.get('status', {}).get('timer')
        
        # --- Score Extraction for NFL (Confirmed) ---
        away_score = 0
        home_score = 0
        scores_safe = scores if isinstance(scores, dict) else {}
        
        away_score_raw = scores_safe.get('away', {}).get('total', 0)
        home_score_raw = scores_safe.get('home', {}).get('total', 0)
    
        try:
            away_score = int(away_score_raw) if str(away_score_raw).isdigit() else 0
            home_score = int(home_score_raw) if str(home_score_raw).isdigit() else 0
            current_total = away_score + home_score
        except (ValueError, TypeError):
            current_total = 0
            away_score = 0
            home_score = 0
            logger.warning(f"Non-numeric scores encountered for NFL game {game_data.get('id')}. Resetting scores to 0.")
        # --------------------------------------------------------

        over_under = None
        point_spread = None
        
        game_id = game_data.get('id')
        
        # --- FIX: Odds Fetching Logic Adjustment ---
        # Only skip fetching odds if game is explicitly POSTPONED or CANCELED. 
        # Allow fetching for FINAL games to get the closing line.
        is_postponed_or_canceled = parsed_status.upper() in ['POSTPONED', 'CANCELED']
        
        if game_id and game_id != 'N/A' and not is_postponed_or_canceled:
            try:
                odds_data = self.get_game_odds(game_id)
                ou_candidates = []
                spread_candidates = []
                
                if odds_data and isinstance(odds_data, list) and len(odds_data) > 0:
                    for bookmaker in odds_data:
                        for market in bookmaker.get('bets', []):
                            market_name_lower = market.get('name', '').lower()
                            
                            # --- FIX: ROBUST O/U LINE EXTRACTION ---
                            if market_name_lower in ['over/under', 'total points']:
                                for value in market.get('values', []):
                                    raw_value_text = str(value.get('value', '')).strip()
                                    match = re.search(r'(?:over|under|total)\s*(\d+\.?\d*)', raw_value_text, re.IGNORECASE)
                                    if match:
                                        line_candidate = float(match.group(1))
                                        if 30.0 <= line_candidate < 100.0:
                                            ou_candidates.append(line_candidate)
                            
                            # --- FIX: ROBUST SPREAD EXTRACTION ---
                            if market_name_lower in ['asian handicap', 'spread', 'point spread']:
                                for value in market.get('values', []):
                                    raw_value = str(value.get('value', '')).strip()
                                    spread_match = re.search(r'([+-]?\d+\.?\d*)', raw_value)
                                    
                                    if spread_match:
                                        try:
                                            spread_val = float(spread_match.group(1))
                                            if 0.5 <= abs(spread_val) < 25.0: 
                                                spread_candidates.append(spread_val)
                                        except (ValueError, TypeError): pass
                                        
                    # Final O/U Selection: Pick the most common line
                    if ou_candidates:
                        rounded_candidates = [round(c, 1) for c in ou_candidates if c > 0]
                        if rounded_candidates:
                            most_common_line, count = Counter(rounded_candidates).most_common(1)[0]
                            over_under = most_common_line
                            logger.info(f"ODDS PARSED: Selected O/U Line: {over_under} (Found {count} times) for {self.current_sport} (NFL)")
                        
                    # Final Spread Selection: Pick the value closest to the typical line
                    if spread_candidates:
                        spread_candidates.sort(key=lambda x: abs(x + 3.5)) 
                        point_spread = spread_candidates[0]
                        logger.info(f"SPREAD PARSED: Selected Spread Line: {point_spread} for {self.current_sport} (NFL)")

            except Exception as e:
                logger.debug(f"Failed to fetch or parse odds for game {game_id}: {str(e)}")

        # --- Robust Date Extraction (Confirmed Good) ---
        date_time_raw = game_data.get('date', 'N/A')

        if isinstance(date_time_raw, dict):
             date_time_raw = date_time_raw.get('date', date_time_raw.get('iso', date_time_raw.get('timestamp', 'N/A')))

        date = str(date_time_raw).split('T')[0] if 'T' in str(date_time_raw) and str(date_time_raw) != 'N/A' else str(date_time_raw)

        if date.startswith("{") or date.startswith("dict_keys"):
             date = 'N/A'
        # --- End Date ---
        
        # --- Robust Stadium Extraction (Confirmed Good) ---
        stadium = 'N/A'
        if isinstance(venue_data_raw, dict):
            stadium = venue_data_raw.get('name')
            if not stadium or str(stadium).upper() in ['NONE', 'N/A']:
                stadium = venue_data_raw.get('stadium', {}).get('name')
            if not stadium or str(stadium).upper() in ['NONE', 'N/A']:
                stadium = venue_data_raw.get('arena', {}).get('name') 
        
        if not stadium or str(stadium).upper() in ['NONE', 'N/A']:
            stadium = 'N/A'
        stadium = str(stadium)
        # --- End Stadium ---
        
        
        # FINAL FALLBACKS and CLEANUP for NFL 
        # Check status again using the fully parsed status field
        is_scheduled = parsed_status.upper() in ['SCHEDULED', 'TBD', 'NS']
        is_postponed_or_canceled = parsed_status.upper() in ['POSTPONED', 'CANCELED']
        
        # 1. Fallback for O/U Line (only if odds fetch failed AND not postponed/canceled)
        if (over_under is None or over_under <= 0.0) and not is_postponed_or_canceled:
            over_under = 45.5 
            logger.warning(f"ODDS FALLBACK: Using default NFL total of {over_under} for game {game_id}.")
        
        # 2. Fallback for Spread (only if odds fetch failed AND not postponed/canceled)
        if (point_spread is None or point_spread == 0.0) and not is_postponed_or_canceled:
            point_spread = 3.5
            logger.warning(f"SPREAD FALLBACK: Using default NFL spread of {point_spread} for game {game_id}.")
            
        # 3. Clear odds only if the status is CANCELED/POSTPONED
        # NOTE: Final games now retain their closing line.
        if is_postponed_or_canceled:
            over_under = 0.0
            point_spread = 0.0
        
        # Clear scores for Scheduled games
        if is_scheduled:
            away_score = 0
            home_score = 0
            current_total = 0
            
        logger.debug(f"Final Parsed Stadium (NFL): {stadium}")
        
        return {
             'game_id': game_data.get('id', 'N/A'), 'sport': self.current_sport, 'status': parsed_status, 'date': date,
             'away_team': away_team, 'home_team': home_team, 'away_score': away_score, 'home_score': home_score,
             'current_total': current_total, 'quarter': period, 'time_remaining': time_remaining,
             'ou_line': over_under,  
             'spread': point_spread,  
             'away_team_name': away_team,  
             'home_team_name': home_team,  
             'stadium': stadium,
             'weather': None
        }
        
    def _parse_other_sport_game_data(self, game: Any, season: Union[str, int]) -> Dict:
        """
        VERSION 7.18 FIX: Robust extraction for NBA, MLB, NHL. Retains final odds.
        """
        
        period = None
        over_under = None
        point_spread = None
        
        # --- Core Data Extraction (Unchanged) ---
        game_data = game.get('game', {})
        teams = game.get('teams', {})
        scores = game.get('scores')  
        status_info = game.get('status', {}) if not game_data else game_data.get('status', {})

        # Basic Info
        away_team = teams.get('away', {}).get('name', 'AWAY')
        home_team = teams.get('home', {}).get('name', 'HOME')
        game_id = str(game_data.get('id', game.get('id', 'N/A')))
        
        # --- Date Extraction (Confirmed Good) ---
        date_time_raw = game_data.get('date', game.get('date', 'N/A'))
        if isinstance(date_time_raw, dict):
            date_time_raw = date_time_raw.get('date', date_time_raw.get('iso', 'N/A'))
            
        date = str(date_time_raw).split('T')[0] if 'T' in str(date_time_raw) and str(date_time_raw) != 'N/A' else str(date_time_raw)
        
        # --- Robust Stadium Extraction (Confirmed Good) ---
        venue_data_nested = game_data.get('venue', {})
        venue_data_top = game.get('venue', {}) 
        
        venue_data = venue_data_nested if isinstance(venue_data_nested, dict) and venue_data_nested else venue_data_top 
        
        stadium = 'N/A'
        if isinstance(venue_data, dict):
            stadium = venue_data.get('name')
            
            if not stadium or str(stadium).upper() in ['NONE', 'N/A']:
                 stadium = venue_data.get('arena', {}).get('name')
            if not stadium or str(stadium).upper() in ['NONE', 'N/A']:
                stadium = venue_data.get('stadium', {}).get('name') 
                
        elif isinstance(venue_data, str) and venue_data:
            stadium = venue_data
        
        if not stadium or str(stadium).upper() in ['NONE', 'N/A']:
            stadium = 'N/A'
        stadium = str(stadium)
        # --- End Stadium ---


        # Status Parsing (Confirmed Good) 
        status_short = status_info.get('short', '')
        status_map = {
             'TBD': 'Scheduled', 'NS': 'Scheduled', 'HT': 'Halftime', 'FT': 'Final', 'AOT': 'Final',
             'SUSP': 'Suspended', 'PST': 'Postponed', 'CANC': 'Canceled', 
             '1P': 'InProgress', 'P1': 'InProgress', '2P': 'InProgress', 'P2': 'InProgress', 
             '3P': 'InProgress', 'P3': 'InProgress', '4P': 'InProgress', 'Q1': 'InProgress', 
             'Q2': 'InProgress', 'Q3': 'InProgress', 'Q4': 'InProgress', 'OT': 'Overtime', 'SO': 'Overtime',
             'BT': 'Break Time', 'FIN': 'Final'
        }
        parsed_status = status_map.get(status_short, status_info.get('long', status_short or 'Unknown'))
        if 'FINAL' in parsed_status.upper() or status_short in ['FT', 'AOT', 'FIN']: 
             parsed_status = 'Final'
        
        # --- Score Calculation (Robust for NBA/NHL/MLB - Confirmed) ---
        away_score = 0; home_score = 0
        if scores and isinstance(scores, dict):
            if isinstance(scores.get('home'), dict) and 'total' in scores['home']:
                try: 
                    away_score = int(scores.get('away', {}).get('total', 0))
                    home_score = int(scores.get('home', {}).get('total', 0))
                except (ValueError, TypeError): pass
            
            elif 'home' in scores and 'away' in scores:
                try:
                    away_score = int(scores.get('away', 0)) if str(scores.get('away', '')).isdigit() else 0
                    home_score = int(scores.get('home', 0)) if str(scores.get('home', '')).isdigit() else 0
                except (ValueError, TypeError): pass

        current_total = away_score + home_score
        # ----------------------------------------------------------------------

        # --- Period/Time Remaining (Confirmed) ---
        if status_short and status_short[0] in ['Q', 'P']:
              match = re.search(r'(\d+)', status_short)
              if match:
                  period = int(match.group(1))
        elif status_short in ['OT', 'SO', 'AOT']:
              period = 4 if self.current_sport == 'NHL' else 5
        
        time_remaining = status_info.get('timer', None)

        # --- Odds Fetching (Centralized and Robust) ---
        game_id_str = str(game_id)
        
        # NEW FIX: Only skip odds fetching if the game is CANCELED or POSTPONED.
        # This allows Final games to fetch their closing line if the API provides it.
        is_postponed_or_canceled = parsed_status.upper() in ['POSTPONED', 'CANCELED', 'SUSPENDED']
        
        if game_id != 'N/A' and not is_postponed_or_canceled:
            try:
                game_id_int = int(game_id)
                odds_data = self.get_game_odds(game_id_int)
                
                ou_candidates = []
                spread_candidates = []
                
                if odds_data and isinstance(odds_data, list) and len(odds_data) > 0:
                    for bookmaker in odds_data:
                        for market in bookmaker.get('bets', []):
                            market_name_lower = market.get('name', '').lower()

                            # 1. O/U Line Extraction (Prioritize full game totals)
                            if market_name_lower in ['over/under', 'totals', 'total goals', 'total runs', 'total goals (including ot)', 'over/under (reg time)']:
                                for value in market.get('values', []):
                                    raw_value_text = str(value.get('value', '')).strip()
                                    
                                    match = re.search(r'(?:over|under|total)\s*([\+\-]?\d+\.?\d*)', raw_value_text, re.IGNORECASE)
                                    if match:
                                        line_candidate = float(match.group(1))
                                        
                                        # Use sport-specific filtering logic
                                        if self.current_sport == 'NBA' and 100.0 <= line_candidate < 300.0:
                                            ou_candidates.append(line_candidate)
                                        elif self.current_sport in ['NHL', 'MLB'] and 4.0 <= line_candidate < 15.0:
                                            ou_candidates.append(line_candidate)
                                        elif self.current_sport == 'NFL' and 30.0 <= line_candidate < 100.0:
                                            ou_candidates.append(line_candidate)
                            
                            # 2. Spread Extraction (Handles Asian Handicap and Point Spread markets)
                            if market_name_lower in ['asian handicap', 'point spread', 'handicap', 'asian handicap (reg time)']:
                                for value in market.get('values', []):
                                    raw_value = str(value.get('value', '')).strip()
                                    
                                    spread_match = re.search(r'([+-]?\d+\.?\d*)', raw_value)
                                    
                                    if spread_match:
                                        try:
                                            spread_val = float(spread_match.group(1))
                                            if 0.5 <= abs(spread_val) < 25.0:
                                                spread_candidates.append(spread_val)
                                        except (ValueError, TypeError): pass
                                        
                    # Final O/U Selection: Pick the most common line
                    if ou_candidates:
                        rounded_candidates = [round(c, 1) for c in ou_candidates if c > 0]
                        
                        if rounded_candidates:
                            most_common_line, count = Counter(rounded_candidates).most_common(1)[0]
                            over_under = most_common_line
                            logger.info(f"ODDS PARSED: Selected O/U Line: {over_under} (Found {count} times) for game {game_id_str}.")
                        
                    # Final Spread Selection: Pick the value closest to the typical line
                    if spread_candidates:
                        target_spread = 1.5 if self.current_sport in ['NHL', 'MLB'] else 5.5
                        
                        filtered_spreads = [s for s in spread_candidates if abs(s) >= 0.5] 
                        
                        if filtered_spreads:
                            # Prioritize spreads closer to the default line
                            filtered_spreads.sort(key=lambda x: (abs(abs(x) - target_spread), abs(x)))
                            point_spread = filtered_spreads[0]
                            logger.info(f"SPREAD PARSED: Selected Spread Line: {point_spread} for game {game_id_str}.")

            except Exception as e:
                logger.debug(f"Failed to fetch or parse odds for game {game_id_str}: {str(e)}")

        
        # === CRITICAL FINAL FALLBACKS AND CLEANUP ===
        is_scheduled = parsed_status.upper() in ['SCHEDULED', 'TBD', 'NS']
        is_postponed_or_canceled = parsed_status.upper() in ['POSTPONED', 'CANCELED', 'SUSPENDED']

        # 1. Fallback for O/U Line (only if odds fetch failed AND not canceled/postponed)
        if (over_under is None or over_under <= 0.0) and not is_postponed_or_canceled:
            if self.current_sport == 'NHL': over_under = 6.5
            elif self.current_sport == 'NBA': over_under = 220.5
            elif self.current_sport == 'MLB': over_under = 8.5
            elif self.current_sport == 'NFL': over_under = 45.5
            if over_under is not None:
                logger.warning(f"ODDS FALLBACK: Using default {self.current_sport} total of {over_under} for game {game_id}.")
            
        # 2. Fallback for Spread (only if odds fetch failed AND not canceled/postponed)
        if (point_spread is None or point_spread == 0.0) and not is_postponed_or_canceled:
            if self.current_sport == 'NHL': point_spread = 1.5 
            elif self.current_sport == 'NBA': point_spread = 5.5
            elif self.current_sport == 'MLB': point_spread = 1.5
            elif self.current_sport == 'NFL': point_spread = 3.5
            if point_spread is not None:
                logger.warning(f"SPREAD FALLBACK: Using default {self.current_sport} spread of {point_spread} for game {game_id}.")

        # 3. Clear odds only if the status is CANCELED/POSTPONED/SUSPENDED
        if is_postponed_or_canceled:
            over_under = 0.0
            point_spread = 0.0
            
        # 4. Clear scores and period for Scheduled games
        if is_scheduled:
            period = None
            away_score = 0
            home_score = 0
            current_total = 0
            
        logger.debug(f"Final Parsed Stadium ({self.current_sport}): {stadium}")
        
        return {
             'game_id': game_id, 'sport': self.current_sport, 'status': parsed_status, 
             'date': date, 'away_team': away_team, 'home_team': home_team, 
             'away_score': away_score, 'home_score': home_score, 'current_total': current_total, 
             'quarter': period, 'time_remaining': time_remaining, 
             'ou_line': over_under,
             'spread': point_spread, 
             'away_team_name': away_team, 'home_team_name': home_team, 
             'stadium': stadium,
             'weather': None 
        }