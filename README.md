# kk-slider-bot
Personal music streaming bot for HONK and TAE.

## Dependencies
- Python 3
- Discord.py package
- youtube-dl package
- ffmmpeg in the same directory
- getopt package

## Running a bot
You need to create `const.py` first in order to run a bot. Inside this file contains your discord bot token
```
BOT_TOKEN = '<YOUR DISCORD BOT TOKEN>'
```

After that, simply start the bot by simply run kksliderbot.py

Make sure to give a bot needed permission in your server as well.

## Usage
### Playing / Pausing
```
!play <URL>
```
where `<URL>` can be either Youtube URL or query word (just like when you search in Youtube) such as
```
!play https://www.youtube.com/watch?v=dQw4w9WgXcQ
!play rickroll
```

When you type `play` command while another song is playing, the new song will be queued and play next when the current song ends.

#### Extra parameters

- `-s <SPEED>` where `SPEED` is between 0.5 and 2
-  `-r` to reverse a song


You can also use Youtube playlist as a URL. All songs in a playlist will be queued.

To pause a song, type
```
!pause
```

To skip current song and play next song in queue, type
```
!skip
```

To stop playing current song, type
```
!stop
```

### Loop a song
You can also play/queue a song with loop function using `loop` command instead of `play`
```
!loop [URL]
```
if `URL` is not given, the bot will loop current song.


### Queue management
To see all songs in queue, type
```
!queue
```

To remove a specific song in queue, type
```
!pop <INDEX>
```
where `<INDEX>` is the index of the song you want to remove. (Use `!q` to see an index of a song.)


### Other features
To disconnect the bot, type (as admin)
```
!dc
```
