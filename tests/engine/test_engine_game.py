import unittest
from unittest.mock import Mock
from copy import deepcopy
from gcbc.core.core_data import (
    Player,
    TableTopGameState,
    PlayerGameState,
    PlayerGunState,
    PlayerHealthState,
    PlayerIntegrityCardState,
    DeckState,
    EquipmentCard,
    IntegrityCard,
)
from gcbc.bot.base_bot import BaseBot
from gcbc.operators.actions import Actions
from gcbc.engine.engine import GCBCGameEngine, WinCondition
from gcbc.bot.base_bot import BotManager
from gcbc.operators.equipment.blackmail import Blackmail
from gcbc.operators.equipment.swap import Swap
from gcbc.operators.equipment.taser import Taser

class TestGCBCGameEngineHappyPath(unittest.TestCase):
    def setUp(self):
        self.player_1 = 0
        self.player_2 = 1
        self.player_3 = 2

        # Create player states
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
            gun=PlayerGunState(has_gun=False, aimed_at=None),
            equipment=None,
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
            equipment_cards=[
                EquipmentCard.TASER,
                EquipmentCard.BLACKMAIL,
                EquipmentCard.SWAP,
            ],
            guns=3,
        )

        # Create a BotManager with mock bots
        self.bot_manager = BotManager(player_map={
            self.player_1: Mock(BaseBot),
            self.player_2: Mock(BaseBot),
            self.player_3: Mock(BaseBot),
        })

        # Create the game engine
        self.engine = GCBCGameEngine(self.game_state, self.deck_state, self.bot_manager)

    def test_happy_path(self):
        # Round 1: All players draw equipment cards

        self.bot_manager.get_bot(self.player_1).pre_round.return_value = None
        self.bot_manager.get_bot(self.player_2).pre_round.return_value = None
        self.bot_manager.get_bot(self.player_3).pre_round.return_value = None

        self.bot_manager.get_bot(self.player_1).action.return_value = Actions.equip(self.player_1, 0)
        self.bot_manager.get_bot(self.player_2).action.return_value = Actions.equip(self.player_2, 0)
        self.bot_manager.get_bot(self.player_3).action.return_value = Actions.equip(self.player_3, 0)

        self.bot_manager.get_bot(self.player_1).aim.return_value = None
        self.bot_manager.get_bot(self.player_2).aim.return_value = None
        self.bot_manager.get_bot(self.player_3).aim.return_value = None

        self.engine.play_round()
        self.engine.play_round()
        self.engine.play_round()

        # Check if each player has drawn an equipment card
        self.assertEqual(self.engine.game_state.state[self.player_1].equipment, EquipmentCard.SWAP)
        self.assertEqual(self.engine.game_state.state[self.player_2].equipment, EquipmentCard.BLACKMAIL)
        self.assertEqual(self.engine.game_state.state[self.player_3].equipment, EquipmentCard.TASER)
        
        # Round 2: Players use their equipment cards
        self.bot_manager.get_bot(self.player_1).pre_round.return_value = Swap(self.player_1, self.player_1, 0, self.player_2, 1)
        self.bot_manager.get_bot(self.player_2).pre_round.return_value = Blackmail(self.player_2, self.player_3)
        self.bot_manager.get_bot(self.player_3).pre_round.return_value = Taser(self.player_3, self.player_2, self.player_1)

        self.bot_manager.get_bot(self.player_1).action.return_value = Actions.arm_and_aim(self.player_1, 2, 0)
        self.bot_manager.get_bot(self.player_2).action.return_value = Actions.arm_and_aim(self.player_2, 1, 0)
        self.bot_manager.get_bot(self.player_3).action.return_value = Actions.arm_and_aim(self.player_3, 3, 1)

        self.engine.play_round()
        self.engine.play_round()
        self.engine.play_round()
        
        # Check the results of using the equipment cards
        self.assertNotEqual(self.game_state.state[self.player_1].integrity_cards[0].card, IntegrityCard.GOOD_COP)
        self.assertTrue(self.game_state.state[self.player_2].gun.has_gun)
        self.assertEqual(self.game_state.state[self.player_2].gun.aimed_at, self.player_1)
        
        # Round 3: All players draw their gun
        self.bot_manager.get_bot(self.player_1).action.return_value = Actions.arm_and_aim(self.player_1, self.player_2, 0)
        self.bot_manager.get_bot(self.player_2).action.return_value = Actions.arm_and_aim(self.player_2, self.player_3, 1)
        self.bot_manager.get_bot(self.player_3).action.return_value = Actions.arm_and_aim(self.player_3, self.player_1, 2)

        for player in [self.player_1, self.player_2, self.player_3]:
            bot = self.bot_manager.get_bot(player)
            self.engine.action(player, bot)

        # Check if each player has a gun
        self.assertTrue(self.game_state.state[self.player_1].gun.has_gun)
        self.assertTrue(self.game_state.state[self.player_2].gun.has_gun)
        self.assertTrue(self.game_state.state[self.player_3].gun.has_gun)
        
        # Round 4: Player 1 shoots Player 2, Player 3 shoots Player 1
        self.bot_manager.get_bot(self.player_1).action.return_value = Actions.shoot(self.player_1, self.player_2)
        self.bot_manager.get_bot(self.player_3).action.return_value = Actions.shoot(self.player_3, self.player_1)

        self.engine.action(self.player_1, self.bot_manager.get_bot(self.player_1))
        self.engine.action(self.player_3, self.bot_manager.get_bot(self.player_3))

        # Check the results of the shooting
        self.assertEqual(self.game_state.state[self.player_2].health, PlayerHealthState.DEAD)
        self.assertEqual(self.game_state.state[self.player_1].health, PlayerHealthState.WOUNDED)

        # Round 5: Ensure Player 3 wins
        self.game_state.state[self.player_1].health = PlayerHealthState.DEAD  # Simulate end of game
        self.assertEqual(self.engine.win_condition(), WinCondition.ONE_PLAYER_ALIVE)

if __name__ == "__main__":
    unittest.main()
