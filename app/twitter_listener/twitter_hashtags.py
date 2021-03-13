import os
import tweepy
import socket

from stream_listener import MyStreamListener

if __name__ == "__main__":

    auth = tweepy.OAuthHandler(os.getenv("TWITTER_API_KEY"),
                               os.getenv("TWITTER_API_SECRET"))
    auth.set_access_token(os.getenv("ACCESS_TOKEN"),
                          os.getenv("ACCESS_TOKEN_SECRET"))
    api = tweepy.API(auth)

    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.bind(("0.0.0.0", 9009))
    s.listen(10)

    print("Waiting for TCP connection...")
    conn, addr = s.accept()
    print("Connected... Starting getting tweets.")

    myStreamListener = MyStreamListener(conn)
    myStream = tweepy.Stream(auth=api.auth, listener=myStreamListener)
    myStream.sample(languages=["fr"])