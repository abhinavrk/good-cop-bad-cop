import unittest
from unittest.mock import Mock, patch, call
from gcbc.core.core_data import (
    IntegrityCard,
    Player,
    TableTopGameState,
    PlayerGameState,
    PlayerGunState,
    PlayerHealthState,
    PlayerIntegrityCardState,
    DeckState,
    EquipmentCard,
)
from gcbc.bot.base_bot import BaseBot
from gcbc.operators.action.aim import Aim
from gcbc.operators.actions import Actions
from gcbc.operators.base_operator import BaseAction, BaseEquipment, BaseOperator
from gcbc.engine.engine import GCBCGameEngine, WinCondition
from gcbc.bot.base_bot import BotManager

class TestGCBCGameEngine(unittest.TestCase):
    def setUp(self):
        self.player_1 = 0
        self.player_2 = 1
        self.player_3 = 2

        # Create some player states
        self.player_1_state = PlayerGameState(
            integrity_cards=[
                PlayerIntegrityCardState(card=IntegrityCard.GOOD_COP, face_up=False),
                PlayerIntegrityCardState(card=IntegrityCard.BAD_COP, face_up=False),
                PlayerIntegrityCardState(card=IntegrityCard.AGENT, face_up=True),
            ],
            gun=PlayerGunState(has_gun=False, aimed_at=None),
            equipment=None,
            health=PlayerHealthState.ALIVE,
        )

        self.player_2_state = PlayerGameState(
            integrity_cards=[
                PlayerIntegrityCardState(card=IntegrityCard.GOOD_COP, face_up=False),
                PlayerIntegrityCardState(card=IntegrityCard.BAD_COP, face_up=True),
                PlayerIntegrityCardState(card=IntegrityCard.KINGPIN, face_up=False),
            ],
            gun=PlayerGunState(has_gun=True, aimed_at=self.player_3),
            equipment=EquipmentCard.TASER,
            health=PlayerHealthState.ALIVE,
        )

        self.player_3_state = PlayerGameState(
            integrity_cards=[
                PlayerIntegrityCardState(card=IntegrityCard.GOOD_COP, face_up=False),
                PlayerIntegrityCardState(card=IntegrityCard.GOOD_COP, face_up=False),
                PlayerIntegrityCardState(card=IntegrityCard.AGENT, face_up=False),
            ],
            gun=PlayerGunState(has_gun=False, aimed_at=None),
            equipment=None,
            health=PlayerHealthState.ALIVE,
        )

        # Create the game state
        self.game_state = TableTopGameState(
            state={
                self.player_1: self.player_1_state,
                self.player_2: self.player_2_state,
                self.player_3: self.player_3_state,
            }
        )

        # Create the deck state
        self.deck_state = DeckState(
            equipment_cards=[EquipmentCard.SWAP, EquipmentCard.DEFIBRILLATOR],
            guns=1,
        )

        # Create a BotManager with mock bots
        self.bot_manager = BotManager(player_map={
            self.player_1: Mock(BaseBot),
            self.player_2: Mock(BaseBot),
            self.player_3: Mock(BaseBot),
        })

        # Create the game engine
        self.engine = GCBCGameEngine(self.game_state, self.deck_state, self.bot_manager)

    def test_enact_valid_action(self):
        action = Mock(BaseAction)
        action.is_valid.return_value = True
        action.play.return_value = (self.game_state, self.deck_state)

        result = self.engine.enact(action)

        self.assertTrue(result)
        action.is_valid.assert_called_once()
        action.play.assert_called_once()
        action.notify.assert_called_once()
        action.private_notify.assert_called_once()

    def test_enact_invalid_action(self):
        action = Mock(BaseOperator)
        action.is_valid.return_value = False

        result = self.engine.enact(action)

        self.assertFalse(result)
        action.is_valid.assert_called_once()
        action.play.assert_not_called()
        action.notify.assert_not_called()
        action.private_notify.assert_not_called()

    def test_single_pre_round(self):
        bot = self.bot_manager.get_bot(self.player_1)
        equipment = Mock(BaseEquipment)
        equipment.is_valid.return_value = True
        bot.pre_round.return_value = equipment

        with patch.object(self.engine, 'enact') as mock_enact:
            result = self.engine.single_pre_round()

        self.assertTrue(result)
        bot.pre_round.assert_called_once()
        mock_enact.assert_called_once_with(equipment)

    def test_single_pre_round_no_valid_moves(self):
        for bot in self.bot_manager.player_map.values():
            bot.pre_round.return_value = None

        with patch.object(self.engine, 'enact') as mock_enact:
            result = self.engine.single_pre_round()

        self.assertFalse(result)
        for bot in self.bot_manager.player_map.values():
            bot.pre_round.assert_called_once()

        mock_enact.assert_not_called()

    def test_action(self):
        bot = self.bot_manager.get_bot(self.player_1)
        action = Mock(BaseOperator)
        bot.action.return_value = action

        with patch.object(self.engine, 'enact') as mock_enact:
            mock_enact.return_value = True
            self.engine.action(self.player_1, bot)

        bot.action.assert_called_once()
        mock_enact.assert_called_once_with(action)

    def test_action_invalid(self):
        bot = self.bot_manager.get_bot(self.player_1)
        action = Mock(BaseAction)
        bot.action.return_value = action

        with patch.object(self.engine, 'enact') as mock_enact:
            mock_enact.return_value = False
            self.engine.action(self.player_1, bot)

        bot.action.assert_called_once()
        mock_enact.assert_any_call(action)
        mock_enact.assert_called_with(Actions.passMove(self.player_1))

    def test_aim(self):
        bot = self.bot_manager.get_bot(self.player_1)
        aim = Aim(1, 2)
        bot.aim.return_value = aim

        with patch.object(self.engine, 'enact') as mock_enact:
            mock_enact.return_value = True
            self.engine.aim(self.player_1, bot)

        bot.aim.assert_called_once()
        mock_enact.assert_called_once_with(aim)

    def test_aim_invalid(self):
        bot = self.bot_manager.get_bot(self.player_1)
        bot.aim.return_value = None

        with patch.object(self.engine, 'enact') as mock_enact:
            mock_enact.return_value = False
            self.engine.aim(self.player_1, bot)

        bot.aim.assert_called_once()

    def test_run_round(self):
        with patch.object(self.engine, 'pre_round') as mock_pre_round, \
             patch.object(self.engine, 'action') as mock_action, \
             patch.object(self.engine, 'aim') as mock_aim:
            
            mock_pre_round.return_value = False
            self.engine.run_round()

        mock_pre_round.assert_called_once()
        mock_action.assert_called_once_with(self.player_1, self.bot_manager.get_bot(self.player_1))
        mock_aim.assert_called_once_with(self.player_1, self.bot_manager.get_bot(self.player_1))

    def test_play_round_no_win(self):
        with patch.object(self.engine, 'win_condition') as mock_win_condition, \
             patch.object(self.engine, 'run_round') as mock_run_round, \
             patch.object(self.engine, 'next_player') as mock_next_player:
            mock_win_condition.return_value = None
            self.engine.play_round()

        mock_win_condition.assert_called_once()
        mock_run_round.assert_called_once()
        mock_next_player.assert_called_once()

    def test_play_round_with_win(self):
        with patch.object(self.engine, 'win_condition') as mock_win_condition:
            mock_win_condition.return_value = WinCondition.ONE_PLAYER_ALIVE
            result = self.engine.play_round()

        mock_win_condition.assert_called_once()
        self.assertEqual(result, WinCondition.ONE_PLAYER_ALIVE)

    def test_next_player(self):
        self.assertEqual(self.engine.next_player(self.player_1), self.player_2)
        self.player_2_state.health = PlayerHealthState.DEAD
        self.assertEqual(self.engine.next_player(self.player_1), self.player_3)

    def test_win_condition(self):
        self.assertIsNone(self.engine.win_condition())

        self.player_1_state.health = PlayerHealthState.DEAD
        self.player_2_state.health = PlayerHealthState.DEAD
        self.assertEqual(self.engine.win_condition(), WinCondition.ONE_PLAYER_ALIVE)

        self.player_1_state.health = PlayerHealthState.ALIVE
        self.player_2_state.health = PlayerHealthState.ALIVE
        self.player_3_state.health = PlayerHealthState.DEAD
        self.assertEqual(self.engine.win_condition(), WinCondition.AGENT_DEAD)

        self.player_3_state.health = PlayerHealthState.ALIVE
        self.player_2_state.integrity_cards = [
            PlayerIntegrityCardState(card=IntegrityCard.AGENT, face_up=True),
            PlayerIntegrityCardState(card=IntegrityCard.KINGPIN, face_up=True),
        ]
        self.assertEqual(self.engine.win_condition(), WinCondition.AGENT_IS_KINGPIN)
