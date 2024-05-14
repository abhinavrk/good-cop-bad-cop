from copy import deepcopy
from gcbc.core.core_data import ActionType, Card, DeckState, Player, TableTopGameState
from gcbc.action.base_action import BaseAction

class Equip(BaseAction):
    def __init__(self, actor: Player, card_to_flip: int):
        self.actor = actor
        self.card_to_flip = card_to_flip

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

    def play(self, game: TableTopGameState, deck: DeckState) -> TableTopGameState:
        new_state = deepcopy(game.state)
        actor_state = new_state[self.actor]

        # Draw an equipment card
        equipment_card = deck.draw_equipment_card()
        if equipment_card:
            actor_state.equipment = equipment_card

            # Flip the card
            card_to_flip_state = actor_state.integrity_cards[self.card_to_flip]
            card_to_flip_state.face_up = True

        return TableTopGameState(new_state)

    def notify(self) -> dict:
        return {
            "action": ActionType.EQUIP,
            "actor": self.actor,
            "card_to_flip": self.card_to_flip,
        }
