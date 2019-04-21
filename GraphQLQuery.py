'''
Created on Feb 19, 2019

@author: peipei
'''
import requests
import json
from time import sleep
import sys
from datetime import datetime
headers = {"Authorization": "token 15fb92d880eea329e3a7a512156f9bda46ee3a1a"}

# The GraphQL query (with a few aditional bits included) itself defined as a multi-line string.       
query1 = """
{
  viewer {
    login
  }
  rateLimit {
    limit
    cost
    remaining
    resetAt
  }
}
"""
query_limit=1000
res_size=10
subQueries_longJava={"queryString": "'regular Expression' state:closed updated:<2019-02-01 language:Java","first": res_size}
subQueries_longPython={"queryString": "'regular Expression' state:closed updated:<2019-02-01 language:Python","first": res_size}
subQueries_longJS={"queryString": "'regular Expression' state:closed updated:<2019-02-01 language:JavaScript","first": res_size}
subQueries_longPhp={"queryString": "'regular Expression' state:closed updated:<2019-02-01 language:PHP","first": res_size}
subQueries_longRuby={"queryString": "'regular Expression' state:closed updated:<2019-02-01 language:Ruby","first": res_size}
subQueries_shortJava={"queryString": "'regex' state:closed updated:<2019-02-01 language:Java","first": res_size}
subQueries_shortPython={"queryString": "'regex' state:closed updated:<2019-02-01 language:Python","first": res_size}
subQueries_shortJS={"queryString": "'regex' state:closed updated:<2019-02-01 language:JavaScript","first": res_size}
subQueries_shortPhp={"queryString": "'regex' state:closed updated:<2019-02-01 language:PHP","first": res_size}
subQueries_shortRuby={"queryString": "'regex' state:closed updated:<2019-02-01 language:Ruby","first": res_size}


def run_query(query): # A simple function to use requests.post to make the API call. Note the json= section.
    request = requests.post('https://api.github.com/graphql', json={'query': query}, headers=headers)
#     print("request return code - {}".format(request.status_code))
    if request.status_code == 200:
        return request.json()
#     else:
#         tries=3
#         while request.status_code != 200 and tries>0:
#             print("sleep {} min".format(4-tries))
#             sleep((4-tries)*60)
# 
#             request = requests.post('https://api.github.com/graphql', json={'query': query}, headers=headers)
#             tries-=1
#             print("Retry {} th".format(3-tries))
#         if request.status_code == 200:
#             return request.json()
    else: 
        print("request return code - {}".format(request.status_code))
        raise Exception("Query failed to run by returning code of {}. {}".format(request.status_code, query))
    
def checkTokenLimit():
    result = run_query(query1) # Execute the query
    remaining_rate_limit = result["data"]["rateLimit"]["remaining"] # Drill down the dictionary
    print("Remaining rate limit - {}".format(remaining_rate_limit))
    
    resetTime = result["data"]["rateLimit"]["resetAt"]
    print("GitHub API must be reset to time - {}".format(resetTime))
    
    resetTime=datetime.strptime(resetTime,'%Y-%m-%dT%H:%M:%SZ')
    nowTimeUTC=datetime.utcnow()
    print("UTC time now - {}".format(nowTimeUTC))
    if nowTimeUTC.date()==resetTime.date() and nowTimeUTC.time()<resetTime.time():
        print("will reset in future")
        return remaining_rate_limit
    else:
        raise Exception("resetAt error")
    
    
def run_first_query(query_id,subQuery):
    print("{} th query".format(query_id))
    result = run_query(getFirstQueryIssueSearch(subQuery))
    
    totalCount=result['data']['search']['issueCount']
    print("total issueCount - {}".format(totalCount))
    
    remain_token=result["data"]["rateLimit"]["remaining"]
    print("remain token - {}".format(remain_token))
    
    n_issues=len(result['data']['search']['edges'])
    if n_issues<res_size:
        raise Exception("Not enough data returned, return size - {}, query size - {}".format(n_issues,res_size))
     
    lastCursor=result['data']['search']['pageInfo']['endCursor']
    hasNextPage=result['data']['search']['pageInfo']['hasNextPage']
    
    print("FirstQuery lastCursor - {}".format(lastCursor))
     
    return result,hasNextPage,lastCursor,remain_token

def run_next_query(query_id,subQuery,lastCursor):
    print("{} th query".format(query_id))
    
    result = run_query(getNextQueryIssueSearch(subQuery,lastCursor))
    
    if 'data' not in result:
        print(result)
        raise Exception("GraphQL query Error id - {}".format(query_id))

    remain_token=result["data"]["rateLimit"]["remaining"]
    print("remain token - {}".format(remain_token))
    
    n_issues=len(result['data']['search']['edges'])
    if n_issues<res_size:
        raise Exception("Not enough data returned, return size - {}, query size - {}".format(n_issues,res_size))
    
    lastCursor=result['data']['search']['pageInfo']['endCursor']
    hasNextPage=result['data']['search']['pageInfo']['hasNextPage']
    print("NextQuery lastCursor - {}".format(lastCursor))

    return result,hasNextPage,lastCursor,remain_token

