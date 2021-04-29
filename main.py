#!/usr/bin/env python3

import pylast
import spotify.sync as spotify
import requests
import time
import pickle

import secrets

lastfm_client = pylast.LastFMNetwork(api_key=secrets.lastfm["api_key"], api_secret=secrets.lastfm["secret"])

spotify_client = spotify.Client(secrets.spotify["client_id"], secrets.spotify["client_secret"])

lastfm_top_tracks = lastfm_client.get_user("chandlerswift").get_top_tracks(stream=True, limit=None)

track_data=[]
find_manually=[]
could_not_find_track=[]
failed = []
zerodivides = []

for i, lastfm_track in enumerate(lastfm_top_tracks):
    try:
        try:
            spotify_track = spotify_client.search(
                f"{lastfm_track.item.artist.name} {lastfm_track.item.title}", types=["track"], limit=1
            ).tracks[0]
        except IndexError:
            print(f"Could not find track {lastfm_track.item.title}")
            could_not_find_track.append(lastfm_track)
            continue

        res = requests.get(f"http://localhost:8080/albumPlayCount?albumid={spotify_track.album.id}").json()

        found_track = None
        for spotify_disc in res['data']['discs']:
            for spotify_track_info in spotify_disc['tracks']:
                if spotify_track_info['name'].lower() == lastfm_track.item.title.lower():
                    found_track = spotify_track_info

        if found_track:
            found_track['my_playcount'] = lastfm_track.weight
            track_data.append(found_track)
            print(f"{i}. {found_track['name']}: {found_track['my_playcount']}/{found_track['playcount']} ({100*found_track['my_playcount']/found_track['playcount']:.3f}%)")
        else:
            find_manually.append(lastfm_track)
            print(f"No track {lastfm_track.item.title} found on album {spotify_track.album.name} (will find later)")

        time.sleep(2) # I don't think Spotify's going to ban me, but doesn't hurt
                    # to be a little extra careful!
    except ZeroDivisionError:
        zerodivides.append(lastfm_track)
    except Exception as e:
        failed.append(lastfm_track)
        # Sometimes things crash. This might give me a chance to continue, if I want.
        print(f"{e} on {lastfm_track.item.title}")
        input("press enter to continue…")

for i, lastfm_track in enumerate(find_manually):
    try:
        spotify_track = spotify_client.search(
            f"{lastfm_track.item.artist.name} {lastfm_track.item.title}", types=["track"], limit=1
        ).tracks[0]

        res = requests.get(f"http://localhost:8080/albumPlayCount?albumid={spotify_track.album.id}").json()

        found_track = None
        print(f"looking for {lastfm_track.item.title}")
        for spotify_disc in res['data']['discs']:
            for j, spotify_track_info in enumerate(spotify_disc['tracks']):
                print(f"  {j}. {spotify_track_info['name']}")
            answer = input("Track number? (empty if none match) >")
            if answer:
                found_track = spotify_disc['tracks'][int(answer)]

        if found_track:
            found_track['my_playcount'] = lastfm_track.weight
            track_data.append(found_track)
            print(f"{i/len(find_manually)}. {found_track['name']}: {found_track['my_playcount']}/{found_track['playcount']} ({100*found_track['my_playcount']/found_track['playcount']:.3f}%)")
        else:
            print("Still not found, ignoring")

        time.sleep(2) # I don't think Spotify's going to ban me, but doesn't hurt
                    # to be a little extra careful!
    except Exception as e:
        # Sometimes things crash. This might give me a chance to continue, if I want.
        print(e)
        input("continue? ")

pickle.dump(track_data, open("track_data.pickle", "wb"))
