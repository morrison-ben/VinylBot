# VinylBot

I started collecting records a few years ago, and it's recently become a pretty big hobby of mine. One day, I stumbled upon a useful subreddit called *VinylReleases* where users make posts about new vinyl releases. I found myself checking this subreddit far too often, looking for new releases from artists I enjoy listening to. Turning notifications on wasn't helpful either, as I would then be spammed with a lot of releases I don't care about. What if there was a way to get notified of these releases, but only for artists that I cared about?

Luckily, these posts tend to follow a certain format - the title contains the name of the artist and the album they are releasing, and the post itself contains a link to the page where the vinyl can be purchased. Since I planned on doing an artist-based match and linking the URL, this gave me all the info I needed. I listen to pretty much all of my music on Spotify, so I used their API to find artists that I like. This was achieved by grabbing a list of all my liked songs, then forming a unique set of artists from that list. I needed a place to store these artists, so I used MongoDB for that.

I use the Twilio API to send a text message to my phone with a link whenever there's a match. The final result is a nice, compact text message sent to my phone with a link to the URL where I can purchase the release. My main goal was to stop checking the subreddit so much, as it was a giant waste of time - the completion of this project helped me achieve that goal. It also gives me the chance to purchase vinyl that may sell out quickly. Like any supply and demand market, the resale prices can be driven way up once a sought after item is sold out. The bot runs every hour, so I typically have a chance at purchasing before it sells out...this is a nice perk as well.


## Finished State

![IMG_0976](https://github.com/user-attachments/assets/573f24f1-9e8b-4335-ae0c-a8a502dd609d)
