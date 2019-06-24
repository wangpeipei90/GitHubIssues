'''
Created on Apr 25, 2019

@author: peipei
'''
import api
import pickle
from pprint import pprint
import json
import csv
from datetime import datetime
from itertools import chain
import glob
from github import Github
import re

def getUniquePRsInOrg(dir,org="apache"):   
    dict_file2url,dict_url2info=api.getUniqueIssues(dir,True)    
    print("unique PRs in org {} is {}".format(org,len(dict_url2info)))
    
    pickle.dump(dict_file2url,open(dir+"/dict_file2url","wb"))
    pickle.dump(dict_url2info,open(dir+"/dict_url2info","wb"))
    
    return dict_file2url,dict_url2info

def getUniqueReposInOrg(dict_url2info,dir,org="apache"):
    dict_repo2files=dict()
    for issue_info in dict_url2info.values():
        file=issue_info['file']
        with open(file) as json_file:  
            data = json.load(json_file)
            repo_url=data['repository']['url']
            if repo_url not in dict_repo2files:
                dict_repo2files[repo_url]=[]
#             else:
#                 print("repo_url:{} existing files:{},{}".format(repo_url,file,dict_repo2files[repo_url]))
            dict_repo2files[repo_url].append(file)
            
    print("unique PRs in org {} are from {} repos".format(org,len(dict_repo2files)))
    pickle.dump(dict_repo2files,open(dir+"/dict_repo2files","wb"))
    
    dict_repo2info={repo_url:api.buildProjInfo(files) for repo_url,files in dict_repo2files.items()}
    pickle.dump(dict_repo2info,open(dir+"/dict_repo2info","wb"))
    return dict_repo2info

def getUniquePRsInOrgs(ws="/home/peipei/GitHubIssues/Orgs/"):
    for org in ["apache","mozilla","google","facebook"]:
#         prs,repos=[],[]
        dict_file2url,dict_url2info=getUniquePRsInOrg(ws+org,org)
        dict_repo2info=getUniqueReposInOrg(dict_url2info,ws+org,org)
        
        prs_urls,repo_urls=dict_url2info.keys(),dict_repo2info.keys()
#         prs.extend(prs)
#         repos.extend(repo_urls)
        print("total unique issue-{} unique repo-{}".format(len(set(prs_urls)),len(set(repo_urls))))
    

def getPRInfoPerLangPerRepo(url2info_file,repo2info_file,file_csv,dir="/home/peipei/GitHubIssues/Orgs/apache/"):
    #file_data: the name of the dict_rep2info file
    res=[]
    with open(dir+url2info_file,"rb") as pickle_file:
        dict_url2info = pickle.load(pickle_file)
    with open(dir+repo2info_file,"rb") as pickle_file:
        dict_repo2info = pickle.load(pickle_file)
    
    for pr_url, pr_info in dict_url2info.items():
        repo_url=pr_info['repo_url']
        primaryLang=dict_repo2info[repo_url]['primaryLanguage']
        res.append({"repo_url":repo_url,"primeLang":primaryLang,"pr_url":pr_url,"merged":pr_info['merged']})
        pr_info['lang']=primaryLang
          
    with open(dir+file_csv, 'w', encoding='utf8', newline='') as output_file:
        dict_writer = csv.DictWriter(output_file,fieldnames=res[0].keys())
        dict_writer.writeheader()
        dict_writer.writerows(res)
    
    pickle.dump(dict_url2info,open(dir+"dict_url2info","wb"))

def getDuplicatedPRs(url2info_file,dir="/home/peipei/GitHubIssues/Orgs/apache/"):
    res=dict()
    from github import Github
    github=Github("870589d0ca53859c2e4e54f71b1bdce3af5e609f")
    with open(dir+url2info_file,"rb") as pickle_file:
        dict_url2info = pickle.load(pickle_file)
    for pr_url, pr_info in dict_url2info.items():
        repo_url=pr_info['repo_url']
        if repo_url not in res:
            res[repo_url]=dict()
        id,user,title,merged=api.getPRInfo(github, pr_url)
        if title not in res[repo_url]:
            res[repo_url][title]=[(id,pr_url,merged)]
        else:
            res[repo_url][title].append((id,pr_url,merged))
    
    for repo_url, titleInfos in res.items():
        count1,count2=0,0
        for title, prInfos in titleInfos.items():
            if len(prInfos)>1:
                count1+=1
                count2+=(len(prInfos)-1)
                print("in repo {} {} pull requests have the same title, they are: ".format(repo_url,len(prInfos),title))
                print(sorted(prInfos,key=lambda prInfo: prInfo[0]))
                print("--------------------------------")
        if count1>0:
            print("in repo {} total same-titled pull requests: {} groups in {} prs".format(repo_url,count1,count2))


