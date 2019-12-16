#!/usr/bin/env python3
from collections import Counter
import svportal.deckcode as svp

import logging
logger = logging.getLogger(__name__)


def process_deckcodes(deckcodes):
    if(len(deckcodes) > 1):
        return
    code = deckcodes[0]
    try:
        hsh = svp.get_hash(code)
        return process_deckhash(hsh)
    except ValueError:
        logger.warning('Deckcode {} has expired or is invalid'.format(code))
        return


def process_svportal_links(links):
    if(len(links) > 1):
        return
    return process_deckhash(links[0])


def process_deckhash(deckhash):
    try:
        deckhash = deckhash.replace(r'\_', '_')
        deck = svp.get_deck(deckhash)
    except ValueError:
        logger.warning('Deck hash is invalid: {}'.format(deckhash))
        return

    decklist_reply = generate_decklist_reply(deck)

    decklist_reply = ''.join([decklist_reply,
                              '[**View this deck in SV-Portal**]',
                              '(https://shadowverse-portal.com/deck/',
                              '{})'.format(deckhash)])

    return decklist_reply


def generate_decklist_reply(deck):
    filtered_card_list = []
    keys = ['card_id',
            'card_name',
            'char_type',
            'cost',
            'rarity',
            'use_red_ether',
            'format_type'
            ]
    cards_list = deck['cards']
    # remove keys we don't care about, leaving only the ones listed above
    for card_dict in cards_list:
        filtered_card_list.append(dict((k, card_dict[k])
                                  for k in keys if k in card_dict))

    card_qty = Counter()
    vials = 0
    for card in filtered_card_list:
        card_qty[card['card_id']] += 1
        vials += card['use_red_ether']

    crafts = ['', 'Forestcraft', 'Swordcraft', 'Runecraft', 'Dragoncraft',
              'Shadowcraft', 'Bloodcraft', 'Havencraft', 'Portalcraft']

    # 3 seems to be prebuilts...but only recent ones starting from set 5
    # except some non-prebuilt decks also use 3, so purpose unclear
    # just treat it same as 1 unless a difference is found
    deck_format = ['', 'Constructed', 'Take Two', 'Constructed', 'Open 6']

    if deck['deck_format'] in (1, 3):
        mode = '(Unlimited)' if (any(card['format_type'] == 0
                                 for card in filtered_card_list)) \
                         else '(Rotation)'
    else:
        mode = ''

    reply_header = ' | '.join([
                            ' '.join(['**Class**:', crafts[deck['clan']]]),
                            ' '.join(['**Format**:',
                                      deck_format[deck['deck_format']],
                                      mode]),
                            ' '.join(['**Vials**:', str(vials)])
                        ])
    reply_header += '\n'
    # card list contains an entry for each invidual card
    # this filters out dupe entries
    unique_card_list = [dict(t)
                        for t in {tuple(sorted(d.items()))
                        for d in filtered_card_list}]
    # filtering destroys the card list ordering,
    # so we sort them back in ascending cost
    sorted_card_list = sorted(unique_card_list,
                              key=lambda k: (k['cost'], k['card_id']))

    decklist_table = generate_decklist_table(sorted_card_list, card_qty)

    decklist_reply = ' '.join([reply_header, decklist_table])
    return decklist_reply


def generate_decklist_table(cards_list, qty):
    decklist_table_header = """
Cost|Rarity|Name|Qty|Link
:--:|:--:|:--:|:--:|:--:
"""

    rarity = ['', 'Bronze', 'Silver', 'Gold', 'Legendary']

    card_rows = []
    for card in cards_list:
        card_name_img = ''.join(['[', card['card_name'], ']',
                                 '(https://shadowverse-portal.com/image/',
                                 'card/phase2/common/C/C_',
                                 str(card['card_id']),
                                 '.png)'])
        svp_link = '[SV-Portal](https://shadowverse-portal.com/card/{})\n'
        cards_str = '|'.join([str(card['cost']),
                              rarity[card['rarity']],
                              card_name_img,
                              str(qty[card['card_id']]),
                              svp_link.format(card['card_id']),
                              ])
        card_rows.append(cards_str)

    card_rows.insert(0, decklist_table_header)
    card_rows.append('\n')

    decklist_table = ''.join(card_rows)
    return decklist_table
