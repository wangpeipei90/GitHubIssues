if (getwd()!="/home/peipei/GitHubIssues/Orgs/"){
  setwd("/home/peipei/GitHubIssues/Orgs/")
}
library(ggplot2)
library(fifer)
getSummary=function(data){
  print(mean(data))
  print(min(data))
  print(max(data))
  t=c("mean"=mean(data),"max"=max(data),"min"=min(data))
  c(t,quantile(data, c(0.1,0.25,0.5,0.75,0.9,0.95,0.98,0.99)))
  # return(c(t,quantile(data, c(0.1,0.25,0.5,0.75,0.9,0.95,0.98,0.99))))
}

data_file="apache/repo_lang_file.csv"
#data_file="mozilla/repo_lang_file.csv"
# data_file="google/repo_lang_file.csv"
# data_file="facebook/repo_lang_file.csv"
repoLangFile=read.csv(file=data_file,head=TRUE,colClasses=c("character","character","character","logical"), sep=",")
repoLangFile=as.data.frame(repoLangFile)

sort(table(repoLangFile$primeLang)) ## prs in primary lang of repo
dim(table(repoLangFile$repo_url)) ## == # of repos
getSummary(table(repoLangFile$repo_url))  ## prs/repo

t=split(repoLangFile,f=repoLangFile$repo_url) ## length(t)==num(repos)
sort(table(sapply(t, function(repo)unique(repo$primeLang)))) ###  repos in primary langs

tt=split(repoLangFile,f=repoLangFile$primeLang)
for(lang in c("Java","Python","JavaScript","PHP","Ruby")){
  print(lang)
  print(getSummary(table(tt[[lang]]$repo_url)))  ## prs/repo in each lang
}

table(repoLangFile$merged) ## merged prs vs not merged prs
for(lang in c("Java","Python","JavaScript","PHP","Ruby")){
  print(lang)
  print(table(tt[[lang]]$merged))  ## merged/repo in each lang
}

s=as.data.frame(sort(table(repoLangFile$repo_url),decreasing = TRUE))#[1:10,] ## top 10 repos with most prs
names(s)=c("repo","prs")
s$primeLang=sapply(s$repo,function(x)unique(repoLangFile[which(repoLangFile$repo_url==x),"primeLang"])) ## with prime lang
s$merged=sapply(s$repo,function(x)length(which(repoLangFile$repo_url==x & repoLangFile$merged==TRUE)))
s$notMerged=sapply(s$repo,function(x)length(which(repoLangFile$repo_url==x & repoLangFile$merged==FALSE)))

s[s$primeLang=="Python",]

#selected=repoLangFile[which(repoLangFile$repo_url=='https://github.com/mozilla/treeherder'),]
# selected=repoLangFile[which(repoLangFile$repo_url=='https://github.com/apache/pulsar'),]
selected=repoLangFile[which(repoLangFile$repo_url=='https://github.com/apache/kafka'),]
write.csv(selected,'apache_kafka.csv')
print(selected$pr_url)


getRepoPrsLang=function(filename,org){
  print(filename)
  print(org)
  org_repoLangFile=read.csv(file=filename,head=TRUE,colClasses=c("character","character","character","logical"), sep=",")
  org_repoLangFile=as.data.frame(org_repoLangFile)
  m=unique(org_repoLangFile[,c("repo_url","primeLang")])
  for (i in 1:nrow(m)){
    repo_url=m[i,"repo_url"]
    prs=org_repoLangFile[org_repoLangFile$repo_url==m[i,"repo_url"],]
    m[i,"prs"]=nrow(prs)
    m[i,"merged"]=nrow(prs[prs$merged==TRUE,])
    m[i,"unmerged"]=nrow(prs[prs$merged==FALSE,])
  }
  m$org=org
  # return(m)
  org_repoLangFile$org=org
  return(org_repoLangFile)
}
##### For overall process across organizations
filenames=c("apache/repo_lang_file.csv","mozilla/repo_lang_file.csv","google/repo_lang_file.csv","facebook/repo_lang_file.csv")
orgs=c("apache","mozilla","google","facebook")
res=data.frame()
for (i in 1:length(filenames)) {
  res=rbind(res,getRepoPrsLang(filenames[i],orgs[i]))
}
res=res[res$primeLang %in% c("Java","JavaScript","Python"),]
###Stratified Sampling
out=stratified(res, c("merged","primeLang","org"), .1)

