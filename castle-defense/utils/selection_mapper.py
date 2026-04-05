class SelectionMapper:

    @staticmethod
    def map_players(players_list):
        return [SelectionMapper._map_player(p) for p in players_list]

    @staticmethod
    def map_enemy(enemy):
        return SelectionMapper._map_enemy(enemy)

    @staticmethod
    def map_castle(castle):
        return SelectionMapper._map_castle(castle)

    # =========================
    # 🔽 MÉTODOS PRIVADOS
    # =========================

    @staticmethod
    def _map_player(player_string):
        if "Fairy" in player_string:
            return {"type": "Fairies", "variant": int(player_string.split()[-1])}

        if "Gent" in player_string:
            return {"type": "gentlemen", "variant": int(player_string.split()[-1])}

        if "War" in player_string:
            return {"type": "Warrior", "variant": int(player_string.split()[-1])}

        return {"type": "Fairies", "variant": 1}

    @staticmethod
    def _map_enemy(enemy_string):
        if "A" in enemy_string:
            return {"type": "trolls", "variant": 1}

        if "B" in enemy_string:
            return {"type": "trolls", "variant": 2}

        if "C" in enemy_string:
            return {"type": "trolls", "variant": 3}

        return {"type": "trolls", "variant": 1}

    @staticmethod
    def _map_castle(castle_string):
        if "Fortress" in castle_string:
            return {"type": "castle", "variant": 1}

        if "Ice" in castle_string:
            return {"type": "castle", "variant": 2}

        if "Fire" in castle_string:
            return {"type": "castle", "variant": 3}

        return {"type": "castle", "variant": 1}