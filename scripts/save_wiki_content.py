#!/usr/bin/env python3
"""Save wiki page content to individual files."""
import os
import json

WIKI_DIR = os.path.join(os.path.dirname(__file__), '..', 'knowledge', 'raw', 'spigotmc_wiki')
CONTENT_DIR = os.path.join(WIKI_DIR, 'pages')
os.makedirs(CONTENT_DIR, exist_ok=True)

# Already scraped content (from browser sessions)
scraped_pages = {
    'spigot-plugin-development': {
        'title': 'Spigot Plugin Development',
        'url': 'https://www.spigotmc.org/wiki/spigot-plugin-development/',
        'content': """Build you Spigot plugin with Gradle Groovy
Bukkit inventory views – Raw slot IDs
Clean Code
Command Alias
Crash Course to Java
    Part 0: Sources
Creating & Maintaining a Resource
Creating a blank Spigot plugin in Eclipse
Creating a blank Spigot plugin in IntelliJ IDEA
Creating a blank Spigot plugin in NetBeans
Creating a blank Spigot plugin in VS Code
Creating a Config File
Creating a plugin with Maven using Eclipse
Creating a plugin with Maven using IntelliJ IDEA
Creating an update checker that checks for updates
Creating external Libraries
Creating offline Javadoc for the Spigot API
Creating your development workspace
Eclipse: Debug your Plugin
Extra Resources for Learning Java
Guide - How to auto-export your plugin using ant
How to learn Java programming
How to use Kotlin in your plugins
Included libraries in Spigot
IntelliJ: Debug Your Plugin
List with all item names
Mojang UUID Rate Limit
MongoDB With Morphia
MultiThreading - Completable Futures
MySQL database integration with your plugin.
Particle list 1.8.8
Plugin.yml
Premium Resource Placeholders & Identifiers
Reading and Understanding stack-traces
Send title to player - Packets
Setting up the WorldEdit API
SettingsManager instructions
Spigot NMS and Minecraft Versions - 1.10-1.15
Spigot NMS and Minecraft Versions - 1.16+
Spigot NMS and Minecraft Versions - 1.21+
Spigot Plugin.yml Annotations
Spigot/Bukkit Plugin Development
    Scheduler Programming
Testing with WatchWolf
    Auto-run integration tests
    Stress testing with WatchWolf
Using Dependency Injection
Using the Event API

Spigot Plugin Development

Using the Spigot-API

This section is dedicated to Spigot plugin developers. This guide assumes that the reader has no prior modding experience in Minecraft. Hence, the guides can/should be read in a progressive order. Experienced modders, feel free to skip ahead. Where applicable, Eclipse and IntelliJ version of each guide is shown.

Guides

Crash Course to Java
Creating a blank plugin with:
- IntelliJ IDEA and Maven
- IntelliJ IDEA and Gradle
- IntelliJ IDEA (manual API loading, not recommended)
- Eclipse (manual API loading, not recommended)
- NetBeans (manual API loading, not recommended)
Creating offline Javadoc (optional)
Create and register a basic command
Using the Event API
Creating a Config File
Plugin debug with Eclipse
IntelliJ IDEA Plugin Debug
NoSQL/MongoDB integration with your plugin
MongoDB with Morphia (Easy Database Storage)
MySQL database integration with your plugin
Plugin.yml
Additional Resources

Spigot Source Code
Spigot Javadoc
User contributed resources and guides from the Spigot Plugin Development forum section. They provide explanations, short code sections or full libraries that might aid you with developing your plugins or provide inspiration."""
    },
    'using-the-event-api': {
        'title': 'Using the Event API',
        'url': 'https://www.spigotmc.org/wiki/using-the-event-api/',
        'content': """Using the Event API

One of the best features of using Spigot is the ability to intercept a wide range of events. This tutorial will demonstrate how to get started on listening to and intercepting events and how to create your own.

1) Creating your First Listener

1.1) Create a new Spigot project
Or use an existing project.

1.2) Create a new class
Name this class whatever you wish, keeping in mind that this class will listen to events.

1.3) Preparing your listener
Listeners must implement the org.bukkit.event.Listener interface.

Code (Java):
import org.bukkit.event.Listener;

public class MyListener implements Listener {
}

1.4) Registering your listener
It is now necessary to register an instance of this class so Spigot is able to pass events to your plugin. A common area to create a new instance of your listener and register it is in your onEnable() method in your main class.

Code (Java):
@Override
public void onEnable() {
    getServer().getPluginManager().registerEvents(new MyListener(), this);
}

You are now ready to proceed to add events to your listener.

1.5) Listening to events
To listen to any given event in your listener class, you must create a method with the org.bukkit.event.EventHandler annotation attached and the event is specified by the type in the method's argument. The method may be named whatever you wish.

Code (Java):
import org.bukkit.event.EventHandler;
import org.bukkit.event.Listener;
import org.bukkit.event.player.PlayerJoinEvent;

public class MyListener implements Listener {
    @EventHandler
    public void onPlayerJoin(PlayerJoinEvent event) {
    }
}

This method will fire whenever a player joins the server. Let's make this broadcast a greeting to the whole server:

Code (Java):
import org.bukkit.Bukkit;
import org.bukkit.event.EventHandler;
import org.bukkit.event.Listener;
import org.bukkit.event.player.PlayerJoinEvent;

public class MyListener implements Listener {
    @EventHandler
    public void onPlayerJoin(PlayerJoinEvent event) {
        Bukkit.broadcastMessage("Welcome to the server!");
    }
}

1.6) Manipulating events
You may modify what happens with most events and also obtain information about the given event. These functions are stored in the Event object in your method.

Code (Java):
event.setJoinMessage("Welcome, " + event.getPlayer().getName() + "!");

1.7) What can I listen to?
Browse through the org.bukkit.event package for a full list of events you can listen to. See the Spigot JavaDocs.

2) Advanced Functions

2.1) EventHandler parameters
The org.bukkit.event.EventHandler annotation accepts a couple parameters:

priority - Indicates the priority of your listener. There are six different priorities, in order of execution: LOWEST, LOW, NORMAL [default], HIGH, HIGHEST, MONITOR. These constants refer to the org.bukkit.event.EventPriority enum.

Note: The MONITOR priority should only be used for reading only. This priority is useful for logging plugins to see the results of an event and modifying values may interfere with those types of plugins.

ignoreCancelled - A boolean which indicates whether or not your listener should fire if the event has been cancelled before it is the listener's turn to handle the event. False by default.

2.2) Unregistering a listener
HandlerList.unregisterAll(Listener);

3) Creating your own Event

3.1) Creating the Event
Firstly, your class must extend Event:

Code (Java):
import org.bukkit.event.Event;

public class ExampleEvent extends Event {
}

You need to incorporate HandlerList methods:

Code (Java):
import org.bukkit.event.Event;
import org.bukkit.event.HandlerList;

public class ExampleEvent extends Event {
    private static final HandlerList HANDLERS = new HandlerList();

    public static HandlerList getHandlerList() {
        return HANDLERS;
    }

    @Override
    public HandlerList getHandlers() {
        return HANDLERS;
    }
}

3.2) Calling and Listening to your Event
Calling your event is relatively easy:

ExampleEvent exampleEvent = new ExampleEvent("Msrules123");
Bukkit.getPluginManager().callEvent(exampleEvent);

And listening to it is the same as any other event:

@EventHandler
public void onExampleEvent(ExampleEvent event) {
    // Handle implementation here
}

3.3) Making your Event cancellable
Implement Cancellable interface."""
    },
    'plugin-yml': {
        'title': 'Plugin.yml',
        'url': 'https://www.spigotmc.org/wiki/plugin-yml/',
        'content': """Plugin.yml

The plugin.yml is a file made to contain information about your plugin. Without this file, your plugin will NOT work. It consists of a set of attributes, each defined on a new line with no indentation.
All attributes are case sensitive. Attributes in bold are required. Attributes in italics are not.

Required Attributes:

main - Points to the class of your plugin that extends JavaPlugin. Must contain full namespace including the class file itself.
Example: main: org.spigotmc.testplugin.Test

name - The name of your plugin. Must consist of alphanumeric characters and underscores. Used to determine data folder name.
Example: name: MyPlugin

version - The version of your plugin. Common format: MAJOR.MINOR.PATCH
Example: version: 1.4.1

Optional Attributes:

description - Human friendly description of functionality.
api-version - API version (1.13-1.20+). Signals server about compatibility.
load - When plugin loads: STARTUP or POSTWORLD (default).
author / authors - Developer identifier(s).
website - Plugin/author website.
depend - Required plugins list.
softdepend - Optional plugins for full functionality.
loadbefore - Plugins that should load after yours.
prefix - Console logging name instead of plugin name.
libraries - Maven Central libraries to load (preview feature).

Commands block:
- description, aliases, permission, permission-message, usage

Permissions block:
- description, default (true/false/op/not op), children

Plugin Annotations:
Alternative to manual plugin.yml. Add as dependency:
<dependency>
    <groupId>org.spigotmc</groupId>
    <artifactId>plugin-annotations</artifactId>
    <version>1.1.0-SNAPSHOT</version>
</dependency>"""
    }
}

for page_id, page_data in scraped_pages.items():
    filepath = os.path.join(CONTENT_DIR, f'{page_id}.json')
    with open(filepath, 'w', encoding='utf-8') as f:
        json.dump(page_data, f, indent=2, ensure_ascii=False)
    print(f'Saved: {page_id}.json ({len(page_data["content"])} chars)')

print(f'\nTotal: {len(scraped_pages)} pages saved to {CONTENT_DIR}')
