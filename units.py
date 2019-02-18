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


@attr.s
class Unit:
    mele_specs = attr.ib(AttackSpecs(0, 0, 0))
    range_specs = attr.ib(AttackSpecs(0, 0, 0))
    # unit hp is a list of health points for each troop member
    hp = attr.ib([1])

    def _attack(self, target, attack_specs, near_hero=False, distance=0, cover=False):
        if distance > attack_specs.max_distance:
            return 0

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

        self._apply_damage(target, damage)
        return damage

    def _apply_damage(self, target, damage):
        for i, hp in enumerate(target.hp):
            if hp < damage:
                target.hp[i] = 0
                damage -= hp
            else:
                target.hp[i] -= damage
                damage = 0

            if damage == 0:
                break


    def mele_attack(self, target, near_hero=False):
        return self._attack(target, self.mele_specs, near_hero)

    def range_attack(self, target, distance, cover=False, near_hero=False):
        return self._attack(target, self.range_specs, near_hero, distance, cover)


@attr.s
class Hero(Unit):
    mele_specs = attr.ib(AttackSpecs(2, 1, 0))
    range_specs = attr.ib(AttackSpecs(2, 0, 24))
    hp = attr.ib([3])


@attr.s
class Terminator(Unit):
    mele_specs = attr.ib(AttackSpecs(2, 2, 0))
    range_specs = attr.ib(AttackSpecs(4, 2, 24))
    hp = attr.ib([3])


@attr.s
class RegularMarines(Unit):
    regular_soldiers = attr.ib(4)
    mele_specs = attr.ib(init=False)
    range_specs = attr.ib(init=False)
    hp = attr.ib(init=False)

    def __attrs_post_init__(self):
        self.mele_specs = AttackSpecs(self.regular_soldiers, 0, 0)
        self.range_specs = AttackSpecs(self.regular_soldiers, 0, 24)
        self.hp = [1 for x in range(self.regular_soldiers) ]


@attr.s
class LaserMarines(RegularMarines):
    """Only use this class is special soldier is still alive"""
    special_weapon_specs = attr.ib(AttackSpecs(1, 4, 48))

    def __attrs_post_init__(self):
        self.mele_specs = AttackSpecs(self.regular_soldiers + 1, 0, 0)
        self.hp = [1 for x in range(self.regular_soldiers + 1)]

    def special_range_attack(self, distance, cover, near_hero):
        pass


@attr.s
class MissileMarines(LaserMarines):
    special_weapon_specs = attr.ib(AttackSpecs(1, 0, 48))


@attr.s
class AssaultMarines(Unit):
    regular_soldiers = attr.ib(5)
    mele_specs = attr.ib(init=False)
    range_specs = attr.ib(init=False)
    hp = attr.ib(init=False)

    def __attrs_post_init__(self):
        self.mele_specs = AttackSpecs(2 * self.regular_soldiers, 1, 0)
        self.range_specs = AttackSpecs(self.regular_soldiers, 1, 12)
        self.hp = [1 for x in range(self.regular_soldiers)]


@attr.s
class Dreadnought(Unit):
    mele_specs = attr.ib(AttackSpecs(3, 4, 0))
    hp = attr.ib([10])

    def range_attack(self, distance, cover, near_hero):
        if distance <=12:
            self.range_specs = AttackSpecs(6, 1, 12)
        else:
            self.range_specs = AttackSpecs(4, 1, 24)

        return self._attack(distance, cover, near_hero, self.range_specs)
