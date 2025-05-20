import instaloader
from datetime import datetime

# Function to check if a profile is fake
def is_fake_profile(profile):
    # Check if the profile is private
    if profile.is_private:
        return False  # Assume private profiles are real

    # Check follower-to-following ratio
    if profile.followers < 100 and profile.followees > 1000:
        return True  # Likely fake

    # Check if bio is empty or too short
    if not profile.biography or len(profile.biography) < 10:
        return True  # Likely fake

    # Check if the account is new (less than 30 days old)
    try:
        account_age = (datetime.now() - profile.created_at).days
        if account_age < 30:
            return True  # Likely fake
    except AttributeError:
        print("Account creation date not available. Skipping account age check.")

    return False  # Assume real

# Create an Instaloader object
L = instaloader.Instaloader()

# Input Instagram username
username = input("Enter Instagram username: ")

# Fetch profile data
profile = instaloader.Profile.from_username(L.context, username)

# Print profile details
print("\nProfile Details:")
print("Username:", profile.username)
print("Followers:", profile.followers)
print("Following:", profile.followees)
print("Number of Posts:", profile.mediacount)
print("Bio:", profile.biography)
print("Is Private:", profile.is_private)

# Try to print account creation date (if available)
try:
    print("Account Created:", profile.created_at)
except AttributeError:
    print("Account creation date not available.")

# Check if the profile is fake
if is_fake_profile(profile):
    print("\nThis profile is likely FAKE.")
else:
    print("\nThis profile is likely REAL.")