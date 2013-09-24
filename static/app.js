$(function() {
    $("#search").autocomplete({
        source: function(request, response) {
            $.ajax({
                url: "http://en.wikipedia.org/w/api.php",
                dataType: "jsonp",
                data: {
                    'action': "opensearch",
                    'format': "json",
                    'search': request.term
                },
                success: function(data) {
                    response(data[1]);
                }
            });
        }, 
        select: function(event,ui) {
            crowl(ui.item.value)
        }
    });
});


function createStepsList(steps){
   list = ""
   $.each(steps,function(i,d){
      list+="<a href="+d.link+">"+d.title+"</a><br/>"
   })
   return list
}

function formatTitle(title){
   return title
}

function crowl(title){
   $("#crowl-steps").html("") 
   $("#crowl-result").html("Waiting...")
   $.ajax({
      url: "crowl",
      data: {title:formatTitle(title)}, 
      success: function(data){
         console.log(data)
         $("#crowl-steps").html(createStepsList(data.steps)) 
         $("#crowl-result").html(data.result)
      }, 
      error: function(data){
         $("#crowl-steps").html("") 
         $("#crowl-result").html("ERROR")
      }, 
      timeout: 30000
   })
}

function searchKeyPress(e){
// look for window.event in case event isn't passed in
   if (typeof e == 'undefined' && window.event) { e = window.event; }
      if (e.keyCode == 13)
      {
         value = $('#search').val();
         $( "#search" ).autocomplete( "close" );
         crowl(value)
      }
 }
