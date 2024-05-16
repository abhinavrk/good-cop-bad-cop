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
from gcbc.operators.equipment.swap import Swap  # Assuming swap.py file for Swap class
from gcbc.bot.base_bot import BotManager

class TestSwap(unittest.TestCase):
    def setUp(self):
        # Create some players
        self.user = 1
        self.playerA = 2
        self.playerB = 3
        self.other_player = 4

        # Create some player states
        self.user_state = PlayerGameState(
            integrity_cards=[
                PlayerIntegrityCardState(card=IntegrityCard.GOOD_COP, face_up=False),
                PlayerIntegrityCardState(card=IntegrityCard.BAD_COP, face_up=False),
                PlayerIntegrityCardState(card=IntegrityCard.AGENT, face_up=True),
            ],
            gun=PlayerGunState(has_gun=False, aimed_at=None),
            equipment=EquipmentCard.SWAP,
            health=PlayerHealthState.ALIVE,
        )

        self.playerA_state = PlayerGameState(
            integrity_cards=[
                PlayerIntegrityCardState(card=IntegrityCard.GOOD_COP, face_up=False),
                PlayerIntegrityCardState(card=IntegrityCard.BAD_COP, face_up=True),
                PlayerIntegrityCardState(card=IntegrityCard.KINGPIN, face_up=False),
            ],
            gun=PlayerGunState(has_gun=False, aimed_at=None),
            equipment=None,
            health=PlayerHealthState.ALIVE,
        )

        self.playerB_state = PlayerGameState(
            integrity_cards=[
                PlayerIntegrityCardState(card=IntegrityCard.GOOD_COP, face_up=False),
                PlayerIntegrityCardState(card=IntegrityCard.GOOD_COP, face_up=False),
                PlayerIntegrityCardState(card=IntegrityCard.AGENT, face_up=False),
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
                self.user: self.user_state,
                self.playerA: self.playerA_state,
                self.playerB: self.playerB_state,
                self.other_player: self.other_player_state,
            }
        )

        # Create the deck state
        self.deck_state = DeckState(
            equipment_cards=[EquipmentCard.TASER, EquipmentCard.DEFIBRILLATOR],
            guns=1,
        )

        # Create a BotManager with mock bots
        self.bot_manager = BotManager(player_map={
            self.user: Mock(BaseBot),
            self.playerA: Mock(BaseBot),
            self.playerB: Mock(BaseBot),
            self.other_player: Mock(BaseBot),
        })

    def test_is_valid(self):
        # Test valid swap action
        action = Swap(user=self.user, playerA=self.playerA, cardA=0, playerB=self.playerB, cardB=1)
        self.assertTrue(action.is_valid(self.game_state, self.deck_state))

        # Test invalid swap action - user not alive
        self.user_state.health = PlayerHealthState.DEAD
        self.assertFalse(action.is_valid(self.game_state, self.deck_state))
        self.user_state.health = PlayerHealthState.ALIVE  # Reset

        # Test invalid swap action - playerA not alive
        self.playerA_state.health = PlayerHealthState.DEAD
        self.assertFalse(action.is_valid(self.game_state, self.deck_state))
        self.playerA_state.health = PlayerHealthState.ALIVE  # Reset

        # Test invalid swap action - playerB not alive
        self.playerB_state.health = PlayerHealthState.DEAD
        self.assertFalse(action.is_valid(self.game_state, self.deck_state))
        self.playerB_state.health = PlayerHealthState.ALIVE  # Reset

        # Test invalid swap action - same player for A and B
        action = Swap(user=self.user, playerA=self.playerA, cardA=0, playerB=self.playerA, cardB=1)
        self.assertFalse(action.is_valid(self.game_state, self.deck_state))

    def test_play(self):
        action = Swap(user=self.user, playerA=self.playerA, cardA=0, playerB=self.playerB, cardB=1)
        new_game_state, new_deck_state = action.play(self.game_state, self.deck_state)

        # Check the cards have been swapped
        self.assertEqual(new_game_state.state[self.playerA].integrity_cards[0].card, IntegrityCard.GOOD_COP)
        self.assertEqual(new_game_state.state[self.playerB].integrity_cards[1].card, IntegrityCard.GOOD_COP)

        # Check swap equipment is returned to the deck
        self.assertEqual(len(new_deck_state.equipment_cards), 3)
        self.assertIn(EquipmentCard.SWAP, new_deck_state.equipment_cards)

        # Check user has no equipment
        self.assertIsNone(new_game_state.state[self.user].equipment)

    def test_notify(self):
        action = Swap(user=self.user, playerA=self.playerA, cardA=0, playerB=self.playerB, cardB=1)
        action.notify(self.game_state, self.bot_manager)

        # Check that public notification was called for each bot
        expected_notification = {
            "action": EquipmentCard.SWAP,
            "actor": self.user,
            "playerA": self.playerA,
            "cardA": 0,
            "playerB": self.playerB,
            "cardB": 1,
        }

        for bot in self.bot_manager.player_map.values():
            bot.on_public_notification.assert_called_with(expected_notification)

    def test_private_notify(self):
        action = Swap(user=self.user, playerA=self.playerA, cardA=0, playerB=self.playerB, cardB=1)
        action.private_notify(self.game_state, self.bot_manager)

        # Check private notifications were called correctly
        expected_private_notification = {
            "action": EquipmentCard.SWAP,
            "private_data": {
                "actor": self.user,
                "playerA": self.playerA,
                "cardA": 0,
                "cardAValue": IntegrityCard.GOOD_COP,
                "playerB": self.playerB,
                "cardB": 1,
                "cardBValue": IntegrityCard.GOOD_COP,
            },
        }

        self.bot_manager.player_map[self.playerA].on_private_notification.assert_called_with(expected_private_notification)
        self.bot_manager.player_map[self.playerB].on_private_notification.assert_called_with(expected_private_notification)

if __name__ == "__main__":
    unittest.main()
