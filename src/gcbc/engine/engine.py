from copy import deepcopy
import enum
import time
from gcbc.bot.base_bot import BaseBot, BotManager
from gcbc.core.core_data import (
    IntegrityCard,
    Player,
    TableTopGameState,
    DeckState,
)
from gcbc.operators.action.aim import Aim
from gcbc.operators.actions import Actions
from gcbc.operators.base_operator import BaseOperator


class WinCondition(enum.Enum):
    ONE_PLAYER_ALIVE = 0
    AGENT_DEAD = 1
    KINGPIN_DEAD = 2
    AGENT_IS_KINGPIN = 3


class GCBCGameEngine:
    def __init__(
        self,
        game_state: TableTopGameState,
        deck_state: DeckState,
        bot_manager: BotManager,
    ):
        self.game_state = game_state
        self.deck_state = deck_state
        self.bot_manager = bot_manager

        self.current_player = 0
        self.turn_increment = 1

    def enact(self, operator: BaseOperator) -> bool:
        new_game_state = deepcopy(self.game_state)
        new_deck_state = deepcopy(self.deck_state)

        is_valid = operator.is_valid(new_game_state, new_deck_state)

        if is_valid:
            new_game_state, new_deck_state = operator.play(
                new_game_state, new_deck_state
            )
            operator.notify(new_game_state, self.bot_manager)
            operator.private_notify(new_game_state, self.bot_manager)

            self.game_state = new_game_state
            self.deck_state = new_deck_state

        return is_valid

    def single_pre_round(self):
        pre_round_moves = []

        for player, bot in self.bot_manager.player_map.items():
            if not self.game_state.is_player_alive(player):
                continue

            new_game_state = deepcopy(self.game_state)
            new_deck_state = deepcopy(self.deck_state)

            start_time = time.time()
            pre_round_move = bot.pre_round(new_game_state, new_deck_state)
            end_time = time.time()

            if pre_round_move is None:
                continue

            if pre_round_move.is_valid(new_game_state, new_deck_state):
                pre_round_moves.append((pre_round_move, end_time - start_time))

        if not pre_round_moves:
            return False

        pre_round_moves.sort(reverse=True, key=lambda x: x[1])
        best = pre_round_moves.pop()[0]
        self.enact(best)
        return True

    def pre_round(self):
        run_pre_round = True
        while run_pre_round:
            run_pre_round = self.single_pre_round()

    def action(self, player: Player, bot: BaseBot):
        action_to_take = bot.action(
            self.game_state.opaque_state(), self.deck_state.opaque_state()
        )

        if (action_to_take is None) or (type(action_to_take) == Aim):
            return self.enact(Actions.passMove(player))

        if self.enact(action_to_take):
            return True
        else:
            self.enact(Actions.passMove(player))

    def aim(self, player: Player, bot: BaseBot):
        maybe_aim = bot.aim(self.game_state, self.deck_state)
        if maybe_aim is None:
            return False

        if type(maybe_aim) != Aim:
            return self.enact(Actions.passMove(player))

        if self.enact(maybe_aim):
            return True
        else:
            return False

    def run_round(self):
        self.pre_round()

        bot = self.bot_manager.get_bot(self.current_player)
        self.action(self.current_player, bot)
        self.aim(self.current_player, bot)

    def play_round(self):
        win_condition = self.win_condition()
        if win_condition is None:
            self.run_round()
            next_player = self.next_player(self.current_player)
            self.current_player = next_player

        return win_condition

    def next_player(self, curr_player: Player):
        next_player = (curr_player + self.turn_increment) % len(
            self.bot_manager.player_map
        )
        if self.game_state.is_player_alive(next_player):
            return next_player
        else:
            return self.next_player(next_player)

    def win_condition(self):
        players = self.bot_manager.player_map.keys()
        num_players_alive = sum(
            1 for p in players if self.game_state.is_player_alive(p)
        )

        if num_players_alive == 1:
            return WinCondition.ONE_PLAYER_ALIVE

        for p in players:
            if self.game_state.is_player_alive(p):
                if self.is_player_x(p, IntegrityCard.AGENT) and self.is_player_x(
                    p, IntegrityCard.KINGPIN
                ):
                    return WinCondition.AGENT_IS_KINGPIN
            else:
                if self.is_player_x(p, IntegrityCard.AGENT):
                    return WinCondition.AGENT_DEAD

                if self.is_player_x(p, IntegrityCard.KINGPIN):
                    return WinCondition.KINGPIN_DEAD

        return None

    def is_player_x(self, player: Player, x: IntegrityCard) -> bool:
        player_state = self.game_state.state[player]
        player_cards = [x.card for x in player_state.integrity_cards]
        if x in player_cards:
            return True
        return False
