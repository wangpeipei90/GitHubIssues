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
import glob
from github import Github
import re
import UniqueQueryResults

# keywords=["close","closes","closed","fix","fixes","fixed","resolve","resolves","resolved"]
r=re.compile("(?i)(close|close[sd]|fix|fixe[sd]|resolve|resolve[sd]):?\s*#?(\d+)")
ws="/home/peipei/GitHubIssues/"
def getLinkedIssueNum(msg):
    m=r.findall(msg)
    return [issue_id for key,issue_id in m] if len(m)>0 else None

def isPRLinked2Issue(github,pr_url):
    ## with GitHub REST API V3
    # pr_url https://github.com/PyGithub/PyGithub/pull/1090
    # return issue url: if not linked return empty list else return issue url string   
    elements=pr_url.split("/")
#     print(elements)
    owner,repo_name,is_pr,id=tuple(elements[3:])
    if is_pr!="pull":
        raise ValueError("isLinked2Issue should pass in a PR URL")
    repo=github.get_repo(owner+"/"+repo_name)
    pr=repo.get_pull(int(id))
    
    candidates=[pr.title,pr.body]
    candidates.extend([cmt.commit.message for cmt in pr.get_commits()])
    candidates=[msg for msg in set(candidates) if msg is not None and msg!='']
    
    isLinked=chain(*[x for x in [getLinkedIssueNum(msg) for msg in candidates] if x is not None])
    return ["{}issues/{}".format(pr_url[:pr_url.index(is_pr)],x) for x in set(isLinked)]

def isPRLinked2Issue2(pr_url):
    ## with GitHub GraphQL API V4
    # pr_url https://github.com/PyGithub/PyGithub/pull/1090
    # return issue url: if not linked return empty list else return issue url string   
    elements=pr_url.split("/")
#     print(elements)
    owner,repo_name,is_pr,id=tuple(elements[3:])
    if is_pr!="pull":
        raise ValueError("isLinked2Issue should pass in a PR URL")
    
    isLinked=UniqueQueryResults.getMsgPerPRRepo(owner, repo_name, id, 10)
    return ["{}issues/{}".format(pr_url[:pr_url.index(is_pr)],x) for x in isLinked]

def getLang(file):
    # return from which lang the issue is found
    prefix_len=len(ws)
    sub_filename=file[prefix_len:]
    loc_index=sub_filename.index("/")
    return sub_filename[:loc_index]

def isPR(issue_url):
    #issue_url: pr_url 
    loc_index=issue_url.rindex("/")
    if issue_url[loc_index-6:loc_index]=="issues":
        return False
    elif issue_url[loc_index-4:loc_index]=="pull":
        return True
    else:
        raise ValueError("Uncommon issue url!!!")
    
def getLatestProjInfo(files):
    # files: list of issue file path
    # return the repo data with the latest updated time
    dict_time2Repo=dict()
    for file in files:
        with open(file) as json_file:  
            data = json.load(json_file)
            dict_time2Repo[data['repository']['updatedAt']]=data['repository']
    latest_time=max(dict_time2Repo.keys(),key=lambda updated_time:datetime.strptime(updated_time,'%Y-%m-%dT%H:%M:%SZ'))
    return dict_time2Repo[latest_time]

def buildProjInfo(files):
    # files: list of issue file path
    # return a ProjInfo with selected attributed form json file
    # and the issues found in the repo in form of file path
    proj_info={"files":files}
    latest_info=getLatestProjInfo(files)
    for key in ["url","createdAt","updatedAt", "diskUsage", "primaryLanguage", "forkCount","stargazers","watchers","releases",
                "pullRequests","issues","assignableUsers"]:
        proj_info[key]=latest_info[key]
    proj_info['#lang']=len(latest_info['languages'])
    proj_info['sizeLang']=sum(latest_info['languages'].values())
    
    return proj_info

