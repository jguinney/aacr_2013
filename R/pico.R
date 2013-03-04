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

## transform matrix to graph
#install.packages("igraph")
#library(igraph)
#g2 <- graph.adjacency(docC, weighted=TRUE, mode="upper", diag=F, add.colnames=NULL, add.rownames=NULL)
#fail

#source("http://www.bioconductor.org/biocLite.R")
#biocLite("Ruuid")
#biocLite("graph")Replace broken link
#biocLite("Rgraphviz")
#library(Rgraphviz)
#g3<-new("graphAM", adjMat=docC, edgemode="undirected")
#fail

g6<-data.frame(mrow=c(col(docC)),   
           mcol=c(row(docC)), 
           m.f.res= mapply(function(r,c) docC[r,c], row(docC), col(docC)  ) )
#success

## Now, simplify and export
names(g6)<-c("ab1","ab2","weight")
g7<-g6[g6$ab1<g6$ab2,] #top half of matrix
ab1<-sapply(g7$ab1, function(x) r[x])
g8<-g7[g7$weight>0.24,]
write.table(g8,file="/git/aacr2013/data/graph_0.24.csv",sep=",",row.names=F, quote=F)
