import asyncio
import requests
from twitchio import Client
import time
from datetime import datetime

# --------- CONFIGURATION ---------
TWITCH_NICK = "freshnokapo"
TWITCH_OAUTH = "yrr1ymggyy367z94lfy3vtibia6wa3"
CHANNEL = "freshnokapo"
SUMMONER_NAME = "Cringe0master"
REGION = "euw1"  # Try changing this to "na1" or "kr" if needed
RIOT_API_KEY = "RGAPI-45d58b8b-d093-4ebb-bc50-6a4191f31a41"  # Replace with your new key
UPDATE_INTERVAL = 30

# --------- Validate API key on startup ---------
def validate_api_key():
    print("🔍 Validating Riot API key...")
    url = f"https://{REGION}.api.riotgames.com/lol/summoner/v4/summoners/by-name/{SUMMONER_NAME}?api_key={RIOT_API_KEY}"
    
    try:
        response = requests.get(url)
        
        if response.status_code == 200:
            print("✅ API key is valid!")
            return True
        elif response.status_code == 403:
            print("❌ API key is invalid or expired!")
            print("   Solutions:")
            print("   1. Generate a NEW key at https://developer.riotgames.com/")
            print("   2. Wait 10 minutes after generating a new key")
            print("   3. Make sure you're logged into your Riot account")
            print("   4. Apply for a production key if you need permanent access")
            return False
        elif response.status_code == 404:
            print(f"❌ Summoner '{SUMMONER_NAME}' not found on {REGION.upper()}!")
            print("   Try a different region or summoner name")
            return False
        else:
            print(f"⚠️ Unexpected response: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Connection error: {e}")
        return False

# --------- Riot API call ---------
def get_lol_stats():
    try:
        url = f"https://{REGION}.api.riotgames.com/lol/summoner/v4/summoners/by-name/{SUMMONER_NAME}?api_key={RIOT_API_KEY}"
        r = requests.get(url)
        
        if r.status_code == 200:
            data = r.json()
            
            # Try to get ranked stats
            try:
                ranked_url = f"https://{REGION}.api.riotgames.com/lol/league/v4/entries/by-summoner/{data['id']}?api_key={RIOT_API_KEY}"
                ranked_r = requests.get(ranked_url)
                
                if ranked_r.status_code == 200:
                    ranked_data = ranked_r.json()
                    for queue in ranked_data:
                        if queue['queueType'] == 'RANKED_SOLO_5x5':
                            return f"{data['name']} - Level {data['summonerLevel']} | {queue['tier']} {queue['rank']} ({queue['leaguePoints']} LP)"
            except:
                pass
            
            return f"{data['name']} - Level {data['summonerLevel']}"
            
        elif r.status_code == 403:
            return "⚠️ API key expired! Get a new key at developer.riotgames.com (keys last 24h)"
        elif r.status_code == 404:
            return f"❌ Summoner '{SUMMONER_NAME}' not found on {REGION.upper()}"
        else:
            return f"⚠️ API error: {r.status_code}"
            
    except Exception as e:
        return f"⚠️ Error: {str(e)}"

# --------- Twitch Bot ---------
class Bot(Client):
    def __init__(self):
        super().__init__(token=TWITCH_OAUTH, initial_channels=[CHANNEL])
        self.key_validated = False

    async def event_ready(self):
        print(f"✅ Logged in as {self.nick}")
        print(f"📺 Connected to channel: {CHANNEL}")
        
        # Validate API key on startup
        if validate_api_key():
            self.key_validated = True
            print(f"🎮 Monitoring summoner: {SUMMONER_NAME} on {REGION.upper()}")
        else:
            print("⚠️ Bot will run but API calls will fail until key is fixed")
        
        print("=" * 50)
        asyncio.create_task(self.post_stats())

    async def event_message(self, message):
        try:
            if not message or not hasattr(message, 'author') or not message.author:
                return
            
            if message.author.name.lower() == self.nick.lower():
                return
            
            if message.content and message.content.lower().startswith("!stats"):
                if not self.key_validated:
                    await message.channel.send("⚠️ Riot API key not configured. Check console for details.")
                else:
                    stats = get_lol_stats()
                    await message.channel.send(stats)
                    print(f"📊 !stats command used by {message.author.name}")
                
        except AttributeError:
            pass
        except Exception as e:
            print(f"❌ Error: {e}")

    async def post_stats(self):
        await self.wait_for_ready()
        channel = self.get_channel(CHANNEL)
        await asyncio.sleep(5)
        
        error_count = 0
        while True:
            try:
                if not self.key_validated:
                    # Don't spam if key is invalid
                    if error_count == 0:
                        await channel.send("⚠️ Bot waiting for valid Riot API key. Check console for instructions.")
                        error_count += 1
                    await asyncio.sleep(60)  # Wait 1 minute before checking again
                    
                    # Re-validate key periodically
                    if validate_api_key():
                        self.key_validated = True
                        await channel.send("✅ Riot API key validated! Stats will now appear.")
                        error_count = 0
                    continue
                
                stats = get_lol_stats()
                await channel.send(stats)
                print(f"📢 [{datetime.now().strftime('%H:%M:%S')}] Posted: {stats}")
                error_count = 0
                
                # Check if key expired during runtime
                if "expired" in stats:
                    self.key_validated = False
                    
            except Exception as e:
                error_count += 1
                print(f"❌ Error: {e}")
            
            await asyncio.sleep(UPDATE_INTERVAL)

# --------- Run Bot ---------
async def main():
    bot = Bot()
    await bot.start()

if __name__ == "__main__":
    print("🤖 Starting Twitch Bot...")
    print("=" * 50)
    print(f"Bot Name: {TWITCH_NICK}")
    print(f"Channel: {CHANNEL}")
    print(f"Summoner: {SUMMONER_NAME}")
    print(f"Region: {REGION.upper()}")
    print("=" * 50)
    asyncio.run(main())