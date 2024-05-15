from copy import deepcopy
from gcbc.core.core_data import (
    DeckState,
    NotificationManager,
    Player,
    TableTopGameState,
)
from gcbc.data_models import EquipmentCard
from gcbc.operators.base_operator import BaseEquipment


class Polygraph(BaseEquipment):

    def __init__(self, user: Player, target: Player):
        self.user = user
        self.target = target

    def is_valid(self, game: TableTopGameState, deck: DeckState) -> bool:
        return (
            self.user in game.state
            and self.target in game.state
            and game.state[self.user].equipment == EquipmentCard.POLYGRAPH
            and game.is_player_alive(self.user)
            and game.is_player_alive(self.target)
        )

    def play(self, game: TableTopGameState, deck: DeckState):
        new_state = game.state
        new_state[self.user].equipment = None
        deck.return_equipment_card(EquipmentCard.POLYGRAPH)
        return game, deck

    def notify(self, game: TableTopGameState, notif_manager: NotificationManager):
        notif_manager.emit_public_notification(
            {
                "action": EquipmentCard.POLYGRAPH,
                "actor": self.user,
                "target": self.target,
            }
        )

    def private_notify(
        self, game: TableTopGameState, notif_manager: NotificationManager
    ):
        actor_cards = [card.card for card in game.state[self.user].integrity_cards]
        target_cards = [card.card for card in game.state[self.target].integrity_cards]
        payload = {
            "action": EquipmentCard.POLYGRAPH,
            "private_data": {
                "actor": self.user,
                "target": self.target,
                "actor_cards": actor_cards,
                "target_cards": target_cards,
            },
        }

        notif_manager.emit_private_notification(self.user, payload)
        notif_manager.emit_private_notification(self.target, payload)