def parseRepoInfo(repo):
    if repo['primaryLanguage'] is not None and 'name' in repo['primaryLanguage']:
        repo['primaryLanguage']=repo['primaryLanguage']['name']
    temp={}
    for lang in repo['languages']['edges']:
        temp[lang['node']['name']]=lang['size']
    repo['languages']=temp
    for k,v in repo.items():
        if type(v) is dict and 'totalCount' in v:
            repo[k]=repo[k]['totalCount']
#     print(repo)
    return repo

def parseIssueInfo(issue):
        for k,v in issue.items():
            if type(v) is dict and 'totalCount' in v:
                issue[k]=issue[k]['totalCount']
#         print(issue)
        issue['repository']=parseRepoInfo(issue['repository'])
        return issue
    
def parseSaveResultInfo(results,query_id,ws):
    id=-1
    for info in results['data']['search']['edges']:
        obj=parseIssueInfo(info['node'])
        obj['cursor']=info['cursor']
        id+=1
        with open(ws+'/data_'+str(query_id)+"_"+str(id)+'.json', 'w') as outfile:
            json.dump(obj, outfile)

def query_issue(subQuery,ws):
    times=query_limit//res_size
    print("times - {}".format(times))
    
    query_id=1
    result,hasNextPage,lastCursor,remain_token=run_first_query(query_id,subQuery)
    parseSaveResultInfo(result,query_id,ws)
       
    #times=10
    while hasNextPage:
        if remain_token>0:
            query_id+=1
            result,hasNextPage,lastCursor,remain_token=run_next_query(query_id,subQuery,lastCursor)
            parseSaveResultInfo(result,query_id,ws)
        else:
            sleep(3600)
            while checkTokenLimit()<4000:
                sleep(60)

def query_issueFollowing(query_id,lastCursor,subQuery,ws):
    remain_token=checkTokenLimit()
    hasNextPage=True
    while hasNextPage:
#     if query_id<=times:
        if remain_token>0:
            result,hasNextPage,lastCursor,remain_token=run_next_query(query_id,subQuery,lastCursor)
            parseSaveResultInfo(result,query_id,ws)
            query_id+=1
        else:
            print("sleep because of token limits")
            sleep(3600)
            while checkTokenLimit()<4000:
                sleep(60)

def getFirstQueryIssueSearch(variables):
    query_first = """
{{
    rateLimit {{
        remaining
        resetAt
    }}
    
    search(query: "{queryString}", type: ISSUE, first: {first}) {{
        issueCount
        pageInfo {{
          hasNextPage
          endCursor
        }}
        edges {{
            node {{
            __typename
            ... on Issue {{
                title
                bodyText
                number
                url
                state
                createdAt
                updatedAt
                closedAt
                comments {{
                    totalCount
                }}            
                labels {{
                    totalCount
                }}
                participants {{
                    totalCount
                }}
                repository {{
                    ... repoInfo
                }}
            }}
            ... on PullRequest {{
                title
                bodyText
                number
                url
                merged
                createdAt
                updatedAt
                closedAt
                lastEditedAt
                publishedAt
                commits {{
                    totalCount
                }}
                comments {{
                    totalCount
                }}
                labels {{
                    totalCount
                }}
                participants {{
                    totalCount
                }}
          
                repository {{
                    ... repoInfo
                }}
            }}
        }}
    }}
  }}
}}
fragment repoInfo on Repository {{
                    id
                    nameWithOwner
                    description
                    url
                    createdAt
                    updatedAt
                    pushedAt
                    diskUsage
                    primaryLanguage {{
                      name
                    }}
                    languages(first: 20, orderBy: {{field: SIZE, direction: DESC}}) {{
                      totalCount
                      totalSize
                      edges {{
                        size
                        node {{
                          name
                        }}
                      }}
                    }}
                    forkCount
                    stargazers {{
                      totalCount
                    }}
                    watchers {{
                      totalCount
                    }}
                    releases {{
                      totalCount
                    }}
                    pullRequests {{
                      totalCount
                    }}
                    issues {{
                      totalCount
                    }}
                    assignableUsers {{
                      totalCount
                    }}
                    collaborators{{
                      totalCount
                    }}
                }}
"""
    return query_first.format(**variables)

