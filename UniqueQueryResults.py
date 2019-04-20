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
    
if __name__ == '__main__':
    getCmtMsgPerRepo("PyGithub","PyGithub",'100')
    
    pass

