import instaloader
import getpass
import time
import pandas as pd
import numpy as np
from datetime import datetime
import re
import logging
import os
import traceback
from tqdm import tqdm
import pickle
import random

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class InstagramFakeProfileDetector:
    def __init__(self):
        self.L = instaloader.Instaloader(
            download_pictures=False,
            download_videos=False, 
            download_video_thumbnails=False,
            download_geotags=False,
            download_comments=False,
            save_metadata=False
        )
        self.user_profile = None
        self.followers_data = []
        
    def login(self, username=None, password=None):
        """Login to Instagram"""
        try:
            if not username:
                username = input("Enter your Instagram username: ")
            if not password:
                password = getpass.getpass("Enter your Instagram password: ")
                
            self.L.login(username, password)
            logger.info(f"Successfully logged in as {username}")
            
            # Save session for future use
            session_file = f"{username}_instagram_session"
            self.L.save_session_to_file(session_file)
            logger.info(f"Session saved to {session_file}")
            
            return True
        except instaloader.exceptions.BadCredentialsException:
            logger.error("Login failed: Bad credentials")
            return False
        except instaloader.exceptions.TwoFactorAuthRequiredException:
            logger.error("Login failed: Two-factor authentication required")
            logger.info("Please try the session cookie method instead")
            return False
        except instaloader.exceptions.ConnectionException as e:
            logger.error(f"Connection error: {str(e)}")
            logger.info("This might be due to rate limiting or IP blocking")
            return False
        except Exception as e:
            logger.error(f"Login failed: {str(e)}")
            logger.error(traceback.format_exc())
            return False
            
    def session_login(self):
        """Login using saved session"""
        try:
            username = input("Enter your Instagram username (for session file): ")
            session_file = f"{username}_instagram_session"
            
            if os.path.exists(session_file):
                self.L.load_session_from_file(username, session_file)
                logger.info(f"Successfully loaded session for {username}")
                return True
            else:
                logger.error(f"No session file found for {username}")
                return False
        except Exception as e:
            logger.error(f"Session login failed: {str(e)}")
            logger.error(traceback.format_exc())
            return False
            
    def cookie_login(self):
        """Login using a cookie file exported from browser"""
        try:
            cookie_file = input("Enter path to the cookie file: ")
            if not os.path.exists(cookie_file):
                logger.error(f"Cookie file not found: {cookie_file}")
                return False
                
            with open(cookie_file, 'rb') as f:
                cookies = pickle.load(f)
                
            # Set cookies to the instaloader context
            self.L.context._session.cookies.update(cookies)
            
            # Test if login worked
            test_profile = instaloader.Profile.from_username(self.L.context, "instagram")
            if test_profile:
                logger.info("Cookie login successful")
                return True
            else:
                logger.error("Cookie login failed")
                return False
        except Exception as e:
            logger.error(f"Cookie login failed: {str(e)}")
            logger.error(traceback.format_exc())
            return False
    
    def set_target_profile(self, username):
        """Set the target profile to analyze followers"""
        try:
            self.user_profile = instaloader.Profile.from_username(self.L.context, username)
            logger.info(f"Target profile set: {username}")
            logger.info(f"Profile has {self.user_profile.followers} followers and {self.user_profile.followees} following")
            return True
        except instaloader.exceptions.ProfileNotExistsException:
            logger.error(f"Profile {username} does not exist")
            return False
        except instaloader.exceptions.ConnectionException as e:
            logger.error(f"Connection error: {str(e)}")
            logger.info("This might be due to rate limiting or IP blocking")
            return False
        except Exception as e:
            logger.error(f"Failed to set target profile: {str(e)}")
            logger.error(traceback.format_exc())
            return False
    
    def collect_followers_data(self, max_followers=None):
        """Collect data about followers"""
        if not self.user_profile:
            logger.error("No target profile set")
            return False
        
        try:
            followers_count = self.user_profile.followers
            logger.info(f"Profile has {followers_count} followers")
            
            if max_followers and max_followers < followers_count:
                logger.info(f"Limiting analysis to {max_followers} followers")
                followers_count = max_followers
                
            # Warning for large accounts
            if followers_count > 500:
                logger.warning(f"Analyzing {followers_count} followers will take a long time and may trigger Instagram limits")
                confirm = input("Continue with analysis? (y/n): ")
                if confirm.lower() != 'y':
                    logger.info("Analysis cancelled")
                    return False
            
            self.followers_data = []
            
            # Create progress bar
            with tqdm(total=followers_count if max_followers is None else min(followers_count, max_followers), 
                      desc="Collecting follower data") as pbar:
                
                followers_iterator = self.user_profile.get_followers()
                follower_count = 0
                
                for follower in followers_iterator:
                    if max_followers and follower_count >= max_followers:
                        break
                    
                    try:
                        # Basic profile info that doesn't require extra API calls
                        follower_data = {
                            'username': follower.username,
                            'full_name': follower.full_name,
                            'is_private': follower.is_private,
                            'has_profile_pic': follower.has_profile_pic,
                            'is_verified': follower.is_verified,
                        }
                        
                        # Get additional info - may require extra API calls
                        try:
                            # Try to get detailed profile info but handle if it fails
                            detailed_profile = instaloader.Profile.from_username(self.L.context, follower.username)
                            follower_data.update({
                                'biography': detailed_profile.biography,
                                'mediacount': detailed_profile.mediacount,
                                'followers': detailed_profile.followers,
                                'followees': detailed_profile.followees,
                                'external_url': detailed_profile.external_url,
                            })
                        except Exception as e:
                            # If detailed info fails, use basic info only
                            logger.debug(f"Could not get detailed info for {follower.username}: {str(e)}")
                            follower_data.update({
                                'biography': '',
                                'mediacount': 0,
                                'followers': 0,
                                'followees': 0,
                                'external_url': '',
                            })
                        
                        self.followers_data.append(follower_data)
                        follower_count += 1
                        pbar.update(1)
                        
                        # Add random delay to avoid rate limiting
                        time.sleep(random.uniform(1.0, 3.0))
                    except Exception as e:
                        logger.warning(f"Error collecting data for {follower.username}: {str(e)}")
                        continue
            
            logger.info(f"Collected data for {len(self.followers_data)} followers")
            
            # Save raw data as backup
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            raw_data_file = f"raw_followers_data_{timestamp}.csv"
            pd.DataFrame(self.followers_data).to_csv(raw_data_file, index=False)
            logger.info(f"Raw data saved to {raw_data_file}")
            
            return True
        except instaloader.exceptions.ConnectionException as e:
            logger.error(f"Connection error: {str(e)}")
            logger.info("This might be due to rate limiting or IP blocking")
            return False
        except Exception as e:
            logger.error(f"Error collecting followers data: {str(e)}")
            logger.error(traceback.format_exc())
            return False
    
    def detect_fake_profiles(self):
        """Analyze followers data to detect fake profiles"""
        if not self.followers_data:
            logger.error("No follower data available for analysis")
            return None
        
        try:
            df = pd.DataFrame(self.followers_data)
            
            # Replace NaN values with appropriate defaults
            df['followers'] = df['followers'].fillna(0).astype(int)
            df['followees'] = df['followees'].fillna(0).astype(int)
            df['mediacount'] = df['mediacount'].fillna(0).astype(int)
            df['biography'] = df['biography'].fillna('')
            df['external_url'] = df['external_url'].fillna('')
            
            # Add calculated features
            df['follower_ratio'] = df['followers'] / (df['followees'] + 1)  # Add 1 to avoid division by zero
            df['content_ratio'] = df['mediacount'] / (df['followers'] + 1)  # Add 1 to avoid division by zero
            
            # Feature: Check for spam patterns in username
            def has_spam_username(username):
                # Check for patterns like many numbers, follow/like keywords, etc.
                spam_patterns = [
                    r'\d{4,}',  # 4+ consecutive numbers
                    r'follow|flw|f4f|l4l|like4like|spam|_bot|\.bot|bot_',  # Follow/like related patterns
                    r'^[a-z]{1,2}\d{4,}',  # Short character prefix with numbers
                ]
                for pattern in spam_patterns:
                    if re.search(pattern, username, re.IGNORECASE):
                        return True
                return False
            
            df['spam_username'] = df['username'].apply(has_spam_username)
            
            # Feature: Check for suspicious biography
            def has_suspicious_bio(bio):
                if not isinstance(bio, str):
                    return False
                    
                spam_bio_patterns = [
                    r'follow for follow',
                    r'follow back',
                    r'f4f',
                    r'l4l',
                    r'dm for promo',
                ]
                for pattern in spam_bio_patterns:
                    if re.search(pattern, bio, re.IGNORECASE):
                        return True
                return False
            
            df['suspicious_bio'] = df['biography'].apply(has_suspicious_bio)
            
            # Calculate fake profile probability using these features
            def calculate_fake_probability(row):
                score = 0
                
                # Extreme follower ratios
                if row['follower_ratio'] < 0.01:  # Very few followers compared to followees
                    score += 3
                elif row['follower_ratio'] > 50:  # Extremely high followers compared to followees
                    score += 2
                
                # No profile picture
                if not row['has_profile_pic']:
                    score += 2
                
                # No posts or very few posts
                if row['mediacount'] == 0:
                    score += 3
                elif row['mediacount'] < 3:
                    score += 1
                
                # Suspicious username
                if row['spam_username']:
                    score += 2
                
                # Suspicious biography
                if row['suspicious_bio']:
                    score += 2
                
                # No biography
                if not isinstance(row['biography'], str) or row['biography'].strip() == '':
                    score += 1
                
                # No full name
                if not isinstance(row['full_name'], str) or row['full_name'].strip() == '':
                    score += 1
                
                # Verified accounts are not fake
                if row['is_verified']:
                    score = 0
                
                # Very high followers usually not fake
                if row['followers'] > 10000 and row['mediacount'] > 30:
                    score = max(0, score - 2)
                
                # Convert score to probability (0-100%)
                max_score = 14
                probability = min(100, (score / max_score) * 100)
                
                return probability
            
            df['fake_probability'] = df.apply(calculate_fake_probability, axis=1)
            
            # Classify profiles
            def classify_profile(probability):
                if probability < 30:
                    return "Likely Real"
                elif probability < 60:
                    return "Suspicious"
                else:
                    return "Likely Fake"
            
            df['classification'] = df['fake_probability'].apply(classify_profile)
            
            # Sort by fake probability (highest first)
            df = df.sort_values('fake_probability', ascending=False)
            
            return df
        except Exception as e:
            logger.error(f"Error analyzing followers: {str(e)}")
            logger.error(traceback.format_exc())
            return None
    
    def export_results(self, dataframe, filename=None):
        """Export analysis results to CSV"""
        if filename is None:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"instagram_fake_followers_{timestamp}.csv"
        
        try:
            dataframe.to_csv(filename, index=False)
            logger.info(f"Results exported to {filename}")
            return True
        except Exception as e:
            logger.error(f"Error exporting results: {str(e)}")
            logger.error(traceback.format_exc())
            return False
    
    def summarize_results(self, dataframe):
        """Summarize analysis results"""
        if dataframe is None or len(dataframe) == 0:
            return "No data to summarize"
        
        total = len(dataframe)
        fake_count = len(dataframe[dataframe['classification'] == "Likely Fake"])
        suspicious_count = len(dataframe[dataframe['classification'] == "Suspicious"])
        real_count = len(dataframe[dataframe['classification'] == "Likely Real"])
        
        fake_percent = (fake_count / total) * 100
        suspicious_percent = (suspicious_count / total) * 100
        real_percent = (real_count / total) * 100
        
        summary = f"""
        FAKE PROFILE DETECTION SUMMARY
        =============================
        Total followers analyzed: {total}
        
        Likely fake profiles: {fake_count} ({fake_percent:.1f}%)
        Suspicious profiles: {suspicious_count} ({suspicious_percent:.1f}%)
        Likely real profiles: {real_count} ({real_percent:.1f}%)
        
        Top 5 most suspicious followers:
        """
        
        for _, row in dataframe.head(5).iterrows():
            summary += f"\n- @{row['username']} (Probability: {row['fake_probability']:.1f}%)"
        
        return summary

    def load_data_from_csv(self, file_path):
        """Load previously collected follower data from CSV"""
        try:
            if not os.path.exists(file_path):
                logger.error(f"File not found: {file_path}")
                return False
                
            df = pd.read_csv(file_path)
            self.followers_data = df.to_dict('records')
            logger.info(f"Loaded {len(self.followers_data)} follower records from {file_path}")
            return True
        except Exception as e:
            logger.error(f"Error loading data: {str(e)}")
            logger.error(traceback.format_exc())
            return False


