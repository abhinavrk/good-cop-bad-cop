from gcbc.core.core_data import Card, Player
from gcbc.operators.action.aim import Aim
from gcbc.operators.action.arm_and_aim import ArmAndAim
from gcbc.operators.action.equip import Equip
from gcbc.operators.action.investigate import Investigate
from gcbc.operators.action.pass_action import Pass
from gcbc.operators.action.shoot import Shoot


class Actions:
    @staticmethod
    def aim(user: Player, target: Player) -> Aim:
        return Aim(user, target)

    @staticmethod
    def arm_and_aim(user: Player, target: Player, card_to_flip: Card) -> ArmAndAim:
        return ArmAndAim(user, target, card_to_flip)

    @staticmethod
    def equip(user: Player, card_to_flip: Card) -> Equip:
        return Equip(user, card_to_flip)

    @staticmethod
    def shoot(user: Player, target: Player) -> Shoot:
        return Shoot(user, target)

    @staticmethod
    def investigate(user: Player, target: Player, target_card: Card) -> Investigate:
        return Investigate(user, target, target_card)

    @staticmethod
    def passMove(actor: Player) -> Pass:
        return Pass(actor)
