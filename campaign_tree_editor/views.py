"""Campaign tree editor UI"""

import json

import flask
from campaign_tree_editor import config, campaign_tree

from mara_page import acl, navigation, response, _, bootstrap, html

blueprint = flask.Blueprint('campaign_tree', __name__, static_folder='static', url_prefix='/campaign-tree')

acl_resource = acl.AclResource(name='Campaign Tree')


def navigation_entry():
    return navigation.NavigationEntry(
        label='Campaign Tree', uri_fn=lambda: flask.url_for('campaign_tree.index_page'), icon='sitemap',
        description='Editor for wrong utm parameters in campaign structure')


@blueprint.route('')
@acl.require_permission(acl_resource)
def index_page():
    return response.Response(
        title='Campaign Tree',
        js_files=[flask.url_for('campaign_tree.static', filename='campaign-tree.js')],
        css_files=[flask.url_for('campaign_tree.static', filename='campaign-tree.css')],
        html=[
            bootstrap.card(
                id='campaign-tree-card',
                header_left=_.span(id="table-title")['First ', _.b['search'], ' to select campaigns, then ',
                                                     _.b['edit'], ' all campaigns of the search result'],
                header_right=_.span(id="edit-mode")[
                    _.button(type='button', class_="btn btn-success", onclick='campaignTree.startEdit()')[
                        'Start Editing']],
                sections=[
                    [_.p['Match results: ',
                         '&nbsp; ',
                         _.input(type='radio', name="searchOptions", id='fuzzy', value='fuzzy', checked='checked'),
                         ' Fuzzy&nbsp; ',
                         _.input(type='radio', name="searchOptions", id='exact', value='exact'),
                         ' Exact',
                     ],
                     _.p['Sort results by: ',
                         '&nbsp; ',
                         _.input(type='checkbox', name="sortOptions", id='sort-level_1', value='level_1'),
                         ' 1st level&nbsp; ',
                         _.input(type='checkbox', name="sortOptions", id='sort-number_of_clicks_last_two_weeks',
                                 value='number_of_clicks_last_two_weeks', checked='checked'),
                         ' # Clicks last 2 Weeks&nbsp; ',
                         _.input(type='checkbox', name="sortOptions", id='sort-number_of_clicks_all_time',
                                 value='number_of_clicks_all_time'),

                         ' # Clicks all time&nbsp; ']],
                    bootstrap.table(
                        id='campaign-tree-table',

                        headers=[_.input(id=level, class_='form-control search-col editable',
                                         type='text', data_level=level, style='min-width:90px', placeholder=level)[' ']
                                 for
                                 level in config.levels()] +
                                [_.input(id='campaign_code', class_='form-control search-col non-editable',
                                         type='text', data_level='campaign_code', style='min-width:90px',
                                         placeholder='Campaign code')[' ']],
                        rows=[])
                ]),
            _.script['''
var campaignTree = null;

document.addEventListener('DOMContentLoaded', function() {
    campaignTree = new CampaignTree("'''
                     + flask.url_for('campaign_tree.index_page') + '''", '''
                     + json.dumps(config.levels()) + ''');
});'''],
            html.spinner_js_function()])


@blueprint.route('/search', methods=['POST'])
@acl.require_permission(acl_resource)
def search():
    return flask.jsonify(campaign_tree.search(flask.request.get_json()))


@blueprint.route('/count', methods=['POST'])
@acl.require_permission(acl_resource)
def count():
    return flask.jsonify(campaign_tree.count(flask.request.get_json()))


@blueprint.route('/save', methods=['POST'])
@acl.require_permission(acl_resource)
def save():
    data = campaign_tree.save(flask.request.get_json())
    flask.flash(
        "Successfully saved" + str(data[0][7:-1]) + " Campaigns " + " where we " + str(data[1]),
        category='success')
    return flask.jsonify(data)
