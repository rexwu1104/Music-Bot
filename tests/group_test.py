import unittest

import discord

class GuildController:
    guild: discord.Guild
    
    class Guild:
        id: int
        
        def __init__(self, id: int) -> None:
            self.guild = None
            self.id = id
    
    def __init__(self, guild: discord.Guild | int) -> None:
        if isinstance(guild, discord.Guild):
            self.guild = guild
        else:        
            self.guild = GuildController.Guild(guild)
            
    def __eq__(self, __value: object) -> bool:
        if isinstance(__value, GuildController):
            return self.id == __value.id
        return False
    
    def __hash__(self) -> int:
        return self.id
    
    @property
    def id(self) -> int:
        return self.guild.id

class Manager:
    gourps: set[GuildController]
    
    def __init__(self):
        self.gourps = set()
        
    def __contains__(self, __value: GuildController) -> bool:
        return __value in self.gourps
        
    def add_controller(self, controller: GuildController) -> bool:
        length = len(self.gourps)
        self.gourps.add(controller)
        return len(self.gourps) == length + 1
    
    def remove_controller(self, id: int) -> bool:
        length = len(self.gourps)
        self.gourps.remove(GuildController(id))
        return len(self.gourps) == length - 1
        

class GroupTest(unittest.TestCase):
    manager: Manager = Manager()
    def equal(self):
        group = GuildController(123)
        group2 = GuildController(123)
        
        self.assertEqual(group, group2)
        
    def same(self):
        group = GuildController(123)
        group2 = GuildController(123)
        
        self.assertEqual(self.manager.add_controller(group), True)
        self.assertEqual(self.manager.add_controller(group2), False)
        self.assertEqual(self.manager.remove_controller(123), True)