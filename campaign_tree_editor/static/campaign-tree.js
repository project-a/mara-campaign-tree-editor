var CampaignTree = function (baseUrl, levels) {
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

    var sortOptions = ['1', 'touchpoints_last_two_weeks', 'all_time_touchpoints'];

    function search(limit_) {
        limit = limit_ ? limit_ : defaultLimit;
        //create empty string array

        var filters = new Array(levels.length);
        for (var i = 0; i < filters.length; i++) {
            filters[i] = '';
        }

        // get values
        var request = {
            'filters': filters,
            'campaign_code': '',
            'sort-columns': [],
            'limit': limit,
            'search-mode': $('input[name="searchOptions"]:checked').val()
        };
        for (var level in levels) {
            request['filters'][level] = $('#level-' + level).val();
        }
        request['campaign_code'] = $('#level-campaign_code').val();
        for (var i in sortOptions) {
            var option = sortOptions[i];
            if ($('#sort-' + option).prop('checked')) {
                request['sort-columns'].push(option);
            }
        }

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

        $('#campaign-tree-table tbody tr').css('opacity', 0.5);
    }

    function displaySearchResult(data) {
        numberOfResults = data.length;

        // Add a spinner for the result count (will be loaded asynchronously
        trs = [$('<tr/>').append($('<td colspan="' + (levels.length + 1) + '" id="search-result-counts"/>')
            .append(spinner()))];

        //build request again
        var filters = new Array(levels.length);
        for (var i = 0; i < filters.length; i++) {
            filters[i] = '';
        }
        var request = {
            'filters': filters,
            'campaign_code': '',
            'search-mode': $('input[name="searchOptions"]:checked').val()
        };
        for (var level in levels) {
            request['filters'][level] = $('#level-' + level).val();
        }
        request['campaign_code'] = $('#level-campaign_code').val();

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
                var cellContent = $('<td class="data-col" data-level="' + levelKey + '"><a href="javascript:void(0)">' + row[0][levelKey] + '</a></td>');
                tr.append(cellContent);
            }
            var cellContent = $('<td class="data-col" data-level=campaign_code><a href="javascript:void(0)">' + row[1] + '</a></td>');
            tr.append(cellContent);

            trs.push(tr);
        }

        // Display
        $('#campaign-tree-table tbody').empty().append(trs);

        // Bind row events for search mode
        bindRowEvents();
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
                    text += '<a href="javascript:campaignTree.search(' + limitOptions[i] + ')">' + limitOptions[i] + '</a>, ';
                }
            }
            text += '<a href="javascript:campaignTree.search(' + count + ')">' + count + '</a> results)';
        }
        ;

        $('#search-result-counts').html(text);
    };


// Start search while typing
    var bindSearchEvents = function () {
        $('.search-col').unbind().keyup(function () {
            search();
        });

        $('input[name="sortOptions"]').unbind().change(function () {
            search();
        });
        $('input[name="searchOptions"]').unbind().change(function () {
            search();
        });
    };

// Update columns in edit mode while typing
    var bindEditEvents = function () {
        var editAble = levels;
        for (var levelIndex in levels) {
            (function (l) {
                $('#level-' + l).keyup(function () {
                    var inp = $(this).val();
                    console.log(inp);
                    $(this).val(inp.replace(/\|,|\.|;|\?/g, ''));
                    $('.data-col[data-level="' + l + '"]').html($(this).val());
                });
            })(levelIndex);
        }
    };

// Remove all event handlers from input fields
    var unbindSearchOrEditEvents = function () {
        $('.search-col').unbind();
    };

// Start search when clicking on a cell
    var bindRowEvents = function () {
        $('.data-col').click(function () {
            $('#level-' + $(this).attr('data-level')).val($(this).text());
            search();
        });
    };

// Remove all event handlers from cells
    var unbindRowEvents = function () {
        $('.data-col').unbind();
    };

    // Edit mode
// ---------

