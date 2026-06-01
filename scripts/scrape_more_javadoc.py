"""Batch scrape additional Paper API javadoc classes."""
import json
import re
import time
import urllib.request
import urllib.error
from pathlib import Path

BASE_URL = "https://jd.papermc.io/paper/1.21.4/"
OUTPUT_DIR = Path(__file__).parent.parent / "knowledge" / "raw" / "paper_javadoc"

# Additional classes to fetch - Paper-specific, Events, and commonly used Bukkit classes
ADDITIONAL_CLASSES = [
    # Paper-specific APIs
    "io.papermc.paper.event.block.BlockBreakBlockEvent",
    "io.papermc.paper.event.player.PlayerFlowerPotManipulateEvent",
    "io.papermc.paper.event.entity.EntityMoveEvent",
    "io.papermc.paper.event.player.PlayerTradeEvent",
    "io.papermc.paper.event.player.PlayerLoomPatternSelectEvent",
    "io.papermc.paper.event.block.BlockDestroyEvent",
    "io.papermc.paper.event.player.AsyncChatEvent",
    "io.papermc.paper.adventure.Adventure",
    "io.papermc.paper.entity.TeleportFlag",
    "io.papermc.paper.event.world.WorldLoadEvent",
    "io.papermc.paper.event.server.ServerTickEvent",
    "io.papermc.paper.event.player.PlayerItemFrameChangeEvent",
    "io.papermc.paper.event.block.BlockPreDispenseEvent",
    # Key Bukkit Events
    "org.bukkit.event.player.PlayerRespawnEvent",
    "org.bukkit.event.player.PlayerGameModeChangeEvent",
    "org.bukkit.event.player.PlayerTeleportEvent",
    "org.bukkit.event.player.PlayerDropItemEvent",
    "org.bukkit.event.player.PlayerPickupItemEvent",
    "org.bukkit.event.player.PlayerToggleSneakEvent",
    "org.bukkit.event.player.PlayerToggleSprintEvent",
    "org.bukkit.event.player.PlayerToggleFlightEvent",
    "org.bukkit.event.player.PlayerBedEnterEvent",
    "org.bukkit.event.player.PlayerBedLeaveEvent",
    "org.bukkit.event.player.PlayerChangedWorldEvent",
    "org.bukkit.event.player.PlayerItemConsumeEvent",
    "org.bukkit.event.player.PlayerItemDamageEvent",
    "org.bukkit.event.player.PlayerItemBreakEvent",
    "org.bukkit.event.player.PlayerFishEvent",
    "org.bukkit.event.player.PlayerExpChangeEvent",
    "org.bukkit.event.player.PlayerLevelChangeEvent",
    "org.bukkit.event.player.PlayerArmorStandManipulateEvent",
    "org.bukkit.event.player.PlayerEditBookEvent",
    "org.bukkit.event.player.PlayerBucketEmptyEvent",
    "org.bukkit.event.player.PlayerBucketFillEvent",
    "org.bukkit.event.player.PlayerShearEntityEvent",
    "org.bukkit.event.player.PlayerStatisticIncrementEvent",
    "org.bukkit.event.player.PlayerSwapHandItemsEvent",
    "org.bukkit.event.entity.EntityTargetEvent",
    "org.bukkit.event.entity.EntityShootBowEvent",
    "org.bukkit.event.entity.EntityTameEvent",
    "org.bukkit.event.entity.EntityBreedEvent",
    "org.bukkit.event.entity.EntityExplodeEvent",
    "org.bukkit.event.entity.EntityPortalEvent",
    "org.bukkit.event.entity.EntityRegainHealthEvent",
    "org.bukkit.event.entity.EntityCombustEvent",
    "org.bukkit.event.entity.EntityAirChangeEvent",
    "org.bukkit.event.entity.ProjectileHitEvent",
    "org.bukkit.event.entity.ProjectileLaunchEvent",
    "org.bukkit.event.entity.ExplosionPrimeEvent",
    "org.bukkit.event.entity.CreatureSpawnEvent",
    "org.bukkit.event.entity.FoodLevelChangeEvent",
    "org.bukkit.event.entity.AreaEffectCloudApplyEvent",
    "org.bukkit.event.entity.EntityMountEvent",
    "org.bukkit.event.entity.EntityDismountEvent",
    "org.bukkit.event.entity.EntityChangeBlockEvent",
    "org.bukkit.event.entity.EntityPlaceEvent",
    "org.bukkit.event.block.BlockGrowEvent",
    "org.bukkit.event.block.BlockSpreadEvent",
    "org.bukkit.event.block.BlockFormEvent",
    "org.bukkit.event.block.BlockFadeEvent",
    "org.bukkit.event.block.BlockDamageEvent",
    "org.bukkit.event.block.BlockIgniteEvent",
    "org.bukkit.event.block.BlockBurnEvent",
    "org.bukkit.event.block.BlockExplodeEvent",
    "org.bukkit.event.block.BlockPistonExtendEvent",
    "org.bukkit.event.block.BlockPistonRetractEvent",
    "org.bukkit.event.block.BlockRedstoneEvent",
    "org.bukkit.event.block.BlockMultiPlaceEvent",
    "org.bukkit.event.block.BlockCanBuildEvent",
    "org.bukkit.event.block.SignChangeEvent",
    "org.bukkit.event.block.LeavesDecayEvent",
    "org.bukkit.event.inventory.InventoryClickEvent",
    "org.bukkit.event.inventory.InventoryOpenEvent",
    "org.bukkit.event.inventory.InventoryCloseEvent",
    "org.bukkit.event.inventory.InventoryDragEvent",
    "org.bukkit.event.inventory.InventoryMoveItemEvent",
    "org.bukkit.event.inventory.InventoryPickupItemEvent",
    "org.bukkit.event.inventory.CraftItemEvent",
    "org.bukkit.event.inventory.FurnaceBurnEvent",
    "org.bukkit.event.inventory.FurnaceSmeltEvent",
    "org.bukkit.event.inventory.PrepareItemCraftEvent",
    "org.bukkit.event.inventory.PrepareAnvilEvent",
    "org.bukkit.event.inventory.BrewEvent",
    "org.bukkit.event.inventory.HopperItemMoveEvent",
    "org.bukkit.event.world.ChunkLoadEvent",
    "org.bukkit.event.world.ChunkUnloadEvent",
    "org.bukkit.event.world.ChunkPopulateEvent",
    "org.bukkit.event.world.StructureGrowEvent",
    "org.bukkit.event.world.PortalCreateEvent",
    "org.bukkit.event.world.SpawnChangeEvent",
    "org.bukkit.event.world.WorldSaveEvent",
    "org.bukkit.event.world.WorldInitEvent",
    "org.bukkit.event.server.ServerListPingEvent",
    "org.bukkit.event.server.MapInitializeEvent",
    "org.bukkit.event.server.RemoteServerCommandEvent",
    "org.bukkit.event.server.ServerCommandEvent",
    "org.bukkit.event.server.PluginEnableEvent",
    "org.bukkit.event.server.PluginDisableEvent",
    "org.bukkit.event.vehicle.VehicleCreateEvent",
    "org.bukkit.event.vehicle.VehicleDestroyEvent",
    "org.bukkit.event.vehicle.VehicleEnterEvent",
    "org.bukkit.event.vehicle.VehicleExitEvent",
    "org.bukkit.event.vehicle.VehicleDamageEvent",
    "org.bukkit.event.vehicle.VehicleMoveEvent",
    "org.bukkit.event.vehicle.VehicleUpdateEvent",
    "org.bukkit.event.hanging.HangingBreakEvent",
    "org.bukkit.event.hanging.HangingPlaceEvent",
    "org.bukkit.event.weather.LightningStrikeEvent",
    "org.bukkit.event.weather.ThunderChangeEvent",
    "org.bukkit.event.weather.WeatherChangeEvent",
    # Common Bukkit utility classes
    "org.bukkit.util.Vector",
    "org.bukkit.util.BoundingBox",
    "org.bukkit.util.BlockIterator",
    "org.bukkit.util.io.BukkitObjectOutputStream",
    "org.bukkit.block.Block",
    "org.bukkit.block.BlockState",
    "org.bukkit.block.Chest",
    "org.bukkit.block.Sign",
    "org.bukkit.block.data.BlockData",
    "org.bukkit.enchantments.Enchantment",
    "org.bukkit.entity.EntityType",
    "org.bukkit.entity.Player",
    "org.bukkit.entity.Mob",
    "org.bukkit.entity.Projectile",
    "org.bukkit.entity.Arrow",
    "org.bukkit.entity.Item",
    "org.bukkit.entity.Villager",
    "org.bukkit.entity.Zombie",
    "org.bukkit.entity.Skeleton",
    "org.bukkit.entity.Creeper",
    "org.bukkit.entity.Spider",
    "org.bukkit.entity.ArmorStand",
    "org.bukkit.entity.FallingBlock",
    "org.bukkit.entity.ThrownPotion",
    "org.bukkit.entity.Firework",
    "org.bukkit.entity.Boat",
    "org.bukkit.entity.Minecart",
    "org.bukkit.entity.Animals",
    "org.bukkit.entity.Monster",
    "org.bukkit.entity.Monster",
    "org.bukkit.inventory.Recipe",
    "org.bukkit.inventory.ShapedRecipe",
    "org.bukkit.inventory.ShapelessRecipe",
    "org.bukkit.inventory.FurnaceRecipe",
    "org.bukkit.inventory.MerchantRecipe",
    "org.bukkit.inventory.InventoryView",
    "org.bukkit.inventory.InventoryHolder",
    "org.bukkit.map.MapView",
    "org.bukkit.permissions.Permission",
    "org.bukkit.permissions.PermissionDefault",
    "org.bukkit.plugin.java.JavaPlugin",
    "org.bukkit.scheduler.BukkitRunnable",
    "org.bukkit.scheduler.BukkitTask",
    "org.bukkit.scoreboard.Objective",
    "org.bukkit.scoreboard.Team",
    "org.bukkit.scoreboard.DisplaySlot",
    "org.bukkit.GameMode",
    "org.bukkit.Difficulty",
    "org.bukkit.GameRule",
    "org.bukkit.Statistic",
    "org.bukkit.Achievement",
    "org.bukkit.BanList",
    "org.bukkit.ChatColor",
    "org.bukkit.Color",
    "org.bukkit.FireworkEffect",
    "org.bukkit.Instrument",
    "org.bukkit.Note",
    "org.bukkit.OfflinePlayer",
    "org.bukkit.Particle",
    "org.bukkit.Rotation",
    "org.bukkit.SoundCategory",
    "org.bukkit.Tag",
    "org.bukkit.WorldType",
    "org.bukkit.WorldBorder",
    "org.bukkit.attribute.Attribute",
    "org.bukkit.attribute.AttributeModifier",
    "org.bukkit.entity.Damageable",
    "org.bukkit.event.Cancellable",
    "org.bukkit.event.EventPriority",
    "org.bukkit.event.HandlerList",
    "org.bukkit.inventory.EquipmentSlot",
    "org.bukkit.inventory.ItemFlag",
    "org.bukkit.inventory.meta.BookMeta",
    "org.bukkit.inventory.meta.SkullMeta",
    "org.bukkit.inventory.meta.EnchantmentStorageMeta",
    "org.bukkit.inventory.meta.FireworkMeta",
    "org.bukkit.inventory.meta.LeatherArmorMeta",
    "org.bukkit.inventory.meta.PotionMeta",
    "org.bukkit.inventory.meta.MapMeta",
    "org.bukkit.inventory.meta.CompassMeta",
    "org.bukkit.inventory.meta.CrossbowMeta",
    "org.bukkit.inventory.meta.BannerMeta",
    "org.bukkit.inventory.meta.ItemMeta",
    "org.bukkit.loot.LootContext",
    "org.bukkit.loot.LootTable",
    "org.bukkit.metadata.MetadataValue",
    "org.bukkit.persistence.PersistentDataContainer",
    "org.bukkit.persistence.PersistentDataType",
    "org.bukkit.potion.PotionEffectType",
    "org.bukkit.potion.PotionData",
    "org.bukkit.potion.PotionType",
    "org.bukkit.projectiles.ProjectileSource",
    "org.bukkit.raid.Raid",
    "org.bukkit.util.EulerAngle",
    "org.bukkit.util.NumberConversions",
    "org.bukkit.Warning",
    "org.bukkit.help.HelpTopic",
    "org.bukkit.conversations.Conversation",
    "org.bukkit.scheduler.BukkitWorker",
    "org.bukkit.plugin.PluginManager",
    "org.bukkit.plugin.PluginLoader",
    "org.bukkit.plugin.EventExecutor",
    # Paper-specific additions
    "io.papermc.paper.event.block.BlockBreakBlockEvent",
    "io.papermc.paper.event.player.AsyncChatEvent",
    "io.papermc.paper.event.server.WhitelistToggleEvent",
    "io.papermc.paper.event.server.ServerResourcesReloadedEvent",
    "io.papermc.paper.event.player.PlayerElytraBoostEvent",
    "io.papermc.paper.event.entity.EntityInsideBlockEvent",
    "io.papermc.paper.event.entity.EntityKnockbackByEntityEvent",
    "io.papermc.paper.event.entity.WitherSkullTransformEvent",
    "io.papermc.paper.datapack.DatapackManager",
    "io.papermc.paper.registry.RegistryAccess",
    "io.papermc.paper.registry.RegistryKey",
    "io.papermc.paper.command.PaperCommands",
    "io.papermc.paper.world.WorldView",
]