def buildIssueInfo(file,is_pr=False):
    # file: issue file path
    # return dict as issue info with repo url
    issue_info=dict()
    with open(file) as json_file:
        data = json.load(json_file)
        for key in ["url","comments", "labels","participants"]:
            issue_info[key]=data[key]
        
        createdAt,closedAt=data['createdAt'],data['closedAt']
        createdAt=datetime.strptime(createdAt,'%Y-%m-%dT%H:%M:%SZ')
        closedAt=datetime.strptime(closedAt,'%Y-%m-%dT%H:%M:%SZ')
        
        duration=closedAt-createdAt
        issue_info["duration"]=duration.total_seconds()/(24*60*60) ##from create to close
        
        issue_info['file']=file
        issue_info['type']=getLang(file)
        issue_info['repo_url']=data['repository']['url']
        
        issue_info['is_pr']=False
        issue_info['merged']=False
        if is_pr or isPR(issue_info['url']):
            issue_info['is_pr']=True
            issue_info['merged']=data['merged'] 
    return issue_info 

def getUniqueIssues(dir,is_pr=False):
    ##is_pr false means we are not sure if it is a pr
    print("Processing dir-{}".format(dir))
    dict_file2url=dict()
    dict_url2info=dict()
    
    fileList=glob.glob(dir+"/data_*.json")
    print("# files-{}".format(len(fileList)))
    for file in fileList:
        with open(file) as json_file:  
            data = json.load(json_file)
            issue_url=data['url']
            
            dict_file2url[file]=issue_url
            if issue_url in dict_url2info:
                print("Duplicated url-{} file1-{} file2-{}".format(issue_url, file,dict_url2info[data['url']]))
                pass
            else:
                dict_url2info[data['url']]=buildIssueInfo(file,is_pr)

    print("unique issues in {} is {}".format(dir,len(dict_url2info)))
    return dict_file2url,dict_url2info

def getUniqueIssuesInLang(lang="python"):   
    dict_file2url1,dict_url2info1=getUniqueIssues("/home/peipei/GitHubIssues/"+lang+"/shortKey")
    dict_file2url2,dict_url2info2=getUniqueIssues("/home/peipei/GitHubIssues/"+lang+"/longKey")
    
    dict_file2url={**dict_file2url1,**dict_file2url2}
    dict_url2info = {**dict_url2info1, **dict_url2info2}
    
    print("unique issues in lang {} is {}".format(lang,len(dict_url2info)))
    
    pickle.dump(dict_file2url,open("/home/peipei/GitHubIssues/"+lang+"/dict_file2url","wb"))
    pickle.dump(dict_url2info,open("/home/peipei/GitHubIssues/"+lang+"/dict_url2info","wb"))
    
    return dict_file2url,dict_url2info

def getUniqueProjectsInLang(dict_url2info,lang="python"):
    dict_repo2files=dict()
    for issue_info in dict_url2info.values():
        file=issue_info['file']
        with open(file) as json_file:  
            data = json.load(json_file)
            repo_url=data['repository']['url']
            if repo_url not in dict_repo2files:
                dict_repo2files[repo_url]=[]
            dict_repo2files[repo_url].append(file)
            
    print("unique issues in lang {} are from {} repos".format(lang,len(dict_repo2files)))
    pickle.dump(dict_repo2files,open("/home/peipei/GitHubIssues/"+lang+"/dict_repo2files","wb"))
    
    dict_repo2info={repo_url:buildProjInfo(files) for repo_url,files in dict_repo2files.items()}
    pickle.dump(dict_repo2info,open("/home/peipei/GitHubIssues/"+lang+"/dict_repo2info","wb"))
    return dict_repo2info

def getUniqueIssuesRepos():
    issues,repos=[],[]
    for lang in ["python","java","ruby","javascript","php"]:
        dict_file2url,dict_url2info=getUniqueIssuesInLang(lang)
        dict_repo2info=getUniqueProjectsInLang(dict_url2info,lang)
        
        issue_urls,repo_urls=dict_url2info.keys(),dict_repo2info.keys()
        issues.extend(issue_urls)
        repos.extend(repo_urls)
    print("total unique issue-{} unique repo-{}".format(len(set(issues)),len(set(repos))))

    
