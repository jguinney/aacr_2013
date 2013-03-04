
library(tm)
library(slam)
library(wordcloud)

load("data/aacr.rda")

strip.markup <- function(x){
  gsub("</?[A-Za-z]+>|<[A-Za-z]+\\s?/>"," ", x)
}

concatenate_and_split_hyphens <- function(x){
  gsub("\\s(\\w+)-(\\w+)\\s"," \\1\\2 \\1 \\2 ",x)
}

removeAloneNumbers <- function(x){
  gsub("\\s\\d+\\s","", x)
}

abstract.stop.words <- c("cell","cancer","tumor","express","studi","activ","result",
                "line","increas","gene","protein","level","signific",
                "compar","associ","develop","analysi","use","observ",
                "demonstr","found","includ","determin","suggest","conclusion",
                "background","effect","identifi","data","potenti")

doc.titles <- sapply(abstractTbl$ABSTRACT.TITLE, strip.markup,USE.NAMES = FALSE)
docids <- abstractTbl$id
corpus <- Corpus(VectorSource(abstractTbl$Abstract))
corpus <- tm_map(corpus, strip.markup)
corpus <- tm_map(corpus, stripWhitespace)
corpus <- tm_map(corpus, concatenate_and_split_hyphens)
corpus <- tm_map(corpus, removePunctuation)
corpus <- tm_map(corpus, tolower)
corpus <- tm_map(corpus, removeWords, stopwords("english"))
corpus <- tm_map(corpus, removeAloneNumbers)
corpus <- tm_map(corpus, stemDocument)
corpus <- tm_map(corpus, removeWords, abstract.stop.words)

dtm <- DocumentTermMatrix(corpus,
                          control = list(weighting = function(x) weightTfIdf(x, normalize = TRUE)))
word.freq <- as.numeric(as.array(slam::rollup(dtm, 1, FUN=function(x) { sum(x > 0)})) )
dtm.sub <- dtm[, word.freq > 2]
D <- as.matrix(dissimilarity(dtm.sub, method = "cosine"))
S <- 1 - D
diag(S) <- 0
colnames(S) <- docids
rownames(S) <- docids
save(S, file="data/aacrSimilarityMatrix_Cosine.rdata")


######################
# affinity propagation clustering
library(apcluster)
ids = colnames(S)
load(file="data/aacrSimilarityMatrix_Cosine.rdata")
cluster1 = apcluster(S)
cluster2 = apcluster(S[ids %in% names(cluster1@exemplars), ids %in% names(cluster1@exemplars)])
cluster3 = apcluster(S[ids %in% names(cluster2@exemplars), ids %in% names(cluster2@exemplars)])
cluster4 = apcluster(S[ids %in% names(cluster3@exemplars), ids %in% names(cluster3@exemplars)])
clusters = c(cluster1, cluster2, cluster3, cluster4)

edges = list()
levels = list()
for(j in 1:4){
  cluster = clusters[[j]]
  exemplars <- names(cluster@exemplars)
  for(i in 1:length(exemplars)){
    ex <- exemplars[i]
    edges[[ex]] <- c(edges[[ex]], names(cluster@clusters[[i]]))
  }
  levels[[j]] <- exemplars
}
save(edges, levels, file="data/APCcluster.rda")


#################################################
### older analysis
                 
# only keep words that show up more than 2 times
word.freq <- as.numeric(as.array(slam::rollup(dtm, 1, FUN=function(x) { sum(x > 0)})) )
idxs <- order(word.freq,decreasing=T)
tmp <- cbind(word.freq[idxs], colnames(dtm)[idxs])
dtm <- dtm[, word.freq > 2]
M <- as.matrix(dtm)

# global inverse weight: frequenctly used terms across documents will be downweighted


# pick up ras related docs
#ras.term.idxs <- which(colnames(M) %in% c("ras","kras","nras","hras","egfr","raf","braf","erk","mek"))
#ras.mask <- rowSums(M[, ras.term.idxs]) > 0
#ras_dtm <- M[ras.mask,]
#ras_dtm <- ras_dtm[, colSums(ras_dtm) > 0]
#ras_titles <- doc.titles[ras.mask]
ras_dtm <- M

# local log weighting and global inverse weight
global.inv.weight <- apply(ras_dtm, 2, function(x){
  log(length(x) / (1+sum(x > 0)))
})

wDTM <- log(ras_dtm+1) * global.inv.weight


wordC <- cor(wDTM, method="spearman")
docC <- cor(t(wDTM), method="spearman")
docE <- as.matrix(dist(wDTM,"euclidean"))

wordC[!upper.tri(wordC)] <- 0
docC[!upper.tri(docC)] <- 0
diag(docC) <- 
colnames(docC) <- docNums[ras.mask]
rownames(docC) <- docNums[ras.mask]
save(docC, file="../aacr/data/rasDocCor.rdata")

write.graphML(docC, abs2013$PRESENTATIONNUMBER[ras.mask], abs2013$PRESENTERCONTACTEMAIL[ras.mask], 
              file="rasDocGraphML.xml",threshold=.25)

words <- colnames(wDTM)
pc <- svd(t(wDTM)-rowMeans(t(wDTM)))
plot(pc$d^2 / sum(pc$d^2),main="Spectral decay",ylab="% variance")
idxs <- order(abs(pc$u[,1]),decreasing=TRUE)
plot(pc$u[idxs,1],pch=16,cex=.5)
text(1:10 + 50, pc$u[idxs[1:10],1],labels=words[idxs][1:10],cex=.5,adj=c(0,.5))

plot.pc <- function(pc.num=1,sz=50){
  
  idxs <- order(abs(pc$u[,pc.num]),decreasing=TRUE)
  pdf(paste("plots/RAS_aacr_2013_pc",pc.num,".pdf",sep=""))
  wordcloud(words[idxs[1:sz]], abs(pc$u[idxs[1:sz],pc.num]), random.order=FALSE); 
  dev.off()
}
# word frequency
freq <- as.numeric(as.array(slam::rollup(dtm, 1, FUN=function(x) { sum(x > 1)})) )
hist(log(freq))

ras_words <- c("ras","hras","kras","nras")

assocs <- findAssocs(dtm, "kras",0.85)

write.graphML <- function(M, ids, labels, file, threshold=.22){
  zz <- file(file, "w") 
  cat("<graphml>",file = zz,sep="")
  cat("<key id=\"label\" for=\"all\" attr.name=\"label\" attr.type=\"string\"/>",file=zz,sep="")
  cat("<key id=\"weight\" for=\"node\" attr.name=\"weight\" attr.type=\"double\"/>",file=zz,sep="")
  cat("<graph edgedefault=\"undirected\">",file=zz,sep="")
  N <- ncol(M)
  for(i in 1:N){
    cat("<node id=\"",ids[i],"\">", "<data key=\"label\">",labels[i],"</data></node>\n",file=zz,sep="")
  }
  for(i in 1:(N-1)){
    for(j in (i+1):N){
      if(M[i,j] > threshold){
        cat("<edge source=\"",ids[i],"\" target=\"",ids[j],"\"><data key=\"label\">",format(M[i,j],digits=2),"</data></edge>\n",file=zz,sep="")
      }
    }
  }
  cat("</graph></graphml>",file=zz,sep="")
  close(zz)
}
  