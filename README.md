# LOLStatsBot 🎮

A Twitch chat bot that displays real-time League of Legends summoner statistics.

## Features
- 📊 Automatically posts summoner level and rank every 30 seconds
- 💬 Responds to `!stats` command for on-demand stats
- 🏆 Shows ranked tier, division, and LP when available
- 🛡️ Smart error handling with no spam
- 🌍 Supports multiple regions

## How It Works
1. Bot connects to Twitch chat using TwitchIO
2. Fetches summoner data from Riot Games API
3. Displays stats automatically or on command

## Commands
| Command | Description |
|---------|-------------|
| `!stats` | Get current summoner stats |

## Technologies Used
- **Python 3.8+**
- **TwitchIO** - Twitch chat integration
- **Riot Games API** - League of Legends data
- **Requests** - HTTP requests

## Setup Instructions

### Prerequisites
```bash
pip install twitchio requests
