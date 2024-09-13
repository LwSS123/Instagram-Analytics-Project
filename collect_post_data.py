import instaloader
import csv

L = instaloader.Instaloader()

with open('allpostsdata(10_cat_cafe).csv', 'w', newline='', encoding='utf-8') as file:
    writer = csv.writer(file)
    writer.writerow(['Username', 'Post Date', 'Content', 'Like Count'])

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
        try:
            # Load the profile without login
            profile = instaloader.Profile.from_username(L.context, username)
            for post in profile.get_posts():
                post_date = post.date_utc.strftime('%Y-%m-%d %H:%M:%S')  
                content = post.caption if post.caption else "No caption"
                like_count = post.likes

                writer.writerow([username, post_date, content, like_count])
            
            print(f"Data fetched successfully for {username}")

        except Exception as e:
            print(f"Failed to fetch data for {username}: {str(e)}")

