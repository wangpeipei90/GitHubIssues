if (getwd()!="/home/peipei/workspace/GitHubIssues"){
  setwd("/home/peipei/workspace/GitHubIssues")
}

data_file="/home/peipei/GitHubIssues/list_filteredIssueInfo.csv"
issueInfo=read.csv(file=data_file,head=TRUE,colClasses=c("character","integer","integer","integer","double","character","character"), sep=",")
issueInfo=as.data.frame(issueInfo)
sprintf("issue total: %s",nrow(issueInfo))

getSummary=function(data){
  print(mean(data))
  print(min(data))
  print(max(data))
  t=c("mean"=mean(data),"max"=max(data),"min"=min(data))
  c(t,quantile(data, c(0.1,0.25,0.5,0.75,0.9,0.95,0.98,0.99)))
  # return(c(t,quantile(data, c(0.1,0.25,0.5,0.75,0.9,0.95,0.98,0.99))))
}

table(issueInfo$labels)
# 0    1    2    3    4    5    6    7    8    9   10   11   13 
# 1261  662  347  182   64   24   10    2    7    3    1    1    1
getSummary(issueInfo$labels)
# mean        maxmin        10%        25%        50%        75%        90%        95%        98%        99% 
# 0.9625731 13.0000000  0.0000000  0.0000000  0.0000000  1.0000000  2.0000000  3.0000000  3.0000000  4.0000000  5.0000000 

table(issueInfo$comments)
getSummary(issueInfo$comments)
# mean        max        min        10%        25%        50%        75%        90%        95%        98%        99% 
# 3.848343 139.000000   0.000000   0.000000   1.000000   2.000000   5.000000   9.000000  13.000000  19.000000  28.080000

table(issueInfo$participants)
# 0   1   2   3   4   5   6   7   8   9  10  11  12  13  14  16  17  22  26  28  41  60 130 
# 1 207 986 677 342 162  76  41  27  18   7   5   3   2   2   2   1   1   1   1   1   1   1
getSummary(issueInfo$participants)
# mean        max        min        10%        25%        50%        75%        90%        95%        98%        99% 
# 3.150097 130.000000   0.000000   2.000000   2.000000   3.000000   4.000000   5.000000   6.000000   8.000000  10.000000

getSummary(issueInfo$duration)
# mean          max          min          10%          25%          50%          75%          90%          95%          98%          99%
# 9.293646e+01 4.477998e+03 2.314815e-05 4.306481e-02 5.428356e-01 4.057488e+00 3.421682e+01 2.180714e+02 5.108295e+02 1.015344e+03 1.717948e+03


length(which(issueInfo$duration>1)) #1691
length(which(issueInfo$duration<=1)) #874

length(which(issueInfo$participants>1)) #2357
length(which(issueInfo$participants<=1)) #208
length(which(issueInfo$participants>0)) #2564
length(which(issueInfo$participants<=0)) #1

length(which(issueInfo$comments>1)) #1518
length(which(issueInfo$comments<=1)) #1047
length(which(issueInfo$comments>0)) #2016
length(which(issueInfo$comments<=0)) #549

length(which(issueInfo$labels>0)) #1304
length(which(issueInfo$labels<=0)) #1261

length(which(issueInfo$labels>0 & issueInfo$duration>1 & issueInfo$participants>1 & issueInfo$comments>1)) #675
length(which(issueInfo$labels>0 & issueInfo$duration>1 & issueInfo$participants>0 & issueInfo$comments>0)) #827
length(which(issueInfo$labels>0 & issueInfo$duration>1)) #944
length(which(issueInfo$duration>1 & issueInfo$participants>0 & issueInfo$comments>0)) #1443

subIssueInfo=issueInfo[which(issueInfo$labels>0),]

table(subIssueInfo$comments)
getSummary(subIssueInfo$comments)
# mean        max        min        10%        25%        50%        75%        90%        95%        98%        99% 
# 4.532209 122.000000   0.000000   0.000000   1.000000   3.000000   5.250000  10.000000  15.000000  23.940000  35.940000

table(subIssueInfo$participants)
getSummary(subIssueInfo$participants)
# mean      max      min      10%      25%      50%      75%      90%      95%      98%      99% 
# 3.38727 60.00000  1.00000  2.00000  2.00000  3.00000  4.00000  5.00000  7.00000  9.00000 11.00000 

getSummary(subIssueInfo$duration)
# mean          max          min          10%          25%          50%          75%          90%          95%          98%          99% 
# 1.422514e+02 4.477998e+03 2.314815e-05 8.561921e-02 8.622975e-01 7.341944e+00 7.420451e+01 4.116162e+02 8.286257e+02 1.641745e+03 2.025189e+03 

length(which(subIssueInfo$duration>1)) #944
length(which(subIssueInfo$duration<=1)) #360

length(which(subIssueInfo$participants>1)) #2357
length(which(subIssueInfo$participants<=1)) #99

length(which(subIssueInfo$comments>1)) #847
length(which(subIssueInfo$comments<=1)) #457

length(which(subIssueInfo$duration>1 & subIssueInfo$participants>0 & subIssueInfo$comments>0)) #1443



name="issueInfo.csv"
lang="python"
langs=c("java","python","javascript","php","ruby")
filenames=c("issueInfo.csv","issueInfo_f.csv","issueInfo_ff.csv")
for (i in 1:length(filenames)) { 
  name=filenames[i]
  for (j in 1:length(langs)){
    lang=langs[j]
    data_file=paste("/home/peipei/GitHubIssues",lang,name, sep = "/", collapse = NULL)
    issueInfo=read.csv(file=data_file,head=TRUE,colClasses=c("character","integer","integer","integer","double","character","character","character","logical","logical"), sep=",")
    message(sprintf("file name: %s lang: %s",name,lang))
    print(nrow(issueInfo))
    message(sprintf("report:%d pr:%d merged:%d not merged:%d",sum(!issueInfo$is_pr),sum(issueInfo$is_pr),sum(issueInfo$is_pr & issueInfo$merged),sum(issueInfo$is_pr & !issueInfo$merged)))
  }
}