import enum
from dataclasses import dataclass
from typing import Optional, List, Any, Literal, Tuple, Dict


'''
Rules for the game can be found at:
https://upload.snakesandlattes.com/rules/g/GoodCopBadCop.pdf
'''

# BEGIN: Internal-code, do not touch!

Player = int
Card = int


class RoleType(enum.Enum):
    GOOD = 0
    BAD = 1
    UNKNOWN = 2 # a special type - only available through game-state


@dataclass
class Role:
    name: str
    freq: int # used so you know how many of that type of card there is
    type: RoleType


# the different types of roles available - will be dealt randomly
class IntegrityCard(enum.Enum):
    KINGPIN = Role('Kingpin', 1, RoleType.BAD)
    AGENT = Role('Agent', 1, RoleType.GOOD)
    GOOD_COP = Role('Good Cop', 12, RoleType.GOOD)
    BAD_COP = Role('Bad Cop', 10, RoleType.BAD)

    # this will never be in your hand, this only comes in when you're looking at
    # someone else's card
    UNKNOWN = Role('Unknown', 24, RoleType.UNKNOWN)


@dataclass
class EquipmentDesc:
    name: str
    desc: str


# the different types of equipment cards
class EquipmentCard(enum.Enum):
    TASER = EquipmentDesc(
        'Taser',
        'Steal someones gun'
    )
    SMOKE_GRENADE = EquipmentDesc(
        'Smoke Grenade',
        'Reverse the turn order'
    )
    DEFIBRILLATOR = EquipmentDesc(
        'Defibrillator',
        'Revive a fallen comrade'
    )
    BLACKMAIL = EquipmentDesc(
        'Blackmail',
        'Flip bad-cops to good and vice-versa'
    )
    POLYGRAPH = EquipmentDesc(
        'Polygraph',
        'Show your cards to a player, and see all their cards'
    )
    TRUTH_SERUM = EquipmentDesc(
        'Truth Serum',
        'Pick any players face-down card and flip it over'
    )
    AUDIT = EquipmentDesc(
        'Audit',
        'Pick two cards from two players to inspect'
    )
    EVIDENCE_BAG = EquipmentDesc(
        'Evidence bag',
        'The last card that was inspected has to be flipped over'
    )
    SWAP = EquipmentDesc(
        'Swap',
        'Swap any two cards between two players'
    )
    GUN_CONTROL = EquipmentDesc(
        'Gun control',
        'Interrupt a firing gun to have them pick another player'
    )
    PLANTED_EVIDENCE = EquipmentDesc(
        'Planted evidence',
        'Investigate one face-down card from any players holding a gun'
    )


# used to describe the use of an equipment card, includes the equipment card itself
# as well as any metadata (e.g. target-player etc). Use the utility methods instead of
# constructing the class yourself.
@dataclass
class EquipmentConsumption:
    equipment_card: EquipmentCard
    constraint: Any

    @staticmethod
    def taser(target: Player) -> 'EquipmentConsumption':
        return EquipmentConsumption(EquipmentCard.TASER, target)
    
    @staticmethod
    def smoke_grenade() -> 'EquipmentConsumption':
        return EquipmentConsumption(EquipmentCard.SMOKE_GRENADE, None)
    
    @staticmethod
    def defibrillator(target: Player) -> 'EquipmentConsumption':
        return EquipmentConsumption(EquipmentCard.DEFIBRILLATOR, target)

    @staticmethod
    def blackmail(target: Player) -> 'EquipmentConsumption':
        return EquipmentConsumption(EquipmentCard.BLACKMAIL, target)

    @staticmethod
    def polygraph(target: Player) -> 'EquipmentConsumption':
        return EquipmentConsumption(EquipmentCard.POLYGRAPH, target)

    @staticmethod
    def truth_serum(target: Player, card: Card) -> 'EquipmentConsumption':
        return EquipmentConsumption(EquipmentCard.TRUTH_SERUM, [target, card])

    @staticmethod
    def audit(target1: Player, card1: Card, target2: Player, card2: Card) -> 'EquipmentConsumption':
        return EquipmentConsumption(EquipmentCard.AUDIT, [[target1, card1], [target2, card2]])

    @staticmethod
    def evidence_bag() -> 'EquipmentConsumption':
        return EquipmentConsumption(EquipmentCard.EVIDENCE_BAG, None)

    @staticmethod
    def swap(target1: Player, card1: Card, target2: Player, card2: Card) -> 'EquipmentConsumption':
        return EquipmentConsumption(EquipmentCard.SWAP, [[target1, card1], [target2, card2]])

    @staticmethod
    def gun_control(target: Player) -> 'EquipmentConsumption':
        return EquipmentConsumption(EquipmentCard.GUN_CONTROL, target)

    @staticmethod
    def planted_evidence(targets: List[Tuple[Player, Card]]) -> 'EquipmentConsumption':
        return EquipmentConsumption(EquipmentCard.PLANTED_EVIDENCE, targets)


class ActionType(enum.Enum):
    INVESTIGATE = 0
    EQUIP = 1
    ARM = 2
    SHOOT = 3


