import instaloader
import csv
import pandas as pd
import time
from collections import Counter
import re
import seaborn as sns
import matplotlib.pyplot as plt
import tkinter as tk
from tkinter import scrolledtext

###########################

file1_allposts = pd.read_csv('allpostsdata(10_cat_cafe).csv')
file2_phan = pd.read_csv('datas_from_phantombuster.csv')

print("Columns in 'allpostdata(10_cat_Cafe).csv':")
print(file1_allposts.columns.tolist())
print("\nColumns in 'datas_from_phantombuster.csv':")
print(file2_phan.columns.tolist())

na_columns_data1 = file1_allposts.columns[file1_allposts.isna().any()].tolist()
print("\nColumns with NA in 'allpostdata(10_cat_Cafe).csv':")
print(na_columns_data1)

na_columns_data2 = file2_phan.columns[file2_phan.isna().any()].tolist()
print("\nColumns with NA in 'datas_from_phantombuster.csv':")
print(na_columns_data2)

###########################

earliestPostDate = file2_phan[['profileName','earliestPostDate', 'dateJoined']]
print(earliestPostDate)

earliestPostDate['dateJoined'] = pd.to_datetime(earliestPostDate['dateJoined'], format='%b-%y').dt.strftime('%m/%Y')

earliestPostDate['earliestPostDate'] = pd.to_datetime(earliestPostDate['earliestPostDate'], errors='coerce', exact=False)
earliestPostDate['earliestPostDate'] = earliestPostDate['earliestPostDate'].dt.strftime('%d/%m/%Y')
earliestPostDate['earliestPostDate'].fillna(earliestPostDate['dateJoined'].apply(lambda x: f"01-{x.replace('/', '-')[:-5]}{x[-5:]}"), inplace=True)

earliestPostDate.rename(columns={'profileName': 'Username'}, inplace=True)
print(earliestPostDate)

###########################

df1_allpost = file1_allposts.copy()
df2_phan = file2_phan.copy()

df2_phan['earliestPostDate'] = earliestPostDate['earliestPostDate']

na_columns_df2_phan = df2_phan.columns[df2_phan.isna().any()].tolist()
print("\nColumns with NA in 'datas_from_phantombuster.csv':")
print(na_columns_df2_phan)

###########################

username_counts = df1_allpost['Username'].value_counts().reset_index()
username_counts.columns = ['Username', 'ig_posts_fetched']

total_posts = df2_phan[['profileName', 'postsCount']]

# Merge and rename columns to avoid redundancy
combine_ig_post_count = pd.merge(username_counts, total_posts, left_on='Username', right_on='profileName', how='left')
combine_ig_post_count.drop('profileName', axis=1, inplace=True)  # Remove redundant column after merge
combine_ig_post_count.columns = ['Username', 'ig_posts_fetched', 'Total_ig_posts']

combine_ig_post_count['data_acquisition_success_rate'] = combine_ig_post_count['ig_posts_fetched'] / combine_ig_post_count['Total_ig_posts'] * 100
combine_ig_post_count['data_acquisition_success_rate'] = combine_ig_post_count['data_acquisition_success_rate'].apply(lambda x: f"{round(x)}%")
print(combine_ig_post_count)

###########################

ig_name_list = df1_allpost['Username']

average_post_likes = df1_allpost.groupby('Username')['Like Count'].mean().reset_index()
average_post_likes.rename(columns = {'Like Count' : 'average_post_like'}, inplace =True)
average_post_likes['average_post_like'] = average_post_likes['average_post_like'] .apply(lambda x :round(x))
print(average_post_likes)

###########################

