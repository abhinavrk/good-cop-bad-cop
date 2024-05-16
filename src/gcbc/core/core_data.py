import enum
from dataclasses import dataclass
from typing import Dict, List, Optional

"""
Rules for the game can be found at:
https://upload.snakesandlattes.com/rules/g/GoodCopBadCop.pdf
"""

Player = int
Card = int


class RoleType(enum.Enum):
    GOOD = 0
    BAD = 1
    UNKNOWN = 2  # a special type - only available through game-state


@dataclass
class Role:
    name: str
    freq: int  # used so you know how many of that type of card there is
    type: RoleType


# the different types of roles available - will be dealt randomly
class IntegrityCard(enum.Enum):
    KINGPIN = Role("Kingpin", 1, RoleType.BAD)
    AGENT = Role("Agent", 1, RoleType.GOOD)
    GOOD_COP = Role("Good Cop", 12, RoleType.GOOD)
    BAD_COP = Role("Bad Cop", 10, RoleType.BAD)

    # this will never be in your hand, this only comes in when you're looking at
    # someone else's card
    UNKNOWN = Role("Unknown", 24, RoleType.UNKNOWN)

    def flip(self) -> "IntegrityCard":
        match self:
            case IntegrityCard.KINGPIN:
                return IntegrityCard.KINGPIN
            case IntegrityCard.AGENT:
                return IntegrityCard.AGENT
            case IntegrityCard.GOOD_COP:
                return IntegrityCard.BAD_COP
            case IntegrityCard.BAD_COP:
                return IntegrityCard.GOOD_COP
            case IntegrityCard.UNKNOWN:
                return IntegrityCard.UNKNOWN


@dataclass
class EquipmentDesc:
    name: str
    desc: str


# the different types of equipment cards
class EquipmentCard(enum.Enum):
    TASER = EquipmentDesc("Taser", "Steal someones gun")
    DEFIBRILLATOR = EquipmentDesc("Defibrillator", "Revive a fallen comrade")
    BLACKMAIL = EquipmentDesc("Blackmail", "Flip bad-cops to good and vice-versa")
    POLYGRAPH = EquipmentDesc(
        "Polygraph", "Show your cards to a player, and see all their cards"
    )
    SWAP = EquipmentDesc("Swap", "Swap any two cards between two players")
    UNKNOWN = EquipmentDesc(
        "Unknown",
        "used in game state to indicate the presence of an unknown equipment card",
    )


class ActionType(enum.Enum):
    INVESTIGATE = 0
    EQUIP = 1
    ARM_AND_AIM = 2
    AIM = 3
    SHOOT = 4
    PASS = 5


# describes the current game-turn-phase
class TurnPhase(enum.Enum):
    """
    This pre-round is used to resolve any equipment cards that are played before the
    current players round. Only equipment cards can be played in this round.
    """

    PRE_ROUND = 0

    """
    In the action round, only the player who's turn it is may make a move.
    They may:
    1/ investigate the card of another player
    2/ take an equipment card - they will need to flip a face-down card
    3/ arm themselves with a gun - they will need to flip a face-down card, and take aim
    4/ shoot if they previously had a gun - the player who was shot will have to turn cards
        face-up and return their equipment cards
    """
    ACTION = 1

    """
    In the aim phase, a player who has a gun, and who's turn it is, can pick/change who to aim it as.
    """
    AIM = 4


class PlayerHealthState:
    DEAD = 0
    ALIVE = 1
    WOUNDED = 2


@dataclass
class PlayerIntegrityCardState:
    card: IntegrityCard
    face_up: bool


@dataclass
class PlayerGunState:
    has_gun: bool
    aimed_at: Optional[Player]


@dataclass
class PlayerGameState:
    integrity_cards: List[PlayerIntegrityCardState]
    gun: PlayerGunState
    equipment: Optional[EquipmentCard]
    health: PlayerHealthState


@dataclass
class TableTopGameState:
    state: Dict[Player, PlayerGameState]

    def get_player_state(self, player: Player) -> PlayerGameState:
        return self.state[player]

    def is_player_alive(self, player: Player) -> bool:
        return self.state[player].health != PlayerHealthState.DEAD

    def get_player_health(self, player: Player) -> PlayerHealthState:
        return self.state[player].health

    def opaque_state(self) -> "TableTopGameState":
        return TableTopGameState(
            {
                player: PlayerGameState(
                    [
                        PlayerIntegrityCardState(
                            state.card if state.face_up else IntegrityCard.UNKNOWN,
                            state.face_up,
                        )
                        for state in player_state.integrity_cards
                    ],
                    PlayerGunState(player_state.gun.has_gun, player_state.gun.aimed_at),
                    EquipmentCard.UNKNOWN if player_state.equipment else None,
                    player_state.health,
                )
                for player, player_state in self.state.items()
            }
        )


@dataclass
class DeckState:
    equipment_cards: List[EquipmentCard]
    guns: int

    def get_gun(self) -> bool:
        if self.guns > 0:
            self.guns -= 1
            return True
        else:
            return False

    def return_gun(self):
        self.guns += 1

    def draw_equipment_card(self) -> Optional[EquipmentCard]:
        if len(self.equipment_cards) > 0:
            return self.equipment_cards.pop()
        else:
            return None

    def return_equipment_card(self, card: EquipmentCard):
        self.equipment_cards.insert(0, card)

    def opaque_state(self):
        return DeckState(
            [EquipmentCard.UNKNOWN for _ in range(len(self.equipment_cards))], self.guns
        )