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
        print('attack dices :', attack_dices)
        hits = len([d for d in attack_dices if d >= hit_floor])
        print('hit floor :', hit_floor)
        print('hits :', hits)

        defense_floor = 2 + attack_specs.armor_piercing
        defense_dices = throw_dices(hits)
        print('defense dices:', defense_dices)
        damage = [attack_specs.damage_per_hit for d in defense_dices if d < defense_floor]
        print('defense floor :', defense_floor)
        print('damage:', damage)

        print('target hp before:', target.hp)
        target.get_damage(damage, attack_specs.can_a_hit_make_damage_to_multi_fighters)
        print('damage :', damage)
        print('target hp after:', target.hp)

        return target

    def mele_attack(self, target, near_hero=False):
        return self._attack(target, self.mele_specs, near_hero)

    def range_attack(self, target, distance, cover=False, near_hero=False):
        return self._attack(target, self.range_specs, near_hero, distance, cover)


@attr.s
class Unit:
    fighters = attr.ib(factory=list)

    @property
    def hp(self):
        return [c.hp for c in self.fighters]

    def take_damage(self, damage, can_a_hit_make_damage_to_multi_fighters):
        if not self.fighters:
            raise Exception('You cannot attack a unit without fighters')
        if can_a_hit_make_damage_to_multi_fighters:
            reformed_damage = []
            for hit_damage in damage:
                reformed_damage.extend([1]*hit_damage)

            damage = reformed_damage

        for hit_damage in damage:
            first_fighter = self.fighters[0]
            if first_fighter.hp > hit_damage:
                first_fighter.hp -= hit_damage
            else:
                self.fighters.remove(first_fighter)
                if not self.fighters:
                    break


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
