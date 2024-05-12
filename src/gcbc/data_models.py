import enum
from dataclasses import dataclass, field
from typing import Any, Dict, List, Literal, Optional
from uuid import uuid4, UUID

"""
Rules for the game can be found at:
https://upload.snakesandlattes.com/rules/g/GoodCopBadCop.pdf
"""

# BEGIN: Internal-code, do not touch!

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
    # these are eqipment cards I'm too lazy to implement right now
    # ---------------------
    # GUN_CONTROL = EquipmentDesc(
    #     "Gun control", "Interrupt a firing gun to have them pick another player"
    # )
    # SMOKE_GRENADE = EquipmentDesc("Smoke Grenade", "Reverse the turn order")
    # TRUTH_SERUM = EquipmentDesc(
    #     "Truth Serum", "Pick any players face-down card and flip it over"
    # )
    # AUDIT = EquipmentDesc("Audit", "Pick two cards from two players to inspect")
    # EVIDENCE_BAG = EquipmentDesc(
    #     "Evidence bag", "The last card that was inspected has to be flipped over"
    # )
    # PLANTED_EVIDENCE = EquipmentDesc(
    #     "Planted evidence",
    #     "Investigate one face-down card from any players holding a gun",
    # )
    UNKNOWN = EquipmentDesc(
        "Unknown",
        "used in game state to indicate the presence of an unknown equipment card",
    )


# used to describe the use of an equipment card, includes the equipment card itself
# as well as any metadata (e.g. target-player etc). Use the utility methods instead of
# constructing the class yourself.
@dataclass
class EquipmentConsumption:
    equipment_card: EquipmentCard
    constraint: Any

    @staticmethod
    def taser(steal_from: Player, aim_at: Player) -> "EquipmentConsumption":
        return EquipmentConsumption(EquipmentCard.TASER, [steal_from, aim_at])

    @staticmethod
    def defibrillator(target: Player) -> "EquipmentConsumption":
        return EquipmentConsumption(EquipmentCard.DEFIBRILLATOR, target)

    @staticmethod
    def blackmail(target: Player) -> "EquipmentConsumption":
        return EquipmentConsumption(EquipmentCard.BLACKMAIL, target)

    @staticmethod
    def polygraph(target: Player) -> "EquipmentConsumption":
        return EquipmentConsumption(EquipmentCard.POLYGRAPH, target)

    @staticmethod
    def swap(
        target1: Player, card1: Card, target2: Player, card2: Card
    ) -> "EquipmentConsumption":
        return EquipmentConsumption(
            EquipmentCard.SWAP, [[target1, card1], [target2, card2]]
        )

    # @staticmethod
    # def gun_control(target: Player) -> "EquipmentConsumption":
    #     return EquipmentConsumption(EquipmentCard.GUN_CONTROL, target)

    # @staticmethod
    # def smoke_grenade() -> "EquipmentConsumption":
    #     return EquipmentConsumption(EquipmentCard.SMOKE_GRENADE, None)

    # @staticmethod
    # def truth_serum(target: Player, card: Card) -> "EquipmentConsumption":
    #     return EquipmentConsumption(EquipmentCard.TRUTH_SERUM, [target, card])

    # @staticmethod
    # def audit(
    #     target1: Player, card1: Card, target2: Player, card2: Card
    # ) -> "EquipmentConsumption":
    #     return EquipmentConsumption(
    #         EquipmentCard.AUDIT, [[target1, card1], [target2, card2]]
    #     )

    # @staticmethod
    # def evidence_bag() -> "EquipmentConsumption":
    #     return EquipmentConsumption(EquipmentCard.EVIDENCE_BAG, None)

    # @staticmethod
    # def planted_evidence(targets: List[Tuple[Player, Card]]) -> "EquipmentConsumption":
    #     return EquipmentConsumption(EquipmentCard.PLANTED_EVIDENCE, targets)


class ActionType(enum.Enum):
    INVESTIGATE = 0
    EQUIP = 1
    ARM_AND_AIM = 2
    AIM = 3
    SHOOT = 4
    PASS = 5


# used to describe taking an action - includes the action itself, as well
# as any metadata e.g. the target player for a shot. Use the utility methods
# instead of constructing the class yourself
@dataclass
class Action:
    type: ActionType
    metadata: Any

    @staticmethod
    def investigate(player: Player, card: Card) -> "Action":
        return Action(ActionType.INVESTIGATE, [player, card])

    @staticmethod
    def equip(card_to_flip: Optional[Card]):
        return Action(ActionType.EQUIP, card_to_flip)

    @staticmethod
    def arm_and_aim(target: Player, card_to_flip: Optional[Card]):
        return Action(ActionType.ARM_AND_AIM, [target, card_to_flip])

    @staticmethod
    def aim(target: Player):
        return Action(ActionType.AIM, target)

    @staticmethod
    def shoot():
        return Action(ActionType.SHOOT, None)
    
    @staticmethod
    def passMove():
        return Action(ActionType.PASS, None)


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


# describes other updates (not caused by taking actions)
class OtherUpdateType(enum.Enum):
    EQUIPMENT_CARD = 0
    CARD_FLIP = 1
    TURN_PHASE_START = 2
    SWAP = 3
    INVESTIGATION_RESULT = 4
    ROLLBACK_INCLUDING = 5


# describes any game-state updates, either from actions or other updates
# includes metadata on the event
@dataclass
class Update:
    type: ActionType | OtherUpdateType
    actor: Player | None
    data: Any
    uuid: UUID = field(default_factory = uuid4)

    @staticmethod
    def action(actor: Player, action: Action) -> "Update":
        return Update(action.type, actor, action)

    @staticmethod
    def play_equipment_card(
        actor: Player, equipment_consumption: EquipmentConsumption
    ) -> "Update":
        return Update(OtherUpdateType.EQUIPMENT_CARD, actor, equipment_consumption)

    @staticmethod
    def flip_card(
        actor: Player,
        card: Card,
        value: IntegrityCard,
        trigger: Literal[
            ActionType.ARM_AND_AIM,
            ActionType.EQUIP,  # EquipmentCard.EVIDENCE_BAG, EquipmentCard.TRUTH_SERUM
        ],
    ) -> "Update":
        return Update(
            OtherUpdateType.CARD_FLIP,
            actor,
            {"card": card, "value": value, "trigger": trigger},
        )

    @staticmethod
    def game_phase_start(turn_phase: TurnPhase) -> "Update":
        return Update(OtherUpdateType.TURN_PHASE_START, None, turn_phase)

    @staticmethod
    def investigation_result(
        actor: Player, target: Player, card: Card, value: IntegrityCard
    ) -> "Update":
        return Update(
            OtherUpdateType.INVESTIGATION_RESULT,
            actor,
            {"target": target, "card": card, "value": value},
        )
    
    @staticmethod
    def rollback_move(move_uuid: UUID) -> "Update":
        # someone screwed up - so the last move is getting undone
        return Update(OtherUpdateType.ROLLBACK_INCLUDING, None, move_uuid)


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


TableTopGameState = Dict[Player, PlayerGameState]
