"""Configures the campaign tree editor"""

def levels():
    """Determines the number of hierarchy levels and their names"""
    return ['Level_1', 'Level_2', 'Level_3', 'Level_4', 'Level_5', 'Level_6']


def campaign_codes_query()->str:
    """
    A SQL query that returns rows with three columns:
    - campaign_code
    - all_time_touchpoints
    - touchpoints_last_two_weeks
    """
    return 'SELECT * FROM m_tmp.campaign_codes_for_campaign_tree_editor'


def campaign_codes_db_alias()->str:
    """The database in which to run the `campaign_codes_query`"""
    return 'dwh-etl'


def campaign_code_delimiter():
    """The character that separates levels in a campaign code string"""
    return '@'
