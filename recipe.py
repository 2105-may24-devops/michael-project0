import json

class Recipe:
    """Data structure to represent the recipe, and contains manipulation recipes
    """
    TITLE_KEY="title"
    INGR_KEY="ingredients"
    STEP_KEY="steps"
    META_KEY="metadata"
    
    title:str
    #K:V = str:IngredientAmount
    ingredients:dict
    steps:list

    #TODO: stores other information, such as #served, author and whatever else.
    metadata:dict
    META_AUTHOR="author"
    META_SERVES="serves"
    META_SRCURL="src_url"
    META_REF="refs"

    modified:bool = False

    def __init__(self, filepath=None):
        self.title = ""
        self.ingredients={}
        self.steps=[]
        if filepath is not None:
            self.read_json()
        
    def __str__(self):
        #let's use Markdown
        string_builder = []
        string_builder.append(f"# {self.title}")
        #TODO: metadata?

        string_builder.append(f"\n## Ingredients")
        for ingr, amt in self.ingredients.items():
            string_builder.append(f"  - {amt.amount} {amt.unit} {ingr}")
        
        string_builder.append(f"\n## Instructions")
        for step_num,  step in enumerate(self.steps):
            string_builder.append(f"  {step_num+1}. step")
        return "\n".join(string_builder)
    

    def write_json(self, filepath):
        with open(filepath,"w",) as outfile:
            self_dict = {}
            self_dict[self.TITLE_KEY] = self.title
            self_dict[self.INGR_KEY] = {ingr:amt.get_tuple() for ingr, amt in self.ingredients.items()}
            self_dict[self.STEP_KEY] = self.steps
            self_dict[self.META_KEY] = self.metadata
            json.dump(self_dict, outfile,indent=4)
        

    def read_json(self, filepath):
        """
            Could fail if format is wrong. Handle exceptions elsewhere?
        """
        with open(filepath,"r",) as infile:
            my_dict=json.load(infile)
            self.title = my_dict[self.TITLE_KEY]
            self.steps = my_dict[self.STEP_KEY]
            self.ingredients = {ingr:IngredientAmount(*amt) for ingr, amt in my_dict[self.INGR_KEY]}
            self.metadata = my_dict[self.META_KEY]

    def scale_ingredients(self, factor:int):
        """
        Modify the ingredient amounts by a scale factor
        Can be called by other methods.
        """
        for ingred in self.ingredients.values():
            ingred.scale(factor)


class IngredientAmount:
    """
    Carries the amount and unit, handles conversions.
    
    Could maybe be a tuple, but has methods for conversions.
    """
    amount:float
    unit:str

    def __init__(self, amount:float, unit:str):
        pass
    
    def __str__(self):
        return f"{self.amount:.2} {self.unit}"
    
    #repr is for debugging, shows more decimals
    def __repr__(self):
        return f"{self.amount} {self.unit}"
    
    def get_tuple(self):
        return (self.amount, self.unit)

    #conversion units, possible float imprecision, but good enough.
    def scale(self, factor):
        self.amount *= factor

    #keys are lowercase, and some are abbreviated
    VOLUME_CONV:dict = {
        "ml": 1,
        "liter":1000,
        "cup":236.5875,
        "tbsp":14.7868,
        "tsp":4.92892,
        "fl oz": 29.5735
    }

    MASS_CONV:dict = {
        "grams":1 , 
        "kg":1000,
        "lbs": 453.592,
        "oz":28.3495
    }

    def is_volume_unit(self, unit:str = None):
        unit = self.unit if unit is None else unit
        return unit in self.VOLUME_CONV

    def is_mass_unit(self, unit:str = None):
        unit = self.unit if unit is None else unit
        return unit in self.MASS_CONV

    def convert_volume(self, dest_unit:str, src_unit:str, amt:float):
        """
        Converts volume units, returns a float
        Does not check whether units exist, which would throw a KeyError
        """
        factor = self.VOLUME_CONV[src_unit]/self.VOLUME_CONV[dest_unit]
        return amt*factor

    def convert_mass(self, dest_unit:str, src_unit:str, amt:float):
        """
        Converts mass units, returns a float
        Does not check whether units exist, which would throw a KeyError
        """
        factor = self.MASS_CONV[src_unit]/self.MASS_CONV[dest_unit]
        return amt*factor

    def convert_density(self,amt:float, density:float=1, to_volume=True):
        """
        density is in g/ml
        returns a float to convert between grams and milliliters
        """
        if to_volume:
            return amt/density
        else:
            return amt*density

    def convert_amount(self, dest_unit:str, src_unit:str=None, amt:float=None, density=1):
        """
        returns a float
        """
        src_unit = self.unit if src_unit is None else src_unit
        amt = self.amount if amt is None else amt

        src_is_vol = self.is_volume_unit(src_unit)
        dest_is_vol = self.is_volume_unit(dest_unit)

        if src_is_vol != dest_is_vol:
            #needs density stuff
            if src_is_vol:
                src_ml = self.convert_volume("ml", src_unit, amt)
                dest_g = self.convert_density(src_ml, density, dest_is_vol)
                return self.convert_mass(dest_unit, "g", dest_g)
            else:
                src_g = self.convert_mass("g", src_unit, amt)
                dest_ml = self.convert_density(src_g, density, dest_is_vol)
                return self.convert_volume(dest_unit, "ml", dest_ml)
        elif src_is_vol:
            return self.convert_volume(dest_unit, src_unit, amt)
        else:
            return self.convert_mass(dest_unit, src_unit, amt)

# class RecipeNode:
#     next_node:RecipeNode
#     name:str
#     description:str
#     #numeric, int or float, for sorting a flowchart's nodes
#     step_number
#     def __init__(self, step):
#         self.step_number = step
#     #comparison functions for sorting. 
#     def __lt__(self, other:RecipeNode):
#         return self.step_number < other.step_number
#     def __eq__(self, other:RecipeNode):
#         return self.step_number == other.step_number
#     #



