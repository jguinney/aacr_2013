$(function() {
    
    $( "#startId" ).autocomplete({
      source: function( request, response ) {
        $.ajax({
          url: $SCRIPT_ROOT + "/getauthors",
          dataType: "json",
          data: {
            name_startsWith: request.term
          },
          success: function( data ) {
            response( data.authors);
          }
        });
      },
      minLength: 2,
      select: function( event, ui ) {
        /* log( ui.item ?
          "Selected: " + ui.item.label :
          "Nothing selected, input was " + this.value);*/
      }
    });
  });