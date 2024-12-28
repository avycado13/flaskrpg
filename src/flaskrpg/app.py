from flask import Flask, render_template, request, redirect, url_for, session
import random

app = Flask(__name__)
app.secret_key = "secretkey"  # Required for session management



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
    def __init__(self, attributes: dict, inventory: list[Item,None] = None, gold: int = 0):
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

# Sample Data
items = {
    Item("Sword", damage=10, health=100): 50,
    Item("Staff", damage=8, health=80): 30,
    Item("Healing Potion", damage=0, health=50): 10
}

player = Player(attributes={"name": "Hero"}, gold=100)
shop = Shop(name="Armory", items=items, player=player)
enemy = Enemy(name="Goblin", health=50, damage=5, reward=20)  # Simple enemy example

combat_instance = None

@app.route('/')
def home():
    return redirect(url_for('shop'))

@app.route('/shop')
def shop():
    return render_template("shop.html", shop=shop)

@app.route('/buy/<item_name>')
def buy(item_name):
    item = next((i for i in shop.items if i.name == item_name), None)
    if item:
        try:
            shop.buy(item)
        except ValueError:
            return "Not enough gold!", 400
    return redirect(url_for('shop'))

@app.route('/player')
def player_page():
    return render_template("player.html", player=player)

@app.route('/set_primary/<item_name>')
def set_primary(item_name):
    item = next((i for i in player.inventory if i.name == item_name), None)
    if item:
        player.set_primary(item)
    return redirect(url_for('player_page'))

@app.route('/set_healer/<item_name>')
def set_healer(item_name):
    item = next((i for i in player.inventory if i.name == item_name), None)
    if item:
        player.set_healer(item)
    return redirect(url_for('player_page'))

@app.route('/combat')
def combat():
    global combat_instance, enemy
    if not combat_instance or not enemy.is_alive():
        # Create a new enemy if there's no active combat or if the previous enemy was defeated
        enemy = Enemy(name="Goblin", health=50, damage=5, reward=20)
        combat_instance = Combat(player, enemy)

    return render_template("combat.html", player=player, enemy=enemy)

@app.route('/attack')
def attack():
    global combat_instance
    if combat_instance and player.health > 0 and enemy.is_alive():
        combat_instance.player_turn()  # Player attacks enemy
        if enemy.is_alive():
            combat_instance.enemy_turn()  # Enemy attacks back if still alive

    if player.health <= 0:
        return redirect(url_for("game_over"))
    elif not enemy.is_alive():
        player.gold += enemy.reward  # Reward player for defeating the enemy
        return redirect(url_for("combat"))  # Start a new combat with a new enemy
    
    return redirect(url_for("combat"))

@app.route('/game_over')
def game_over():
    return "Game Over! You have been defeated."

if __name__ == '__main__':
    app.run(debug=True)
