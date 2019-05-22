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
        title='Campaign Tree Editor',
        js_files=[flask.url_for('campaign_tree.static', filename='campaign-tree.js')],
        css_files=[flask.url_for('campaign_tree.static', filename='campaign-tree.css')],
        html=[
            bootstrap.card(
                id='campaign-tree-card',
                header_left=_.span(id="table-title")['First ', _.b['search'], ' to select campaigns, then ',
                                                     _.b['edit'], ' all campaigns of the search result'],
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
                         _.input(type='checkbox', name="sortOptions", id='sort-1', value='1'),
                         f' {config.levels()[0]}&nbsp;&nbsp; ',
                         _.input(type='checkbox', name="sortOptions", id='sort-touchpoints_last_two_weeks',
                                 value='touchpoints_last_two_weeks', checked='checked'),
                         ' # Touchpoints last 2 Weeks&nbsp;&nbsp; ',
                         _.input(type='checkbox', name="sortOptions", id='sort-all_time_touchpoints',
                                 value='all_time_touchpoints'),

                         ' # Touchpoints all time&nbsp; ']],
                    bootstrap.table(
                        id='campaign-tree-table',

                        headers=[_.input(id=f'level-{i}', class_='form-control search-col editable',
                                         type='text', data_level=level, placeholder=level, style='min-width:90px')[' ']
                                 for
                                 i, level in enumerate(config.levels())] +
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
            html.spinner_js_function()]
      )


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
    return flask.jsonify(campaign_tree.save(flask.request.get_json()))
