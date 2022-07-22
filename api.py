import time

import requests
import pprint
import json
import os
import time
import html_parsing
from selenium import webdriver
from selenium.webdriver.common.by import By
from dotenv import load_dotenv

TIMEOUT = 20
HOST = 'https://y.qq.com'

# Load bot token from environment variable .env
load_dotenv()
TOKEN = os.getenv('CHROME_PATH2')
driver = webdriver.Chrome(executable_path=TOKEN)


class MusicCrawler:
    """
    Attributes:
        - cookie: a dict containing all the cookie values
        - user: the qq id of the given user for playlist
        - song_list: a list of all the public playlists from self.user.
            format: [{'dissid': dissid1, 'dirid': dirid1}, {'dissid': dissid2, 'dirid': dirid2}]
            where each dict is an instance of a playlist
        - playlist: a list of song mids from the selected playlist.
        - playlist_url: the url of songs from the previous playlist
    """
    cookie: dict
    user: int = 0
    song_list: list = []
    playlist: list = []
    playlist_url: list = []

    def __init__(self) -> None:
        """
        Login to y.qq.com via selenium.
        Retrieve the cookie from the driver and assign it to self.
        Set self.cookie
        """
        # Use Google Chrome driver.
        driver.get(HOST)
        # Open login page.
        driver.find_element(by=By.LINK_TEXT, value='登录').click()
        # Switch to the top window.
        driver.switch_to.window(driver.window_handles[-1])
        # Switch to the login iframe step by step.
        while 1:
            try:
                driver.switch_to.frame('login_frame')  # iframe login_frame
                break
            except Exception as e:
                print(e)
                time.sleep(0.5)

        while 1:
            try:
                driver.switch_to.frame('ptlogin_iframe')  # iframe ptlogin_iframe.
                break
            except Exception as e:
                print(e)
                time.sleep(0.5)

        time.sleep(3)
        # # Switch to input popup, fill username and password, then login.
        driver.find_element(by=By.ID, value="switcher_plogin").click()
        driver.find_element(by=By.NAME, value='u').send_keys(os.getenv('username2'))
        driver.find_element(by=By.NAME, value='p').send_keys(os.getenv('password2'))
        driver.find_element(by=By.ID, value="login_button").click()

        # Check if login is successful by checking value of qm_keyst in cookies.
        time_cost = 0
        while 1:
            cookies_list = driver.get_cookies()
            cookies_dict = {item.get('name'): item.get('value') for item in cookies_list}
            if cookies_dict.get('qm_keyst'):
                break
            if time_cost > TIMEOUT:
                raise TimeoutError('Login timeout.')
            time.sleep(0.5)
            time_cost += 0.5

        self.cookie = cookies_dict

    def set_user(self, qq_id: int) -> list:
        """
        using the initialized cookie and input id
        Set self.user and self.song_list

        :param qq_id: the qq id of the given user.
        :return: a list of playlist titles.
        """
        self.user = qq_id
        url_1 = f'https://c.y.qq.com/rsc/fcgi-bin/fcg_get_profile_homepage.fcg?cid=205360838&userid={qq_id}&reqfrom=1'
        response1 = requests.get(url_1, cookies=self.cookie)

        text = response1.text.strip()

        # transform into json format

        titles = []
        j_data = json.loads(text)
        for item in j_data['data']['mydiss']['list']:
            self.song_list.append({
                'dissid': item['dissid'],
                'dirid': item['dirid']
            })
            titles.append(item['title'])
            # print(item['dissid'])  # the list id
            # print(item['title'])  # the list title
            # print('---------------')
        return titles

    def set_song_list(self, index: int) -> None:
        """


        :param index:
        :return:
        """
        dissid = self.song_list[index - 1]['dissid']
        dirid = self.song_list[index - 1]['dirid']

        # get individual songs
        if self.user == 0:
            return

        url = f"https://c.y.qq.com/splcloud/fcgi-bin/fcg_musiclist_getmyfav.fcg?uin={self.user}&dissid={dissid}&dirid={dirid}&g_tk=5381&format='json'"
        response = requests.get(url, cookies=self.cookie, headers={'referer': 'https://y.qq.com/n/yqq/playlist'})

        # transform into json format
        j_data = json.loads(response.text.strip()[1:-1])
        self.playlist = list(j_data['mapmid'].keys())
        for item in self.playlist:
            self.playlist_url.append(self.search_list(item))

    def search_list(self, mid) -> str:
        """
        with the mid of the given song:
        1. get its name and singer from qq music website
        2. search at youtube
        3. get the url of the first result, return it
        :param mid: the music id of the song
        :return: the url of its search result from youtube
        """
        url3 = f"https://y.qq.com/n/ryqq/songDetail/{mid}"
        response3 = requests.get(url3, cookies=self.cookie, allow_redirects=False)
        html_text = html_parsing.strip_tags(response3.text)
        check = 0
        index = 0
        for i in range(len(html_text)):
            if html_text[i] == '-':
                check = check + 1
            if check == 2:
                index = i
                break
        serach_item = html_text[0:index]
        url = f"https://www.youtube.com/results?search_query={serach_item}"
        response = requests.get(url)
        html_text = html_parsing.strip_tags(response.text)
        index = html_text.find("/watch?v=")
        i = index
        while html_text[i] != "\"":
            i = i + 1
        extraction = "https://www.youtube.com" + html_text[index: i]
        return extraction

    def get_playlist_urls(self) -> list:
        return self.playlist_url


if __name__ == '__main__':
    # cookie_dict = login_for_cookies()
    # print("--------------------------------------")
    # pprint.pprint(cookie_dict)
    # print("--------------------------------------")
    # main()
    mc = MusicCrawler()
    mc.set_user(1519831417)
    mc.set_song_list(2)
    urls = mc.get_playlist_urls()
    print(urls)
