from gcbc.core.core_data import DeckState, NotificationManager, TableTopGameState


class BaseOperator:

    def is_valid(self, game: TableTopGameState, deck: DeckState) -> bool:
        """
        For the given table-top state, determines if the action is valid
        """
        pass

    def play(
        self, game: TableTopGameState, deck: DeckState
    ) -> tuple[TableTopGameState, DeckState]:
        """
        Performs the action on the given state, and returns the new state.
        Does not mutate the given state.
        """
        pass

    def notify(self, game: TableTopGameState, notif_manager: NotificationManager):
        """
        Emit a notification dict that includes any relevant metadata associated with
        this action that can be used to notify other players. The dict will
        only include information that is publicly available to all players.

        examples include the acting player, the target player, any cards in
        the case of swaps, etc.
        """
        pass

    def private_notify(
        self, game: TableTopGameState, notif_manager: NotificationManager
    ):
        """
        Emit a notification dict that includes any relevant metadata associated with
        this action that can be used to notify other players. The dict will
        only include information that is privately availalbe to a few players.
        """
        pass


class BaseAction(BaseOperator):
    pass


class BaseEquipment(BaseOperator):
    pass
