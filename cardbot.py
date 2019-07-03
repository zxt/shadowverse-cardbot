#!/usr/bin/env python3
import os
import re

import praw

from db_connect import DBConnect

CARD_DB = 'cards.db'
SEEN_DB = 'seen_ids.txt'

REGEX = '\[\[(.*)\]\]'

REPLY_TEMPLATE = """- **{card_name}** | {craft} | {card_rarity} {card_type}

  {stats} | Trait: {tribe_name} | Set: {card_set}

  {skill_disc}
"""

def load_seen_db():
    if not os.path.isfile(SEEN_DB):
        seen_db = set()
    else:
        with open(SEEN_DB, 'r') as f:
            seen_db = f.read().splitlines()
    return seen_db

def lookup_name_from_id(_id, table, cur):
    sql = 'SELECT name FROM {} WHERE id = ?'.format(table)
    return cur.execute(sql, [_id]).fetchone()[0]

def process_reply(_id, matches):
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

            r['craft'] = lookup_name_from_id(r['clan'], 'crafts', cur)
            r['card_rarity'] = lookup_name_from_id(r['rarity'], 'card_rarity', cur)
            r['card_type'] = lookup_name_from_id(r['char_type'], 'card_types', cur)
            r['card_set'] = lookup_name_from_id(r['card_set_id'], 'card_sets', cur)

            print(REPLY_TEMPLATE.format(**r))

def process_comment(comment):
    matches = re.findall(REGEX, comment.body)
    if(matches):
        process_reply(comment.id, matches)

def process_submission(submission):
    matches = re.findall(REGEX, submission.selftext)
    if(matches):
        process_reply(submission.id, matches)

def process_post(post):
        if(isinstance(post, praw.models.Submission)):
            process_submission(post)
        elif(isinstance(post, praw.models.Comment)):
            process_comment(post)

def submissions_and_comments(subreddit, **kwargs):
    results = []
    results.extend(subreddit.new(**kwargs))
    results.extend(subreddit.comments(**kwargs))
    results.sort(key=lambda post: post.created_utc, reverse=True)
    return results

def main():
    reddit = praw.Reddit('shadowverse-cardbot')

    subreddit = reddit.subreddit('ringon')

    seen_db = load_seen_db()

    stream = praw.models.util.stream_generator(lambda **kwargs: submissions_and_comments(subreddit, **kwargs))

    with open(SEEN_DB, 'a') as f:
        for post in stream:
            if(post.id not in seen_db):
                process_post(post)
                f.write(post.id + '\n')
                seen_db.add(post.id)

if __name__ == "__main__":
    main()
