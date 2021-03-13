import tweepy


class MyStreamListener(tweepy.StreamListener):
    def __init__(self, csocket):
        super().__init__()
        self.client_socket = csocket

    def on_status(self, status):
        if len(status.entities.get("hashtags")) > 0:
            self.client_socket.sendall((status.text + "\n").encode("utf-8"))

    def on_error(self, status_code):
        '''
        Since Twitter API has rate limits, 
        stop srcraping data as it exceed to the thresold.
        '''
        print(status_code)
        if status_code == 420:
            print("KO")
            # return False to disconnect the stream
            return False