re_version=re.compile("to\s+(version)?\s*v?\d+\.\d+\.\d+")
def getDependencyPRs(url2info_file,dir="/home/peipei/GitHubIssues/Orgs/apache/"):
    definite_userCnt={"pyup-bot":0,"greenkeeperio-bot":0,"renovate[bot]":0,"dependabot-preview[bot]":0}
    definite_res=list()
    indefinite_res=list()
    indefinite_res2=list()

    from github import Github
    github=Github("870589d0ca53859c2e4e54f71b1bdce3af5e609f")
    
    #test the user login name
#     print(api.getPRInfo(github, "https://github.com/mozilla/experiments-viewer/pull/381"))
#     print(api.getPRInfo(github, "https://github.com/mozilla/payments-client/pull/89"))
#     print(api.getPRInfo(github, "https://github.com/mozilla/foundation.mozilla.org/pull/1935"))
#     print(api.getPRInfo(github, "https://github.com/mozilla/delivery-console/pull/124"))
    
    
    
    
    with open(dir+url2info_file,"rb") as pickle_file:
        dict_url2info = pickle.load(pickle_file)
    print("total pr:{}".format(len(dict_url2info)))
     
    for pr_url, pr_info in dict_url2info.items():
        repo_url=pr_info['repo_url']
        id,user,title,merged=api.getPRInfo(github, pr_url)
        if user in definite_userCnt:
            definite_userCnt[user]+=1
            definite_res.append((pr_url,user,title,merged))
        elif any([keyword in title for keyword in ['dependency','package']]):
            indefinite_res.append((pr_url,user,title,merged))
        elif re_version.search(title) is not None:
            indefinite_res2.append((pr_url,user,title,merged))
    
    if definite_res:
        print("Definite dependency PRs")
        print(definite_userCnt)
        for pr_url,user,title,merged in definite_res:
            print("{},'{}','{}'".format(pr_url,user,title,merged))
    if indefinite_res:
        print("Indefinite dependency PRs by keywords")
        for pr_url,user,title,merged in indefinite_res:
            print("{},'{}','{}'".format(pr_url,user,title,merged))
    if indefinite_res2:
        print("Indefinite dependency PRs by version")
        for pr_url,user,title,merged in indefinite_res2:
            print("{},'{}','{}'".format(pr_url,user,title,merged))
             
def getPRLinkedIssueInOrg(url2info_file,file_csv,dir="/home/peipei/GitHubIssues/Orgs/apache/"):
    
    with open(dir+url2info_file,"rb") as pickle_file:
        dict_url2info = pickle.load(pickle_file)
    
    
    for pr_url, pr_info in dict_url2info.items():
        linkedIssues=api.isPRLinked2Issue2(pr_url)
        if linkedIssues==[]:
            pr_info['fix']=False
        else:
            pr_info['fix']=True
            pr_info['issue_urls']=linkedIssues
    
    pickle.dump(dict_url2info,open(dir+"dict_url2info","wb"))
    
    query_issue_urls=[issue_url for issue_url in issue_urls if issue_url in infos]
    print("in lang {} {} pull requests are linked with {} issues. Among them {} issues are also going to analyzed ".format(lang,len(dict_pr2issues),len(issue_urls),len(query_issue_urls)))
         
#         with open("/home/peipei/GitHubIssues/"+lang+file_csv, 'w', encoding='utf8', newline='') as output_file:
#             dict_writer = csv.DictWriter(output_file,fieldnames=infos[0].keys())
#             dict_writer.writeheader()
#             dict_writer.writerows(infos)    
if __name__ == '__main__':
#     getUniquePRsInOrgs()
#     getPRInfoPerLangPerRepo("dict_url2info","dict_repo2info","repo_lang_file.csv","/home/peipei/GitHubIssues/Orgs/facebook/")
#     getDuplicatedPRs("dict_url2info","/home/peipei/GitHubIssues/Orgs/google/")
#     getDuplicatedPRs("dict_url2info","/home/peipei/GitHubIssues/Orgs/facebook/")
#     getDuplicatedPRs("dict_url2info","/home/peipei/GitHubIssues/Orgs/mozilla")
#     getDuplicatedPRs("dict_url2info","/home/peipei/GitHubIssues/Orgs/apache/")
    
    
#     getDependencyPRs("dict_url2info","/home/peipei/GitHubIssues/Orgs/google/")
    getDependencyPRs("dict_url2info","/home/peipei/GitHubIssues/Orgs/facebook/")
#     getDependencyPRs("dict_url2info","/home/peipei/GitHubIssues/Orgs/mozilla")
#     getDependencyPRs("dict_url2info","/home/peipei/GitHubIssues/Orgs/apache/")
    pass