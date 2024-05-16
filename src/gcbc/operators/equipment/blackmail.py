from copy import deepcopy
from dataclasses import dataclass
from gcbc.bot.base_bot import BotManager
from gcbc.core.core_data import (
    DeckState,
    Player,
    TableTopGameState,
)
from gcbc.core.core_data import EquipmentCard
from gcbc.operators.base_operator import BaseEquipment


@dataclass
class Blackmail(BaseEquipment):
    user: Player
    target: Player

    def is_valid(self, game: TableTopGameState, deck: DeckState) -> bool:
        return (
            self.user in game.state
            and self.target in game.state
            and game.is_player_alive(self.user)
            and game.is_player_alive(self.target)
            and game.state[self.user].equipment == EquipmentCard.BLACKMAIL
        )

    def play(self, game: TableTopGameState, deck: DeckState):
        new_state = game.state
        for integrity_card in new_state[self.target].integrity_cards:
            integrity_card.card = integrity_card.card.flip()

        deck.return_equipment_card(EquipmentCard.BLACKMAIL)
        new_state[self.user].equipment = None
        return game, deck

    def notify(self, game: TableTopGameState, notif_manager: BotManager):
        notif_manager.emit_public_notification(
            {
                "action": EquipmentCard.BLACKMAIL,
                "actor": self.user,
                "target": self.target,
            }
        )
