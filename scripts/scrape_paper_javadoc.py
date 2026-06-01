"""Scrape Paper API Javadoc for key Bukkit/Spigot classes."""
import json
import os
import re
import sys
import time

try:
    import requests
    from bs4 import BeautifulSoup
except ImportError:
    os.system(f"{sys.executable} -m pip install requests beautifulsoup4 -q")
    import requests
    from bs4 import BeautifulSoup

OUTPUT_DIR = os.path.join(os.path.dirname(__file__), '..', 'knowledge', 'raw', 'paper_javadoc')
BASE_URL = "https://jd.papermc.io/paper/1.21.4"

HEADERS = {'User-Agent': 'CyanBukkit-MCP/0.1 Knowledge indexer'}

# Most important Bukkit/Spigot API classes for plugin developers
KEY_CLASSES = [
    # Core
    ("org/bukkit/Bukkit.html", "Bukkit"),
    ("org/bukkit/Server.html", "Server"),
    ("org/bukkit/World.html", "World"),
    ("org/bukkit/entity/Player.html", "Player"),
    ("org/bukkit/entity/Entity.html", "Entity"),
    ("org/bukkit/entity/LivingEntity.html", "LivingEntity"),
    
    # Events
    ("org/bukkit/event/Event.html", "Event"),
    ("org/bukkit/event/EventHandler.html", "EventHandler"),
    ("org/bukkit/event/Listener.html", "Listener"),
    ("org/bukkit/event/player/PlayerJoinEvent.html", "PlayerJoinEvent"),
    ("org/bukkit/event/player/PlayerQuitEvent.html", "PlayerQuitEvent"),
    ("org/bukkit/event/player/PlayerMoveEvent.html", "PlayerMoveEvent"),
    ("org/bukkit/event/player/AsyncPlayerChatEvent.html", "AsyncPlayerChatEvent"),
    ("org/bukkit/event/player/PlayerInteractEvent.html", "PlayerInteractEvent"),
    ("org/bukkit/event/block/BlockBreakEvent.html", "BlockBreakEvent"),
    ("org/bukkit/event/block/BlockPlaceEvent.html", "BlockPlaceEvent"),
    ("org/bukkit/event/entity/EntityDamageEvent.html", "EntityDamageEvent"),
    ("org/bukkit/event/entity/EntityDeathEvent.html", "EntityDeathEvent"),
    ("org/bukkit/event/entity/PlayerDeathEvent.html", "PlayerDeathEvent"),
    ("org/bukkit/event/server/PluginEnableEvent.html", "PluginEnableEvent"),
    
    # Plugin system
    ("org/bukkit/plugin/Plugin.html", "Plugin"),
    ("org/bukkit/plugin/JavaPlugin.html", "JavaPlugin"),
    ("org/bukkit/plugin/PluginManager.html", "PluginManager"),
    
    # Scheduler
    ("org/bukkit/scheduler/BukkitRunnable.html", "BukkitRunnable"),
    ("org/bukkit/scheduler/BukkitScheduler.html", "BukkitScheduler"),
    
    # Commands
    ("org/bukkit/command/Command.html", "Command"),
    ("org/bukkit/command/CommandSender.html", "CommandSender"),
    ("org/bukkit/command/CommandExecutor.html", "CommandExecutor"),
    ("org/bukkit/command/TabCompleter.html", "TabCompleter"),
    ("org/bukkit/command/TabExecutor.html", "TabExecutor"),
    
    # Inventory
    ("org/bukkit/inventory/Inventory.html", "Inventory"),
    ("org/bukkit/inventory/ItemStack.html", "ItemStack"),
    ("org/bukkit/inventory/InventoryHolder.html", "InventoryHolder"),
    ("org/bukkit/inventory/PlayerInventory.html", "PlayerInventory"),
    
    # Configuration
    ("org/bukkit/configuration/file/YamlConfiguration.html", "YamlConfiguration"),
    ("org/bukkit/configuration/file/FileConfiguration.html", "FileConfiguration"),
    ("org/bukkit/configuration/ConfigurationSection.html", "ConfigurationSection"),
    
    # Material & Items
    ("org/bukkit/Material.html", "Material"),
    ("org/bukkit/inventory/meta/ItemMeta.html", "ItemMeta"),
    
    # Location/Chunk
    ("org/bukkit/Location.html", "Location"),
    ("org/bukkit/Chunk.html", "Chunk"),
    ("org/bukkit/Block.html", "Block"),
    
    # Scoreboard
    ("org/bukkit/scoreboard/Scoreboard.html", "Scoreboard"),
    ("org/bukkit/scoreboard/ScoreboardManager.html", "ScoreboardManager"),
    
    # Boss bar
    ("org/bukkit/boss/BossBar.html", "BossBar"),
    
    # Persistence
    ("org/bukkit/persistence/PersistentDataHolder.html", "PersistentDataHolder"),
    ("org/bukkit/persistence/PersistentDataContainer.html", "PersistentDataContainer"),
    
    # Particle & Sound
    ("org/bukkit/Particle.html", "Particle"),
    ("org/bukkit/Sound.html", "Sound"),
    
    # Potion
    ("org/bukkit/potion/PotionEffect.html", "PotionEffect"),
    ("org/bukkit/potion/PotionEffectType.html", "PotionEffectType"),
]


