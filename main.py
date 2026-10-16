import os
import asyncio
import aiohttp
from aiohttp import web
import discord

# Configure Discord Intents
intents = discord.Intents.default()
intents.members = True  # Required to detect member joins
client = discord.Client(intents=intents)

N8N_WEBHOOK_URL = os.environ.get("N8N_WEBHOOK_URL")
PORT = int(os.environ.get("PORT", 10000))
DISCORD_BOT_TOKEN = os.environ.get("DISCORD_BOT_TOKEN")

@client.event
async def on_ready():
    print(f"Logged in as {client.user} (ID: {client.user.id})")
    print("RoDAAI Discord Bot watcher is active and listening for new members...")

@client.event
async def on_member_join(member):
    print(f"New member joined: {member.name} (ID: {member.id})")
    
    payload = {
        "user": {
            "username": member.name,
            "id": str(member.id),
            "discriminator": getattr(member, "discriminator", "0")
        },
        "guild_id": str(member.guild.id)
    }

    if not N8N_WEBHOOK_URL:
        print("Error: N8N_WEBHOOK_URL environment variable is missing!")
        return

    async with aiohttp.ClientSession() as session:
        try:
            async with session.post(N8N_WEBHOOK_URL, json=payload) as response:
                if response.status == 200:
                    print(f"Successfully triggered n8n workflow for {member.name}")
                else:
                    print(f"Failed to trigger n8n. Status: {response.status}")
        except Exception as e:
            print(f"Exception while calling n8n webhook: {e}")

# Simple HTTP health-check server to satisfy Render's Web Service port binding requirement
async def health_check(request):
    return web.Response(text="RoDAAI Bot Service is running!")

async def main():
    if not DISCORD_BOT_TOKEN:
        print("Error: DISCORD_BOT_TOKEN environment variable is missing!")
        return

    # Start the aiohttp web server for Render health checks
    app = web.Application()
    app.router.add_get("/", health_check)
    runner = web.AppRunner(app)
    await runner.setup()
    site = web.TCPSite(runner, "0.0.0.0", PORT)
    await site.start()
    print(f"Health check web server running on port {PORT}")

    # Start the Discord client
    async with client:
        await client.start(DISCORD_BOT_TOKEN)

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("Bot stopped.")
