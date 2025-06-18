import discord
from discord.ext import commands, tasks
import os, json, random, time, asyncio
from datetime import datetime, timedelta, timezone
from collections import defaultdict
from dotenv import load_dotenv
from typing import Optional, Dict, List

load_dotenv()
BOT_TOKEN = os.getenv('BOT_TOKEN', 'what the croc')
CHANNEL_ID = 1359790747934789706
CATCH_COOLDOWN, BATTLE_COOLDOWN, SAVE_INTERVAL = 1800, 3600, 300
STARTING_BALANCE, DAILY_REWARD, MAX_DAILY_STREAK, MAX_CATCHES = 5000, 2500, 30, 200
GUILD_TAX_RATE, MAX_GUILD_MEMBERS = 0.05, 4
ADMIN_ID = 133267997065216000

RARITY_TIERS = {"Common": (1.0, 0.60), "Uncommon": (1.5, 0.30), "Rare": (2.0, 0.08), "Epic": (3.0, 0.04), "Legendary": (5.0, 0.01), "Mythic": (10.0, 0.001)}

FANTASY_ADJECTIVES = ["Sparkly", "Fluffy", "Grumpy", "Sleepy", "Bouncy", "Sneaky", "Dizzy", "Giggly", "Wobbly", "Squishy", "Bumpy", "Fuzzy", "Silly", "Goofy", "Majestic", "Ancient", "Wise", "Fierce", "Gentle", "Swift", "Mighty", "Mysterious", "Radiant", "Shadow", "Crystal", "Golden", "Silver"]

# Initialize bot
intents = discord.Intents.default()
intents.message_content = True
intents.members = True
bot = commands.Bot(command_prefix="!", intents=intents, help_command=None)

# CREATURE TYPES WITH TYPE SYSTEM
CREATURE_TYPES = {
    "Nile Crocodile": {"base_value": 1000, "size_range": (1.0, 2.5), "emoji": "🐊", "rarity": "Common", "hp": 45, "attack": 35, "defense": 40, "speed": 25, "type": "Water"},
    "American Alligator": {"base_value": 950, "size_range": (1.0, 2.5), "emoji": "🐊", "rarity": "Common", "hp": 40, "attack": 32, "defense": 38, "speed": 28, "type": "Water"},
    "Dwarf Crocodile": {"base_value": 900, "size_range": (1.0, 2.5), "emoji": "🐊", "rarity": "Common", "hp": 35, "attack": 28, "defense": 32, "speed": 35, "type": "Water"},
    "Fox": {"base_value": 1000, "size_range": (1.0, 2.5), "emoji": "🦊", "rarity": "Common", "hp": 38, "attack": 30, "defense": 25, "speed": 42, "type": "Earth"},
    "Dog": {"base_value": 950, "size_range": (1.0, 2.5), "emoji": "🐕", "rarity": "Common", "hp": 40, "attack": 28, "defense": 30, "speed": 35, "type": "Earth"},
    "Cat": {"base_value": 900, "size_range": (1.0, 2.5), "emoji": "🐱", "rarity": "Common", "hp": 32, "attack": 26, "defense": 22, "speed": 45, "type": "Fire"},
    "Rabbit": {"base_value": 850, "size_range": (1.0, 2.5), "emoji": "🐰", "rarity": "Common", "hp": 28, "attack": 20, "defense": 18, "speed": 50, "type": "Fire"},
    "Owl": {"base_value": 1000, "size_range": (1.0, 2.5), "emoji": "🦉", "rarity": "Common", "hp": 35, "attack": 28, "defense": 24, "speed": 40, "type": "Air"},
    "Turtle": {"base_value": 950, "size_range": (1.0, 2.5), "emoji": "🐢", "rarity": "Common", "hp": 55, "attack": 22, "defense": 55, "speed": 12, "type": "Earth"},
    "Frog": {"base_value": 900, "size_range": (1.0, 2.5), "emoji": "🐸", "rarity": "Common", "hp": 25, "attack": 18, "defense": 20, "speed": 38, "type": "Water"},
    
    "Saltwater Crocodile": {"base_value": 1400, "size_range": (1.5, 3.0), "emoji": "🐊", "rarity": "Uncommon", "hp": 40, "attack": 42, "defense": 48, "speed": 22, "type": "Water"},
    "Black Caiman": {"base_value": 1350, "size_range": (1.5, 3.0), "emoji": "🐊", "rarity": "Uncommon", "hp": 42, "attack": 38, "defense": 45, "speed": 25, "type": "Water"},
    "Wolf": {"base_value": 1450, "size_range": (1.5, 3.0), "emoji": "🐺", "rarity": "Uncommon", "hp": 43, "attack": 40, "defense": 32, "speed": 38, "type": "Earth"},
    "Eagle": {"base_value": 1400, "size_range": (1.5, 3.0), "emoji": "🦅", "rarity": "Uncommon", "hp": 38, "attack": 38, "defense": 26, "speed": 48, "type": "Air"},
    "Goose": {"base_value": 1300, "size_range": (1.5, 3.0), "emoji": "🪿", "rarity": "Uncommon", "hp": 42, "attack": 32, "defense": 35, "speed": 40, "type": "Fire"},
    "Rat": {"base_value": 1250, "size_range": (1.5, 3.0), "emoji": "🐀", "rarity": "Uncommon", "hp": 35, "attack": 28, "defense": 24, "speed": 50, "type": "Earth"},
    
    "Gharial": {"base_value": 1800, "size_range": (2.0, 3.5), "emoji": "🐊", "rarity": "Rare", "hp": 45, "attack": 32, "defense": 36, "speed": 30, "type": "Water"},
    "Bear": {"base_value": 1900, "size_range": (2.0, 3.5), "emoji": "🐻", "rarity": "Rare", "hp": 48, "attack": 48, "defense": 45, "speed": 20, "type": "Earth"},
    "Hamster": {"base_value": 1850, "size_range": (2.0, 3.5), "emoji": "🐹", "rarity": "Rare", "hp": 44, "attack": 55, "defense": 28, "speed": 40, "type": "Fire"},
    "Raven": {"base_value": 1870, "size_range": (2.0, 3.5), "emoji": "🐦‍", "rarity": "Rare", "hp": 46, "attack": 45, "defense": 22, "speed": 60, "type": "Air"},
    
    "Dragon": {"base_value": 2200, "size_range": (2.5, 4.0), "emoji": "🐉", "rarity": "Epic", "hp": 63, "attack": 51, "defense": 40, "speed": 35, "type": "Fire"},
    "Phoenix": {"base_value": 2400, "size_range": (2.5, 4.0), "emoji": "🔥", "rarity": "Epic", "hp": 61, "attack": 52, "defense": 38, "speed": 50, "type": "Fire"},
    "Griffin": {"base_value": 2300, "size_range": (2.5, 4.0), "emoji": "🦃", "rarity": "Epic", "hp": 65, "attack": 48, "defense": 40, "speed": 52, "type": "Air"},
    "Whale": {"base_value": 2300, "size_range": (2.5, 4.0), "emoji": "🐋", "rarity": "Epic", "hp": 70, "attack": 40, "defense": 43, "speed": 45, "type": "Water"},
    "Gorilla": {"base_value": 2250, "size_range": (2.5, 4.0), "emoji": "🦍", "rarity": "Epic", "hp": 64, "attack": 40, "defense": 46, "speed": 34, "type": "Earth"},
    "Fairy": {"base_value": 2250, "size_range": (2.5, 4.0), "emoji": "🦋", "rarity": "Epic", "hp": 57, "attack": 47, "defense": 35, "speed": 70, "type": "Light"},
    
    "Kraken": {"base_value": 3200, "size_range": (3.0, 4.5), "emoji": "🐙", "rarity": "Legendary", "hp": 71, "attack": 65, "defense": 55, "speed": 32, "type": "Water"},
    "Unicorn": {"base_value": 3400, "size_range": (3.0, 4.5), "emoji": "🦄", "rarity": "Legendary", "hp": 70, "attack": 55, "defense": 40, "speed": 55, "type": "Light"},
    "Chimera": {"base_value": 3600, "size_range": (3.0, 4.5), "emoji": "🦁", "rarity": "Legendary", "hp": 73, "attack": 60, "defense": 48, "speed": 45, "type": "Fire"},
    "Vampire": {"base_value": 3500, "size_range": (3.0, 4.5), "emoji": "🦇", "rarity": "Legendary", "hp": 72, "attack": 65, "defense": 38, "speed": 43, "type": "Air"},
    "Giant": {"base_value": 3500, "size_range": (3.0, 4.5), "emoji": "🗿", "rarity": "Legendary", "hp": 72, "attack": 64, "defense": 43, "speed": 25, "type": "Earth"},
    
    "Azu, God of Crocs": {"base_value": 5000, "size_range": (4.0, 5.0), "emoji": "☄️", "rarity": "Mythic", "hp": 120, "attack": 75, "defense": 65, "speed": 50, "type": "Divine"}
}

# TYPE EFFECTIVENESS SYSTEM (Rock/Paper/Scissors style)
TYPE_EFFECTIVENESS = {
    "Fire": {"strong_against": ["Earth", "Air"], "weak_against": ["Water", "Light"]},
    "Water": {"strong_against": ["Fire", "Earth"], "weak_against": ["Air", "Light"]},
    "Earth": {"strong_against": ["Air", "Light"], "weak_against": ["Fire", "Water"]},
    "Air": {"strong_against": ["Water", "Light"], "weak_against": ["Fire", "Earth"]},
    "Light": {"strong_against": ["Fire", "Water"], "weak_against": ["Earth", "Air"]},
    "Divine": {"strong_against": ["Fire", "Water", "Earth", "Air"], "weak_against": ["Light"]},  # Divine is strong against basic types
}

def get_type_multiplier(attacker_type, defender_type):
    """Calculate damage multiplier based on type effectiveness"""
    if attacker_type in TYPE_EFFECTIVENESS:
        effectiveness = TYPE_EFFECTIVENESS[attacker_type]
        if defender_type in effectiveness["strong_against"]:
            return 1.3  # 30% more damage
        elif defender_type in effectiveness["weak_against"]:
            return 0.75  # 25% less damage
    return 1.0  # Normal damage

# IMPROVED BATTLE MOVES
BATTLE_MOVES = {
    "Bite": {"base_damage": 1.1, "accuracy": 95, "description": "A powerful bite attack", "type": "physical", "emoji": "🦷", "cooldown": 0},
    "Scratch": {"base_damage": 0.9, "accuracy": 100, "description": "Scratches with claws", "type": "physical", "emoji": "💥", "cooldown": 0},
    "Tackle": {"base_damage": 1.0, "accuracy": 100, "description": "Charges at the enemy", "type": "physical", "emoji": "💨", "cooldown": 0},
    "Tail Whip": {"base_damage": 0.7, "accuracy": 100, "description": "Strikes with tail", "type": "physical", "effect": "lower_defense", "emoji": "🌪️", "cooldown": 0},
    "Roar": {"base_damage": 0, "accuracy": 100, "description": "Intimidating roar that reduces enemy attack by 30% and has 25% chance to cause fear", "type": "status", "effect": "improved_roar", "emoji": "📢", "cooldown": 2},
    "Heal": {"base_damage": 0, "accuracy": 100, "description": "Restores 30% of max HP", "type": "heal", "effect": "heal", "emoji": "💚", "cooldown": 5},
    "Venom Strike": {"base_damage": 1.2, "accuracy": 85, "description": "Poisonous attack", "type": "special", "effect": "poison", "emoji": "☠️", "cooldown": 0},
    "Fire Breath": {"base_damage": 1.3, "accuracy": 90, "description": "Breathes fire", "type": "special", "effect": "burn", "emoji": "🔥", "cooldown": 0},
    "Ice Shard": {"base_damage": 1.2, "accuracy": 85, "description": "Launches ice shards", "type": "special", "effect": "freeze", "emoji": "❄️", "cooldown": 0},
    "Lightning Bolt": {"base_damage": 1.4, "accuracy": 80, "description": "Powerful electric attack", "type": "special", "emoji": "⚡", "cooldown": 0},
    "Earthquake": {"base_damage": 1.5, "accuracy": 75, "description": "Devastating ground attack", "type": "special", "emoji": "🌍", "cooldown": 0},
    "Divine Light": {"base_damage": 1.2, "accuracy": 85, "description": "Holy attack", "type": "special", "emoji": "✨", "cooldown": 0},
    "Cosmic Blast": {"base_damage": 1.5, "accuracy": 70, "description": "Ultimate cosmic energy", "type": "special", "emoji": "🌌", "cooldown": 0},
    "Shield": {"base_damage": 0, "accuracy": 100, "description": "Creates a protective barrier, reducing damage by 50% for 3 turns and reflecting 15% damage", "type": "status", "effect": "improved_defense", "emoji": "🛡️", "cooldown": 3},
    "Focus": {"base_damage": 0, "accuracy": 100, "description": "Raises attack", "type": "status", "effect": "raise_attack", "emoji": "🎯", "cooldown": 3},
    "Wing Attack": {"base_damage": 1.1, "accuracy": 90, "description": "Strikes with powerful wings", "type": "physical", "emoji": "🪶", "cooldown": 0},
    "Pounce": {"base_damage": 1.0, "accuracy": 95, "description": "Leaps onto the enemy", "type": "physical", "emoji": "🐾", "cooldown": 0},
    "Slam": {"base_damage": 1.2, "accuracy": 85, "description": "Powerful body slam", "type": "physical", "emoji": "💢", "cooldown": 0},
    "Aqua Jet": {"base_damage": 0.9, "accuracy": 100, "description": "High-speed water attack", "type": "special", "emoji": "🌊", "cooldown": 0},
    "Stone Edge": {"base_damage": 1.3, "accuracy": 80, "description": "Sharp stone projectiles", "type": "special", "emoji": "🪨", "cooldown": 0},
    "Shadow Ball": {"base_damage": 1.2, "accuracy": 85, "description": "Ghostly energy attack", "type": "special", "emoji": "👻", "cooldown": 0},
    "Solar Beam": {"base_damage": 1.4, "accuracy": 90, "description": "Concentrated sunlight", "type": "special", "emoji": "☀️", "cooldown": 0},
    "Blizzard": {"base_damage": 1.3, "accuracy": 70, "description": "Freezing wind storm", "type": "special", "effect": "freeze", "emoji": "🌨️", "cooldown": 0},
    "Thunder": {"base_damage": 1.5, "accuracy": 70, "description": "Massive lightning strike", "type": "special", "emoji": "⛈️", "cooldown": 0},
    "Psychic": {"base_damage": 1.2, "accuracy": 100, "description": "Mind-based attack", "type": "special", "emoji": "🧠", "cooldown": 0},
    "Hyper Beam": {"base_damage": 1.7, "accuracy": 90, "description": "Devastating energy beam", "type": "special", "emoji": "💫", "cooldown": 0},
    "Meteor Strike": {"base_damage": 1.9, "accuracy": 75, "description": "Calls down meteors", "type": "special", "emoji": "☄️", "cooldown": 0},
    "Speed Boost": {"base_damage": 0, "accuracy": 100, "description": "Increases speed and grants 25% chance for extra attack", "type": "status", "effect": "speed_boost", "emoji": "💨", "cooldown": 3},
    "Time Warp": {"base_damage": 0, "accuracy": 100, "description": "Resets all move cooldowns and grants extra turn", "type": "status", "effect": "time_warp", "emoji": "⏰", "cooldown": 5},
    "Regenerate": {"base_damage": 0, "accuracy": 100, "description": "Slowly heals over time", "type": "heal", "effect": "regen", "emoji": "🔄", "cooldown": 5},
    "Barrier": {"base_damage": 0, "accuracy": 100, "description": "Creates protective barrier", "type": "status", "effect": "defense_boost", "emoji": "🔮", "cooldown": 3}
}