def extract_javadoc(html: str, url: str, class_name: str) -> dict:
    """Extract javadoc content from Paper API page."""
    soup = BeautifulSoup(html, 'html.parser')
    
    # Get class description
    description = ''
    desc_el = soup.select_one('.description, .block, #class-description')
    if desc_el:
        description = desc_el.get_text(separator='\n', strip=True)
    
    # Get method signatures
    methods = []
    method_table = soup.select_one('.memberSummary-table, table.memberSummary')
    if method_table:
        for row in method_table.select('tr'):
            cells = row.select('td')
            if len(cells) >= 2:
                method_sig = cells[-1].get_text(strip=True)
                if method_sig and '(' in method_sig:
                    methods.append(method_sig)
    
    # Alternative: get all method summaries from the methods summary section
    if not methods:
        for el in soup.select('.memberSignature, .method-summary-table .col-last'):
            text = el.get_text(strip=True)
            if text and ('(' in text or 'void' in text or class_name in text):
                methods.append(text)
    
    # Get nested classes
    nested = []
    for el in soup.select('.nested-class-summary .col-first a, .nested-class-summary td a'):
        text = el.get_text(strip=True)
        if text:
            nested.append(text)
    
    # Get all text from main content
    content_el = soup.select_one('.contentContainer, #class-content, main')
    if content_el:
        for tag in content_el.find_all(['script', 'style', 'nav']):
            tag.decompose()
        full_text = content_el.get_text(separator='\n', strip=True)
    else:
        full_text = ''
    
    return {
        'class_name': class_name,
        'url': url,
        'description': description[:2000],
        'methods': methods[:50],
        'nested_classes': nested[:20],
        'full_text': full_text[:5000],
        'method_count': len(methods),
    }


def main():
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    
    # Build index
    index = {}
    success = 0
    failed = []
    
    for i, (path, class_name) in enumerate(KEY_CLASSES):
        url = f"{BASE_URL}/{path}"
        print(f"[{i+1}/{len(KEY_CLASSES)}] Scraping: {class_name}...")
        
        try:
            resp = requests.get(url, headers=HEADERS, timeout=15)
            resp.raise_for_status()
            
            result = extract_javadoc(resp.text, url, class_name)
            
            # Save individual file
            out_path = os.path.join(OUTPUT_DIR, f"{class_name}.json")
            with open(out_path, 'w', encoding='utf-8') as f:
                json.dump(result, f, ensure_ascii=False, indent=2)
            
            index[class_name] = {
                'url': url,
                'method_count': result['method_count'],
                'has_description': bool(result['description']),
                'file': f"{class_name}.json"
            }
            
            print(f"  OK: {result['method_count']} methods, desc={len(result['description'])} chars")
            success += 1
            time.sleep(0.8)
            
        except Exception as e:
            print(f"  ERROR: {e}")
            failed.append((class_name, str(e)))
            time.sleep(1)
    
    # Save index
    index_path = os.path.join(OUTPUT_DIR, '_index.json')
    with open(index_path, 'w', encoding='utf-8') as f:
        json.dump(index, f, ensure_ascii=False, indent=2)
    
    print(f"\nDone! Success: {success}, Failed: {len(failed)}")
    if failed:
        for cn, reason in failed:
            print(f"  {cn}: {reason}")


if __name__ == '__main__':
    main()
