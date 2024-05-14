from copy import deepcopy
from gcbc.core.core_data import DeckState, Player, TableTopGameState
from gcbc.data_models import EquipmentCard, PlayerHealthState
from gcbc.equipment.base_equipment import BaseEquipment


class Defibrillator(BaseEquipment):

    def __init__(self, user: Player, target: Player):
        self.user = user
        self.target = target

    def is_valid(self, game: TableTopGameState) -> bool:
        return (
            self.user in game.state
            and self.target in game.state
            and game.state[self.user].equipment == EquipmentCard.DEFRIBRILLATOR
            and not game.is_player_alive(self.target)
        )

    def play(self, game: TableTopGameState, deck: DeckState) -> TableTopGameState:
        new_state = deepcopy(game.state)
        new_state[self.target].health = PlayerHealthState.ALIVE
        new_state[self.user].equipment = None
        deck.return_equipment_card(EquipmentCard.DEFRIBRILLATOR)
        return TableTopGameState(new_state)

    def notify(self):
        return {
            "action": EquipmentCard.DEFRIBRILLATOR,
            "actor": self.user,
            "revived": self.target,
        }
