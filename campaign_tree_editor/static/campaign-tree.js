// result limiting
var defaultLimit = 20;
var limitOptions = [20, 50, 500];
var limit = defaultLimit;

// current xhr request, kept in order to be able to cancel them
var currentSearchRequest = null;
var currentCountRequest = null;

// result counts of last search response
var numberOfResults = 0;
var numberOfResultsNotDisplayed = 0;

var sortOptions = ['level_1', 'number_of_clicks_last_two_weeks', 'number_of_clicks_all_time'];

var CampaignTree = function (baseUrl, levels) {
    function search() {
        // get values
        var request = {
            'filters': ['', '', '', '', '', ''],
            'sort-columns': [],
            'limit': 0,
            'search-mode': $('input[name="searchOptions"]:checked').val()
        };
        for (var level in levels) {
            request['filters'][level] = $('#' + levels[level]).val();
        }

        for (var i in sortOptions) {
            var option = sortOptions[i];
            if ($('#sort-' + option).prop('checked')) {
                request['sort-columns'].push(option);
            }
        }
        console.log(request['sort-columns'])
        currentSearchRequest = $.ajax({
            type: "POST",
            url: baseUrl + '/search',
            beforeSend: function () {
                if (currentSearchRequest != null) {
                    currentSearchRequest.abort();
                }
                if (currentCountRequest != null) {
                    currentCountRequest.abort();
                }
            },
            contentType: "application/json; charset=utf-8",
            data: JSON.stringify(request),
            success: displaySearchResult,
            dataType: 'json'
        });

        $('#campaign-tree-table tbody').html(spinner());
    }

    function displaySearchResult(data) {
        //numberOfResults = data.length;

        // Add a spinner for the result count (will be loaded asynchronously
        trs = [$('<tr/>').append($('<td colspan="' + (levels.length + 1) + '" id="search-result-counts"/>')
            .append(spinner()))];

        //build request again
        var request = {
            'filters': ['', '', '', '', '', ''],
            'search-mode': $('input[name="searchOptions"]:checked').val()
        };
        for (var level in levels) {
            request['filters'][level] = $('#' + levels[level]).val();
        }

        currentCountRequest = $.ajax({
            type: "POST",
            url: baseUrl + '/count',
            contentType: "application/json; charset=utf-8",
            data: JSON.stringify(request),
            success: displaySearchCounts,
            dataType: 'json'
        });
        //
        // Build rows
        for (var rowKey in data) {
            var row = data[rowKey];


            var tr = $('<tr/>');
            for (var levelKey in row[0]) {
                tr.append($('<td/>').append(row[0][levelKey]));
            }
            tr.append($('<td/>').append(row[1]));
            trs.push(tr);
        }

        // Display
        $('#campaign-tree-table tbody').empty().append(trs);

        // Bind row events for search mode
        // bindRowEvents();
    }

    // Display results from the search query
    var displaySearchCounts = function (data) {
        count = parseInt(data, 10);
        numberOfResultsNotDisplayed = count - numberOfResults;

        var text = (numberOfResults > 0 ? 'Campaigns 1 - ' + Math.min(numberOfResults, count) + ' of ' + data : 'No campaigns found');
        if (count > defaultLimit) {
            text += ' (display '
            for (var i in limitOptions) {
                if (count > limitOptions[i]) {
                    text += '<a href="javascript:search(' + limitOptions[i] + ')">' + limitOptions[i] + '</a>, ';
                }
            }
            text += '<a href="javascript:search(' + count + ')">' + count + '</a> results)';
        }
        ;

        $('#search-result-counts').html(text);
    }

    $('.level-input').unbind().keyup(function () {
        search();
    });
    $('input[name="sortOptions"]').unbind().change(function () {
        search();
    });
    $('input[name="searchOptions"]').unbind().change(function () {
        search();
    });

    search();

    return {}
};


