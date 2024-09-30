
import instaloader

L = instaloader.Instaloader()

ig_list = [
        "meow_art_coffee",
        "urban.cafe.hk",
        "catiocatiocafe",
        "nekoscube",
        "catislandcafe",
        "catstearoom",
        "honeymoon_pet",
        "manymo_cafe",
        "acupofcat_cafe",
        "meow_plus_space"
    ]

for username in ig_list:
    profile = instaloader.Profile.from_username(L.context, username)
    posts = profile.get_posts()

    earliest_post_date = None

    for post in posts:
        if earliest_post_date is None or post.date < earliest_post_date:
            earliest_post_date = post.date

    if earliest_post_date:
        print(f"{username}: {earliest_post_date}")
    else:
        print(f"{username}: No posts found.")