import os
import sys
import collections
import requests
from bs4 import BeautifulSoup
from colorama import init, Fore
init(autoreset=True)

nytimes_com = '''
This New Liquid Is Magnetic, and Mesmerizing
Scientists have created “soft” magnets that can flow 
and change shape, and that could be a boon to medicine 
and robotics. (Source: New York Times)
Most Wikipedia Profiles Are of Men. This Scientist Is Changing That.
Jessica Wade has added nearly 700 Wikipedia biographies for
 important female and minority scientists in less than two 
 years.
'''

bloomberg_com = '''
The Space Race: From Apollo 11 to Elon Musk
It's 50 years since the world was gripped by historic images
 of Apollo 11, and Neil Armstrong -- the first man to walk 
 on the moon. It was the height of the Cold War, and the charts
 were filled with David Bowie's Space Oddity, and Creedence's 
 Bad Moon Rising. The world is a very different place than 
 it was 5 decades ago. But how has the space race changed since
 the summer of '69? (Source: Bloomberg)
Twitter CEO Jack Dorsey Gives Talk at Apple Headquarters
Twitter and Square Chief Executive Officer Jack Dorsey 
 addressed Apple Inc. employees at the iPhone maker’s headquarters
 Tuesday, a signal of the strong ties between the Silicon Valley giants.
'''


class Browser:
    def __init__(self):
        self.path = '.'  # default home path
        self.create_dir()  # create folder using name in arguments

    def create_dir(self):
        # check if folder name pass in arguments
        if len(sys.argv) > 1:
            # create directory
            directory = sys.argv[1]
            # check if folder exist
            if not os.path.exists(directory):
                os.mkdir(directory)
            # set new directory path
            self.path = directory

    def open_page(self, url):
        # complate file path
        filename = self.path + '/' + url + '.txt'
        # check if file exist in home folder
        if not os.path.exists(filename):
            print("Error: Incorrect URL")
        else:
            # open and decode file content
            with open(filename, encoding='utf-8', errors='ignore') as infile:
                print(infile.read())

    def get_page(self, url):
        # check if pae is correct
        if url.find('https://') < 0:
            url = 'https://' + url
        r = requests.get(url)
        return r.text

    def save_page(self, url, text):
        # check url domain
        index = url.rfind('.')
        filename = self.path + '/' + url[0:index] + '.txt'
        with open(filename, 'w+', encoding='utf-8', errors='ignore') as outfile:
            outfile.write(text)
        return url[0:index]

    def parse_page(self, text):
        text_list = []
        tags = ['title', 'p', 'h1', 'h2', 'h3', 'h4', 'h5', 'h6', 'a', 'ul', 'ol', 'li']
        soup = BeautifulSoup(text, 'html.parser')
        for tag in soup.find_all(tags):
            text = tag.get_text()
            if tag.name == 'a':
                text = Fore.BLUE + text
            text_list.append(text)
        return '\n'.join(text_list)

    def run(self):
        # init history collection
        history = collections.deque()
        previous_page = ''
        current_page = ''

        # add new url to history
        if current_page != previous_page:
            history.append(previous_page)
            previous_page = current_page

        while True:
            # get user input
            url = input()
            if url == "exit":
                break
            elif url == "back":
                if history:
                    current_page = history.pop()
                    self.open_page(current_page)
            elif url.rfind('.') < 0:
                current_page = url
                self.open_page(current_page)
            else:
                text = self.parse_page(self.get_page(url))
                print(text)
                # save new page
                current_page = self.save_page(url, text)


if __name__ == '__main__':
    browser = Browser()
    browser.run()