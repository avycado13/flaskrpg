import random


class Item:
    def __init__(self, name: str, damage: float, health: float):
        self.name = name
        self.damage = damage
        self.health = health

    def take_damage(self, damage: float):
        self.health -= damage
        if self.health < 0:
            self.health = 0

    def __repr__(self):
        return f"Item(name={self.name}, damage={self.damage}, health={self.health})"


class Player:
    def __init__(self, attributes: dict, inventory: list[Item] = None, gold: int = 0):
        self.attributes = attributes
        self.inventory = inventory if inventory is not None else []
        self.gold = gold
        self.health = attributes.get("health", 100)

    def inventory_add(self, item: Item):
        self.inventory.append(item)

    def can_afford(self, cost: int) -> bool:
        return self.gold >= cost

    def spend_gold(self, cost: int):
        self.gold -= cost

    def take_damage(self, damage: float):
        self.health -= damage
        if self.health < 0:
            self.health = 0

    def attack(self, enemy: "Enemy"):
        total_damage = self.primary.damage if self.primary else self.inventory[0].damage
        enemy.take_damage(total_damage)
        self.primary.take_damage(random.randint(0, 3))
        return total_damage

    def set_primary(self, item: Item):
        if item in self.inventory:
            self.primary = item

    def set_healer(self, item: Item):
        if item in self.inventory:
            self.healer = item


class Enemy:
    def __init__(self, name: str, health: float, damage: float, reward: int):
        self.name = name
        self.health = health
        self.damage = damage
        self.reward = reward

    def attack(self, player: Player):
        player.take_damage(self.damage)

    def is_alive(self) -> bool:
        return self.health > 0

    def take_damage(self, damage: float):
        self.health -= damage
        if self.health < 0:
            self.health = 0

    def __repr__(self):
        return f"Enemy(name={self.name}, health={self.health}, damage={self.damage}, reward={self.reward})"


class Combat:
    def __init__(self, player: Player, enemy: Enemy):
        self.player = player
        self.enemy = enemy

    def player_turn(self):
        damage_dealt = self.player.attack(self.enemy)
        print(
            f"{self.player.attributes['name']} attacks {self.enemy.name} for {damage_dealt:.2f} damage."
        )

    def enemy_turn(self):
        if self.enemy.is_alive():
            self.enemy.attack(self.player)
            print(
                f"{self.enemy.name} attacks {self.player.attributes['name']} for {self.enemy.damage:.2f} damage."
            )

    def combat_round(self):
        if self.player.health > 0 and self.enemy.is_alive():
            self.player_turn()
            if self.enemy.is_alive():
                self.enemy_turn()

    def start(self):
        while self.player.health > 0 and self.enemy.is_alive():
            if input("Fight? (Y/n): ") == "Y":
                self.combat_round()

        if self.player.health <= 0:
            print(f"{self.player.attributes['name']} has been defeated!")
        else:
            print(f"{self.enemy.name} has been defeated!")
            self.player.gold += self.enemy.reward  # Reward for defeating an enemy
            
            return True


class Shop:
    def __init__(self, name:str, items: dict[Item, int], player: Player):
        self.items = items
        self.player = player
        self.name = name

    def buy(self, item: Item):
        cost = self.items[item]

        if not self.player.can_afford(cost):
            raise ValueError("Not enough gold to purchase this item.")

        self.player.spend_gold(cost)
        self.player.inventory_add(item)
        print(f"{self.player.attributes['name']} bought {item.name} for {cost} gold.")
        return item

    def list_items(self):
        return self.items


def main():
    # Create player
    player_attributes = {"name": "Hero", "health": 100}
    player = Player(attributes=player_attributes, gold=50)

    # Create items
    sword = Item("Sword", 10, 5)
    axe = Item("Axe", 15, 3)
    ax = Item("Ax", 0, 3)
    health_potion = Item("Health Potion", -10, float('inf'))  # Use special healing logic later

    # Create shops with items and costs as a single dictionary
    blacksmith_shop = Shop(items={sword: 20, axe: 30, ax: 5}, player=player)
    potion_shop = Shop(items={health_potion: 10}, player=player)

    # Create enemies
    goblin = Enemy("Goblin", health=30, damage=5, reward=10)
    troll = Enemy("Troll", health=50, damage=10, reward=15)

    # Game loop
    while True:
        action = input("Choose an action: (1) Fight (2) Shop (3) Exit: ")
        if action == "1":
            enemy = random.choice([goblin, troll])
            print(f"A wild {enemy.name} appears!")
            combat = Combat(player, enemy)
            combat.start()
        elif action == "2":
            shop_choice = input("Choose a shop: (1) Blacksmith (2) Potion Shop: ")
            if shop_choice == "1":
                print("Your Balance: " + str(player.gold))
                items = blacksmith_shop.list_items()
                print("Available items for sale:")
                for item, cost in items.items():
                    print(f"{item} - {cost} gold")
                item_id = int(input("Select an item to buy (enter item number): "))
                item = list(blacksmith_shop.items.keys())[item_id-1]
                try:
                    blacksmith_shop.buy(item)
                    if (
                        input(
                            "Would you like this Item to be set as the primary weapon? (Y/n): "
                        )
                        == "Y"
                    ):
                        player.set_primary(item)
                except Exception as e:
                    print(e)
            elif shop_choice == "2":
                print("Your Balance: " + str(player.gold))
                items = potion_shop.list_items()
                print("Available items for sale:")
                for item, cost in items.items():
                    print(f"{item} - {cost} gold")
                item_id = int(input("Select an item to buy (enter item number): "))
                item = list(potion_shop.items.keys())[item_id]
                try:
                    potion_shop.buy(item)
                except Exception as e:
                    print(e)
        elif action == "3":
            print("Exiting game.")
            break
        else:
            print("Invalid action. Try again.")


if __name__ == "__main__":
    main()