df1_allpost['Post Date'] = pd.to_datetime(df1_allpost['Post Date'], errors='coerce')
df1_allpost = df1_allpost[df1_allpost['Content'] != 'No caption']
df1_allpost['Date'] = df1_allpost['Post Date'].dt.date
df1_allpost = df1_allpost.sort_values(by='Date').drop_duplicates(subset=['Username', 'Date'], keep='first')
df1_allpost.sort_values(by=['Username', 'Post Date'], inplace=True)
df1_allpost['DateDiff(days)'] = df1_allpost.groupby('Username')['Post Date'].diff().dt.days
df1_allpost['DateDiff(days)'] = df1_allpost['DateDiff(days)'].fillna(0)
average_date_diff = df1_allpost.groupby('Username', as_index=False)['DateDiff(days)'].mean()
average_date_diff['DateDiff(days)'] = average_date_diff['DateDiff(days)'].apply(lambda x : round(x))
print(average_date_diff)

###########################
# Calculate the average date difference per user per year

df1_allpost['Post Date'] = pd.to_datetime(df1_allpost['Post Date'], errors='coerce')
df1_allpost = df1_allpost[df1_allpost['Content'] != 'No caption']
df1_allpost['Date'] = df1_allpost['Post Date'].dt.date
df1_allpost = df1_allpost.drop_duplicates(subset='Date', keep='first')
df1_allpost.sort_values(by=['Username', 'Post Date'], inplace=True)
df1_allpost['DateDiff(days)'] = df1_allpost.groupby('Username')['Post Date'].diff().dt.days
df1_allpost['DateDiff(days)'] = df1_allpost['DateDiff(days)'].fillna(0)
df1_allpost['Year'] = df1_allpost['Post Date'].dt.year
average_date_diff_year = df1_allpost.groupby(['Username', 'Year'], as_index=False)['DateDiff(days)'].mean()
average_date_diff_year['DateDiff(days)'] = average_date_diff_year['DateDiff(days)'].apply(lambda x: round(x))
average_date_diff_year['Year'] = average_date_diff_year['Year'].apply(lambda x: round(x))

print(average_date_diff_year)

###########################

plt.figure(figsize=(10, 6))
sns.lineplot(data=average_date_diff_year, x='Year', y='DateDiff(days)', hue='Username', marker='o')
plt.title('Average Post Date Difference by Year and User')
plt.xlabel('Year')
plt.ylabel('Average Date Difference (days)')
plt.show()

###########################

earliestPostDate['earliestPostDate'] = earliestPostDate['earliestPostDate'].str.replace('-', '/')
earliestPostDate['earliestPostDate'] = pd.to_datetime(earliestPostDate['earliestPostDate'], format='%d/%m/%Y', errors='coerce')
today = pd.to_datetime('today').normalize()  
earliestPostDate['days_from_today(days)'] = (today - earliestPostDate['earliestPostDate']).dt.days

print(earliestPostDate)

###########################
df1_allpost_c = file1_allposts.copy()

def extract_hashtags(content):
    hashtags = []
    if '#' in content:
        # Split the content into parts by spaces to parse each individual word
        parts = content.split()
        for part in parts:
            # Check if the part starts with '#' and then process the content until a stop character
            if part.startswith('#'):
                # Find the first occurrence of a comma or newline within the hashtag
                end_index = min(part.find(','), part.find('\n'))
                if end_index == -1:  # If neither comma nor newline is found
                    hashtags.append(part)
                else:
                    hashtags.append(part[:end_index])
    if not hashtags:
        return None, 0  
    return hashtags, len(hashtags)

df1_allpost_c[['hashtags', 'hashtag_count']] = df1_allpost_c['Content'].apply(extract_hashtags).apply(pd.Series)

###########################

df1_allpost_c['hashtag_count'].fillna(0, inplace=True) 
average_hashtags_per_user = df1_allpost_c.groupby('Username')['hashtag_count'].mean()
average_hashtags_per_user_df = average_hashtags_per_user.reset_index()
average_hashtags_per_user_df.columns = ['Username', 'avg_hashtag_count']
average_hashtags_per_user_df['avg_hashtag_count'] = average_hashtags_per_user_df['avg_hashtag_count'].apply(lambda x: round(x))

print(average_hashtags_per_user_df)
###########################

def excel_date_to_datetime(excel_date):
    return pd.Timestamp('1899-12-30') + pd.to_timedelta(excel_date, unit='D')

