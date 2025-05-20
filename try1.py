import streamlit as st
import matplotlib.pyplot as plt

# Dummy followers data
followers_data = [
    {"username": "john_doe", "posts": 2, "followers": 50, "following": 200, "profile_pic": False, "bio": False},
    {"username": "jane_smith", "posts": 10, "followers": 500, "following": 300, "profile_pic": True, "bio": True},
    {"username": "bot_account1", "posts": 0, "followers": 10, "following": 100, "profile_pic": False, "bio": False},
    {"username": "real_guy", "posts": 25, "followers": 1000, "following": 400, "profile_pic": True, "bio": True},
    {"username": "suspect_123", "posts": 1, "followers": 20, "following": 100, "profile_pic": False, "bio": True},
    {"username": "active_user", "posts": 15, "followers": 800, "following": 600, "profile_pic": True, "bio": True},
    {"username": "no_bio_user", "posts": 5, "followers": 100, "following": 300, "profile_pic": True, "bio": False},
    {"username": "ghost", "posts": 0, "followers": 5, "following": 50, "profile_pic": False, "bio": False},
]

def analyze_follower(f):
    score = 0
    reasons = []
    if f["posts"] < 3:
        score += 30
        reasons.append("Very few posts")
    if f["followers"] > 0 and (f["following"] / f["followers"]) > 2:
        score += 30
        reasons.append("High following/follower ratio")
    if not f["profile_pic"]:
        score += 20
        reasons.append("No profile picture")
    if not f["bio"]:
        score += 20
        reasons.append("No bio")
    label = "Suspicious/Fake" if score >= 50 else "Real"
    return label, score, reasons

def main():
    st.set_page_config(page_title="Instagram Fake Profile Detector", layout="centered")
    st.title("Instagram Fake Profile Detector")
    st.write("This app simulates fake follower detection on Instagram.")

    # Dummy login form
    with st.form("login_form"):
        username = st.text_input("Instagram Username")
        password = st.text_input("Password", type="password")
        login_btn = st.form_submit_button("Login (Simulation)")

    if login_btn:
        if not username or not password:
            st.error("Please enter both username and password.")
            return
        st.success(f"Logged in as {username} (simulation)")
        st.write(":point_down: Click below to analyze your followers!")
        if st.button("Analyze My Followers"):
            results = []
            for f in followers_data:
                label, score, reasons = analyze_follower(f)
                results.append({**f, "label": label, "score": score, "reasons": reasons})
            real_count = sum(1 for r in results if r["label"] == "Real")
            fake_count = sum(1 for r in results if r["label"] == "Suspicious/Fake")
            # Pie chart
            fig, ax = plt.subplots()
            ax.pie([real_count, fake_count], labels=["Real", "Suspicious/Fake"], autopct="%1.1f%%", colors=["#4CAF50", "#FF5252"])
            ax.set_title("Followers Classification")
            st.pyplot(fig)
            st.write(f"**Total Followers Analyzed:** {len(results)}")
            st.write(f"**Real:** {real_count}")
            st.write(f"**Suspicious/Fake:** {fake_count}")
            # Suspicious accounts list
            st.subheader("Suspicious/Fake Accounts")
            suspicious = [r for r in results if r["label"] == "Suspicious/Fake"]
            if suspicious:
                for r in suspicious:
                    st.markdown(f"**@{r['username']}** - Fake Score: {r['score']}%  ")
                    st.write(f"Reasons: {', '.join(r['reasons'])}")
            else:
                st.write("No suspicious accounts detected!")

if __name__ == "__main__":
    main()
