import mara_db.postgresql
import psycopg2.extensions
import sqlalchemy
from sqlalchemy.ext.declarative import declarative_base
import io, os
from campaign_tree_editor import config

Base = declarative_base()


class CampaignTree(Base):
    """A mapping of campaign codes to (edited) levels"""
    __tablename__ = 'campaign_tree'

    campaign_code = sqlalchemy.Column(sqlalchemy.TEXT, primary_key=True)
    levels = sqlalchemy.Column(sqlalchemy.ARRAY(sqlalchemy.TEXT))
    all_time_touchpoints = sqlalchemy.Column(sqlalchemy.INTEGER)
    touchpoints_last_two_weeks = sqlalchemy.Column(sqlalchemy.INTEGER)


def update():
    """Adds new campaign codes to the campaign tree table"""

    print('get campaign codes with touchpoint counts')
    buf = io.StringIO()
    with mara_db.postgresql.postgres_cursor_context(
            config.campaign_codes_db_alias()) as cursor:  # type: psycopg2.extensions.cursor
        cursor.copy_to(buf, f"({config.campaign_codes_query()})")

    with mara_db.postgresql.postgres_cursor_context('mara') as cursor:  # type: psycopg2.extensions.cursor
        print('write to temporary table')
        cursor.execute("""
CREATE TEMPORARY TABLE dwh_campaign_code (
    campaign_code TEXT,
    all_time_touchpoints INTEGER,
    touchpoints_last_two_weeks INTEGER);
""")
        buf.seek(0, os.SEEK_SET)
        cursor.copy_from(buf, 'dwh_campaign_code')

        print('insert new campaign codes')
        cursor.execute(f"""
INSERT INTO campaign_tree (campaign_code, levels, all_time_touchpoints, touchpoints_last_two_weeks)
SELECT 
    cc.campaign_code, 
    string_to_array(cc.campaign_code, {"%s"}),
    cc.all_time_touchpoints,
    cc.touchpoints_last_two_weeks
FROM dwh_campaign_code cc
LEFT JOIN campaign_tree USING (campaign_code)
WHERE campaign_tree.campaign_code IS NULL""", (config.campaign_code_delimiter()))

        print('update existing campaign codes')
        cursor.execute("""
UPDATE campaign_tree ct
SET all_time_touchpoints = cc.all_time_touchpoints,
    touchpoints_last_two_weeks = cc.touchpoints_last_two_weeks 
FROM dwh_campaign_code cc
WHERE cc.campaign_code = ct.campaign_code""")

        print('delete disappeared codes')
        cursor.execute("""
WITH current_campaign_codes AS (
SELECT DISTINCT campaign_code FROM dwh_campaign_code
)
DELETE FROM campaign_tree WHERE campaign_code NOT IN (SELECT campaign_code FROM current_campaign_codes)
""")

        print('done')
        return True  # this is important for mara ETL



def _build_where_clause(request):
    """builds the search mode query depending on if search is fuzzy or exact"""
    variables = []
    conditions = []
    def _add_clause(column, value):
        if request["search-mode"] == 'fuzzy':
            conditions.append(f'{column} ILIKE %s')
            variables.append(f'%{value}%')
        else:
            conditions.append(f'{column} = %s')
            variables.append(value)

    for index, search in enumerate(request["filters"]):
        if search:
            _add_clause(f'levels[{index + 1}]', search)

    if request['campaign_code']:
        _add_clause('campaign_code', request['campaign_code'])

    if conditions:
        return 'WHERE ' + ' AND '.join(conditions), variables
    else:
        return '', []


def search(request):
    """Search campaigns either on exact or fuzzy(ilike) matching and order results by touchpoint count"""
    query = '''
SELECT levels, campaign_code 
FROM campaign_tree
'''

    search_query, variables = _build_where_clause(request)
    query += search_query

    sort_columns = [sort_column for sort_column in request["sort-columns"]
                    if sort_column in ['touchpoints_last_two_weeks', 'all_time_touchpoints', '1']]


    if sort_columns:
        query += ' ORDER BY ' + ', '.join(sort_columns)

    query += f""" LIMIT {int(request["limit"])}"""

    with mara_db.postgresql.postgres_cursor_context('mara') as cursor:  # type: psycopg2.extensions.cursor
        print(query)
        cursor.execute(query, variables)
        return cursor.fetchall() or []


def count(request):
    """Count number of found campaigns"""
    query = '''
SELECT COUNT(campaign_code) 
FROM campaign_tree
'''

    search_query, variables  = _build_where_clause(request)
    query += search_query

    with mara_db.postgresql.postgres_cursor_context('mara') as cursor:  # type: psycopg2.extensions.cursor
        cursor.execute(query, variables)
        return cursor.fetchall() or []


def save(request):
    """Search campaigns either on exact or fuzzy(ilike) matching and order results by touchpoint count"""
    if any(request["changes"]):

        query = 'UPDATE campaign_tree SET '

        query += ', '.join([f'levels[{index + 1}] = %s'
                           for index, change in enumerate(request["changes"])
                           if change])
        where_clause, variables = _build_where_clause(request)
        query += ' ' + where_clause

        with mara_db.postgresql.postgres_cursor_context('mara') as cursor:  # type: psycopg2.extensions.cursor
            cursor.execute(query, tuple([change for change in request['changes'] if change] + variables))
            return f'Successfully updated {cursor.rowcount} rows: <tt>{str(cursor.query.decode("utf-8"))}</tt>'
    else:
        return 'No changes to be made'


if __name__ == "__main__":
    import app

    update()