if df1_allpost_c['Post Date'].dtype in ['float64', 'int64']:
    df1_allpost_c['Post Date'] = df1_allpost_c['Post Date'].apply(excel_date_to_datetime)
else:
    # Try to parse as day/month/year format if they are not serial numbers
    df1_allpost_c['Post Date'] = pd.to_datetime(df1_allpost_c['Post Date'], format='%d/%m/%Y', errors='coerce')

df1_allpost_c['Year'] = df1_allpost_c['Post Date'].dt.year
average_hashtags_per_user = df1_allpost_c.groupby('Username')['hashtag_count'].mean()

average_hashtags_per_user_per_year = df1_allpost_c.groupby(['Username', 'Year'])['hashtag_count'].mean().reset_index()
average_hashtags_per_user_per_year.columns = ['Username', 'Year', 'average_hashtags_per_year']
average_hashtags_per_user_per_year['average_hashtags_per_year'] = average_hashtags_per_user_per_year['average_hashtags_per_year'].apply(lambda x: round(x))
average_hashtags_per_user_per_year['Year'] = average_hashtags_per_user_per_year['Year'].apply(lambda x: round(x))

print(average_hashtags_per_user_per_year)

###########################

plt.figure(figsize=(12, 8))
sns.lineplot(data=average_hashtags_per_user_per_year, x='Year', y='average_hashtags_per_year', hue='Username', marker='o')
plt.title('Average Hashtags Used Per User Per Year')
plt.xlabel('Year')
plt.ylabel('Average Hashtags Per Year')
plt.show()

###########################

df1_allpost_c['hashtags'] = df1_allpost_c['hashtags'].astype(str)
# Remove '#' and other undesired characters from the hashtags
df1_allpost_c['hashtags'] = df1_allpost_c['hashtags'].str.replace('[#\[\]\'"]', '', regex=True)
# Remove all types of whitespace from each hashtag entry
df1_allpost_c['hashtags'] = df1_allpost_c['hashtags'].str.replace(r'\s+', '', regex=True)
df1_allpost_c['hashtags_list'] = df1_allpost_c['hashtags'].str.split(',')
# Extract all unique hashtags
all_hashtags = set()
df1_allpost_c['hashtags_list'].apply(lambda tags: all_hashtags.update(tags))
all_hashtags = list(all_hashtags)  # Convert set back to list to see all unique hashtags
print(all_hashtags)

###########################

# Analyze unique hashtags used by each user
user_hashtags = df1_allpost_c.groupby('Username')['hashtags_list'].sum()  # Aggregate tags by user
user_unique_hashtags = user_hashtags.apply(set)  # Convert lists to sets to remove duplicates
print(user_unique_hashtags)

###########################

# Find the most common hashtags
filtered_tags = [tag for sublist in df1_allpost_c['hashtags_list'] for tag in sublist if tag.lower() not in ['na', 'nan']]
tags_count = Counter(filtered_tags)
most_common_tags = tags_count.most_common(10)  # Get the top 10 most common tags
print(most_common_tags)

###########################

#Extract the names of the top tags from the most_common_tags
top_tags = [tag for tag, count in most_common_tags]

# calculate the percentage of top tags used by each user
def calculate_top_tag_percentage(user_tags):
    if not user_tags:  
        return 0.0
    # Count how many of the user's tags are in the list of top tags
    common_tag_count = sum(1 for tag in user_tags if tag in top_tags)
    percentage = (common_tag_count / len(user_tags)) * 100 if user_tags else 0
    return percentage

user_top_tag_percentage = user_unique_hashtags.apply(calculate_top_tag_percentage)
user_top_tag_percentage = user_top_tag_percentage.reset_index()
user_top_tag_percentage.columns = ['Username', 'top10_commontags_using_%']
user_top_tag_percentage['top10_commontags_using_%'] = user_top_tag_percentage['top10_commontags_using_%'].apply(lambda x :f'{round(x)}%')

print(f'Percentage of common hashtag usage by user:\n{user_top_tag_percentage}')
###########################

