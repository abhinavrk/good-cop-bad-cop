from gcbc.data_models import IntegrityCard
from gcbc.game_engine import GCBCInitalizer
import unittest as ut


class TestGCBCInitializer(ut.TestCase):
    def _test_player_deck_expectation(self, num_players, num_good, num_bad):
        deck = GCBCInitalizer.build_deck(num_players=num_players)

        self.assertEqual(num_players * 3, len(deck))
        self.assertIn(IntegrityCard.AGENT, deck)
        self.assertIn(IntegrityCard.KINGPIN, deck)

        good_cards = sum(1 for x in deck if x == IntegrityCard.GOOD_COP)
        bad_cards = sum(1 for x in deck if x == IntegrityCard.BAD_COP)

        self.assertEqual(
            num_good, good_cards, f"Expected {num_good} good cards, got {good_cards}"
        )
        self.assertEqual(
            num_bad, bad_cards, f"Expected {num_bad} bad cards, got {bad_cards}"
        )

    def test_player_deck_expectations(self):
        self._test_player_deck_expectation(num_players=4, num_good=5, num_bad=5)

        self._test_player_deck_expectation(num_players=5, num_good=8, num_bad=5)

        self._test_player_deck_expectation(num_players=6, num_good=8, num_bad=8)

        self._test_player_deck_expectation(num_players=7, num_good=11, num_bad=8)

        self._test_player_deck_expectation(num_players=8, num_good=11, num_bad=11)
