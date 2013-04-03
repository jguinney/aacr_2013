
function showAbstractData(abstractId){

	$.getJSON(
			$SCRIPT_ROOT + "/getabstract/" + abstractId,
			function(resp) {
				document.getElementById("lblAbstractTitle").innerHTML = resp.title
				document.getElementById("lblAbstractText").innerHTML = resp.abstract
				document.getElementById("lblAbstractId").innerHTML = abstractId
				document.getElementById("lblAbstractAuthors").innerHTML = resp.authors
				document.getElementById("lblSurveyText").innerHTML = resp.survey
			});
}

