$(document).ready(function() {

     $('#selectAll').click(function() {
        selectAll();
     });

      $('#expandAll').click(function() {
        expandAll();
     });

     $('.selectLocal').click(function() {
        selectLocal($(this).prop("id"));
     })

      $('.unselectLocal').click(function() {
        selectLocal($(this).prop("id"));
     })
});

function selectAll(){

    if(!$('#expandAll').hasClass('expanded')){
        expandAll();
    }


    $('#data-items .content input[type=checkbox]').each(function(){
        $(this).prop('checked', true)

    });
}

function expandAll(){
    var coll = document.getElementsByClassName("collapsible");

    $('#expandAll').toggleClass("expanded");

    for (var c = 0; c < coll.length; c++) {
        coll[c].classList.toggle("active");
        var content = coll[c].nextElementSibling;
        if (content.style.maxHeight){
          content.style.maxHeight = null;
        } else {
          content.style.maxHeight = content.scrollHeight + "px";
        }
    }


    if($('#expandAll').hasClass('expanded')){
      $('#expandAll').empty().text("Collapse all sections");
    }
    else{
      $('#expandAll').empty().text("Expand all sections");
    }
}

function selectLocal(element){
    var type = element.split(":")[0]
    var schema = element.split(":")[1]

    $('#'+ schema + ' input[type=checkbox]').each(function(){
        if (type == 'select'){
            $(this).prop('checked', true)
        }
        else{
            $(this).prop('checked', false)
        }
    });
}