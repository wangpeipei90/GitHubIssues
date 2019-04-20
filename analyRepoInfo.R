if (getwd()!="/home/peipei/workspace/GitHubIssues"){
  setwd("/home/peipei/workspace/GitHubIssues")
}
library(ggplot2)
getSummary=function(data){
  print(mean(data))
  print(min(data))
  print(max(data))
  t=c("mean"=mean(data),"max"=max(data),"min"=min(data))
  c(t,quantile(data, c(0.1,0.25,0.5,0.75,0.9,0.95,0.98,0.99)))
  # return(c(t,quantile(data, c(0.1,0.25,0.5,0.75,0.9,0.95,0.98,0.99))))
}

# data_file="/home/peipei/GitHubIssues/type_repo_issue.csv"
# data_file="/home/peipei/GitHubIssues/type_repo_issue_f.csv"
data_file="/home/peipei/GitHubIssues/type_repo_issue_ff.csv"
repoInfo=read.csv(file=data_file,head=TRUE,colClasses=c("character","character","integer"), sep=",")
repoInfo=as.data.frame(repoInfo)

t=repoInfo[which(repoInfo$type=="python"),]
nrow(t)
sum(t$files)
getSummary(t$files)

t=repoInfo[which(repoInfo$type=="java"),]
nrow(t)
sum(t$files)
getSummary(t$files)

t=repoInfo[which(repoInfo$type=="ruby"),]
nrow(t)
sum(t$files)
getSummary(t$files)

t=repoInfo[which(repoInfo$type=="php"),]
nrow(t)
sum(t$files)
getSummary(t$files)

t=repoInfo[which(repoInfo$type=="javascript"),]
nrow(t)
sum(t$files)
getSummary(t$files)

p=ggplot()+theme_bw()
p=p+geom_boxplot(data=repoInfo,aes(x=type,y=files,fill=type),alpha=0.4)
p=p+scale_fill_brewer()
p=p+coord_cartesian(ylim = c(0, 3))
p=p+labs(x="lang",y="# issue per repo",fill="Lang")
p=p+stat_summary(fun.y=mean, geom="point", shape=20, size=10, color="red", fill="red") 
# p=p+scale_x_discrete(labels=c("Intersection","Addition","Removal"))
#ggsave("abc")

name="repoInfo.csv"
lang="python"
langs=c("java","python","javascript","php","ruby")
filenames=c("repoInfo.csv","repoInfo_f.csv","repoInfo_ff.csv")
for (i in 1:length(filenames)) { 
  name=filenames[i]
  # for (j in 1:length(langs)){
  #   lang=langs[j]
  #   data_file=paste("/home/peipei/GitHubIssues",lang,name, sep = "/", collapse = NULL)
  #   repoInfo=read.csv(file=data_file,head=TRUE,colClasses=c("integer","character","character","character","integer",
  #                                                                  "character","integer","integer","integer","integer",
  #                                                                  "integer","integer","integer","integer","integer"), sep=",")
  #   message(sprintf("file name: %s lang: %s",name,lang))
  #   print(getSummary(repoInfo$files/log(repoInfo$sizeLang)))
  # }
  data_file=paste("/home/peipei/GitHubIssues","java",name, sep = "/", collapse = NULL)
  repoInfo_java=read.csv(file=data_file,head=TRUE,colClasses=c("integer","character","character","character","integer",
                                                          "character","integer","integer","integer","integer",
                                                          "integer","integer","integer","integer","integer"), sep=",")
  data_file=paste("/home/peipei/GitHubIssues","python",name, sep = "/", collapse = NULL)
  repoInfo_python=read.csv(file=data_file,head=TRUE,colClasses=c("integer","character","character","character","integer",
                                                               "character","integer","integer","integer","integer",
                                                               "integer","integer","integer","integer","integer"), sep=",")
  data_file=paste("/home/peipei/GitHubIssues","ruby",name, sep = "/", collapse = NULL)
  repoInfo_ruby=read.csv(file=data_file,head=TRUE,colClasses=c("integer","character","character","character","integer",
                                                                 "character","integer","integer","integer","integer",
                                                                 "integer","integer","integer","integer","integer"), sep=",")
  data_file=paste("/home/peipei/GitHubIssues","javascript",name, sep = "/", collapse = NULL)
  repoInfo_javascript=read.csv(file=data_file,head=TRUE,colClasses=c("integer","character","character","character","integer",
                                                               "character","integer","integer","integer","integer",
                                                               "integer","integer","integer","integer","integer"), sep=",")
  data_file=paste("/home/peipei/GitHubIssues","php",name, sep = "/", collapse = NULL)
  repoInfo_php=read.csv(file=data_file,head=TRUE,colClasses=c("integer","character","character","character","integer",
                                                                     "character","integer","integer","integer","integer",
                                                                     "integer","integer","integer","integer","integer"), sep=",")
  
  repoInfo=rbind(repoInfo_java,repoInfo_python,repoInfo_javascript,repoInfo_ruby,repoInfo_php)
  print(nrow(repoInfo))
  print(getSummary(repoInfo$files/log(repoInfo$sizeLang)))
}



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