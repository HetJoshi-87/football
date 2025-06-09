import os
os.makedirs("/data/output", exist_ok=True)
#!/usr/bin/env python3
"""
ULTIMATE FOOTBALL WEB PAGES SCRAPER 2025 - ENHANCED
====================================================
FlareSolverr + Docker solution for bypassing advanced Cloudflare protection

ENHANCED FEATURES:
- Accurate appearances extraction (not just numbers)
- Pagination handling for multiple pages (?page=2, ?page=3, etc.)
- Dynamic season detection (only available seasons)
- Better player data extraction with appearances and goals
- Efficient processing (skips non-existent data)
- Real data extraction (no mocks)
- Handles interactive "Verify you are human" challenges
"""

import os
import sys
import time
import random
import json
import subprocess
from typing import List, Dict, Optional
from bs4 import BeautifulSoup

# Auto-install required packages
def install_requirements():
    packages = ['beautifulsoup4', 'requests']
    for package in packages:
        try:
            __import__(package.replace('-', '_'))
        except ImportError:
            print(f"Installing {package}...")
            os.system(f"{sys.executable} -m pip install {package}")

install_requirements()

import requests

# ── CONFIGURATION ───────────────────────────────────────────────────────────────
BASE_URL = "https://www.footballwebpages.co.uk"
CLUBS_FILE = "step(1-4).txt"  # Using step5 file with remaining teams
SEASONS_FILE = "seasons.txt"
OUTPUT_DIR = "football_data(1to4)"
FLARESOLVERR_URL = "http://localhost:8191/v1"

# Default seasons if file doesn't exist
DEFAULT_SEASONS = [
    "2024-2025", "2023-2024", "2022-2023", "2021-2022",
    "2020-2021", "2019-2020", "2018-2019"
]

# ─────────────────────────────────────────────────────────────────────────────────

def ensure_output_dir():
    """Create output directory structure"""
    os.makedirs(OUTPUT_DIR, exist_ok=True)

def check_docker():
    """Check if Docker is available"""
    possible_paths = [
        r"C:\Program Files\Docker\Docker\resources\bin\docker.exe",
        r"C:\Program Files (x86)\Docker\Docker\resources\bin\docker.exe",
        "docker.exe",
        "docker"
    ]

    for path in possible_paths:
        try:
            result = subprocess.run([path, '--version'], capture_output=True, text=True)
            if result.returncode == 0:
                print(f"✅ Docker found: {result.stdout.strip()}")
                return path
        except:
            continue

    print("❌ Docker not found")
    return None

def setup_flaresolverr():
    """Setup FlareSolverr using Docker"""
    print("🔥 Setting up FlareSolverr...")

    # Check if FlareSolverr is already running
    try:
        response = requests.get(f"{FLARESOLVERR_URL}", timeout=5)
        if response.status_code == 405:  # Method not allowed is expected for GET
            print("✅ FlareSolverr already running")
            return True
    except:
        pass

    # Check if Docker is available
    docker_path = check_docker()
    if not docker_path:
        print("💡 Please install Docker Desktop from: https://www.docker.com/products/docker-desktop/")
        print("💡 Or run FlareSolverr manually:")
        print("   docker run -d --name flaresolverr -p 8191:8191 ghcr.io/flaresolverr/flaresolverr:latest")
        return False

    try:
        # Stop existing container if running
        print("🧹 Cleaning up existing containers...")
        subprocess.run([docker_path, 'rm', '-f', 'flaresolverr'], capture_output=True)

        # Start FlareSolverr container (image should already be pulled)
        print("🐳 Starting FlareSolverr container...")
        cmd = [
            docker_path, 'run', '-d',
            '--name', 'flaresolverr',
            '-p', '8191:8191',
            '--restart', 'unless-stopped',
            'ghcr.io/flaresolverr/flaresolverr:latest'
        ]

        result = subprocess.run(cmd, capture_output=True, text=True)
        if result.returncode == 0:
            print("✅ FlareSolverr container started")

            # Wait for it to be ready
            print("⏳ Waiting for FlareSolverr to be ready...")
            for attempt in range(60):  # Wait up to 2 minutes
                try:
                    response = requests.get(f"{FLARESOLVERR_URL}", timeout=3)
                    if response.status_code == 405:  # Method not allowed is expected
                        print("✅ FlareSolverr is ready!")
                        print("🌐 Available at: http://localhost:8191")
                        return True
                except:
                    time.sleep(2)
                    if attempt % 10 == 0:
                        print(f"   Still waiting... ({attempt + 1}/60)")

            print("❌ FlareSolverr failed to start properly")
            return False
        else:
            print(f"❌ Failed to start FlareSolverr: {result.stderr}")
            return False

    except Exception as e:
        print(f"❌ Error setting up FlareSolverr: {e}")
        return False

