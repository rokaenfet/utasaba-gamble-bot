

class CommandArg():

    BASIC_COMMAND_ARGUMENT_DESCRIPTIONS = [
        ["common",{

        }],
        ["unique",{

        }]
    ]

    OWNER_COMMAND_ARGUMENT_DESCRIPTIONS = [
        ["common",{

        }],
        ["unique",{

        }]
    ]

    GAMBLE_COMMAND_ARGUMENT_DESCRIPTIONS = [
        ["common",{
            "bet_amount":"「all」でオールイン、または数字入力でその額をベット e.g. 「100」",
            "opponent":"相手となる@[ユーザー名]。入力なしでボット相手に変更"
        }],
        ["unique",{
            "side":"「表」か「裏」と入力でどちらにコインが落ちると思うか決める"
        }]
    ]

    MEMBER_COMMAND_ARGUMENT_DESCRIPTIONS = [
        ["common",{

        }],
        ["unique",{

        }]
    ]

    command_descriptions = [
        BASIC_COMMAND_ARGUMENT_DESCRIPTIONS,
        OWNER_COMMAND_ARGUMENT_DESCRIPTIONS,
        GAMBLE_COMMAND_ARGUMENT_DESCRIPTIONS,
        MEMBER_COMMAND_ARGUMENT_DESCRIPTIONS
    ]

    ALL_COMMAND_ARGUMENT_DESCRIPTIONS = dict()
    # merge all above dict into 1
    for (common, unique) in command_descriptions:
        print(common, unique)
        ALL_COMMAND_ARGUMENT_DESCRIPTIONS = {
            **ALL_COMMAND_ARGUMENT_DESCRIPTIONS,
            **common[1],
            **unique[1]
            }