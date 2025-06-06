from python_functions import change_unit


__all__ = ['Material']


class Material:
    def __init__(
                self,
                etabs=None,
                ):
        self.etabs = etabs
        self.SapModel = etabs.SapModel

    def all_material(self):
        return self.SapModel.PropMaterial.GetNameList()[1]

    def material_type(self, name):
        return self.SapModel.PropMaterial.GetTypeOAPI(name)[0]
    
    def get_all_rebars(self):
        return self.SapModel.PropRebar.GetNameList()[1]

    def get_material_of_type(self, type_):
        '''
        type_ can be: 
            1: Steel
            2: Concrete
            6: Rebar
        '''
        mats = [mat for mat in self.all_material() if self.material_type(mat) == type_]
        return mats

    def get_rebar_fy_fu(self, rebar):
        return self.SapModel.PropMaterial.GetORebar(rebar)[0:2]
    
    def get_steel_fy_fu(self, steel):
        return self.SapModel.PropMaterial.GetOSteel(steel)[0:2]
    
    def get_frame_steel_fy_fu(self,
                              frame_name: str,
                              unit: tuple= ("kgf", 'cm'),
                              ):
        if unit is not None:
            self.etabs.set_current_unit(*unit)
        material = self.etabs.prop_frame.get_material(frame_name)
        if material is not None and self.material_type(material) == 1:
            ret = self.SapModel.PropMaterial.GetOSteel(material)
            return ret[:2]
        return None

    @change_unit('N', 'mm')
    def get_S340_S400_rebars(self):
        '''
        try to find S400 (AIII) and S340 (AII) Rebars material
        '''
        rebars = self.get_material_of_type(6)
        S340 = []
        S400 = []
        for rebar in rebars:
            fy, _ = self.get_rebar_fy_fu(rebar)
            if 390 < fy < 430:
                S400.append(rebar)
            elif 290 < fy < 350:
                S340.append(rebar)
        return S340, S400

    @change_unit('N', 'mm')
    def get_tie_main_rebar_all_sizes(self):
        '''
        return rebars that size is in (10, 12) as tie_rebar_sizes
        and rebars that size is in [14, 16, 18, 20, 22, 25, 28, 30, 32, 36, 40, 50] as main_rebar_sizes
        and all rebars with size and name
        '''
        tie_rebar_sizes = set()
        main_rebar_sizes = set()
        all_rebars = {}
        rebar_names = self.get_all_rebars()
        for name in rebar_names:
            if self.etabs.software == "ETABS":
                size = self.SapModel.PropRebar.GetRebarProps(name)[1]
            elif self.etabs.software == "SAP2000":
                size = self.SapModel.PropRebar.GetProp(name)[1]

        # for name, size in zip(rebars[1], rebars[3]):
            if not name.startswith('#') or not name.endswith('M') and int(size) == size:
                size = int(size)
                if  size in [10, 12]:
                    tie_rebar_sizes.add(str(size))
                    all_rebars[str(size)] = name
                elif size in [14, 16, 18, 20, 22, 25, 28, 30, 32, 36, 40, 50]:
                    main_rebar_sizes.add(str(size))
                    all_rebars[str(size)] = name
        return tie_rebar_sizes, main_rebar_sizes, all_rebars

    @change_unit('N', 'mm')
    def get_fc(self, conc):
        fc = self.SapModel.PropMaterial.GetOConcrete(conc)[0]
        return fc

    def add_material(
        self,
        name: str,
        type_: int,
        ):
        '''
        type_ can be: 
            1: Steel
            2: Concrete
            6: Rebar
        '''
        self.SapModel.PropMaterial.SetMaterial(name, type_)

    @change_unit(force='N', length='mm')
    def add_AIII_rebar(
        self,
        name: str = 'AIII',
        ):
        self.add_material(name, 6)
        self.SapModel.PropMaterial.SetORebar(name, 400, 600, 500, 750, 1, 1, 0.01, 0.09, False, 0)
    
    @change_unit(force='N', length='mm')
    def add_AII_rebar(
        self,
        name: str = 'AII',
        ):
        self.add_material(name, 6)
        self.SapModel.PropMaterial.SetORebar(name, 300, 500, 375, 625, 1, 1, 0.01, 0.09, False, 0)

    def get_unit_weight_of_materials(self) -> dict:
        '''
        Return the unit weight of each material as pair of key, value of dictionary
        '''
        table_key = "Material Properties - Basic Mechanical Properties"
        cols = ['Material', 'UnitWeight']
        df = self.etabs.database.read(table_key, to_dataframe=True, cols=cols)
        df = df.astype({'UnitWeight': float})
        df = df.set_index('Material')
        return df.to_dict()['UnitWeight']
    
    @change_unit(force='N', length='mm')
    def add_concrete(self,
                     name: str,
                     fc: float,
                     is_lightweight: bool=False,
                     fcs_factor: float=1,
                     ss_type: int=2,
                     ssh_ys_type: int=4,
                     strain_at_fc: float=0.002219,
                     strain_ultimate: float=.005,
                     weight_for_calculate_ec: float=0,
                     ):
        self.add_material(name, type_=2)
        if weight_for_calculate_ec == 0:
            par = 4700
        else:
            par = 0.043 * weight_for_calculate_ec ** 1.5
        ec = par * fc ** 0.5
        self.SapModel.PropMaterial.SetMPIsotropic(name, ec, 0.2, 0.0000055)
        self.SapModel.PropMaterial.SetOConcrete(name, fc, is_lightweight, fcs_factor, ss_type, ssh_ys_type, strain_at_fc, strain_ultimate)
        self.etabs.set_current_unit('kgf', 'm')
        self.SapModel.PropMaterial.SetWeightAndMass(name, 1, 2500)

    @change_unit(force='N', length='mm')
    def add_rebar(self,
                  name: str,
                  fy: int,
                  fu: int,
    ):
        ry = 1.25
        e = 2e5
        nu = 0.2
        a = 0.0000117
        self.add_material(name, type_=6)
        self.SapModel.PropMaterial.SetMPIsotropic(name, e, nu, a)
        self.SapModel.PropMaterial.SetORebar(name, fy, fu, ry * fy, ry * fu, 1, 1, 0.01, 0.09, False)
        self.etabs.set_current_unit('kgf', 'm')
        self.SapModel.PropMaterial.SetWeightAndMass(name, 1, 7850)
    
    @change_unit(force='N', length='mm')
    def add_steel(self,
                  name: str,
                  fy: int,
                  fu: int,
    ):
        ry = 1.25
        e = 2e5
        nu = 0.2
        a = 0.0000117
        self.add_material(name, type_=1)
        self.SapModel.PropMaterial.SetMPIsotropic(name, e, nu, a)
        self.SapModel.PropMaterial.SetOSteel_1(name, fy, fu, ry * fy, ry * fu, 1, 1, 0.015, 0.11, 0.17, -0.1)
        self.etabs.set_current_unit('kgf', 'm')
        self.SapModel.PropMaterial.SetWeightAndMass(name, 1, 7850)

    
        