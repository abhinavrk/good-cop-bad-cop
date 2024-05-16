from copy import deepcopy
from dataclasses import dataclass
from gcbc.bot.base_bot import BotManager
from gcbc.core.core_data import (
    ActionType,
    Card,
    DeckState,
    Player,
    TableTopGameState,
)
from gcbc.operators.base_operator import BaseAction


@dataclass
class Equip(BaseAction):
    actor: Player
    card_to_flip: Card

    def is_valid(self, game: TableTopGameState, deck: DeckState) -> bool:
        if self.actor not in game.state:
            return False

        actor_state = game.get_player_state(self.actor)

        if not game.is_player_alive(self.actor):
            return False

        if len(deck.equipment_cards) <= 0:
            return False

        if actor_state.equipment is not None:
            return False

        integrity_cards = actor_state.integrity_cards
        if not (0 <= self.card_to_flip < len(integrity_cards)):
            return False

        card_to_flip_state = integrity_cards[self.card_to_flip]
        all_cards_face_up = all(card.face_up for card in integrity_cards)
        card_face_down = not card_to_flip_state.face_up

        return all_cards_face_up or card_face_down

    def play(self, game: TableTopGameState, deck: DeckState):
        actor_state = game.state[self.actor]

        # Draw an equipment card
        equipment_card = deck.draw_equipment_card()
        if equipment_card:
            actor_state.equipment = equipment_card

            # Flip the card
            card_to_flip_state = actor_state.integrity_cards[self.card_to_flip]
            card_to_flip_state.face_up = True

        return game, deck

    def notify(self, game: TableTopGameState, notif_manager: BotManager):
        notif_manager.emit_public_notification(
            {
                "action": ActionType.EQUIP,
                "actor": self.actor,
                "card_to_flip": self.card_to_flip,
            }
        )

    def private_notify(
        self, game: TableTopGameState, notif_manager: BotManager
    ):
        equipped_card = game.state[self.actor].equipment
        notif_manager.emit_private_notification(
            self.actor,
            {
                "action": ActionType.EQUIP,
                "private_data": {
                    "actor": self.actor,
                    "equipped_card": equipped_card,
                },
            },
        )