# removes words following a # until it encounters a newline, space, or punctuation like a comma
def remove_hashtag_content(text):
    # removes the hashtag and any text following it until a space, newline, or comma
    return re.sub(r'#\S+[\s,\n]', '', text)

df1_allpost_c['content_before_hashtag'] = df1_allpost_c['Content'].apply(remove_hashtag_content)
df1_allpost_c['word_count'] = df1_allpost_c['content_before_hashtag'].apply(lambda x: len(x.split()))
average_post_word_count_per_iguser = df1_allpost_c.groupby('Username')['word_count'].mean().reset_index()
average_post_word_count_per_iguser.columns = ['Username', 'average_post_word_count']
average_post_word_count_per_iguser['average_post_word_count'] = average_post_word_count_per_iguser['average_post_word_count'].apply(round)
total_post_count = df2_phan[['profileName', 'postsCount']].rename(columns={'profileName': 'Username', 'postsCount': 'Total_post_count'})
average_post_word_count_per_iguser = pd.merge(average_post_word_count_per_iguser, total_post_count, on='Username', how='left')
print(f'The average IG post word count per user: \n{average_post_word_count_per_iguser}')

###########################

hong_kong_places = [
    ("中環", "Central"),
    ("金鐘", "Admiralty"),
    ("灣仔", "Wan Chai"),
    ("銅鑼灣", "Causeway Bay"),
    ("北角", "North Point"),
    ("太古", "Taikoo"),
    ("西灣河", "Sai Wan Ho"),
    ("鰂魚涌", "Quarry Bay"),
    ("柴灣", "Chai Wan"),
    ("薄扶林", "Pok Fu Lam"),
    ("赤柱", "Stanley"),
    ("大潭", "Tai Tam"),
    ("香港仔", "Aberdeen"),
    ("旺角", "Mong Kok"),
    ("太子", "Prince Edward"),
    ("油麻地", "Yau Ma Tei"),
    ("佐敦", "Jordan"),
    ("尖沙咀", "Tsim Sha Tsui"),
    ("紅磡", "Hung Hom"),
    ("九龍城", "Kowloon City"),
    ("觀塘", "Kwun Tong"),
    ("鑽石山", "Diamond Hill"),
    ("九龍灣", "Kowloon Bay"),
    ("新蒲崗", "San Po Kong"),
    ("黃大仙", "Wong Tai Sin"),
    ("樂富", "Lok Fu"),
    ("荃灣", "Tsuen Wan"),
    ("元朗", "Yuen Long"),
    ("屯門", "Tuen Mun"),
    ("大埔", "Tai Po"),
    ("沙田", "Sha Tin"),
    ("粉嶺", "Fanling"),
    ("上水", "Sheung Shui"),
    ("馬鞍山", "Ma On Shan"),
    ("西貢", "Sai Kung"),
    ("清水灣", "Clear Water Bay"),
    ("天水圍", "Tin Shui Wai"),
    ("將軍澳", "Tseung Kwan O"),
    ("大嶼山", "Lantau Island"),
    ("東涌", "Tung Chung"),
    ("大澳", "Tai O")
]

flat_places = [place for sublist in hong_kong_places for place in sublist]
def count_unique_places(bio):
    found_places = set()
    for place in flat_places:
        if place in bio:
            found_places.add(place)
    return found_places

df2_phan['unique_places_bio'] = df2_phan['bio'].apply(count_unique_places)

profile_place_counts_bio = df2_phan.groupby('profileName')['unique_places_bio'].sum()

profile_place_counts_bio = profile_place_counts_bio.apply(len)
profile_place_counts_bio = profile_place_counts_bio.reset_index()
profile_place_counts_bio.columns = ['Username','place_mentions_in_bio']
print(profile_place_counts_bio)

###########################

df2_phan['unique_places_FN'] = df2_phan['fullName'].apply(count_unique_places)

profile_place_counts_FN = df2_phan.groupby('profileName')['unique_places_FN'].sum()

profile_place_counts_FN = profile_place_counts_FN.apply(len)
profile_place_counts_FN = profile_place_counts_FN.reset_index()
profile_place_counts_FN.columns = ['Username','place_mentions_in_fullName']
print(profile_place_counts_FN)

