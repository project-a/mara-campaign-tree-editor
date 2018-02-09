import mara_db.sqlalchemy
import psycopg2.extensions
import sqlalchemy
from sqlalchemy.ext.declarative import declarative_base
import io, os
from app.campaign_tree import config

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
    with mara_db.sqlalchemy.postgres_cursor_context(
            config.campaign_codes_db_alias()) as cursor:  # type: psycopg2.extensions.cursor
        cursor.copy_to(buf, f"({config.campaign_codes_query()})")

    with mara_db.sqlalchemy.postgres_cursor_context(
            mara_db.config.mara_db_alias()) as cursor:  # type: psycopg2.extensions.cursor
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
DELETE FROM campaign_tree 
USING campaign_tree ct
LEFT JOIN dwh_campaign_code cc USING (campaign_code)
WHERE  cc.campaign_code IS NULL""")

        print('done')


def replace_external_sortnames_with_internal(sortcolumn):
    """Map external sort column names to internal names"""
    return [column.replace('number_of_clicks_last_two_weeks', 'touchpoints_last_two_weeks').replace(
        'number_of_clicks_all_time', 'all_time_touchpoints').replace('level_1', '1')
            for column in sortcolumn]


def search(request):
    """Search campaigns either on exact or fuzzy(ilike) matching and order results by touchpoint count"""
    query = '''
SELECT levels, campaign_code 
FROM campaign_tree
WHERE TRUE '''

    if request["search-mode"] == 'fuzzy':  # searching
        for index, search in enumerate(request["filters"]):
            if search:
                query += f"""
    AND levels[{index + 1}] ILIKE '%{search}%'"""
    else:  # exact
        for index, search in enumerate(request["filters"]):
            if search:
                query += f"""
    AND levels[{index + 1}] = '{search}'"""

    if len(request["sort-columns"]) > 0:  # sorting
        query += """ ORDER BY """
        for index, sort_columns in enumerate(replace_external_sortnames_with_internal(request["sort-columns"])):
            if index == 0:
                query += f""" {sort_columns}"""
            else:
                query += f""", {sort_columns}"""

    with mara_db.sqlalchemy.postgres_cursor_context(
            mara_db.config.mara_db_alias()) as cursor:  # type: psycopg2.extensions.cursor
        cursor.execute(query)
        return cursor.fetchall() or []


def count(request):
    """Count number of found campaigns"""
    query = '''
SELECT Count(campaign_code) 
FROM campaign_tree
WHERE TRUE '''

    if request["search-mode"] == 'fuzzy':
        for index, search in enumerate(request["filters"]):
            if search:
                query += f"""
     AND levels[{index + 1}] ILIKE '%{search}%'"""
    else:  # exact
        for index, search in enumerate(request["filters"]):
            if search:
                query += f"""
     AND levels[{index + 1}] = '{search}'"""
    with mara_db.sqlalchemy.postgres_cursor_context(
            mara_db.config.mara_db_alias()) as cursor:  # type: psycopg2.extensions.cursor
        cursor.execute(query)
        return cursor.fetchall() or []


if __name__ == "__main__":
    import app

    update()
