#include <stdio.h>
#include <stdlib.h>
#include <time.h>

int main()
{
    srand(time(NULL));
    char weapon; //S=sword  W=magic wand
    char location; //P=plains  F=forest
    int enemy; //0=goblin  1=goblin shaman   2=bear  3=witch     4=kobold  5=cave troll
    int enemy_health, enemy_level, enemy_max_damage;
    int health = 100;
    int health_max = 100;
    int mana = 50;
    int mana_max = 50;
    int level = 1;
    int exp = 0;
    int exp_max = 100;
    int gold = 0;
    int run_away = 0;
    int health_potions = 0;
    int mana_potions = 0;
    int damage, healing, success, reward;
    char action, magic;
    printf("Choose your weapon: [S]word or Magic [W]and.\n");
    scanf(" %c", &weapon);
    if (weapon == 'S') {
        health_max = 140;
        health = 140;
    }
    if (weapon == 'W') {
        mana_max = 100;
        mana = 100;
    }
    while (health > 0) {
        run_away = 0;
        while (exp >= exp_max) {
                level = level + 1;
                exp = exp - exp_max;
                exp_max = level*level/2.0*5+100;
                health_max = health_max+20;
                health = health_max;
                mana_max = mana_max+10;
                mana = mana_max;
                printf("\nYou leveled up!\nDamage increased\nCurrent health: %d HP\nCurrent mana: %d MP\nCurrent experience: %d/%d EXP\n", health, mana, exp, exp_max);
        }
        do {
            printf("\n\n\n\n\n\n\n\n\n\n\n\nYou have %d gold.\nWhere do you want to go? The [P]lains, [F]orest, [C]aves or [S]hop?\n", gold);
            scanf(" %c", &location);
            action = 'X';
            while (location == 'S' && action != 'N') {
                printf("\n\nThe shop sells [H]ealth and [M]ana potions for 50 gold each.\n");
                if (gold >= 50) {
                    printf("Do you want to buy a [H]ealth potion, [M]ana potion or [N]othing?\n");
                    scanf(" %c", &action);
                    if (action == 'H') {
                        gold = gold - 50;
                        health_potions = health_potions + 1;
                        printf("\nYou bought a health potion.\n");
                    }
                    if (action == 'M') {
                        gold = gold - 50;
                        mana_potions = mana_potions + 1;
                        printf("\nYou bought a mana potion.\n");
                    }
                }
                else {
                    printf("You don't have enough gold to buy anything. Come back later.\n");
                    action = 'N';
                }
            }
        } while (location == 'S');
        enemy = rand() %10;
        if (enemy == 9) {
            enemy = 1;
        }
        else {
            enemy = 0;
        }
        if (location == 'F') {
            enemy = enemy + 2;
        }
        if (location == 'C') {
            enemy = enemy + 4;
        }
        switch(enemy) {
            case 0:
                printf("\n\n\n\n\n\nYou encounter a goblin.\n");
                enemy_level = 1 + (rand() %101)*level/40.0;
                enemy_health = 50 + 5*enemy_level + enemy_level*(rand() %6);
                enemy_max_damage = 10+1.2*enemy_level;
                break;
            case 1:
                printf("\n\n\n\n\n\nYou encounter a goblin shaman.\n");
                enemy_level = 1 + (rand() %101)*level/30.0;
                enemy_health = 70 + 7*enemy_level + enemy_level*(rand() %8);
                enemy_max_damage = 15+1.5*enemy_level;
                break;
            case 2:
                printf("\n\n\n\n\n\nYou encounter a bear.\n");
                enemy_level = 1 + (rand() %101)*level/40.0;
                enemy_health = 90 + 8*enemy_level + enemy_level*(rand() %9);
                enemy_max_damage = 17+1.75*enemy_level;
                break;
            case 3:
                printf("\n\n\n\n\n\nYou encounter a witch.\n");
                enemy_level = 1 + (rand() %101)*level/30.0;
                enemy_health = 100 + 9*enemy_level + enemy_level*(rand() %10);
                enemy_max_damage = 20+2*enemy_level;
                break;
            case 4:
                printf("\n\n\n\n\n\nYou encounter a kobold.\n");
                enemy_level = 1 + (rand() %101)*level/40.0;
                enemy_health = 60 + 5*enemy_level + enemy_level*(rand() %6);
                enemy_max_damage = 12+1.25*enemy_level;
                break;
            case 5:
                printf("\n\n\n\n\n\nYou encounter a cave troll.\n");
                enemy_level = 1 + (rand() %101)*level/30.0;
                enemy_health = 150 + 12*enemy_level + enemy_level*(rand() %13);
                enemy_max_damage = 25+3*enemy_level;
                break;
        }
        while(enemy_health > 0 && run_away == 0 && health > 0) {
            damage = rand() %enemy_max_damage;
            printf("The enemy attacks you for %d damage.\n", damage);
            health = health - damage;
            printf("\n\n\nEnemy\nHealth: %d HP\nLevel: %d\n", enemy_health, enemy_level);
            printf("\n\n\nYour health: %d/%d HP\nYour mana: %d/%d MP\nYour level: %d\nYour experience: %d/%d EXP\n", health, health_max, mana, mana_max, level, exp, exp_max);
            if (health <= 0) {
                health = 0;
                printf("\n\n\n\nYou died.\n");
            }
            else {
            do {
                printf("\n\n\n\n\n\n\nChoose an action: [F]ight, [M]agic, [P]otions or [R]un away.\n");
                scanf(" %c", &action);
                switch(action) {
                case 'F':
                    if (weapon == 'S'){
                        damage = (rand() %101)*level/10;
                        printf("\nYou attack with your sword for %d damage.\n", damage);
                        enemy_health = enemy_health - damage;
                    }
                    if (weapon == 'W'){
                        damage = (rand() %51)*level/10;
                        printf("\nYou attack with your magic wand for %d damage.\n", damage);
                        enemy_health = enemy_health - damage;
                    }
                    break;
                case 'M':
                    printf("You can use 5 mana to cast a [F]ireball or [H]ealing magic.\n");
                    scanf(" %c", &magic);
                    if (magic == 'F') {
                        if (weapon == 'S') {
                            damage = (rand() %151)*level/10;
                            printf("\nYou cast a fireball for %d damage.\n", damage);
                            enemy_health = enemy_health - damage;
                            mana = mana - 5;
                        }
                        if (weapon == 'W') {
                            damage = (rand() %201)*level/10;
                            printf("\nYou cast a fireball for %d damage.\n", damage);
                            enemy_health = enemy_health - damage;
                            mana = mana - 5;
                        }
                    }
                    if (magic == 'H') {
                        if (weapon == 'S') {
                            healing = (rand() %51)*level/10;
                            printf("\nYou heal yourself for %d points.\n", healing);
                            health = health + healing;
                            mana = mana - 5;
                        }
                        if (weapon == 'W') {
                            healing = (rand() %101)*level/10;
                            printf("\nYou heal yourself for %d points.\n", healing);
                            health = health + healing;
                            mana = mana - 5;
                        }
                    }
                    break;
                case 'P':
                    printf("You have %d health potions and %d mana potions.\nDo you want to use a [H]ealth potion, [M]ana potion or [G]o back?\n", health_potions, mana_potions);
                    scanf(" %c", &action);
                    if (action == 'H') {
                        action = 'G';
                        if (health_potions > 0) {
                            health_potions = health_potions - 1;
                            health = health_max;
                            printf("\nYou are fully healed.\n");
                        }
                        else {
                            printf("You don't have any health potions to use.\n");
                        }
                    }
                    if (action == 'M') {
                        action = 'G';
                        if (mana_potions > 0) {
                            mana_potions = mana_potions - 1;
                            mana = mana_max;
                            printf("\nYour mana is fully replenished.\n");
                        }
                        else {
                            printf("You don't have any mana potions to use.\n");
                        }
                    }
                    break;
                case 'R':
                    success = rand() %2;
                    if (success >= 1) {
                        printf("\nYou successfully escaped.\n\n\n\n\n\n\n\n\n");
                        run_away = 1;
                    }
                    if (success == 0) {
                        printf("\nYou couldn't escape.\n");
                    }
                    break;

                }
            } while (action != 'F' && action != 'M' && action != 'R' && action != 'H');
            if (enemy_health <= 0) {
                printf("\n\n\n\n\n\n\n\nCongratulations, you successfully defeated the enemy.\n");
                reward = (rand() % 101)*enemy_max_damage*(enemy_level/level)/20;
                printf("You earned %d EXP.\n", reward);
                exp = exp + reward;
                reward = (rand() % 101)*enemy_max_damage*(enemy_level/level)/100;
                printf("You earned %d gold.\n", reward);
                gold = gold + reward;
                }
            }
        }
    }
    return 0;
}
