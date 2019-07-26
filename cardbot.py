#!/usr/bin/env python3
import os
import re

import praw

import settings
import templates
import card_lookup
import decklist

def load_seen_db():
    if not os.path.isfile(settings.SEEN_DB):
        seen_db = set()
    else:
        with open(settings.SEEN_DB, 'r') as f:
            seen_db = set(f.read().splitlines())
    return seen_db

def process_reply(post, msg):
    reply_msg = ''.join([msg, templates.BOT_SIGNATURE_TEMPLATE])
    print(''.join(['-----\n', 'post id:', post.id, '\n', reply_msg, '\n-----']))
    post.reply(reply_msg)

def process_lookup(regex, post, fn):
    if isinstance(post, praw.models.Submission):
        text = post.selftext
    elif isinstance(post, praw.models.Comment):
        text = post.body
    matches = re.findall(regex, text)
    if matches:
        reply = fn(matches)
        if reply:
            process_reply(post, reply)

def process_post(post):
    process_lookup(templates.CARD_INFO_REGEX, post, card_lookup.process_card_lookup)
    process_lookup(templates.DECKCODE_REGEX, post, decklist.process_deckcodes)

def submissions_and_comments(subreddit, **kwargs):
    results = []
    results.extend(subreddit.new(**kwargs))
    results.extend(subreddit.comments(**kwargs))
    results.sort(key=lambda post: post.created_utc, reverse=True)
    return results

def main():
    reddit = praw.Reddit(settings.SITE_NAME)

    subreddit = reddit.subreddit(settings.SUBREDDITS)

    seen_db = load_seen_db()

    stream = praw.models.util.stream_generator(lambda **kwargs: submissions_and_comments(subreddit, **kwargs),
                                                skip_existing=True)

    with open(settings.SEEN_DB, 'a') as f:
        for post in stream:
            if post.id not in seen_db and post.author.name not in settings.IGNORED_USERS:
                process_post(post)
                f.write(post.id + '\n')
                f.flush()
                os.fsync(f)
                seen_db.add(post.id)

if __name__ == "__main__":
    main()
