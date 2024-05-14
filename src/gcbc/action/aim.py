from copy import deepcopy
from gcbc.core.core_data import ActionType, Card, DeckState, Player, TableTopGameState
from gcbc.action.base_action import BaseAction


class Aim(BaseAction):
    def __init__(self, actor: Player, target: Player):
        self.actor = actor
        self.target = target

    def is_valid(self, game: TableTopGameState, deck: DeckState) -> bool:
        return (
            self.actor in game.state
            and self.target in game.state
            and game.is_player_alive(self.actor)
            and game.is_player_alive(self.target)
            and game.state[self.actor].gun.has_gun
        )

    def play(self, game: TableTopGameState, deck: DeckState) -> TableTopGameState:
        new_state = deepcopy(game.state)
        new_state[self.actor].gun.aimed_at = self.target
        return TableTopGameState(new_state)

    def notify(self) -> dict:
        return {
            "action": ActionType.AIM,
            "actor": self.actor,
            "target": self.target,
        }