STORE_ITEMS = {
    "upgrades": {
        "net": {"name": "Advanced Net", "description": "Increases catch value by 8% per level (max 15)", "price": 10000, "max_level": 15, "price_increase": 1.4, "keywords": ["net", "advanced", "catch", "value"]},
        "radar": {"name": "Species Radar", "description": "10% chance per level to detect rarer species (max 10)", "price": 15000, "max_level": 10, "price_increase": 1.8, "keywords": ["radar", "species", "rare", "detect"]},
        "luck": {"name": "Lucky Charm", "description": "Increases rare modifier chance by 0.5% per level (max 10)", "price": 20000, "max_level": 10, "price_increase": 2.0, "keywords": ["luck", "lucky", "charm", "modifier"]},
        "storage": {"name": "Storage Expansion", "description": "Adds 10 more slots per level (max 5)", "price": 25000, "max_level": 5, "price_increase": 2.5, "keywords": ["storage", "expansion", "slots", "space"]},
        "efficiency": {"name": "Catch Efficiency", "description": "Reduces catch cooldown by 5% per level (max 10)", "price": 18000, "max_level": 10, "price_increase": 1.6, "keywords": ["efficiency", "cooldown", "speed", "faster"]},
        "battle_training": {"name": "Battle Training", "description": "Increases battle rewards by 8% per level (max 10)", "price": 22000, "max_level": 10, "price_increase": 1.7, "keywords": ["battle", "training", "rewards", "combat"]},
        "treasure_hunter": {"name": "Treasure Hunter", "description": "5% chance per level to find bonus money when catching (max 10)", "price": 25000, "max_level": 10, "price_increase": 1.8, "keywords": ["treasure", "hunter", "money", "bonus"]},
        "daily_boost": {"name": "Daily Boost", "description": "Increases daily reward by 10% per level (max 5)", "price": 30000, "max_level": 5, "price_increase": 2.0, "keywords": ["daily", "boost", "reward", "income"]},
    },
    "enchantments": {
        "fire": {"name": "Flaming Aura", "description": "+15% damage, 20% burn chance (7 days)", "price": 35000, "duration": 7, "effect": {"damage_multiplier": 1.15, "burn_chance": 0.2}, "keywords": ["fire", "flame", "burn", "damage"]},
        "ice": {"name": "Frostbite", "description": "15% freeze chance, +10% defense (7 days)", "price": 40000, "duration": 7, "effect": {"freeze_chance": 0.15, "defense_multiplier": 1.1}, "keywords": ["ice", "frost", "freeze", "defense"]},
        "vampire": {"name": "Vampiric Bite", "description": "Heals 10% of damage dealt (7 days)", "price": 45000, "duration": 7, "effect": {"lifesteal": 0.1}, "keywords": ["vampire", "lifesteal", "heal", "drain"]},
        "lightning": {"name": "Lightning Strikes", "description": "15% chance for +50% damage (5 days)", "price": 50000, "duration": 5, "effect": {"crit_chance": 0.15, "crit_multiplier": 1.5}, "keywords": ["lightning", "electric", "crit", "damage"]},
        "poison": {"name": "Toxic Venom", "description": "Applies poison dealing 3% damage per turn (7 days)", "price": 38000, "duration": 7, "effect": {"poison_chance": 0.25, "poison_damage": 0.03}, "keywords": ["poison", "toxic", "venom", "dot"]},
        "stealth": {"name": "Stealth Mode", "description": "15% chance to dodge attacks (5 days)", "price": 42000, "duration": 5, "effect": {"dodge_chance": 0.15}, "keywords": ["stealth", "dodge", "evasion", "avoid"]},
        "critical": {"name": "Critical Focus", "description": "20% chance for critical hits dealing +40% damage (7 days)", "price": 48000, "duration": 7, "effect": {"crit_chance": 0.2, "crit_damage": 1.4}, "keywords": ["critical", "crit", "focus", "precision"]},
        "regeneration": {"name": "Regeneration", "description": "Recover 2% HP each turn (6 days)", "price": 55000, "duration": 6, "effect": {"regen": 0.02}, "keywords": ["regen", "regeneration", "heal", "recovery"]},
    },
    "cosmetics": {
        "hat": {"name": "Golden Crown", "description": "Increases value by 20% when equipped", "price": 75000, "emoji": "👑", "effect": {"value_multiplier": 1.2}, "keywords": ["hat", "crown", "golden", "value"]},
        "glasses": {"name": "Lucky Shades", "description": "15% higher chance for rare modifiers", "price": 60000, "emoji": "🕶️", "effect": {"rare_chance": 1.15}, "keywords": ["glasses", "shades", "lucky", "rare"]},
        "scarf": {"name": "Champion's Scarf", "description": "Gives +15% battle power", "price": 50000, "emoji": "🧣", "effect": {"battle_power": 1.15}, "keywords": ["scarf", "champion", "battle", "power"]},
        "armor": {"name": "Knight's Armor", "description": "+25% defense in battles", "price": 90000, "emoji": "🛡️", "effect": {"defense_multiplier": 1.25}, "keywords": ["armor", "knight", "defense", "protection"]},
        "amulet": {"name": "Lucky Amulet", "description": "10% chance to find rare items in lootboxes", "price": 85000, "emoji": "🔮", "effect": {"lootbox_luck": 1.1}, "keywords": ["amulet", "lucky", "lootbox", "rare"]},
        "cape": {"name": "Hero's Cape", "description": "Increases battle rewards by 15%", "price": 95000, "emoji": "🧥", "effect": {"battle_reward": 1.15}, "keywords": ["cape", "hero", "battle", "rewards"]},
    },
    "consumables": {
        "revive": {"name": "Revive Crystal", "description": "Revives a dead creature after battle", "price": 100000, "effect": {"revive": True}, "keywords": ["revive", "crystal", "resurrect", "death"]},
        "reroll": {"name": "Modifier Reroll", "description": "Rerolls all modifiers on a creature", "price": 50000, "effect": {"reroll": True}, "keywords": ["reroll", "modifier", "random", "change"]},
    },
    "lootboxes": {
        "basic": {"name": "Basic Lootbox", "description": "Contains common items and small rewards", "price": 35000, "contents": ["money_small", "consumable_common", "enchantment_common"], "keywords": ["basic", "lootbox", "common", "small"]},
        "premium": {"name": "Premium Lootbox", "description": "Better chance for rare items and medium rewards", "price": 65000, "contents": ["money_medium", "consumable_uncommon", "enchantment_uncommon", "cosmetic_common"], "keywords": ["premium", "lootbox", "rare", "medium"]},
        "deluxe": {"name": "Deluxe Lootbox", "description": "High chance for rare items and large rewards", "price": 100000, "contents": ["money_large", "consumable_rare", "enchantment_rare", "cosmetic_uncommon"], "keywords": ["deluxe", "lootbox", "high", "large"]},
        "legendary": {"name": "Legendary Lootbox", "description": "Guaranteed rare items and massive rewards", "price": 250000, "contents": ["money_huge", "consumable_rare", "enchantment_rare", "cosmetic_rare", "special_item"], "keywords": ["legendary", "lootbox", "guaranteed", "massive"]}
    }
}

MODIFIERS = [("Tiny", 0.8, "🔹", "Common"), ("Large", 1.5, "🔸", "Common"), ("Swift", 1.3, "💨", "Common"), ("Heavy", 1.4, "⚖️", "Common"), ("Bright", 1.2, "💡", "Common"), ("Dark", 1.2, "🌑", "Common"), ("Sparkly", 1.8, "✨", "Uncommon"), ("Glowing", 1.7, "🌟", "Uncommon"), ("Shiny", 1.6, "💎", "Uncommon"), ("Metallic", 1.9, "🔩", "Uncommon"), ("Crystalline", 2.0, "💠", "Uncommon"), ("Ethereal", 1.8, "👻", "Uncommon"), ("Mystical", 2.5, "🔮", "Rare"), ("Enchanted", 2.3, "🪄", "Rare"), ("Blessed", 2.4, "🙏", "Rare"), ("Cursed", 2.6, "💀", "Rare"), ("Ancient", 2.7, "🏛️", "Rare"), ("Elemental", 2.5, "🌪️", "Rare"), ("Spectral", 2.8, "👤", "Rare"), ("Radiant", 2.6, "☀️", "Rare"), ("Legendary", 4.0, "🏆", "Epic"), ("Mythical", 4.2, "🦄", "Epic"), ("Divine", 4.5, "⚡", "Epic"), ("Infernal", 4.3, "🔥", "Epic"), ("Celestial", 4.8, "🌌", "Epic"), ("Primordial", 4.6, "🌋", "Epic"), ("Cosmic", 6.0, "🌠", "Mythic"), ("Transcendent", 7.0, "🔆", "Mythic"), ("Omnipotent", 8.0, "👁️", "Mythic"), ("Reality-Bending", 9.0, "🌀", "Mythic"), ("Time-Touched", 10.0, "⏳", "Mythic")]

class MoveManager:
    def __init__(self):
        self.cooldowns = defaultdict(lambda: defaultdict(int))
    
    def can_use_move(self, creature_id, move_name, current_turn):
        if move_name not in BATTLE_MOVES:
            return True
        
        move_cooldown = BATTLE_MOVES[move_name].get("cooldown", 0)
        if move_cooldown == 0:
            return True
        
        last_used = self.cooldowns[creature_id][move_name]
        return current_turn - last_used >= move_cooldown
    
    def use_move(self, creature_id, move_name, current_turn):
        if self.can_use_move(creature_id, move_name, current_turn):
            self.cooldowns[creature_id][move_name] = current_turn
            return True
        return False
    
    def get_cooldown_remaining(self, creature_id, move_name, current_turn):
        if move_name not in BATTLE_MOVES:
            return 0
        
        move_cooldown = BATTLE_MOVES[move_name].get("cooldown", 0)
        if move_cooldown == 0:
            return 0
        
        last_used = self.cooldowns[creature_id][move_name]
        remaining = move_cooldown - (current_turn - last_used)
        return max(0, remaining)
    
    def reset_cooldowns(self, creature_id):
        """Reset all cooldowns for a creature (used by Time Warp)"""
        if creature_id in self.cooldowns:
            self.cooldowns[creature_id].clear()

class StatusEffect:
    def __init__(self, name, duration, effect_type, value):
        self.name, self.duration, self.effect_type, self.value = name, duration, effect_type, value

class BattleCreature:
    def __init__(self, creature_data, owner_name, team_color="🔴"):
        self.name, self.emoji, self.owner, self.team_color = creature_data["type"], creature_data["emoji"], owner_name, team_color
        self.display_name = creature_data.get("display_name", creature_data["type"])
        self.id = f"{owner_name}_{self.name}_{random.randint(1000, 9999)}"
        base_stats = CREATURE_TYPES[creature_data["type"]]
        
        # Get creature type for type effectiveness
        self.creature_type = base_stats.get("type", "Earth")
        
        size_multiplier = 1 + (creature_data["size"] - 1) * 0.05
        
        self.max_hp = int(base_stats["hp"] * size_multiplier)
        self.current_hp = self.max_hp
        self.base_attack = int(base_stats["attack"] * size_multiplier)
        self.base_defense = int(base_stats["defense"] * size_multiplier)
        self.base_speed = int(base_stats["speed"] * size_multiplier)
        self.current_attack, self.current_defense, self.speed = self.base_attack, self.base_defense, self.base_speed
        self.status_effects, self.value, self.size, self.rarity = [], creature_data["value"], creature_data["size"], creature_data["rarity"]
        self.modifiers, self.cosmetics, self.enchantments = creature_data.get("modifiers", []), creature_data.get("cosmetics", []), creature_data.get("enchantments", [])
        self.stat_modifiers = {"attack": 1.0, "defense": 1.0, "speed": 1.0}
        self.is_dead = False
        self.shield_turns = 0
        self.shield_damage_reduction = 0
        self.shield_reflection = 0
        self.fear_turns = 0
        self.speed_boost_active = False
        self.extra_attack_chance = 0
        self.battle_log = []  # Initialize battle_log
        self._apply_cosmetic_effects()
        self._apply_enchantment_effects()
        self.moves = self._assign_moves()
    
    def _apply_cosmetic_effects(self):
        for cosmetic in self.cosmetics:
            if cosmetic in STORE_ITEMS["cosmetics"]:
                effect = STORE_ITEMS["cosmetics"][cosmetic].get("effect", {})
                if "battle_power" in effect: 
                    self.current_attack = int(self.current_attack * min(effect["battle_power"], 1.15))
                if "defense_multiplier" in effect: 
                    self.current_defense = int(self.current_defense * min(effect["defense_multiplier"], 1.25))
                if "value_multiplier" in effect: 
                    self.value = int(self.value * effect["value_multiplier"])
                # Handle type additions from cosmetics
                if "add_type" in effect:
                    self.creature_type = effect["add_type"]
    
    def _apply_enchantment_effects(self):
        for enchantment in self.enchantments:
            if enchantment in STORE_ITEMS["enchantments"]:
                effect = STORE_ITEMS["enchantments"][enchantment].get("effect", {})
                if "damage_multiplier" in effect: 
                    self.current_attack = int(self.current_attack * min(effect["damage_multiplier"], 1.15))
                if "defense_multiplier" in effect: 
                    self.current_defense = int(self.current_defense * min(effect["defense_multiplier"], 1.1))
    
    def _assign_moves(self):
        base_moves = ["Bite", "Scratch", "Tackle"]
        if self.rarity == "Common": additional_moves = random.sample(["Tail Whip", "Roar", "Pounce"], 2)
        elif self.rarity == "Uncommon": additional_moves = random.sample(["Heal", "Wing Attack", "Slam", "Shield"], 2)
        elif self.rarity == "Rare": additional_moves = random.sample(["Fire Breath", "Ice Shard", "Aqua Jet", "Stone Edge"], 3)
        elif self.rarity == "Epic": additional_moves = random.sample(["Lightning Bolt", "Shadow Ball", "Solar Beam", "Psychic", "Blizzard"], 3)
        else: additional_moves = random.sample(["Cosmic Blast", "Divine Light", "Hyper Beam", "Meteor Strike", "Speed Boost", "Time Warp"], 4)
        
        creature_type_moves = {"Dragon": ["Fire Breath", "Cosmic Blast"], "Phoenix": ["Fire Breath", "Solar Beam"], "Kraken": ["Aqua Jet", "Thunder"], "Fox": ["Pounce", "Shadow Ball"], "Wolf": ["Bite", "Roar"], "Eagle": ["Wing Attack", "Lightning Bolt"], "Bear": ["Slam", "Roar"]}
        if self.name in creature_type_moves: additional_moves.extend(creature_type_moves[self.name])
        
        all_moves = list(set(base_moves + additional_moves))
        return random.sample(all_moves, min(6, len(all_moves)))
    
    def get_effective_attack(self):
        return int(self.current_attack * self.stat_modifiers["attack"])
    
    def get_effective_defense(self):
        return int(self.current_defense * self.stat_modifiers["defense"])
    
    def get_effective_speed(self):
        return int(self.speed * self.stat_modifiers["speed"])
    
    def apply_status_effects(self):
        effects_to_remove = []
        for effect in self.status_effects:
            if effect.effect_type == "poison":
                damage = int(self.max_hp * effect.value)
                self.current_hp = max(0, self.current_hp - damage)
                effect.duration -= 1
                if effect.duration <= 0: 
                    effects_to_remove.append(effect)
                    self.battle_log.append(f"☠️ {self.team_color} {self.display_name} is no longer poisoned!")
            elif effect.effect_type == "burn":
                damage = int(self.max_hp * 0.05)
                self.current_hp = max(0, self.current_hp - damage)
                effect.duration -= 1
                if effect.duration <= 0: 
                    effects_to_remove.append(effect)
                    self.battle_log.append(f"🔥 {self.team_color} {self.display_name} is no longer burned!")
            elif effect.effect_type == "regen":
                heal = int(self.max_hp * effect.value)
                self.current_hp = min(self.max_hp, self.current_hp + heal)
                effect.duration -= 1
                if effect.duration <= 0: 
                    effects_to_remove.append(effect)
                    self.battle_log.append(f"💚 {self.team_color} {self.display_name} stopped regenerating!")
        
        if self.shield_turns > 0:
            self.shield_turns -= 1
            if self.shield_turns <= 0:
                self.shield_damage_reduction = 0
                self.shield_reflection = 0
                self.battle_log.append(f"🛡️ {self.team_color} {self.display_name}'s shield wore off!")
        
        if self.fear_turns > 0:
            self.fear_turns -= 1
            if self.fear_turns <= 0:
                self.battle_log.append(f"😱 {self.team_color} {self.display_name} is no longer afraid!")
        
        for effect in effects_to_remove: 
            self.status_effects.remove(effect)
        
        for enchantment in self.enchantments:
            if enchantment == "regeneration" and enchantment in STORE_ITEMS["enchantments"]:
                regen_amount = int(self.max_hp * 0.01)
                if self.current_hp < self.max_hp:
                    self.current_hp = min(self.max_hp, self.current_hp + regen_amount)
    
    def can_dodge(self):
        dodge_chance = 0
        for enchantment in self.enchantments:
            if enchantment in STORE_ITEMS["enchantments"]:
                effect = STORE_ITEMS["enchantments"][enchantment].get("effect", {})
                if "dodge_chance" in effect: 
                    dodge_chance += min(effect["dodge_chance"], 0.25)
        return random.random() < dodge_chance

