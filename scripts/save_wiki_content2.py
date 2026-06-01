#!/usr/bin/env python3
"""Save additional scraped wiki pages."""
import json
import os

CONTENT_DIR = os.path.join(os.path.dirname(__file__), '..', 'knowledge', 'raw', 'spigotmc_wiki', 'pages')
os.makedirs(CONTENT_DIR, exist_ok=True)

scraped_pages = {
    'plugin-snippets': {
        'title': 'Plugin Snippets',
        'url': 'https://www.spigotmc.org/wiki/plugin-snippets/',
        'content': """Plugin Snippets

User-contributed code examples for simple plugins.

Available snippets:
- Asynchronously working with a database
- Auto-Selling Items
- Basic Chat Muting
- Bypassing Player Slot Limits
- Colored Particles
- Connecting to databases - MySQL
- Creating a GUI Inventory
- Creating a Simple Command
- Creating an Anti-Swear Listener
- Creating Join Messages
- Custom Item Models in 1.9 and Up
- Enderbow: An easy first plugin
- Feature/Command Cooldowns
- Flat File Generic Save/Load
- Hook Into Vault
- How to make custom rank system
- Interactive Books
- Making Scoreboard with Teams (No flicker)
- MongoDB Guide
- NMS on different versions (without reflection)
- Recipe Example
- Save & Load Data Files
- Signs - Editing, Getting, Using
- Sound enum and others in multiple versions
- Stop Baby Zombies Example
- Using MongoDB
- Using Redis (Jedis)
- Vector Programming for Beginners
- Working with Configuration Files
- XPBoost API"""
    },
    'buildtools': {
        'title': 'BuildTools Guide',
        'url': 'https://www.spigotmc.org/wiki/buildtools/',
        'content': """BuildTools - Simple instructions to build CraftBukkit and Spigot

About:
BuildTools is a standalone program that compiles the Spigot Server JAR. It downloads Vanilla Minecraft Server Jar, Bukkit, CraftBukkit, and Spigot. Then decompiles vanilla server, injects CraftBukkit code, applies Spigot patches.

As of Jan 15, 2024, BuildTools now comes with a GUI!

Prerequisites: Git and Java

Running BuildTools (GUI):
1. Download BuildTools for your OS
2. Double click the file
3. Select version from dropdown and press compile

Running BuildTools (CLI):
Windows: java -jar BuildTools.jar
Linux/Mac: java -jar BuildTools.jar

Command Line Flags:
--compile craftbukkit - Also compile CraftBukkit
--rev <version> - Build specific version
--disable-certificate-check - Skip certificate validation

FAQ:
- Q: Why no direct download? A: DMCA Takedown 2014, BuildTools is legal workaround
- Q: No CraftBukkit jar? A: Add --compile craftbukkit for 1.14+
- Q: Eclipse import errors? A: Use spigot-api jar or Maven/Gradle

Supported versions: 1.8 through 1.21.5+"""
    }
}

for page_id, page_data in scraped_pages.items():
    filepath = os.path.join(CONTENT_DIR, f'{page_id}.json')
    with open(filepath, 'w', encoding='utf-8') as f:
        json.dump(page_data, f, indent=2, ensure_ascii=False)
    print(f'Saved: {page_id}.json')

print(f'Total: {len(scraped_pages)} pages saved')
