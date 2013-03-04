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
    return jsonify(title=abstract.title,lastName="Foo",abstract=abstract.abstract)

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

    
@app.route('/')
def hello():
    return render_template('cyto.html')

def _makeJSONGraph(uniqueIds, edges):
    dataSchema = {}
    dataSchema['nodes'] = [{"name": "label","type":"string"},\
                           {"name": "tooltip","type":"string"},\
                           {"name": "year","type":"string"}]
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
            "tooltip": abs.title + "\n" + abs.lastAuthor().institution } for abs in abstracts]
    return tmp

def _makeJSONNodesGlobalNetwork(uniqueIds, levels):
    abstracts = [aacr.getAbstractForId(id) for id in uniqueIds]
    def findLevel(abs):
        for i in reversed(range(len(levels))):
            if(abs.uniqueId in levels[i]):
                return (i+1)
        return 0
        
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
    dataSchema['nodes'] = [{"name": "label","type":"string"},\
                           {"name": "tooltip","type":"string"},\
                           {"name": "year","type":"string"},\
                           {"name": "level","type":"integer"}]
    dataSchema['edges'] = [{"name": "weight","type":"float"}]
    
    data = {"nodes": _makeJSONNodesGlobalNetwork(aacr.getAllIds(),levels),\
            "edges": _makeJSONEdges(edges) }
    network = {"data":data,"dataSchema":dataSchema}
    
    return network
    
    


def _makeGraphML(docIds,threshold,startIds=[],selDocIds=[]):
    strVar = "<graphml>\
      <key id=\"label\" for=\"node\" attr.name=\"label\" attr.type=\"string\"/>\
      <key id=\"label\" for=\"edge\" attr.name=\"label\" attr.type=\"float\"/>\
      <key id=\"sel\" for=\"node\" attr.name=\"sel\" attr.type=\"string\"/>\
      <key id=\"start\" for=\"node\" attr.name=\"start\" attr.type=\"string\"/>\
      <graph edgedefault=\"undirected\">"
    
    selDocIds = set(selDocIds)
    selStartIds = set(startIds)
    for docId in docIds:
	first = abs2013Obj.rx(12)[0][index_dict[docId]]
	last = abs2013Obj.rx(13)[0][index_dict[docId]]
        strVar  += "<node id=\"" + docId + "\">"
        strVar  += "<data key=\"label\">" +\
			u"%s, %s" % (last.decode('utf-8'), first.decode('utf-8')) +\
			"</data>"
        if docId in selDocIds:
            strVar += "<data key=\"sel\">T</data>"
	if docId in selStartIds:
	    strVar += "<data key=\"start\">T</data>"
        strVar += "</node>"
    for i in range(len(docIds)-1):
        idx1 = doc_index_dict[docIds[i]]
        for j in range(i+1, len(docIds)):
            idx2 = doc_index_dict[docIds[j]]
            if(docC.rx(idx1,idx2)[0] > threshold):
                strVar  += "<edge source=\"" + docIds[i] + "\" target=\"" + docIds[j] + "\"><data key=\"label\">" + '%.2f' % docC.rx(idx1,idx2)[0] + "</data></edge>"
    strVar  += "</graph></graphml>" 
    
    return strVar 


if __name__ == '__main__':
     app.run(host='0.0.0.0',debug=True)
