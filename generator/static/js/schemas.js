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

      $('.addProperty').click(function() {
        addProperty($(this).prop("id"));
     })

     $('input.property').change(function() {
        if ($(this).is(':checked')) {
            $(this).closest('ul').siblings('input:checkbox').prop('checked', true);
        }
     });
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
        var content = coll[c].nextElementSibling;
        if ($('#expandAll').hasClass('expanded') && !coll[c].classList.contains("active")){
              content.style.maxHeight = content.scrollHeight + "px";
              coll[c].classList.toggle("active");
        } else if (!$('#expandAll').hasClass('expanded') && coll[c].classList.contains("active")){
              content.style.maxHeight = null;
              coll[c].classList.toggle("active");
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

function addProperty(element){
    var schema = element.split(":")[1]

    var list = $('#'+ schema + ' ul li')
    var last = list.last()

    var textbox = $("<li class='propAdd'>").html("<input type='text' class='addPropertyText' onkeypress='addCheckbox(event)'>");

    textbox.insertBefore(last);

    var section = $('#' + schema).parent('div');
    var height = section.css('max-height');
    var newheight = parseInt(height.replace('px', '')) + 20;
    section.css('max-height', newheight + "px");

}

function addCheckbox(event){

    if(event.key == 'Enter'){
        event.preventDefault();
        var added = document.getElementsByClassName("addPropertyText");

        if (added.length > 1){
            console.log("There is more than one active textbox on the page");
        }

        var newProperty = added[0].value;

        var schema = $('li.propAdd').parents('div').prop('id');

        $('li.propAdd').remove();

        var list = $('#'+ schema + ' ul li')
        var last = list.last()
        var newCheckbox = $('<li>').html('<input type="checkbox" class="property" name="property" value="' + schema + ':' + newProperty + '" checked>' + newProperty);

        newCheckbox.insertBefore(last);

    }

}