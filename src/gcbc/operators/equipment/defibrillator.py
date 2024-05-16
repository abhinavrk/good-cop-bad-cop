from copy import deepcopy
from dataclasses import dataclass
from gcbc.bot.base_bot import BotManager
from gcbc.core.core_data import (
    DeckState,
    Player,
    TableTopGameState,
)
from gcbc.core.core_data import EquipmentCard, PlayerHealthState
from gcbc.operators.base_operator import BaseEquipment


@dataclass
class Defibrillator(BaseEquipment):
    user: Player
    target: Player

    def is_valid(self, game: TableTopGameState, deck: DeckState) -> bool:
        return (
            self.user in game.state
            and self.target in game.state
            and game.state[self.user].equipment == EquipmentCard.DEFIBRILLATOR
            and not game.is_player_alive(self.target)
            and game.is_player_alive(self.user)
        )

    def play(self, game: TableTopGameState, deck: DeckState):
        new_state = game.state
        new_state[self.target].health = PlayerHealthState.ALIVE
        new_state[self.user].equipment = None
        deck.return_equipment_card(EquipmentCard.DEFIBRILLATOR)
        return game, deck

    def notify(self, game: TableTopGameState, notif_manager: BotManager):
        notif_manager.emit_public_notification(
            {
                "action": EquipmentCard.DEFIBRILLATOR,
                "actor": self.user,
                "revived": self.target,
            }
        )
