initializeLocalGraph = function() {

	// id of Cytoscape Web container div
	var div_id = "cytoscapeweb";

	// NOTE: - the attributes on nodes and edges
	// - it also has directed edges, which will automatically display edge
	// arrows
	var xml = '\
                <graphml>\
                  <key id="label" for="all" attr.name="label" attr.type="string"/>\
                  <key id="sel" for="node" attr.name="sel" attr.type="string"/>\
		  		 <key id="start" for="node" attr.name="start" attr.type="string"/>\
                  <key id="weight" for="node" attr.name="weight" attr.type="double"/>\
                  <graph edgedefault="directed">\
                    <node id="1">\
                        <data key="label">AACR</data>\
                        <data key="weight">2.0</data>\
                        <data key="start">T</data>\
                    </node>\
                    <node id="2">\
                        <data key="label">RAS</data>\
                        <data key="weight">1.5</data>\
                        <data key="start">A</data>\
                    </node>\
                    <node id="3">\
                        <data key="label">2013</data>\
                        <data key="weight">1.0</data>\
                        <data key="start">B</data>\
                    </node>\
                    <edge source="1" target="2">\
                        <data key="label"></data>\
                    </edge>\
                    <edge source="1" target="3">\
                        <data key="label"></data>\
                    </edge>\
                  </graph>\
                </graphml>\
                ';

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
			label : {
				passthroughMapper : {
					attrName : "label"
				}
			},
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
					attrName : "sel",
					entries : [ {
						attrValue : "T",
						value : 75
					} ]
				}
			},
			color : {
				defaultValue : "#EEE",
				discreteMapper : {
					attrName : "start",
					entries : [ {
						attrValue : "B",
						value : "#0B94B1"
					}, {
						attrValue : "T",
						value : "#CA2B2B"
					}, {
						attrValue : "A",
						value : "#dddd00"
					} ]
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
		network : xml,

		// show edge labels too
		edgeLabelsVisible : false,
		edgeTooltipsEnabled : true,
		nodeTooltipsEnabled : true,

		// let's try another layout
		layout : "Radial",

		visualStyle : visual_style,
		// hide pan zoom
		panZoomControlVisible : true
	};

	// initialization options
	var options = {
		swfPath : "/static/swf/CytoscapeWeb",
		flashInstallerPath : "/static/swf/playerProductInstall"
	};

	var vis = new org.cytoscapeweb.Visualization("cytoscapeweb", options);

	vis
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

	vis.ready(function() {

		document.getElementById("lnkLoadNetwork").onclick = function() {
			$.getJSON("/getnetwork", {
				docId : document.getElementById('startId').value,
				startId : document.getElementById('startId').value,
				top : document.getElementById("top").value
			}, function(resp) {
				draw_options.network = resp.network

				vis.draw(draw_options);
			});
		};
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
		vis.addContextMenuItem("Get network for this author", "nodes",
				function(evt) {
					// Get the right-clicked node:
					var rootNode = evt.target;
					$.getJSON("/getnetworkForNode", {
						startId : document.getElementById('startId').value,
						docId : rootNode.data.id,
						threshold : document.getElementById("threshold").value
					}, function(resp) {
						draw_options.network = resp.network
						vis.draw(draw_options);

					});

				});
		vis.select("nodes", [ document.getElementById('startId').value ])
	});

	vis.draw(draw_options);

};

// support pressing return
function submit(e) {
	if (e && e.keyCode == 13) {
		document.getElementById("lnkGetPresentationById").click();
	}
}
