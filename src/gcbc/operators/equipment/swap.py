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
class Swap(BaseEquipment):
    user: Player
    playerA: Player
    cardA: int
    playerB: Player
    cardB: int

    def is_valid(self, game: TableTopGameState, deck: DeckState) -> bool:
        return (
            self.user in game.state
            and self.playerA in game.state
            and self.playerB in game.state
            and game.is_player_alive(self.user)
            and game.is_player_alive(self.playerA)
            and game.is_player_alive(self.playerB)
            and self.playerA != self.playerB
            and game.state[self.user].equipment == EquipmentCard.SWAP
            and 0 <= self.cardA < len(game.state[self.playerA].integrity_cards)
            and 0 <= self.cardB < len(game.state[self.playerB].integrity_cards)
        )

    def play(self, game: TableTopGameState, deck: DeckState):
        new_state = game.state

        # Swap the integrity cards
        temp_card = new_state[self.playerA].integrity_cards[self.cardA]
        new_state[self.playerA].integrity_cards[self.cardA] = new_state[
            self.playerB
        ].integrity_cards[self.cardB]
        new_state[self.playerB].integrity_cards[self.cardB] = temp_card

        new_state[self.user].equipment = None
        deck.return_equipment_card(EquipmentCard.SWAP)
        return game, deck

    def notify(self, game: TableTopGameState, notif_manager: BotManager):
        notif_manager.emit_public_notification(
            {
                "action": EquipmentCard.SWAP,
                "actor": self.user,
                "playerA": self.playerA,
                "cardA": self.cardA,
                "playerB": self.playerB,
                "cardB": self.cardB,
            }
        )

    def private_notify(self, game: TableTopGameState, notif_manager: BotManager):
        original_cardA = game.state[self.playerA].integrity_cards[self.cardA].card
        original_cardB = game.state[self.playerB].integrity_cards[self.cardB].card

        payload = {
            "action": EquipmentCard.SWAP,
            "private_data": {
                "actor": self.user,
                "playerA": self.playerA,
                "cardA": self.cardA,
                "cardAValue": original_cardA,
                "playerB": self.playerB,
                "cardB": self.cardB,
                "cardBValue": original_cardB,
            },
        }

        notif_manager.emit_private_notification(self.playerA, payload)
        notif_manager.emit_private_notification(self.playerB, payload)
