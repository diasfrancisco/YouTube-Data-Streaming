import html
import logging
import requests
import socket
import pprint

import config


class YouTubeStatistics:
    def get_titles(self):
        top_n_channel_videos_url = f'https://www.googleapis.com/youtube/v3/search?key={config.API_KEY}&channelId={config.CHANNEL_ID}&part=snippet,id&order=date&maxResults=20'
        payload = requests.get(top_n_channel_videos_url)
        
        logging.info('CHANNEL PAYLOAD RECEIVED')
        
        video_info = {}
        
        for video in payload.json()['items']:
            title = html.unescape(video['snippet']['title'])
            id = html.unescape(video['id']['videoId'])
            video_info[id] = {'title': title}
            
        return self.get_video_stats(video_info)
    
    def get_video_stats(self, video_info):
        for id in video_info.keys():
            video_stats_url = f'https://www.googleapis.com/youtube/v3/videos?part=statistics&id={id}&key={config.API_KEY}'
            payload = requests.get(video_stats_url)
            info_dict = video_info[id]
            info_dict.update(payload.json()['items'][0]['statistics'])
            
        return video_info

def main():
    logging.info('START')
    
    stats_inst = YouTubeStatistics()
    video_info = stats_inst.get_titles()
    
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.bind(('127.0.0.1', 5000))
        s.listen()
        conn, addr = s.accept()
        with conn:
            print(f'Connected by {addr}')
            while True:
                data = conn.recv(1024)
                if not data:
                    break
                conn.sendall(data)
    
    logging.info('COMPILED VIDEO STATS')

if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO)
    main()