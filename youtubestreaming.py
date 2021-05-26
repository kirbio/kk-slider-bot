import youtube_dl
import discord
import asyncio

youtube_dl.utils.bug_reports_message = lambda: ''


ytdl_format_options = {
    'format': 'bestaudio/best',
    'outtmpl': '%(extractor)s-%(id)s-%(title)s.%(ext)s',
    'restrictfilenames': True,
    'noplaylist': True,
    'nocheckcertificate': True,
    'ignoreerrors': False,
    'logtostderr': False,
    'quiet': True,
    'no_warnings': True,
    'default_search': 'auto',
    'youtube_include_dash_manifest': False,
    'source_address': '0.0.0.0' # bind to ipv4 since ipv6 addresses cause issues sometimes
}

ffmpeg_options = {
    'before_options': '-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5', 'options': '-vn'
}

ytdl = youtube_dl.YoutubeDL(ytdl_format_options)

class YTDLSource(discord.PCMVolumeTransformer):
    def __init__(self, source, *, data, volume=0.5):
        super().__init__(source, volume)

        self.data = data

        self.title = data.get('title')
        self.url = data.get('url')

    @classmethod
    async def from_url(cls, url, *, loop=None, stream=False, options=None):
        loop = loop or asyncio.get_event_loop()
        data = await loop.run_in_executor(None, lambda: ytdl.extract_info(url, download=not stream))

        if 'entries' in data:
            # take first item from a playlist
            data = data['entries'][0]

        filename = data['url'] if stream else ytdl.prepare_filename(data)
        ffmpeg_options['options'] = parse_ffmpeg_options(options)
        print(ffmpeg_options['options'])
        return cls(discord.FFmpegPCMAudio(filename, **ffmpeg_options), data=data)

def extract_info(url):
    '''
    song keys : (['id', 'uploader', 'uploader_id', 'uploader_url', 'channel_id', 'channel_url', 'upload_date', 'license', 'creator', 'title', 'alt_title', 'thumbnails', 'description', 'categories', 'tags', 'subtitles', 'automatic_captions', 'duration', 'age_limit', 'annotations', 'chapters', 'webpage_url', 'view_count', 'like_count', 'dislike_count', 'average_rating', 'formats', 'is_live', 'start_time', 'end_time', 'series', 'season_number', 'episode_number', 'track', 'artist', 'album', 'release_date', 'release_year', 'extractor', 'webpage_url_basename', 'extractor_key', 'n_entries', 'playlist', 'playlist_id', 'playlist_title', 'playlist_uploader', 'playlist_uploader_id', 'playlist_index', 'thumbnail', 'display_id', 'requested_subtitles', 'format_id', 'url', 'player_url', 'ext', 'format_note', 'acodec', 'abr', 'container', 'asr', 'filesize', 'fps', 'height', 'tbr', 'width', 'vcodec', 'downloader_options', 'format', 'protocol', 'http_headers'])
    '''
    data = ytdl.extract_info(url, download=False)
    if 'entries' in data:
        print('playlist found : {} videos'.format(len(data['entries'])))
        return data['entries']
        # data = data['entries'][0]
    return [data]

def parse_ffmpeg_options(options=None):
    '''
    optlist
    -s S    playback speed
    -r      reverse
    '''
    opt_str = '-vn '
    if options:
        opt_str += '-filter:a '
        filter = []
        for k,v in options:
            if k == '-s':
                filter.append('atempo={}'.format(v))
            if k == '-r':
                filter.append('areverse')
        opt_str += ','.join(filter)
    return opt_str