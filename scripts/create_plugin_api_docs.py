"""Create plugin API documentation files."""
import json
import os

OUTPUT = os.path.join(os.path.dirname(__file__), '..', 'knowledge', 'raw', 'plugin_apis')
os.makedirs(OUTPUT, exist_ok=True)

docs = {
    'placeholderapi': {
        'title': 'PlaceholderAPI',
        'url': 'https://github.com/PlaceholderAPI/PlaceholderAPI',
        'content': """PlaceholderAPI - Spigot plugin for placeholder management

## Overview
PlaceholderAPI is a plugin for Spigot servers that allows server owners to display information from various plugins with a uniform format. Over 240+ expansions available.

## Hooking into PlaceholderAPI

### Maven Dependency
<dependency>
    <groupId>me.clip</groupId>
    <artifactId>placeholderapi</artifactId>
    <version>2.11.6</version>
    <scope>provided</scope>
</dependency>

### Basic Hook Example
public class MyPlugin extends JavaPlugin {
    @Override
    public void onEnable() {
        if (Bukkit.getPluginManager().getPlugin("PlaceholderAPI") != null) {
            new MyPlaceholders(this).register();
        }
    }
}

### Creating an Expansion (PlaceholderExpansion)
public class MyPlaceholders extends PlaceholderExpansion {
    private final MyPlugin plugin;
    public MyPlaceholders(MyPlugin plugin) { this.plugin = plugin; }
    @Override public String getIdentifier() { return "myplugin"; }
    @Override public String getAuthor() { return "author"; }
    @Override public String getVersion() { return "1.0"; }
    @Override
    public String onRequest(OfflinePlayer player, String params) {
        if (params.equalsIgnoreCase("name")) return player != null ? player.getName() : null;
        if (params.equalsIgnoreCase("money")) return player != null ? String.valueOf(getBalance(player)) : "0";
        return null;
    }
}

### Using Placeholders in Strings
String result = PlaceholderAPI.setPlaceholders(player, "%myplugin_name% has %myplugin_money% coins");

### Key Classes
- me.clip.placeholderapi.PlaceholderAPI
- me.clip.placeholderapi.PlaceholderHook
- me.clip.placeholderapi.expansion.PlaceholderExpansion
- me.clip.placeholderapi.expansion.Relational
- me.clip.placeholderapi.events.ExpansionRegisterEvent
"""
    },
    'protocollib': {
        'title': 'ProtocolLib',
        'url': 'https://github.com/dmulloy2/ProtocolLib',
        'content': """ProtocolLib - Minecraft packet manipulation library for Spigot

## Overview
ProtocolLib provides read/write access to Minecraft packets, allowing plugins to intercept and modify network traffic without NMS code.

## Maven Dependency
<dependency>
    <groupId>com.comphenix.protocol</groupId>
    <artifactId>ProtocolLib</artifactId>
    <version>5.3.0</version>
</dependency>

## Basic Usage

### Listening for Packets
ProtocolManager manager = ProtocolLibrary.getProtocolManager();
manager.addPacketListener(new PacketAdapter(this, ListenerPriority.NORMAL, PacketType.Play.Client.CHAT) {
    @Override
    public void onPacketReceiving(PacketEvent event) {
        PacketContainer packet = event.getPacket();
        String message = packet.getStrings().read(0);
    }
});

### Sending Packets
PacketContainer packet = manager.createPacket(PacketType.Play.Server.CHAT);
packet.getChatComponents().write(0, Component.text("Hello!"));
manager.sendServerPacket(player, packet);

### Key Classes
- com.comphenix.protocol.ProtocolLibrary
- com.comphenix.protocol.ProtocolManager
- com.comphenix.protocol.events.PacketAdapter
- com.comphenix.protocol.events.PacketContainer
- com.comphenix.protocol.events.PacketEvent
- com.comphenix.protocol.events.ListenerPriority
- com.comphenix.protocol.PacketType
- com.comphenix.protocol.wrappers.WrappedChatComponent
- com.comphenix.protocol.wrappers.EnumWrappers
- com.comphenix.protocol.wrappers.WrappedGameProfile

### PacketType Categories
- PacketType.Play.Client - Client to server
- PacketType.Play.Server - Server to client
- PacketType.Login - Login phase
- PacketType.Handshake - Handshake
"""
    },
    'vault': {
        'title': 'Vault API',
        'url': 'https://github.com/MilkBowl/VaultAPI',
        'content': """VaultAPI - Economy/Permission/Chat API abstraction for Bukkit

## Overview
Vault provides a standardized API for Economy, Permission, and Chat operations, allowing plugins to work with any backend.

## Maven Dependency
<dependency>
    <groupId>com.github.MilkBowl</groupId>
    <artifactId>VaultAPI</artifactId>
    <version>1.7</version>
    <scope>provided</scope>
</dependency>

### plugin.yml: depend: [Vault]

## Economy API
RegisteredServiceProvider<Economy> rsp = getServer().getServicesManager().getRegistration(Economy.class);
Economy econ = rsp.getProvider();
econ.getBalance(player);
econ.depositPlayer(player, 100.0);
econ.withdrawPlayer(player, 50.0);
econ.has(player, 25.0);

## Permission API
RegisteredServiceProvider<Permission> rsp = getServer().getServicesManager().getRegistration(Permission.class);
Permission perms = rsp.getProvider();
perms.has(player, "permission.node");
perms.playerAdd(player, "permission.node");
perms.playerRemove(player, "permission.node");
perms.playerInGroup(player, "group_name");
perms.playerAddGroup(player, "group_name");

## Chat API
RegisteredServiceProvider<Chat> rsp = getServer().getServicesManager().getRegistration(Chat.class);
Chat chat = rsp.getProvider();
chat.getPlayerPrefix(player);
chat.getPlayerSuffix(player);
chat.setPlayerPrefix(player, "[Admin]");
chat.getPrimaryGroup(player);

## Key Classes
- net.milkbowl.vault.economy.Economy
- net.milkbowl.vault.economy.EconomyResponse
- net.milkbowl.vault.permission.Permission
- net.milkbowl.vault.chat.Chat
- net.milkbowl.vault.item.ItemInfo
"""
    }
}

for name, data in docs.items():
    out_path = os.path.join(OUTPUT, f'{name}.json')
    with open(out_path, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    print(f"Created: {name}.json ({len(data['content'])} chars)")

print("Done!")
