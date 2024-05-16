from gcbc.bot.base_bot import BotManager
from gcbc.core.core_data import (
    ActionType,
    Card,
    DeckState,
    Player,
    TableTopGameState,
)
from gcbc.operators.base_operator import BaseAction


class Investigate(BaseAction):
    def __init__(self, actor: Player, target: Player, target_card: Card):
        self.actor = actor
        self.target = target
        self.target_card = target_card

    def is_valid(self, game: TableTopGameState, deck: DeckState) -> bool:
        return (
            self.actor in game.state
            and self.target in game.state
            and game.is_player_alive(self.actor)
            and game.is_player_alive(self.target)
            and 0 <= self.target_card < len(game.state[self.target].integrity_cards)
        )

    def play(self, game: TableTopGameState, deck: DeckState):
        # The investigate action doesn't modify the game state
        return game, deck

    def notify(self, game: TableTopGameState, notif_manager: BotManager):
        notif_manager.emit_public_notification(
            {
                "action": ActionType.INVESTIGATE,
                "actor": self.actor,
                "target": self.target,
                "target_card": self.target_card,
            }
        )

    def private_notify(
        self, game: TableTopGameState, notif_manager: BotManager
    ):
        card_value = game.state[self.target].integrity_cards[self.target_card].card
        notif_manager.emit_private_notification(
            self.actor,
            {
                "action": ActionType.INVESTIGATE,
                "private_data": {
                    "actor": self.actor,
                    "target": self.target,
                    "target_card": self.target_card,
                    "card_value": card_value,
                },
            }
        )
