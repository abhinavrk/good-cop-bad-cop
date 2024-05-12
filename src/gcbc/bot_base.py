from typing import List, Optional

from gcbc.data_models import *

# a utility class to get the current-state of the game


class GameState:
    def current_player() -> Player:
        pass

    def current_table_state() -> TableTopGameState:
        pass

    def update_history() -> List[Update]:
        pass

    def current_game_turn_phase() -> TurnPhase:
        pass


class BotTemplate:

    def __init__(
        self,
        integrity_cards: List[IntegrityCard],
        num_players: int,
        player_number: Player,
        game: GameState,
    ) -> "BotTemplate":

        self._integrity_cards = integrity_cards
        self.num_players = num_players
        self.player_number = player_number
        self.game = game

    @property
    def integrity_cards(self) -> List[IntegrityCard]:
        return self._integrity_cards

    @integrity_cards.setter
    def integrity_cards(self, value: List[IntegrityCard]) -> None:
        self._integrity_cards = value

    def pre_round(self) -> Optional[EquipmentConsumption]:
        # TODO: add validation for pre-round
        return self._pre_round()

    def action(self) -> Action:
        # TODO: add validation for valid actions
        return self._action()

    def aim(self) -> Optional[Action]:
        # TODO: Add validation for the aim event
        return self._aim()

    # END: Internal-code, do not touch!

    def _pre_round(self) -> Optional[EquipmentConsumption]:
        return None

    def _action(self) -> Action:
        return Action.equip()

    def _aim(self) -> Optional[Action]:
        pass

    def on_board_update(self, update: Update) -> None:
        pass
