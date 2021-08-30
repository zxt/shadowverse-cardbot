# shadowverse-cardbot

A card lookup bot for [r/shadowverse](https://www.reddit.com/r/Shadowverse/) subreddit

## Setup & Run Locally

Clone the project

```bash
  git clone https://github.com/zxt/shadowverse-cardbot.git
```

The bot requires a sqlite db file to lookup the cards.
You can get one if you go to [this repo](https://github.com/zxt/shadowverse-portal) and either use the scripts or just [download the cards.db file there](https://github.com/zxt/shadowverse-portal/tree/master/svportal/scripts/db).

Go to the project directory

```bash
  cd shadowverse-cardbot
```

Install dependencies

```bash
  pip install -r requirements.txt
```

The bot uses [PRAW](https://praw.readthedocs.io/en/stable/) to access the reddit API, so a `praw.ini` needs to be configured:
```bash
  copy praw.ini.example praw.ini
  vi praw.ini
```

Go through `settings.py` and adjust as needed. In particular you should change `SUBREDDITS` to set which subreddits the bot will monitor, and `CARD_DB` to point to the `cards.db` file you previously set up/downloaded.
```bash
  vi settings.py
```

Finally, start the bot!

```bash
  python3 -u cardbot.py
```

## Running Tests

There are tests written in [pytest](https://pytest.org/) under `tests/`.
To run tests, run the following command at the root directory of the project:

```bash
  pytest
```
## Built With
* python3
* [PRAW](https://praw.readthedocs.io/en/stable/)
* [pytest](https://pytest.org/)
* [shadowverse-portal](https://github.com/zxt/shadowverse-portal)

## License

[MIT](https://github.com/zxt/shadowverse-cardbot/blob/master/LICENSE)
