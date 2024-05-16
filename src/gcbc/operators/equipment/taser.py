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
class Taser(BaseEquipment):
    user: Player
    target: Player
    aimed_at: Player

    def is_valid(self, game: TableTopGameState, deck: DeckState) -> bool:
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

    def play(self, game: TableTopGameState, deck: DeckState):
        new_state = game.state
        new_state[self.user].gun = new_state[self.target].gun
        new_state[self.target].gun = None
        new_state[self.user].gun.aimed_at = self.aimed_at
        new_state[self.user].equipment = None
        deck.return_equipment_card(EquipmentCard.TASER)
        return game, deck

    def notify(self, game: TableTopGameState, notif_manager: BotManager):
        notif_manager.emit_public_notification(
            {
                "action": EquipmentCard.TASER,
                "actor": self.user,
                "stolen_from": self.target,
                "aimed_at": self.aimed_at,
            }
        )
