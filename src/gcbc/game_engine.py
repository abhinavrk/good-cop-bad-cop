from copy import deepcopy
import random
import time
from dataclasses import replace
from typing import List, Tuple

from gcbc.bot_base import BotTemplate
from gcbc.data_models import *


class WinCondition(enum.Enum):
    ONE_PLAYER_ALIVE = 0
    AGENT_DEAD = 1
    KINGPIN_DEAD = 2
    AGENT_IS_KINGPIN = 3


class GCBCInitalizer:
    @staticmethod
    def build_deck(num_players: int) -> List[IntegrityCard]:
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
    def setup_initial_assignment(num_players: int) -> TableTopGameState:
        deck = GCBCInitalizer.build_deck(num_players)
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

        return table_top_state


class GCBCGameEngine:

    @staticmethod
    def new_game(num_players: int) -> "GCBCGameEngine":
        table_top_state = GCBCInitalizer.setup_initial_assignment(num_players)
        return GCBCGameEngine(
            table_top_state,
            random.shuffle(
                [x.value for x in EquipmentCard if x != EquipmentCard.UNKNOWN]
            ),
        )

    def __init__(
        self,
        init_state: TableTopGameState,
        equipment: List[EquipmentCard],
        gun_count: int,
        bots: Dict[Player, BotTemplate],
    ) -> "GCBCGameEngine":

        # initial state variables
        self.state = init_state
        self.equipment = equipment
        self.gun_count = gun_count
        self.bots = bots

        # round variables
        self.current_player = 0
        self.turn_increment = 1
        self.current_phase = TurnPhase.PRE_ROUND

    def play_game(self):
        win_condition = None
        while win_condition is None:
            self.run_round()
            win_condition = self.win_condition()

        return win_condition

    def run_round(self):
        self.current_phase = TurnPhase.PRE_ROUND
        self.emit_global_update(Update.game_phase_start(TurnPhase.PRE_ROUND))

        blacklisted_pre_round = []
        run_preround = True
        while run_preround:
            run_preround = self.pre_round(blacklist=blacklisted_pre_round)

        self.current_phase = TurnPhase.ACTION
        self.emit_global_update(Update.game_phase_start(TurnPhase.ACTION))
        self.action()

        self.current_phase = TurnPhase.AIM
        self.emit_global_update(Update.game_phase_start(TurnPhase.AIM))

        self.aim()

        self.move_to_next_player()

    def win_condition(self):
        players = self.state.keys()
        # only one player alive
        num_players_alive = sum(1 for p in players if self.is_player_alive(p))
        if num_players_alive == 1:
            return WinCondition.ONE_PLAYER_ALIVE

        # agent/kingpin dead
        for p in players:
            if self.is_player_alive(p):
                if self.is_player_x(IntegrityCard.AGENT) and self.is_player_x(IntegrityCard.KINGPIN):
                    return WinCondition.AGENT_IS_KINGPIN
            else:
                if self.is_player_x(IntegrityCard.AGENT):
                    return WinCondition.AGENT_DEAD

                if self.is_player_x(IntegrityCard.KINGPIN):
                    return WinCondition.KINGPIN_DEAD
        
        return None

    def is_player_alive(self, player):
        return self.state[player].health != PlayerHealthState.DEAD

    def pre_round(self, blacklist) -> bool:
        cards: List[Tuple[float, Player, EquipmentConsumption]] = []
        for player, bot in self.bots.items():
            if not self.is_player_alive(player):
                continue
            if player in blacklist:
                # skip bad actors for this round
                continue

            s = time.time()
            card = bot.pre_round()
            e = time.time()
            if card is not None:
                cards.append((e - s, player, card))

        # so the fastest cards are at the end
        cards.sort(reverse=True)

        additional_round_needed = False
        if len(cards):
            additional_round_needed = True

            _, player, card = cards.pop()
            try:
                checkpoint_pre_round = self.checkpoint()
                update = Update.play_equipment_card(player, card)
                self.emit_global_update(update)
                self.enact_preround(player, card)
            except Exception as e:
                # someone screwed up with an invalid move, will
                # bypass their turn and will start again
                # pre-rounds can only change state - they cannot change the deck
                # or the tabletop in any other way
                self.emit_global_update(Update.rollback_move(update.uuid))
                self.restore_checkpoint(checkpoint_pre_round)
                blacklist.append(player)

        return additional_round_needed

    def enact_preround(self, actor: Player, card: EquipmentConsumption):
        self.update_state(actor, equipment=None)
        self.equipment.insert(0, card.equipment_card)

        match card.equipment_card:
            case EquipmentCard.TASER:
                steal_from, aim_at = card.constraint
                if steal_from == actor:
                    raise ValueError(f"Cannot use {card} on yourself")

                if aim_at == actor:
                    raise ValueError(f"Cannot aim at yourself")

                steal_from_state = self.state[steal_from]
                if not steal_from_state.gun.has_gun:
                    raise ValueError(
                        f"Player {steal_from} does not have a gun to steal"
                    )

                self.update_state(
                    steal_from,
                    gun=PlayerGunState(has_gun=False, aimed_at=None),
                )

                self.update_state(
                    actor,
                    gun=PlayerGunState(has_gun=True, aimed_at=aim_at),
                )

            case EquipmentCard.DEFIBRILLATOR:
                target = card.constraint
                if self.state[target].health != PlayerHealthState.DEAD:
                    raise ValueError(f"Cannot revive a player who's not dead")

                self.update_state(target, health=PlayerHealthState.ALIVE)

            case EquipmentCard.BLACKMAIL:
                target = card.constraint
                target_cards = self.state[target].integrity_cards
                new_integrity_cards = [
                    PlayerIntegrityCardState(self._invert(x.card), face_up=x.face_up)
                    for x in target_cards
                ]
                self.update_state(target, integrity_cards=new_integrity_cards)

            case EquipmentCard.POLYGRAPH:
                target = card.constraint
                if target == actor:
                    raise ValueError("cannot use polygraph on yourself")

                self.emit_investigation_result(actor, target, 0)
                self.emit_investigation_result(actor, target, 1)
                self.emit_investigation_result(actor, target, 2)

                self.emit_investigation_result(target, actor, 0)
                self.emit_investigation_result(target, actor, 1)
                self.emit_investigation_result(target, actor, 2)

            case EquipmentCard.SWAP:
                target1, card1, target2, card2 = card.constraint
                if target1 == target2:
                    raise ValueError(f"cannot swap cards between the same player")

                card1_val = self.state[target1].integrity_cards[card1]
                card2_val = self.state[target2].integrity_cards[card2]

                self.state[target1].integrity_cards[card1] = card2_val
                self.state[target2].integrity_cards[card2] = card1_val

                self.bots[target1].integrity_cards = [
                    x.card for x in self.state[target1].integrity_cards
                ]

                self.bots[target2].integrity_cards = [
                    x.card for x in self.state[target2].integrity_cards
                ]

            case _:
                raise ValueError(f"Cannot play {card} in preround")

    def update_state(self, player: Player, **changes: Any):
        self.state[player] = replace(self.state[player], **changes)

    @staticmethod
    def _invert(card: IntegrityCard) -> IntegrityCard:
        if card == IntegrityCard.BAD_COP:
            return IntegrityCard.GOOD_COP
        elif card == IntegrityCard.GOOD_COP:
            return IntegrityCard.BAD_COP
        else:
            return card

    def emit_investigation_result(self, recipient: Player, target: Player, card: Card):
        target_state = self.state[target]
        card_val = target_state.integrity_cards[card]
        update = Update.investigation_result(recipient, target, card, card_val.card)
        self.bots[recipient].on_board_update(update)

    def emit_global_update(self, update: Update):
        for _, bot in self.bots.items():
            bot.on_board_update(update)

    def face_down_for_player(self, player: Player) -> List[Card]:
        cards = self.state[player].integrity_cards
        return [i for i, x in enumerate(cards) if x.face_up == False]

    def do_flip_card(self, player: Player, card: Card):
        cards = deepcopy(self.state[player].integrity_cards)
        cards[card] = replace(cards[card], face_up=True)
        self.update_state(player, integrity_cards=cards)

    def flip_card(self, player: Player, card_to_flip: Card, trigger: ActionType):
        face_down_cards = self.face_down_for_player(player)
        if len(face_down_cards) == 0:
            return
        elif card_to_flip in face_down_cards:
            self.do_flip_card(self.current_player, card_to_flip)
            self.emit_global_update(
                Update.flip_card(
                    actor=player,
                    card=card_to_flip,
                    value=self.state[player].integrity_cards[card_to_flip].card,
                    trigger=trigger,
                )
            )
        else:
            raise ValueError("You have to flip a facedown card")

    def action(self):
        update = Update.action(self.current_player, action)
        self.emit_global_update(update)
        checkpoint_action = self.checkpoint()
        try:
            action = self.bots[self.current_player].action()
            self.enact_action(action)
        except Exception as e:
            self.emit_global_update(Update.rollback_move(update.uuid))
            self.restore_checkpoint(checkpoint_action)
            # at this point, this is going to be a move-pass
            update = Update.action(self.current_player, Action.passMove())
            self.emit_global_update(update)

    def enact_action(self, action: Action):
        match action.type:
            case ActionType.INVESTIGATE:
                target_player, target_card = action.metadata
                self.emit_investigation_result(
                    self.current_player, target_player, target_card
                )
            case ActionType.EQUIP:
                assert len(self.equipment) > 0, "no equipment cards to retrieve"
                card_to_flip = action.metadata
                self.flip_card(self.current_player, card_to_flip, ActionType.EQUIP)
                ec = self.equipment.pop()
                self.update_state(self.current_player, equipment=ec)
            case ActionType.ARM_AND_AIM:
                assert self.gun_count > 0, "no guns to arm and aim"
                assert (
                    self.state[self.current_player].gun.has_gun == False
                ), "cannot take a gun while you have a gun"

                self.gun_count -= 1
                target, card_to_flip = action.metadata
                self.flip_card(
                    self.current_player, card_to_flip, ActionType.ARM_AND_AIM
                )
                self.update_state(
                    self.current_player,
                    gun=PlayerGunState(has_gun=True, aimed_at=target),
                )
            case ActionType.SHOOT:
                target = action.metadata
                assert (
                    self.state[target].health != PlayerHealthState.DEAD
                ), "cannot shoot someone who's already dead"

                if not self.is_player_special(target):
                    self.update_state(target, health=PlayerHealthState.DEAD)
                else:
                    phealth = self.state[target].health
                    if phealth == PlayerHealthState.WOUNDED:
                        self.update_state(target, health=PlayerHealthState.DEAD)
                    else:
                        self.update_state(target, health=PlayerHealthState.WOUNDED)

    def is_player_special(self, player: Player) -> bool:
        return self.is_player_x(player, IntegrityCard.AGENT) or self.is_player_x(
            player, IntegrityCard.KINGPIN
        )

    def is_player_x(self, player: Player, x: IntegrityCard) -> bool:
        player_cards = [x.card for x in self.state[player].integrity_cards]
        if x in player_cards:
            return True
        return False

    def aim(self):
        if not self.state[self.current_player].gun.has_gun:
            update = Update.action(self.current_player, Action.passMove())
            self.emit_global_update(update)
            return

        action = self.bots[self.current_player].aim()
        if action is None:
            update = Update.action(self.current_player, Action.passMove())
            self.emit_global_update(update)
            return
        
        try:
            update = Update.action(self.current_player, action)
            self.emit_global_update(update)
            checkpoint_aim = self.checkpoint()
            assert action.type == ActionType.AIM, "can only aim during the aim phase"

            target = action.metadata
            self.update_state(self.current_player, gun=PlayerGunState(True, target))
        except Exception as e:
            self.emit_global_update(Update.rollback_move(update.uuid))
            self.restore_checkpoint(checkpoint_aim)
            # do nothing and skip

    def checkpoint(self):
        return [
            deepcopy(self.state),
            deepcopy(self.equipment),
            deepcopy(self.gun_count),
            deepcopy(self.current_player),
            deepcopy(self.current_phase),
            deepcopy(self.turn_increment),
        ]
    
    def restore_checkpoint(self, checkpoint):
        self.state = checkpoint[0]
        self.equipment = checkpoint[1]
        self.gun_count = checkpoint[2]
        self.current_player = checkpoint[3]
        self.current_phase = checkpoint[4]
        self.turn_increment = checkpoint[5]