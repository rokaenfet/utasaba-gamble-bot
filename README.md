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
|   commands_argument.py
│
├───cogs
│       basic.py
│       gamble.py
│       member.py
│       owner.py
│
├───json
|       gamble.json
|       daily.json
|       image_daily.json
|       shirotori.json
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
GIPHY_KEY=[insert api key]
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
  - [ ] Make certain messages ephermal / accessible
    - [ ] Admins > can use all commands and see all reps to any users
    - [ ] Members > can use certain commands and see only reps to themselves for certain commands
- [ ] Basic
  - [x] info
  - [x] bal
  - [x] send money
  - [x] simple interactions
    - [x] slap
    - [ ] punch
    - [ ] hug
    - [ ] pat
    - [ ] dance
  - [ ] daily trivia
- [ ] Money
  - [ ] Gamble
    - [x] Rock Paper Scissors
      - [x] VS bot
    - [x] Coin flip
    - [ ] Horse Racing
    - [ ] Black Jack
      - [ ] solo
    - [ ] Poker
      - [ ] solo
      - [ ] multiple participant
    - [ ] Stock Trading
    - [x] Russian Roulette
      - [x] vs bot
      - [x] vs players
  - [ ] Grant Money
    - [x] Via being in VC for over some duration
      - [ ] Move users afk in VC for extended period of time with no activity
    - [x] Posting an image of food in a specific chat daily "飯テロ"
      - [ ] Only reward if image is deemed a food img by AI
    - [x] Posting an image of animals in a specific chat daily "動物"
      - [ ] Only reward if image is deemed a food img by AI
    - [x] reward small amount of money if valid しりとり answer
  - [ ] gamble for match results
    - [ ] sports
      - [ ] football
      - [ ] baseball
      - [ ] basketball
    - [ ] games
      - [ ] valorant
      - [ ] apex legends
- [ ] member management
  - [x] checkしりとりvalidity
    - [x] finishing in ん?
    - [x] ちゃんと「尻」「取り」してる？
    - [x] mapping between カタカナ & ひらがな
    - [ ] is it an existing word? (need AI)
    - [x] no duplicate words
    - [x] handle small case chars and `-`
    - [x] 金貨(きんか) > きんか
    - [x] strip messages of special characters
    - [ ] Only allow hiragana or katakana in bracket
      - [ ] disallow 
  - [ ] assign certain roles given text input in a specific thread e.g. `#見ざる`　`#囁き隊`
- [x] owner/admin
  - [x] sync commands
  - [x] reload extensions
  - [x] give money
  - [ ] /help to display each category of commands easier
  - [x] shiritori managing commands
    - [x] delete past n words from shiritori.json
    - [x] delete a specific word from shiritori.json

### tools / urls
- https://emojipedia.org
  - for getting default emoji's UTF code


![](giphy_attribution_mark.png)