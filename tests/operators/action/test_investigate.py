import unittest
from unittest.mock import Mock
from gcbc.core.core_data import (
    ActionType,
    Card,
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
from gcbc.operators.action.investigate import Investigate
from gcbc.bot.base_bot import BotManager

class TestInvestigate(unittest.TestCase):
    def setUp(self):
        # Create some players
        self.actor = 1
        self.target = 2
        self.other_player = 3

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

        self.target_state = PlayerGameState(
            integrity_cards=[
                PlayerIntegrityCardState(card=IntegrityCard.GOOD_COP, face_up=False),
                PlayerIntegrityCardState(card=IntegrityCard.BAD_COP, face_up=True),
                PlayerIntegrityCardState(card=IntegrityCard.KINGPIN, face_up=False),
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
            self.actor: Mock(BaseBot),
            self.target: Mock(BaseBot),
            self.other_player: Mock(BaseBot),
        })

    def test_is_valid(self):
        # Test valid investigate
        action = Investigate(actor=self.actor, target=self.target, target_card=0)
        self.assertTrue(action.is_valid(self.game_state, self.deck_state))

        # Test invalid investigate - actor not alive
        self.actor_state.health = PlayerHealthState.DEAD
        self.assertFalse(action.is_valid(self.game_state, self.deck_state))
        self.actor_state.health = PlayerHealthState.ALIVE  # Reset

        # Test invalid investigate - target not alive
        self.target_state.health = PlayerHealthState.DEAD
        self.assertFalse(action.is_valid(self.game_state, self.deck_state))
        self.target_state.health = PlayerHealthState.ALIVE  # Reset

        # Test invalid investigate - target card out of range
        action = Investigate(actor=self.actor, target=self.target, target_card=3)
        self.assertFalse(action.is_valid(self.game_state, self.deck_state))

    def test_play(self):
        action = Investigate(actor=self.actor, target=self.target, target_card=0)
        new_game_state, new_deck_state = action.play(self.game_state, self.deck_state)

        # The game state should remain unchanged
        self.assertEqual(new_game_state, self.game_state)
        self.assertEqual(new_deck_state, self.deck_state)

    def test_notify(self):
        action = Investigate(actor=self.actor, target=self.target, target_card=0)
        action.notify(self.game_state, self.bot_manager)

        # Check that public notification was called for each bot
        expected_notification = {
            "action": ActionType.INVESTIGATE,
            "actor": self.actor,
            "target": self.target,
            "target_card": 0,
        }

        for bot in self.bot_manager.player_map.values():
            bot.on_public_notification.assert_called_with(expected_notification)

    def test_private_notify(self):
        action = Investigate(actor=self.actor, target=self.target, target_card=0)
        action.private_notify(self.game_state, self.bot_manager)

        card_value = self.game_state.state[self.target].integrity_cards[0].card

        # Check that private notification was called for the actor
        expected_notification = {
            "action": ActionType.INVESTIGATE,
            "private_data": {
                "actor": self.actor,
                "target": self.target,
                "target_card": 0,
                "card_value": card_value,
            },
        }

        self.bot_manager.player_map[self.actor].on_private_notification.assert_called_with(expected_notification)
