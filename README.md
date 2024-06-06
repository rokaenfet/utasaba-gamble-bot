# utasaba-gamble-bot
custom bot for the new歌鯖

### folder dir

```
C:.
│   .gitignore
│   discord.log
│   funcs.py
│   main.py
│   README.md
│   token.env
│
├───cogs
│       basic.py
│       gamble.py
│       member.py
│       owner.py
│
├───json
        gamble.json
```

- `.gitignore`
  - ignore files such as \_\_pycache_\_\, .env
- `discord.log`
  - logging of bot via `logging.FileHandler()`
- `token.env`
  - omitted from commit. Insert your bot token in the following format
```
# .env
DISCORD_TOKEN=[insert token]
```
- `funcs.py`
  - general functions folder. Use functions via `from [path]/funcs.py import *`
- `main.py`
  - `__main__`, run bot here
- `cogs`
  - cogs files. holds bot commands for each category, e.g. for commands under `owner` category, access via `cogs.owner`
- `json`
  - external file to store data

### Functionality
- [ ] Bot Env
  - [ ] Transform to SQL DB
  - [x] Slash commands rather than prefix commands e.g. `!info ` to ` /info`
- [ ] Basic
  - [x] info
  - [x] bal
  - [ ] send money
  - [ ] simple interactions
    - [ ] e.g. slap
  - [ ] daily trivia
- [ ] Money
  - [ ] Gamble
    - [ ] Rock Paper Scissors
      - [x] VS bot
      - [ ] VS player
    - [x] Coin flip
    - [ ] Horse Racing
    - [ ] Black Jack
      - [ ] solo
      - [ ] multiple participant
    - [ ] Poker
      - [ ] solo
      - [ ] multiple participant
    - [ ] Stock Trading
    - [ ] Russian Roulette
      - [ ] vs bot
      - [ ] vs 1 player
      - [ ] vs multi players
  - [ ] Grant Money
    - [ ] Via being in VC for over some duration
      - [ ] Move users afk in VC for extended period of time with no activity
    - [ ] Posting an image of food in a specific chat daily "飯テロ"
      - [ ] Only reward if image is deemed a food img by AI
    - [ ] Posting an image of animals in a specific chat daily "動物"
      - [ ] Only reward if image is deemed a food img by AI
    - [x] reward small amount of money if valid しりとり answer
- [ ] member management
  - [ ] checkしりとりvalidity
    - [x] finishing in ん?
    - [x] ちゃんと「尻」「取り」してる？
    - [x] mapping between カタカナ & ひらがな
    - [ ] is it an existing word? (need AI)
    - [x] no duplicate words
    - [x] handle small case chars and `-`
    - [x] 金貨(きんか) > きんか
    - [x] strip messages of special characters
  - [ ] assign certain roles given text input in a specific thread e.g. `#見ざる`　`#囁き隊`
- [x] owner/admin
  - [x] sync commands
  - [x] reload extensions
  - [x] give money
  - [ ] /help to display each category of commands easier

### tools / urls
- https://emojipedia.org
  - for getting default emoji's UTF code