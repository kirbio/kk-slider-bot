from discord.ext.commands import CheckFailure, Context

import const


class SongNotPlaying(CheckFailure):
    def __init__(self):
        super().__init__(message='No song is being played')

class SongNotPaused(CheckFailure):
    def __init__(self):
        super().__init__(message='No song is being paused')
        
class NotInSameVoice(CheckFailure):
    def __init__(self):
        super().__init__(message='You must be in the same voice channel with the bot')

def is_admin(ctx: Context):
    return ctx.author.display_name in const.ADMIN_LIST

def is_in_same_vc(ctx: Context):
    if ctx.voice_client: # if bot has joined VC
        if ctx.author.voice and ctx.author.voice.channel == ctx.voice_client.channel: # check if author has joined VC and it's the same one with the bot
            return True
    elif ctx.author.voice: # if bot has not joined VC yet but author did, this check does nothing (first-time call)
        return True
    raise NotInSameVoice()

def is_playing_song(ctx: Context) -> bool:
    return ctx.voice_client and ctx.voice_client.is_playing()

def is_paused(ctx: Context) -> bool:
    return ctx.voice_client and ctx.voice_client.is_paused()
        
def check_is_playing_song(ctx: Context):
    if is_playing_song(ctx):
        return True 
    else:
        raise SongNotPlaying()
        
def check_is_paused(ctx: Context):
    if is_paused(ctx):
        return True 
    else:
        raise SongNotPaused()
    
def has_joined_vc(ctx: Context):
    return True if ctx.voice_client else False