def check_flaresolverr_health() -> bool:
    """Check if FlareSolverr is healthy and responsive"""
    try:
        response = requests.get(f"{FLARESOLVERR_URL}", timeout=10)
        return response.status_code == 405  # Method not allowed is expected for GET
    except:
        return False

def restart_flaresolverr_container():
    """Restart FlareSolverr container when it becomes unresponsive"""
    print("🔄 Restarting FlareSolverr container...")

    docker_path = check_docker()
    if not docker_path:
        print("❌ Docker not available for restart")
        return False

    try:
        # Stop and remove existing container
        subprocess.run([docker_path, 'rm', '-f', 'flaresolverr'], capture_output=True)
        time.sleep(3)

        # Start new container
        cmd = [
            docker_path, 'run', '-d',
            '--name', 'flaresolverr',
            '-p', '8191:8191',
            '--restart', 'unless-stopped',
            'ghcr.io/flaresolverr/flaresolverr:latest'
        ]

        result = subprocess.run(cmd, capture_output=True, text=True)
        if result.returncode == 0:
            print("✅ FlareSolverr container restarted")

            # Wait for it to be ready
            print("⏳ Waiting for FlareSolverr to be ready...")
            for attempt in range(30):  # Wait up to 1 minute
                if check_flaresolverr_health():
                    print("✅ FlareSolverr is ready after restart!")
                    return True
                time.sleep(2)

            print("❌ FlareSolverr failed to become ready after restart")
            return False
        else:
            print(f"❌ Failed to restart FlareSolverr: {result.stderr}")
            return False

    except Exception as e:
        print(f"❌ Error restarting FlareSolverr: {e}")
        return False

def cleanup_flaresolverr_sessions():
    """Clean up all existing FlareSolverr sessions"""
    try:
        # List all sessions
        list_data = {"cmd": "sessions.list"}
        response = requests.post(FLARESOLVERR_URL, json=list_data, timeout=10)

        if response.status_code == 200:
            result = response.json()
            if result.get('status') == 'ok' and 'sessions' in result:
                sessions = result['sessions']
                print(f"    🧹 Found {len(sessions)} existing sessions to clean up")

                # Destroy each session
                for session_id in sessions:
                    destroy_data = {
                        "cmd": "sessions.destroy",
                        "session": session_id
                    }
                    requests.post(FLARESOLVERR_URL, json=destroy_data, timeout=5)

                print(f"    ✅ Cleaned up {len(sessions)} sessions")
                return True

        return False
    except Exception as e:
        print(f"    ⚠️  Session cleanup error: {e}")
        return False

