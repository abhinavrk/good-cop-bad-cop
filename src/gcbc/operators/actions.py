from dataclasses import dataclass
from gcbc.core.core_data import DeckState, TableTopGameState
from gcbc.data_models import Card, Player
from gcbc.operators.action.aim import Aim
from gcbc.operators.action.arm_and_aim import ArmAndAim
from gcbc.operators.action.equip import Equip
from gcbc.operators.action.investigate import Investigate
from gcbc.operators.action.shoot import Shoot


@dataclass
class Actions:
    game: TableTopGameState
    deck: DeckState

    def aim(self, user: Player, target: Player) -> Aim:
        return self._ret_if_valid(Aim(user, target))

    def _ret_if_valid(self, inst):
        if inst.is_valid(self.game, self.deck):
            return inst
        raise ValueError(f"Invalid {type(inst)} instance")

    def arm_and_aim(
        self, user: Player, target: Player, card_to_flip: Card
    ) -> ArmAndAim:
        return self._ret_if_valid(ArmAndAim(user, target, card_to_flip))

    def equip(self, user: Player, card_to_flip: Card) -> Equip:
        return self._ret_if_valid(Equip(user, card_to_flip))

    def shoot(self, user: Player, target: Player) -> Shoot:
        return self._ret_if_valid(Shoot(user, target))

    def investigate(
        self, user: Player, target: Player, target_card: Card
    ) -> Investigate:
        return self._ret_if_valid(Investigate(user, target, target_card))
