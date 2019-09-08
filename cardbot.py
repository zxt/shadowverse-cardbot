#!/usr/bin/env python3
import os
import re
import time
import logging

import praw
from prawcore import PrawcoreException
from praw.exceptions import APIException

import settings
import templates
import card_lookup
import decklist

logger = logging.getLogger(__name__)
logging.basicConfig(format='%(asctime)s %(levelname)s %(message)s',
                    level=logging.INFO)


def load_seen_db():
    if not os.path.isfile(settings.SEEN_DB):
        seen_db = set()
    else:
        with open(settings.SEEN_DB, 'r') as f:
            seen_db = set(f.read().splitlines())
    return seen_db


def process_reply(post, msg):
    reply_msg = ''.join([msg, templates.BOT_SIGNATURE_TEMPLATE])
    logging.info('\n' + reply_msg)
    post.reply(reply_msg)


def process_lookup(regex, post, fn):
    if isinstance(post, praw.models.Submission):
        text = post.selftext
    elif isinstance(post, praw.models.Comment):
        text = post.body
    matches = re.findall(regex, text)
    if matches:
        logging.info('----------')
        logging.info('post id: %s', post.id)
        reply = fn(matches)
        if reply:
            process_reply(post, reply)


def process_post(post):
    process_lookup(templates.CARD_INFO_REGEX, post,
                   card_lookup.process_card_lookup)
    process_lookup(templates.DECKCODE_REGEX, post,
                   decklist.process_deckcodes)
    process_lookup(templates.SVPORTAL_DECK_REGEX, post,
                   decklist.process_svportal_links)


def submissions_and_comments(subreddit, **kwargs):
    results = []
    results.extend(subreddit.new(**kwargs))
    results.extend(subreddit.comments(**kwargs))
    results.sort(key=lambda post: post.created_utc, reverse=True)
    return results


def stream(subreddit):
    s_g = praw.models.util.stream_generator
    stream = s_g(lambda **kwargs: (
                    submissions_and_comments(subreddit, **kwargs)
                    ), skip_existing=True)
    return stream


def main():
    reddit = praw.Reddit(settings.SITE_NAME)

    subreddit = reddit.subreddit(settings.SUBREDDITS)

    seen_db = load_seen_db()

    with open(settings.SEEN_DB, 'a') as f:
        running = True
        while running:
            try:
                logging.info('starting subreddit stream')
                for post in stream(subreddit):
                    if (post.id not in seen_db and
                            post.author.name not in settings.IGNORED_USERS):
                        process_post(post)
                        f.write(post.id + '\n')
                        f.flush()
                        os.fsync(f)
                        seen_db.add(post.id)
                logging.info('subreddit stream stopped')
            except KeyboardInterrupt:
                logging.info("Bot manually terminated.")
                running = False
            except PrawcoreException:
                logging.exception('unhandled exception occurred:')
                time.sleep(10)
            except APIException:
                logging.exception('reddit API exception:')
                time.sleep(10)


if __name__ == "__main__":
    main()