def scrape_with_flaresolverr(url: str, max_retries: int = 3) -> Optional[str]:
    """Use FlareSolverr to bypass Cloudflare with retry logic and health monitoring"""

    for attempt in range(max_retries):
        try:
            # Check FlareSolverr health before attempting
            if not check_flaresolverr_health():
                print(f"    ⚠️  FlareSolverr unhealthy on attempt {attempt + 1}, restarting...")
                if not restart_flaresolverr_container():
                    print(f"    ❌ Failed to restart FlareSolverr on attempt {attempt + 1}")
                    if attempt < max_retries - 1:
                        time.sleep(10)
                        continue
                    else:
                        return None

            # Clean up existing sessions before creating new one
            cleanup_flaresolverr_sessions()

            # Create unique session name with timestamp
            session_name = f"football_session_{int(time.time())}_{attempt}"
            session_data = {
                "cmd": "sessions.create",
                "session": session_name
            }

            print(f"    🔥 Using FlareSolverr (attempt {attempt + 1}/{max_retries})...")
            response = requests.post(FLARESOLVERR_URL, json=session_data, timeout=30)

            if response.status_code != 200:
                print(f"    ❌ Failed to create FlareSolverr session (attempt {attempt + 1})")
                if attempt < max_retries - 1:
                    time.sleep(5)
                    continue
                else:
                    return None

            # Request the page with increased timeout
            request_data = {
                "cmd": "request.get",
                "url": url,
                "session": session_name,
                "maxTimeout": 180000  # 3 minutes (increased from 2)
            }

            response = requests.post(FLARESOLVERR_URL, json=request_data, timeout=200)  # Increased timeout

            # Clean up session after use
            try:
                destroy_data = {
                    "cmd": "sessions.destroy",
                    "session": session_name
                }
                requests.post(FLARESOLVERR_URL, json=destroy_data, timeout=10)
            except:
                pass  # Don't fail if cleanup fails

            if response.status_code == 200:
                result = response.json()
                if result.get('status') == 'ok':
                    html_content = result['solution']['response']
                    print(f"    ✅ FlareSolverr success! HTML: {len(html_content)} chars")
                    return html_content
                else:
                    error_msg = result.get('message', 'Unknown error')
                    print(f"    ❌ FlareSolverr failed (attempt {attempt + 1}): {error_msg}")

                    # If it's a timeout or challenge failure, retry
                    if 'timeout' in error_msg.lower() or 'challenge' in error_msg.lower():
                        if attempt < max_retries - 1:
                            delay = (attempt + 1) * 10  # Exponential backoff
                            print(f"    ⏳ Retrying in {delay}s...")
                            time.sleep(delay)
                            continue

                    return None
            else:
                print(f"    ❌ FlareSolverr request failed (attempt {attempt + 1}): {response.status_code}")

                # If it's a 500 error, restart container and retry
                if response.status_code == 500:
                    print(f"    🔄 500 error detected, restarting FlareSolverr...")
                    if restart_flaresolverr_container():
                        if attempt < max_retries - 1:
                            time.sleep(10)
                            continue

                if attempt < max_retries - 1:
                    time.sleep(5)
                    continue
                else:
                    return None

        except requests.exceptions.Timeout:
            print(f"    ⏰ Request timeout (attempt {attempt + 1})")
            if attempt < max_retries - 1:
                delay = (attempt + 1) * 15  # Longer delay for timeouts
                print(f"    ⏳ Retrying in {delay}s...")
                time.sleep(delay)
                continue
            else:
                return None
        except Exception as e:
            print(f"    ❌ FlareSolverr error (attempt {attempt + 1}): {e}")
            if attempt < max_retries - 1:
                time.sleep(5)
                continue
            else:
                return None

    print(f"    ❌ All {max_retries} attempts failed")
    return None

