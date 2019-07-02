#!/usr/bin/env python3
import os
import re

import praw

from db_connect import DBConnect

CARD_DB = 'cards.db'
REPLY_DB = 'replied_ids.txt'

REGEX = '\[\[(.*)\]\]'

REPLY_TEMPLATE = """- **{card_name}** | {craft} | {card_rarity} {card_type}

  {stats} | Trait: {tribe_name} | Set: {card_set}

  {skill_disc}
"""

def load_reply_db():
    if not os.path.isfile(REPLY_DB):
        reply_db = []
    else:
        with open(REPLY_DB, 'r') as f:
            reply_db = f.read().splitlines()
    return reply_db

def decode_craft(clan, cur):
    sql = 'SELECT name FROM crafts WHERE id = ?'
    return cur.execute(sql, [clan]).fetchone()[0]

def decode_card_set(card_set_id, cur):
    sql = 'SELECT name FROM card_sets WHERE id = ?'
    return cur.execute(sql, [card_set_id]).fetchone()[0]

def decode_rarity(rarity, cur):
    sql = 'SELECT name FROM card_rarity WHERE id = ?'
    return cur.execute(sql, [rarity,]).fetchone()[0]

def decode_card_type(card_type, cur):
    sql = ' SELECT name from card_types WHERE id = ?'
    return cur.execute(sql, [card_type]).fetchone()[0]

def process_reply(_id, matches, reply_db):
    with open(REPLY_DB, 'a') as f:
        f.write(_id + '\n')
    reply_db.append(_id)
    with DBConnect(CARD_DB) as conn:
        cur = conn.cursor()
        sql = 'SELECT * FROM cards WHERE card_name = ? COLLATE NOCASE'
        results = []
        for match in matches:
            rows = cur.execute(sql, [match]).fetchall()
            col_names = list(map(lambda x: x[0], cur.description))
            for r in rows:
                results.append(dict(zip(col_names, r)))
        for r in results:
            # replace <br> with line break
            cleaned_skill_disc = re.sub('<[^<]+?>', '  \n  ', r['skill_disc'])
            # replace ascii line divider in Choose cards with horizontal rule
            cleaned_skill_disc = re.sub('[^-]?----------[^-]?', '\n  *****  ', cleaned_skill_disc)
            if(r['evo_skill_disc'] and r['evo_skill_disc'] != r['skill_disc']):
                cleaned_evo_disc = re.sub('<[^<]+?>', '  \n  ', r['evo_skill_disc'])
                cleaned_evo_disc = re.sub('[^-]?----------[^-]?', '\n*****', cleaned_evo_disc)
                cleaned_skill_disc += """

  (Evolved) {}""".format(cleaned_evo_disc)
            r['skill_disc'] = cleaned_skill_disc
            r['stats'] = str(r['cost']) + 'pp'
            if(r['char_type'] == 1):
                r['stats'] += ' ' + str(r['atk']) + '/' + str(r['life']) + \
                                ' -> ' + str(r['evo_atk']) + '/' + str(r['evo_life'])
            r['craft'] = decode_craft(r['clan'], cur)
            r['card_rarity'] = decode_rarity(r['rarity'], cur)
            r['card_type'] = decode_card_type(r['char_type'], cur)
            r['card_set'] = decode_card_set(r['card_set_id'], cur)
            print(REPLY_TEMPLATE.format(**r))

def process_comment(comment, reply_db):
    if(comment.id not in reply_db):
        matches = re.findall(REGEX, comment.body)
        if(matches):
            process_reply(comment.id, matches, reply_db)

def process_submission(submission, reply_db):
    if(submission.id not in reply_db):
        matches = re.findall(REGEX, submission.selftext)
        if(matches):
            process_reply(submission.id, matches, reply_db)

def process_post(post, reply_db):
    if(isinstance(post, praw.models.Submission)):
        process_submission(post, reply_db)
    elif(isinstance(post, praw.models.Comment)):
        process_comment(post, reply_db)

def submissions_and_comments(subreddit, **kwargs):
    results = []
    results.extend(subreddit.new(**kwargs))
    results.extend(subreddit.comments(**kwargs))
    results.sort(key=lambda post: post.created_utc, reverse=True)
    return results

def main():
    reddit = praw.Reddit('shadowverse-cardbot')

    subreddit = reddit.subreddit('ringon')

    reply_db = load_reply_db()

    stream = praw.models.util.stream_generator(lambda **kwargs: submissions_and_comments(subreddit, **kwargs))

    for post in stream:
        process_post(post, reply_db)

if __name__ == "__main__":
    main()
