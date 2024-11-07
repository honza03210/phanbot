
from json import load


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
        self.data: dict[int: list[int, int, int]] = {}
        self.source_file = filename

    
    def load_data(self) -> bool:
        try:
            with open(self.source_file, 'r') as file:
                for row in file.readlines():
                    elements = row.split("|")

                    user_id = int(elements[0])
                    reac_num = int(elements[1])
                    phanpoints = int(elements[2])
                    phanbomb = int(elements[3])

                    self.data[user_id] = [reac_num, 
                                          phanpoints, 
                                          phanbomb]
            return True

        except OSError:
            return False


    async def save_data(self) -> bool:
        try:
            with open(self.source_file, 'w+') as file:
                for user_id, data in self.data.items():
                    file.write(f"{user_id}|{data[0]}|{data[1]}|{data[2]}\n")

            return True

        except OSError:
            return False
    
    def change_reaction_count(self, user_id: int, delta: int):
        if user_id not in self.data:
            self.data[user_id] = [0, 0, 0]
        self.data[user_id][REACTIONS] += delta
        self.data[user_id][PHANBOMB] += delta