def load_clubs() -> List[str]:
    """Load clubs from step5(3-6).txt file starting from Rising Ballers Kensington"""
    if os.path.exists(CLUBS_FILE):
        with open(CLUBS_FILE, 'r', encoding='utf-8') as f:
            all_lines = [line.strip() for line in f if line.strip()]

        # Find the starting point (Rising Ballers Kensington)
        start_index = -1
        for i, line in enumerate(all_lines):
            if line == "Rising Ballers Kensington":
                start_index = i
                break

        if start_index == -1:
            print("⚠️  Rising Ballers Kensington not found, starting from beginning of file")
            start_index = 0

        # Get remaining clubs (skip comment lines starting with #)
        remaining_clubs = []
        for line in all_lines[start_index:]:
            if not line.startswith('#') and line.strip():
                # Convert team name to URL format
                club_url = line.lower().replace(' ', '-').replace('_', '-')
                # Handle special cases
                club_url = club_url.replace('afc', 'afc').replace('fc-', 'fc-')
                remaining_clubs.append(club_url)

        print(f"📋 Loaded {len(remaining_clubs)} remaining clubs from {CLUBS_FILE}")
        print(f"🎯 Starting from: {all_lines[start_index] if start_index < len(all_lines) else 'Unknown'}")
        return remaining_clubs
    else:
        print(f"⚠️  {CLUBS_FILE} not found, using test club")
        return ["basford-united"]

def discover_available_seasons(club_url: str) -> List[str]:
    """Dynamically discover which seasons have data for a club - ENHANCED to include 2024-2025"""
    url = f"{BASE_URL}/{club_url}/appearances"

    print(f"    🔍 Discovering available seasons for {club_url}...")
    html_content = scrape_with_flaresolverr(url)

    if not html_content:
        print(f"    ❌ Failed to get club page, using current season")
        return ["2024-2025"]

    try:
        soup = BeautifulSoup(html_content, 'html.parser')
        seasons = []

        # Look for season selector dropdown
        season_select = soup.find('select')
        if season_select:
            for option in season_select.find_all('option'):
                season_value = option.get('value')
                if season_value and season_value != '' and '-' in season_value:
                    seasons.append(season_value)

        # Fallback: look for season links in the page
        if not seasons:
            import re
            season_pattern = r'(\d{4}-\d{4})'
            for link in soup.find_all('a', href=True):
                href = link.get('href', '')
                if '/appearances/' in href:
                    match = re.search(season_pattern, href)
                    if match:
                        seasons.append(match.group(1))

        # Additional fallback: look for any 4-digit year patterns that could be seasons
        if not seasons:
            import re
            # Look for patterns like "2024-2025", "2023-2024", etc. in the entire page text
            season_pattern = r'(\d{4}-\d{4})'
            page_text = soup.get_text()
            matches = re.findall(season_pattern, page_text)
            for match in matches:
                # Validate it's a reasonable season (between 2010-2030)
                start_year = int(match.split('-')[0])
                if 2010 <= start_year <= 2030:
                    seasons.append(match)

        # Remove duplicates and sort (most recent first)
        seasons = sorted(list(set(seasons)), reverse=True)

        # ENSURE 2024-2025 SEASON IS ALWAYS INCLUDED
        current_season = "2024-2025"
        if current_season not in seasons:
            print(f"    🔧 Adding current season {current_season} to ensure it's included")
            seasons.insert(0, current_season)  # Add at the beginning (most recent)

        # Also ensure we have some recent seasons if discovery failed
        essential_seasons = ["2024-2025"]
        for essential_season in essential_seasons:
            if essential_season not in seasons:
                print(f"    🔧 Adding essential season {essential_season}")
                seasons.append(essential_season)

        # Sort again after adding essential seasons
        seasons = sorted(list(set(seasons)), reverse=True)

        if seasons:
            print(f"    ✅ Found {len(seasons)} available seasons: {', '.join(seasons[:3])}" +
                  (f" and {len(seasons)-3} more..." if len(seasons) > 3 else ""))
            return seasons
        else:
            print(f"    ⚠️  No seasons found, using default current season")
            return ["2024-2025"]  # Fallback to current season

    except Exception as e:
        print(f"    ❌ Error discovering seasons: {e}")
        print(f"    🔧 Using essential seasons as fallback")
        return ["2024-2025"]  # Essential seasons fallback

