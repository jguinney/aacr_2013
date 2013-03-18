
initializeMap = function(selId, jsonGraph) {
	nodes = jsonGraph.data.nodes
	selNode = ""
	for(i = 0; i < nodes.length; ++i){
		if(nodes[i].id == selId){
			selNode = nodes[i];
			break;
		}
	}
	var mapOptions = {
      center: new google.maps.LatLng(selNode.lat, selNode.lng),
      zoom: 8,
      mapTypeId: google.maps.MapTypeId.ROADMAP
    };
    var map = new google.maps.Map(document.getElementById("map_canvas"),mapOptions);
    for(i = 0; i < nodes.length; ++i){
    	markerOptions = {
    		position: new google.maps.LatLng(nodes[i].lat, nodes[i].lng),
    		title: nodes[i].tooltip,
    		map: map,
    		clickable: true,
    		id: nodes[i].id
    	};
    	polyLineOptions = {
    		path: [new google.maps.LatLng(nodes[i].lat, nodes[i].lng), new google.maps.LatLng(selNode.lat, selNode.lng)],
    		geodesic: true,
    		map: map
    	};
    	var marker = new google.maps.Marker(markerOptions)
    	setMarkerListener(marker)
    	new google.maps.Polyline(polyLineOptions)
    	
}

function setMarkerListener(marker){
	google.maps.event.addListener(marker, 'click', function(){
		showAbstractData(marker.id)
	})
}
}