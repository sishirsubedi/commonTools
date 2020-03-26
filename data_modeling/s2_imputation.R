library("mice")

df <- read.csv("d2_before_impute_final_datamat.csv")

df_sub <- subset(df, select=-c(MRN,PTH))

df_temp <- mice(df_sub,m=1,maxit=1,meth='pmm',seed=500)

summary(df_temp)

completedData <- complete(df_temp,1)

completedData$MRN <- df$MRN
completedData$PTH <- df$PTH

write.csv(completedData,"d3_after_impute_final_datamat.csv",row.names=FALSE)
