## Exploratory R Code
# Alex Pico

load("/git/aacr2013/data/aacrAbstr2013.rda")
dim(abs2013)
sapply(abs2013,class)
head(abs2013,1)

load("/git/aacr2013/data/rasDocCor.rdata")
dim(docC)
head(docC,1)

## determine best edge thickness mapping
max(sapply(docC,max, na.rm=T))
min(sapply(docC,min, na.rm=T))
boxplot(docC)  