# used to describe taking an action - includes the action itself, as well
# as any metadata e.g. the target player for a shot. Use the utility methods
# instead of constructing the class yourself
@dataclass
class Action:
    type: ActionType
    metadata: Any

    @staticmethod
    def investigate(player: Player, card: Card) -> 'Action':
        return Action(ActionType.INVESTIGATE, [player, card])
    
    @staticmethod
    def equip():
        return Action(ActionType.EQUIP, None)
    
    @staticmethod
    def aim(player: Player):
        return Action(ActionType.AIM, player)
    
    @staticmethod
    def shoot():
        return Action(ActionType.SHOOT, None)


# describes the current game-turn-phase
class TurnPhase(enum.Enum):
    '''
    This pre-round is used to resolve any equipment cards that are played before the
    current players round. Only equipment cards can be played in this round.
    '''
    PRE_ROUND = 0

    '''
    In the action round, only the player who's turn it is may make a move.
    They may:
    1/ investigate the card of another player
    2/ take an equipment card - they will need to flip a face-down card
    3/ arm themselves with a gun - they will need to flip a face-down card, and take aim
    4/ shoot if they previously had a gun - the player who was shot will have to turn cards
        face-up and return their equipment cards
    '''
    ACTION = 1

    ''''
    In this phase of the game - any interrupts to the declared action can be played. 
    '''
    ACTION_INTERRUPT = 2

    '''
    In the correction phase - if the interrupt stopped the action from happening, an updated action can be performed.
    Only the player who's turn it is can play a correction.
    '''
    ACTION_CORRECTION = 3

    '''
    In the aim phase, a player who has a gun, and who's turn it is, can pick/change who to aim it as.
    '''
    AIM = 4


# describes other updates (not caused by taking actions)
class OtherUpdateType(enum.Enum):
    EQUIPMENT_CARD = 0
    CARD_FLIP = 1
    TURN_PHASE_START = 2
    SWAP = 3
    INVESTIGATION_RESULT = 4


# describes any game-state updates, either from actions or other updates
# includes metadata on the event
@dataclass
class Update:
    type: ActionType | OtherUpdateType
    actor: Player | None
    data: Any

    @staticmethod
    def action(actor: Player, action: Action) -> 'Update':
        return Update(action.type, actor, action)
    
    @staticmethod
    def play_equipment_card(actor: Player, equipment_consumption: EquipmentConsumption) -> 'Update':
        return Update(OtherUpdateType.EQUIPMENT_CARD, actor, equipment_consumption)

    @staticmethod
    def flip_card(
        actor: Player,
        card: Card,
        value: IntegrityCard,
        trigger: Literal[ActionType.EQUIP, EquipmentCard.EVIDENCE_BAG, EquipmentCard.TRUTH_SERUM]
    ) -> 'Update':
        return Update(
            OtherUpdateType.CARD_FLIP,
            actor,
            {
                'card': card,
                'value': value,
                'trigger': trigger
            }
        )

    @staticmethod
    def game_phase_start(turn_phase: TurnPhase) -> 'Update':
        return Update(
            OtherUpdateType.TURN_PHASE_START,
            None,
            turn_phase
        )

    @staticmethod
    def investigation_result(actor: Player, target: Player, card: Card, value: IntegrityCard) -> 'Update':
        return Update(
            OtherUpdateType.INVESTIGATION_RESULT,
            actor,
            {
                'target': target,
                'card': card,
                'value': value
            }
        )


# a utility class to get the current-state of the game
class GameState:
    def current_player() -> Player:
        pass

    def current_table_state() -> Dict[Player, Dict[Card, IntegrityCard]]:
        pass

    def update_history() -> List[Update]:
        pass

    def current_game_turn_phase() -> TurnPhase:
        pass


class BotTemplate:

    def __init__(
        self,
        integrity_cards: List[IntegrityCard],
        num_players: int,
        player_number: Player,
        game: GameState) -> 'BotTemplate':

        self._integrity_cards = integrity_cards
        self.num_players = num_players
        self.player_number = player_number
        self.game = game

    @property
    def integrity_cards(self) -> List[IntegrityCard]:
        return self._integrity_cards

    @integrity_cards.setter
    def integrity_cards(self, value: List[IntegrityCard]) -> None:
        self._integrity_cards = value

    def pre_round(self) -> Optional[EquipmentConsumption]:
        # TODO: add validation for pre-round
        return self._pre_round()

    def action(self) -> Action:
        # TODO: add validation for valid actions
        return self._action()

    def action_interrupt(self) -> Optional[EquipmentConsumption]:
        # TODO: add validation for valid interrupts
        return self._action_interrupt()
    
    def action_correction(self, prev_action: Action) -> Action:
        new_action = self._action_correction(prev_action)
        if new_action == prev_action:
            raise ValueError('You cannot play the same action again')
        return new_action
    
    def aim(self) -> Optional[Action]:
        # TODO: Add validation for the aim event
        return self._aim()
    
    # END: Internal-code, do not touch!

    def _pre_round(self) -> Optional[EquipmentConsumption]:
        return None

    def _action(self) -> Action:
        return Action.equip()

    def _action_interrupt(self) -> Optional[EquipmentConsumption]:
        pass

    def _action_correction(self, prev_action: Action) -> Action:
        pass

    def _aim(self) -> Optional[Action]:
        pass

    def on_board_update(self, update: Update) -> None:
        pass