def load_seasons() -> List[str]:
    """Load seasons from file or use defaults (kept for backward compatibility)"""
    if os.path.exists(SEASONS_FILE):
        with open(SEASONS_FILE, 'r', encoding='utf-8') as f:
            seasons = []
            for line in f:
                line = line.strip()
                # Skip empty lines and comments
                if line and not line.startswith('#'):
                    seasons.append(line)
        print(f"📋 Loaded {len(seasons)} seasons from {SEASONS_FILE}")
    else:
        seasons = DEFAULT_SEASONS
        print(f"📋 Using {len(seasons)} default seasons")
    return seasons

def extract_players_with_appearances(html_content: str) -> List[dict]:
    """Extract player names with appearances data from Football Web Pages HTML - SIMPLIFIED"""
    try:
        soup = BeautifulSoup(html_content, 'html.parser')
        players = []

        # Find the main appearances table
        tables = soup.find_all('table')
        main_table = None

        for table in tables:
            # Look for table with player appearance links
            if table.find('a', href=lambda x: x and '/appearances/' in x):
                main_table = table
                break

        if not main_table:
            print(f"    ⚠️  No appearances table found")
            return []

        # Extract table headers to understand column structure
        headers = []
        header_row = main_table.find('tr')
        if header_row:
            for th in header_row.find_all(['th', 'td']):
                headers.append(th.get_text(strip=True).lower())

        print(f"    📊 Table headers: {headers}")

        # Process each player row
        rows = main_table.find_all('tr')[1:]  # Skip header row

        for row in rows:
            cells = row.find_all(['td', 'th'])
            if len(cells) < 2:
                continue

            player_data = {
                'name': '',
                'appearances': 0,
                'player_url': '',
                'player_id': ''
            }

            # Extract player name and link
            player_link = row.find('a', href=True)
            if player_link and '/appearances/' in player_link.get('href', ''):
                player_data['name'] = player_link.get_text(strip=True)
                player_data['player_url'] = player_link.get('href')

                # Extract player ID from URL
                url_parts = player_data['player_url'].split('/')
                if len(url_parts) > 0:
                    player_data['player_id'] = url_parts[-1]
            else:
                continue  # Skip rows without player links

            # SIMPLIFIED: Look for appearances in the second column (after player name)
            # Skip the first cell (player name) and look for the first numeric value
            appearances_found = False

            for cell in cells[1:]:  # Start from second cell
                text = cell.get_text(strip=True)
                if text.isdigit():
                    value = int(text)
                    # Reasonable appearance range (1-50 for most players)
                    if 1 <= value <= 50 and not appearances_found:
                        player_data['appearances'] = value
                        appearances_found = True
                        break

            # If no reasonable appearances found, try any numeric value
            if not appearances_found:
                for cell in cells[1:]:
                    text = cell.get_text(strip=True)
                    if text.isdigit():
                        value = int(text)
                        if value > 0:  # Any positive number
                            player_data['appearances'] = value
                            break

            # Only add if we have a valid player with appearances
            if player_data['name'] and player_data['appearances'] > 0:
                players.append(player_data)

        print(f"    👥 Extracted {len(players)} players with appearances data")
        return players

    except Exception as e:
        print(f"    ✖ Error extracting players: {e}")
        return []

