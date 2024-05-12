from copy import deepcopy
import unittest as ut
from unittest.mock import MagicMock

from gcbc.data_models import (
    Action,
    ActionType,
    EquipmentCard,
    EquipmentConsumption,
    IntegrityCard,
    OtherUpdateType,
    PlayerGameState,
    PlayerGunState,
    PlayerHealthState,
    PlayerIntegrityCardState,
)
from gcbc.game_engine import GCBCGameEngine, WinCondition


class TestGCBCGameEngine(ut.TestCase):
    P0 = PlayerGameState(
        integrity_cards=[
            PlayerIntegrityCardState(card=IntegrityCard.GOOD_COP, face_up=False),
            PlayerIntegrityCardState(card=IntegrityCard.GOOD_COP, face_up=False),
            PlayerIntegrityCardState(card=IntegrityCard.BAD_COP, face_up=False),
        ],
        gun=PlayerGunState(False, None),
        equipment=None,
        health=PlayerHealthState.ALIVE,
    )

    P1 = PlayerGameState(
        integrity_cards=[
            PlayerIntegrityCardState(card=IntegrityCard.BAD_COP, face_up=False),
            PlayerIntegrityCardState(card=IntegrityCard.BAD_COP, face_up=False),
            PlayerIntegrityCardState(card=IntegrityCard.AGENT, face_up=False),
        ],
        gun=PlayerGunState(False, None),
        equipment=None,
        health=PlayerHealthState.ALIVE,
    )

    P2 = PlayerGameState(
        integrity_cards=[
            PlayerIntegrityCardState(card=IntegrityCard.GOOD_COP, face_up=False),
            PlayerIntegrityCardState(card=IntegrityCard.GOOD_COP, face_up=False),
            PlayerIntegrityCardState(card=IntegrityCard.KINGPIN, face_up=False),
        ],
        gun=PlayerGunState(False, None),
        equipment=None,
        health=PlayerHealthState.ALIVE,
    )

    E = [
        EquipmentCard.TASER,
        EquipmentCard.POLYGRAPH,
        EquipmentCard.DEFIBRILLATOR,
        EquipmentCard.SWAP,
        EquipmentCard.BLACKMAIL,
    ]

    def setUp(self) -> None:
        self.mock_bots = {
            0: MagicMock(),
            1: MagicMock(),
            2: MagicMock(),
        }

        self.engine = GCBCGameEngine(
            init_state={
                0: deepcopy(self.P0),
                1: deepcopy(self.P1),
                2: deepcopy(self.P2),
            },
            equipment=deepcopy(self.E),
            gun_count=4,
            bots=self.mock_bots,
        )

    def reset_bot_mocks(self):
        self.mock_bots[0] = MagicMock()
        self.mock_bots[1] = MagicMock()
        self.mock_bots[2] = MagicMock()

    def test_round_1(self):
        self.mock_bots[0].pre_round.return_value = None
        self.mock_bots[1].pre_round.return_value = None
        self.mock_bots[2].pre_round.return_value = None

        self.mock_bots[0].action.return_value = Action.investigate(1, 2)

        self.mock_bots[0].aim.return_value = None

        result = self.engine.play_round()
        self.assertIsNone(result)

        # for preround, action, aim
        self.assertEqual(6, self.count_updates(self.mock_bots[0], None))

        self.assertEqual(
            3, self.count_updates(self.mock_bots[0], OtherUpdateType.TURN_PHASE_START)
        )
        # for action = INVESTIGATE
        self.assertEqual(
            1, self.count_updates(self.mock_bots[0], ActionType.INVESTIGATE)
        )
        # for the result
        self.assertEqual(
            1,
            self.count_updates(self.mock_bots[0], OtherUpdateType.INVESTIGATION_RESULT),
        )
        # for the aim
        self.assertEqual(1, self.count_updates(self.mock_bots[0], ActionType.PASS))

        # other bots don't get to see the investigation result
        for b in (1, 2):
            # for preround, action, aim
            self.assertEqual(5, self.count_updates(self.mock_bots[b], None))
            self.assertEqual(
                3,
                self.count_updates(self.mock_bots[b], OtherUpdateType.TURN_PHASE_START),
            )
            # for action = INVESTIGATE
            self.assertEqual(
                1, self.count_updates(self.mock_bots[b], ActionType.INVESTIGATE)
            )
            # for the aim
            self.assertEqual(1, self.count_updates(self.mock_bots[b], ActionType.PASS))

    def test_round_2(self):
        self.test_round_1()
        self.reset_bot_mocks()

        # invalid pre-round
        self.mock_bots[0].pre_round.return_value = EquipmentConsumption.blackmail(2)
        self.mock_bots[1].pre_round.return_value = None
        self.mock_bots[2].pre_round.return_value = None
        self.mock_bots[1].action.return_value = Action.equip(1)
        self.mock_bots[1].aim.return_value = None

        result = self.engine.play_round()
        self.assertIsNone(result)

        for b in (0, 2):
            self.assertEqual(8, self.count_updates(self.mock_bots[b], None))

            # for preround, action, aim
            self.assertEqual(
                3,
                self.count_updates(self.mock_bots[b], OtherUpdateType.TURN_PHASE_START),
            )
            # for rollback
            self.assertEqual(
                1, self.count_updates(self.mock_bots[b], OtherUpdateType.EQUIPMENT_CARD)
            )
            self.assertEqual(
                1,
                self.count_updates(
                    self.mock_bots[b], OtherUpdateType.ROLLBACK_INCLUDING
                ),
            )
            # for action = equip
            self.assertEqual(1, self.count_updates(self.mock_bots[b], ActionType.EQUIP))
            self.assertEqual(
                1, self.count_updates(self.mock_bots[b], OtherUpdateType.CARD_FLIP)
            )
            # for the aim
            self.assertEqual(1, self.count_updates(self.mock_bots[b], ActionType.PASS))

        self.assertEqual(9, self.count_updates(self.mock_bots[1], None))

        # for preround, action, aim
        self.assertEqual(
            3, self.count_updates(self.mock_bots[1], OtherUpdateType.TURN_PHASE_START)
        )
        # for rollback
        self.assertEqual(
            1, self.count_updates(self.mock_bots[1], OtherUpdateType.EQUIPMENT_CARD)
        )
        self.assertEqual(
            1, self.count_updates(self.mock_bots[1], OtherUpdateType.ROLLBACK_INCLUDING)
        )
        # for action = equip
        self.assertEqual(1, self.count_updates(self.mock_bots[1], ActionType.EQUIP))
        self.assertEqual(
            1, self.count_updates(self.mock_bots[1], OtherUpdateType.CARD_FLIP)
        )
        self.assertEqual(
            1, self.count_updates(self.mock_bots[1], OtherUpdateType.EQUIP_RESULT)
        )
        # for the aim
        self.assertEqual(1, self.count_updates(self.mock_bots[1], ActionType.PASS))

        self.assertEqual(self.engine.state[1].equipment, EquipmentCard.BLACKMAIL)
        self.assertNotIn(EquipmentCard.BLACKMAIL, self.engine.equipment)

    def test_round_3(self):
        self.test_round_2()
        self.reset_bot_mocks()

        self.mock_bots[0].pre_round.return_value = None
        self.mock_bots[1].pre_round.return_value = None
        self.mock_bots[2].pre_round.return_value = None
        self.mock_bots[2].action.return_value = Action.equip(2)
        self.mock_bots[2].aim.return_value = None

        result = self.engine.play_round()
        self.assertIsNone(result)

        for b in (0, 1):
            self.assertEqual(6, self.count_updates(self.mock_bots[b], None))

            # for preround, action, aim
            self.assertEqual(
                3,
                self.count_updates(self.mock_bots[b], OtherUpdateType.TURN_PHASE_START),
            )
            # for action = equip
            self.assertEqual(1, self.count_updates(self.mock_bots[b], ActionType.EQUIP))
            self.assertEqual(
                1, self.count_updates(self.mock_bots[b], OtherUpdateType.CARD_FLIP)
            )
            # for the aim
            self.assertEqual(1, self.count_updates(self.mock_bots[b], ActionType.PASS))

        self.assertEqual(7, self.count_updates(self.mock_bots[2], None))

        # for preround, action, aim
        self.assertEqual(
            3, self.count_updates(self.mock_bots[2], OtherUpdateType.TURN_PHASE_START)
        )
        # for action = equip
        self.assertEqual(1, self.count_updates(self.mock_bots[2], ActionType.EQUIP))
        self.assertEqual(
            1, self.count_updates(self.mock_bots[2], OtherUpdateType.CARD_FLIP)
        )
        self.assertEqual(
            1, self.count_updates(self.mock_bots[2], OtherUpdateType.EQUIP_RESULT)
        )
        # for the aim
        self.assertEqual(1, self.count_updates(self.mock_bots[2], ActionType.PASS))

        self.assertEqual(self.engine.state[1].equipment, EquipmentCard.BLACKMAIL)
        self.assertEqual(self.engine.state[2].equipment, EquipmentCard.SWAP)
        self.assertNotIn(EquipmentCard.BLACKMAIL, self.engine.equipment)
        self.assertNotIn(EquipmentCard.SWAP, self.engine.equipment)

    def test_round_4(self):
        self.test_round_3()
        self.reset_bot_mocks()

        self.mock_bots[0].pre_round.return_value = None
        self.mock_bots[1].pre_round.side_effect = [
            EquipmentConsumption.blackmail(2),
            None,
        ]
        self.mock_bots[2].pre_round.return_value = None
        self.mock_bots[0].action.return_value = Action.arm_and_aim(2, 2)
        self.mock_bots[0].aim.return_value = None

        result = self.engine.play_round()
        self.assertIsNone(result)

        for b in (0, 1, 2):
            self.assertEqual(7, self.count_updates(self.mock_bots[b], None))

            # for preround, action, aim
            self.assertEqual(
                3,
                self.count_updates(self.mock_bots[b], OtherUpdateType.TURN_PHASE_START),
            )
            # for blackmail
            self.assertEqual(
                1, self.count_updates(self.mock_bots[b], OtherUpdateType.EQUIPMENT_CARD)
            )
            # for action = arm
            self.assertEqual(
                1, self.count_updates(self.mock_bots[b], ActionType.ARM_AND_AIM)
            )
            self.assertEqual(
                1, self.count_updates(self.mock_bots[b], OtherUpdateType.CARD_FLIP)
            )

            # for the aim
            self.assertEqual(1, self.count_updates(self.mock_bots[b], ActionType.PASS))

        self.assertEqual(self.engine.state[1].equipment, None)
        self.assertEqual(self.engine.state[2].equipment, EquipmentCard.SWAP)
        self.assertEqual(self.engine.state[0].gun, PlayerGunState(True, 2))

        self.assertIn(EquipmentCard.BLACKMAIL, self.engine.equipment)
        self.assertNotIn(EquipmentCard.SWAP, self.engine.equipment)
        self.assertEqual(3, self.engine.gun_count)
        self.assertEqual(
            self.mock_bots[2].integrity_cards,
            [IntegrityCard.BAD_COP, IntegrityCard.BAD_COP, IntegrityCard.KINGPIN],
        )
        self.assertEqual(
            self.engine.state[2].integrity_cards,
            [
                PlayerIntegrityCardState(card=IntegrityCard.BAD_COP, face_up=False),
                PlayerIntegrityCardState(card=IntegrityCard.BAD_COP, face_up=False),
                PlayerIntegrityCardState(card=IntegrityCard.KINGPIN, face_up=True),
            ],
        )

    def test_round_5(self):
        self.test_round_4()
        self.reset_bot_mocks()

        self.mock_bots[0].pre_round.return_value = None
        self.mock_bots[1].pre_round.return_value = None
        self.mock_bots[2].pre_round.side_effect = [
            EquipmentConsumption.swap(1, 2, 2, 1),
            None,
        ]
        # flipping over a card that's already been flipped over
        self.mock_bots[1].action.return_value = Action.equip(1)
        self.mock_bots[1].aim.return_value = None

        result = self.engine.play_round()
        self.assertIsNone(result)

        for b in (0, 1, 2):
            self.assertEqual(8, self.count_updates(self.mock_bots[b], None))

            # for preround, action, aim
            self.assertEqual(
                3,
                self.count_updates(self.mock_bots[b], OtherUpdateType.TURN_PHASE_START),
            )
            # for swap
            self.assertEqual(
                1, self.count_updates(self.mock_bots[b], OtherUpdateType.EQUIPMENT_CARD)
            )
            # for action = equip
            self.assertEqual(1, self.count_updates(self.mock_bots[b], ActionType.EQUIP))
            self.assertEqual(
                1,
                self.count_updates(
                    self.mock_bots[b], OtherUpdateType.ROLLBACK_INCLUDING
                ),
            )
            # ++ for the aim
            self.assertEqual(2, self.count_updates(self.mock_bots[b], ActionType.PASS))

        self.assertEqual(self.engine.state[1].equipment, None)
        self.assertEqual(self.engine.state[2].equipment, None)
        self.assertEqual(self.engine.state[0].gun, PlayerGunState(True, 2))

        self.assertIn(EquipmentCard.BLACKMAIL, self.engine.equipment)
        self.assertIn(EquipmentCard.SWAP, self.engine.equipment)

        self.assertEqual(3, self.engine.gun_count)
        self.assertEqual(
            self.mock_bots[2].integrity_cards,
            [IntegrityCard.BAD_COP, IntegrityCard.AGENT, IntegrityCard.KINGPIN],
        )
        self.assertEqual(
            self.engine.state[2].integrity_cards,
            [
                PlayerIntegrityCardState(card=IntegrityCard.BAD_COP, face_up=False),
                PlayerIntegrityCardState(card=IntegrityCard.AGENT, face_up=False),
                PlayerIntegrityCardState(card=IntegrityCard.KINGPIN, face_up=True),
            ],
        )

        self.assertEqual(
            self.mock_bots[1].integrity_cards,
            [IntegrityCard.BAD_COP, IntegrityCard.BAD_COP, IntegrityCard.BAD_COP],
        )
        self.assertEqual(
            self.engine.state[1].integrity_cards,
            [
                PlayerIntegrityCardState(card=IntegrityCard.BAD_COP, face_up=False),
                PlayerIntegrityCardState(card=IntegrityCard.BAD_COP, face_up=True),
                PlayerIntegrityCardState(card=IntegrityCard.BAD_COP, face_up=False),
            ],
        )

    def test_round_6(self):
        self.test_round_5()
        self.reset_bot_mocks()

        self.mock_bots[0].pre_round.return_value = None
        self.mock_bots[1].pre_round.return_value = None
        self.mock_bots[2].pre_round.return_value = None

        # flipping over a card that's already been flipped over
        self.mock_bots[2].action.return_value = None
        self.mock_bots[2].aim.return_value = None

        result = self.engine.play_round()
        self.assertEqual(result, WinCondition.AGENT_IS_KINGPIN)

    def count_updates(self, mock_bot, updateType: ActionType | OtherUpdateType = None):
        count = 0
        for call in mock_bot.on_board_update.mock_calls:
            if updateType is None:
                count += 1
            elif call.args[0].type == updateType:
                count += 1
        return count
