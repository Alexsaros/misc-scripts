import os
import pandas as pd
import praw
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.model_selection import train_test_split
from sklearn.linear_model import LinearRegression
from sklearn.metrics import mean_squared_error
from dotenv import load_dotenv
from datetime import datetime, timedelta
import tkinter as tk
from tkinter import scrolledtext
import webbrowser

# Load environment variables from .env file
load_dotenv()

# Define your subreddits and CSV file path
CSV_FILE = 'graded_posts.csv'
SUBREDDITS = ["jokes"]


def authenticate_reddit() -> praw.Reddit:
    """
    Authenticates and returns a Reddit instance using credentials from the .env file.
    """
    print("Authenticating Reddit...")
    reddit = praw.Reddit(
        client_id=os.getenv('REDDIT_CLIENT_ID'),
        client_secret=os.getenv('REDDIT_CLIENT_SECRET'),
        user_agent=os.getenv('REDDIT_USER_AGENT')
    )
    print("Reddit authenticated successfully.")
    return reddit


def load_dataset() -> pd.DataFrame:
    """
    Loads the dataset from the CSV file.
    Returns:
        pd.DataFrame: A DataFrame containing the dataset.
    """
    print(f"Loading dataset from {CSV_FILE}...")
    data = pd.read_csv(CSV_FILE)
    print(f"Dataset loaded. {len(data)} records found.")
    return data


def initialize_vectorizer(data: pd.DataFrame) -> tuple[TfidfVectorizer, pd.DataFrame]:
    """
    Initializes and fits the TF-IDF vectorizer on the dataset.

    Args:
        data (pd.DataFrame): The dataset containing text data.

    Returns:
        tuple: The fitted vectorizer and transformed data.
    """
    print("Initializing TF-IDF vectorizer...")

    # Create the TF-IDF vectorizer that will ignore common English stop words
    vectorizer = TfidfVectorizer(stop_words='english')
    # Fit the vectorizer to the text data and transform it into a numerical format (sparse matrix)
    tfidf_matrix = vectorizer.fit_transform(data['text'])

    print("TF-IDF vectorizer initialized and dataset transformed.")

    # Return both the fitted vectorizer and the transformed dataset
    return vectorizer, tfidf_matrix


def train_model(tfidf_matrix: pd.DataFrame, data: pd.Series) -> LinearRegression:
    """
    Trains a linear regression model on the dataset.
    Args:
        tfidf_matrix (pd.DataFrame): Transformed feature data.
        data (pd.Series): Target values (grades).
    Returns:
        LinearRegression: The trained model.
    """
    print("Training the linear regression model...")
    X_train, X_test, y_train, y_test = train_test_split(tfidf_matrix, data, test_size=0.2, random_state=42)

    # Train the model
    model = LinearRegression()
    model.fit(X_train, y_train)

    # Make predictions and calculate mean squared error
    y_pred = model.predict(X_test)
    mse = mean_squared_error(y_test, y_pred)
    print(f"Model trained successfully. Mean Squared Error: {mse:.4f}")

    return model


def get_new_posts(reddit: praw.Reddit, subreddits: list, limit: int = 100) -> list[dict]:
    """
    Retrieves posts from specified subreddits posted in the last 2 days.
    Args:
        reddit (praw.Reddit): Reddit instance for API access.
        subreddits (list): List of subreddit names to retrieve posts from.
        limit (int): Maximum number of posts to retrieve per subreddit.
    Returns:
        list[dict]: A list of posts containing the id, content, and URL.
    """
    print("Fetching new posts from Reddit...")
    two_days_ago = datetime.utcnow() - timedelta(days=2)
    posts = []

    for subreddit in subreddits:
        print(f"Fetching posts from r/{subreddit}...")
        for submission in reddit.subreddit(subreddit).new(limit=limit):
            post_time = datetime.utcfromtimestamp(submission.created_utc)
            if post_time >= two_days_ago:
                content = submission.title + "\n\n" + submission.selftext
                username = submission.author.name if submission.author else None
                # Skip users who deleted their accounts
                if username is None:
                    print("Skipped post from deleted user: " + submission.title)
                    continue
                posts.append({
                    'id': submission.id,
                    'content': content,
                    'url': submission.url,
                    'username': username
                })

    print(f"Fetched {len(posts)} posts.")
    return posts


