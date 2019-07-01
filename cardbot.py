#!/usr/bin/env python3
import os
import re
from urllib.request import pathname2url
import sqlite3

import praw

CARD_DB = 'cards.db'
REPLY_DB = 'replied_ids.txt'

REGEX = '\[\[(.*)\]\]'

REPLY_TEMPLATE = """- **{card_name}** | {craft} | {card_rarity} {card_type}
    {stats} | Trait: {tribe_name} | Set: {card_set}
    {skill_disc}
"""

def load_card_db_conn():
    try:
        dbURI = 'file:{}?mode=rw'.format(pathname2url(CARD_DB))
        conn = sqlite3.connect(dbURI, uri=True)
        return conn
    except sqlite3.OperationalError as e:
        print(e, ":", CARD_DB)
        raise e

def load_reply_db():
    if not os.path.isfile(REPLY_DB):
        reply_db = []
    else:
        with open(REPLY_DB, 'r') as f:
            reply_db = f.read().splitlines()
    return reply_db

def decode_craft(clan, cur):
    print(clan)
    sql = 'SELECT name FROM crafts WHERE id = ?'
    return cur.execute(sql, [clan]).fetchone()

def decode_card_set(card_set_id, cur):
    sql = 'SELECT name FROM card_sets WHERE id = ?'
    return cur.execute(sql, [card_set_id]).fetchone()

def decode_rarity(rarity, cur):
    sql = 'SELECT name FROM card_rarity WHERE id = ?'
    return cur.execute(sql, [rarity,]).fetchone()

def decode_card_type(card_type, cur):
    sql = ' SELECT name from card_types WHERE id = ?'
    return cur.execute(sql, [card_type]).fetchone()

def process_reply(_id, matches, card_db_conn, reply_db):
    with open(REPLY_DB, 'a') as f:
        f.write(_id + '\n')
    reply_db.append(_id)
    #card_db_conn.set_trace_callback(print)
    with card_db_conn:
        cur = card_db_conn.cursor()
        sql = 'SELECT * FROM cards WHERE card_name = ? COLLATE NOCASE'
        results = []
        for match in matches:
            rows = cur.execute(sql, [match]).fetchall()
            col_names = list(map(lambda x: x[0], cur.description))
            for r in rows:
                results.append(dict(zip(col_names, r)))
        for r in results:
            # replace <br> with line break
            skill_disc = re.sub('<[^<]+?>', '  \n', r['skill_disc'])
            # replace ascii line divider in Choose cards with horizontal rule
            skill_disc = re.sub('[^-]?----------[^-]?', '\n*****', skill_disc)
            r['skill_disc'] = skill_disc
            r['stats'] = str(r['cost'])
            if(r['char_type'] == 1):
                r['stats'] += ' ' + str(r['atk']) + '/' + str(r['life']) + \
                                ' -> ' + str(r['evo_atk']) + '/' + str(r['evo_life'])
            r['craft'] = decode_craft(r['clan'], cur)
            r['card_rarity'] = decode_rarity(r['rarity'], cur)
            r['card_type'] = decode_card_type(r['char_type'], cur)
            r['card_set'] = decode_card_set(r['card_set_id'], cur)
            print(REPLY_TEMPLATE.format(**r))

def process_comment(comment, card_db_conn, reply_db):
    if(comment.id not in reply_db):
        matches = re.findall(REGEX, comment.body)
        if(matches):
            process_reply(comment.id, matches, card_db_conn, reply_db)

def process_submission(submission, card_db_conn, reply_db):
    if(submission.id not in reply_db):
        matches = re.findall(REGEX, submission.selftext)
        if(matches):
            process_reply(submission.id, matches, card_db_conn, reply_db)
    submission.comments.replace_more(limit=None)
    for comment in submission.comments.list():
        process_comment(comment, card_db_conn, reply_db)

def main():
    reddit = praw.Reddit('shadowverse-cardbot')

    subreddit = reddit.subreddit('ringon')

    card_db_conn = load_card_db_conn()
    print("card_db connection established")

    reply_db = load_reply_db()
    print("reply_db loaded")

    for submission in subreddit.stream.submissions():
        print("processing submission...")
        process_submission(submission, card_db_conn, reply_db)

if __name__ == "__main__":
    main()
