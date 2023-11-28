import random
import json
import utils

system_data = json.load(open('./tables/system.json'))

#Create dies
d10 = utils.Die(10)
d100 = utils.Die(100)

#Create tables
primary_table = utils.DieTable(d100, utils.flatten_range(system_data['primary_table']))
rare_table = utils.DieTable(d100, utils.flatten_range(system_data['rare_table']))
special_table = utils.DieTable(d100, utils.flatten_range(system_data['special_table']))
star_information = system_data['star_information']
sizes_tables = {}
giant_outer_table = utils.DieTable(d100, utils.flatten_range(system_data['giant_outer_table']))
massive_outer_table = utils.DieTable(d100, utils.flatten_range(system_data['massive_outer_table']))
inner_planet_tables = {}
outer_planet_tables = {}

for star_type in star_information:
    sizes_tables[star_type] = utils.DieTable(d10, utils.flatten_range(star_information[star_type]['sizes_table']))
    if 'inner_planet_table' in star_information[star_type]:
        if type(star_information[star_type]['inner_planet_table']) == dict:
            inner_planet_tables[star_type] = utils.DieTable(d100, utils.flatten_range(star_information[star_type]['inner_planet_table']))
        else:
            inner_planet_tables[star_type] = inner_planet_tables[star_information[star_type]['inner_planet_table']]
    else:
        inner_planet_tables[star_type] = None
    if type(star_information[star_type]['outer_planet_table']) == dict:
        outer_planet_tables[star_type] = utils.DieTable(d100, utils.flatten_range(star_information[star_type]['outer_planet_table']))
    elif star_information[star_type]['outer_planet_table'] == 'giant_outer_table':
        outer_planet_tables[star_type] = giant_outer_table
    elif star_information[star_type]['outer_planet_table'] == 'massive_outer_table':
        outer_planet_tables[star_type] = massive_outer_table
    else:
        outer_planet_tables[star_type] = outer_planet_tables[star_information[star_type]['outer_planet_table']]

gas_giant_rings_table = utils.DieTable(d10, utils.flatten_range(system_data['gas_giant_rings_table']))
moons_table = utils.DieTable(d10, utils.flatten_range(system_data['moons_table']))
gas_giant_moons_table = utils.DieTable(d10, utils.flatten_range(system_data['gas_giant_moons_table']))
moon_type_table = utils.DieTable(d10, utils.flatten_range(system_data['moon_type_table']))
orbiting_stars_table = utils.DieTable(d10, utils.flatten_range(system_data['orbiting_stars_table']))
space_stations_table = utils.DieTable(d100, utils.flatten_range(system_data['space_stations_table']))
space_outposts_table = utils.DieTable(d100, utils.flatten_range(system_data['space_outposts_table']))
ground_settlements_table = utils.DieTable(d100, utils.flatten_range(system_data['ground_settlements_table']))
government_table = utils.DieTable(d100, utils.flatten_range(system_data['government_table']))
economy_table = utils.DieTable(d100, utils.flatten_range(system_data['economy_table']))
allegiance_table = utils.DieTable(d10, utils.flatten_range(system_data['allegiance_table']))
first_name_table = utils.DieTable(d100, utils.flatten_range(system_data['first_name_table']))
second_name_table = utils.DieTable(d100, utils.flatten_range(system_data['second_name_table']))

planet_discovery_rewards = system_data['planet_discovery_reward']
non_habitable_map = system_data['non_habitable_mappings']

inhabited_probability = system_data['inhabited_probability']

def roll_star_type():
    star_type = primary_table.roll()[0]
    if star_type == "Rare":
        star_type = rare_table.roll()[0]
    elif star_type == "Special":
        star_type = special_table.roll()[0]
    return star_type

def roll_allegiance():
    return allegiance_table.roll()[0]

invalid_allegiance = {'Federation': ['Imperial', 'Patronage'],
                      'Empire': ['Democracy'],
                      'Alliance': ['Imperial'],
                      'Independent': ['Imperial']}

