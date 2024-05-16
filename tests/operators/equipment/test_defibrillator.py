import unittest
from unittest.mock import Mock
from gcbc.core.core_data import (
    ActionType,
    DeckState,
    Player,
    PlayerGameState,
    PlayerGunState,
    PlayerHealthState,
    PlayerIntegrityCardState,
    TableTopGameState,
    IntegrityCard,
    EquipmentCard,
)
from gcbc.bot.base_bot import BaseBot
from gcbc.operators.base_operator import BaseEquipment
from gcbc.operators.equipment.defibrillator import Defibrillator  # Assuming defibrillator.py file for Defibrillator class
from gcbc.bot.base_bot import BotManager

class TestDefibrillator(unittest.TestCase):
    def setUp(self):
        # Create some players
        self.user = 1
        self.target = 2
        self.other_player = 3

        # Create some player states
        self.user_state = PlayerGameState(
            integrity_cards=[
                PlayerIntegrityCardState(card=IntegrityCard.GOOD_COP, face_up=False),
                PlayerIntegrityCardState(card=IntegrityCard.BAD_COP, face_up=False),
                PlayerIntegrityCardState(card=IntegrityCard.AGENT, face_up=True),
            ],
            gun=PlayerGunState(has_gun=False, aimed_at=None),
            equipment=EquipmentCard.DEFIBRILLATOR,
            health=PlayerHealthState.ALIVE,
        )

        self.target_state = PlayerGameState(
            integrity_cards=[
                PlayerIntegrityCardState(card=IntegrityCard.GOOD_COP, face_up=False),
                PlayerIntegrityCardState(card=IntegrityCard.BAD_COP, face_up=True),
                PlayerIntegrityCardState(card=IntegrityCard.KINGPIN, face_up=False),
            ],
            gun=PlayerGunState(has_gun=False, aimed_at=None),
            equipment=None,
            health=PlayerHealthState.DEAD,
        )

        self.other_player_state = PlayerGameState(
            integrity_cards=[
                PlayerIntegrityCardState(card=IntegrityCard.GOOD_COP, face_up=False),
                PlayerIntegrityCardState(card=IntegrityCard.GOOD_COP, face_up=False),
                PlayerIntegrityCardState(card=IntegrityCard.GOOD_COP, face_up=False),
            ],
            gun=PlayerGunState(has_gun=False, aimed_at=None),
            equipment=None,
            health=PlayerHealthState.ALIVE,
        )

        # Create the game state
        self.game_state = TableTopGameState(
            state={
                self.user: self.user_state,
                self.target: self.target_state,
                self.other_player: self.other_player_state,
            }
        )

        # Create the deck state
        self.deck_state = DeckState(
            equipment_cards=[EquipmentCard.TASER, EquipmentCard.POLYGRAPH],
            guns=1,
        )

        # Create a BotManager with mock bots
        self.bot_manager = BotManager(player_map={
            self.user: Mock(BaseBot),
            self.target: Mock(BaseBot),
            self.other_player: Mock(BaseBot),
        })

    def test_is_valid(self):
        # Test valid defibrillator usage
        action = Defibrillator(user=self.user, target=self.target)
        self.assertTrue(action.is_valid(self.game_state, self.deck_state))

        # Test invalid defibrillator usage - user not alive
        self.user_state.health = PlayerHealthState.DEAD
        self.assertFalse(action.is_valid(self.game_state, self.deck_state))
        self.user_state.health = PlayerHealthState.ALIVE  # Reset

        # Test invalid defibrillator usage - target alive
        self.target_state.health = PlayerHealthState.ALIVE
        self.assertFalse(action.is_valid(self.game_state, self.deck_state))
        self.target_state.health = PlayerHealthState.DEAD  # Reset

        # Test invalid defibrillator usage - user has no defibrillator equipment
        self.user_state.equipment = None
        self.assertFalse(action.is_valid(self.game_state, self.deck_state))
        self.user_state.equipment = EquipmentCard.DEFIBRILLATOR# Reset

    def test_play(self):
        action = Defibrillator(user=self.user, target=self.target)
        new_game_state, new_deck_state = action.play(self.game_state, self.deck_state)

        # Check target's health is updated to alive
        self.assertEqual(new_game_state.state[self.target].health, PlayerHealthState.ALIVE)

        # Check defibrillator equipment is returned to the deck
        self.assertEqual(len(new_deck_state.equipment_cards), 3)
        self.assertIn(EquipmentCard.DEFIBRILLATOR, new_deck_state.equipment_cards)

        # Check user has no equipment
        self.assertIsNone(new_game_state.state[self.user].equipment)

    def test_notify(self):
        action = Defibrillator(user=self.user, target=self.target)
        action.notify(self.game_state, self.bot_manager)

        # Check that public notification was called for each bot
        expected_notification = {
            "action": EquipmentCard.DEFIBRILLATOR,
            "actor": self.user,
            "revived": self.target,
        }

        for bot in self.bot_manager.player_map.values():
            bot.on_public_notification.assert_called_with(expected_notification)
