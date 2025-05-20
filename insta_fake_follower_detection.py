import pandas as pd
import matplotlib.pyplot as plt
import random

# -----------------------------
# Instagram Fake Follower Detection
# -----------------------------

def generate_dummy_followers(num_followers=50):
    """
    Generate a DataFrame with dummy follower data.
    Each follower has: username, posts, followers, following, has_profile_pic, bio
    """
    followers = []
    for i in range(num_followers):
        username = f"user_{i+1}"
        posts = random.choices([0, random.randint(1, 10), random.randint(11, 100)], [0.2, 0.5, 0.3])[0]
        followers_count = random.randint(0, 1000)
        following_count = random.randint(0, 3000)
        has_profile_pic = random.choices([True, False], [0.85, 0.15])[0]
        bio = random.choices(["", f"Bio of {username}"], [0.3, 0.7])[0]
        followers.append({
            "username": username,
            "posts": posts,
            "followers": followers_count,
            "following": following_count,
            "has_profile_pic": has_profile_pic,
            "bio": bio
        })
    return pd.DataFrame(followers)

def calculate_fake_score(row):
    """
    Calculate a fake score (0 to 1) for a follower based on heuristics.
    """
    score = 0
    # Low number of posts (0 or 1)
    if row['posts'] <= 1:
        score += 0.3
    # High following-to-follower ratio (>2)
    if row['followers'] == 0:
        ratio = float('inf')
    else:
        ratio = row['following'] / (row['followers'] + 1e-6)
    if ratio > 2:
        score += 0.3
    # Missing profile picture
    if not row['has_profile_pic']:
        score += 0.2
    # Missing bio
    if not row['bio']:
        score += 0.2
    return min(score, 1.0)

def main():
    print("=== Instagram Fake Follower Detection ===")
    username = input("Enter a public Instagram username: ")
    print(f"\nSimulating followers for @{username}...\n")

    # Simulate or load follower data
    df = generate_dummy_followers(num_followers=50)

    # Calculate fake score for each follower
    df['fake_score'] = df.apply(calculate_fake_score, axis=1)
    df['label'] = df['fake_score'].apply(lambda x: 'Fake' if x > 0.5 else 'Real')

    # Output pie chart
    counts = df['label'].value_counts()
    plt.figure(figsize=(6, 6))
    plt.pie(counts, labels=counts.index, autopct='%1.1f%%', colors=['#ff9999','#66b3ff'])
    plt.title(f"Fake vs Real Followers for @{username}")
    plt.show()

    # List suspicious accounts
    suspicious = df[df['label'] == 'Fake'].copy()
    if not suspicious.empty:
        print("Suspicious (Fake) Followers:")
        print(suspicious[['username', 'fake_score']].assign(fake_score_pct=lambda x: (x['fake_score']*100).round(1)).rename(columns={'fake_score_pct': 'Fake Score (%)'}).to_string(index=False))
    else:
        print("No suspicious followers detected.")

if __name__ == "__main__":
    main()
