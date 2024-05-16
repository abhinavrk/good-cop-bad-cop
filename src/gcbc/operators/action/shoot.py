from copy import deepcopy
from gcbc.core.core_data import (
    ActionType,
    Card,
    DeckState,
    Player,
    TableTopGameState,
)
from gcbc.bot.base_bot import BotManager
from gcbc.core.core_data import IntegrityCard, PlayerHealthState
from gcbc.operators.base_operator import BaseAction


class Shoot(BaseAction):
    def __init__(self, actor: Player, target: Player):
        self.actor = actor
        self.target = target

    def is_valid(self, game: TableTopGameState, deck: DeckState) -> bool:
        if self.actor not in game.state:
            return False

        actor_state = game.state[self.actor]
        target = actor_state.gun.aimed_at

        return (
            target is not None
            and target in game.state
            and target == self.target
            and actor_state.gun.has_gun
            and game.is_player_alive(self.actor)
            and game.is_player_alive(target)
        )

    def play(self, game: TableTopGameState, deck: DeckState):
        actor_state = game.state[self.actor]
        target_state = game.state[self.target]

        # Check if the target has AGENT or KINGPIN card
        has_special_card = any(
            card.card in {IntegrityCard.AGENT, IntegrityCard.KINGPIN}
            for card in target_state.integrity_cards
        )

        # Update the health state of the target
        if has_special_card:
            if target_state.health == PlayerHealthState.ALIVE:
                target_state.health = PlayerHealthState.WOUNDED
            else:
                target_state.health = PlayerHealthState.DEAD
        else:
            target_state.health = PlayerHealthState.DEAD

        # Return the gun to the deck
        actor_state.gun.has_gun = False
        actor_state.gun.aimed_at = None
        deck.return_gun()

        return game, deck

    def notify(self, game: TableTopGameState, notif_manager: BotManager):
        notif_manager.emit_public_notification(
            {
                "action": ActionType.SHOOT,
                "actor": self.actor,
                "target": self.target,
            }
        )
