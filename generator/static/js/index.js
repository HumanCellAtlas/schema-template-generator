$(function() {
    triggerPolling();
    renderDates();
    // $('#submissions').DataTable({searching: false, paging: false});
});

function triggerPolling(){
    $('#submissions > tbody > tr').each(function(){
        var row = $(this);
        pollRow(row);
    });
}

function pollRow(row){
    var POLL_INTERVAL = 3000; //in milliseconds

    var rowData = row.data();
    var url = rowData.url;
    var date = rowData.date;

    var submissionId = url.split("/").pop(); // for logging only
    $.ajax({
        url: url,
        headers: {"If-Modified-Since":date},
        type: 'GET',
        dataType: 'json',
        success: function(data, textStatus, jqXHR){
            if(data){
                var lastModifiedDate = jqXHR.getResponseHeader('Last-Modified');
                console.log("Got response, submissionId '" + submissionId + " was last modified at " + lastModifiedDate);
                renderResponse(url, data);
                row.data('date', lastModifiedDate);
            }
        },
        complete: function(data){
            setTimeout(function(){
                pollRow(row);
            }, POLL_INTERVAL)
        }
    });
}

function renderResponse(url, data) {
    var STATUS_LABEL = {
        'Valid': 'label-success',
        'Validating': 'label-info',
        'Invalid': 'label-danger',
        'Submitted': 'label-default',
        'Complete': 'label-default'
    }

    var DEFAULT_STATUS_LABEL = 'label-warning';

    var row = $('#submissions').find('> tbody > tr[data-url="' + url + '"]');

    var statusCol = row.find('.submission-state')
    statusCol.text(data.submissionState);
    statusCol.attr('class', 'submission-state label ' + (STATUS_LABEL[data.submissionState] || DEFAULT_STATUS_LABEL) + ' label-lg');

    var date = moment(data.updateDate).toDate(); // use moment to correctly parse date even in safari
    var formattedDate = date.toLocaleTimeString() + " " + date.toLocaleDateString();

    row.find('.update-date').text(formattedDate);

    var form = row.find('.submission-form');
    if (data['_links']['submit']){
        form.html(createSubmissionForm(data['_links']['submit']['href']));
    } else {
        form.html(createSubmissionForm());
    }

    console.log("Rendered updated info");
}