def getNextQueryIssueSearch(variables,endCursor):
    query_first = """
{{
    rateLimit {{
        remaining
        resetAt
    }}
    
    search(query: "{queryString}", type: ISSUE, after: "{endCursor}", first: {first}) {{
        issueCount
        pageInfo {{
          hasNextPage
          endCursor
        }}
        edges {{
            node {{
            __typename
            ... on Issue {{
                title
                bodyText
                number
                url
                state
                createdAt
                updatedAt
                closedAt
                comments {{
                    totalCount
                }}            
                labels {{
                    totalCount
                }}
                participants {{
                    totalCount
                }}
                repository {{
                    ... repoInfo
                }}
            }}
            ... on PullRequest {{
                title
                bodyText
                number
                url
                merged
                createdAt
                updatedAt
                closedAt
                lastEditedAt
                publishedAt
                commits {{
                    totalCount
                }}
                comments {{
                    totalCount
                }}
                labels {{
                    totalCount
                }}
                participants {{
                    totalCount
                }}
          
                repository {{
                    ... repoInfo
                }}
            }}
        }}
    }}
  }}
}}
fragment repoInfo on Repository {{
                    id
                    nameWithOwner
                    description
                    url
                    createdAt
                    updatedAt
                    pushedAt
                    diskUsage
                    primaryLanguage {{
                      name
                    }}
                    languages(first: 20, orderBy: {{field: SIZE, direction: DESC}}) {{
                      totalCount
                      totalSize
                      edges {{
                        size
                        node {{
                          name
                        }}
                      }}
                    }}
                    forkCount
                    stargazers {{
                      totalCount
                    }}
                    watchers {{
                      totalCount
                    }}
                    releases {{
                      totalCount
                    }}
                    pullRequests {{
                      totalCount
                    }}
                    issues {{
                      totalCount
                    }}
                    assignableUsers {{
                      totalCount
                    }}
                    collaborators{{
                      totalCount
                    }}
                }}
"""     
    variables["endCursor"]=endCursor
    return query_first.format(**variables)

def getFirstQueryCmtMsgPerRepo(owner,name,first):
    query_first='''
    {{
      repository(owner:{owner}, name:{name}) {{
        description
        ref(qualifiedName: "master") {{
          name
          target{{
            ... on Commit{{
              id
              history(first: {first}) {{
                pageInfo {{
                  hasNextPage
                  endCursor
                }}
                edges {{
                  node {{
                    message
                    oid
                  }}
                }}
              }}
            }}
          }}
        }}
      }}
    }}
    '''
    variables={"owner": owner,"first":first,"name":name}
    return query_first.format(**variables)

def getNextQueryCmtMsgPerRepo(owner,name,first,endCursor):
    query_next='''
    {{
      repository(owner:{owner}, name:{name}) {{
        description
        ref(qualifiedName: "master") {{
          name
          target{{
            ... on Commit{{
              id
              history(first:{first}, after: "{endCursor}") {{
                pageInfo {{
                  hasNextPage
                  endCursor
                }}
                edges {{
                  node {{
                    message
                    oid
                  }}
                }}
              }}
            }}
          }}
        }}
      }}
    }}
    '''
    variables={"owner": owner,"first":first,"name":name,"endCursor":endCursor}
    return query_next.format(**variables)     

def getFirstQueryMsgPerPRRepo(owner,name,id_pr,first):
    query_first='''
{{
  repository(owner: {owner}, name: {name}) {{
    pullRequest(number: {prID}) {{
      title
      bodyText
      commits(first: {first}) {{
        totalCount
          pageInfo{{
            hasNextPage
            endCursor
          }}
        edges {{
          node {{
            commit {{
              oid
              message
            }}
          }}
        }}
      }}
    }}
  }}
}}
'''
    variables={"owner": owner,"first":first,"name":name,"prID":id_pr}
    return query_first.format(**variables)

def getNextQueryMsgPerPRRepo(owner,name,id_pr,first,endCursor):
    query_first='''
{{
  repository(owner: {owner}, name: {name}) {{
    pullRequest(number: {prID}) {{
      title
      bodyText
      commits(first: {first} after: {endCursor}) {{
        totalCount
          pageInfo{{
            hasNextPage
            endCursor
          }}
        edges {{
          node {{
            commit {{
              oid
              message
            }}
          }}
        }}
      }}
    }}
  }}
}}
'''
    variables={"owner": owner,"first":first,"name":name,"prID":id_pr,"endCursor":endCursor}
    return query_first.format(**variables)      
if __name__ == '__main__':
#     checkTokenLimit()
    query_issue(subQueries_shortPhp,"/home/peipei/GitHubIssues/php/shortKey")
#     query_issue(subQueries_longPython,"/home/peipei/GitHubIssues/python/longKey")
#     query_issueFollowing(51, "Y3Vyc29yOjUwMA==", 100, subQueries_longPython,"/home/peipei/GitHubIssues/python/longKey")
    #query_issue2(26,"Y3Vyc29yOjI1MA==",50950)
#     if sys.argv is not None or len(sys.argv)==2:
#         query_issueFollowing(int(sys.argv[1]),sys.argv[2],50950)

    pass
