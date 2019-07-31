#!/usr/bin/env python3
import re

import settings
import templates
from db_connect import DBConnect


def lookup_name_from_id(_id, table, cur):
    sql = 'SELECT name FROM {} WHERE id = ?'.format(table)
    return cur.execute(sql, [_id]).fetchone()['name']


def clean_disc_string(string):
    # replace <br> with line break
    cleaned_string = re.sub('<br>', '  \n  ', string)
    # replace ascii line divider in Choose cards with horizontal rule
    cleaned_string = re.sub('[^-]?----------[^-]?',
                            '\n  *****  ',
                            cleaned_string)
    return cleaned_string


def process_card_lookup(matches):
    with DBConnect(settings.CARD_DB) as conn:
        cur = conn.cursor()
        sql = 'SELECT * FROM cards WHERE card_name = ? COLLATE NOCASE'
        results = []
        for match in matches:
            row = cur.execute(sql, [match]).fetchone()
            if(row is not None):
                results.append(row)
            else:  # try to search by card ID
                sql2 = 'SELECT * FROM cards WHERE card_id = ?'
                row = cur.execute(sql2, [match]).fetchone()
                if(row is not None):
                    results.append(row)

        reply_message = ""
        if results:
            card_ids = []
            for r in results:
                # don't make dupe replies to same card
                if r['card_id'] in card_ids:
                    continue
                card_ids.append(r['card_id'])
                cleaned_skill_disc = clean_disc_string(r['skill_disc'])
                if(r['evo_skill_disc'] and
                   r['evo_skill_disc'] != r['skill_disc']):
                    cleaned_evo_disc = clean_disc_string(r['evo_skill_disc'])
                    t = templates.EVO_SKILL_DISC_TEMPLATE_FRAG
                    cleaned_skill_disc = ''.join([cleaned_skill_disc,
                                                 t.format(cleaned_evo_disc)])

                r['skill_disc'] = cleaned_skill_disc
                r['stats'] = str(r['cost']) + 'pp'
                if r['char_type'] == 1:
                    r['stats'] = ''.join([r['stats'], ' ',
                                          str(r['atk']), '/', str(r['life']),
                                          ' -> ',
                                          str(r['evo_atk']), '/',
                                          str(r['evo_life'])])

                r['craft'] = lookup_name_from_id(r['clan'], 'crafts', cur)
                r['card_rarity'] = lookup_name_from_id(r['rarity'],
                                                       'card_rarity', cur)
                r['card_type'] = lookup_name_from_id(r['char_type'],
                                                     'card_types', cur)
                r['card_set'] = lookup_name_from_id(r['card_set_id'],
                                                    'card_sets', cur)

                r['art_links'] = templates.BASE_ART_LINK.format(r['card_id'])
                if r['card_type'] == 'Follower':
                    t = templates.EVO_ART_LINK
                    r['art_links'] = ''.join([r['art_links'],
                                              t.format(r['card_id'])])

                reply_message = ''.join([reply_message,
                                         templates.CARD_TEMPLATE.format(**r)])

        return reply_message