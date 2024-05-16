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
from gcbc.operators.action.equip import Equip
from gcbc.bot.base_bot import BotManager

class TestEquip(unittest.TestCase):
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
        # Test valid equip
        action = Equip(actor=self.actor, card_to_flip=0)
        self.assertTrue(action.is_valid(self.game_state, self.deck_state))

        # Test invalid equip - actor not alive
        self.actor_state.health = PlayerHealthState.DEAD
        self.assertFalse(action.is_valid(self.game_state, self.deck_state))
        self.actor_state.health = PlayerHealthState.ALIVE  # Reset

        # Test invalid equip - no equipment cards in deck
        self.deck_state.equipment_cards = []
        self.assertFalse(action.is_valid(self.game_state, self.deck_state))
        self.deck_state.equipment_cards = [EquipmentCard.TASER, EquipmentCard.POLYGRAPH]  # Reset

        # Test invalid equip - actor already has equipment
        self.actor_state.equipment = EquipmentCard.TASER
        self.assertFalse(action.is_valid(self.game_state, self.deck_state))
        self.actor_state.equipment = None  # Reset

    def test_play(self):
        action = Equip(actor=self.actor, card_to_flip=0)
        new_game_state, new_deck_state = action.play(self.game_state, self.deck_state)

        self.assertIsNotNone(new_game_state.state[self.actor].equipment)
        self.assertTrue(new_game_state.state[self.actor].integrity_cards[0].face_up)
        self.assertEqual(len(new_deck_state.equipment_cards), 1)

    def test_notify(self):
        action = Equip(actor=self.actor, card_to_flip=0)
        action.notify(self.game_state, self.bot_manager)

        # Check that public notification was called for each bot
        expected_notification = {
            "action": ActionType.EQUIP,
            "actor": self.actor,
            "card_to_flip": 0,
        }

        for bot in self.bot_manager.player_map.values():
            bot.on_public_notification.assert_called_with(expected_notification)

    def test_private_notify(self):
        action = Equip(actor=self.actor, card_to_flip=0)
        new_game_state, _ = action.play(self.game_state, self.deck_state)
        action.private_notify(new_game_state, self.bot_manager)

        equipped_card = new_game_state.state[self.actor].equipment

        # Check that private notification was called for the actor
        expected_notification = {
            "action": ActionType.EQUIP,
            "private_data": {
                "actor": self.actor,
                "equipped_card": equipped_card,
            },
        }

        self.bot_manager.player_map[self.actor].on_private_notification.assert_called_with(expected_notification)
