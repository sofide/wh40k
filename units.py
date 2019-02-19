import attr

import fighters

@attr.s
class Unit:
    fighters = attr.ib(factory=list)

    @property
    def hp(self):
        return [c.hp for c in self.fighters]

    def mele_attack(self, target, near_hero=False):
        for fighter in self.fighters:
            fighter.mele_attack(target, near_hero)
        return target

    def range_attack(self, target, distance, cover=False, near_hero=False):
        for fighter in self.fighters:
            fighter.range_attack(target, distance, cover, near_hero)
        return target

    def get_damage(self, damage, can_a_hit_make_damage_to_multi_fighters):
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
class HeroUnit(Unit):
    fighters = attr.ib([fighters.HeroFighter()])


@attr.s
class TerminatorUnit(Unit):
    fighters = attr.ib([fighters.TerminatorFighter()])


@attr.s
class LaserMarinesUnit(Unit):
    fighters = attr.ib([fighters.RegularMarineFighter()]*4 + [fighters.LaserMarineFighter()])


@attr.s
class MissileMarinesUnit(Unit):
    fighters = attr.ib([fighters.RegularMarineFighter()]*4 + [fighters.MissileMarineFighter()])


@attr.s
class AssaultMarinesUnit(Unit):
    fighters = attr.ib([fighters.AssaultMarineFighter()]*5)


@attr.s
class DreadnoughtUnit(Unit):
    fighters = attr.ib([fighters.DreadnoughtFighter()])
