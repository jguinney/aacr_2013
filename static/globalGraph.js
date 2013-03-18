var vis2 = ""
var visual_style_2 = {
	global : {
		backgroundColor : "#E0D9FF", // "#CFCFE6",
		tooltipDelay : 100
	// default: 800 ms
	},
	nodes : {
		tooltipText : {
			passthroughMapper : {
				attrName : "tooltip"
			}
		},
		label : "",
		shape : {
			defaultValue : "CIRCLE",
			discreteMapper : {
				attrName : "year",
				entries : [ {
					attrValue : "2012",
					value : "OCTAGON"
				} ]
			}
		},
		borderWidth : 3,
		borderColor : {
			defaultValue : "#FFFFFF",
			discreteMapper : {
				attrName : "sel",
				entries : [ {
					attrValue : "T",
					value : "#9A0B0B"
				} ]
			}
		},
		size : { customMapper: { functionName: "customSizeMapper"}},
		color : {
			defaultValue : "#EEE",
			discreteMapper : {
				attrName : "level",
				entries : [ { attrValue : "0", value : "#EEE"},
				            { attrValue : "1", value : "blue"}, 
				            {attrValue : "2",value: "green" },
				            {attrValue:"3",value:"red"},
				            {attrValue:"4",value:"yellow"}]
			}
		},
		opacity : 1.0,
		labelHorizontalAnchor : "center",
		labelFontWeight : "bold",
		labelFontSize : {
			defaultValue : 14,
			discreteMapper : {
				attrName : "start",
				entries : [ {
					attrValue : "T",
					value : 18
				} ]
			}
		}

	},
	edges : {
		width : {
			continuousMapper : {
				attrName : "label",
				minValue : 1,
				maxValue : 15,
				minAttrValue : 0.24,
				maxAttrValue : 0.4
			}
		},
		color : "#706B58", // { continuousMapper: colorMapper }
		tooltipText : {
			passthroughMapper : {
				attrName : "label"
			}
		}
	}
};

updateGlobalGraph = function(){
	vis2.visualStyle(visual_style_2)
};

initializeGlobalGraph = function() {

	// id of Cytoscape Web container div
	var div_id = "cytoscapeweb2";
	

	var sizeMapper = function(data){
		var val = 50
		if(document.getElementById('startId').value == data.id){
			val = 2000
		}else{
			switch(data["level"]){
			case "0": val = 20; break;
			case "1": val = 100; break;
			case "2": val= 250; break;
			case "3": val=500; break;
			case "4": val=1000; break;
			default: val=1000;
			}
		}
		return val;
	}

	// visual style we will use
	
	var draw_options = {
		// your data goes here
		network : "",

		// show edge labels too
		edgeLabelsVisible : false,
		edgeTooltipsEnabled : true,
		nodeTooltipsEnabled : true,

		// let's try another layout
		layout: "Radial",

		visualStyle : visual_style_2,
		// hide pan zoom
		panZoomControlVisible : true
	};

	// initialization options
	var options = {
		swfPath : "/static/swf/CytoscapeWeb",
		flashInstallerPath : "/static/swf/playerProductInstall"
	};

	vis2 = new org.cytoscapeweb.Visualization("cytoscapeweb2", options);

	vis2.addListener(
					"select",
					"nodes",
					function(evt) {
						var nodes = evt.target;
						showAbstractData(nodes[0].data.id)
					});

	
	vis2.ready(function() {
		vis2["customSizeMapper"] = sizeMapper;
		vis2.select("nodes", [ document.getElementById('startId').value ])
		vis2.visualStyle(visual_style_2)
		vis2.addContextMenuItem("Get network for this node", "nodes",
			function(evt) {
				
				// Get the right-clicked node:
		
				var rootNode = evt.target;
				document.getElementById('startId').value = rootNode.data.id
				loadLocalNetwork()
			});
	});
	
	vis2.draw(draw_options);
	$.getJSON($SCRIPT_ROOT + "/getGlobalNetwork", {}, function(resp) {
		//vis2["customSizeMapper"] = sizeMapper;
		draw_options.network = resp.network
		vis2.draw(draw_options);
	});

};
