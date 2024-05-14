from copy import deepcopy
from gcbc.core.core_data import ActionType, Card, DeckState, Player, TableTopGameState
from gcbc.action.base_action import BaseAction

class ArmAndAim(BaseAction):
    def __init__(self, actor: Player, target: Player, card_to_flip: int):
        self.actor = actor
        self.target = target
        self.card_to_flip = card_to_flip

    def is_valid(self, game: TableTopGameState, deck: DeckState) -> bool:
        if self.actor not in game.state or self.target not in game.state:
            return False

        actor_state = game.state[self.actor]

        if not (game.is_player_alive(self.actor) and game.is_player_alive(self.target)):
            return False

        if deck.guns <= 0:
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

        if deck.get_gun():
            actor_state.gun.has_gun = True
            actor_state.gun.aimed_at = self.target

            # Flip the card
            card_to_flip_state = actor_state.integrity_cards[self.card_to_flip]
            card_to_flip_state.face_up = True

        return TableTopGameState(new_state)

    def notify(self) -> dict:
        return {
            "action": ActionType.ARM_AND_AIM,
            "actor": self.actor,
            "target": self.target,
            "card_to_flip": self.card_to_flip,
        }