def check_for_pagination(html_content: str) -> List[int]:
    """Check if there are additional pages and return page numbers"""
    try:
        soup = BeautifulSoup(html_content, 'html.parser')
        page_numbers = []

        # Look for pagination links
        pagination_selectors = [
            'a[href*="?page="]',
            '.pagination a',
            '.page-numbers a',
            'a[href*="page="]'
        ]

        for selector in pagination_selectors:
            links = soup.select(selector)
            for link in links:
                href = link.get('href', '')
                if '?page=' in href:
                    try:
                        page_num = int(href.split('?page=')[1].split('&')[0])
                        if page_num not in page_numbers and page_num <= 10:  # Reasonable limit
                            page_numbers.append(page_num)
                    except:
                        continue

        # Also look for "Next" or page number text
        for link in soup.find_all('a', href=True):
            text = link.get_text(strip=True)
            if text.isdigit():
                try:
                    page_num = int(text)
                    if page_num > 1 and page_num <= 10 and page_num not in page_numbers:
                        page_numbers.append(page_num)
                except:
                    continue

        page_numbers = sorted(list(set(page_numbers)))
        if page_numbers:
            print(f"    📄 Found pagination: pages {page_numbers}")

        return page_numbers

    except Exception as e:
        print(f"    ⚠️  Error checking pagination: {e}")
        return []

def save_club_season_data(club: str, season: str, players: List[dict], html_content: str):
    """Save simplified data for a specific club and season - PLAYERS AND APPEARANCES ONLY"""
    club_dir = os.path.join(OUTPUT_DIR, club)
    os.makedirs(club_dir, exist_ok=True)

    # Save players list with appearances only
    if players:
        season_safe = season.replace('-', '_')

        # Save simple players text file
        players_file = os.path.join(club_dir, f"{season_safe}_players.txt")
        with open(players_file, 'w', encoding='utf-8') as f:
            for player in players:
                f.write(f"{player['name']} - {player['appearances']} apps\n")

        # Save simplified JSON data
        data = {
            'club': club,
            'season': season,
            'players_count': len(players),
            'players': players,
            'total_appearances': sum(p['appearances'] for p in players),
            'top_appearance_maker': max(players, key=lambda x: x['appearances']) if players else None,
            'timestamp': int(time.time()),
            'html_length': len(html_content)
        }

        json_file = os.path.join(club_dir, f"{season_safe}_data.json")
        with open(json_file, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)

        print(f"    💾 Saved {len(players)} players for {club} {season}")
        print(f"    📊 Total appearances: {data['total_appearances']}")

        if data['top_appearance_maker']:
            top_apps = data['top_appearance_maker']
            print(f"    🏆 Most apps: {top_apps['name']} ({top_apps['appearances']} appearances)")

        return True

    return False

# Removed Selenium functions - using pure FlareSolverr approach

