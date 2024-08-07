
# class holding each command's information
class Command():
    def __init__(self, args:dict, name:str="", description:str=""):
        self.name = name
        self.description = description
        for param_name, param_description in args.items():
            exec(f"self.{param_name} = '{param_description}'")

class Category():
    def __init__(self, category:str, commands:dict):
        """
        commands = {
            command_name:[command_description:str, args:dict],
            command_name2:[command_description2:str, args2:dict]
        }
        """
        self.category = category
        for name, (command_description, args) in commands.items():
            exec(f"self.{name} = Command(args, name, command_description)")

# class holding all command's information
class CommandParams():
    def __init__(self):
        """
        define name, description, argument names and argument descriptions of each slash command.
        Making it accessible by e.g. CommandParams().cogName.commandName.description
        """

        self.basic = Category(
            "basic",
            {
                "info":["display various information", {}],
                "avatar":["Get user avatar", {"member":"@[ユーザー名]"}],
                "daily":["１日一回のデイリー報酬をもらうコマンド", {}],
                "send_money":["選んだ相手にお金を送ろう！", {"user":"お金を送りたいユーザー名", "amount":"送る金額か「all」で全額送る"}],
                "reload_gif":["reload gifs from GIPHY",{}],
                "slap":["ビンタァァァァァ！！！",{"user":"誰をぉぉぉ、ビンタァァァ、するんだぁぁいぃぃ？！"}],
                "punch":["ぱーんち！",{"user":"誰をパンチしたいんだい？"}],
                "hug":["窒息するほどのハグをしよう！",{"user":"誰に抱擁を授けるのでしょうか？"}],
                "dance":["イッツパーティタァァァイム！！！",{"user":"朝まで一緒に踊るイカレたやつを選べぇ！"}],
                "rankings":["ランキング表示！",{}]
            }
        )
        
        self.owner = Category(
            "owner",
            {
                "admin_change_money":["ADMIN: change bal of user", {"user":"残高を変更する対象の@[ユーザー名]", "money":"変更後の残高となる金額"}],
                "reload":["update cogs/*** extensions", {}],
                "reset_daily":["reset the daily for a specific user", {"user":"member to reset daily for"}],
                "get_channel_text":["get all text in a given text channel", {"channel":"channel to get all txt for", "history":"how many messages to go back"}],
                "purge":["remove some amount of messages", {"channel":"channel to remove texts from","number":"quantity of messages to remove"}],
                "shiritori_del_words":["remove n recent words from shiritori list", {"n":"num of recent words to remove"}],
                "shiritori_show_words":["show n recent words from shiritori list", {"n":"num of recent words to remove"}]
            }
        )

        self.gamble = Category(
            "gamble",
            {
                "bal":["選択したユーザーの残高を確認する", {"user":"ユーザーを選択する"}],
                "flip":["コインの表裏のギャンブル", {"bet_amount":"「all」でオールイン、または数字入力でその額をベット e.g. 「100」", "side":"「表」か「裏」と入力でどちらにコインが落ちると思うか決める"}],
                "rps":["ギャンブルジャンケン", {"bet_amount":"「all」でオールイン、または数字入力でその額をベット e.g. 「100」"}],
                "reload_player_sets":["remove players from in-game list", {}],
                "rl":["時短でボット相手にロシアンルーレット~",{"bet_amount":"「all」でオールイン、または数字入力でその額をベット e.g. 「100」"}],
                "rl_multi":["皆でロシアンルーレット！",{"pocket":"参加費用の金額"}],
                "blackjack":["Get to 21", {"bet_amount": '"all" is all-in, please enter an integer figure like 100'}]
            }
        )

        self.member = Category(
            "member",
            {
                "shiritori":["現在のしりとりの言葉を見る", {}]
            }
        )

def get_all_commands():
    return CommandParams()