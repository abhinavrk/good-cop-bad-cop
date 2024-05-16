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
from gcbc.operators.base_operator import BaseAction
from gcbc.operators.action.pass_action import Pass  # Assuming pass_action.py file for Pass class
from gcbc.bot.base_bot import BotManager

class TestPass(unittest.TestCase):
    def setUp(self):
        # Create some players
        self.actor = 1
        self.other_player = 2

        # Create some player states
        self.actor_state = PlayerGameState(
            integrity_cards=[
                PlayerIntegrityCardState(card=IntegrityCard.GOOD_COP, face_up=False),
                PlayerIntegrityCardState(card=IntegrityCard.BAD_COP, face_up=False),
                PlayerIntegrityCardState(card=IntegrityCard.AGENT, face_up=True),
            ],
            gun=PlayerGunState(has_gun=False, aimed_at=None),
            equipment=None,
            health=PlayerHealthState.ALIVE,
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
                self.actor: self.actor_state,
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
            self.actor: Mock(BaseBot),
            self.other_player: Mock(BaseBot),
        })

    def test_is_valid(self):
        # Test valid pass
        action = Pass(actor=self.actor)
        self.assertTrue(action.is_valid(self.game_state, self.deck_state))

        # There's no real edge case for is_valid since it always returns True
        # But let's test with an invalid actor just to see it still returns True
        action = Pass(actor=999)  # Invalid player ID
        self.assertTrue(action.is_valid(self.game_state, self.deck_state))

    def test_play(self):
        action = Pass(actor=self.actor)
        new_game_state, new_deck_state = action.play(self.game_state, self.deck_state)

        # The game state and deck state should remain unchanged
        self.assertEqual(new_game_state, self.game_state)
        self.assertEqual(new_deck_state, self.deck_state)

    def test_notify(self):
        action = Pass(actor=self.actor)
        action.notify(self.game_state, self.bot_manager)

        # Check that public notification was called for each bot
        expected_notification = {
            "action": ActionType.PASS,
            "actor": self.actor,
        }

        for bot in self.bot_manager.player_map.values():
            bot.on_public_notification.assert_called_with(expected_notification)
