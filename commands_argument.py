
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
                "daily":["１日一回のデイリー報酬をもらうコマンド", {}]
            }
        )
        
        self.owner = Category(
            "owner",
            {
                "admin_change_money":["ADMIN: change bal of user", {"user":"残高を変更する対象の@[ユーザー名]", "money":"変更後の残高となる金額"}],
                "reload":["update cogs/*** extensions", {}],
                "reset_daily":["reset the daily for a specific user", {"user":"member to reset daily for"}],
                "get_channel_text":["get all text in a given text channel", {"channel":"channel to get all txt for", "history":"how many messages to go back"}],
                "purge":["remove some amount of messages", {"channel":"channel to remove texts from","number":"quantity of messages to remove"}]
            }
        )

        self.gamble = Category(
            "gamble",
            {
                "bal":["選択したユーザーの残高を確認する", {"user":"ユーザーを選択する"}],
                "flip":["コインの表裏のギャンブル", {"bet_amount":"「all」でオールイン、または数字入力でその額をベット e.g. 「100」", "side":"「表」か「裏」と入力でどちらにコインが落ちると思うか決める"}],
                "rps":["ギャンブルジャンケン", {"bet_amount":"「all」でオールイン、または数字入力でその額をベット e.g. 「100」"}],
                "reload_player_sets":["remove players from in-game list", {}]
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