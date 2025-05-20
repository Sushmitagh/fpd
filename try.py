import requests
from instagrapi import Client
import pandas as pd

class FakeProfileDetector:
    def __init__(self):
        self.cl = Client()
        self.fake_indicator_threshold = 0.6
        
    def login(self, username, password):
        try:
            self.cl.login(username, password)
            return True
        except Exception as e:
            print(f"Login failed: {e}")
            return False

    def get_followers(self):
        user_id = self.cl.user_id
        followers = self.cl.user_followers(user_id)
        return followers

    def analyze_profile(self, user):
        # Calculate fake probability based on multiple factors
        fake_score = 0
        indicators = {}
        
        # Check profile characteristics
        indicators['is_private'] = user.is_private
        indicators['follower_count'] = user.follower_count
        indicators['following_count'] = user.following_count
        indicators['post_count'] = user.media_count
        indicators['has_profile_pic'] = bool(user.profile_pic_url)
        indicators['username_digits'] = sum(c.isdigit() for c in user.username)
        indicators['fullname_length'] = len(user.full_name) if user.full_name else 0
        
        # Calculate fake score
        if indicators['is_private']:
            fake_score += 0.2
            
        if indicators['follower_count'] < 100:
            fake_score += 0.3
            
        if indicators['following_count'] > 1000:
            fake_score += 0.4
            
        if indicators['post_count'] < 3:
            fake_score += 0.3
            
        if not indicators['has_profile_pic']:
            fake_score += 0.25
            
        if indicators['username_digits'] > 4:
            fake_score += 0.15
            
        return {
            'username': user.username,
            'fake_score': min(fake_score, 1.0),
            'is_fake': fake_score >= self.fake_indicator_threshold,
            'indicators': indicators
        }

    def analyze_followers(self):
        followers = self.get_followers()
        results = []
        
        for user_id in followers.keys():
            try:
                user = self.cl.user_info(user_id)
                result = self.analyze_profile(user)
                results.append(result)
            except Exception as e:
                print(f"Error analyzing {user_id}: {e}")
                
        return pd.DataFrame(results)

if __name__ == "__main__":
    detector = FakeProfileDetector()
    
    # User login
    username = input("Enter Instagram username: ")
    password = input("Enter Instagram password: ")
    
    if detector.login(username, password):
        print("Login successful! Analyzing followers...")
        df = detector.analyze_followers()
        print("\nFake Profile Analysis Results:")
        print(df[['username', 'is_fake', 'fake_score']])
        
        fake_profiles = df[df['is_fake']]
        print(f"\nDetected {len(fake_profiles)} potential fake profiles")
    else:
        print("Failed to login. Please check your credentials.")