import sys
import inspect
import pandas as pd
from osier.technology import *
from osier.technology import _dim_opts
from unyt import GW, MW, kW, hour, day, year, kg, MWh
import unyt as u

to_MDOLLARS = 1e-6

co2_eq_units = (u.megatonnes*(GW*hour)**-1)

nuclear = ThermalTechnology(technology_name='Nuclear',
                            capacity=18.609404*GW,
                            capital_cost=50*(1/kW)*to_MDOLLARS,
                            om_cost_variable=0.0*to_MDOLLARS,
                            om_cost_fixed=177.73741*(1/kW)*to_MDOLLARS,
                            fuel_cost=5.811*(1/(MW*hour))*to_MDOLLARS,
                            ramp_up_rate=0.0,
                            ramp_down_rate=0.0,
                            lifecycle_co2_rate=5.1e-6*co2_eq_units,
                            land_intensity=0.0,
                            )
nuclear_adv = ThermalTechnology(technology_name='Nuclear_Adv',
                                capacity=0*GW,
                                capital_cost=4916.4*(1/kW)*to_MDOLLARS,
                                om_cost_variable=0.0*to_MDOLLARS,
                                om_cost_fixed=118.99*(1/kW)*to_MDOLLARS,
                                fuel_cost=9.158*(1/(MW*hour))*to_MDOLLARS,
                                ramp_up_rate=0.25,
                                ramp_down_rate=0.25,
                                lifecycle_co2_rate=nuclear.lifecycle_co2_rate,
                                land_intensity=0.0,
                                )
natural_gas = ThermalTechnology(technology_name='NaturalGas_Conv',
                                capacity=8.3751331*GW,
                                capital_cost=959.58*(1/kW)*to_MDOLLARS,
                                om_cost_variable=0.0*to_MDOLLARS,
                                om_cost_fixed=11.1934*(1/kW)*to_MDOLLARS,
                                fuel_cost=22.387*(1/(MW*hour))*to_MDOLLARS,
                                ramp_up_rate=1.0,
                                ramp_down_rate=1.0,
                                lifecycle_co2_rate=4.9e-4*co2_eq_units,
                                land_intensity=0.0,
                                )
biomass = ThermalTechnology(technology_name='Biomass',
                            renewable=True,
                            capacity=0*GW,
                            capital_cost=3436*(1/kW)*to_MDOLLARS,
                            om_cost_variable=0.0*to_MDOLLARS,
                            om_cost_fixed=123*(1/kW)*to_MDOLLARS,
                            fuel_cost=47*(1/(MW*hour))*to_MDOLLARS,
                            ramp_up_rate=1.0,
                            ramp_down_rate=1.0,
                            lifecycle_co2_rate=2.3e-4*co2_eq_units,
                            land_intensity=0.0,
                            )
natural_gas_adv = ThermalTechnology(technology_name='NaturalGas_Adv',
                                    capacity=0*GW,
                                    capital_cost=1891.0*(1/kW)*to_MDOLLARS,
                                    om_cost_variable=0.0*to_MDOLLARS,
                                    om_cost_fixed=26.99*(1/kW)*to_MDOLLARS,
                                    fuel_cost=27.475*(1/(MW*hour))*to_MDOLLARS,
                                    ramp_up_rate=1.0,
                                    ramp_down_rate=1.0,
                                    lifecycle_co2_rate=1.3e-4*co2_eq_units,
                                    land_intensity=0.0,
                                    )
coal = ThermalTechnology(technology_name='Coal_Conv',
                         capacity=0*GW,
                         capital_cost=1000*(1/kW)*to_MDOLLARS,
                         om_cost_variable=0.0*to_MDOLLARS,
                         om_cost_fixed=40.7033*(1/kW)*to_MDOLLARS,
                         fuel_cost=21.369*(1/(MW*hour))*to_MDOLLARS,
                         ramp_up_rate=0.5,
                         ramp_down_rate=0.5,
                         lifecycle_co2_rate=1e-3*co2_eq_units,
                         land_intensity=0.0,
                         )
coal_adv = ThermalTechnology(technology_name='Coal_Adv',
                            capacity=0*GW,
                            capital_cost=4924.6*(1/kW)*to_MDOLLARS,
                            om_cost_variable=0.0*to_MDOLLARS,
                            om_cost_fixed=58.24*(1/kW)*to_MDOLLARS,
                            fuel_cost=36.6329*(1/(MW*hour))*to_MDOLLARS,
                            ramp_up_rate=0.5,
                            ramp_down_rate=0.5,
                            lifecycle_co2_rate=3.7e-4*co2_eq_units,
                            land_intensity=0.0,
                            )
battery = StorageTechnology(technology_name='Battery',
                            capacity=0.81534126*GW,
                            capital_cost=613*(1/kW)*to_MDOLLARS,
                            om_cost_variable=0*to_MDOLLARS,
                            om_cost_fixed=15.32*(1/kW)*to_MDOLLARS,
                            fuel_cost=0*to_MDOLLARS,
                            storage_duration=4,
                            efficiency=0.85,
                            initial_storage=0.0*MWh,
                            capacity_credit=0.5,
                            lifecycle_co2_rate=3.3e-5*co2_eq_units,
                            land_intensity=0.0,
                            )
wind = Technology(technology_name='WindTurbine',
                  renewable=True,
                  dispatchable=False,
                  fuel_type='wind',
                  capacity=0*GW, 
                  capital_cost=1180.6*(1/kW)*to_MDOLLARS,
                  om_cost_fixed=33.11*(1/kW)*to_MDOLLARS,
                  lifecycle_co2_rate=1.2e-5*co2_eq_units,
                  land_intensity=0.0,
                  capacity_credit=0.35)
solar = Technology(technology_name='SolarPanel',
                  renewable=True,
                  dispatchable=False,
                  fuel_type='solar',
                  capacity=2.8103015*GW, 
                  capital_cost=673.2*(1/kW)*to_MDOLLARS,
                  om_cost_fixed=8.05*(1/kW)*to_MDOLLARS,
                  lifecycle_co2_rate=3.7e-5*co2_eq_units,
                  land_intensity=0.0,
                  capacity_credit=0.19)


def _get_names_technologies():
    """
    Returns a list of names and technologies in
    the :mod:`osier.tech_library`.
    """

    current_module = sys.modules[__name__]
    technology_list = []
    name_list = []

    for name, obj in inspect.getmembers(current_module):
        if isinstance(obj, Technology):
            technology_list.append(obj)
            name_list.append(name)
    
    return name_list, technology_list


def renewables_plus_storage():
    """
    Returns a list of technology objects including only
    renewable technologies and storage options.
    """

    names_list, technology_list = _get_names_technologies()
    technology_list = [tech
                       for tech in technology_list 
                       if ((tech.renewable) or (hasattr(tech, "storage_duration")))]

    return technology_list


def all_technologies():
    """
    Returns a list of all technology objects.
    """

    names_list, technology_list = _get_names_technologies()

    return technology_list


def catalog():
    """
    Returns a :class:`pandas.DataFrame` of technology names
    and their :class`osier` aliases.
    """

    names_list, technology_list = _get_names_technologies()
    catalog_df = pd.DataFrame({"Import Name":names_list,
                               "Technology Name":[t.technology_name 
                                                  for t in technology_list]})

    return catalog_df
