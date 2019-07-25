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
    if msg:
        reply_msg = ''.join([msg, templates.BOT_SIGNATURE_TEMPLATE])
        print('-----')
        print('post id:', post.id)
        print(reply_msg)
        print('-----')
        post.reply(reply_msg)

def process_comment(comment):
    matches = re.findall(templates.CARD_INFO_REGEX, comment.body)
    if matches :
        msg = card_lookup.process_card_lookup(matches)
        process_reply(comment, msg)

    match = re.search(templates.DECKCODE_REGEX, comment.body)
    deckcode = match.group(1)
    if deckcode:
        msg = decklist.process_deckcodes(deckcode)
        process_reply(comment, msg)

def process_submission(submission):
    matches = re.findall(templates.CARD_INFO_REGEX, submission.selftext)
    if matches:
        msg = card_lookup.process_card_lookup(matches)
        process_reply(submission, msg)

    match = re.search(templates.DECKCODE_REGEX, submission.selftext)
    deckcode = match.group(1)
    if deckcode:
        msg = decklist.process_deckcodes(deckcode)
        process_reply(submission, msg)

def process_post(post):
        if isinstance(post, praw.models.Submission):
            process_submission(post)
        elif isinstance(post, praw.models.Comment):
            process_comment(post)

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
