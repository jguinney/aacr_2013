initializeGlobalGraph = function() {

	// id of Cytoscape Web container div
	var div_id = "cytoscapeweb2";

	// NOTE: - the attributes on nodes and edges
	// - it also has directed edges, which will automatically display edge
	// arrows

	var widthMapper = {
		attrName : "label",
		minValue : 1,
		maxValue : 15,
		minAttrValue : 0.24,
		maxAttrValue : 0.4
	};
	var colorMapper = {
		attrName : "label",
		minValue : "#0000ff",
		maxValue : "#ff0000",
		minAttrValue : 0.1,
		maxAttrValue : 0.45
	};

	// visual style we will use
	var visual_style = {
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
			size : {
				defaultValue : 50,
				discreteMapper : {
					attrName : "level",
					entries : [ { attrValue : "0", value : 20},
					            { attrValue : "1", value : 100}, 
					            {attrValue : "2",value: 250 },
					            {attrValue:"3",value:500},
					            {attrValue:"4",value:1000}]
				}
			},
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
				continuousMapper : widthMapper
			},
			color : "#706B58", // { continuousMapper: colorMapper }
			tooltipText : {
				passthroughMapper : {
					attrName : "label"
				}
			}
		}
	};

	var draw_options = {
		// your data goes here
		network : "",

		// show edge labels too
		edgeLabelsVisible : false,
		edgeTooltipsEnabled : true,
		nodeTooltipsEnabled : true,

		// let's try another layout
		layout: "Radial",

		visualStyle : visual_style,
		// hide pan zoom
		panZoomControlVisible : true
	};

	// initialization options
	var options = {
		swfPath : "/static/swf/CytoscapeWeb",
		flashInstallerPath : "/static/swf/playerProductInstall"
	};

	var vis2 = new org.cytoscapeweb.Visualization("cytoscapeweb2", options);

	vis2
			.addListener(
					"select",
					"nodes",
					function(evt) {
						var nodes = evt.target;
						$
								.getJSON(
										"/getabstract/" + nodes[0].data.id,
										function(resp) {
											document
													.getElementById("lblAbstractTitle").innerHTML = resp.title
											document
													.getElementById("lblAbstractText").innerHTML = resp.abstract
											document
													.getElementById("lblAbstractId").innerHTML = nodes[0].data.id
										});
						document.getElementById("lblAbstractEmail").innerHTML = nodes[0].data.label

						// alert(nodes[0].data.label);
					});


	vis2.ready(function() {
/*
		document.getElementById("lnkGetPresentationById").onclick = function() {
			$.getJSON("/getnetworkForNode", {
				docId : document.getElementById('startId').value,
				startId : document.getElementById('startId').value,
				top : document.getElementById("top").value
			}, function(resp) {
				draw_options.network = resp.network
				vis.draw(draw_options);

			});
		};
*/
		vis2.select("nodes", [ document.getElementById('startId').value ])
	});

	vis2.draw(draw_options);
	$.getJSON("/getGlobalNetwork", {}, function(resp) {
		draw_options.network = resp.network
		vis2.draw(draw_options);
	});

};

// support pressing return
function submit(e) {
	if (e && e.keyCode == 13) {
		document.getElementById("lnkGetPresentationById").click();
	}
}
