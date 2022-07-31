import networkx as nx
import matplotlib.pyplot as plt
import numpy as np
from sqlalchemy import desc
from tqdm import tqdm
from polyfuzz import PolyFuzz
from polyfuzz.models import RapidFuzz # on MIT licence :)
from polyfuzz.models import EditDistance
import argparse
import os

parser = argparse.ArgumentParser()
parser.add_argument('-graph_name', nargs="+",required=False,dest='graph_name', help="List of graphs to analyze", default=["Examples_output/Harvard.gpickle"])
parser.add_argument('-top_K', required=False,dest='top_K', help="", default=5)

args = parser.parse_args()


URLS= args.graph_name
K = int(args.top_K)


for U in URLS:
    print("U  :", U)
    G = nx.read_gpickle(os.getcwd() +"/Examples_output/"+ U + '.gpickle')
    print("The Graph has : ", G.number_of_nodes(), G.number_of_edges())
    max_mails_urls = 0
    urls_wth_mails = []
    nb_mail_url = []

    #with tqdm(list(G.nodes())) as t:
    for n in list(G.nodes()):
        #print(n)
        #print(G.nodes("emails_contained")[n])
        if G.nodes("emails_contained")[n] is not None:
            urls_wth_mails.append(n)
            nb_mail_url.append(G.nodes("number_emails")[n])

    ar = np.argsort(nb_mail_url)


    top_20_url = []
    for i in range (1, 31):
        top_20_url.append(urls_wth_mails[ar[-i]])

    for u in top_20_url:
        matcher = RapidFuzz(n_jobs=1, score_cutoff=0.8)
        model = PolyFuzz(matcher)
        model.match(urls_wth_mails, [u])
        matches = model.get_matches()
        print(model.get_matches())
        matches = matches.sort_values('Similarity', ascending=False)
        print(matches.columns)
        print("Considered url :", u)
        print("Top 5 similarity :", matches["From"][1:6].to_list())
    for i in range (1, K+1):

        print("For the Domain of ", U, "the " ,i,"th ","best url is " , urls_wth_mails[ar[-i]]," containing ",nb_mail_url[ar[-i]] , "emails inside.")
    
# nodes / url with the highest adjacent number of edges : 
    G.degree()
    print("Node with the highest degree : ", max(dict(G.degree()).items(), key = lambda x : x[1]))


    fig, ax = plt.subplots(figsize=(15,8))
    nx.draw(G,with_labels=False, node_color="blue", alpha= 0.6, node_size=5)
    plt.show()