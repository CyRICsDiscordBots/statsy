import discord
from discord.ext import commands
import asyncio
from colorthief import ColorThief
from urllib.parse import urlparse
import io
import os
import json

from pymongo import MongoClient
client = MongoClient("mongodb://oommenb:Manny123@cluster0bbb-shard-00-00-ffddp.mongodb.net:27017,cluster0bbb-shard-00-01-ffddp.mongodb.net:27017,cluster0bbb-shard-00-02-ffddp.mongodb.net:27017/test?ssl=true&replicaSet=Cluster0bbb-shard-0&authSource=admin")

db = client.test
games = ['clash_royale', 'clash_of_clans', 'overwatch']
user_tags = db.usertags.insert_one({"user tags":"here", "clash_royale": {}, "clash_of_clans": {}, "overwatch": {}})

class CustomContext(commands.Context):
    '''Custom Context class to provide utility.'''
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

    @property
    def session(self):
        '''Returns the bot's aiohttp client session'''
        return self.bot.session

    def delete(self):
        '''shortcut'''
        return self.message.delete()

    async def purge(self, *args, **kwargs):
        '''Shortcut to channel.purge'''
        await self.channel.purge(*args, **kwargs)

    @staticmethod
    def valid_image_url(url):
        '''Checks if a url leads to an image.'''
        types = ['.png', '.jpg', '.gif', '.webp']
        parsed = urlparse(url)
        if any(parsed.path.endswith(i) for i in types):
            return url.replace(parsed.query, 'size=128')
        return False

    async def get_dominant_color(self, url=None, quality=10):
        '''
        Returns the dominant color of an image from a url
        '''
        av = self.author.avatar_url
        url = self.valid_image_url(url or av)

        if not url:
            raise ValueError('Invalid image url passed.')
        try:
            async with self.session.get(url) as resp:
                image = await resp.read()
        except:
            return discord.Color.default()

        with io.BytesIO(image) as f:
            try:
                color = ColorThief(f).get_color(quality=quality)
            except:
                return discord.Color.dark_grey()
            
        return discord.Color.from_rgb(*color)

    def load_json(self, path=None):
        with open(path or 'data/stats.json') as f:
            return json.load(f)

    def save_json(self, data, path=None):
        with open(path or 'data/stats.json', 'w') as f:
            f.write(json.dumps(data, indent=4))

    
    def save_db (self, key, value):
        user_tags = db.usertags.update_one({"user tags" : "here"}, {'$set': {key : value}}, upsert=True)
        
        
    def save_tag(self, tag, game, id=None):
        id = id or self.author.id
        game = game.lower()
        
        user_tags = db.usertags.update_one({"user tags" : "here"}, {'$set': {str(game) + '.' + str(id) : str(tag)}}, upsert=True)
        print("successful")
        

    def add_tag(self, tag, game, id=None):
        id = id or self.author.id
        
        if db.usertags.find({ str(game) + '.' + str(id): { '$exists': True, '$ne': None } }) is None:
            user_tags = db.usertags.update_one({"user tags" : "here"}, {'$set': {str(game) + '.' + str(id) : str(tag)}}, upsert=True)
        else: 
            pass

    def remove_tag(self, tag, game, id=None):
        id = id or self.author.id
        game = game.lower()
        if game in games:
            user_tags = db.usertags.update({"user tags" : "here"}, { '$unset' : {str(game) + '.' + str(id) : str(tag)} });


    def get_tag(self, game, id=None, *, index=0):
        id = id or self.author.id
        if game in games:
            tag = db.usertags.distinct(str(game) + '.' + str(id))
            return tag[0]

    @staticmethod
    def paginate(text: str):
        '''Simple generator that paginates text.'''
        last = 0
        pages = []
        for curr in range(0, len(text)):
            if curr % 1980 == 0:
                pages.append(text[last:curr])
                last = curr
                appd_index = curr
        if appd_index != len(text)-1:
            pages.append(text[last:curr])
        return list(filter(lambda a: a != '', pages))