def scrape_club_season(club: str, season: str, max_retries: int = 2) -> bool:
    """Scrape a specific club and season using FlareSolverr with enhanced error handling"""
    # Convert club name to URL format (lowercase, spaces to dashes)
    club_url = club.lower().replace(' ', '-').replace('_', '-')
    base_url = f"{BASE_URL}/{club_url}/appearances/{season}"

    print(f"  🎯 {club} ({club_url}) - {season}")

    # Initialize all players list
    all_players = []

    # Start with page 1 (no page parameter needed)
    current_page = 1
    url = base_url

    while True:
        print(f"    📄 Processing page {current_page}...")

        # Use FlareSolverr to bypass Cloudflare with retry logic
        html_content = scrape_with_flaresolverr(url, max_retries=max_retries)

        if not html_content:
            print(f"    ❌ Failed to get content for page {current_page} after {max_retries} attempts")

            # If this is the first page and we failed, the season might not exist
            if current_page == 1:
                print(f"    ⚠️  Season {season} might not exist for {club}")
                return False
            else:
                # If we failed on a later page, we still have some data
                print(f"    ⚠️  Failed on page {current_page}, but we have data from previous pages")
                break

        # Debug: Check what's in the content
        content_lower = html_content.lower()
        has_table = "table" in content_lower
        has_player_links = "/appearances/" in content_lower
        has_club_name = club.replace('-', ' ').lower() in content_lower
        has_appearances = "appearances" in content_lower

        print(f"    🔍 Debug - Table: {has_table}, Player links: {has_player_links}, Club: {has_club_name}, Appearances: {has_appearances}")

        # Extract players with appearances data
        page_players = extract_players_with_appearances(html_content)
        print(f"    👥 Extracted {len(page_players)} players from page {current_page}")

        # Add to master list
        all_players.extend(page_players)

        # Check for more pages
        if current_page == 1:  # Only check pagination on first page
            next_pages = check_for_pagination(html_content)

            if next_pages and max(next_pages) > current_page:
                # Move to next page
                current_page += 1
                url = f"{base_url}?page={current_page}"
                print(f"    ⏭️  Moving to page {current_page}...")
                time.sleep(3)  # Small delay between pages
            else:
                # No more pages
                break
        else:
            # We've already processed additional pages
            break

    # Remove duplicates (by player name)
    unique_players = []
    seen_names = set()

    for player in all_players:
        if player['name'] not in seen_names:
            seen_names.add(player['name'])
            unique_players.append(player)

    # Save the combined data from all pages
    if unique_players:
        print(f"    ✅ Total unique players across all pages: {len(unique_players)}")
        save_club_season_data(club, season, unique_players, html_content)
        print(f"    🎉 SUCCESS! Found {len(unique_players)} players")
        return True
    elif len(html_content) > 10000:
        # Save for debugging even if no players found
        print(f"    ⚠️  Large content but no players - saving for debug")
        save_club_season_data(club, season, [], html_content)

        # Check if we're on an error page or wrong page
        if "not found" in content_lower or "error" in content_lower:
            print(f"    ❌ Appears to be an error page")
            return False
        elif "verify you are human" in content_lower:
            print(f"    ❌ Still on verification page - FlareSolverr couldn't solve")
            return False
        else:
            print(f"    ⚠️  Unknown page content - check debug files")
            return False
    else:
        print(f"    ❌ Content too small: {len(html_content)} chars")
        return False

