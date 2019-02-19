import random

import attr


def throw_dices(dices=1):
    return random.choices(range(1, 7), k=dices)


@attr.s
class AttackSpecs:
    dices = attr.ib()
    armor_piercing = attr.ib()
    max_distance = attr.ib()
    damage_per_hit = attr.ib(1)
    can_a_hit_make_damage_to_multi_fighters = attr.ib(False)


@attr.s
class Fighter:
    mele_specs = attr.ib(AttackSpecs(0, 0, 0))
    range_specs = attr.ib(AttackSpecs(0, 0, 0))
    hp = attr.ib(1)

    def _attack(self, target, attack_specs, near_hero=False, distance=0, cover=False):
        # cannot atack a target which is out of range
        if distance > attack_specs.max_distance:
            return target

        # cannot atack a target with no fighters alive
        if not target.fighters:
            return target

        hit_floor = 3
        if cover:
            hit_floor += 1
        if near_hero:
            hit_floor -= 1

        attack_dices = throw_dices(attack_specs.dices)
        hits = len([d for d in attack_dices if d >= hit_floor])

        defense_floor = 2 + attack_specs.armor_piercing
        defense_dices = throw_dices(hits)
        damage = [attack_specs.damage_per_hit for d in defense_dices if d < defense_floor]

        target.get_damage(damage, attack_specs.can_a_hit_make_damage_to_multi_fighters)

        return target

    def mele_attack(self, target, near_hero=False):
        return self._attack(target, self.mele_specs, near_hero)

    def range_attack(self, target, distance, cover=False, near_hero=False):
        return self._attack(target, self.range_specs, near_hero, distance, cover)


@attr.s
class HeroFighter(Fighter):
    mele_specs = attr.ib(AttackSpecs(2, 1, 0))
    range_specs = attr.ib(AttackSpecs(2, 0, 24))
    hp = attr.ib(3)


@attr.s
class TerminatorFighter(Fighter):
    mele_specs = attr.ib(AttackSpecs(2, 2, 0))
    range_specs = attr.ib(AttackSpecs(4, 2, 24))
    hp = attr.ib(3)


@attr.s
class RegularMarineFighter(Fighter):
    mele_specs = attr.ib(AttackSpecs(1, 0, 0))
    range_specs = attr.ib(AttackSpecs(1, 0, 24))
    hp = attr.ib(1)


@attr.s
class LaserMarineFighter(RegularMarineFighter):
    range_specs = attr.ib(AttackSpecs(1, 4, 48, damage_per_hit=2))


@attr.s
class MissileMarineFighter(RegularMarineFighter):
    range_specs = attr.ib(AttackSpecs(1, 0, 48, damage_per_hit=3,
                                      can_a_hit_make_damage_to_multi_fighters=True))


@attr.s
class AssaultMarineFighter(Fighter):
    mele_specs = attr.ib(AttackSpecs(2, 1, 0))
    range_specs = attr.ib(AttackSpecs(1, 1, 12))
    hp = attr.ib(1)


@attr.s
class DreadnoughtFighter(Fighter):
    mele_specs = attr.ib(AttackSpecs(3, 4, 0))
    flame_specs = attr.ib(AttackSpecs(6, 1, 12))
    cannon_specs = attr.ib(AttackSpecs(4, 1, 24))

    hp = attr.ib(10)

    def range_attack(self, distance, cover, near_hero):
        if distance <=12:
            self.range_specs = self.flame_specs
        else:
            self.range_specs = self.cannon_specs

        return self._attack(distance, cover, near_hero, self.range_specs)
