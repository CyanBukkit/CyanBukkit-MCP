#!/usr/bin/env python3
"""Save SpigotMC Wiki page index and manage wiki content."""
import json
import os

WIKI_DIR = os.path.join(os.path.dirname(__file__), '..', 'knowledge', 'raw', 'spigotmc_wiki')

pages = {
    'spigot': {
        'title': 'Spigot',
        'url': 'https://www.spigotmc.org/wiki/spigot/',
        'pages': [
            {'name': 'About Spigot', 'url': 'https://www.spigotmc.org/wiki/about-spigot/'},
            {'name': 'Installation', 'url': 'https://www.spigotmc.org/wiki/spigot-installation/'},
            {'name': 'FAQ', 'url': 'https://www.spigotmc.org/wiki/faq/'},
            {'name': 'Configuration guide (spigot.yml)', 'url': 'https://www.spigotmc.org/wiki/spigot-configuration/'},
            {'name': 'Commands and Permissions', 'url': 'https://www.spigotmc.org/wiki/spigot-commands/'},
            {'name': 'Start-up parameters', 'url': 'https://www.spigotmc.org/wiki/start-up-parameters/'},
            {'name': 'Tips, Tricks & Tutorials', 'url': 'https://www.spigotmc.org/wiki/tips-tricks-tutorials/'},
            {'name': 'Changelog', 'url': 'https://www.spigotmc.org/wiki/changelog'},
            {'name': 'Maven Repository', 'url': 'https://www.spigotmc.org/wiki/spigot-maven'},
            {'name': 'Making Pull Requests / CLA', 'url': 'https://www.spigotmc.org/wiki/cla/'},
            {'name': 'Plugin Development', 'url': 'https://www.spigotmc.org/wiki/spigot-plugin-development/'},
            {'name': 'Plugin Snippets', 'url': 'https://www.spigotmc.org/wiki/plugin-snippets/'},
            {'name': 'BuildTools Guide', 'url': 'https://www.spigotmc.org/wiki/buildtools/'},
            {'name': 'Compatible Plugins By Release', 'url': 'https://www.spigotmc.org/wiki/compatible-plugins-by-release/'},
            {'name': 'Contributing to Spigot', 'url': 'https://www.spigotmc.org/wiki/guide-contributing-to-spigot/'},
            {'name': 'How to learn the Spigot API', 'url': 'https://www.spigotmc.org/wiki/how-to-learn-the-spigot-api/'},
            {'name': 'Server Icon', 'url': 'https://www.spigotmc.org/wiki/server-icon/'},
            {'name': 'Configuration (server.properties)', 'url': 'https://www.spigotmc.org/wiki/spigot-configuration-server-properties/'},
            {'name': 'Gradle', 'url': 'https://www.spigotmc.org/wiki/spigot-gradle/'},
            {'name': 'Server with version 1.8-1.16', 'url': 'https://www.spigotmc.org/wiki/spigot-server-with-version-1-8-1-16/'},
        ]
    },
    'bungeecord': {
        'title': 'BungeeCord',
        'url': 'https://www.spigotmc.org/wiki/bungeecord/',
        'pages': [
            {'name': 'About BungeeCord', 'url': 'https://www.spigotmc.org/wiki/about-bungeecord/'},
            {'name': 'Installation', 'url': 'https://www.spigotmc.org/wiki/bungeecord-installation/'},
            {'name': 'Configuration Guide (config.yml)', 'url': 'https://www.spigotmc.org/wiki/bungeecord-configuration-guide/'},
            {'name': 'Firewall Guide', 'url': 'https://www.spigotmc.org/wiki/firewall-guide'},
            {'name': 'Commands', 'url': 'https://www.spigotmc.org/wiki/bungeecord-commands/'},
            {'name': 'FAQ', 'url': 'https://www.spigotmc.org/wiki/bungeecord-faq/'},
            {'name': 'Maven', 'url': 'https://www.spigotmc.org/wiki/bungeecord-maven/'},
            {'name': 'Modules', 'url': 'https://www.spigotmc.org/wiki/bungeecord-modules/'},
            {'name': 'Plugin Development', 'url': 'https://www.spigotmc.org/wiki/bungeecord-plugin-development/'},
            {'name': 'Creating basic command functions', 'url': 'https://www.spigotmc.org/wiki/creating-basic-command-functions-in-bungeecord/'},
        ]
    },
    'general': {
        'title': 'General Pages',
        'pages': [
            {'name': 'Using the Event API', 'url': 'https://www.spigotmc.org/wiki/using-the-event-api/'},
            {'name': 'Plugin.yml', 'url': 'https://www.spigotmc.org/wiki/plugin-yml/'},
            {'name': 'Glossary', 'url': 'https://www.spigotmc.org/wiki/glossary/'},
            {'name': 'Languages', 'url': 'https://www.spigotmc.org/wiki/languages/'},
        ]
    }
}

os.makedirs(WIKI_DIR, exist_ok=True)

with open(os.path.join(WIKI_DIR, 'page_index.json'), 'w', encoding='utf-8') as f:
    json.dump(pages, f, indent=2, ensure_ascii=False)

total = sum(len(c.get('pages', [])) for c in pages.values())
print(f'Saved page_index.json with {total} pages')
