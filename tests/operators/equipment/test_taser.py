import unittest
from unittest.mock import Mock
from gcbc.core.core_data import (
    DeckState,
    EquipmentCard,
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
from gcbc.operators.equipment.taser import Taser  # Assuming taser.py file for Taser class
from gcbc.bot.base_bot import BotManager

class TestTaser(unittest.TestCase):
    def setUp(self):
        # Create some players
        self.user = 1
        self.target = 2
        self.aimed_at = 3

        # Create some player states
        self.user_state = PlayerGameState(
            integrity_cards=[
                PlayerIntegrityCardState(card=IntegrityCard.GOOD_COP, face_up=False),
                PlayerIntegrityCardState(card=IntegrityCard.BAD_COP, face_up=False),
                PlayerIntegrityCardState(card=IntegrityCard.AGENT, face_up=True),
            ],
            gun=PlayerGunState(has_gun=False, aimed_at=None),
            equipment=EquipmentCard.TASER,
            health=PlayerHealthState.ALIVE,
        )

        self.target_state = PlayerGameState(
            integrity_cards=[
                PlayerIntegrityCardState(card=IntegrityCard.GOOD_COP, face_up=False),
                PlayerIntegrityCardState(card=IntegrityCard.BAD_COP, face_up=True),
                PlayerIntegrityCardState(card=IntegrityCard.KINGPIN, face_up=False),
            ],
            gun=PlayerGunState(has_gun=True, aimed_at=self.aimed_at),
            equipment=None,
            health=PlayerHealthState.ALIVE,
        )

        self.aimed_at_state = PlayerGameState(
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
                self.user: self.user_state,
                self.target: self.target_state,
                self.aimed_at: self.aimed_at_state,
            }
        )

        # Create the deck state
        self.deck_state = DeckState(
            equipment_cards=[EquipmentCard.SWAP, EquipmentCard.DEFIBRILLATOR],
            guns=1,
        )

        # Create a BotManager with mock bots
        self.bot_manager = BotManager(player_map={
            self.user: Mock(BaseBot),
            self.target: Mock(BaseBot),
            self.aimed_at: Mock(BaseBot),
        })

    def test_is_valid(self):
        # Test valid taser action
        action = Taser(user=self.user, target=self.target, aimed_at=self.aimed_at)
        self.assertTrue(action.is_valid(self.game_state, self.deck_state))

        # Test invalid taser action - user not alive
        self.user_state.health = PlayerHealthState.DEAD
        self.assertFalse(action.is_valid(self.game_state, self.deck_state))
        self.user_state.health = PlayerHealthState.ALIVE  # Reset

        # Test invalid taser action - target not alive
        self.target_state.health = PlayerHealthState.DEAD
        self.assertFalse(action.is_valid(self.game_state, self.deck_state))
        self.target_state.health = PlayerHealthState.ALIVE  # Reset

        # Test invalid taser action - aimed_at not alive
        self.aimed_at_state.health = PlayerHealthState.DEAD
        self.assertFalse(action.is_valid(self.game_state, self.deck_state))
        self.aimed_at_state.health = PlayerHealthState.ALIVE  # Reset

        # Test invalid taser action - user is target
        action = Taser(user=self.user, target=self.user, aimed_at=self.aimed_at)
        self.assertFalse(action.is_valid(self.game_state, self.deck_state))

        # Test invalid taser action - user is aimed_at
        action = Taser(user=self.user, target=self.target, aimed_at=self.user)
        self.assertFalse(action.is_valid(self.game_state, self.deck_state))

    def test_play(self):
        action = Taser(user=self.user, target=self.target, aimed_at=self.aimed_at)
        new_game_state, new_deck_state = action.play(self.game_state, self.deck_state)

        # Check that the gun was transferred from target to user
        self.assertTrue(new_game_state.state[self.user].gun.has_gun)
        self.assertEqual(new_game_state.state[self.user].gun.aimed_at, self.aimed_at)
        self.assertIsNone(new_game_state.state[self.target].gun)

        # Check taser equipment is returned to the deck
        self.assertEqual(len(new_deck_state.equipment_cards), 3)
        self.assertIn(EquipmentCard.TASER, new_deck_state.equipment_cards)

        # Check user has no equipment
        self.assertIsNone(new_game_state.state[self.user].equipment)

    def test_notify(self):
        action = Taser(user=self.user, target=self.target, aimed_at=self.aimed_at)
        action.notify(self.game_state, self.bot_manager)

        # Check that public notification was called for each bot
        expected_notification = {
            "action": EquipmentCard.TASER,
            "actor": self.user,
            "stolen_from": self.target,
            "aimed_at": self.aimed_at,
        }

        for bot in self.bot_manager.player_map.values():
            bot.on_public_notification.assert_called_with(expected_notification)
