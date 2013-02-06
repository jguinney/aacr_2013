$(function() {
    
    $( "#authors" ).autocomplete({
      source: function( request, response ) {
        $.ajax({
          url: "/getauthors",
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
      },
      open: function() {
        $( this ).removeClass( "ui-corner-all" ).addClass( "ui-corner-top" );
      },
      close: function() {
        $( this ).removeClass( "ui-corner-top" ).addClass( "ui-corner-all" );
      }
    });
  });