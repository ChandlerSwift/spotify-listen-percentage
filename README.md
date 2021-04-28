# Spotify listen percentage

### Motivation

I have a few songs I listen to very frequently. Enough that I wonder, "Does the
amount I stream this song have a substantial effect on the song's popularity?"
Here's an attempt to gather some data on that.

### Prereqs
Spotify API key:
Create an app at https://developer.spotify.com/dashboard/

last.fm API key:
https://www.last.fm/api/account/create (or https://www.last.fm/api/accounts if you already have one)

Put both of these in `secrets.py`.

Spotify's API doesn't let you grab song popularity numbers directly, so I'm
using the jar from the latest release of https://github.com/evilarceus/sp-playcount-librespot
That needs to be available while this script is running.