def scrape_class(full_class_name: str) -> dict | None:
    """Scrape a single class javadoc page."""
    url_path = full_class_name.replace('.', '/') + '.html'
    url = BASE_URL + url_path
    
    req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
    
    try:
        with urllib.request.urlopen(req, timeout=15) as resp:
            html = resp.read().decode('utf-8', errors='replace')
    except urllib.error.HTTPError as e:
        if e.code == 404:
            return None
        return None
    except Exception:
        return None
    
    # Extract description (first paragraph after class name)
    simple_name = full_class_name.split('.')[-1]
    
    # Try to extract from the class description area
    desc_match = re.search(
        r'<div class="block"[^>]*>(.*?)</div>',
        html, re.DOTALL
    )
    description = ""
    if desc_match:
        description = re.sub(r'<[^>]+>', ' ', desc_match.group(1)).strip()
        description = re.sub(r'\s+', ' ', description)
        # Limit description length
        if len(description) > 2000:
            description = description[:2000] + "..."
    
    # Extract method signatures
    method_sigs = re.findall(
        r'<a href="[^"]*" class="member-name-link"[^>]*>(\w+)</a>\s*<span class="parameters">\((.*?)\)</span>',
        html, re.DOTALL
    )
    
    methods = []
    for name, params in method_sigs:
        params_clean = re.sub(r'<[^>]+>', '', params).strip()
        methods.append(f"{name}({params_clean})")
    
    # Get full text (stripped of HTML)
    full_text = re.sub(r'<script[^>]*>.*?</script>', '', html, flags=re.DOTALL)
    full_text = re.sub(r'<style[^>]*>.*?</style>', '', full_text, flags=re.DOTALL)
    full_text = re.sub(r'<[^>]+>', ' ', full_text)
    full_text = re.sub(r'\s+', ' ', full_text).strip()
    # Limit full text
    if len(full_text) > 30000:
        full_text = full_text[:30000]
    
    return {
        'class_name': simple_name,
        'full_class': full_class_name,
        'url': url,
        'description': description,
        'methods': methods,
        'method_count': len(methods),
        'full_text': full_text,
    }


def main():
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    
    success = 0
    failed = 0
    skipped = 0
    
    # Deduplicate
    seen = set()
    unique_classes = []
    for c in ADDITIONAL_CLASSES:
        simple = c.split('.')[-1]
        if simple not in seen:
            seen.add(simple)
            unique_classes.append(c)
    
    print(f"Fetching {len(unique_classes)} javadoc classes...")
    
    for i, cls in enumerate(unique_classes):
        simple_name = cls.split('.')[-1]
        output_file = OUTPUT_DIR / f"{simple_name}.json"
        
        if output_file.exists():
            skipped += 1
            continue
        
        data = scrape_class(cls)
        
        if data:
            with open(output_file, 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
            success += 1
            if (i + 1) % 20 == 0:
                print(f"  Progress: {i+1}/{len(unique_classes)} (success: {success}, failed: {failed}, skipped: {skipped})")
        else:
            failed += 1
        
        time.sleep(0.3)  # Be respectful
    
    print(f"\nDone! Success: {success}, Failed: {failed}, Skipped: {skipped}")


if __name__ == '__main__':
    main()
