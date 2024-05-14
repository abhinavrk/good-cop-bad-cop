
from gcbc.core.core_data import DeckState, TableTopGameState


class BaseEquipment:

    def is_valid(self, game: TableTopGameState) -> bool:
        """
        For the given table-top state, determines if the action is valid
        """
        pass

    def play(self, game: TableTopGameState, deck: DeckState) -> TableTopGameState:
        """
        Performs the action on the given state, and returns the new state.
        Does not mutate the given state.
        """
        pass

    def notify(self) -> dict:
        """
        Returns a dict that includes any relevant metadata associated with
        this action that can be used to notify other players. The dict will
        only include information that is publicly available to all players.

        examples include the acting player, the target player, any cards in
        the case of swaps, etc.
        """
        pass

    def private_notify(self, game: TableTopGameState) -> dict:
        return {}
