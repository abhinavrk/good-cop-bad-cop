from dataclasses import dataclass
from gcbc.core.core_data import (
    ActionType,
    DeckState,
    Player,
    TableTopGameState,
)
from gcbc.bot.base_bot import BotManager
from gcbc.operators.base_operator import BaseAction


@dataclass
class Pass(BaseAction):
    actor: Player

    def is_valid(self, game: TableTopGameState, deck: DeckState) -> bool:
        return True

    def play(self, game: TableTopGameState, deck: DeckState):
        return game, deck

    def notify(self, game: TableTopGameState, notif_manager: BotManager):
        notif_manager.emit_public_notification(
            {
                "action": ActionType.PASS,
                "actor": self.actor,
            }
        )