def is_in_csv(data: pd.DataFrame, post: dict) -> bool:
    """
    Checks if the post's content already exists in the CSV file.
    Args:
        data (pd.DataFrame): The dataset.
        post (dict): The Reddit post.
    Returns:
        bool: True if the post exists, False otherwise.
    """
    post_text = post['content']
    return data['text'].str.contains(post_text, regex=False).any()


def grade_post(vectorizer: TfidfVectorizer, model: LinearRegression, post_text: str) -> float:
    """
    Grades a post using the trained AI model.
    Args:
        vectorizer (TfidfVectorizer): The fitted TF-IDF vectorizer.
        model (LinearRegression): The trained model.
        post_text (str): The text content of the post to grade.
    Returns:
        float: The predicted grade.
    """
    post_features = vectorizer.transform([post_text])
    grade = model.predict(post_features)[0]
    return grade


def show_post(post: dict, predicted_grade: float) -> None:
    """
    Displays a post in a Tkinter UI for manual grading.
    Args:
        post (dict): The Reddit post data (id, content, URL).
        predicted_grade (float): The grade predicted by the AI model.
    """
    def open_link():
        webbrowser.open(post['url'])

    def save_grade():
        grade = grade_entry.get()
        new_entry = pd.DataFrame({
            'id': [post['id']],
            'text': [post['content']],
            'grade': [grade],
            'username': [post['username']]
        })
        new_entry.to_csv(CSV_FILE, mode='a', header=False, index=False)
        window.destroy()

    def on_enter(event):
        save_grade()

    # Create the window and display post information
    window = tk.Tk()
    window.title("Reddit Post Grader")

    # Set a fixed size for the window
    window.geometry("600x400")

    # Create a frame for the content and a scrollbar
    frame = tk.Frame(window)
    frame.pack(expand=True, fill=tk.BOTH)

    # Create a scrolled text widget for the post content
    content_text = scrolledtext.ScrolledText(frame, wrap=tk.WORD, height=15)
    content_text.insert(tk.END, f"Post Content:\n{post['content']}")
    content_text.config(state=tk.DISABLED)
    content_text.pack(expand=True, fill=tk.BOTH)

    tk.Label(window, text=f"Predicted Grade: {predicted_grade:.2f}").pack()

    tk.Button(window, text="Open Post", command=open_link).pack()


    # Manual grading UI
    tk.Label(window, text="Enter your grade:").pack()
    grade_entry = tk.Entry(window)
    grade_entry.pack()
    grade_entry.bind('<Return>', on_enter)  # Bind Enter key to save_grade function

    tk.Button(window, text="Save Grade", command=save_grade).pack()

    window.mainloop()


def main():
    """
    Main function to orchestrate Reddit post retrieval, grading, and manual review.
    """
    # Authenticate Reddit
    reddit = authenticate_reddit()

    # Load dataset and train model
    data = load_dataset()
    vectorizer = None
    model = None
    try:
        vectorizer, tfidf_matrix = initialize_vectorizer(data)
        model = train_model(tfidf_matrix, data['grade'])
    except ValueError:
        pass

    # Fetch new posts from Reddit
    new_posts = get_new_posts(reddit, SUBREDDITS)

    # Grade each post and sort them by predicted grade
    scored_posts = []
    for post in new_posts:
        if not is_in_csv(data, post):
            score = 0
            if model is not None:
                score = grade_post(vectorizer, model, post['content'])
            scored_posts.append((post, score))

    # Sort posts from highest to lowest predicted grade
    scored_posts.sort(key=lambda x: x[1], reverse=True)

    # Display posts one by one in Tkinter UI
    for post, predicted_grade in scored_posts:
        show_post(post, predicted_grade)


if __name__ == "__main__":
    main()