sort(table(res$primeLang)) ## repos in primary lang of repo
dim(table(res$repo_url)) ## == # of repos
getSummary(res$prs) ### prs/repo 
# sum(res[res$primeLang=="Java","prs"])

t=split(res,f=res$org) ## length(t)==num(repos)
sapply(t,FUN = function(x)c("all"=nrow(x),"merged"=sum(x$merged),"unmerged"=nrow(x)-sum(x$merged)))
ot=split(out,f=out$org)
stat_ot=sapply(ot,FUN = function(x)c("all"=nrow(x),"merged"=sum(x$merged),"unmerged"=nrow(x)-sum(x$merged)))
stat_ot=cbind(stat_ot,"total"=apply(stat_ot,1,sum))
print(stat_ot)


sapply(t,function(x)getSummary(x$prs))
wilcox.test(t$apache$prs,t$mozilla$prs)
wilcox.test(t$apache$prs,t$google$prs)
wilcox.test(t$apache$prs,t$facebook$prs)
wilcox.test(t$mozilla$prs,t$facebook$prs)
wilcox.test(t$mozilla$prs,t$google$prs)
wilcox.test(t$google$prs,t$facebook$prs)

tt=split(res,f=res$primeLang)
sapply(tt,FUN = function(x)c("all"=nrow(x),"merged"=sum(x$merged),"unmerged"=nrow(x)-sum(x$merged)))

ott=split(out,f=out$primeLang)
stat_ott=sapply(ott,FUN = function(x)c("all"=nrow(x),"merged"=sum(x$merged),"unmerged"=nrow(x)-sum(x$merged)))
stat_ott=cbind(stat_ott,"total"=apply(stat_ott,1,sum))
print(stat_ott)

write.csv(out,'strata_sampling.csv')

# ttt=tt[c("Java","JavaScript","Python")]
# sapply(ttt,FUN = function(x)c("all"=sum(x$prs),"merged"=sum(x$merged),"unmerged"=sum(x$unmerged)))

sapply(tt,function(x)getSummary(x$prs))
wilcox.test(tt$Python$prs,t$Java$prs)
wilcox.test(tt$Python$prs,t$JavaScript$prs)
wilcox.test(tt$Java$prs,t$JavaScript$prs)
# wilcox.test(tt$Java$prs,t$PHP$prs)
# getSummary(tt[["Java"]]$prs)
# getSummary(tt[["JavaScript"]]$prs)
# getSummary(tt[["Python"]]$prs)
sapply(ttt,function(x)getSummary(x$prs))

p=ggplot()+theme_bw()
p=p+geom_boxplot(data=repoInfo,aes(x=type,y=files,fill=type),alpha=0.4)
p=p+scale_fill_brewer()
p=p+coord_cartesian(ylim = c(0, 3))
p=p+labs(x="lang",y="# issue per repo",fill="Lang")
p=p+stat_summary(fun.y=mean, geom="point", shape=20, size=10, color="red", fill="red") 
# p=p+scale_x_discrete(labels=c("Intersection","Addition","Removal"))
#ggsave("abc")



data_file=paste("/home/peipei/GitHubIssues",lang,name, sep = "/", collapse = NULL)
repoInfo_python=read.csv(file=data_file,head=TRUE,colClasses=c("integer","character","character","character","integer",
                                                               "character","integer","integer","integer","integer",
                                                               "integer","integer","integer","integer","integer"), sep=",")

repoInfo=as.data.frame(repoInfo)
sprintf("repo total: %s",nrow(repoInfo))
sprintf("files total: %s",sum(repoInfo$files))



table(repoInfo$files)
getSummary(repoInfo$files)
# mean        max        min        10%        25%        50%        75%        90%        95%        98%        99% 
# 1.714209 113.000000   1.000000   1.000000   1.000000   1.000000   2.000000   3.000000   4.000000   7.000000  11.000000

getSummary(repoInfo$forkCount)
# mean        max        min        10%        25%        50%        75%        90%        95%        98%        99% 
# 266.2732 23889.0000     0.0000     0.0000     1.0000    14.0000   102.0000   459.0000  1054.8000  2749.0800  4873.0400

getSummary(repoInfo$stargazers)
# mean        max        min        10%        25%        50%        75%        90%        95%        98%        99% 
# 1122.904 301523.000      0.000      0.000      2.000     26.000    304.000   2001.200   4849.200  11668.000  19632.080
length(which(repoInfo$stargazers>0)) #4563
length(which(repoInfo$stargazers==0)) #990