class System:
    def __init__(self, inhabited = True):
        self.stars = []  # List of Star objects
        self.inhabited = inhabited
        self.society = "Anarchy"
        self.security = "Low"
        self.economy = []
        # implement logic for inhabited systems later
        # systems without settlements are uninhabited

    def generate_system(self):
        # Generate the primary star
        primary_star_type = roll_star_type()

        main_star = Star(primary_star_type)
        main_star.generate_size()
        self.stars.append(main_star)

        # Generate companion stars
        num_companions = 0
        while num_companions < 5:
            companion_star_type = roll_star_type()
            companion_star = Star(companion_star_type)
            companion_star.generate_size()
            if companion_star.size < main_star.size:
                companion_star.generate_planets()
                self.stars.append(companion_star)
                num_companions += 1
                if d10.roll()[0] not in [9, 10]:
                    break
            else:
                break
        
        # Generate planets
        for star in self.stars:
            star.generate_planets()

        # Ensure at least one planet is inhabited if system is inhabited
        if self.inhabited and not any(planet.inhabited for star in self.stars for planet in star.planets):
            while not any(planet.inhabited for star in self.stars for planet in star.planets):
                for star in self.stars:
                    star.generate_planets()
        
        # Generate society if inhabited
        if self.inhabited:
            self.generate_economy()
            self.generate_government()
    
    def generate_economy(self):
        elw_ww_count = 0
        mr_metallic_count = 0
        for star in self.stars:
            for planet in star.planets:
                if planet.planet_type == "Earth-like World" or planet.planet_type == "Water World":
                    elw_ww_count += 1
                if planet.planet_type == "Metal Rich" or (planet.planet_type.startswith("Gas Giant")\
                    and planet.rings.endswith("Metallic")):
                    mr_metallic_count += 1
        
        if elw_ww_count >= 2:
            self.economy.append("Agricultural")
        if mr_metallic_count >= 2:
            self.economy.append("Extraction")
        
        star_planet_count = len(self.stars)

        for star in self.stars:
            star_planet_count += len(star.planets)

        if len(self.economy) == 0 or star_planet_count < 6:
            new_economy = economy_table.roll()[0]
            if new_economy not in self.economy:
                self.economy.append(new_economy)
    
    def generate_government(self):
        government = government_table.roll()[0]
        self.society = government['Society']
        self.security = government['Security Rating']
        allegiance_done = False
        while not allegiance_done:
            allegiance = roll_allegiance()
            if self.society not in invalid_allegiance[allegiance]:
                self.allegiance = allegiance
                allegiance_done = True
    
