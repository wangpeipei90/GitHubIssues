'''
Created on Feb 19, 2019

@author: peipei
'''
import pickle
from pprint import pprint
import json
import csv
from datetime import datetime
from itertools import chain




    

    
    list_projInfo=[buildProjInfo(dict_repoUrl2file[url]) for url in dict_repoUrl2file]
    pickle.dump(list_projInfo,open("/home/peipei/GitHubIssues/list_projInfo","wb"))          

    keys = list_projInfo[0].keys()
    with open("/home/peipei/GitHubIssues/list_projInfo.csv", 'w', encoding='utf8', newline='') as output_file:
        dict_writer = csv.DictWriter(output_file,fieldnames=list_projInfo[0].keys())
        dict_writer.writeheader()
        dict_writer.writerows(list_projInfo)
  
        
def getFilteredIssues(filteredProj): 
    # filteredProj: List
    with open("/home/peipei/GitHubIssues/dict_repoUrl2file","rb") as pickle_file:
        dict_repoUrl2file = pickle.load(pickle_file)
    
    filteredIssues=list(chain.from_iterable([dict_repoUrl2file[repo_url] for repo_url in filteredProj]))
    print(len(filteredIssues))
    return filteredIssues

def getFilteredIssues2(filteredProj): 
    # filteredProj: List
    res=[]
    for lang in ["python","java","ruby","javascript","php"]:
        with open("/home/peipei/GitHubIssues/"+lang+"/dict_repo2file","rb") as pickle_file:
            dict_repo2file = pickle.load(pickle_file)
    
        filteredIssues=list(chain.from_iterable([dict_repo2file[repo_url] for repo_url in filteredProj if repo_url in dict_repo2file]))
        print("lang-{} filteredIssues-{}".format(lang,len(filteredIssues)))
        
        res.append(filteredIssues)
    return res
 

     
def getFilteredIssueInfo(filteredIssues): 
    # filteredIssues: list of issue file path  
#     print(filteredIssues[0])    
#     buildIssueInfo(filteredIssues[0]) 
    list_issueInfo=[buildIssueInfo(file) for file in filteredIssues]
    pickle.dump(list_issueInfo,open("/home/peipei/GitHubIssues/list_filteredIssueInfo","wb"))          

    keys = list_issueInfo[0].keys()
    with open("/home/peipei/GitHubIssues/list_filteredIssueInfo.csv", 'w', encoding='utf8', newline='') as output_file:
        dict_writer = csv.DictWriter(output_file,fieldnames=list_issueInfo[0].keys())
        dict_writer.writeheader()
        dict_writer.writerows(list_issueInfo)    
if __name__ == '__main__':
#     getUniqueProjInfo()

#     filterProjInfo()
#     filteredProj=filterProjInfo()
#     filteredIssues=getFilteredIssues(filteredProj)
# #     filteredIssues=getFilteredIssues2(filteredProj)
#     getFilteredIssueInfo(filteredIssues)

    filterFilteredIssueInfo()
#     getUniqueIssueInfo()
    pass