class TeamBattleSystem:
    def __init__(self, p1_team, p2_team, p1_name, p2_name, ctx):
        self.p1_team = p1_team
        self.p2_team = p2_team
        self.p1_name = p1_name
        self.p2_name = p2_name
        self.ctx = ctx
        self.current_turn = 0
        self.move_manager = MoveManager()
        self.battle_log = []
        self.embed = None
        self.message = None
        self.battle_active = True
        self.extra_attack_chance = 0.25  # 25% max chance at 100 speed
        self.min_speed_for_extra = 20  # Minimum speed required for extra attacks
        self.max_speed_for_extra = 60  # Speed at which max extra attack chance is reached
        self.p1_current, self.p2_current = 0, 0
        for creature in self.p1_team: 
            creature.team_color = "🔴"
            creature.battle_log = self.battle_log
        for creature in self.p2_team: 
            creature.team_color = "🔵"
            creature.battle_log = self.battle_log
    
    async def start_battle(self):
        embed = discord.Embed(title="⚔️ Team Battle Started!", description=f"🔴 {self.p1_name} vs 🔵 {self.p2_name}", color=0xff9900)
        p1_team_text = "\n".join([f"{i+1}. {c.emoji} {c.display_name} (HP: {c.current_hp}) [{c.creature_type}]" for i, c in enumerate(self.p1_team)])
        p2_team_text = "\n".join([f"{i+1}. {c.emoji} {c.display_name} (HP: {c.current_hp}) [{c.creature_type}]" for i, c in enumerate(self.p2_team)])
        embed.add_field(name=f"🔴 {self.p1_name}'s Team", value=p1_team_text, inline=True)
        embed.add_field(name=f"🔵 {self.p2_name}'s Team", value=p2_team_text, inline=True)
        embed.add_field(name="Battle Log", value="Team battle begins!", inline=False)
        self.message = await self.ctx.send(embed=embed)
        
        while self.p1_current < len(self.p1_team) and self.p2_current < len(self.p2_team):
            p1_creature = self.p1_team[self.p1_current]
            p2_creature = self.p2_team[self.p2_current]

            # If either creature is defeated, move to the next
            if p1_creature.current_hp <= 0:
                self.battle_log.append(f"💀 {p1_creature.team_color} {p1_creature.display_name} has been defeated!")
                self.p1_current += 1
                if self.p1_current < len(self.p1_team):
                    next_creature = self.p1_team[self.p1_current]
                    self.battle_log.append(f"🔄 {next_creature.team_color} {next_creature.display_name} enters the battle!")
                await self.update_battle_embed()
                await asyncio.sleep(2)
                continue

            if p2_creature.current_hp <= 0:
                self.battle_log.append(f"💀 {p2_creature.team_color} {p2_creature.display_name} has been defeated!")
                self.p2_current += 1
                if self.p2_current < len(self.p2_team):
                    next_creature = self.p2_team[self.p2_current]
                    self.battle_log.append(f"🔄 {next_creature.team_color} {next_creature.display_name} enters the battle!")
                await self.update_battle_embed()
                await asyncio.sleep(2)
                continue

            # Only the two current creatures fight each round
            if p1_creature.get_effective_speed() >= p2_creature.get_effective_speed():
                await self.execute_turn(p1_creature, p2_creature)
                if p2_creature.current_hp > 0:
                    await self.execute_turn(p2_creature, p1_creature)
            else:
                await self.execute_turn(p2_creature, p1_creature)
                if p1_creature.current_hp > 0:
                    await self.execute_turn(p1_creature, p2_creature)

            # Apply status effects after both have acted
            p1_creature.apply_status_effects()
            p2_creature.apply_status_effects()

            self.current_turn += 1
            await asyncio.sleep(2)
        
        winner_name = self.p2_name if self.p1_current >= len(self.p1_team) else self.p1_name
        winner_team = self.p2_team if self.p1_current >= len(self.p1_team) else self.p1_team
        self.battle_log.append(f"🏆 {winner_name} wins the team battle!")
        await self.update_battle_embed()
        return winner_name, winner_team
    
    async def execute_turn(self, attacker, defender):
        # Check for extra attack based on speed difference
        extra_attack = False
        if attacker.get_effective_speed() > defender.get_effective_speed():
            speed_diff = attacker.get_effective_speed() - defender.get_effective_speed()
            # Calculate extra attack chance based on speed
            if speed_diff >= self.min_speed_for_extra:
                # Linear scaling from 0% at min_speed to max_chance at max_speed
                speed_factor = min(1.0, (speed_diff - self.min_speed_for_extra) / (self.max_speed_for_extra - self.min_speed_for_extra))
                extra_attack_chance = self.extra_attack_chance * speed_factor
                extra_attack = random.random() < extra_attack_chance

        # Execute main attack
        move_name = self.select_move(attacker, defender)
        await self.execute_move(attacker, defender, move_name)
        
        # Execute extra attack if triggered
        if extra_attack and attacker.current_hp > 0 and defender.current_hp > 0:
            self.battle_log.append(f"⚡ {attacker.team_color} {attacker.display_name} gets an extra attack!")
            move_name = self.select_move(attacker, defender)
            await self.execute_move(attacker, defender, move_name, is_extra_attack=True)
        
        # Apply status effects
        attacker.apply_status_effects()
        defender.apply_status_effects()
        
        # Update battle display
        await self.update_battle_embed()
        
        # Check for battle end
        if not self.battle_active:
            return True
        return False
    
    def select_move(self, attacker, defender):
        available_moves = []
        for move in attacker.moves:
            if self.move_manager.can_use_move(attacker.id, move, self.current_turn):
                available_moves.append(move)
        
        if not available_moves:
            available_moves = [move for move in attacker.moves if BATTLE_MOVES[move].get("cooldown", 0) == 0]
        
        if not available_moves:
            available_moves = attacker.moves
        
        if attacker.current_hp < attacker.max_hp * 0.3 and "Heal" in available_moves: 
            return "Heal"
        if attacker.stat_modifiers["attack"] < 1.5 and "Focus" in available_moves and random.random() < 0.3: 
            return "Focus"
        if attacker.shield_turns == 0 and "Shield" in available_moves and random.random() < 0.3: 
            return "Shield"
        if "Roar" in available_moves and random.random() < 0.4:
            return "Roar"
        if "Speed Boost" in available_moves and not attacker.speed_boost_active and random.random() < 0.3:
            return "Speed Boost"
        if "Time Warp" in available_moves and random.random() < 0.2:
            return "Time Warp"
        
        special_moves = [m for m in available_moves if BATTLE_MOVES[m]["type"] == "special"]
        if special_moves and random.random() < 0.7: 
            return random.choice(special_moves)
        
        return random.choice(available_moves)
    
    async def execute_move(self, attacker, defender, move_name, is_extra_attack=False):
        move = BATTLE_MOVES[move_name]
        move_emoji = move.get("emoji", "💥")
        
        if not self.move_manager.can_use_move(attacker.id, move_name, self.current_turn):
            remaining = self.move_manager.get_cooldown_remaining(attacker.id, move_name, self.current_turn)
            self.battle_log.append(f"{attacker.team_color} {attacker.display_name} tried to use {move_name} but it's on cooldown for {remaining} more turns!")
            return
        
        self.move_manager.use_move(attacker.id, move_name, self.current_turn)
        
        if defender.can_dodge() and move["type"] in ["physical", "special"]:
            self.battle_log.append(f"{defender.team_color} {defender.display_name} dodged {attacker.team_color} {attacker.display_name}'s {move_emoji} {move_name}!")
            return
        
        hit = random.random() * 100 < move["accuracy"]
        if not hit:
            self.battle_log.append(f"{attacker.team_color} {attacker.display_name} used {move_emoji} {move_name} but missed!")
            return
        
        if move["type"] == "heal":
            heal_amount = int(attacker.max_hp * 0.3)
            attacker.current_hp = min(attacker.current_hp + heal_amount, attacker.max_hp)
            self.battle_log.append(f"{attacker.team_color} {attacker.display_name} used {move_emoji} {move_name} and restored {heal_amount} HP!")
        
        elif move["type"] == "status":
            effect = move.get("effect")
            if effect == "improved_roar":
                defender.stat_modifiers["attack"] = max(0.3, defender.stat_modifiers["attack"] - 0.3)
                self.battle_log.append(f"{attacker.team_color} {attacker.display_name} used {move_emoji} {move_name}! {defender.team_color} {defender.display_name}'s attack fell sharply!")
                
                if random.random() < 0.25:
                    defender.fear_turns = 2
                    self.battle_log.append(f"{defender.team_color} {defender.display_name} is paralyzed with fear!")
                
                attacker.stat_modifiers["attack"] = min(2.0, attacker.stat_modifiers["attack"] + 0.15)
                self.battle_log.append(f"{attacker.team_color} {attacker.display_name} gained confidence!")
                
            elif effect == "improved_defense":
                attacker.shield_turns = 3
                attacker.shield_damage_reduction = 0.5
                attacker.shield_reflection = 0.15
                self.battle_log.append(f"{attacker.team_color} {attacker.display_name} used {move_emoji} {move_name}! Created a powerful protective barrier!")
                
            elif effect == "speed_boost":
                attacker.stat_modifiers["speed"] = min(2.0, attacker.stat_modifiers["speed"] + 0.4)
                attacker.speed_boost_active = True
                # Calculate extra attack chance based on speed stat
                base_chance = 0.10  # Base 25% chance
                speed_bonus = min(0.15, attacker.speed / 100)  # Up to 15% additional chance based on speed
                attacker.extra_attack_chance = base_chance + speed_bonus
                self.battle_log.append(f"{attacker.team_color} {attacker.display_name} used {move_emoji} {move_name}! Speed rose sharply and gained {int(attacker.extra_attack_chance * 100)}% extra attack chance!")
                
            elif effect == "time_warp":
                # Reset all cooldowns for the attacker
                self.move_manager.reset_cooldowns(attacker.id)
                self.battle_log.append(f"{attacker.team_color} {attacker.display_name} used {move_emoji} {move_name}! All move cooldowns reset!")
                # Grant an extra turn by allowing another move immediately
                extra_move = self.select_move(attacker, defender)
                self.battle_log.append(f"⏰ Time flows differently! {attacker.team_color} {attacker.display_name} gets another turn!")
                await self.execute_move(attacker, defender, extra_move)
                
            elif effect == "lower_attack":
                defender.stat_modifiers["attack"] = max(0.5, defender.stat_modifiers["attack"] - 0.2)
                self.battle_log.append(f"{attacker.team_color} {attacker.display_name} used {move_emoji} {move_name}! {defender.team_color} {defender.display_name}'s attack fell!")
            elif effect == "lower_defense":
                defender.stat_modifiers["defense"] = max(0.5, defender.stat_modifiers["defense"] - 0.2)
                self.battle_log.append(f"{attacker.team_color} {attacker.display_name} used {move_emoji} {move_name}! {defender.team_color} {defender.display_name}'s defense fell!")
            elif effect == "raise_attack":
                attacker.stat_modifiers["attack"] = min(2.0, attacker.stat_modifiers["attack"] + 0.3)
                self.battle_log.append(f"{attacker.team_color} {attacker.display_name} used {move_emoji} {move_name}! Attack rose!")
            elif effect == "raise_defense":
                attacker.stat_modifiers["defense"] = min(2.0, attacker.stat_modifiers["defense"] + 0.3)
                self.battle_log.append(f"{attacker.team_color} {attacker.display_name} used {move_emoji} {move_name}! Defense rose!")
            elif effect == "defense_boost":
                attacker.stat_modifiers["defense"] = min(2.0, attacker.stat_modifiers["defense"] + 0.5)
                self.battle_log.append(f"{attacker.team_color} {attacker.display_name} used {move_emoji} {move_name}! Defense rose sharply!")
            elif effect == "regen":
                attacker.status_effects.append(StatusEffect("Regeneration", 5, "regen", 0.01))
                self.battle_log.append(f"{attacker.team_color} {attacker.display_name} used {move_emoji} {move_name}! Started regenerating!")
        
        else:
            base_damage = move["base_damage"]
            attack_stat = attacker.get_effective_attack()
            defense_stat = defender.get_effective_defense()
            
            # Apply type effectiveness
            type_multiplier = get_type_multiplier(attacker.creature_type, defender.creature_type)
            
            damage = int((base_damage * attack_stat * 20 * type_multiplier) / (defense_stat + 10))
            damage = int(damage * random.uniform(0.85, 1.15))
            damage = max(1, min(damage, defender.max_hp // 3))
            
            # Reduce damage for extra attacks
            if is_extra_attack:
                damage = int(damage * 0.5)  # Extra attacks do 50% damage
            
            if defender.shield_turns > 0:
                reduced_damage = int(damage * defender.shield_damage_reduction)
                damage -= reduced_damage
                self.battle_log.append(f"🛡️ Shield absorbed {reduced_damage} damage!")
                
                if defender.shield_reflection > 0:
                    reflected_damage = int(damage * defender.shield_reflection)
                    attacker.current_hp = max(0, attacker.current_hp - reflected_damage)
                    self.battle_log.append(f"⚡ {reflected_damage} damage reflected back to {attacker.team_color} {attacker.display_name}!")
            
            crit_multiplier = 1.0
            crit_happened = False

            for enchantment in attacker.enchantments:
                if enchantment in STORE_ITEMS["enchantments"]:
                    effect = STORE_ITEMS["enchantments"][enchantment]["effect"]
                    
                    if "crit_chance" in effect and random.random() < effect["crit_chance"]:
                        if enchantment == "lightning":
                            crit_multiplier = min(effect.get("crit_multiplier", 1.5), 2.0)
                            self.battle_log.append(f"⚡ Lightning Strike! Critical hit!")
                        elif enchantment == "critical":
                            crit_multiplier = min(effect.get("crit_damage", 1.4), 1.8)
                            self.battle_log.append(f"🎯 Critical Focus! Precise strike!")
                        else:
                            crit_multiplier = min(effect.get("crit_multiplier", 1.5), 1.8)
                            self.battle_log.append(f"💥 Critical hit!")
                        crit_happened = True
                        break
            
            damage = int(damage * crit_multiplier)
            defender.current_hp = max(0, defender.current_hp - damage)
            
            # Show type effectiveness in battle log
            effectiveness_text = ""
            if type_multiplier > 1.0:
                effectiveness_text = " It's super effective!"
            elif type_multiplier < 1.0:
                effectiveness_text = " It's not very effective..."
            
            attack_text = f"{attacker.team_color} {attacker.display_name} used {move_emoji} {move_name} and dealt {damage} damage!"
            if is_extra_attack:
                attack_text += " (Extra Attack)"
            attack_text += effectiveness_text
            self.battle_log.append(attack_text)
            
            for enchantment in attacker.enchantments:
                if enchantment in STORE_ITEMS["enchantments"]:
                    effect = STORE_ITEMS["enchantments"][enchantment]["effect"]
                    if "lifesteal" in effect:
                        heal = int(damage * min(effect["lifesteal"], 0.15))
                        if heal > 0:
                            attacker.current_hp = min(attacker.max_hp, attacker.current_hp + heal)
                            self.battle_log.append(f"🩸 {attacker.team_color} {attacker.display_name} drained {heal} HP!")
            
            if "effect" in move and move["effect"] in ["burn", "freeze", "poison"]:
                effect_chance = 0.3
                
                for enchantment in attacker.enchantments:
                    if enchantment in STORE_ITEMS["enchantments"]:
                        ench_effect = STORE_ITEMS["enchantments"][enchantment]["effect"]
                        if move["effect"] == "burn" and "burn_chance" in ench_effect:
                            effect_chance = max(effect_chance, min(ench_effect["burn_chance"], 0.4))
                        elif move["effect"] == "freeze" and "freeze_chance" in ench_effect:
                            effect_chance = max(effect_chance, min(ench_effect["freeze_chance"], 0.4))
                        elif move["effect"] == "poison" and "poison_chance" in ench_effect:
                            effect_chance = max(effect_chance, min(ench_effect["poison_chance"], 0.5))
                
                if random.random() < effect_chance:
                    if move["effect"] == "burn":
                        defender.status_effects.append(StatusEffect("Burn", 3, "burn", 0.05))
                        self.battle_log.append(f"{defender.team_color} {defender.display_name} was burned! 🔥")
                    elif move["effect"] == "freeze":
                        defender.stat_modifiers["speed"] = max(0.3, defender.stat_modifiers["speed"] - 0.5)
                        self.battle_log.append(f"{defender.team_color} {defender.display_name} was frozen! ❄️")
                    elif move["effect"] == "poison":
                        poison_damage = 0.03
                        for enchantment in attacker.enchantments:
                            if enchantment in STORE_ITEMS["enchantments"]:
                                ench_effect = STORE_ITEMS["enchantments"][enchantment]["effect"]
                                if "poison_damage" in ench_effect:
                                    poison_damage = min(ench_effect["poison_damage"], 0.05)
                        defender.status_effects.append(StatusEffect("Poison", 4, "poison", poison_damage))
                        self.battle_log.append(f"{defender.team_color} {defender.display_name} was poisoned! ☠️")

            for enchantment in attacker.enchantments:
                if enchantment in STORE_ITEMS["enchantments"]:
                    ench_effect = STORE_ITEMS["enchantments"][enchantment]["effect"]
                    
                    if enchantment == "fire" and "burn_chance" in ench_effect:
                        if random.random() < ench_effect["burn_chance"]:
                            defender.status_effects.append(StatusEffect("Burn", 3, "burn", 0.05))
                            self.battle_log.append(f"🔥 {attacker.team_color} {attacker.display_name}'s Flaming Aura burned {defender.team_color} {defender.display_name}!")
                    
                    elif enchantment == "ice" and "freeze_chance" in ench_effect:
                        if random.random() < ench_effect["freeze_chance"]:
                            defender.stat_modifiers["speed"] = max(0.3, defender.stat_modifiers["speed"] - 0.3)
                            self.battle_log.append(f"❄️ {attacker.team_color} {attacker.display_name}'s Frostbite slowed {defender.team_color} {defender.display_name}!")
                    
                    elif enchantment == "poison" and "poison_chance" in ench_effect:
                        if random.random() < ench_effect["poison_chance"]:
                            poison_dmg = ench_effect.get("poison_damage", 0.03)
                            defender.status_effects.append(StatusEffect("Poison", 4, "poison", poison_dmg))
                            self.battle_log.append(f"☠️ {attacker.team_color} {attacker.display_name}'s Toxic Venom poisoned {defender.team_color} {defender.display_name}!")
    
    async def update_battle_embed(self):
        embed = discord.Embed(title="⚔️ Team Battle in Progress", description=f"🔴 {self.p1_name} vs 🔵 {self.p2_name}", color=0xff9900)
        
        # Get current active creatures
        p1_current = self.p1_team[self.p1_current] if self.p1_current < len(self.p1_team) else None
        p2_current = self.p2_team[self.p2_current] if self.p2_current < len(self.p2_team) else None
        
        if p1_current:
            p1_hp_bar = self.create_hp_bar(p1_current.current_hp, p1_current.max_hp)
            status_text = ""
            if p1_current.shield_turns > 0:
                status_text += f"🛡️({p1_current.shield_turns}) "
            if p1_current.fear_turns > 0:
                status_text += f"😱({p1_current.fear_turns}) "
            if p1_current.speed_boost_active:
                status_text += f"💨(Speed) "
            embed.add_field(name=f"🔴 {p1_current.display_name} [{p1_current.creature_type}]", value=f"{p1_hp_bar}\n{p1_current.current_hp}/{p1_current.max_hp} HP\nATK: {p1_current.get_effective_attack()} | DEF: {p1_current.get_effective_defense()} | SPD: {p1_current.get_effective_speed()}\n{status_text}", inline=True)
        
        if p2_current:
            p2_hp_bar = self.create_hp_bar(p2_current.current_hp, p2_current.max_hp)
            status_text = ""
            if p2_current.shield_turns > 0:
                status_text += f"🛡️({p2_current.shield_turns}) "
            if p2_current.fear_turns > 0:
                status_text += f"😱({p2_current.fear_turns}) "
            if p2_current.speed_boost_active:
                status_text += f"💨(Speed) "
            embed.add_field(name=f"🔵 {p2_current.display_name} [{p2_current.creature_type}]", value=f"{p2_hp_bar}\n{p2_current.current_hp}/{p2_current.max_hp} HP\nATK: {p2_current.get_effective_attack()} | DEF: {p2_current.get_effective_defense()} | SPD: {p2_current.get_effective_speed()}\n{status_text}", inline=True)
        
        # Update team status to show correct active creature numbers
        p1_status = f"Active: {self.p1_current + 1}/{len(self.p1_team)}"
        p2_status = f"Active: {self.p2_current + 1}/{len(self.p2_team)}"
        embed.add_field(name="Team Status", value=f"🔴 {p1_status}\n🔵 {p2_status}", inline=True)
        
        log_text = "\n".join(self.battle_log[-8:]) if self.battle_log else "Team battle begins!"
        embed.add_field(name="Battle Log", value=log_text, inline=False)
        await self.message.edit(embed=embed)
    
    def create_hp_bar(self, current_hp, max_hp):
        percentage = current_hp / max_hp
        filled_blocks = int(percentage * 10)
        empty_blocks = 10 - filled_blocks
        bar_color = "🟩" if percentage > 0.6 else "🟨" if percentage > 0.3 else "🟥"
        return bar_color * filled_blocks + "⬜" * empty_blocks

class UserData:
    def __init__(self):
        self.catches, self.last_gamba, self.last_battle, self.last_daily = [], None, None, None
        self.daily_streak, self.upgrades, self.enchantments, self.cosmetics, self.consumables = 0, {}, [], [], {}
        self.balance, self.battles_won, self.battles_lost, self.total_earned, self.lootboxes = STARTING_BALANCE, 0, 0, 0, {}
        self.battle_team = []
        self.tournament_wins = 0
        self.tournament_placings = []  # List of (date, place)
        self.battle_available = False  # New flag for battle opt-in
        self.battle_training = 0  # Add battle training attribute

class Guild:
    def __init__(self, name, owner_id):
        self.name = name
        self.owner_id = owner_id
        self.members = [owner_id]
        self.level = 1
        self.xp = 0
        self.treasury = 0
        self.created_at = datetime.now(timezone.utc).isoformat()
        self.description = f"A guild created by <@{owner_id}>"
        self.perks = {}
        self.last_contribution = {}

def get_recent_players():
    """Get list of players active in the last 24 hours"""
    current_time = datetime.now(timezone.utc)
    return [uid for uid, data in user_data.items() 
            if data.last_interaction and 
            (current_time - data.last_interaction).total_seconds() <= RECENT_PLAYERS_WINDOW]

def update_user_activity(user_id):
    """Update user's last interaction time"""
    if user_id in user_data:
        user_data[user_id].last_interaction = datetime.now(timezone.utc)
        save_data()

@bot.event
async def on_command(ctx):
    """Track user activity on any command"""
    update_user_activity(str(ctx.author.id))

@bot.command()
async def battles(ctx, setting: str = None):
    """Toggle battle availability"""
    user_id = str(ctx.author.id)
    data = user_data[user_id]
    
    if not setting:
        status = "enabled" if data.battle_available else "disabled"
        return await ctx.send(f"Your battle availability is currently {status}. Use `!battles on` or `!battles off` to change.")
    
    if setting.lower() not in ["on", "off"]:
        return await ctx.send("Invalid setting! Use `!battles on` or `!battles off`")
    
    data.battle_available = (setting.lower() == "on")
    status = "enabled" if data.battle_available else "disabled"
    await ctx.send(f"Battle availability {status}!")
    save_data()

@bot.command()
async def battle(ctx):
    user_id = str(ctx.author.id)
    data = user_data[user_id]
    
    # Prevent concurrent battles
    if user_id in active_battles:
        return await ctx.send("🚫 You are already in a battle! Wait for it to finish before starting another.")
    
    # Check if user has battles enabled
    if not data.battle_available:
        return await ctx.send("🚫 You have battles disabled! Use `!battles on` to enable them.")
    
    # Check if user is in battle cooldown
    if data.last_battle and (datetime.now(timezone.utc) - data.last_battle).total_seconds() < BATTLE_COOLDOWN:
        remaining = timedelta(seconds=BATTLE_COOLDOWN - (datetime.now(timezone.utc) - data.last_battle).total_seconds())
        return await ctx.send(f"⏳ You can battle again in {remaining}!")
    
    # Check if user has enough creatures
    if len(data.catches) < 3:
        return await ctx.send("❌ You need at least 3 creatures to battle!")
    
    # Get available opponents
    available_opponents = []
    for opponent_id, opponent_data in user_data.items():
        if opponent_id == user_id:
            continue
        
        # Skip if opponent has battles disabled
        if not opponent_data.battle_available:
            continue
            
        # Skip if opponent has fewer than 3 creatures
        if len(opponent_data.catches) < 3:
            continue
            
        # Prevent concurrent battles for opponent
        if opponent_id in active_battles:
            continue
        
        # Add opponent to available list with priority
        priority = 0
        if opponent_data.battle_team and len(opponent_data.battle_team) == 3:
            priority = 2  # Highest priority for players with teams set up
        elif len(opponent_data.catches) >= 3:
            priority = 1  # Lower priority for players with enough creatures but no team
            
        available_opponents.append((opponent_id, priority))
    
    if not available_opponents:
        return await ctx.send("❌ No opponents available! Make sure other players have battles enabled and are not already in a battle.")
    
    # Sort opponents by priority (highest first)
    available_opponents.sort(key=lambda x: x[1], reverse=True)
    
    # Select opponent from highest priority group
    highest_priority = available_opponents[0][1]
    high_priority_opponents = [opp for opp in available_opponents if opp[1] == highest_priority]
    opponent_id = random.choice(high_priority_opponents)[0]
    opponent = await bot.fetch_user(int(opponent_id))
    opponent_data = user_data[opponent_id]
    
    # Add both users to active_battles
    active_battles.add(user_id)
    active_battles.add(opponent_id)
    try:
        # Create teams
        async def create_safe_battle_team(user_data, display_name):
            # Only use indices that are valid
            valid_indices = [idx for idx in (user_data.battle_team if user_data.battle_team else []) if 0 <= idx < len(user_data.catches)]
            # If we have 3 valid indices, use them
            if len(valid_indices) == 3:
                return [BattleCreature(user_data.catches[idx], display_name) for idx in valid_indices]
            else:
                # Fill with strongest available creatures not already in valid_indices
                available = [i for i in range(len(user_data.catches)) if i not in valid_indices]
                needed = 3 - len(valid_indices)
                # Sort available by value
                available_sorted = sorted(available, key=lambda i: user_data.catches[i]["value"], reverse=True)
                fill_indices = valid_indices + available_sorted[:needed]
                return [BattleCreature(user_data.catches[idx], display_name) for idx in fill_indices]
        
        p1_team = await create_safe_battle_team(data, ctx.author.display_name)
        p2_team = await create_safe_battle_team(opponent_data, opponent.display_name)
        
        # Start battle
        battle_system = TeamBattleSystem(p1_team, p2_team, ctx.author.display_name, opponent.display_name, ctx)
        winner_name, winner_team = await battle_system.start_battle()
        
        # Update battle stats and rewards
        winner_data = data if winner_name == ctx.author.display_name else opponent_data
        loser_data = opponent_data if winner_name == ctx.author.display_name else data
        
        # Calculate rewards
        loser_team_value = sum(creature["value"] for creature in loser_data.catches)
        base_reward = int(loser_team_value * 0.15)  # 15% of loser's team value
        
        # Add battle training bonus
        training_bonus = 0
        battle_training_level = winner_data.upgrades.get("battle_training", 0)
        if battle_training_level > 0:
            training_bonus = int(base_reward * (battle_training_level * 0.05))  # 5% per level
        
        # Add guild bonus if applicable
        guild_bonus = 0
        winner_id = None
        # Find the user_id for winner_data
        for uid, d in user_data.items():
            if d is winner_data:
                winner_id = uid
                break
        guild_name = user_guilds.get(winner_id)
        if guild_name and guild_name in guilds:
            guild = guilds[guild_name]
            battle_bonus_level = guild.perks.get("battle_bonus", 0)
            if battle_bonus_level > 0:
                guild_bonus = int(base_reward * (battle_bonus_level * 0.05))  # 5% per level
        
        total_reward = base_reward + training_bonus + guild_bonus
        winner_data.balance += total_reward
        winner_data.total_earned += total_reward
        winner_data.battles_won += 1
        loser_data.battles_lost += 1
        
        # Give loser a small participation reward
        base_compensation = int(total_reward * 0.2)  # 20% of winner's reward
        
        # Add battle training bonus to compensation
        loser_training_bonus = 0
        loser_battle_training_level = loser_data.upgrades.get("battle_training", 0)
        if loser_battle_training_level > 0:
            loser_training_bonus = int(base_compensation * (loser_battle_training_level * 0.05))  # 5% per level
        
        # Add guild bonus to compensation if applicable
        loser_guild_bonus = 0
        loser_id = None
        for uid, d in user_data.items():
            if d is loser_data:
                loser_id = uid
                break
        loser_guild_name = user_guilds.get(loser_id)
        if loser_guild_name and loser_guild_name in guilds:
            loser_guild = guilds[loser_guild_name]
            loser_battle_bonus_level = loser_guild.perks.get("battle_bonus", 0)
            if loser_battle_bonus_level > 0:
                loser_guild_bonus = int(base_compensation * (loser_battle_bonus_level * 0.05))  # 5% per level
        
        total_compensation = base_compensation + loser_training_bonus + loser_guild_bonus
        loser_data.balance += total_compensation
        loser_data.total_earned += total_compensation
        
        # Update last battle time only for the initiator
        data.last_battle = datetime.now(timezone.utc)
        
        # Create reward embed
        winner_user = ctx.author if winner_name == ctx.author.display_name else opponent
        reward_embed = create_embed("🏆 Battle Results", f"{winner_user.display_name} won the battle!")
        
        # Winner's reward details
        reward_text = f"Base Reward: ${base_reward:,}\n"
        if training_bonus > 0:
            reward_text += f"Training Bonus: ${training_bonus:,} (Battle Training Level {battle_training_level}: +{battle_training_level * 5}%)\n"
        if guild_bonus > 0:
            reward_text += f"Guild Bonus: ${guild_bonus:,} (Guild Battle Bonus Level {battle_bonus_level}: +{battle_bonus_level * 5}%)\n"
        reward_text += f"Total Reward: ${total_reward:,}\n"
        reward_text += f"New Balance: ${winner_data.balance:,}"
        
        reward_embed.add_field(name="Winner's Reward", value=reward_text, inline=False)
        
        # Loser's reward details
        loser_text = f"Base Compensation: ${base_compensation:,}\n"
        if loser_training_bonus > 0:
            loser_text += f"Training Bonus: ${loser_training_bonus:,} (Battle Training Level {loser_battle_training_level}: +{loser_battle_training_level * 5}%)\n"
        if loser_guild_bonus > 0:
            loser_text += f"Guild Bonus: ${loser_guild_bonus:,} (Guild Battle Bonus Level {loser_battle_bonus_level}: +{loser_battle_bonus_level * 5}%)\n"
        loser_text += f"Total Compensation: ${total_compensation:,}\n"
        loser_text += f"New Balance: ${loser_data.balance:,}"
        
        reward_embed.add_field(name="Loser's Compensation", value=loser_text, inline=False)
        
        await ctx.send(embed=reward_embed)
        save_data()
    finally:
        # Always remove both users from active_battles
        active_battles.discard(user_id)
        active_battles.discard(opponent_id)

user_data = defaultdict(UserData)
guild_data = {}  # Initialize guild_data dictionary
guilds = {}
user_guilds = {}
active_trades = {}

# --- Prevent concurrent battles ---
active_battles = set()

def save_data():
    import builtins
    with builtins.open("user_data.json", "w") as f:
        json.dump({user_id: {"catches": data.catches, "last_gamba": data.last_gamba.isoformat() if data.last_gamba else None, "last_battle": data.last_battle.isoformat() if data.last_battle else None, "last_daily": data.last_daily.isoformat() if data.last_daily else None, "daily_streak": data.daily_streak, "upgrades": data.upgrades, "enchantments": data.enchantments, "cosmetics": data.cosmetics, "consumables": data.consumables, "lootboxes": data.lootboxes, "balance": data.balance, "battles_won": data.battles_won, "battles_lost": data.battles_lost, "total_earned": data.total_earned, "battle_team": getattr(data, 'battle_team', []), "tournament_wins": getattr(data, 'tournament_wins', 0), "tournament_placings": data.tournament_placings, "battle_available": getattr(data, 'battle_available', False)} for user_id, data in user_data.items()}, f)
    # Save tournament data
    with builtins.open("tournament_data.json", "w") as f:
        json.dump({
            "entrants": tournament_data['entrants'],
            "pot": tournament_data['pot'],
            "active": tournament_data['active'],
            "in_progress": tournament_data['in_progress'],
            "last_placings": tournament_data['last_placings'],
            "last_winner": tournament_data.get('last_winner'),
            "results": tournament_data.get('results', [])
        }, f)

def load_data():
    import builtins
    try:
        with builtins.open("user_data.json", "r") as f:
            data = json.load(f)
            for user_id, info in data.items():
                def aware(dt):
                    if dt is None:
                        return None
                    if dt.tzinfo is None:
                        return dt.replace(tzinfo=timezone.utc)
                    return dt
                user = user_data[user_id]
                user.catches = info.get("catches", [])
                user.last_gamba = aware(datetime.fromisoformat(info["last_gamba"])) if info.get("last_gamba") else None
                user.last_battle = aware(datetime.fromisoformat(info["last_battle"])) if info.get("last_battle") else None
                user.last_daily = aware(datetime.fromisoformat(info["last_daily"])) if info.get("last_daily") else None
                user.daily_streak, user.upgrades, user.enchantments, user.cosmetics, user.consumables = info.get("daily_streak", 0), info.get("upgrades", {}), info.get("enchantments", []), info.get("cosmetics", []), info.get("consumables", {})
                user.lootboxes, user.balance, user.battles_won, user.battles_lost, user.total_earned = info.get("lootboxes", {}), info.get("balance", STARTING_BALANCE), info.get("battles_won", 0), info.get("battles_lost", 0), info.get("total_earned", 0)
                user.battle_team = info.get("battle_team", [])
                user.tournament_wins = info.get("tournament_wins", 0)
                user.tournament_placings = info.get("tournament_placings", [])
                user.battle_available = info.get("battle_available", False)
        # Load tournament data
        try:
            with builtins.open("tournament_data.json", "r") as f:
                tdata = json.load(f)
                tournament_data['entrants'] = tdata.get('entrants', [])
                tournament_data['pot'] = tdata.get('pot', 0)
                tournament_data['active'] = tdata.get('active', False)
                tournament_data['in_progress'] = tdata.get('in_progress', False)
                tournament_data['last_placings'] = tdata.get('last_placings', [])
                tournament_data['last_winner'] = tdata.get('last_winner')
                tournament_data['results'] = tdata.get('results', [])
        except (FileNotFoundError, json.JSONDecodeError):
            pass
        print(f"Loaded data for {len(user_data)} users")
    except (FileNotFoundError, json.JSONDecodeError): print("Starting with fresh data")

def save_guild_data():
    import builtins
    with builtins.open("guild_data.json", "w") as f:
        json.dump({"guilds": {name: {"name": guild.name, "owner_id": guild.owner_id, "members": guild.members, "level": guild.level, "xp": guild.xp, "treasury": guild.treasury, "created_at": guild.created_at, "description": guild.description, "perks": guild.perks, "last_contribution": guild.last_contribution} for name, guild in guilds.items()}, "user_guilds": user_guilds}, f)

def load_guild_data():
    import builtins
    try:
        with builtins.open("guild_data.json", "r") as f:
            data = json.load(f)
            global guild_data
            guild_data = data.get("guilds", {})
            for name, guild_info in guild_data.items():
                guild = Guild(name, guild_info["owner_id"])
                guild.members = guild_info.get("members", [guild_info["owner_id"]])
                guild.level = guild_info.get("level", 1)
                guild.xp = guild_info.get("xp", 0)
                guild.treasury = guild_info.get("treasury", 0)
                guild.created_at = guild_info.get("created_at", datetime.now(timezone.utc).isoformat())
                guild.description = guild_info.get("description", f"A guild created by <@{guild_info['owner_id']}>")
                guild.perks = guild_info.get("perks", {})
                guild.last_contribution = guild_info.get("last_contribution", {})
                guilds[name] = guild
            user_guild_data = data.get("user_guilds", {})
            for user_id, guild_name in user_guild_data.items():
                user_guilds[user_id] = guild_name
        print(f"Loaded {len(guilds)} guilds")
    except (FileNotFoundError, json.JSONDecodeError):
        print("No guild data found, starting fresh")
        guild_data = {}  # Initialize empty guild_data if no file exists

def open_lootbox(lootbox_type, user_data, user_id):
    """Generate lootbox contents based on type"""
    rewards = []
    
    luck_multiplier = 1.0
    if "amulet" in user_data.cosmetics:
        luck_multiplier = STORE_ITEMS["cosmetics"]["amulet"]["effect"]["lootbox_luck"]
    
    if lootbox_type == "basic":
        money = random.randint(5000, 15000)
        rewards.append(("money", money))
        
        if random.random() < (0.6 * luck_multiplier):
            consumable = random.choice(["elixir", "reroll"])
            rewards.append(("consumable", consumable))
        
        if random.random() < (0.3 * luck_multiplier):
            enchantment = random.choice(["fire", "ice", "poison"])
            rewards.append(("enchantment", enchantment))
    
    elif lootbox_type == "premium":
        money = random.randint(15000, 35000)
        rewards.append(("money", money))
        
        if random.random() < (0.8 * luck_multiplier):
            consumable = random.choice(["elixir", "reroll", "stat_reset"])
            rewards.append(("consumable", consumable))
        
        if random.random() < (0.5 * luck_multiplier):
            enchantment = random.choice(["fire", "ice", "vampire", "poison", "stealth"])
            rewards.append(("enchantment", enchantment))
        
        if random.random() < (0.25 * luck_multiplier):
            cosmetic = random.choice(["glasses", "scarf", "cape"])
            rewards.append(("cosmetic", cosmetic))
    
    elif lootbox_type == "deluxe":
        money = random.randint(30000, 60000)
        rewards.append(("money", money))
        
        consumable = random.choice(["elixir", "reroll", "stat_reset"])
        rewards.append(("consumable", consumable))
        
        if random.random() < (0.7 * luck_multiplier):
            enchantment = random.choice(["fire", "ice", "vampire", "lightning", "poison", "stealth", "critical"])
            rewards.append(("enchantment", enchantment))
        
        if random.random() < (0.4 * luck_multiplier):
            cosmetic = random.choice(["hat", "glasses", "scarf", "armor", "cape", "amulet"])
            rewards.append(("cosmetic", cosmetic))
    
    elif lootbox_type == "legendary":
        money = random.randint(75000, 150000)
        rewards.append(("money", money))
        
        consumable = random.choice(["reroll", "stat_reset", "revive"])
        rewards.append(("consumable", consumable))
        
        enchantment = random.choice(["vampire", "lightning", "critical", "regeneration"])
        rewards.append(("enchantment", enchantment))
        
        cosmetic = random.choice(["hat", "armor", "cape", "amulet"])
        rewards.append(("cosmetic", cosmetic))
        
        if random.random() < (0.15 * luck_multiplier):
            if random.random() < 0.5:
                rewards.append(("cosmetic", "ring"))
            else:
                rewards.append(("money", random.randint(100000, 200000)))
    
    return rewards

@bot.event
async def on_ready():
    print(f'{bot.user} has connected to Discord!')
    load_data()
    load_guild_data()
    auto_save.start()
    setup_tournament_scheduler()
    # Ensure a tournament is always open for entry unless in progress
    if not tournament_data['active'] and not tournament_data['in_progress']:
        reset_tournament()
    start_tournament_reminders()

@tasks.loop(seconds=SAVE_INTERVAL)
async def auto_save():
    save_data()
    save_guild_data()

def create_embed(title, description="", color=0x00ff00):
    return discord.Embed(title=title, description=description, color=color)

def generate_catch(user_id=None):
    creature_type = random.choices(list(CREATURE_TYPES.keys()), weights=[RARITY_TIERS[stats["rarity"]][1] for stats in CREATURE_TYPES.values()])[0]
    stats = CREATURE_TYPES[creature_type]
    size = random.uniform(*stats["size_range"])
    value = stats["base_value"] * size
    
    if user_id:
        data = user_data[user_id]
        value *= 1 + (0.08 * data.upgrades.get("net", 0))
        if user_id in user_guilds:
            guild_name = user_guilds[user_id]
            guild = guilds[guild_name]
            catch_bonus_level = guild.perks.get("catch_bonus", 0)
            if catch_bonus_level > 0: value *= 1 + (0.02 * catch_bonus_level)
        treasure_level = data.upgrades.get("treasure_hunter", 0)
        if treasure_level > 0 and random.random() < (0.05 * treasure_level):
            bonus_money = random.randint(1000, 5000)
            data.balance += bonus_money
    
    display_name = f"{random.choice(FANTASY_ADJECTIVES)} {creature_type}"
    
    applied_mods, emoji_modifiers = [], []
    base_chance = 0.7
    if user_id:
        luck_level = user_data[user_id].upgrades.get("luck", 0)
        base_chance += (0.005 * luck_level)
    
    num_mods = 1 if random.random() < base_chance else 2
    if stats["rarity"] in ["Rare", "Epic"] and random.random() < 0.2: num_mods = 3
    if stats["rarity"] in ["Legendary", "Mythic"]: num_mods = random.randint(3, 5)
    
    available_modifiers = MODIFIERS.copy()
    for _ in range(num_mods):
        if not available_modifiers: break
        mod = random.choices([m[0] for m in available_modifiers], weights=[RARITY_TIERS[m[3]][1] for m in available_modifiers])[0]
        mod_data = next(m for m in available_modifiers if m[0] == mod)
        available_modifiers.remove(mod_data)
        value *= mod_data[1]
        applied_mods.append(mod)
        emoji_modifiers.append(mod_data[2])
    
    return {"type": creature_type, "display_name": display_name, "size": round(size, 2), "value": int(value), "modifiers": applied_mods, "emoji_modifiers": emoji_modifiers, "emoji": stats["emoji"], "caught_at": datetime.now(timezone.utc).isoformat(), "rarity": stats["rarity"], "cosmetics": [], "enchantments": []}

@bot.command()
async def use(ctx, consumable_name: str = None, creature_index: int = None):
    user_id = str(ctx.author.id)
    data = user_data[user_id]
    
    if not consumable_name:
        return await ctx.send("Usage: `!use <consumable_name> [creature_number]`\nAvailable consumables: elixir, revive, reroll, stat_reset")
    
    consumable_name = consumable_name.lower()
    
    consumable_id = None
    for item_id, item_data in STORE_ITEMS["consumables"].items():
        if (item_id.lower() == consumable_name or 
            item_data["name"].lower() == consumable_name or 
            consumable_name in [k.lower() for k in item_data.get("keywords", [])]):
            consumable_id = item_id
            break
    
    if not consumable_id:
        return await ctx.send(f"Consumable '{consumable_name}' not found! Available: {', '.join(STORE_ITEMS['consumables'].keys())}")
    
    if consumable_id not in data.consumables or data.consumables[consumable_id] <= 0:
        return await ctx.send(f"You don't have any {STORE_ITEMS['consumables'][consumable_id]['name']}!")
    
    consumable_data = STORE_ITEMS["consumables"][consumable_id]
    
    if not creature_index:
        return await ctx.send(f"Usage: `!use {consumable_name} <creature_number>`\nSpecify which creature to use it on!")
    
    if creature_index < 1 or creature_index > len(data.catches):
        return await ctx.send(f"Invalid creature number! You have {len(data.catches)} creatures.")
    
    creature = data.catches[creature_index - 1]
    
    if consumable_id == "revive":
        embed = create_embed("💎 Revive Crystal Used!", f"Used on {creature['emoji']} {creature.get('display_name', creature['type'])}")
        embed.add_field(name="Effect", value="This creature is now protected from death in the next battle!", inline=False)
        
    elif consumable_id == "elixir":
        old_value = creature["value"]
        creature["value"] = int(creature["value"] * 1.15)
        
        embed = create_embed("⚗️ Value Elixir Used!", f"Used on {creature['emoji']} {creature.get('display_name', creature['type'])}")
        embed.add_field(name="Value Change", value=f"${old_value:,} → ${creature['value']:,}", inline=True)
        
    elif consumable_id == "reroll":
        stats = CREATURE_TYPES[creature["type"]]
        num_mods = len(creature.get("modifiers", []))
        if num_mods == 0: num_mods = 1
        
        new_mods, new_emojis = [], []
        available_modifiers = MODIFIERS.copy()
        base_value = stats["base_value"] * creature["size"]
        
        for _ in range(num_mods):
            if not available_modifiers: break
            mod = random.choices([m[0] for m in available_modifiers], weights=[RARITY_TIERS[m[3]][1] for m in available_modifiers])[0]
            mod_data = next(m for m in available_modifiers if m[0] == mod)
            available_modifiers.remove(mod_data)
            base_value *= mod_data[1]
            new_mods.append(mod)
            new_emojis.append(mod_data[2])
        
        old_mods = " ".join(creature.get("emoji_modifiers", []))
        new_mod_display = " ".join(new_emojis)
        
        creature["modifiers"] = new_mods
        creature["emoji_modifiers"] = new_emojis
        creature["value"] = int(base_value)
        
        embed = create_embed("🎲 Modifier Reroll Used!", f"Used on {creature['emoji']} {creature.get('display_name', creature['type'])}")
        embed.add_field(name="Old Modifiers", value=old_mods if old_mods else "None", inline=True)
        embed.add_field(name="New Modifiers", value=new_mod_display if new_mod_display else "None", inline=True)
        embed.add_field(name="New Value", value=f"${creature['value']:,}", inline=True)
        
    elif consumable_id == "stat_reset":
        # Get base stats from creature type
        base_stats = CREATURE_TYPES[creature["type"]]
        size_multiplier = 1 + (creature["size"] - 1) * 0.05
        
        # Calculate total stat points
        total_points = base_stats["hp"] + base_stats["attack"] + base_stats["defense"] + base_stats["speed"]
        
        # Redistribute stats with focus on speed
        new_hp = int(base_stats["hp"] * 0.8 * size_multiplier)  # Reduce HP by 20%
        new_attack = int(base_stats["attack"] * 0.9 * size_multiplier)  # Reduce attack by 10%
        new_defense = int(base_stats["defense"] * 0.9 * size_multiplier)  # Reduce defense by 10%
        new_speed = int(base_stats["speed"] * 1.4 * size_multiplier)  # Increase speed by 40%
        
        # Update creature stats
        creature["hp"] = new_hp
        creature["attack"] = new_attack
        creature["defense"] = new_defense
        creature["speed"] = new_speed
        
        embed = create_embed("📊 Stat Reset Used!", f"Used on {creature['emoji']} {creature.get('display_name', creature['type'])}")
        embed.add_field(name="New Stats", value=f"HP: {new_hp}\nAttack: {new_attack}\nDefense: {new_defense}\nSpeed: {new_speed}", inline=False)
    
    data.consumables[consumable_id] -= 1
    
    await ctx.send(embed=embed)
    save_data()

@bot.command()
async def open(ctx, lootbox_type: str = None):
    user_id = str(ctx.author.id)
    data = user_data[user_id]
    
    if not lootbox_type:
        return await ctx.send("Usage: `!open <lootbox_type>`\nAvailable types: basic, premium, deluxe, legendary")
    
    lootbox_type = lootbox_type.lower()
    if lootbox_type not in STORE_ITEMS["lootboxes"]:
        return await ctx.send(f"Invalid lootbox type! Available: {', '.join(STORE_ITEMS['lootboxes'].keys())}")
    
    if lootbox_type not in data.lootboxes or data.lootboxes[lootbox_type] <= 0:
        return await ctx.send(f"You don't have any {lootbox_type} lootboxes! Buy some from the store first.")
    
    data.lootboxes[lootbox_type] -= 1
    
    rewards = open_lootbox(lootbox_type, data, user_id)
    
    reward_text = []
    total_value = 0
    
    for reward_type, reward_value in rewards:
        if reward_type == "money":
            data.balance += reward_value
            data.total_earned += reward_value
            total_value += reward_value
            reward_text.append(f"💰 ${reward_value:,}")
        elif reward_type == "consumable":
            data.consumables[reward_value] = data.consumables.get(reward_value, 0) + 1
            item_name = STORE_ITEMS["consumables"][reward_value]["name"]
            item_value = STORE_ITEMS["consumables"][reward_value]["price"]
            total_value += item_value
            reward_text.append(f"🧪 {item_name} (Value: ${item_value:,})")
        elif reward_type == "enchantment":
            data.enchantments.append(reward_value)
            item_name = STORE_ITEMS["enchantments"][reward_value]["name"]
            item_value = STORE_ITEMS["enchantments"][reward_value]["price"]
            total_value += item_value
            reward_text.append(f"✨ {item_name} (Value: ${item_value:,})")
        elif reward_type == "cosmetic":
            if reward_value not in data.cosmetics:
                data.cosmetics.append(reward_value)
                item_data = STORE_ITEMS["cosmetics"][reward_value]
                total_value += item_data["price"]
                reward_text.append(f"{item_data['emoji']} {item_data['name']} (Value: ${item_data['price']:,})")
            else:
                duplicate_value = STORE_ITEMS["cosmetics"][reward_value]["price"] // 2
                data.balance += duplicate_value
                data.total_earned += duplicate_value
                total_value += duplicate_value
                reward_text.append(f"💰 ${duplicate_value:,} (duplicate cosmetic)")
    
    lootbox_data = STORE_ITEMS["lootboxes"][lootbox_type]
    embed = create_embed(f"📦 {lootbox_data['name']} Opened!", f"You received rewards worth ${total_value:,}!")
    
    for i, reward in enumerate(reward_text, 1):
        embed.add_field(name=f"Reward {i}", value=reward, inline=True)
    
    embed.add_field(name="New Balance", value=f"${data.balance:,}", inline=False)
    embed.add_field(name="Remaining Lootboxes", value=f"{data.lootboxes.get(lootbox_type, 0)} {lootbox_type} left", inline=True)
    
    await ctx.send(embed=embed)
    save_data()

@bot.command()
async def admin_give_money(ctx, user: discord.Member, amount: int):
    if ctx.author.id != ADMIN_ID:
        return await ctx.send("🚫 You don't have permission to use this command!")
    
    user_id = str(user.id)
    user_data[user_id].balance += amount
    embed = create_embed("💰 Admin: Money Given", f"Gave ${amount:,} to {user.display_name}")
    embed.add_field(name="New Balance", value=f"${user_data[user_id].balance:,}", inline=True)
    await ctx.send(embed=embed)
    save_data()

@bot.command()
async def admin_stats(ctx, user: discord.Member = None):
    if ctx.author.id != ADMIN_ID:
        return await ctx.send("🚫 You don't have permission to use this command!")
    
    if user:
        user_id = str(user.id)
        data = user_data[user_id]
        embed = create_embed(f"📊 Admin Stats: {user.display_name}")
        embed.add_field(name="Balance", value=f"${data.balance:,}", inline=True)
        embed.add_field(name="Creatures", value=f"{len(data.catches)}", inline=True)
        embed.add_field(name="Total Earned", value=f"${data.total_earned:,}", inline=True)
        embed.add_field(name="Battles", value=f"{data.battles_won}W/{data.battles_lost}L", inline=True)
        embed.add_field(name="Daily Streak", value=f"{data.daily_streak} days", inline=True)
        if data.catches:
            total_value = sum(c["value"] for c in data.catches)
            embed.add_field(name="Collection Value", value=f"${total_value:,}", inline=True)
    else:
        embed = create_embed("📊 Admin: Global Stats")
        total_users = len(user_data)
        total_creatures = sum(len(data.catches) for data in user_data.values())
        total_balance = sum(data.balance for data in user_data.values())
        embed.add_field(name="Total Users", value=f"{total_users:,}", inline=True)
        embed.add_field(name="Total Creatures", value=f"{total_creatures:,}", inline=True)
        embed.add_field(name="Total Money", value=f"${total_balance:,}", inline=True)
        embed.add_field(name="Total Guilds", value=f"{len(guilds)}", inline=True)
    await ctx.send(embed=embed)

@bot.command()
async def trade(ctx, user: discord.Member, offer_type: str, offer_item: str, request_type: str, request_item: str):
    if ctx.author.id == user.id:
        return await ctx.send("🚫 You can't trade with yourself!")
    
    user1_id, user2_id = str(ctx.author.id), str(user.id)
    user1_data, user2_data = user_data[user1_id], user_data[user2_id]
    
    offer_value = 0
    if offer_type.lower() == "money":
        try:
            offer_amount = int(offer_item)
            if offer_amount <= 0:
                return await ctx.send("🚫 You must offer a positive amount of money!")
            if user1_data.balance < offer_amount:
                return await ctx.send(f"🚫 You don't have ${offer_amount:,}!")
            offer_value = offer_amount
            offer_desc = f"${offer_amount:,}"
        except ValueError:
            return await ctx.send("🚫 Invalid money amount!")
    elif offer_type.lower() == "creature":
        try:
            creature_idx = int(offer_item) - 1
            if creature_idx < 0 or creature_idx >= len(user1_data.catches):
                return await ctx.send(f"🚫 Invalid creature number! You have {len(user1_data.catches)} creatures.")
            creature = user1_data.catches[creature_idx]
            offer_value = creature["value"]
            offer_desc = f"{creature['emoji']} {creature.get('display_name', creature['type'])}"
        except ValueError:
            return await ctx.send("🚫 Invalid creature number!")
    else:
        return await ctx.send("🚫 Offer type must be 'money' or 'creature'!")
    
    request_value = 0
    if request_type.lower() == "money":
        try:
            request_amount = int(request_item)
            if request_amount <= 0:
                return await ctx.send("🚫 You must request a positive amount of money!")
            if user2_data.balance < request_amount:
                return await ctx.send(f"🚫 {user.display_name} doesn't have ${request_amount:,}!")
            request_value = request_amount
            request_desc = f"${request_amount:,}"
        except ValueError:
            return await ctx.send("🚫 Invalid money amount!")
    elif request_type.lower() == "creature":
        try:
            creature_idx = int(request_item) - 1
            if creature_idx < 0 or creature_idx >= len(user2_data.catches):
                return await ctx.send(f"🚫 {user.display_name} doesn't have creature #{creature_idx + 1}!")
            creature = user2_data.catches[creature_idx]
            request_value = creature["value"]
            request_desc = f"{creature['emoji']} {creature.get('display_name', creature['type'])}"
        except ValueError:
            return await ctx.send("🚫 Invalid creature number!")
    else:
        return await ctx.send("🚫 Request type must be 'money' or 'creature'!")
    
    higher_value = max(offer_value, request_value)
    tax = int(higher_value * 0.05)
    
    embed = create_embed("🤝 Trade Proposal", f"{ctx.author.display_name} wants to trade with {user.display_name}")
    
    # Format offer details
    if offer_type.lower() == "money":
        offer_details = f"💰 ${int(offer_item):,}"
    else:
        creature_idx = int(offer_item) - 1
        creature = user1_data.catches[creature_idx]
        offer_details = f"{creature['emoji']} {creature.get('display_name', creature['type'])}\n"
        offer_details += f"Value: ${creature['value']:,}\n"
        if creature.get("modifiers"):
            offer_details += f"Modifiers: {' '.join(creature.get('emoji_modifiers', []))}\n"
        offer_details += f"Stats: HP:{creature.get('hp', 'N/A')} ATK:{creature.get('attack', 'N/A')} DEF:{creature.get('defense', 'N/A')} SPD:{creature.get('speed', 'N/A')}"
    
    # Format request details
    if request_type.lower() == "money":
        request_details = f"💰 ${int(request_item):,}"
    else:
        creature_idx = int(request_item) - 1
        creature = user2_data.catches[creature_idx]
        request_details = f"{creature['emoji']} {creature.get('display_name', creature['type'])}\n"
        request_details += f"Value: ${creature['value']:,}\n"
        if creature.get("modifiers"):
            request_details += f"Modifiers: {' '.join(creature.get('emoji_modifiers', []))}\n"
        request_details += f"Stats: HP:{creature.get('hp', 'N/A')} ATK:{creature.get('attack', 'N/A')} DEF:{creature.get('defense', 'N/A')} SPD:{creature.get('speed', 'N/A')}"
    
    embed.add_field(name=f"{ctx.author.display_name} Offers", value=offer_details, inline=True)
    embed.add_field(name=f"{user.display_name} Gets", value=request_details, inline=True)
    embed.add_field(name="Tax", value=f"${tax:,} (5% of higher value)", inline=True)
    embed.add_field(name="Instructions", value=f"{user.display_name}, react with ✅ to accept or ❌ to decline", inline=False)
    
    message = await ctx.send(embed=embed)
    await message.add_reaction("✅")
    await message.add_reaction("❌")
    
    trade_id = f"{user1_id}_{user2_id}_{message.id}"
    active_trades[trade_id] = {
        "user1_id": user1_id,
        "user2_id": user2_id,
        "offer_type": offer_type.lower(),
        "offer_item": offer_item,
        "request_type": request_type.lower(),
        "request_item": request_item,
        "tax": tax,
        "message_id": message.id
    }
    
    def check(reaction, reaction_user):
        return (reaction_user.id == user.id and 
                str(reaction.emoji) in ["✅", "❌"] and 
                reaction.message.id == message.id)
    
    try:
        reaction, reaction_user = await bot.wait_for("reaction_add", timeout=300.0, check=check)
        
        if str(reaction.emoji) == "✅":
            # Money offer
            if offer_type.lower() == "money":
                user1_data.balance -= int(offer_item)
                user2_data.balance += int(offer_item)
            else:
                creature_idx = int(offer_item) - 1
                traded_creature = user1_data.catches.pop(creature_idx)
                user2_data.catches.append(traded_creature)
            # Money request
            if request_type.lower() == "money":
                user2_data.balance -= int(request_item)
                user1_data.balance += int(request_item)
            else:
                creature_idx = int(request_item) - 1
                traded_creature = user2_data.catches.pop(creature_idx)
                user1_data.catches.append(traded_creature)
            # Tax
            user1_data.balance -= tax // 2
            user2_data.balance -= tax // 2
            # Ensure no negative balances
            if user1_data.balance < 0 or user2_data.balance < 0:
                # Rollback (very basic, just abort and warn)
                return await ctx.send("🚫 Trade would result in negative balance for one of the users. Trade cancelled.")
            embed = create_embed("✅ Trade Completed!", f"Trade between {ctx.author.display_name} and {user.display_name} successful!")
            embed.add_field(name="Tax Paid", value=f"${tax:,} (split between both users)", inline=True)
            await message.edit(embed=embed)
            save_data()
        else:
            embed = create_embed("❌ Trade Declined", f"{user.display_name} declined the trade.")
            await message.edit(embed=embed)
        
        try:
            await message.clear_reactions()
        except discord.Forbidden:
            pass
        if trade_id in active_trades:
            del active_trades[trade_id]
            
    except asyncio.TimeoutError:
        embed = create_embed("⏰ Trade Expired", "Trade timed out after 5 minutes.")
        await message.edit(embed=embed)
        try:
            await message.clear_reactions()
        except discord.Forbidden:
            pass
        if trade_id in active_trades:
            del active_trades[trade_id]

@bot.command(aliases=["catch"])
async def gamba(ctx):
    user_id = str(ctx.author.id)
    data = user_data[user_id]
    base_cooldown = CATCH_COOLDOWN
    efficiency_level = data.upgrades.get("efficiency", 0)
    cooldown_reduction = 1 - (0.05 * efficiency_level)
    for cosmetic in data.cosmetics:
        if cosmetic in STORE_ITEMS["cosmetics"]:
            effect = STORE_ITEMS["cosmetics"][cosmetic].get("effect", {})
            if "cooldown_reduction" in effect: cooldown_reduction *= (1 - effect["cooldown_reduction"])
    actual_cooldown = int(base_cooldown * cooldown_reduction)
    
    if data.last_gamba and (datetime.now(timezone.utc) - data.last_gamba).total_seconds() < actual_cooldown:
        remaining = timedelta(seconds=actual_cooldown - (datetime.now(timezone.utc) - data.last_gamba).total_seconds())
        return await ctx.send(f"🚫 Wait {remaining} before catching again!")
    
    max_catches = 50 + (data.upgrades.get("storage", 0) * 10)
    if len(data.catches) >= max_catches: return await ctx.send(f"Your collection is full ({len(data.catches)}/{max_catches})! Upgrade storage or sell creatures.")
    
    catch = generate_catch(user_id)
    data.catches.append(catch)
    data.last_gamba = datetime.now(timezone.utc)
    
    rarity_color = {"Common": 0x808080, "Uncommon": 0x00ff00, "Rare": 0x0080ff, "Epic": 0x8000ff, "Legendary": 0xff8000, "Mythic": 0xff0000}
    embed = create_embed(f"New {catch['display_name']} Catch!", f"Rarity: {catch['rarity']} | Type: {CREATURE_TYPES[catch['type']]['type']}", rarity_color.get(catch["rarity"], 0x00ff00))
    embed.add_field(name="Size", value=f"{catch['size']}m", inline=True)
    embed.add_field(name="Value", value=f"${catch['value']:,}", inline=True)
    if catch["modifiers"]: 
        modifier_display = " ".join([f"{emoji} {mod}" for mod, emoji in zip(catch["modifiers"], catch["emoji_modifiers"])])
        embed.add_field(name="Modifiers", value=modifier_display, inline=False)
    await ctx.send(embed=embed)

@bot.command(aliases=["bal"])
async def balance(ctx, user: discord.Member = None):
    target = user or ctx.author
    data = user_data[str(target.id)]
    embed = create_embed(f"💰 {target.display_name}'s Balance")
    embed.add_field(name="Cash", value=f"${data.balance:,}", inline=True)
    if data.catches:
        total_value = sum(c["value"] for c in data.catches)
        networth = data.balance + total_value
        embed.add_field(name="Collection Value", value=f"${total_value:,}", inline=True)
        embed.add_field(name="Net Worth", value=f"${networth:,}", inline=True)
    if data.battles_won or data.battles_lost:
        total = data.battles_won + data.battles_lost
        win_rate = (data.battles_won / total) * 100 if total > 0 else 0
        embed.add_field(name="Battles", value=f"{data.battles_won}W/{data.battles_lost}L ({win_rate:.1f}%)", inline=False)
    # Tournament stats
    embed.add_field(name="Tournament Wins", value=str(getattr(data, 'tournament_wins', 0)), inline=True)
    if getattr(data, 'tournament_placings', []):
        recent = data.tournament_placings[-3:][::-1]
        placing_str = "\n".join([f"{date}: {place}{'st' if place==1 else 'nd' if place==2 else 'rd' if place==3 else 'th'}" for date, place in recent])
        embed.add_field(name="Recent Tournament Placings", value=placing_str, inline=False)
    await ctx.send(embed=embed)

@bot.command()
async def daily(ctx):
    user_id = str(ctx.author.id)
    data = user_data[user_id]
    now = datetime.now(timezone.utc)
    if data.last_daily and (now - data.last_daily).days < 1:
        next_claim = data.last_daily + timedelta(days=1)
        return await ctx.send(f"🚫 You already claimed today! Next claim at {next_claim.strftime('%H:%M UTC')}")
    
    streak = min(data.daily_streak + 1, MAX_DAILY_STREAK)
    reward = DAILY_REWARD + min(streak * 100, MAX_DAILY_STREAK * 100)
    daily_boost_level = data.upgrades.get("daily_boost", 0)
    if daily_boost_level > 0:
        boost_bonus = int(reward * (0.1 * daily_boost_level))
        reward += boost_bonus
    
    guild_bonus = 0
    if user_id in user_guilds:
        guild_name = user_guilds[user_id]
        guild = guilds[guild_name]
        daily_bonus_level = guild.perks.get("daily_bonus", 0)
        if daily_bonus_level > 0:
            guild_bonus = int(reward * (0.05 * daily_bonus_level))
            reward += guild_bonus
    
    data.balance += reward
    data.total_earned += reward
    data.last_daily = now
    data.daily_streak = streak
    
    embed = create_embed("🎉 Daily Reward Claimed!", f"You received ${reward:,}")
    embed.add_field(name="Streak", value=f"{streak} days", inline=True)
    if guild_bonus > 0: embed.add_field(name="Guild Bonus", value=f"${guild_bonus:,}", inline=True)
    await ctx.send(embed=embed)

@bot.command(aliases=["creatures", "pets"])
async def collection(ctx, user: discord.Member = None, page: int = 1):
    target = user or ctx.author
    data = user_data[str(target.id)]
    if not data.catches: return await ctx.send(f"{target.display_name} hasn't caught any creatures yet!")
    
    # Sort by value for consistent indexing
    sorted_catches = sorted(enumerate(data.catches), key=lambda x: x[1]["value"], reverse=True)
    
    per_page = 10
    total_pages = (len(sorted_catches) + per_page - 1) // per_page
    page = max(1, min(page, total_pages))
    
    start_idx = (page - 1) * per_page
    end_idx = start_idx + per_page
    
    page_catches = sorted_catches[start_idx:end_idx]
    embed = create_embed(f"🏆 {target.display_name}'s Collection", f"Page {page}/{total_pages} (Sorted by Value)")
    
    for original_idx, creature in page_catches:
        modifier_text = ""
        if creature.get("modifiers"):
            modifier_emojis = " ".join(creature.get("emoji_modifiers", []))
            modifier_text = f"\nModifiers: {modifier_emojis}"
        
        creature_type = CREATURE_TYPES[creature["type"]].get("type", "Unknown")
        embed.add_field(
            name=f"{original_idx + 1}. {creature['emoji']} {creature.get('display_name', creature['type'])} [{creature_type}]", 
            value=f"Value: ${creature['value']:,}\nSize: {creature['size']}m\nRarity: {creature['rarity']}{modifier_text}", 
            inline=False
        )
    
    if total_pages > 1:
        embed.set_footer(text=f"Use !collection [user] [page] to navigate • React with ⬅️➡️ to change pages")
    
    message = await ctx.send(embed=embed)
    
    if total_pages > 1:
        await message.add_reaction("⬅️")
        await message.add_reaction("➡️")
        
        def check(reaction, reaction_user):
            return (reaction_user.id == ctx.author.id and 
                    str(reaction.emoji) in ["⬅️", "➡️"] and 
                    reaction.message.id == message.id)
        
        try:
            while True:
                reaction, reaction_user = await bot.wait_for("reaction_add", timeout=60.0, check=check)
                
                if str(reaction.emoji) == "⬅️" and page > 1:
                    page -= 1
                elif str(reaction.emoji) == "➡️" and page < total_pages:
                    page += 1
                else:
                    continue
                
                start_idx = (page - 1) * per_page
                end_idx = start_idx + per_page
                page_catches = sorted_catches[start_idx:end_idx]
                
                embed = create_embed(f"🏆 {target.display_name}'s Collection", f"Page {page}/{total_pages} (Sorted by Value)")
                for original_idx, creature in page_catches:
                    modifier_text = ""
                    if creature.get("modifiers"):
                        modifier_emojis = " ".join(creature.get("emoji_modifiers", []))
                        modifier_text = f"\nModifiers: {modifier_emojis}"
                    
                    creature_type = CREATURE_TYPES[creature["type"]].get("type", "Unknown")
                    embed.add_field(
                        name=f"{original_idx + 1}. {creature['emoji']} {creature.get('display_name', creature['type'])} [{creature_type}]", 
                        value=f"Value: ${creature['value']:,}\nSize: {creature['size']}m\nRarity: {creature['rarity']}{modifier_text}", 
                        inline=False
                    )
                
                embed.set_footer(text=f"Use !collection [user] [page] to navigate • React with ⬅️➡️ to change pages")
                await message.edit(embed=embed)
                
                try:
                    await message.remove_reaction(reaction.emoji, reaction_user)
                except discord.Forbidden:
                    pass
                
        except asyncio.TimeoutError:
            try:
                await message.clear_reactions()
            except discord.Forbidden:
                pass

@bot.command(aliases=["commands", "help"])
async def help_command(ctx, category: str = None):
    help_data = {
        "basic": {"title": "🎯 Basic Commands", "commands": [("!daily", "Claim your daily reward"), ("!balance [user]", "Check your or another user's balance"), ("!help [category]", "Show available commands")]},
        "creatures": {"title": "🐾 Creature Commands", "commands": [("!catch", "Catch a new creature"), ("!collection [user] [page]", "View your or another user's collection with pagination"), ("!sell", "Interactive sell menu with confirmation"), ("!inspect <number>", "View detailed creature information")]},
        "battle": {"title": "⚔️ Battle Commands", "commands": [("!team", "View your current battle team"), ("!team set <1> <2> <3>", "Set your 3-creature battle team"), ("!battle @user", "Battle another user with teams")]},
        "teams": {"title": "👥 Team Management", "commands": [("!team", "View your current team setup"), ("!team set 1 5 10", "Set creatures 1, 5, and 10 as your battle team"), ("Teams must have exactly 3 creatures", "Choose your strongest creatures for battles")]},
        "trading": {"title": "🤝 Trading Commands", "commands": [("!trade @user <offer_type> <offer_item> <request_type> <request_item>", "Trade creatures or money with another user"), ("Example: !trade @user money 5000 creature 3", "Trade $5000 for their 3rd creature")]},
        "items": {"title": "🛒 Item Commands", "commands": [("!store [category]", "View store categories or items"), ("!buy <category> <item_or_keyword>", "Purchase an item using name or keyword"), ("!inventory", "View your owned items"), ("!open <lootbox_type>", "Open a lootbox you own"), ("!use <consumable> [creature_number]", "Use a consumable item"), ("!equip <creature_number> <cosmetic>", "Equip cosmetic to creature"), ("!enchant <creature_number> <enchantment>", "Apply enchantment to creature")]},
        "guild": {"title": "🏰 Guild Commands", "commands": [("!guild", "View your guild or guild commands"), ("!guild create <name>", "Create a new guild ($50,000)"), ("!guild join <name>", "Join an existing guild"), ("!guild contribute <amount>", "Contribute money to guild treasury"), ("!guild upgrade <perk>", "Upgrade guild perks"), ("Available perks:", "catch_bonus, daily_bonus, battle_bonus, xp_boost, storage_boost")]},
        "tournament": {"title": "🏆 Tournament Commands", "commands": [
            ("!tournament", "Show tournament status and info"),
            ("!tournament join", "Join the daily tournament (before 8pm UTC)"),
            ("!tournament placings", "View the most recent tournament results"),
            ("Tournament Info:", "Daily at 8pm UTC, buy-in required, winner takes all, Bo3 grand final")
        ]}
    }
    
    if not category:
        embed = create_embed("🎮 Help Menu", "Use `!help <category>` for more info")
        for cat, info in help_data.items(): embed.add_field(name=info["title"], value=f"`!help {cat}`", inline=False)
        embed.set_footer(text="💡 New: Type effectiveness system and improved guild perks!")
        return await ctx.send(embed=embed)
    
    if category not in help_data: return await ctx.send(f"Invalid category! Available: {', '.join(help_data.keys())}")
    
    embed = create_embed(help_data[category]["title"])
    for cmd, desc in help_data[category]["commands"]: embed.add_field(name=cmd, value=desc, inline=False)
    await ctx.send(embed=embed)

@bot.command()
async def sell(ctx):
    user_id = str(ctx.author.id)
    data = user_data[user_id]
    if not data.catches: return await ctx.send("You don't have any creatures to sell!")
    
    # Sort by value for consistent indexing
    sorted_catches = sorted(enumerate(data.catches), key=lambda x: x[1]["value"], reverse=True)
    page = 0
    per_page = 10
    selected_indices = set()
    number_emojis = ["1️⃣", "2️⃣", "3️⃣", "4️⃣", "5️⃣", "6️⃣", "7️⃣", "8️⃣", "9️⃣", "🔟"]
    nav_emojis = ["⬅️", "➡️"]
    
    def get_page_embed():
        start = page * per_page
        end = start + per_page
        creatures_to_show = sorted_catches[start:end]
        embed = create_embed("💰 Select Creatures to Sell", f"Page {page+1}/{(len(sorted_catches)-1)//per_page+1}\nReact with numbers to select, ⬅️/➡️ to change page, then ✅ to confirm")
        for i, (original_idx, creature) in enumerate(creatures_to_show, 1):
            sell_price = int(creature["value"] * 0.7)
            modifier_text = ""
            if creature.get("modifiers"):
                modifier_emojis = " ".join(creature.get("emoji_modifiers", []))
                modifier_text = f" {modifier_emojis}"
            selection_indicator = "✅ " if original_idx in selected_indices else ""
            embed.add_field(
                name=f"{selection_indicator}{i}. {creature['emoji']} {creature.get('display_name', creature['type'])}{modifier_text}",
                value=f"Value: ${creature['value']:,} → Sell for: ${sell_price:,}",
                inline=False
            )
        embed.set_footer(text=f"Showing {start+1}-{min(end, len(sorted_catches))} of {len(sorted_catches)} creatures • Page {page+1}/{(len(sorted_catches)-1)//per_page+1}")
        return embed, creatures_to_show
    
    embed, creatures_to_show = get_page_embed()
    message = await ctx.send(embed=embed)
    for i in range(min(len(creatures_to_show), 10)):
        await message.add_reaction(number_emojis[i])
    if len(sorted_catches) > per_page:
        await message.add_reaction("⬅️")
        await message.add_reaction("➡️")
    await message.add_reaction("✅")
    await message.add_reaction("❌")
    
    def check(reaction, user):
        return (user.id == ctx.author.id and reaction.message.id == message.id)
    
    try:
        while True:
            reaction, user = await bot.wait_for("reaction_add", timeout=60.0, check=check)
            emoji = str(reaction.emoji)
            if emoji == "❌":
                embed = create_embed("❌ Sale Cancelled", "No creatures were sold.")
                await message.edit(embed=embed)
                try: await message.clear_reactions()
                except discord.Forbidden: pass
                return
            elif emoji == "✅":
                if not selected_indices:
                    await ctx.send("❌ No creatures selected! React with numbers first.")
                    continue
                total_value = 0
                creatures_to_sell = []
                for original_idx in selected_indices:
                    creature = data.catches[original_idx]
                    sell_price = int(creature["value"] * 0.7)
                    total_value += sell_price
                    creatures_to_sell.append((original_idx, creature, sell_price))
                confirm_embed = create_embed("⚠️ Confirm Multiple Sales", f"Selling {len(selected_indices)} creatures for ${total_value:,}")
                creature_list = "\n".join([f"{creature['emoji']} {creature.get('display_name', creature['type'])} - ${price:,}" for _, creature, price in creatures_to_sell])
                confirm_embed.add_field(name="Creatures to Sell", value=creature_list, inline=False)
                confirm_embed.add_field(name="React to confirm", value="✅ Sell All | ❌ Cancel", inline=False)
                await message.edit(embed=confirm_embed)
                await message.clear_reactions()
                await message.add_reaction("✅")
                await message.add_reaction("❌")
                try:
                    reaction, user = await bot.wait_for("reaction_add", timeout=30.0, check=check)
                    if str(reaction.emoji) == "✅":
                        # Sort by original index in reverse order to avoid index shifting
                        creatures_to_sell.sort(key=lambda x: x[0], reverse=True)
                        for original_idx, creature, price in creatures_to_sell:
                            data.catches.pop(original_idx)
                            data.balance += price
                        final_embed = create_embed("✅ Creatures Sold!", f"Sold {len(selected_indices)} creatures for ${total_value:,}")
                        final_embed.add_field(name="New Balance", value=f"${data.balance:,}", inline=True)
                        await message.edit(embed=final_embed)
                        save_data()
                    else:
                        cancel_embed = create_embed("❌ Sale Cancelled", "No creatures were sold.")
                        await message.edit(embed=cancel_embed)
                    try: await message.clear_reactions()
                    except discord.Forbidden: pass
                    return
                except asyncio.TimeoutError:
                    timeout_embed = create_embed("⏰ Sale Timed Out", "No creatures were sold.")
                    await message.edit(embed=timeout_embed)
                    try: await message.clear_reactions()
                    except discord.Forbidden: pass
                    return
            elif emoji in number_emojis[:len(creatures_to_show)]:
                selected_index = number_emojis.index(emoji)
                original_idx, _ = creatures_to_show[selected_index]
                if original_idx in selected_indices:
                    selected_indices.remove(original_idx)
                else:
                    selected_indices.add(original_idx)
                embed, creatures_to_show = get_page_embed()
                await message.edit(embed=embed)
            elif emoji == "⬅️" and page > 0:
                page -= 1
                embed, creatures_to_show = get_page_embed()
                await message.edit(embed=embed)
            elif emoji == "➡️" and (page+1)*per_page < len(sorted_catches):
                page += 1
                embed, creatures_to_show = get_page_embed()
                await message.edit(embed=embed)
            try:
                await message.remove_reaction(reaction.emoji, user)
            except discord.Forbidden:
                pass
    except asyncio.TimeoutError:
        timeout_embed = create_embed("⏰ Selection Timed Out", "No creatures were selected.")
        await message.edit(embed=timeout_embed)
        try: await message.clear_reactions()
        except discord.Forbidden: pass

@bot.command()
async def store(ctx, category: str = None):
    if not category:
        embed = create_embed("🛒 Store Categories")
        for cat, items in STORE_ITEMS.items():
            embed.add_field(name=cat.title(), value=f"{len(items)} items available", inline=True)
        embed.set_footer(text="Use !store <category> to view items")
        return await ctx.send(embed=embed)
    
    category = category.lower()
    if category not in STORE_ITEMS: return await ctx.send(f"Invalid category! Available: {', '.join(STORE_ITEMS.keys())}")
    
    embed = create_embed(f"🛒 {category.title()} Store")
    for item_id, item_data in STORE_ITEMS[category].items():
        price = item_data["price"]
        if category == "upgrades":
            user_id = str(ctx.author.id)
            level = user_data[user_id].upgrades.get(item_id, 0)
            if level < item_data["max_level"]:
                price = int(price * (item_data["price_increase"] ** level))
                embed.add_field(name=f"{item_data['name']} (Level {level}/{item_data['max_level']})", value=f"${price:,}\n{item_data['description']}\nKeywords: {', '.join(item_data['keywords'])}", inline=False)
        else:
            embed.add_field(name=item_data["name"], value=f"${price:,}\n{item_data['description']}\nKeywords: {', '.join(item_data['keywords'])}", inline=False)
    await ctx.send(embed=embed)

@bot.command()
async def buy(ctx, category: str = None, item_name: str = None):
    if not category or not item_name: return await ctx.send("Usage: `!buy <category> <item_name_or_keyword>`\n💡 Tip: You can use keywords! Check `!store <category>` for keywords.")

    user_id = str(ctx.author.id)
    data = user_data[user_id]
    category, item_name = category.lower(), item_name.lower()
    if category not in STORE_ITEMS: return await ctx.send(f"Invalid category! Available: {', '.join(STORE_ITEMS.keys())}")

    item = None
    for item_id, item_data in STORE_ITEMS[category].items():
        if (item_id.lower() == item_name or item_data["name"].lower() == item_name or item_name in [k.lower() for k in item_data.get("keywords", [])]):
            item = (item_id, item_data)
            break

    if not item: return await ctx.send(f"Item not found in {category}! Use `!store {category}` to see available items and keywords.")

    item_id, item_data = item
    price = item_data["price"]

    if category == "upgrades":
        level = data.upgrades.get(item_id, 0)
        if level >= item_data["max_level"]: return await ctx.send(f"You already have max level {item_data['name']}!")
        price = int(price * (item_data["price_increase"] ** level))

    if data.balance < price: return await ctx.send(f"You need ${price:,} but only have ${data.balance:,}!")

    data.balance -= price

    if category == "upgrades": 
        data.upgrades[item_id] = data.upgrades.get(item_id, 0) + 1
    elif category == "enchantments": 
        if item_id not in data.enchantments:
            data.enchantments.append(item_id)
        else:
            await ctx.send(f"Note: You already had the {item_data['name']} enchantment. Duration has been refreshed.")
    elif category == "cosmetics":
        if item_id not in data.cosmetics: 
            data.cosmetics.append(item_id)
        else:
            data.balance += price
            return await ctx.send(f"You already own {item_data['name']}!")
    elif category == "consumables": 
        data.consumables[item_id] = data.consumables.get(item_id, 0) + 1
    elif category == "lootboxes": 
        data.lootboxes[item_id] = data.lootboxes.get(item_id, 0) + 1

    embed = create_embed(f"✅ Purchased {item_data['name']}!", f"Remaining balance: ${data.balance:,}")
    await ctx.send(embed=embed)
    save_data()

@bot.command()
async def inventory(ctx):
    user_id = str(ctx.author.id)
    data = user_data[user_id]
    embed = create_embed(f"🎒 {ctx.author.display_name}'s Inventory")
    
    if data.upgrades:
        upgrade_text = "\n".join([f"{STORE_ITEMS['upgrades'][k]['name']}: Level {v}" for k, v in data.upgrades.items()])
        embed.add_field(name="Upgrades", value=upgrade_text, inline=False)
    
    if data.enchantments:
        enchant_text = []
        for e in data.enchantments:
            if e in STORE_ITEMS['enchantments']:
                enchant_text.append(f"{STORE_ITEMS['enchantments'][e]['name']}")
            else:
                enchant_text.append(f"Unknown enchantment: {e}")
        
        if enchant_text:
            embed.add_field(name="Enchantments", value="\n".join(enchant_text), inline=False)
    
    if data.cosmetics:
        cosmetic_text = []
        for c in data.cosmetics:
            if c in STORE_ITEMS['cosmetics']:
                cosmetic_text.append(f"{STORE_ITEMS['cosmetics'][c]['emoji']} {STORE_ITEMS['cosmetics'][c]['name']}")
            else:
                cosmetic_text.append(f"Unknown cosmetic: {c}")
        
        if cosmetic_text:
            embed.add_field(name="Cosmetics", value="\n".join(cosmetic_text), inline=False)
    
    if data.consumables:
        consumable_text = "\n".join([f"{STORE_ITEMS['consumables'][k]['name']}: {v}" for k, v in data.consumables.items() if v > 0 and k in STORE_ITEMS['consumables']])
        if consumable_text: embed.add_field(name="Consumables", value=consumable_text, inline=False)
    
    if data.lootboxes:
        lootbox_text = "\n".join([f"{STORE_ITEMS['lootboxes'][k]['name']}: {v}" for k, v in data.lootboxes.items() if v > 0 and k in STORE_ITEMS['lootboxes']])
        if lootbox_text: embed.add_field(name="Lootboxes", value=lootbox_text, inline=False)
    
    if not any([data.upgrades, data.enchantments, data.cosmetics, data.consumables, data.lootboxes]):
        embed.add_field(name="Empty", value="No items in inventory", inline=False)
    
    await ctx.send(embed=embed)

@bot.command()
async def team(ctx, action: str = None, *args):
    user_id = str(ctx.author.id)
    user_data[user_id]
    
    if not action:
        if not user_data[user_id].battle_team:
            return await ctx.send("You don't have a battle team set up! Use `!team set <creature1> <creature2> <creature3>` to create one.")
        
        team_text = []
        for i, idx in enumerate(user_data[user_id].battle_team, 1):
            creature = user_data[user_id].catches[idx]
            team_text.append(f"{i}. {creature['emoji']} {creature.get('display_name', creature['type'])} (Value: ${creature['value']:,})")
        
        embed = create_embed("Your Battle Team", "\n".join(team_text))
        return await ctx.send(embed=embed)
    
    if action == "set":
        if len(args) != 3:
            return await ctx.send("Please specify exactly 3 creature numbers! Example: `!team set 1 2 3`")
        
        try:
            indices = [int(arg) - 1 for arg in args]  # Convert to 0-based indices
        except ValueError:
            return await ctx.send("Please provide valid numbers!")
        
        # Validate indices
        if not all(0 <= idx < len(user_data[user_id].catches) for idx in indices):
            return await ctx.send("One or more of those creatures don't exist!")
        
        if len(set(indices)) != 3:
            return await ctx.send("You can't use the same creature twice!")
        
        user_data[user_id].battle_team = indices
        await ctx.send("✅ Battle team updated!")
        save_data()
    
    elif action == "auto":
        if len(user_data[user_id].catches) < 3:
            return await ctx.send("You need at least 3 creatures to create a battle team!")
        
        # Sort by value and take top 3
        strongest = sorted(
            range(len(user_data[user_id].catches)),
            key=lambda i: user_data[user_id].catches[i]["value"],
            reverse=True
        )[:3]
        
        user_data[user_id].battle_team = strongest
        await ctx.send("✅ Battle team automatically set to your 3 strongest creatures!")
        save_data()
    
    else:
        await ctx.send("Invalid action! Use `!team set <creature1> <creature2> <creature3>` or `!team auto`")

# Add at the top with other global variables
RECENT_PLAYERS = {}  # Dict to store recent players and their last activity time
RECENT_PLAYERS_WINDOW = 24 * 60 * 60  # 24 hours in seconds

def add_recent_player(user_id):
    """Add or update a player in the recent players list"""
    RECENT_PLAYERS[str(user_id)] = datetime.now(timezone.utc)

def get_recent_players():
    """Get list of players active in the last 24 hours"""
    current_time = datetime.now(timezone.utc)
    return [uid for uid, last_active in RECENT_PLAYERS.items() 
            if (current_time - last_active).total_seconds() <= RECENT_PLAYERS_WINDOW]

@bot.command()
async def guild(ctx, action: str = None, *args):
    user_id = str(ctx.author.id)
    
    if not action:
        if user_id in user_guilds:
            guild_name = user_guilds[user_id]
            guild = guilds[guild_name]
            embed = create_embed(f"🏰 Guild: {guild.name}")
            embed.add_field(name="Level", value=f"{guild.level}", inline=True)
            
            xp_needed = guild.level * 500
            xp_progress = min(guild.xp / xp_needed * 100, 100) if xp_needed > 0 else 100
            embed.add_field(name="XP Progress", value=f"{guild.xp:,}/{xp_needed:,} ({xp_progress:.1f}%)", inline=True)
            
            embed.add_field(name="Members", value=f"{len(guild.members)}/{MAX_GUILD_MEMBERS}", inline=True)
            embed.add_field(name="Treasury", value=f"${guild.treasury:,}", inline=True)
            embed.add_field(name="Description", value=guild.description, inline=False)
        
            if guild.perks:
                perk_text = []
                for perk, level in guild.perks.items():
                    if perk == "catch_bonus":
                        perk_text.append(f"Catch Bonus: Level {level}/{guild.level} (+{level * 2}% catch value)")
                    elif perk == "daily_bonus":
                        perk_text.append(f"Daily Bonus: Level {level}/{guild.level} (+{level * 5}% daily rewards)")
                    elif perk == "battle_bonus":
                        perk_text.append(f"Battle Bonus: Level {level}/{guild.level} (+{level * 5}% battle rewards)")
                    elif perk == "xp_boost":
                        perk_text.append(f"XP Boost: Level {level}/{guild.level} (+{level * 5}% guild XP gain)")
                    elif perk == "storage_boost":
                        perk_text.append(f"Storage Boost: Level {level}/{guild.level} (+{level * 5} creature slots)")
                    else:
                        perk_text.append(f"{perk.replace('_', ' ').title()}: Level {level}/{guild.level}")
                
                embed.add_field(name="Guild Perks", value="\n".join(perk_text), inline=False)
            else:
                embed.add_field(name="Guild Perks", value=f"No perks upgraded yet (Max level: {guild.level})", inline=False)
        
            member_list = "\n".join([f"<@{member}>" for member in guild.members[:10]])
            embed.add_field(name="Members", value=member_list, inline=False)
        else:
            embed = create_embed("🏰 Guild Commands")
            embed.add_field(name="!guild create <name>", value="Create a guild ($50,000)", inline=False)
            embed.add_field(name="!guild join <name>", value="Join a guild", inline=False)
            embed.add_field(name="!guild list", value="List all guilds", inline=False)
            embed.add_field(name="!guild contribute <amount>", value="Contribute money to guild treasury", inline=False)
            embed.add_field(name="!guild upgrade <perk>", value="Upgrade guild perks", inline=False)
            embed.add_field(name="Available Perks", value="catch_bonus: +2 percent catch value per level\ndaily_bonus: +5 percent daily rewards per level\nbattle_bonus: +5 percent battle rewards per level\nxp_boost: +5 percent guild XP gain per level\nstorage_boost: +5 creature slots per level", inline=False)
        return await ctx.send(embed=embed)
    
    if action.lower() == "create":
        if not args: return await ctx.send("Usage: `!guild create <name>`")
        if user_id in user_guilds: return await ctx.send("🚫 You're already in a guild!")
        
        guild_name = " ".join(args)
        if guild_name in guilds: return await ctx.send("🚫 A guild with that name already exists!")
        
        data = user_data[user_id]
        if data.balance < 50000: return await ctx.send("🚫 You need $50,000 to create a guild!")
        
        data.balance -= 50000
        guild = Guild(guild_name, user_id)
        guilds[guild_name] = guild
        user_guilds[user_id] = guild_name
        
        embed = create_embed("🏰 Guild Created!", f"Created guild '{guild_name}'")
        await ctx.send(embed=embed)
        save_data()
        save_guild_data()
    
    elif action.lower() == "join":
        if not args: return await ctx.send("Usage: `!guild join <name>`")
        if user_id in user_guilds: return await ctx.send("🚫 You're already in a guild!")
        
        guild_name = " ".join(args)
        if guild_name not in guilds: return await ctx.send("🚫 Guild not found!")
        
        guild = guilds[guild_name]
        if len(guild.members) >= MAX_GUILD_MEMBERS: return await ctx.send("🚫 Guild is full!")
        
        guild.members.append(user_id)
        user_guilds[user_id] = guild_name
        
        embed = create_embed("🏰 Joined Guild!", f"Joined '{guild_name}'")
        await ctx.send(embed=embed)
        save_guild_data()
    
    elif action.lower() == "contribute":
        if user_id not in user_guilds: return await ctx.send("🚫 You're not in a guild!")
        if not args: return await ctx.send("Usage: `!guild contribute <amount>`")
        
        try:
            amount = int(args[0])
            if amount <= 0: return await ctx.send("🚫 Amount must be positive!")
            
            data = user_data[user_id]
            if data.balance < amount: return await ctx.send(f"🚫 You don't have ${amount:,}!")
            
            guild_name = user_guilds[user_id]
            guild = guilds[guild_name]
            
            data.balance -= amount
            guild.treasury += amount
            
            # Apply XP boost if the guild has it
            xp_boost_level = guild.perks.get("xp_boost", 0)
            xp_multiplier = 1 + (0.05 * xp_boost_level)
            
            # Calculate XP gain (1 XP per 1000 coins)
            xp_gained = int((amount // 1000) * xp_multiplier)
            guild.xp += xp_gained
            
            # Check for level up
            xp_needed = guild.level * 500
            level_ups = 0
            while guild.xp >= xp_needed:
                guild.level += 1
                guild.xp -= xp_needed
                level_ups += 1
                xp_needed = guild.level * 500
            
            embed = create_embed("💰 Guild Contribution", f"Contributed ${amount:,} to {guild_name}")
            embed.add_field(name="Guild Treasury", value=f"${guild.treasury:,}", inline=True)
            embed.add_field(name="Your Balance", value=f"${data.balance:,}", inline=True)
            
            xp_text = f"+{xp_gained} XP (1 XP per 1000 coins)"
            if xp_boost_level > 0:
                xp_text += f" with {xp_boost_level * 5}% XP boost"
            embed.add_field(name="XP Gained", value=xp_text, inline=False)
            
            if level_ups > 0:
                embed.add_field(name="🎉 Guild Level Up!", value=f"Guild is now level {guild.level}!", inline=False)
            
            await ctx.send(embed=embed)
            save_data()
            save_guild_data()
            
        except ValueError:
            return await ctx.send("🚫 Invalid amount!")
    
    elif action.lower() == "upgrade":
        if user_id not in user_guilds: return await ctx.send("🚫 You're not in a guild!")
        if not args: return await ctx.send("Usage: `!guild upgrade <perk>`\nAvailable perks: catch_bonus, daily_bonus, battle_bonus, xp_boost, storage_boost")
        
        guild_name = user_guilds[user_id]
        guild = guilds[guild_name]
        
        if str(guild.owner_id) != user_id: return await ctx.send("🚫 Only the guild owner can upgrade perks!")
        
        perk_name = args[0].lower()
        valid_perks = ["catch_bonus", "daily_bonus", "battle_bonus", "xp_boost", "storage_boost"]
        if perk_name not in valid_perks: return await ctx.send(f"🚫 Invalid perk! Available: {', '.join(valid_perks)}")
        
        current_level = guild.perks.get(perk_name, 0)
        max_level = guild.level
        if current_level >= max_level: return await ctx.send(f"🚫 {perk_name} is already at max level for your guild! Upgrade your guild level first by contributing more XP.")
        
        cost = (current_level + 1) * 50000
        if guild.treasury < cost: return await ctx.send(f"🚫 Guild needs ${cost:,} in treasury to upgrade {perk_name}!")
        
        guild.treasury -= cost
        guild.perks[perk_name] = current_level + 1
        
        # Create description based on perk type
        perk_descriptions = {
            "catch_bonus": f"+{(current_level + 1) * 2}% catch value",
            "daily_bonus": f"+{(current_level + 1) * 5}% daily rewards",
            "battle_bonus": f"+{(current_level + 1) * 5}% battle rewards",
            "xp_boost": f"+{(current_level + 1) * 10}% guild XP gain",
            "storage_boost": f"+{(current_level + 1) * 5} creature slots"
        }
        
        embed = create_embed("⬆️ Guild Perk Upgraded!", f"Upgraded {perk_name.replace('_', ' ').title()} to level {guild.perks[perk_name]}")
        embed.add_field(name="Effect", value=perk_descriptions[perk_name], inline=True)
        embed.add_field(name="Cost", value=f"${cost:,}", inline=True)
        embed.add_field(name="Remaining Treasury", value=f"${guild.treasury:,}", inline=True)
        embed.add_field(name="Max Perk Level", value=f"Level {guild.level} (Guild Level)", inline=True)
        await ctx.send(embed=embed)
        save_guild_data()
    
    elif action.lower() == "list":
        if not guilds: return await ctx.send("No guilds exist yet!")
        
        embed = create_embed("🏰 All Guilds")
        for name, guild in list(guilds.items())[:10]:
            embed.add_field(name=name, value=f"Level {guild.level} | {len(guild.members)}/{MAX_GUILD_MEMBERS} members | ${guild.treasury:,} treasury", inline=False)
        await ctx.send(embed=embed)

@bot.command()
async def leaderboard(ctx, category: str = "networth"):
    if category.lower() in ["balance", "money", "cash"]:
        top_users = sorted(user_data.items(), key=lambda x: x[1].balance, reverse=True)[:10]
        embed = create_embed("💰 Balance Leaderboard")
        for i, (user_id, data) in enumerate(top_users, 1):
            try:
                user = bot.get_user(int(user_id))
                name = user.display_name if user else f"User {user_id}"
                embed.add_field(name=f"{i}. {name}", value=f"${data.balance:,}", inline=False)
            except: continue
    
    elif category.lower() in ["networth", "worth", "net"]:
        user_networth = []
        for user_id, data in user_data.items():
            collection_value = sum(c["value"] for c in data.catches) if data.catches else 0
            networth = data.balance + collection_value
            user_networth.append((user_id, networth))
        
        top_users = sorted(user_networth, key=lambda x: x[1], reverse=True)[:10]
        embed = create_embed("💎 Net Worth Leaderboard")
        for i, (user_id, networth) in enumerate(top_users, 1):
            try:
                user = bot.get_user(int(user_id))
                name = user.display_name if user else f"User {user_id}"
                embed.add_field(name=f"{i}. {name}", value=f"${networth:,}", inline=False)
            except: continue
    
    elif category.lower() == "collection":
        user_collections = [(user_id, len(data.catches)) for user_id, data in user_data.items() if data.catches]
        top_users = sorted(user_collections, key=lambda x: x[1], reverse=True)[:10]
        embed = create_embed("🐾 Collection Leaderboard")
        for i, (user_id, count) in enumerate(top_users, 1):
            try:
                user = bot.get_user(int(user_id))
                name = user.display_name if user else f"User {user_id}"
                embed.add_field(name=f"{i}. {name}", value=f"{count} creatures", inline=False)
            except: continue
    
    elif category.lower() == "battles":
        battle_users = [(user_id, data.battles_won) for user_id, data in user_data.items() if data.battles_won > 0]
        top_users = sorted(battle_users, key=lambda x: x[1], reverse=True)[:10]
        embed = create_embed("⚔️ Battle Leaderboard")
        for i, (user_id, wins) in enumerate(top_users, 1):
            try:
                user = bot.get_user(int(user_id))
                name = user.display_name if user else f"User {user_id}"
                data = user_data[user_id]
                total = data.battles_won + data.battles_lost
                win_rate = (data.battles_won / total) * 100 if total > 0 else 0
                embed.add_field(name=f"{i}. {name}", value=f"{wins} wins ({win_rate:.1f}%)", inline=False)
            except: continue
    
    else:
        return await ctx.send("Invalid category! Use: networth, balance, collection, or battles")
    
    await ctx.send(embed=embed)

@bot.command()
async def equip(ctx, creature_index: int, cosmetic_name: str):
    user_id = str(ctx.author.id)
    data = user_data[user_id]
    
    if creature_index < 1 or creature_index > len(data.catches):
        return await ctx.send(f"Invalid creature index! You have {len(data.catches)} creatures.")
    
    cosmetic_id = None
    for item_id, item_data in STORE_ITEMS["cosmetics"].items():
        if (item_id.lower() == cosmetic_name.lower() or 
            item_data["name"].lower() == cosmetic_name.lower() or 
            cosmetic_name.lower() in [k.lower() for k in item_data.get("keywords", [])]):
            cosmetic_id = item_id
            break
    
    if not cosmetic_id: return await ctx.send("Cosmetic not found!")
    if cosmetic_id not in data.cosmetics: return await ctx.send("You don't own this cosmetic!")
    
    # Remove this cosmetic from all other creatures first
    for idx, c in enumerate(data.catches):
        if "cosmetics" in c and cosmetic_id in c["cosmetics"]:
            c["cosmetics"].remove(cosmetic_id)
    
    creature = data.catches[creature_index - 1]
    if "cosmetics" not in creature:
        creature["cosmetics"] = []
        
    if cosmetic_id not in creature["cosmetics"]:
        creature["cosmetics"].append(cosmetic_id)
        cosmetic_data = STORE_ITEMS["cosmetics"][cosmetic_id]
        embed = create_embed("✨ Cosmetic Equipped!", f"Equipped {cosmetic_data['emoji']} {cosmetic_data['name']} on {creature.get('display_name', creature['type'])}")
        await ctx.send(embed=embed)
        save_data()
    else:
        await ctx.send("This creature already has that cosmetic equipped!")

@bot.command()
async def unequip(ctx, creature_index: int, cosmetic_name: str):
    user_id = str(ctx.author.id)
    data = user_data[user_id]
    
    if creature_index < 1 or creature_index > len(data.catches):
        return await ctx.send(f"Invalid creature index! You have {len(data.catches)} creatures.")
    
    cosmetic_id = None
    for item_id, item_data in STORE_ITEMS["cosmetics"].items():
        if (item_id.lower() == cosmetic_name.lower() or 
            item_data["name"].lower() == cosmetic_name.lower() or 
            cosmetic_name.lower() in [k.lower() for k in item_data.get("keywords", [])]):
            cosmetic_id = item_id
            break
    
    if not cosmetic_id: return await ctx.send("Cosmetic not found!")
    
    creature = data.catches[creature_index - 1]
    if cosmetic_id in creature.get("cosmetics", []):
        creature["cosmetics"].remove(cosmetic_id)
        cosmetic_data = STORE_ITEMS["cosmetics"][cosmetic_id]
        embed = create_embed("🔄 Cosmetic Unequipped!", f"Unequipped {cosmetic_data['emoji']} {cosmetic_data['name']} from {creature.get('display_name', creature['type'])}")
        await ctx.send(embed=embed)
        save_data()
    else:
        await ctx.send("This creature doesn't have that cosmetic equipped!")

@bot.event
async def on_command_error(ctx, error):
    if isinstance(error, commands.CommandNotFound):
        return
    elif isinstance(error, commands.MissingRequiredArgument):
        await ctx.send(f"❌ Missing required argument. Use `!help {ctx.command}` for usage info.")
    elif isinstance(error, commands.BadArgument):
        await ctx.send("❌ Invalid argument provided.")
    else:
        print(f"Error in command {ctx.command}: {error}")
        await ctx.send("❌ An error occurred while processing the command.")

@bot.command()
async def fix_enchantments(ctx):
    if ctx.author.id != ADMIN_ID:
        return await ctx.send("🚫 You don't have permission to use this command!")
    
    user_id = str(ctx.author.id)
    data = user_data[user_id]
    
    before_count = len(data.enchantments)
    data.enchantments = [e for e in data.enchantments if e in STORE_ITEMS['enchantments']]
    after_count = len(data.enchantments)
    
    data.enchantments = list(set(data.enchantments))
    final_count = len(data.enchantments)
    
    embed = create_embed("🔧 Enchantments Fixed", f"Before: {before_count}\nAfter removing invalid: {after_count}\nAfter removing duplicates: {final_count}")
    await ctx.send(embed=embed)
    save_data()

@bot.command()
async def enchant(ctx, creature_index: int, enchantment_name: str):
    user_id = str(ctx.author.id)
    data = user_data[user_id]
    
    if creature_index < 1 or creature_index > len(data.catches):
        return await ctx.send(f"Invalid creature index! You have {len(data.catches)} creatures.")
    
    enchantment_id = None
    for item_id, item_data in STORE_ITEMS["enchantments"].items():
        if (item_id.lower() == enchantment_name.lower() or 
            item_data["name"].lower() == enchantment_name.lower() or 
            enchantment_name.lower() in [k.lower() for k in item_data.get("keywords", [])]):
            enchantment_id = item_id
            break
    
    if not enchantment_id: 
        return await ctx.send("Enchantment not found! Check your inventory with `!inventory`.")
    
    if enchantment_id not in data.enchantments: 
        return await ctx.send("You don't own this enchantment! Purchase it first with `!buy enchantments <name>`.")
    
    creature = data.catches[creature_index - 1]
    
    if "enchantments" not in creature:
        creature["enchantments"] = []
    
    if enchantment_id not in creature["enchantments"]:
        creature["enchantments"].append(enchantment_id)
        # Store the application time for duration tracking
        if "enchantment_times" not in creature:
            creature["enchantment_times"] = {}
        creature["enchantment_times"][enchantment_id] = datetime.now(timezone.utc).isoformat()
        
        # Remove from inventory
        data.enchantments.remove(enchantment_id)
        
        enchantment_data = STORE_ITEMS["enchantments"][enchantment_id]
        embed = create_embed("✨ Enchantment Applied!", f"Applied {enchantment_data['name']} to {creature.get('display_name', creature['type'])}")
        embed.add_field(name="Effect", value=enchantment_data['description'], inline=False)
        embed.add_field(name="Duration", value=f"{enchantment_data['duration']} days", inline=True)
        await ctx.send(embed=embed)
        save_data()
    else:
        await ctx.send("This creature already has that enchantment applied!")

@bot.command()
async def inspect(ctx, creature_index: int):
    user_id = str(ctx.author.id)
    data = user_data[user_id]
    
    if creature_index < 1 or creature_index > len(data.catches):
        return await ctx.send(f"Invalid creature index! You have {len(data.catches)} creatures.")
    
    creature = data.catches[creature_index - 1]
    base_stats = CREATURE_TYPES[creature["type"]]
    creature_type = base_stats.get("type", "Unknown")
    
    embed = create_embed(f"{creature['emoji']} {creature.get('display_name', creature['type'])}", f"Rarity: {creature['rarity']} | Type: {creature_type}")
    embed.add_field(name="Size", value=f"{creature['size']}m", inline=True)
    embed.add_field(name="Value", value=f"${creature['value']:,}", inline=True)
    
    # Show base stats
    embed.add_field(name="Base Stats", value=f"HP: {base_stats['hp']}\nAttack: {base_stats['attack']}\nDefense: {base_stats['defense']}\nSpeed: {base_stats['speed']}", inline=False)
    
    # Show type effectiveness
    if creature_type in TYPE_EFFECTIVENESS:
        strong_against = ", ".join(TYPE_EFFECTIVENESS[creature_type]["strong_against"])
        weak_against = ", ".join(TYPE_EFFECTIVENESS[creature_type]["weak_against"])
        embed.add_field(name="Type Effectiveness", value=f"Strong against: {strong_against}\nWeak against: {weak_against}", inline=False)
    
    # Show modifiers
    if creature.get("modifiers"):
        modifier_display = " ".join([f"{emoji} {mod}" for mod, emoji in zip(creature.get("modifiers", []), creature.get("emoji_modifiers", []))])
        embed.add_field(name="Modifiers", value=modifier_display, inline=False)
    
    # Show cosmetics
    if creature.get("cosmetics"):
        cosmetic_text = []
        for c in creature.get("cosmetics", []):
            if c in STORE_ITEMS["cosmetics"]:
                cosmetic_text.append(f"{STORE_ITEMS['cosmetics'][c]['emoji']} {STORE_ITEMS['cosmetics'][c]['name']}")
        if cosmetic_text:
            embed.add_field(name="Cosmetics", value="\n".join(cosmetic_text), inline=False)
    
    # Show enchantments with time remaining
    if creature.get("enchantments"):
        now = datetime.now(timezone.utc)
        enchant_text = []
        for e in creature.get("enchantments", []):
            if e in STORE_ITEMS["enchantments"]:
                enchant_name = STORE_ITEMS["enchantments"][e]["name"]
                duration = STORE_ITEMS["enchantments"][e]["duration"]
                
                # Calculate time remaining
                time_remaining = "Unknown"
                if "enchantment_times" in creature and e in creature["enchantment_times"]:
                    applied_time = datetime.fromisoformat(creature["enchantment_times"][e])
                    expiry_time = applied_time + timedelta(days=duration)
                    if now < expiry_time:
                        days_left = (expiry_time - now).days
                        hours_left = ((expiry_time - now).seconds // 3600)
                        time_remaining = f"{days_left}d {hours_left}h"
                    else:
                        time_remaining = "Expired"
                
                enchant_text.append(f"✨ {enchant_name} ({time_remaining})")
        if enchant_text:
            embed.add_field(name="Enchantments", value="\n".join(enchant_text), inline=False)
    
    await ctx.send(embed=embed)

# --- TOURNAMENT SYSTEM ---
TOURNAMENT_BUYIN = 10000
TOURNAMENT_HOUR_UTC = 20  # 8pm UTC
TOURNAMENT_MIN_PLAYERS = 2

tournament_data = {
    'entrants': [],
    'pot': 0,
    'active': False,
    'results': [],
    'in_progress': False,
    'last_winner': None,
    'last_placings': [],
}

def reset_tournament():
    tournament_data['entrants'] = []
    tournament_data['pot'] = 0
    tournament_data['active'] = True
    tournament_data['results'] = []
    tournament_data['in_progress'] = False
    tournament_data['last_placings'] = []

@bot.command()
async def tournament(ctx, action: str = None):
    user_id = str(ctx.author.id)
    data = user_data[user_id]
    if action is None or action.lower() == 'status':
        if tournament_data['in_progress']:
            embed = create_embed("🏆 Tournament In Progress", f"Entrants: {len(tournament_data['entrants'])}\nPot: ${tournament_data['pot']:,}")
            await ctx.send(embed=embed)
        elif tournament_data['active']:
            embed = create_embed("🏆 Tournament Open for Entry", f"Entrants: {len(tournament_data['entrants'])}\nPot: ${tournament_data['pot']:,}\nJoin with `!tournament join` (Buy-in: ${TOURNAMENT_BUYIN:,})")
            await ctx.send(embed=embed)
        else:
            embed = create_embed("🏆 No Tournament Currently Open", "Wait for the next daily tournament!")
            await ctx.send(embed=embed)
    elif action.lower() == 'join':
        if not tournament_data['active'] or tournament_data['in_progress']:
            return await ctx.send("No tournament open for entry right now!")
        if user_id in tournament_data['entrants']:
            return await ctx.send("You are already entered in today's tournament!")
        if data.balance < TOURNAMENT_BUYIN:
            return await ctx.send(f"You need ${TOURNAMENT_BUYIN:,} to join the tournament!")
        data.balance -= TOURNAMENT_BUYIN
        tournament_data['entrants'].append(user_id)
        tournament_data['pot'] += TOURNAMENT_BUYIN
        await ctx.send(f"You have joined the tournament! Good luck!")
        save_data()
    elif action.lower() == 'placings':
        if not tournament_data['last_placings']:
            return await ctx.send("No tournament results yet!")
        embed = create_embed("🏆 Last Tournament Placings")
        for i, uid in enumerate(tournament_data['last_placings'], 1):
            member = await bot.fetch_user(int(uid))
            name = member.display_name if member else f"User {uid}"
            if i == 1:
                embed.add_field(name=f"🥇 1st Place", value=name, inline=False)
            elif i == 2:
                embed.add_field(name=f"🥈 2nd Place", value=name, inline=False)
            elif i == 3:
                embed.add_field(name=f"🥉 3rd Place", value=name, inline=False)
            else:
                embed.add_field(name=f"{i}.", value=name, inline=False)
        await ctx.send(embed=embed)

# Background task to start tournament at 8pm UTC daily
@tasks.loop(minutes=1)
async def tournament_scheduler():
    now = datetime.now(timezone.utc)
    if now.hour == TOURNAMENT_HOUR_UTC and now.minute == 0 and not tournament_data['in_progress']:
        if len(tournament_data['entrants']) >= TOURNAMENT_MIN_PLAYERS:
            tournament_data['in_progress'] = True
            await start_tournament()
        else:
            # Not enough players, refund
            for uid in tournament_data['entrants']:
                user_data[uid].balance += TOURNAMENT_BUYIN
            await announce_tournament("Not enough players joined the tournament. Buy-ins refunded.")
        tournament_data['active'] = False
        tournament_data['entrants'] = []
        tournament_data['pot'] = 0
        save_data()
    # Open for entry after last tournament
    if now.hour == (TOURNAMENT_HOUR_UTC + 1) % 24 and now.minute == 0 and not tournament_data['active']:
        reset_tournament()
        await announce_tournament("A new daily tournament is now open! Join with `!tournament join`.")

def setup_tournament_scheduler():
    if not tournament_scheduler.is_running():
        tournament_scheduler.start()

async def announce_tournament(msg):
    # Announce in all guilds (or a specific channel if you want)
    for guild in bot.guilds:
        for channel in guild.text_channels:
            if channel.permissions_for(guild.me).send_messages:
                try:
                    await channel.send(msg)
                    break
                except:
                    continue

async def start_tournament():
    entrants = tournament_data['entrants'][:]
    random.shuffle(entrants)
    placings = []
    round_num = 1
    await announce_tournament(f"Tournament is starting with {len(entrants)} players! Pot: ${tournament_data['pot']:,}")
    # Bracket rounds
    while len(entrants) > 1:
        next_round = []
        round_matches = []
        # Pair up
        for i in range(0, len(entrants), 2):
            if i+1 < len(entrants):
                round_matches.append((entrants[i], entrants[i+1]))
            else:
                # Bye
                next_round.append(entrants[i])
        # Run matches
        for p1, p2 in round_matches:
            winner, loser = await run_auto_battle(p1, p2)
            next_round.append(winner)
            placings.insert(0, loser)  # Loser out this round
            await announce_tournament(f"<@{winner}> defeated <@{loser}> and advances!")
            await asyncio.sleep(2)
        entrants = next_round
        round_num += 1
    # Grand final (Bo3)
    if len(entrants) == 1 and len(placings) > 0:
        finalist1 = entrants[0]
        finalist2 = placings[0]
        wins1, wins2 = 0, 0
        for i in range(3):
            winner, loser = await run_auto_battle(finalist1, finalist2)
            if winner == finalist1:
                wins1 += 1
            else:
                wins2 += 1
            if wins1 == 2 or wins2 == 2:
                break
            await announce_tournament(f"Grand Final Game {i+1}: <@{winner}> wins!")
            await asyncio.sleep(2)
        if wins1 > wins2:
            champion, runnerup = finalist1, finalist2
        else:
            champion, runnerup = finalist2, finalist1
        placings = [runnerup] + placings[1:]  # runnerup is 2nd
    else:
        champion = entrants[0]
    # Award pot
    user_data[champion].balance += tournament_data['pot']
    user_data[champion].tournament_wins = getattr(user_data[champion], 'tournament_wins', 0) + 1
    # Record placings
    today = datetime.now(timezone.utc).strftime('%Y-%m-%d')
    user_data[champion].tournament_placings.append((today, 1))
    for i, uid in enumerate(placings, 2):
        user_data[uid].tournament_placings.append((today, i))
    tournament_data['last_winner'] = champion
    tournament_data['last_placings'] = [champion] + placings
    await announce_tournament(f"Congratulations <@{champion}>! You won the daily tournament and ${tournament_data['pot']:,}!")
    save_data()

def get_battle_team(user_id):
    data = user_data[user_id]
    if data.battle_team and len(data.battle_team) == 3:
        return [data.catches[i] for i in data.battle_team if i < len(data.catches)]
    # fallback: top 3 by value
    return sorted(data.catches, key=lambda c: c['value'], reverse=True)[:3]

# --- Tournament PvP logic ---
class DummyCtx:
    async def send(self, *args, **kwargs):
        return None

async def run_auto_battle(user1_id, user2_id):
    # Use real PvP logic for tournament matches
    user1_data = user_data[user1_id]
    user2_data = user_data[user2_id]
    # Build teams as in !battle
    def get_team(data, display_name):
        if data.battle_team and len(data.battle_team) == 3:
            indices = [idx for idx in data.battle_team if 0 <= idx < len(data.catches)]
            if len(indices) < 3:
                available = [i for i in range(len(data.catches)) if i not in indices]
                needed = 3 - len(indices)
                indices.extend(available[:needed])
            return [BattleCreature(data.catches[idx], display_name) for idx in indices[:3]]
        else:
            strongest = sorted(
                range(len(data.catches)),
                key=lambda i: data.catches[i]["value"],
                reverse=True
            )[:3]
            return [BattleCreature(data.catches[idx], display_name) for idx in strongest]
    team1 = get_team(user1_data, f"User {user1_id}")
    team2 = get_team(user2_data, f"User {user2_id}")
    battle_system = TeamBattleSystem(team1, team2, f"User {user1_id}", f"User {user2_id}", DummyCtx())
    winner_name, _ = await battle_system.start_battle()
    if winner_name == f"User {user1_id}":
        return user1_id, user2_id
    else:
        return user2_id, user1_id

# Start the scheduler when the bot is ready
@bot.event
async def on_ready():
    print(f'{bot.user} has connected to Discord!')
    load_data()
    load_guild_data()
    auto_save.start()
    setup_tournament_scheduler()
    # Ensure a tournament is always open for entry unless in progress
    if not tournament_data['active'] and not tournament_data['in_progress']:
        reset_tournament()
    start_tournament_reminders()

# --- Tournament Reminders ---
REMINDER_CHANNEL_ID = 1359790747934789706

@tasks.loop(minutes=60)
async def tournament_reminder_task():
    now = datetime.now(timezone.utc)
    hours_until = (TOURNAMENT_HOUR_UTC - now.hour) % 24
    channel = None
    for guild in bot.guilds:
        ch = discord.utils.get(guild.text_channels, id=REMINDER_CHANNEL_ID)
        if ch:
            channel = ch
            break
    if not channel:
        return
    if tournament_data['active'] and not tournament_data['in_progress']:
        if hours_until == 1:
            await channel.send("⏰ The daily tournament starts in 1 hour! Use `!tournament join` to enter. Winner takes all!")
        elif hours_until in [3, 6, 9, 12, 18]:
            await channel.send(f"🏆 The daily tournament is open for entry! It starts at 8pm UTC. Use `!tournament join` to enter. Winner takes all!")

def start_tournament_reminders():
    if not tournament_reminder_task.is_running():
        tournament_reminder_task.start()

bot.run(BOT_TOKEN)

