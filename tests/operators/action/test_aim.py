import unittest
from gcbc.bot.base_bot import BaseBot, BotManager
from gcbc.core.core_data import (
    ActionType,
    DeckState,
    PlayerGameState,
    PlayerGunState,
    PlayerHealthState,
    PlayerIntegrityCardState,
    TableTopGameState,
    IntegrityCard,
    EquipmentCard,
)
from gcbc.operators.action.aim import Aim
from unittest.mock import Mock

class TestAim(unittest.TestCase):
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
            gun=PlayerGunState(has_gun=True, aimed_at=None),
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
        # Test valid aim
        action = Aim(actor=self.actor, target=self.target)
        self.assertTrue(action.is_valid(self.game_state, self.deck_state))

        # Test invalid aim - actor has no gun
        self.actor_state.gun.has_gun = False
        self.assertFalse(action.is_valid(self.game_state, self.deck_state))
        self.actor_state.gun.has_gun = True  # Reset

        # Test invalid aim - target not alive
        self.target_state.health = PlayerHealthState.DEAD
        self.assertFalse(action.is_valid(self.game_state, self.deck_state))
        self.target_state.health = PlayerHealthState.ALIVE  # Reset

        # Test invalid aim - actor not alive
        self.actor_state.health = PlayerHealthState.DEAD
        self.assertFalse(action.is_valid(self.game_state, self.deck_state))
        self.actor_state.health = PlayerHealthState.ALIVE  # Reset

        # Test invalid aim - target not in game
        invalid_target = 999
        action = Aim(actor=self.actor, target=invalid_target)
        self.assertFalse(action.is_valid(self.game_state, self.deck_state))

    def test_play(self):
        action = Aim(actor=self.actor, target=self.target)
        new_game_state, _ = action.play(self.game_state, self.deck_state)

        self.assertEqual(new_game_state.state[self.actor].gun.aimed_at, self.target)

    def test_notify(self):
        action = Aim(actor=self.actor, target=self.target)
        action.notify(self.game_state, self.bot_manager)

        # Check that public notification was called for each bot
        expected_notification = {
            "action": ActionType.AIM,
            "actor": self.actor,
            "target": self.target,
        }

        for bot in self.bot_manager.player_map.values():
            bot.on_public_notification.assert_called_with(expected_notification)

