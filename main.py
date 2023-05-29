import requests
import mysql.connector

# З'єднання БД
mydb = mysql.connector.connect(
    user="root",
    password="NTU",
    database="pokemon"
)
mycursor = mydb.cursor()

# Виклик PokéAPI для отримання інформації
pokemon_response = requests.get("https://pokeapi.co/api/v2/pokemon?limit=100&offset=0")
pokemon_data = pokemon_response.json()

# Обробка отриманих даних та збереження їх у базу даних
for pokemon in pokemon_data['results']:
    name = pokemon['name']
    url = pokemon['url']

    # Отримання інформації для таблиці pokemon
    pokemon_response = requests.get(url)
    pokemon_data = pokemon_response.json()
    species_url = pokemon_data['species']['url']
    species_response = requests.get(species_url)
    species_data = species_response.json()
    stats = pokemon_data['stats']
    capture_rate = species_data['capture_rate']
    for stat in stats:
        stat_name = stat['stat']['name']
        base_stat = stat['base_stat']
        if stat_name == 'hp':
            hp = base_stat
        elif stat_name == 'attack':
            atk = base_stat
        elif stat_name == 'defense':
            defense = base_stat
        elif stat_name == 'speed':
            speed = base_stat

    # Збереження даних у таблицю pokemon
    sql = "INSERT INTO pokemon (name, url, hp, atk, def, speed, capture_rate) VALUES (%s, %s, %s, %s, %s, %s, %s)"
    val = (name, url, hp, atk, defense, speed, capture_rate)
    mycursor.execute(sql, val)

    # Отримання інформації для таблиці species
    pokemon_id = mycursor.lastrowid
    color = species_data['color']['name']
    egg_groups = ", ".join([group['name'] for group in species_data['egg_groups']])
    generation = species_data['generation']['name']
    growth_rate = species_data['growth_rate']['name']
    habitat = species_data['habitat']['name'] if species_data['habitat'] else None
    is_baby = species_data['is_baby']
    is_legendary = species_data['is_legendary']
    is_mythical = species_data['is_mythical']

    # Збереження даних у таблицю species
    sql = "INSERT INTO species (color, egg_group, generation, growth_rate, habitat, is_baby, is_legendary, is_misthical, pok_id) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)"
    val = (color, egg_groups, generation, growth_rate, habitat, is_baby, is_legendary, is_mythical, pokemon_id)
    mycursor.execute(sql, val)

    # Отримання інформації про здібності
    abilities = pokemon_data['abilities']
    for ability_info in abilities:
        ability_url = ability_info['ability']['url']
        ability_response = requests.get(ability_url)
        ability_data = ability_response.json()
        ability_name = ability_data['name']

        # Перевірка наявності опису здібності
        if ability_data['effect_entries'] and len(ability_data['effect_entries']) > 1:
            effect = ability_data['effect_entries'][1]['effect']
        else:
            effect = "No effect"

        # Збереження даних у таблицю ability
        sql = "INSERT IGNORE INTO ability (name, effect) VALUES (%s, %s)"
        val = (ability_name, effect)
        mycursor.execute(sql, val)

        # Отримання id здібності за допомогою назви здібності
        sql = "SELECT id FROM ability WHERE name = %s"
        val = (ability_name,)
        mycursor.execute(sql, val)
        existing_ability = mycursor.fetchone()

        # Перевірка наявності здібності для уникнення пропусків при зв'язку
        if existing_ability:
            ability_id = existing_ability[0]
        else:
            ability_id = mycursor.lastrowid

        # Збереження зв'язку між покемоном та абілкою у таблицю pokemon_ability
        sql = "INSERT INTO pokemon_ability (pok_id, ab_id) VALUES (%s, %s)"
        val = (pokemon_id, ability_id)
        mycursor.execute(sql, val)

# Збереження змін
mydb.commit()

# Закриття з'єднання з БД
mycursor.close()
mydb.close()