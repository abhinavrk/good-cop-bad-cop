from dataclasses import dataclass
from gcbc.bot.base_bot import BotManager
from gcbc.core.core_data import (
    ActionType,
    DeckState,
    Player,
    TableTopGameState,
)
from gcbc.operators.base_operator import BaseAction


@dataclass
class Aim(BaseAction):
    actor: Player
    target: Player

    def is_valid(self, game: TableTopGameState, deck: DeckState) -> bool:
        return (
            self.actor in game.state
            and self.target in game.state
            and game.is_player_alive(self.actor)
            and game.is_player_alive(self.target)
            and game.state[self.actor].gun.has_gun
        )

    def play(self, game: TableTopGameState, deck: DeckState):
        game.state[self.actor].gun.aimed_at = self.target
        return game, deck

    def notify(self, game: TableTopGameState, notif_manager: BotManager):
        notif_manager.emit_public_notification(
            {
                "action": ActionType.AIM,
                "actor": self.actor,
                "target": self.target,
            }
        )
