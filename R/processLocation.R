library(gdata)
library(RCurl)
library(RJSONIO)
source("../h3/analysis/JGLibrary.R")
tbl <- read.xls("data/raw/AuthorData2012_Addresses.xlsx",as.is=TRUE)
tbl$AUTHORORDER[is.na(tbl$AUTHORORDER)] <- 999
firstAuthors <- tbl[tbl$PRESENTATIONNUMBER != "" & tbl$AUTHORORDER==1,]
firstAuthors$AUTHORCOUNTRYNAME[grepl("Korea",firstAuthors$AUTHORCOUNTRYNAME)] <- "Korea"


queryStr <- apply(firstAuthors,1,function(x){ gsub(" ","+",paste(x[13],x[14],x[15],sep=","))})
location = t(sapply(queryStr, function(qs){
  R <- fromJSON(getURL(paste("http://maps.googleapis.com/maps/api/geocode/json?address=",qs,"&sensor=false",sep="")))
  Sys.sleep(.5)
  if(length(R$results) > 0){
    return (R$results[[1]]$geometry$location)
  }else{
    return(c(NA,NA))
  }  
}))
locationTbl_2012 <- cbind(firstAuthors, location)
#locationTbl_2013 <- cbind(firstAuthors, location)

locationTbl <- rbind(locationTbl_2012, locationTbl_2013)