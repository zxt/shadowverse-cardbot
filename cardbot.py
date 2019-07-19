#!/usr/bin/env python3
import os
import re

import praw

from db_connect import DBConnect

CARD_DB = 'cards.db'
SEEN_DB = 'seen_ids.txt'

REGEX = '\[\[([^]]*)\]\]'

CARD_TEMPLATE = """\
- **[{card_name}](https://shadowverse-portal.com/card/{card_id})**^[B](https://shadowverse-portal.com/image/card/phase2/common/C/C_{card_id}.png)|[E](https://shadowverse-portal.com/image/card/phase2/common/E/E_{card_id}.png) | {craft} | {card_rarity} {card_type}  
  {stats} | Trait: {tribe_name} | Set: {card_set}  
  {skill_disc}
"""

EVO_SKILL_DISC_TEMPLATE_FRAG ="""\
  
  (Evolved) {}
"""

BOT_SIGNATURE_TEMPLATE = """\
  
  ^(---)  
  ^(ding dong! I am a bot. Call me with [[cardname]].  )
  ^(Issues/feedback are welcome by posting on r/ringon or by) [^PM ^to ^my ^maintainer](https://www.reddit.com/message/compose/?to=Zuiran)
"""

def load_seen_db():
    if not os.path.isfile(SEEN_DB):
        seen_db = set()
    else:
        with open(SEEN_DB, 'r') as f:
            seen_db = set(f.read().splitlines())
    return seen_db

def lookup_name_from_id(_id, table, cur):
    sql = 'SELECT name FROM {} WHERE id = ?'.format(table)
    return cur.execute(sql, [_id]).fetchone()['name']

def clean_disc_string(string):
    # replace <br> with line break
    cleaned_string = re.sub('<[^<]+?>', '  \n  ', string)
    # replace ascii line divider in Choose cards with horizontal rule
    cleaned_string = re.sub('[^-]?----------[^-]?', '\n  *****  ', cleaned_string)
    return cleaned_string

def process_reply(_id, matches):
    with DBConnect(CARD_DB) as conn:
        cur = conn.cursor()
        sql = 'SELECT * FROM cards WHERE card_name = ? COLLATE NOCASE'
        results = []
        for match in matches:
            row = cur.execute(sql, [match]).fetchone()
            if(row is not None):
                results.append(row)
            else: # try to search by card ID
                sql2 = 'SELECT * FROM cards WHERE card_id = ?'
                row = cur.execute(sql2, [match]).fetchone()
                if(row is not None):
                    results.append(row)

        reply_message = ""
        if(results != []):
            for r in results:
                cleaned_skill_disc = clean_disc_string(r['skill_disc'])
                if(r['evo_skill_disc'] and r['evo_skill_disc'] != r['skill_disc']):
                    cleaned_evo_disc = clean_disc_string(r['evo_skill_disc'])
                    cleaned_skill_disc += EVO_SKILL_DISC_TEMPLATE_FRAG.format(cleaned_evo_disc)

                r['skill_disc'] = cleaned_skill_disc
                r['stats'] = str(r['cost']) + 'pp'
                if(r['char_type'] == 1):
                    r['stats'] += ' ' + str(r['atk']) + '/' + str(r['life']) + \
                                    ' -> ' + str(r['evo_atk']) + '/' + str(r['evo_life'])

                r['craft'] = lookup_name_from_id(r['clan'], 'crafts', cur)
                r['card_rarity'] = lookup_name_from_id(r['rarity'], 'card_rarity', cur)
                r['card_type'] = lookup_name_from_id(r['char_type'], 'card_types', cur)
                r['card_set'] = lookup_name_from_id(r['card_set_id'], 'card_sets', cur)

                reply_message += CARD_TEMPLATE.format(**r)

            reply_message += BOT_SIGNATURE_TEMPLATE
            print(reply_message)

        return reply_message

def process_comment(comment):
    matches = re.findall(REGEX, comment.body)
    if(matches):
        msg = process_reply(comment.id, matches)
        if(msg):
            comment.reply(msg)

def process_submission(submission):
    matches = re.findall(REGEX, submission.selftext)
    if(matches):
        msg = process_reply(submission.id, matches)
        if(msg):
            submission.reply(msg)

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

    stream = praw.models.util.stream_generator(lambda **kwargs: submissions_and_comments(subreddit, **kwargs),
                                                skip_existing=True)

    with open(SEEN_DB, 'a') as f:
        for post in stream:
            if(post.id not in seen_db):
                process_post(post)
                f.write(post.id + '\n')
                f.flush()
                os.fsync(f)
                seen_db.add(post.id)

if __name__ == "__main__":
    main()
