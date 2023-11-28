import random
import json
import utils

class MissionManager:
    def __init__(self, mission_types=None):
        with open("tables/missions.json", "r") as file:
            self.missions_data = json.load(file)
        
        self.mission_types = mission_types if mission_types else self.missions_data.keys()
        self.mission_tables = {mission_type: utils.ListTable(self.missions_data[mission_type]) 
                               for mission_type in self.mission_types}
        self.missions = []

    def roll_mission(self, mission_type=None):
        if not mission_type:
            mission_type = random.choice(list(self.mission_tables.keys()))
        mission_data = self.mission_tables[mission_type].roll()[0]
        mission = Mission(mission_type, mission_data)
        self.missions.append(mission)
        return mission

    def roll_missions(self, mission_types=None):
        if not mission_types:
            mission_types = self.mission_types
        return [self.roll_mission(mission_type) for mission_type in mission_types]
    
    def clear_completed(self):
        self.missions = [mission for mission in self.missions if not mission.complete]

class Mission:
    def __init__(self, mission_type, mission_data, random_params = True):
        self.mission_type = mission_type
        self.mission_data = mission_data
        self.name = mission_data["name"]
        self.description = mission_data["description"]
        # print(mission_data)
        self.details = mission_data["details"] if "details" in mission_data else None
        self.location_table = utils.DieTable(10, utils.flatten_range(mission_data["location"]))
        self.twist_table = utils.DieTable(10, utils.flatten_range(mission_data["twist"]))
        self.location = "Not Rolled"
        self.twist = "Not Rolled"
        if random_params:
            self.roll_params()
        else:
            self.params = False
        self.complete = False

    def roll_params(self):
        self.location = self.location_table.roll()[0]
        self.twist = self.twist_table.roll()[0]
        self.params = True
    
    def reroll_param(self, param):
        setattr(self, param, getattr(self, "{}_table".format(param)).roll()[0])
    
    def complete_mission(self):
        self.complete = True
    
    def print_summary(self):
        print(self.name)
        print(self.description)
        if self.details:
            print("Details:")
            for detail in self.details:
                print("\t{}: {}".format(detail, self.details[detail]))
        print("Location: {}".format(self.location))
        print("Twist: {}".format(self.twist))

if __name__ == "__main__":
    mission_manager = MissionManager()
    mission_manager.roll_mission().print_summary()