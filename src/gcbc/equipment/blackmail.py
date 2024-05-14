from copy import deepcopy
from gcbc.core.core_data import DeckState, Player, TableTopGameState
from gcbc.data_models import EquipmentCard
from gcbc.equipment.base_equipment import BaseEquipment


class Blackmail(BaseEquipment):
    def __init__(self, user: Player, target: Player):
        self.user = user
        self.target = target

    def is_valid(self, game: TableTopGameState) -> bool:
        return (
            self.user in game.state
            and self.target in game.state
            and game.is_player_alive(self.user)
            and game.is_player_alive(self.target)
            and game.state[self.user].equipment == EquipmentCard.BLACKMAIL
        )

    def play(self, game: TableTopGameState, deck: DeckState) -> TableTopGameState:
        new_state = deepcopy(game.state)
        for integrity_card in new_state[self.target].integrity_cards:
            integrity_card.card = integrity_card.card.flip()

        deck.return_equipment_card(EquipmentCard.BLACKMAIL)
        new_state[self.user].equipment = None
        return TableTopGameState(new_state)

    def notify(self):
        return {
            "action": EquipmentCard.BLACKMAIL,
            "actor": self.user,
            "target": self.target,
        }