class Star:
    def __init__(self, star_type, inhabited = True):
        self.star_type = star_type
        self.inhabited = inhabited
        self.size = None
        self.habitable_zone = None
        self.planets = []  # List of Planet objects
        self.orbiting_stars = []  # List of OrbitingStar objects
        self.asteroid_belts = []  # List of AsteroidBelt objects

    def generate_size(self):
        self.size = sizes_tables[self.star_type].roll()[0]
        if star_information[self.star_type]['goldilocks_zone']:
            luminosity = calculate_luminosity(self.size, star_information[self.star_type]['alpha'])
            self.habitable_zone = calculate_habitable_zone(luminosity)
    
    def _generate_planets(self, min_distance, max_distance, table = "Inner"):
        no_planet_count = 0
        distance = min_distance
        table = inner_planet_tables[self.star_type] if table == "Inner" else outer_planet_tables[self.star_type]
        while distance <= max_distance:
            planet_type = table.roll()[0]
            if planet_type:
                if planet_type == "Star":
                    new_star_type = orbiting_stars_table.roll()[0]
                    if new_star_type == "Main Sequence":
                        new_star_type = roll_star_type()
                    new_star = OrbitingStar(new_star_type)
                    new_star.generate_size()
                    if new_star.size < self.size:
                        self.orbiting_stars.append(new_star, distance)
                elif planet_type == "Asteroid Belt":
                    new_asteroid_belt = AsteroidBelt(distance)
                    self.asteroid_belts.append(new_asteroid_belt)
                else:
                    if not self.is_in_habitable_zone(distance) and planet_type in non_habitable_map.keys():
                        planet_type = non_habitable_map[planet_type]
                    #else:
                    #    print("Habitable planet found")
                    #    print(planet_type)
                    new_planet = Planet(planet_type, distance, self.inhabited)
                # Additional planet generation logic here
                    self.planets.append(new_planet)
            else:
                no_planet_count += 1
                if no_planet_count == 2:
                    break
            distance += 100

    def generate_planets(self):
        inner_max_distance = 1000 if not self.star_type in rare_table.table else 2000
        outer_min_distance = 2000 if not self.star_type in rare_table.table else 3000
        outer_max_distance = 10000 if not self.star_type in rare_table.table else 20000
        
        # Generate inner and outer planets
        self._generate_planets(100, inner_max_distance, "Inner")
        self._generate_planets(outer_min_distance, outer_max_distance, "Outer")

        # Ensure at least one planet for inhabited systems
        if self.inhabited and not self.planets:
            while not self.planets:
                self._generate_planets(100, inner_max_distance)
                self._generate_planets(outer_min_distance, outer_max_distance)
    
    def is_in_habitable_zone(self, distance):
        if self.habitable_zone:
            return self.habitable_zone[0] <= distance <= self.habitable_zone[1]
        else:
            return False
    
    def sorted_orbiting_objects(self):
        # Combine and sort all orbiting objects by their distance
        return sorted(
            [(obj, obj.distance) for obj in self.planets + self.orbiting_stars + self.asteroid_belts],
            key=lambda x: x[1])

#Extends Star for potential future functionality, like planet generation
class OrbitingStar(Star):
    def __init__(self, star_type, distance, inhabited = False):
        super().__init__(star_type, inhabited)
        self.distance = distance
        self.rings = False
        self.generate_rings()
    
    def roll_star_type(self):
        self.star_type = "placeholder"

    def generate_rings(self):
        self.rings = gas_giant_rings_table.roll()[0]

class Planet:
    def __init__(self, planet_type, distance, system_inhabited):
        self.planet_type = planet_type
        self.distance = distance
        self.inhabited = self.determine_inhabited(system_inhabited)
        self.rings = False
        self.moons = []  # List of Moon objects
        self.stations = []  # List of Station objects
        self.outposts = []  # List of Outpost objects
        self.settlements = []  # List of Settlement objects
        self.generate_all()

    def determine_inhabited(self, system_inhabited):
        if system_inhabited:
            probability = inhabited_probability.get(self.planet_type, 0)
            return random.random() < probability
        return False

    def generate_all(self):
        self.generate_moons()
        gas_giant = self.planet_type.startswith('Gas Giant')
        if gas_giant:
            self.rings = gas_giant_rings_table.roll()[0]
            if self.rings == 'Metallic':
                self.inhabited = random.random() < inhabited_probability['Metallic']
        if self.inhabited:
            # Ensure at least one structure (station, outpost, or settlement)
            while not (self.stations or self.outposts or self.settlements):
                self.generate_stations()
                self.generate_outposts()
                if not self.planet_type.startswith('Gas Giant'):
                    self.generate_settlements()
        # if planet type starts with gas giant, generate rings
    
    def generate_moons(self):
        if self.planet_type.startswith('Gas Giant'):
            num_moons = gas_giant_moons_table.roll()[0]
        else:
            num_moons = moons_table.roll()[0]
        for _ in range(num_moons):
            moon_type = moon_type_table.roll()[0]
            new_moon = Moon(moon_type)
            self.moons.append(new_moon)

    def generate_stations(self):
        self._generate_structures(space_stations_table, Station, self.stations)

    def generate_outposts(self):
        self._generate_structures(space_outposts_table, Outpost, self.outposts)

    def generate_settlements(self):
        self._generate_structures(ground_settlements_table, Settlement, self.settlements)

    def _generate_structures(self, table, structure_class, collection):
        num_structures = table.roll()[0]
        for _ in range(num_structures):
            new_structure = structure_class()
            collection.append(new_structure)

