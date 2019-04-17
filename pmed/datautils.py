import sqlalchemy
import pandas as pd
import os


# create tables
def create_tables(conn):
    conn.execute("DROP TABLE IF EXISTS journal")
    conn.execute("DROP TABLE IF EXISTS article")
    conn.execute("DROP TABLE IF EXISTS citation")
    conn.execute("DROP TABLE IF EXISTS citecount")
    conn.execute(
        "CREATE TABLE IF NOT EXISTS journal (id INTEGER PRIMARY KEY UNIQUE AUTO_INCREMENT, name TEXT)")
    conn.execute(
        "CREATE TABLE IF NOT EXISTS article (id INTEGER PRIMARY KEY UNIQUE, title TEXT, abstract TEXT, pubyear INTEGER, jid INTEGER, keywords TEXT, pmc INTEGER)")
    conn.execute(
        "CREATE TABLE IF NOT EXISTS citation (id INTEGER PRIMARY KEY UNIQUE AUTO_INCREMENT, apmid INTEGER, bpmid INTEGER)")
    conn.execute(
        "CREATE TABLE IF NOT EXISTS citecount (id INTEGER PRIMARY KEY UNIQUE, citations INTEGER)")
    print('Tables created')
    return


# list tables
def list_tables(conn):
    result = conn.execute("SHOW TABLES")
    return result.fetchall()


# write to tables
def write_tables(conn, df, table_name):
    df.to_sql(table_name, con=conn, index=False, if_exists='append')
    return df.shape[0]


# check if journal exists in db, inserting if necessary, return jid
def get_jid(conn, journal):
    # while loop to add, check jid
    jid = 0
    while jid == 0:
        # find jid
        stmt = sqlalchemy.text(
            '''SELECT DISTINCT id FROM journal WHERE name = :j''')
        stmt = stmt.bindparams(j=journal)
        result = conn.execute(stmt).fetchall()
        if result:
            jid = result[0][0]
            return jid
        # insert jid
        stmt = sqlalchemy.text('''INSERT INTO journal VALUES (NULL, :j)''')
        stmt = stmt.bindparams(j=journal)
        conn.execute(stmt)
    return jid


# check if id exist in article, return 0 if not exist
def get_id(conn, id):
    # find id
    stmt = sqlalchemy.text('''SELECT id FROM article WHERE id = :i''')
    stmt = stmt.bindparams(i=id)
    result = conn.execute(stmt).fetchall()
    if result:
        return id
    else:
        return 0


# get all article id
def get_ids(conn):
    # find all ids
    stmt = sqlalchemy.text('''SELECT id FROM article''')
    return pd.read_sql(stmt, conn)['id'].tolist()


# get citation count
def get_cnt(conn, id):
    # find id
    stmt = sqlalchemy.text('''SELECT citations FROM article WHERE id = :i''')
    stmt = stmt.bindparams(i=id)
    result = conn.execute(stmt).fetchall()
    if result:
        return result[0][0]
    else:
        return 0


# update citation count
def update_cnt(conn, id, cnt):
    # update by id
    stmt = sqlalchemy.text('''UPDATE citecount SET citations = :c WHERE id = :i''')
    stmt = stmt.bindparams(c=cnt, i=id)
    conn.execute(stmt)
    return