'''
Created on Feb 19, 2019

@author: peipei
'''
import pickle
from pprint import pprint
import json
import sys
import glob
import requests
import GraphQLQuery
import api
from itertools import chain
def getCmtMsgPerRepo(owner, name, first):
    query=GraphQLQuery.getFirstQueryCmtMsgPerRepo(owner, name, first)
    data=GraphQLQuery.run_query(query)
    
    hasNextPage=data['data']['repository']['ref']['target']['history']['pageInfo']['hasNextPage']
    endCursor=data['data']['repository']['ref']['target']['history']['pageInfo']['endCursor']
    data_msg=[cmt['node']['message'] for cmt in data['data']['repository']['ref']['target']['history']['edges']]
    count=1
    print("count:{} endCursor:{} size of data:{}".format(count,endCursor,len(data_msg)))
#     print(type(endCursor))
#     print(endCursor)
#     print(len(data_msg))   
    issues=[api.getLinkedIssueNum(msg) for msg in data_msg if msg is not None and msg!=""]
    issues=[item for item in issues if item is not None]
    print(issues)
    while hasNextPage:
        query=GraphQLQuery.getNextQueryCmtMsgPerRepo(owner, name, first, endCursor)
        data=GraphQLQuery.run_query(query)
        print(data.keys())
        if 'data' not in data:
            print(query)
            pprint(data)
            break
        hasNextPage=data['data']['repository']['ref']['target']['history']['pageInfo']['hasNextPage']
        endCursor=data['data']['repository']['ref']['target']['history']['pageInfo']['endCursor']
        data_msg=[cmt['node']['message'] for cmt in data['data']['repository']['ref']['target']['history']['edges']]
        
        count+=1
        print("count:{} endCursor:{} size of data:{}".format(count,endCursor,len(data_msg)))
#         print(len(data_msg))   
        temp=[api.getLinkedIssueNum(msg) for msg in data_msg if msg is not None and msg!=""]
        issues.extend([item for item in temp if item is not None])
    print(issues)
#     return data_msg

def getMsgPerPRRepo(owner, name, id_pr, first):
    query=GraphQLQuery.getFirstQueryMsgPerPRRepo(owner, name, id_pr, first)
    data=GraphQLQuery.run_query(query)
    
    hasNextPage=data['data']['repository']['pullRequest']['commits']['pageInfo']['hasNextPage']
    endCursor=data['data']['repository']['pullRequest']['commits']['pageInfo']['endCursor']
    data_msg=[cmt['node']['commit']['message'] for cmt in data['data']['repository']['pullRequest']['commits']['edges']]
    count=1
    print("count:{} endCursor:{} size of data:{}".format(count,endCursor,len(data_msg)+2))
    
    data_msg.extend([data['data']['repository']['pullRequest']['title'],data['data']['repository']['pullRequest']['bodyText']])
    
    while hasNextPage:
        query=GraphQLQuery.getNextQueryMsgPerPRRepo(owner, name, id_pr, first, endCursor)
        data=GraphQLQuery.run_query(query)
        print(data.keys())
#         if 'data' not in data:
#             print(query)
#             pprint(data)
#             break
        hasNextPage=data['data']['repository']['pullRequest']['commits']['pageInfo']['hasNextPage']
        endCursor=data['data']['repository']['pullRequest']['commits']['pageInfo']['endCursor']
        
        data_msg.extend([cmt['node']['commit']['message'] for cmt in data['data']['repository']['pullRequest']['commits']['edges']])
        
        count+=1
        print("count:{} endCursor:{} size of data:{}".format(count,endCursor,len(data_msg)))
        
    issues=[api.getLinkedIssueNum(msg) for msg in set(data_msg) if msg is not None and msg!=""]
#     print(issues)
    issues=list(chain(*[item for item in issues if item is not None]))
    print(issues)
    return issues


def getPRsInOrg(org,first,ws="/home/peipei/GitHubIssues/Orgs/"):
    query=GraphQLQuery.getFirstQueryPRsInOrg(org, first)
    data=GraphQLQuery.run_query(query)
    
    hasNextPage=data['data']['search']['pageInfo']['hasNextPage']
    endCursor=data['data']['search']['pageInfo']['endCursor']
    
    totalCount=data['data']['search']['issueCount']
    print("total issueCount - {}".format(totalCount))
    
#     n_issues=len(data['data']['search']['edges'])
#     if n_issues<first:
#         raise Exception("Not enough data returned, return size - {}, query size - {}".format(n_issues,res_size))
#     
#     print("FirstQuery endCursor - {}".format(endCursor))
     
    count,query_id,res=0,1,data['data']['search']['edges']
    count+=len(res)
    print("count:{} endCursor:{}".format(count,endCursor))
    
    GraphQLQuery.parseSaveResultInfo(res,query_id,ws+org)
    while hasNextPage:
        query_id+=1
        query=GraphQLQuery.getNextQueryPRsInOrg(org, first, endCursor)
        data=GraphQLQuery.run_query(query)
#         print(data.keys())
        if 'data' not in data:
            print(query)
            pprint(data)
            break
        hasNextPage=data['data']['search']['pageInfo']['hasNextPage']
        endCursor=data['data']['search']['pageInfo']['endCursor']
        
        res=data['data']['search']['edges']
        count+=len(res)
        print("count:{} endCursor:{}".format(count,endCursor))
        
        GraphQLQuery.parseSaveResultInfo(res,query_id,ws+org)
#     return data_msg

if __name__ == '__main__':
#     getCmtMsgPerRepo("PyGithub","PyGithub",'100')
    getPRsInOrg("apache",10,ws="/home/peipei/GitHubIssues/Orgs/")
    pass