def getIssuePerLangPerRepo(repo2info_file,file_csv):
    #file_data: the name of the dict_rep2info file
    res=[]
    for lang in ["python","java","ruby","javascript","php"]:
        with open("/home/peipei/GitHubIssues/"+lang+repo2info_file,"rb") as pickle_file:
            dict_repo2info = pickle.load(pickle_file)
            for repo_url, repo_info in dict_repo2info.items():
                res.append({"repo_url":repo_url,"type":lang,"files":len(repo_info['files'])})
                
    with open("/home/peipei/GitHubIssues/"+file_csv, 'w', encoding='utf8', newline='') as output_file:
        dict_writer = csv.DictWriter(output_file,fieldnames=res[0].keys())
        dict_writer.writeheader()
        dict_writer.writerows(res)
    
def printInfo2CSV(file_data,file_csv):
    for lang in ["python","java","ruby","javascript","php"]:
#         print("file-{}".format("/home/peipei/GitHubIssues/"+lang+file_data))
        with open("/home/peipei/GitHubIssues/"+lang+file_data,"rb") as pickle_file:
            infos = list(pickle.load(pickle_file).values())
#         print(type(infos))
#         pprint(infos[0])

        if "files" in infos[0]:
            for info in infos:
                info['files']=len(info['files'])
            
        with open("/home/peipei/GitHubIssues/"+lang+file_csv, 'w', encoding='utf8', newline='') as output_file:
            dict_writer = csv.DictWriter(output_file,fieldnames=infos[0].keys())
            dict_writer.writeheader()
            dict_writer.writerows(infos)

def getPRLinkedIssueInfo(url2info_file_data,g):
     
    for lang in ["python","java","ruby","javascript","php"]:#
        with open("/home/peipei/GitHubIssues/"+lang+"/dict_file2url","rb") as pickle_file:
            dict_file2url = pickle.load(pickle_file)
                        
#         print("file-{}".format("/home/peipei/GitHubIssues/"+lang+file_data))
        with open("/home/peipei/GitHubIssues/"+lang+url2info_file_data,"rb") as pickle_file:
            dict_url2info = pickle.load(pickle_file)

        dict_pr2issues={info['url']:isPRLinked2Issue(g,info['url']) for info in dict_url2info.values() if info['is_pr']}
        dict_pr2issues={pr_url:issue_urls for pr_url,issue_urls in dict_pr2issues.items() if len(issue_urls)>0}
        
        issue_urls=list(chain(*dict_pr2issues.values()))
        query_issue_urls=[issue_url for issue_url in issue_urls if issue_url in dict_url2info.keys()]
        print("in lang {} {} pull requests are linked with {} issues. Among them {} issues are also going to analyzed ".format(lang,len(dict_pr2issues),len(issue_urls),len(query_issue_urls)))
        pprint(issue_urls)    
#         with open("/home/peipei/GitHubIssues/"+lang+file_csv, 'w', encoding='utf8', newline='') as output_file:
#             dict_writer = csv.DictWriter(output_file,fieldnames=infos[0].keys())
#             dict_writer.writeheader()
#             dict_writer.writerows(infos)
                    
def filterInfo(dict_info,keys,values):
    res=dict()
    for url,info in dict_info.items():
        count_down=len(keys)
#             print(projInfo['url'])
        for (key,value) in zip(keys,values):
            if info[key]>value:
                count_down-=1
        if count_down==0:
            res[url]=info
#     print(len(res))
    return res