// Restore state to the version before clicking on the edit button and switch back to search mode
    var cancelEdit = function () {
        // Change UI
        $('#warning').html('');
        $('#mara-page-header div.action-buttons').html(
            '<div class="btn-group"><button type="button" class="btn btn-success" onclick="campaignTree.startEdit()">Start editing</button></div>'
        );
        $('#campaign-tree-table th').removeClass('in-edit-mode');
        $('.search-col.non-editable').prop('readonly', false);
        $('#sort-mode').show();

        // Bind search events
        bindSearchEvents();
        bindRowEvents();

        // Restore last query
        $('.search-col').each(function () {
            $(this).val($(this).attr('data-val'));
        });
        search();
    };

    // Switch from search mode to edit mode
    var startEdit = function () {
        // Save query and clear input fields
        $('.search-col').each(function () {
            $(this).attr('data-val', $(this).val()).val('');
        });

        // Unbind search events
        unbindRowEvents();
        unbindSearchOrEditEvents();
        bindEditEvents();

        // Change UI
        $('#mara-page-header div.action-buttons').html(
            '<div class="btn-group">' +
            '<a id="action-cancel" href="javascript:campaignTree.cancelEdit();"><button type="button" class="btn btn-danger"><span class="icon-trash"> </span>Cancel editing</button></a> ' +
            '&nbsp;&nbsp;&nbsp; <a id="action-save" href="javascript:campaignTree.saveEdit();"><button type="button" class="btn btn-primary"><span class="icon-save"> </span>Save changes</button></a>' +
            '</div>'
        );
        $('#sort-mode').hide();
        if (numberOfResultsNotDisplayed > 0) {
            $('.headline').html('<span style="color: red !important; font-weight: bold;">Saving your edits will also change ' + numberOfResultsNotDisplayed + ' campaigns which are currently not displayed!</span>');
        } else {
            $('.headline').html('Edit all displayed campaigns');
        }
        $('.data-col').each(function () {
            $(this).html($(this).find('a').html());
        });
        $('.input-icon[data-editable="editable"]').each(function () {
            $(this).html('<span class="icon-edit" style="color: green; font-weight: bold;"></span>');
        });
        $('.input-icon[data-editable="non-editable"]').each(function () {
            $(this).html('<span class="icon-edit" style="opacity: 0.3;"></span>');
        });
        $('#campaign-tree-table th').addClass('in-edit-mode');
        $('.search-col.non-editable').prop('readonly', true);
    };


    var displayChange = function (data) {
        //show the warnings and messages
        showAlert(data, 'success');
        cancelEdit();
        search();
    };

// Save changes from edit mode
    var saveEdit = function () {
        var empty_filters = new Array(levels.length);
        var empty_changes = new Array(levels.length);
        for (var i = 0; i < empty_filters.length; i++) {
            empty_filters[i] = '';
            empty_changes[i] = '';
        }

        var request = {
            'filters': empty_filters,
            'campaign_code': '',
            'search-mode': $('input[name="searchOptions"]:checked').val(),
            'changes': empty_changes
        };

        for (var level in levels) {
            request['filters'][level] = $('#level-' + level).attr('data-val');
            request['changes'][level] = $('#level-' + level).val();
        }
        request['campaign_code'] = $('#level-campaign_code').attr('data-val');


        // Send both as POST parameters to the save action
        $.ajax({
            type: "POST",
            url: baseUrl + '/save',
            contentType: "application/json; charset=utf-8",
            data: JSON.stringify(request),
            success: displayChange,
            dataType: 'json'
        });
    };

    $('#campaign-tree-table').removeClass('mara-table-float-header');

    $('.search-col').unbind().keyup(function () {
        search();
    });
    $('input[name="sortOptions"]').unbind().change(function () {
        search();
    });
    $('input[name="searchOptions"]').unbind().change(function () {
        search();
    });

    cancelEdit();

    return {
        search: search,
        startEdit: startEdit,
        cancelEdit: cancelEdit,
        saveEdit: saveEdit
    }
};


