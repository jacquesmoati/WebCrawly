import logging
import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin
import networkx as nx
from multiprocessing import Pool
from concurrent.futures import ThreadPoolExecutor
import concurrent.futures
from tqdm import tqdm
import re
from time import sleep
import argparse


FORMAT = '%(asctime)s'
logging.basicConfig(format=FORMAT,level=logging.INFO)

class WebCrawler:
    
    def __init__(self, URLS = [], OUTPUT_NAME = [], pool = int, max_visit = int) -> None:

        # initialize list of URLS, visited and to be visited
        self.max_visit = int(max_visit)
        self.pool = int(pool)
        print(self.pool)
        self.already_visited_url = []
        self.tobevisited_urls = URLS

        # initialize an empty graph

        global G
        self.G = nx.DiGraph()
        #nx.set_node_attributes(self.G, self.data_base_emails_contained, "emails_contained")

        # we set the attribute of each node,
        # each node will contain the list of valid emails it contains. 
        
    def listURLpage(self,url):

        """
        Input : a valid url, 
        Output : a generator if there is at list one url scrapped in the input url html webpage, else return 0

        """

        requ = requests.get(url)
        html = requ.text
        soup = BeautifulSoup(html, 'html.parser')
        paths = set()

        if len(soup.find_all("a")) > 0:
            for link in soup.find_all('a'):
                path = link.get('href')
                if path and path.startswith('/'):
                    path = urljoin(url, path)
                    paths.add(path)
            return paths
        else:
            return 0

    def url_add_test(self, path, url):

        if path not in self.already_visited_url and path not in self.tobevisited_urls and "download" not in path and "jpeg" not in path and "pdf" not in path: #and path.startswith(U):

            self.tobevisited_urls.append(path)
            
            ##("adder b4 : ", self.G.number_of_nodes(), self.G.number_of_edges())
            self.G.add_node(path)
            self.G.add_edge(url, path) # add directed graph from this url to this new path and so on
            ##print("adder after : ", self.G.number_of_nodes(), self.G.number_of_edges())


    def multiCrawler(self, url):

        """
        crawl current url and add additional pages to be crawled
        """

        #self.already_visited_url.append(url)
        if url not in self.already_visited_url and url not in self.tobevisited_urls:
            print(f'Lets crawl : {url}')

            ##paths = set()
            requ = requests.get(url,timeout=10)
            html = requ.text
            soup = BeautifulSoup(html, 'html.parser')

            for link in set(soup.find_all('a')):
                path = link.get('href')
                if path and path.startswith('/'):
                    path = urljoin(url, path)
                    self.url_add_test(path, url)

    def email_finder(self,html):
        return set(re.findall(r'[\w.+-]+@[\w-]+\.[\w.-]+', html, re.I))

    def email_scrapper(self, url):
        # we get the emails now
        html = requests.get(url, timeout=10).text
        emails = set()
        new_emails = self.email_finder(html) 
        #print("We found on the page : ",url, ":", len(emails), "emails")
        if len(new_emails)!=0: # set not empty
            emails.update(new_emails)
            print("We found on the page : ",url, ":", len(emails), "emails")
            self.G.nodes[url]["emails_contained"] = emails
            self.G.nodes[url]["number_emails"] = len(emails)

        return emails

    def launch(self):
        #for U in URLS:
        while self.tobevisited_urls: # while there is still urls to crawl

            url = self.tobevisited_urls.pop(0)
            self.already_visited_url.append(url)

            requ = requests.get(url)

            if requ.status_code == 200:

                print(f'Lets crawl : {url}')
                # new node in graph
                self.G.add_node(url)

                # 1 need the list of urls in the current url link 
                # for that we call the function listURLpage
                it = list(self.listURLpage(url))
                iterator = iter(it)
                ##print("list of webs : ", it)
                
                if list(self.listURLpage(url)) !=0: # if there is at least one url scrapped in the current url html page then add all the nodes

                    print("it diff than 0 : let's pool the next nodes :-) ")

                    with ThreadPoolExecutor(self.pool) as executor:
                        _ = executor.map(self.multiCrawler, iterator)

            else:
                print(f'Failed to crawl: {url}')

            self.tobevisited_urls = [x for x in self.tobevisited_urls if x not in self.already_visited_url]
            print("Remaining (Updated)number of ULR to visit: ", len(self.tobevisited_urls))

            if self.G.number_of_nodes() > self.max_visit: # max number of nodes to visit (max bounds)
                break

            print("G size : ", self.G.number_of_nodes(),self.G.number_of_edges() )

        with ThreadPoolExecutor(self.pool) as executor:
            list(tqdm(executor.map(self.email_scrapper, iter(list(self.G.nodes()))),total = len(list(self.G.nodes()))))

        """
        # with classic tqdm if needed 
        with tqdm(list(self.G.nodes())) as t:
            for n in t:
                self.email_scrapper(n)
        """

        print("final size : ", self.G.number_of_nodes(),self.G.number_of_edges() )

        nx.write_gpickle(self.G,O[0]+'.gpickle')


if __name__ == '__main__':
    
    parser = argparse.ArgumentParser()
    default_list_urls = ['https://fas.yale.edu/division-science','https://www.seas.harvard.edu/', "https://www.princeton.edu/academics/"]
    default_output_urls = ["Yale", "Harvard", "Princeton"]
    parser.add_argument('-seed_URL', nargs="+",required=True,dest='i_LIST_URLS', help="List of seed URLs that", default=default_list_urls)
    parser.add_argument('-output_name_graphs',nargs="+", required=True,dest='o_name', help="List of corresponding output names", default=default_output_urls)
    parser.add_argument('-nb_thread', required=True,dest='pool', help="Number of thread to launch while scrapping (to find the best bandwidith) ", default=64)
    parser.add_argument('-max_urls_visited', required=True,dest='max_visit', help="", default=300)

    args = parser.parse_args()
    
    for U,O in zip(args.i_LIST_URLS, args.o_name,):
        U = [U]
        O = [O]
        WebCrawler(U, O,  args.pool,args.max_visit).launch()
    