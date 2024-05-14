
from copy import deepcopy
from gcbc.core.core_data import DeckState, Player, TableTopGameState
from gcbc.data_models import EquipmentCard
from gcbc.equipment.base_equipment import BaseEquipment


class Taser(BaseEquipment):

    def __init__(self, user: Player, target: Player, aimed_at: Player):
        self.user = user
        self.target = target
        self.aimed_at = aimed_at

    def is_valid(self, game: TableTopGameState) -> bool:
        return (
            self.user in game.state
            and self.target in game.state
            and self.aimed_at in game.state
            and self.user != self.target
            and self.user != self.aimed_at
            and game.state[self.target].gun is not None
            and game.is_player_alive(self.user)
            and game.is_player_alive(self.target)
            and game.is_player_alive(self.aimed_at)
            and game.state[self.user].equipment == EquipmentCard.TASER
        )

    def play(self, game: TableTopGameState, deck: DeckState) -> TableTopGameState:
        new_state = deepcopy(game.state)
        new_state[self.user].gun = new_state[self.target].gun
        new_state[self.target].gun = None
        new_state[self.user].gun.aimed_at = self.aimed_at
        new_state[self.user].equipment = None
        deck.return_equipment_card(EquipmentCard.TASER)
        return TableTopGameState(new_state)

    def notify(self):
        return {
            "action": EquipmentCard.TASER,
            "actor": self.user,
            "stolen_from": self.target,
            "aimed_at": self.aimed_at
        }
