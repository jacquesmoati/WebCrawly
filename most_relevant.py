import networkx as nx
import matplotlib.pyplot as plt
import numpy as np
from sqlalchemy import desc
from tqdm import tqdm
from polyfuzz import PolyFuzz
from polyfuzz.models import RapidFuzz # on MIT licence :)
from polyfuzz.models import EditDistance

URLS=['Harvard']#, "Yale", 'Princeton']#, 'https://www.clalit.co.il/']
K = 5

for U in URLS:
    print("U  :", U)
    G = nx.read_gpickle(U + '.gpickle')
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

            #if max_mails_urls < G.nodes("number_emails")[n]:
            #    max_mails_urls = G.nodes("number_emails")[n]
            #    top_url = n
    # printing original list 
    #print("The original list : " + str(nb_mail_url))
    ar = np.argsort(nb_mail_url)
    #print("urls_wth_mails arg sort ", np.argsort(nb_mail_url))
    #print("last id :", ar[-K:])
    for i in range (1, K+1):
        #print(urls_wth_mails[ar[-i]])
        #print(nb_mail_url[ar[-i]])
        print("For the Domain of ", U, "the " ,i,"th ","best url is " , urls_wth_mails[ar[-i]]," containing ",nb_mail_url[ar[-i]] , "emails inside.")
    #print("urls_wth_mails :", urls_wth_mails)
    #print("nb_mail_url : ", nb_mail_url)
    #idx_sort = np.argsort(urls_wth_mails)

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
        print(matches["From"][1:6].to_list())
        #print("Top 5 similarity :", list(matches.iloc[1])[:5])

        

# nodes / url with the highest adjacent number of edges : 
    G.degree()
    print(max(dict(G.degree()).items(), key = lambda x : x[1]))
