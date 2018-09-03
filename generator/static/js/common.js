function renderDates() {
    $(".date-column").each(function () {
        var value = $(this).data("date");
        var date = moment(value).toDate(); // use moment to correctly parse date even in safari
        var formattedDate = date.toLocaleTimeString() + " " + date.toLocaleDateString()
        $(this).text(formattedDate);
    });
}