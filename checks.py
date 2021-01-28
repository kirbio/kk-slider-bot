import const

def is_admin(ctx):
    return ctx.author.display_name in const.ADMIN_LIST

def is_in_same_vc(ctx):
    if ctx.voice_client: # if bot has joined VC
        if ctx.author.voice and ctx.author.voice.channel == ctx.voice_client.channel: # check if author has joined VC and it's the same one with the bot
            return True
    elif ctx.author.voice: # if bot has not joined VC but author did
        return True
    return False