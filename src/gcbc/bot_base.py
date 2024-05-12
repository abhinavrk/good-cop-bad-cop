import enum
from dataclasses import dataclass
from typing import Optional, List, Any, Literal


'''
Rules for the game can be found at:
https://upload.snakesandlattes.com/rules/g/GoodCopBadCop.pdf
'''


class RoleType(enum.Enum):
    GOOD = 0
    BAD = 1


@dataclass
class Role:
    name: str
    freq: int
    type: RoleType


class IntegrityCard(enum.Enum):
    KINGPIN = Role('Kingpin', 1, RoleType.BAD)
    AGENT = Role('Agent', 1, RoleType.GOOD)
    GOOD_COP = Role('Good Cop', 12, RoleType.GOOD)
    BAD_COP = Role('Bad Cop', 10, RoleType.BAD)


@dataclass
class Equipment:
    name: str
    desc: str


class EquipmentCard(enum.Enum):
    TASER = Equipment(
        'Taser',
        'Steal someones gun'
    )
    SMOKE_GRENADE = Equipment(
        'Smoke Grenade',
        'Reverse the turn order'
    )
    DEFIBRILLATOR = Equipment(
        'Defibrillator',
        'Revive a fallen comrade'
    )
    BLACKMAIL = Equipment(
        'Blackmail',
        'Flip bad-cops to good and vice-versa'
    )
    POLYGRAPH = Equipment(
        'Polygraph',
        'Show your cards to a player, and see all their cards'
    )
    TRUTH_SERUM = Equipment(
        'Truth Serum',
        'Pick any players face-down card and flip it over'
    )
    AUDIT = Equipment(
        'Audit',
        'Pick two cards from two players to inspect'
    )
    EVIDENCE_BAG = Equipment(
        'Evidence bag',
        'The last card that was inspected has to be flipped over'
    )
    SWAP = Equipment(
        'Swap',
        'Swap any two cards between two players'
    )
    GUN_CONTROL = Equipment(
        'Gun control',
        'Interrupt a firing gun to have them pick another player'
    )
    PLANTED_EVIDENCE = Equipment(
        'Planted evidence',
        'Investigate one face-down card from any players holding a gun'
    )


class ActionType(enum.Enum):
    INVESTIGATE = 0
    EQUIP = 1
    ARM = 2
    SHOOT = 3


@dataclass
class Action:
    '''
    Please do not create actions directly, instead use the utility methods
    in this class
    '''

    type: ActionType
    metadata: Any

    @staticmethod
    def investigate(player: int, card: int) -> 'Action':
        return Action(ActionType.INVESTIGATE, [player, card])
    
    @staticmethod
    def equip():
        return Action(ActionType.EQUIP, None)
    
    @staticmethod
    def aim(player):
        return Action(ActionType.AIM, player)
    
    @staticmethod
    def shoot():
        return Action(ActionType.SHOOT, None)


class GamePhase(enum.Enum):
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


class OtherUpdateType(enum.Enum):
    EQUIPMENT_CARD = 0
    CARD_FLIP = 1
    GAME_PHASE_START = 2


@dataclass
class Update:
    type: ActionType | OtherUpdateType
    actor: int | None
    data: Any

    @staticmethod
    def action(actor: int, action: Action) -> 'Update':
        return Update(action.type, actor, action)
    
    @staticmethod
    def play_equipment_card(actor: int, equipment_card: EquipmentCard) -> 'Update':
        return Update(OtherUpdateType.EQUIPMENT_CARD, actor, equipment_card)

    @staticmethod
    def flip_card(
        actor: int,
        card: int,
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
    def game_phase_start(game_phase: GamePhase) -> 'Update':
        return Update(
            OtherUpdateType.GAME_PHASE_START,
            None,
            game_phase
        )


class BotTemplate(object):

    # BEGIN: Internal-code, do not touch!

    def __init__(
        self,
        integrity_cards: List[IntegrityCard],
        num_players: int) -> 'BotTemplate':

        self._integrity_cards = integrity_cards
        self.num_players = num_players

    @property
    def integrity_cards(self) -> List[IntegrityCard]:
        return self._integrity_cards

    @integrity_cards.setter
    def integrity_cards(self, value: List[IntegrityCard]) -> None:
        self._integrity_cards = value

    def pre_round(self) -> Optional[EquipmentCard]:
        # TODO: add validation for pre-round
        return self._pre_round()

    def action(self) -> Action:
        # TODO: add validation for valid actions
        return self._action()

    def action_interrupt(self) -> Optional[EquipmentCard]:
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

    def _pre_round(self) -> Optional[EquipmentCard]:
        return None

    def _action(self) -> Action:
        return Action.equip()

    def _action_interrupt(self) -> Optional[EquipmentCard]:
        pass

    def _action_correction(self, prev_action: Action) -> Action:
        pass

    def _aim(self) -> Optional[Action]:
        pass

    def on_board_update(self, update: Update) -> None:
        pass