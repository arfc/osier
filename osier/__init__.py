import unyt as u
from unyt import kg

try:
    u.define_unit("megatonnes", 1e9*kg)
except RuntimeError as e:
    print(e)
    u.unit_registry.default_unit_registry.remove("megatonnes")
    u.define_unit("megatonnes", 1e9*kg)


from .technology import *
from .models.model import *
from .models.dispatch import *
from .models.logic_dispatch import *
from .models.capacity_expansion import *
from .models.deap_runner import *
from .utils import *
from .equations import *

from .tech_library import *