import rpy2.robjects as ro
from rpy2.robjects.packages import importr
import re
from operator import itemgetter, attrgetter
base = importr('base')

class AACREdge:
    def __init__(self, fromId, toId, edgeWeight):
        self.fromId = fromId
        self.toId = toId
        self.edgeWeight = edgeWeight

class AACRAuthor:
    def __init__(self, uniqueId, firstName, lastName, email, institution, order, abstract):
        self.uniqueId = uniqueId
        self.firstName = firstName
        self.lastName = lastName
        self.email = email
        self.institution = institution
        self.order = order
        self.abstract = abstract
        
    def formattedName(self):
        return self.lastName + ", " + self.firstName
    
class AACRAbstract:
    def __init__(self, uniqueId, presentationId, controlId, title, year,abstract):
        self.uniqueId = uniqueId
        self.presentationId = presentationId
        self.title = title
        self.year = year
        self.abstract = abstract
        self.authors = []
        
    def firstAuthor(self):
        return self.authors[0]
    
    def lastAuthor(self):
        return self.authors[-1]

class AACRDataStruct:
    def __init__(self, similarityFile="data/aacrSimilarityMatrix_Cosine.rdata", metadataFile="data/aacr.rda"):
        
        # metadata load
        ro.r('load("' + metadataFile +'")')
        abstractTbl = ro.r('abstractTbl')
        authorTbl = ro.r('authorTbl')
        
        uniqueId = abstractTbl.rx('id')[0]
        presentationId = abstractTbl.rx('PRESENTATIONNUMBER')[0]
        controlId = abstractTbl.rx('ControlNumber')[0]
        abstract = abstractTbl.rx('Abstract')[0]
        year = abstractTbl.rx('year')[0]
        title = abstractTbl.rx('ABSTRACT.TITLE')[0]
                
        metaDict = {}
        for i in range(len(uniqueId)):
            metaDict[uniqueId[i]] = AACRAbstract(uniqueId[i],presentationId[i], controlId[i],title[i],year[i],abstract[i])
        self.metaDict = metaDict
            
        ids = authorTbl.rx('id')[0]
        authorFirstName = authorTbl.rx('AUTHORFIRSTNAME')[0]
        authorLastName = authorTbl.rx('AUTHORLASTNAME')[0]
        contactEmail = authorTbl.rx('CONTACTEMAIL')[0]
        institution = authorTbl.rx('INSTITUTIONNAME')[0]
        order = authorTbl.rx('AUTHORORDER')[0]
        
        for i in range(len(ids)):
            id = ids[i]
            abstract = metaDict[id]
            author = AACRAuthor(id, authorFirstName[i],\
                       authorLastName[i],\
                       contactEmail[i],\
                       institution[i],\
                       order[i],
                       abstract)
            abstract.authors.append(author)
            
        authorPrefixDict = {}    
        for abstract in metaDict.values():
            for author in abstract.authors:
                prefix = author.lastName[0:2].lower()
                authorList = []
                if authorPrefixDict.has_key(prefix):
                    authorList = authorPrefixDict[prefix]
                authorList.append(author)
                authorPrefixDict[prefix] = authorList
         
        self.authorPrefixDict = authorPrefixDict    
        
        self.__makeEdgeDict(similarityFile)

    def __makeEdgeDict(self, similarityFile):
        #similarity load
        ro.r('load("' + similarityFile +'")')
        S = ro.r('S')
        ids = tuple(base.colnames(S))
        edgeDict2List = {}
        edgeDict2Dict = {}
        for i in range(len(ids)):
            row = list(ro.r('S[' + str(i+1) + ',]'))
            obs = [AACREdge(ids[i], ids[idx], value) for idx, value in enumerate(row)]
            obs.sort(key=lambda obj: obj.edgeWeight, reverse=True)
            edgeDict2List[ids[i]] = obs
            edgeDict2Dict[ids[i]] = { edge.toId: edge for edge in obs}
            
        self.edgesDict2List = edgeDict2List
        self.edgesDict2Dict = edgeDict2Dict    
        
    def getAllIds(self):
        return self.metaDict.keys()
       
    def getEdgeForAbstracts(self, id1, id2):
        return self.edgesDict2Dict[id1][id2]
    
    def getTopEdgesForAbstract(self, id, top=10):
        return self.edgesDict2List[id][0:top]

    def getAbstractForId(self, id):
        return self.metaDict[id]
    
    def getAuthorsForSearch(self, searchPrefix):
        if(len(searchPrefix) < 2 or not self.authorPrefixDict.has_key(searchPrefix[0:2].lower())):
            return []
        else:
            authors = list(self.authorPrefixDict[searchPrefix[0:2].lower()])
            if len(searchPrefix) > 2:
                p = re.compile("^" + searchPrefix.lower(),re.IGNORECASE)
                authors = [author for author in authors if p.match(author.lastName) != None]
            authors = sorted(authors, key=attrgetter('lastName','firstName'))
            return authors