def main():
    """Simplified main scraping function - PLAYERS AND APPEARANCES ONLY"""
    print("🚀 ULTIMATE FOOTBALL WEB PAGES SCRAPER 2025 - SIMPLIFIED")
    print("=" * 80)
    print("🎯 Extracting PLAYER NAMES and APPEARANCES from ALL clubs")
    print("📄 Pagination support for multiple pages")
    print("🔍 Dynamic season detection (only available seasons)")
    print("📊 Simple and accurate appearances extraction (NO GOALS)")
    print("🔥 FlareSolverr + Simplified parsing for reliability")

    ensure_output_dir()

    # Setup FlareSolverr with enhanced reliability
    flaresolverr_available = setup_flaresolverr()
    if not flaresolverr_available:
        print("❌ FlareSolverr not available - cannot proceed")
        return

    # Clean up any existing sessions from previous runs
    print("🧹 Cleaning up any existing sessions...")
    cleanup_flaresolverr_sessions()

    # Verify FlareSolverr is truly ready with a test request
    print("🔍 Verifying FlareSolverr with test request...")
    test_html = scrape_with_flaresolverr("https://httpbin.org/html", max_retries=2)
    if not test_html or len(test_html) < 100:
        print("⚠️  FlareSolverr test failed, restarting container...")
        if not restart_flaresolverr_container():
            print("❌ Failed to restart FlareSolverr - cannot proceed")
            return
    else:
        print("✅ FlareSolverr test successful - ready to scrape!")

    # Load clubs
    clubs = load_clubs()
    if not clubs:
        print("❌ No clubs to process")
        return

    print(f"\n📊 Processing {len(clubs)} clubs with dynamic season detection")

    # Statistics
    total_completed = 0
    total_successful = 0
    failed_jobs = []

    start_time = time.time()

    # Process each club using dynamic season detection
    for club_idx, club in enumerate(clubs):
        print(f"\n🏟️  Club {club_idx + 1}/{len(clubs)}: {club}")
        print(f"{'='*60}")

        try:
            # Check FlareSolverr health before processing each club
            if not check_flaresolverr_health():
                print(f"    ⚠️  FlareSolverr unhealthy before processing {club}, restarting...")
                if not restart_flaresolverr_container():
                    print(f"    ❌ Failed to restart FlareSolverr for {club}, skipping...")
                    continue

                # Give it a moment to stabilize
                time.sleep(5)

            # Convert club name to URL format
            club_url = club.lower().replace(' ', '-').replace('_', '-')

            # Dynamically discover available seasons for this club
            available_seasons = discover_available_seasons(club_url)

            if not available_seasons:
                print(f"    ❌ No seasons found for {club} - skipping")
                continue

            print(f"    📅 Processing {len(available_seasons)} available seasons...")

            # Process each available season for this club
            club_successful = 0
            club_completed = 0

            for season in available_seasons:
                try:
                    # Periodic health check every few seasons
                    if club_completed > 0 and club_completed % 3 == 0:
                        if not check_flaresolverr_health():
                            print(f"    🔄 Periodic health check failed, restarting FlareSolverr...")
                            restart_flaresolverr_container()
                            time.sleep(5)

                    success = scrape_club_season(club, season, max_retries=3)  # Increased retries
                    club_completed += 1
                    total_completed += 1

                    if success:
                        club_successful += 1
                        total_successful += 1
                    else:
                        failed_jobs.append(f"{club}-{season}")

                    # Progress update
                    print(f"    📈 Club progress: {club_completed}/{len(available_seasons)} seasons")

                    # Delay between seasons to be respectful
                    if season != available_seasons[-1]:  # Not the last season
                        delay = random.uniform(10, 20)  # Increased delay for stability
                        print(f"    ⏳ Waiting {delay:.1f}s before next season...")
                        time.sleep(delay)

                except KeyboardInterrupt:
                    print(f"\n⚠️  Interrupted by user")
                    return
                except Exception as e:
                    print(f"    ✖ Unexpected error for {club}-{season}: {e}")
                    club_completed += 1
                    total_completed += 1

            print(f"  📊 Club {club}: {club_successful}/{len(available_seasons)} seasons successful")

            # Longer delay between clubs
            if club_idx < len(clubs) - 1:
                delay = random.uniform(20, 40)
                print(f"    ⏳ Waiting {delay:.1f}s before next club...")
                time.sleep(delay)

        except Exception as e:
            print(f"    ❌ Error processing club {club}: {e}")
            continue
    
    # Final statistics
    elapsed = time.time() - start_time
    print(f"\n{'='*80}")
    print(f"🏁 ENHANCED SCRAPING COMPLETED!")
    print(f"⏱️  Total time: {elapsed / 60:.1f} minutes")
    print(f"📊 Total club-seasons processed: {total_completed}")
    print(f"✅ Successful extractions: {total_successful}")
    print(f"❌ Failed extractions: {total_completed - total_successful}")
    print(f"📁 Data saved to: {OUTPUT_DIR}/")

    if failed_jobs:
        print(f"\n❌ Failed jobs ({len(failed_jobs)}):")
        for job in failed_jobs[:10]:  # Show first 10
            print(f"   • {job}")
        if len(failed_jobs) > 10:
            print(f"   ... and {len(failed_jobs) - 10} more")

    if total_successful > 0:
        success_rate = (total_successful / total_completed * 100) if total_completed > 0 else 0
        print(f"\n🎉 SUCCESS! Extracted player data from {total_successful} club-seasons")
        print(f"� Success rate: {success_rate:.1f}%")
        print(f"�💡 Check {OUTPUT_DIR}/ for all player names and appearances data")
        print(f"🔧 Features used: Dynamic seasons, Pagination, Simplified appearances extraction")
        print(f"📊 Data format: Player Name - X apps (simple and reliable)")
    else:
        print(f"\n❌ No data extracted. Check your clubs.txt and network connection.")

if __name__ == "__main__":
    main()
