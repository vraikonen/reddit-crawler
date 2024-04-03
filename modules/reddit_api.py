import praw


# Initialize reddit API account
def initilize_reddit(client_id, client_secret, password, username, user_agent):

    reddit = praw.Reddit(
        client_id="NjRuz5CDNTWqsmE0rpVoRQ",  # Developer account
        client_secret="IZD3Vs0bDCwd-3AWb3FoiWoQU9yHyg",  # Developer account
        password="Uv,QkEU,)2rgZzu",  # Personal account
        username="Upset-Foundation-295",  # Personal account
        user_agent="Testing praw and Reddit API 1.0 by u/Upset-Foundation-295",  # Refer to https://github.com/reddit-archive/reddit/wiki/API
    )

    return reddit
