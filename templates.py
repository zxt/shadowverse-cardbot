CARD_INFO_REGEX = r'\[\[([^]]+)\]\]|\\\[\\\[([^]]+)\\\]\\\]'

DECKCODE_REGEX = r'\!(\w{4}(?!\S)|pd\w{4}(?!\S))'

SVPORTAL_DECK_REGEX = r'https://shadowverse-portal\.com/deck/([^?\)\]\s]+)'

BASE_ART_LINK = '^[B](https://shadowverse-portal.com/image/card/phase2/common/C/C_{}.png)'
EVO_ART_LINK = '|[E](https://shadowverse-portal.com/image/card/phase2/common/E/E_{}.png)'

CARD_TEMPLATE = """\
- [**{card_name}**](https://shadowverse-portal.com/card/{card_id}){art_links} | {craft} | {card_rarity} {card_type}  
  {stats} | Trait: {tribe_name} | Set: {card_set}  
  {skill_disc}
"""

EVO_SKILL_DISC_TEMPLATE_FRAG ="""\
  
  (Evolved) {}
"""

BOT_SIGNATURE_TEMPLATE = """\
  
  ^(---)  
  ^(ding dong! I am a bot. Call me with [[cardname]] or !deckcode.)  
  ^(Issues/feedback are welcome by posting on r/ringon or by) [(^PM to my maintainer)](https://www.reddit.com/message/compose/?to=Zuiran)
"""