def filterByProject(keys=['stargazers','issues','assignableUsers','releases','pullRequests'],values=[0,10,8,0,0]):
    for lang in ["python","java","ruby","javascript","php"]:
        with open("/home/peipei/GitHubIssues/"+lang+"/dict_repo2info","rb") as pickle_file:
            dict_repo2info = pickle.load(pickle_file)
        
        dict_repo2info_f=filterInfo(dict_repo2info,keys,values)
        pickle.dump(dict_repo2info_f,open("/home/peipei/GitHubIssues/"+lang+"/dict_repo2info_f","wb"))
              
        ##update issues after filtered by proj
        with open("/home/peipei/GitHubIssues/"+lang+"/dict_file2url","rb") as pickle_file:
            dict_file2url = pickle.load(pickle_file)
        issue_urls=[]
        for info in dict_repo2info_f.values():
            files=info['files']
            issue_urls.extend([dict_file2url[file] for file in files])
        with open("/home/peipei/GitHubIssues/"+lang+"/dict_url2info","rb") as pickle_file:
            dict_url2info = pickle.load(pickle_file)
            
        dict_url2info_f={issue_url:dict_url2info[issue_url] for issue_url in issue_urls}
        pickle.dump(dict_url2info_f,open("/home/peipei/GitHubIssues/"+lang+"/dict_url2info_f","wb"))
        print("after filtering by repos, {} issues in lang {} are from {} repos".format(len(dict_url2info_f),lang,len(dict_repo2info_f)))
        
def filterByIssue(keys=['duration','participants','comments','labels'],values=[1,0,0,0]):
    for lang in ["python","java","ruby","javascript","php"]:
        with open("/home/peipei/GitHubIssues/"+lang+"/dict_url2info_f","rb") as pickle_file:
            dict_url2info_f = pickle.load(pickle_file) 
        
        dict_url2info_ff=filterInfo(dict_url2info_f,keys,values)
        pickle.dump(dict_url2info_ff,open("/home/peipei/GitHubIssues/"+lang+"/dict_url2info_ff","wb"))
        
        ## update repos after filtering by issues
        repo_urls=[info['repo_url'] for info in dict_url2info_ff.values()]              
        with open("/home/peipei/GitHubIssues/"+lang+"/dict_repo2info_f","rb") as pickle_file:
            dict_repo2info_f = pickle.load(pickle_file)
        
        dict_repo2info_ff={repo_url:dict_repo2info_f[repo_url] for repo_url in repo_urls}
        
        # updated included issues in repo after filtering by issues
        with open("/home/peipei/GitHubIssues/"+lang+"/dict_file2url","rb") as pickle_file:
            dict_file2url = pickle.load(pickle_file)
        for repo_url, info in dict_repo2info_ff.items():
            files_f=[file for file in info['files'] if dict_file2url[file] in dict_url2info_ff]
            info['files']=files_f
        
        pickle.dump(dict_repo2info_ff,open("/home/peipei/GitHubIssues/"+lang+"/dict_repo2info_ff","wb"))
        
        print("after filtering by issue, {} issues in lang {} are from {} repos".format(len(dict_url2info_ff),lang,len(dict_repo2info_ff)))
        
if __name__ == '__main__':
#     getUniqueIssuesInLang("python")
#     getUniqueIssuesRepos()
#     getIssuePerLangPerRepo("/dict_repo2info","type_repo_issue.csv")
#     filterByProject()
#     getIssuePerLangPerRepo("/dict_repo2info_f","type_repo_issue_f.csv")
#     filterByIssue()
#     getIssuePerLangPerRepo("/dict_repo2info_ff","type_repo_issue_ff.csv")
    
#     printInfo2CSV("/dict_repo2info","/repoInfo.csv")
#     printInfo2CSV("/dict_repo2info_f","/repoInfo_f.csv")
#     printInfo2CSV("/dict_repo2info_ff","/repoInfo_ff.csv")
    
#     printInfo2CSV("/dict_url2info","/issueInfo.csv")
#     printInfo2CSV("/dict_url2info_f","/issueInfo_f.csv")
#     printInfo2CSV("/dict_url2info_ff","/issueInfo_ff.csv")
    
    g = Github("870589d0ca53859c2e4e54f71b1bdce3af5e609f")
    getPRLinkedIssueInfo("/dict_url2info_ff",g)
#     getPRLinkedIssueInfo("/dict_url2info_f",g)
    pass

