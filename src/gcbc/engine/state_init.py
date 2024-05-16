import random
from re import I
from typing import List

from gcbc.core.core_data import *


class GCBCInitalizer:
    @staticmethod
    def integrity_cards(num_players: int) -> List[IntegrityCard]:
        deck = [
            IntegrityCard.KINGPIN,
            IntegrityCard.AGENT,
        ]

        bad_players = num_players // 2  # round-down
        good_players = num_players - bad_players

        good_cards = good_players * 3 - 1
        bad_cards = bad_players * 3 - 1

        for _ in range(good_cards):
            deck.append(IntegrityCard.GOOD_COP)

        for _ in range(bad_cards):
            deck.append(IntegrityCard.BAD_COP)

        return deck

    @staticmethod
    def build_game_state(num_players: int) -> TableTopGameState:
        deck = GCBCInitalizer.integrity_cards(num_players)
        random.shuffle(deck)

        table_top_state = {}

        for player in range(num_players):
            card1, card2, card3 = deck.pop(), deck.pop(), deck.pop()
            cards = [card1, card2, card3]

            table_top_state[player] = PlayerGameState(
                integrity_cards=[
                    PlayerIntegrityCardState(x, face_up=False) for x in cards
                ],
                gun=PlayerGunState(has_gun=False, aimed_at=None),
                equipment=None,
                health=PlayerHealthState.ALIVE,
            )

        return TableTopGameState(table_top_state)

    @staticmethod
    def build_deck(num_players: int) -> DeckState:
        return DeckState(
            equipment_cards=[x.value for x in EquipmentCard], guns=num_players // 2
        )