class AsteroidBelt:
    def __init__(self, distance):
        self.distance = distance

class Moon:
    def __init__(self, moon_type):
        self.moon_type = moon_type
        # Add more attributes as needed

class Structure:
    def __init__(self, structure_type):
        self.structure_type = structure_type
        self.generate_name()
    
    def generate_name(self):
        first_name = first_name_table.roll()[0]
        second_name = second_name_table.roll()[0]
        if self.structure_type == "Settlement" and second_name == "Orbital":
            while second_name == "Orbital":
                second_name = second_name_table.roll()[0]
        self.name =  f"{first_name} {second_name}"

# Can extend this class for Station, Outpost, and Settlement specific mechanics

class Station(Structure):
    def __init__(self):
        super().__init__("Station")

class Outpost(Structure):
    def __init__(self):
        super().__init__("Outpost")

class Settlement(Structure):
    def __init__(self):
        super().__init__("Settlement")

def calculate_luminosity(mass, alpha):
    assert alpha, 'alpha must be non-zero and not None'
    return mass ** alpha

def calculate_habitable_zone(luminosity):
    # Constants for conversion
    au_to_light_seconds = 499.004784

    inner_boundary_au = (luminosity / 1.1) ** 0.5
    outer_boundary_au = (luminosity / 0.53) ** 0.5

    # Convert from AU to light-seconds
    inner_boundary_ls = inner_boundary_au * au_to_light_seconds
    outer_boundary_ls = outer_boundary_au * au_to_light_seconds

    return inner_boundary_ls, outer_boundary_ls

def print_system_summary(system):
    print("System Summary:")
    print(f"Society: {system.society}")
    print(f"Security: {system.security}")
    print(f"Allegiance: {system.allegiance}")
    print(f"Economy: {', '.join(system.economy) if system.economy else 'None'}")

    for star in system.stars:
        print(f"\nStar: {star.star_type}, Size: {star.size}")
        for obj, distance in star.sorted_orbiting_objects():
            if isinstance(obj, Planet):
                print(f"  Planet at {distance}ls: {obj.planet_type}, Inhabited: {'Yes' if obj.inhabited else 'No'}")
                if obj.rings:
                    print(f"    Rings: {obj.rings}")
                if obj.moons:
                    print(f"    Moons:")
                    for moon in obj.moons:
                        print(f"      {moon.moon_type}")
                if obj.stations:
                    print(f"    Stations:")
                    for station in obj.stations:
                        print(f"      {station.name}")
                if obj.outposts:
                    print(f"    Outposts:")
                    for outpost in obj.outposts:
                        print(f"      {outpost.name}")
                if obj.settlements:
                    print(f"    Settlements:")
                    for settlement in obj.settlements:
                        print(f"      {settlement.name}")

            elif isinstance(obj, OrbitingStar):
                print(f"  Orbiting Star at {distance}ls: {obj.star_type}")
                # You can add more details for orbiting stars here

            elif isinstance(obj, AsteroidBelt):
                print(f"  Asteroid Belt at {distance}ls")
                # Additional details for asteroid belts can be added here

    print("\n")
                    
if __name__ == "__main__":
    # Generate a solar system
    solar_system = System()
    solar_system.generate_system()
    #for key in inner_planet_tables:
    #    print(inner_planet_tables[key].table)
    # elw = False
    # while elw == False:
    #     solar_system = System()
    #     solar_system.generate_system()
    #     for star in solar_system.stars:
    #         for planet in star.planets:
    #             if planet.planet_type == "Water World" or planet.planet_type == "Earth-like World" or planet.planet_type == "Ammonia World":
    #             # if not gas giant or ice world
    #             ##if not planet.planet_type.startswith("Gas Giant") and not planet.planet_type.startswith("Ice World"):
    #                 elw = True
    #                 break

    # Print the system summary
    print_system_summary(solar_system)
    #print(government_table.roll())