
from json import load, dump


class Config():
    """
    loads data from config_file, accessible with Config.attribute
    """
    def __init__(self):
        self.discord_token = None
        self.target_user_id = None
        self.admin_id = None
        self.cat_api_key = None

    def load_config(self, filename) -> bool:
        try:
            with open(filename, 'r') as cfg:
                # Deserialize the JSON data (essentially turning it into a Python dictionary object so we can use it in our code) 
                config = load(cfg) 

                # discord api token
                self.discord_token = config['phanbot-token']

                # This is ID of Phantom
                self.target_user_id = int(config['phantom-id'])

                # ID of the user who will have special permissions and will recieve logs and updates from the bot 
                self.admin_id = int(config['trusted-user-id'])

                # API key to Cat API
                self.cat_api_key = config['cat_key']
            
            return True
            
        except OSError:
            return False


# for oritentation in reaction_data.data: dict[user_id: list[REACTIONS, PHANPOINTS, PHANBOMB]]
REACTIONS = 0
PHANPOINTS = 1
PHANBOMB = 2

class ReactionData():
    def __init__(self, filename):
        # data -> total, points, since_bomb
        self.data: dict[int: dict[str: int]] = {}
        self.source_file = filename

    
    def load_data(self) -> bool:
        try:
            with open(self.source_file, 'r') as file:
                self.data = load(file)
            return True
        except OSError:
            return False


    async def save_data(self) -> bool:
        try:
            with open(self.source_file, 'w+') as file:
                dump(self.data, file)
            return True

        except OSError:
            return False
    
    def get_val(self, user_id: int, key: str) -> int | None:
        '''
        total, points, since_bomb
        '''
        if user_id in self.data:
            return (self.data.get(str(user_id))).get(key, None)
        return None
    

    def set_val(self, user_id: int, key: str, new_val: int) -> bool:
        '''total, points, since_bomb'''
        if user_id in self.data:
            if key in self.data[str(user_id)]:
                self.data[str(user_id)][key] = new_val
                return True
        return False


    def change_reaction_count(self, user_id: int, delta: int):
        if user_id not in self.data:
            self.data[str(user_id)] = [0, 0, 0]
        self.data[str(user_id)]["total"] += delta
        self.data[str(user_id)]["since_bomb"] += delta