###########################

promotional_language = [
    ("學生優惠", "Student Discount"),
    ("抵", "Value"),
    ("最平", "Lowest Price"),
    ("不加", "No Extra Charge"),
    ("不收", "No Fee"),
    ("不設", "No Setup"),
    ("折扣", "Discount"),
    ("優惠", "Special Offer"),
    ("超值", "Super Value"),
    ("免", "Free"),
    ("平", "Cheap"),
    ("限量供應", "Limited Supply"),
    ("免費", "Free of Charge"),
    ("可", "can")  
]

flat_promotional_language = [word.lower() for sublist in promotional_language for word in sublist]

def count_promotional_language(content):
    content = content.lower()  
    found_promotional_language = set()
    for words in flat_promotional_language:
        if words in content:
            found_promotional_language.add(words)
    return found_promotional_language

df1_allpost_c['unique_PL_content'] = df1_allpost_c['Content'].apply(count_promotional_language)

def union_sets(sets):
    result_set = set()
    for s in sets:
        result_set |= s  # the union operation for sets
    return result_set

content_PL_counts = df1_allpost_c.groupby('Username')['unique_PL_content'].agg(union_sets)

# Convert the unioned sets to their lengths
content_PL_counts = content_PL_counts.apply(len).reset_index()
content_PL_counts.columns = ['Username', 'content_PL_counts']

print(content_PL_counts)

###########################
followers_count = df2_phan[['profileName', 'followersCount']]
followers_count.columns = ['Username', 'followersCount']
print(followers_count)

combine_ig_post_count.set_index('Username', inplace=True)
earliestPostDate.set_index('Username', inplace=True)
average_date_diff.set_index('Username', inplace=True)
user_top_tag_percentage.set_index('Username', inplace=True)
average_post_word_count_per_iguser.set_index('Username', inplace=True)
average_hashtags_per_user_df.set_index('Username', inplace=True)
average_post_likes.set_index('Username', inplace=True)
followers_count.set_index('Username', inplace=True)
content_PL_counts.set_index('Username', inplace=True)
profile_place_counts_bio.set_index('Username', inplace=True)
profile_place_counts_FN.set_index('Username', inplace=True)

dfs = [combine_ig_post_count, earliestPostDate, average_date_diff, user_top_tag_percentage, average_post_word_count_per_iguser, average_hashtags_per_user_df, average_post_likes, followers_count,content_PL_counts,profile_place_counts_bio, profile_place_counts_FN]
merged_df = pd.concat(dfs, axis=1, join='outer')

###########################

merged_df['top10_commontags_using_%'] = merged_df['top10_commontags_using_%'].str.replace('%', '').astype(float) / 100
correlation_matrix = merged_df[['Total_ig_posts', 'days_from_today(days)', 'DateDiff(days)', 'top10_commontags_using_%', 'average_post_word_count', 'avg_hashtag_count', 'average_post_like', 'followersCount','content_PL_counts','place_mentions_in_bio','place_mentions_in_fullName']].corr()
print(correlation_matrix)

###########################

# Define pairs of variables to plot
plot_pairs = [
    ('Total_ig_posts', 'followersCount'),
    ('Total_ig_posts', 'average_post_like'),
    ('average_post_word_count', 'followersCount'),
    ('average_post_word_count', 'average_post_like'),
    ('avg_hashtag_count', 'followersCount'),
    ('avg_hashtag_count', 'average_post_like'),
    ('days_from_today(days)', 'followersCount'),
    ('days_from_today(days)', 'average_post_like'),
    ('DateDiff(days)', 'followersCount'),
    ('DateDiff(days)', 'average_post_like'),
    ('top10_commontags_using_%', 'followersCount'),
    ('top10_commontags_using_%', 'average_post_like'),
    ('content_PL_counts', 'followersCount'),
    ('content_PL_counts', 'average_post_like'),
    ('place_mentions_in_bio', 'followersCount'),
    ('place_mentions_in_bio', 'average_post_like'),
    ('place_mentions_in_fullName', 'followersCount'),
    ('place_mentions_in_fullName', 'average_post_like')
]

