import os
import discord
import aiohttp
import threading
from flask import Flask, render_template

token = os.environ.get('bot_token')  # Ensure 'bot_token' is set as an environment variable

bot = discord.Bot()
app = Flask(__name__)

logs_webhook_url = os.environ.get('webhook')  # Replace YOUR_WEBHOOK_URL with the actual URL of your webhook

@app.route('/')
def index():
		return render_template('index.html')

@bot.event
async def on_ready():
		print(f"We have logged in as {bot.user}")

@bot.slash_command()
async def hello(ctx):
		await ctx.respond("Hello!")

@bot.slash_command(name="setup")
async def setup(ctx):
		# Check if the user has the required permissions (e.g., manage_webhooks)
		if not ctx.author.guild_permissions.manage_webhooks:
				await ctx.respond("You don't have the required permissions to use this command.", ephemeral=True)
				return

		# Create a list to store the created webhooks
		webhooks_info = []

		# Create new categories and channels with webhooks
		dashx_category = await ctx.guild.create_category("Dashx - Webhooks")
		channels = ["visit", "non-verified-nbc", "non-verified-premium", "verified-nbc", "verified-premium", "success", "failed"]
		for channel_name in channels:
				new_channel = await dashx_category.create_text_channel(channel_name, topic="This channel was created with a small font.")
				webhook = await new_channel.create_webhook(name="My Webhook")
				webhooks_info.append((channel_name, webhook.url))

		# Send the list of webhooks and channels with webhooks created
		embed = discord.Embed(
				title="Setup was Successful",
				description="New Webhooks and Channels created:",
				color=discord.Color.green()
		)
		for channel_name, webhook_url in webhooks_info:
				embed.add_field(name=channel_name, value=f"Webhook: {webhook_url}", inline=False)

		# Send the embed to the webhook channel
		webhook_channel = await ctx.guild.create_text_channel("webhooks")
		await webhook_channel.send(embed=embed)

		# Embed for logs webhook
		async with aiohttp.ClientSession() as session:
				async with session.post(logs_webhook_url, json={
						"embeds": [{
								"title": "Setup was Successful",
								"description": f"New Line:\nUser: {ctx.author.mention}\nMessage: Thank you for using setup bot",
								"color": discord.Color.green().value
						}]
				}):
						pass

# Define a function to run the bot
def run_bot():
		bot.run(token)

# Start the bot in a separate thread
bot_thread = threading.Thread(target=run_bot)
bot_thread.start()

# Start the Flask app
if __name__ == '__main__':
		app.run(host='0.0.0.0', port=8080)
