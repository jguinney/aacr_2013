import rpy2.robjects as ro
import re
from flask import Flask
from flask import render_template, jsonify, request
from rpy2.robjects.packages import importr
from operator import itemgetter, attrgetter
import AACRStruct
base = importr('base')

app = Flask(__name__)

aacr = AACRStruct.AACRDataStruct()

@app.route("/getabstract/<presenterId>")
def getAbstract(presenterId):
    abstract = aacr.getAbstractForId(presenterId)
    authorStr = ["<a target=\"_blank\" href=\"mailto:" + author.email + "\">" +  author.lastName + ", " + author.firstName + "</a>" \
                  for author in abstract.authors]
    authorStr = "; ".join(authorStr)
    return jsonify(title=abstract.title,authors=authorStr,abstract=abstract.abstract)

@app.route("/getauthors")
def getAuthors():
    queryStr = request.args.get('name_startsWith').lower()
     
    authors = aacr.getAuthorsForSearch(queryStr)
    authorDict = [{"label": x.formattedName() + " [" + x.uniqueId + "]", "value": x.uniqueId} for x in authors]
    return jsonify(authors=authorDict)

@app.route('/getnetworkForNode')
def getNetworkForDocId():
    docId = request.args.get('docId')
    #startId = request.args.get('startId')
    top = int(request.args.get('top'))
   
    edges = aacr.getTopEdgesForAbstract(docId, top)
    docIds = [edge.toId for edge in edges]
    docIds.append(docId)
    
    return jsonify(network=_makeJSONGraph(docIds, edges))
    
@app.route('/getnetwork')
def getNetwork():
    startId = request.args.get('startId')
    threshold = float(request.args.get('threshold'))
    all_doc_ids = tuple(base.colnames(docC))
    return jsonify(network=_makeGraphML(all_doc_ids,threshold,[startId]))

@app.route('/getGlobalNetwork')
def getGlobalNetwork():
    return jsonify(network=_makeJSONGraphForAPCcluster())

@app.route("/info")
def info():
    return render_template("info.html")
    
@app.route('/')
def hello():
    return render_template('cyto.html')

def _makeJSONGraph(uniqueIds, edges):
    dataSchema = {}
    dataSchema['nodes'] = [{"name": "label","type":"string"},\
                           {"name": "tooltip","type":"string"},\
                           {"name": "year","type":"string"},\
                           {"name": "lat","type": "string"},\
                           {"name": "lng","type": "string"}]
    dataSchema['edges'] = [{"name": "weight","type":"float"}]

    data = {"nodes": _makeJSONNodes(uniqueIds),"edges": _makeJSONEdges(edges) }
    network = {"data":data,"dataSchema":dataSchema}
    
    return network

def __chunkText(text, chunkSize=20):
    return NULL

def _makeJSONEdges(edges):
    tmp  = [{"id": "edge"+str(idx), "target": edge.toId, "source": edge.fromId, "weight": "{0:.2f}".format(edge.edgeWeight)} for idx,edge in enumerate(edges)]
    return tmp

def _makeJSONNodes(uniqueIds):
    abstracts = [aacr.getAbstractForId(id) for id in uniqueIds]
    tmp = [{"id": abs.uniqueId,\
            "label": abs.firstAuthor().formattedName() + "\n" + abs.lastAuthor().formattedName() ,\
            "year": abs.year,\
            "lat": abs.lat,\
            "lng": abs.lng,\
            "tooltip": abs.title + "\n" + abs.lastAuthor().institution } for abs in abstracts]
    return tmp

def _makeJSONNodesGlobalNetwork(uniqueIds, levels):
    abstracts = [aacr.getAbstractForId(id) for id in uniqueIds]
    def findLevel(abs):
        for i in reversed(range(len(levels))):
            if(abs.uniqueId in levels[i]):
                return str(i+1)
        return "0"
        
    tmp = [{"id": abs.uniqueId,\
            "year": abs.year,\
            "tooltip": abs.firstAuthor().formattedName() + "\n" + abs.lastAuthor().formattedName() + "\n"\
            + abs.title + "\n" + abs.lastAuthor().institution,
            "level": findLevel(abs) } for abs in abstracts]
    return tmp

def _makeJSONGraphForAPCcluster():
    
    ro.r('load("data/APCcluster.rda")')
    edgeGroups = ro.r('edges')
    levels = [set(lvl) for lvl in ro.r('levels')]

    
    groupIds = tuple(base.names(edgeGroups))
    edges = []
    for i in range(len(groupIds)):
        sourceId = groupIds[i]
        for targetId in list(edgeGroups[i]):
            if sourceId != targetId:
                edges.append(aacr.getEdgeForAbstracts(sourceId, targetId))
    
    dataSchema = {}
    dataSchema['nodes'] = [{"name": "id","type":"string"},\
                           {"name": "label","type":"string"},\
                           {"name": "tooltip","type":"string"},\
                           {"name": "year","type":"string"},\
                           {"name": "level","type":"string"}]
    dataSchema['edges'] = [{"name": "weight","type":"float"}]
    
    data = {"nodes": _makeJSONNodesGlobalNetwork(aacr.getAllIds(),levels),\
            "edges": _makeJSONEdges(edges) }
    network = {"data":data,"dataSchema":dataSchema}
    
    return network
    

if __name__ == '__main__':
     app.run(host='0.0.0.0',debug=True)
