
library(gdata)
tbl2013 <- read.table("data/raw/AACRAbstracts2013.txt",sep="\t",as.is=TRUE,quote="",comment.char="",header=TRUE)
tbl2012 <- read.table("data/raw/AACRAbstracts2012.txt",sep="\t",as.is=TRUE,quote="",comment.char="",header=TRUE)
revised.2013 <- read.xls("data/raw/Revised Pres Numbers 2-12-13.xlsx",as.is=TRUE)

#tbl2012 <- read.xls("data/raw/Abstracts 2012.xlsx",as.is=TRUE)
#load("data/raw/tbl_2013_2013.rda")

idxs <- match(tbl2013$ControlNumber, revised.2013$ControlNumber)
tbl2013.m <- tbl2013[!is.na(idxs),]
revised2013.m <- revised.2013[na.omit(idxs),]
tbl2013.m$status <- revised2013.m$PROGRAMSTATUSNAME
tbl2013.m$PRESENTATIONNUMBER <- revised2013.m$PRESENTATIONNUMBER

tbl2013.final <- tbl2013.m[tbl2013.m$status != "Withdrawn",]

author2013 <- read.xls("data/raw/Author Data 2013_REV_AuthOrder_2-21-13.xlsx",as.is=TRUE)
author2012 <- read.xls("data/raw/Author Data 2012_REV_AuthOrder_2-21-13.xlsx",as.is=TRUE)

find.ras <- function(x){
  grepl("\\sras\\s|\\sraf\\s|kras|nras|hras|k-ras|n-ras|h-ras|egfr|braf|b-raf",x,ignore.case=TRUE)
}

mask.2013 <- find.ras(tbl2013.final$Abstract) | find.ras(tbl2013.final$ABSTRACT.TITLE) 
mask.2012 <- find.ras(tbl2012$Abstract) | find.ras(tbl2012$ABSTRACT.TITLE)

tbl2013.sub <- tbl2013.final[mask.2013,]
tbl2012.sub <- tbl2012[mask.2012,]

abstractTbl <- rbind(tbl2012.sub[,c(-16)], tbl2013.sub[,c(-16,-17)])
abstractTbl$year <- c(rep("2012", nrow(tbl2012.sub)),rep("2013",nrow(tbl2013.sub)))

cntrlIds_2012 <- intersect(as.character(author2012$CONTROLNUMBER),tbl2012.sub$ControlNumber)
cntrlIds_2013 <- intersect(as.character(author2013$CONTROLNUMBER),tbl2013.sub$ControlNumber)

author2013.sub <- author2013[as.character(author2013$CONTROLNUMBER) %in% cntrlIds_2013,]
author2012.sub <- author2012[as.character(author2012$CONTROLNUMBER) %in% cntrlIds_2012,]
tbl2013.sub <- tbl2013.sub[tbl2013.sub$ControlNumber %in% cntrlIds_2013,]
tbl2012.sub <- tbl2012.sub[tbl2012.sub$ControlNumber %in% cntrlIds_2012,]

authorTbl <- rbind(author2013.sub, author2012.sub)
authorTbl$year <- c(rep("2013",nrow(author2013.sub)), c(rep("2012",nrow(author2012.sub))))
authorTbl$id <- paste(authorTbl$CONTROLNUMBER,authorTbl$year,sep=".")
  
abstractTbl <- rbind(tbl2013.sub[,c(-16,-17)],tbl2012.sub[,c(-16,-17)])
abstractTbl$year <- c(rep("2013", nrow(tbl2013.sub)),rep("2012",nrow(tbl2012.sub)))
abstractTbl$id <- paste(abstractTbl$ControlNumber,abstractTbl$year,sep=".")

save(abstractTbl, authorTbl, file="data/aacr.rda")

