from dataclasses import dataclass
from gcbc.core.core_data import DeckState, Player, TableTopGameState


class BaseBot:
    """
    This is a base class for implementing bots in GCBC.
    """

    def pre_round(self, game_state: TableTopGameState, deck_state: DeckState):
        """
        Called before the round is started. This is where the bot should decide which
        equipment card to play.

        :param game_state: The game state, which contains information about the players,
                           the discarded cards, etc.
        :param deck_state: The state of the deck, which contains information about the
                           number of cards in the deck, the number of cards remaining,
                           etc.
        :return: The equipment card to play.
        """
        pass

    def action(self, game_state: TableTopGameState, deck_state: DeckState):
        """
        Called when it is the bot's turn. This is where the bot should decide what action
        to take.

        :param game_state: The game state, which contains information about the players,
                           the discarded cards, etc.
        :param deck_state: The state of the deck, which contains information about the
                           number of cards in the deck, the number of cards remaining,
                           etc.
        :return: The action to take.
        """
        pass

    def aim(self, game_state: TableTopGameState, deck_state: DeckState):
        """
        Called when it is the bot's turn, and the bot has a gun. This is where the bot
        should decide which player to aim at.

        :param game_state: The game state, which contains information about the players,
                           the discarded cards, etc.
        :param deck_state: The state of the deck, which contains information about the
                           number of cards in the deck, the number of cards remaining,
                           etc.
        :return: The aim action to take.
        """
        pass

    def on_public_notification(self, notification: dict):
        """
        Called when the bot receives a public notification from another player. This is
        where the bot should process the notification and update its state if necessary.

        :param notification: The notification from another player.
        """
        pass

    def on_private_notification(self, notification: dict):
        """
        Called when the bot receives a private notification from another player. This is
        where the bot should process the notification and update its state if necessary.

        :param notification: The notification from another player.
        """
        pass


@dataclass
class BotManager:
    player_map: dict[Player, BaseBot]

    def get_bot(self, player: Player) -> BaseBot:
        return self.player_map[player]

    def emit_public_notification(self, notification: dict):
        for _, bot in self.player_map.items():
            bot.on_public_notification(notification)

    def emit_private_notification(self, player: Player, notification: dict):
        self.player_map[player].on_private_notification(notification)