getSummary(repoInfo$watchers)
# mean        max        min        10%        25%        50%        75%        90%        95%        98%        99% 
# 65.07834 8409.00000    0.00000    1.00000    3.00000   11.00000   41.00000  130.80000  245.40000  557.80000  901.80000 


getSummary(repoInfo$releases)
#mean        max        min        10%        25%        50%        75%        90%        95%        98%        99% 
#14.47074 2409.00000    0.00000    0.00000    0.00000    0.00000   11.00000   37.00000   66.00000  117.92000  180.84000
length(which(repoInfo$releases>0)) #2714
length(which(repoInfo$releases==0)) #2839

getSummary(repoInfo$pullRequests)
# mean        max        min        10%        25%        50%        75%        90%        95%        98%        99% 
# 504.0351 71160.0000     0.0000     3.0000    13.0000    65.0000   291.0000  1013.0000  2192.0000  4540.1200  7489.2000
length(which(repoInfo$pullRequests>0)) #5331
length(which(repoInfo$pullRequests==0)) #222

getSummary(repoInfo$issues)
# mean        max        min        10%        25%        50%        75%        90%        95%        98%        99% 
# 400.5503 32163.0000     0.0000     0.0000     5.0000    36.0000   224.0000   873.0000  1935.4000  3728.5200  6000.0000
length(which(repoInfo$issues>10)) #3680
length(which(repoInfo$issues<=10)) #1873


getSummary(repoInfo$assignableUsers)
# mean         max         min         10%         25%         50%         75%         90%         95%         98%         99% 
# 81.42878 12779.00000     1.00000     1.00000     1.00000     6.00000    22.00000    67.00000   155.00000   494.00000  1073.48000
length(which(repoInfo$assignableUsers>8)) #2414
length(which(repoInfo$assignableUsers<=8)) #3139


getSummary(repoInfo$X.lang)
# mean       max       min       10%       25%       50%       75%       90%       95%       98%       99% 
# 3.750765 20.000000  0.000000  1.000000  2.000000  3.000000  5.000000  7.000000  9.000000 12.000000 16.480000
table(repoInfo$X.lang)
# 0    1   10   11   12   13   14   15   16   17   18   19    2   20    3    4    5    6    7    8    9 
# 5 1367   52   63   34   21   11   11   10    8    5   19  972   24  875  713  480  362  243  175  103

getSummary(repoInfo$sizeLang/1024)
# mean          max          min          10%          25%          50%          75%          90%          95%          98%          99% 
# 3013.09101 399644.48633      0.00000     16.57559     53.13574    227.36035   1129.77441   4493.75371  10388.47734  27863.74715  49016.8085

length(which(repoInfo$pullRequests>0 & repoInfo$stargazers>0 & repoInfo$releases>0 & repoInfo$issues>10 & repoInfo$assignableUsers>8)) #1115


name="repoInfo.csv"
lang="python"
langs=c("java","python","javascript","php","ruby")
filenames=c("repoInfo.csv","repoInfo_f.csv","repoInfo_ff.csv")
for (i in 1:length(filenames)) { 
  name=filenames[i]
  df=data.frame()
  for (j in 1:length(langs)){
    lang=langs[j]
    data_file=paste("/home/peipei/GitHubIssues",lang,name, sep = "/", collapse = NULL)
    repoInfo=read.csv(file=data_file,head=TRUE,colClasses=c("integer","character","character","character","integer",
                                                            "character","integer","integer","integer","integer",
                                                            "integer","integer","integer","integer","integer"), sep=",")
    message(sprintf("file name: %s lang: %s",name,lang))
    print(nrow(repoInfo))
    print("stargazers")
    print(getSummary(repoInfo$stargazers))
    print("issues")
    print(getSummary(repoInfo$issues))
    print("releases")
    print(getSummary(repoInfo$releases))
    print("pullRequests")
    print(getSummary(repoInfo$pullRequests))
    print("assignableUsers")
    print(getSummary(repoInfo$assignableUsers))
    
    df=rbind(df,repoInfo)
  }
  print(nrow(df))
  print("across lang stargazers")
  print(getSummary(df$stargazers))
  print("across lang issues")
  print(getSummary(df$issues))
  print("across lang releases")
  print(getSummary(df$releases))
  print("across lang pullRequests")
  print(getSummary(df$pullRequests))
  print("across lang assignableUsers")
  print(getSummary(df$assignableUsers))
}