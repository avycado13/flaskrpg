from datetime import datetime, timezone
from flask import render_template, flash, redirect, url_for, request, g, \
    current_app
from flask_login import current_user, login_required
from flaskrpg.combat import bp
from flaskrpg.helpers import Enemy,Player,Combat

@bp.route('/combat')
def combat():
    global combat_instance, enemy
    if not combat_instance or not enemy.is_alive():
        # Create a new enemy if there's no active combat or if the previous enemy was defeated
        enemy = Enemy(name="Goblin", health=50, damage=5, reward=20)
        combat_instance = Combat(player, enemy)

    return render_template("combat.html", player=player, enemy=enemy)

@bp.route('/attack')
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

@bp.route('/game_over')
def game_over():
    return "Game Over! You have been defeated."