def main():
    detector = InstagramFakeProfileDetector()
    
    print("\n==================================")
    print("INSTAGRAM FAKE FOLLOWER DETECTOR")
    print("==================================\n")
    
    # Login options
    print("LOGIN OPTIONS:")
    print("1. Login with username and password")
    print("2. Login with saved session")
    print("3. Login with cookie file")
    print("4. Skip login (load data from CSV)")
    
    choice = input("\nSelect login method (1-4): ")
    
    login_successful = False
    if choice == '1':
        login_successful = detector.login()
    elif choice == '2':
        login_successful = detector.session_login()
    elif choice == '3':
        login_successful = detector.cookie_login()
    elif choice == '4':
        # Skip login, will load data from CSV
        login_successful = True
        csv_path = input("Enter path to the CSV file with follower data: ")
        if not detector.load_data_from_csv(csv_path):
            print("Failed to load data from CSV. Exiting.")
            return
    else:
        print("Invalid choice. Exiting.")
        return
    
    if not login_successful and choice != '4':
        print("Login failed. Exiting program.")
        return
    
    # Set target profile if not loading from CSV
    if choice != '4':
        target_set = False
        while not target_set:
            target_username = input("\nEnter Instagram username to analyze followers: ")
            target_set = detector.set_target_profile(target_username)
            if not target_set:
                retry = input("Would you like to try another username? (y/n): ")
                if retry.lower() != 'y':
                    print("Exiting program.")
                    return
        
        # Ask for max followers to analyze
        try:
            max_followers = input("\nEnter maximum number of followers to analyze (press Enter for all): ")
            max_followers = int(max_followers) if max_followers.strip() else None
        except ValueError:
            print("Invalid input. Analyzing all followers.")
            max_followers = None
        
        # Collect follower data
        print("\nCollecting follower data. This might take a while...")
        data_collected = detector.collect_followers_data(max_followers)
        
        if not data_collected:
            print("Failed to collect follower data. Exiting.")
            return
    
    # Analyze followers
    print("\nAnalyzing followers for fake profiles...")
    results = detector.detect_fake_profiles()
    
    if results is None:
        print("Analysis failed. Exiting.")
        return
    
    # Show summary
    summary = detector.summarize_results(results)
    print("\n" + summary)
    
    # Export results
    export = input("\nWould you like to export the detailed results to CSV? (y/n): ")
    if export.lower() == 'y':
        detector.export_results(results)
    +
    print("\nAnalysis complete!")


if __name__ == "__main__":
    main()