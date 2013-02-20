import rpy2.robjects as ro
import re
from flask import Flask
from flask import render_template, jsonify, request
from rpy2.robjects.packages import importr
from operator import itemgetter, attrgetter

base = importr('base')
app = Flask(__name__)

ro.r('load("./data/aacrAbstr2013.rda")')
abs2013Obj = ro.r('abs2013')
index_dict = dict((value, idx) for idx,value in enumerate(abs2013Obj.rx(2)[0]))
ro.r('load("./data/rasDocCor.rdata")')
docC = ro.r('docC')
# indices are with respect to R indices e.g. >= 1
doc_index_dict = dict((value, idx+1) for idx,value in enumerate(tuple(base.colnames(docC))))
lastNames = tuple(abs2013Obj.rx(13)[0])
firstNames = tuple(abs2013Obj.rx(12)[0])
controlNums = tuple(abs2013Obj.rx(1)[0])

@app.route("/getabstract/<presenterId>")
def getAbstract(presenterId):
    idx = index_dict[presenterId]
    title = abs2013Obj.rx(3)[0][idx]
    abstract = abs2013Obj.rx(4)[0][idx]
    lastName = abs2013Obj.rx(13)[0][idx]
    
    return jsonify(title=title,lastName=lastName,abstract=abstract)

@app.route("/getauthors")
def getAuthors():
    queryStr = request.args.get('name_startsWith')
    p = re.compile(queryStr +"*",re.IGNORECASE)
    matches = [[lastNames[i] + ', ' + firstNames[i],controlNums[i]]  for i,val in enumerate(lastNames) if p.match(val) != None]
    
    match = sorted(matches, key=itemgetter(0))
    match_dict = [{"label":x[0],"value":x[1]} for x in match]
    return jsonify(authors=match_dict)

@app.route('/getnetworkForNode')
def getNetworkForDocId():
    docId = request.args.get('docId')
    startId = request.args.get('startId')
    threshold = float(request.args.get('threshold'))
    v = tuple(docC.rx(doc_index_dict[docId],True))
    all_doc_ids = base.colnames(docC)
    docIds = [all_doc_ids[i] for i,val in enumerate(v) if val > threshold]
    docIds.append(docId)
    return jsonify(network=_makeGraphML(docIds,threshold,[startId],[docId]))
    
@app.route('/getnetwork')
def getNetwork():
    startId = request.args.get('startId')
    threshold = float(request.args.get('threshold'))
    all_doc_ids = tuple(base.colnames(docC))
    return jsonify(network=_makeGraphML(all_doc_ids,threshold,[startId]))
    
@app.route('/')
def hello():
    return render_template('cyto.html')

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

    
def _buildAuthorDS():
    DS = []
    
    
if __name__ == '__main__':
     app.run(host='0.0.0.0',debug=True)
