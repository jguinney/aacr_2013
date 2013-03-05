## Exploratory R Code
# Alex Pico

load("/git/aacr2013/data/aacrAbstr2013.rda")
dim(abs2013)
sapply(abs2013,class)
head(abs2013,1)

load("/git/aacr2013/data/aacrMatrix.rdata")
dim(S)
head(S,1)

## determine best edge thickness mapping
max(sapply(S,max, na.rm=T))
min(sapply(S,min, na.rm=T))
boxplot(S)  

## transform matrix to graph
#install.packages("igraph")
#library(igraph)
#g2 <- graph.adjacency(S, weighted=TRUE, mode="upper", diag=F, add.colnames=NULL, add.rownames=NULL)
#fail

#source("http://www.bioconductor.org/biocLite.R")
#biocLite("Ruuid")
#biocLite("graph")Replace broken link
#biocLite("Rgraphviz")
#library(Rgraphviz)
#g3<-new("graphAM", adjMat=S, edgemode="undirected")
#fail

g6<-data.frame(mrow=c(col(S)),   
           mcol=c(row(S)), 
           m.f.res= mapply(function(r,c) S[r,c], row(S), col(S)  ) )
#success

## Now, simplify and export
names(g6)<-c("ab1","ab2","weight")
g7<-g6[g6$ab1<g6$ab2,] #top half of matrix
nodes<-as.vector(rownames(S))
ab1<-sapply(g7$ab1, function(x) nodes[x])
ab2<-sapply(g7$ab2, function(x) nodes[x])
g7$ab1<-ab1
g7$ab2<-ab2
g8<-g7[g7$weight>0.24,]
write.table(g8,file="/git/aacr2013/data/graph_new_0.24.csv",sep=",",row.names=F, quote=F)

## Export other data.frame for node attributes
# Doesn't work with new matrix node names, i.e., with ".2013" and ".2012"
#write.table(abs2013,file="/git/aacr2013/data/graph_node_attrs.tab",sep="\t",row.names=F, quote=F)
