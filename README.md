# P&P Ultimate Edition Dicebot

![alt text](https://img.shields.io/badge/discord.py-v2.3.2-blue?logo=discord&logoColor=white)

![alt text](https://img.shields.io/badge/python-3.10+-blue.svg?logo=python&logoColor=white)

![alt text](https://img.shields.io/badge/license-MIT-green.svg)

A Discord bot for rolling dice in the Prowlers & Paragons: Ultimate Edition tabletop roleplaying game.
This bot is designed to handle the specific dice mechanics of P&PUE, including its unique success system and exploding dice. It provides a clean, interactive, and easy-to-use interface right within your Discord server, letting you focus on the game.

# Key Features
- P&P Success System: Automatically calculates successes based on the game's rules (1 success for a 2 or 4, 2 successes for a 6).
- Interactive Buttons: No need to type extra commands. Use the Re-roll and Explode 6s buttons to manage your rolls.
- Persistent Explosion State: Once you explode a roll, the bot remembers! All subsequent re-rolls will automatically explode any 6s, just like in the game.
- Clear Embeds: Roll results are displayed in a clean, color-coded embed that shows the dice, the outcome, and any explosions.
- Roll History: A running log in the message footer tracks the results of your initial roll and subsequent re-rolls.
- Slash Commands: Modern and intuitive to use with Discord's built-in command interface.

# Commands
The bot's functionality is centered around a single, powerful command -
/roll

Parameters:

dice_number (Required): The number of six-sided dice to roll (1-100).

description (Optional): A short description for your roll (e.g. "Blast Attack," "Armour").

Interactive Buttons:

After your initial roll, two buttons will appear on the message:

Re-roll: Discards the entire previous result and rolls a completely new set of dice. You can re-roll up to 5 times.

Explode 6s: For each 6 in your current result, this rolls an additional die and adds its successes. Crucially, using this button activates "explosion memory" for all future re-rolls in this sequence. The button becomes disabled for the current set of dice after being used once.

# Installation
You can either add the public instance of the bot to your server or host it yourself.

Add to Your Server (Recommended)

The easiest way to get started is to invite the bot to your Discord server using this invite link: https://discord.com/oauth2/authorize?client_id=971458596967690360.

Self-Hosting (For Developers)

If you prefer to run and manage the bot yourself, the code can be found at https://github.com/elemmir/dicebot.