# sns.set(style="whitegrid")

# # Determine the number of plots per figure (6 plots per figure)
# plots_per_figure = 6


# for i in range(0, len(plot_pairs), plots_per_figure):
#     fig, axes = plt.subplots(3, 2, figsize=(15, 20))  # Increase the figure size
#     fig.suptitle('Relationships between Instagram Metrics and User Engagement with Trend Lines', fontsize=16)
    
#     # Flatten the axes array and loop over it and the corresponding plot pairs
#     for ax, (x, y) in zip(axes.flat, plot_pairs[i:i+plots_per_figure]):
#         # Plot with regression line
#         sns.regplot(ax=ax, data=merged_df, x=x, y=y, scatter_kws={'alpha':0.5})
#         ax.set_title(f'{x} vs. {y}', fontsize=10)  # Smaller font size for subplot titles
#         ax.set_xlabel(x.replace('_', ' ').title(), fontsize=9)  # Smaller font size for x labels
#         ax.set_ylabel(y.replace('_', ' ').title(), fontsize=9)  # Smaller font size for y labels
#         ax.tick_params(axis='x', rotation=45, labelsize=8)  # Smaller font size for x ticks
#         ax.tick_params(axis='y', rotation=45, labelsize=8)  # Smaller font size for y ticks
    
#     # Adjust layout to prevent overlap and ensure titles and labels are clear
#     plt.tight_layout(rect=[0, 0.03, 1, 0.95])
#     plt.subplots_adjust(wspace=0.3, hspace=0.6)  # Adjust spacing to prevent overlap
#     plt.show()

#     # Handle potentially fewer subplots in the final figure
#     if len(plot_pairs[i:i+plots_per_figure]) < plots_per_figure:
#         for j in range(len(plot_pairs[i:i+plots_per_figure]), plots_per_figure):
#             axes.flat[j].set_visible(False)

###########################

def search_hashtags():
    keywords = entry.get().lower().split(',')
    keywords = [keyword.strip() for keyword in keywords]
    results_users.delete(1.0, tk.END)
    results_hashtags.delete(1.0, tk.END)
    user_text = ""
    hashtag_text = ""
    found = False

    for username, hashtags in user_unique_hashtags.items():
        # Check if any keyword is in the hashtags of the user
        if any(keyword in hashtag.lower() for keyword in keywords for hashtag in hashtags):
            user_text += f"{username}\n"
            # Filter and display hashtags not including the searched keywords
            other_hashtags = [hashtag for hashtag in hashtags if not any(keyword in hashtag.lower() for keyword in keywords)]
            hashtag_text += f"{username}'s other hashtags: {', '.join(other_hashtags)}\n\n"
            found = True
    
    # Handle case when no users are found
    if not found:
        user_text = "No users found using the specified hashtags."
    
    results_users.insert(tk.END, user_text)
    results_hashtags.insert(tk.END, hashtag_text)

# Setting up the main window
root = tk.Tk()
root.title("Hashtag Search")

# Entry widget for input
entry = tk.Entry(root, width=50, font=('Arial', 12))
entry.pack(pady=20)

# Search button
search_button = tk.Button(root, text="Search", command=search_hashtags, font=('Arial', 12))
search_button.pack(pady=10)

# Label and scrollable text area for displaying users
label_users = tk.Label(root, text="Users who have used this hashtag", font=('Arial', 14))
label_users.pack(pady=(20, 0))
results_users = scrolledtext.ScrolledText(root, width=40, height=10, font=('Arial', 12))
results_users.pack(pady=(0, 20))

# Label and scrollable text area for displaying other hashtags used by users
label_hashtags = tk.Label(root, text="Other Hashtags Used by Users", font=('Arial', 14))
label_hashtags.pack(pady=(0, 0))
results_hashtags = scrolledtext.ScrolledText(root, width=60, height=10, font=('Arial', 12))
results_hashtags.pack(pady=20)

# Run the main event loop
root.mainloop()