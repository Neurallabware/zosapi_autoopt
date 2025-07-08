"""
Zemax OpticStudio Python API 评价函数编辑器 (终极完整版 - 带最全智能参数映射)
内置了分类简化、调用便捷的操作数常量库，并使用详尽的智能映射处理各种操作数的复杂参数。
"""
import logging
from typing import Dict, List, Any
import os

logger = logging.getLogger(__name__)

class MeritFunctionEditor:
    """
    评价函数编辑器
    """
    class Operands:
        """
        内置的、分类完整的评价函数操作数常量库。
        调用示例: mf_editor.add_operand(Op.Aberration.SPHA, wave=1, field=2)
        """
    #class Aberration:
        SPHA='SPHA'; COMA='COMA'; ASTI='ASTI'; FCUR='FCUR'; DIST='DIST'; AXCL='AXCL'
        LACL='LACL'; PTUX='PTUX'; PTUY='PTUY'; PSUX='PSUX'; PSUY='PSUY'; OPD='OPD'
        OPDM='OPDM'; OPDX='OPDX'; WAVE='WAVE'; ZERN='ZERN'; SPHD='SPHD'; SPHS='SPHS'
        DPHS='DPHS'; DCRV='DCRV'; DSAG='DSAG'; DSLP='DSLP'; DIMX='DIMX'
    #class Geometric:
        EFFL='EFFL'; EFLX='EFLX'; EFLY='EFLY'; EFLA='EFLA'; FNUM='FNUM'; EFNO='EFNO'
        ISFN='ISFN'; TOTR='TOTR'; TTHI='TTHI'; PLEN='PLEN'; PIMH='PIMH'; STHI='STHI'
        ENPP='ENPP'; EXPP='EXPP'; EPDI='EPDI'; CARD='CARD'; PMAG='PMAG'; AMAG='AMAG'
        SFNO='SFNO'; TFNO='TFNO'; WFNO='WFNO'
    #class Ray:
        REAX='REAX'; REAY='REAY'; REAZ='REAZ'; REAR='REAR'; RAGX='RAGX'; RAGY='RAGY'
        RAGZ='RAGZ'; REAA='REAA'; REAB='REAB'; REAC='REAC'; RAID='RAID'; RAIN='RAIN'
        TRAC='TRAC'; NORX='NORX'; NORY='NORY'; NORZ='NORZ'; RENA='RENA'; RENB='RENB'
        RENC='RENC'; RETX='RETX'; RETY='RETY'; NORD='NORD'; TRAX='TRAX'; TRAY='TRAY'
    #class Constraint:
        MNCG='MNCG'; MXCG='MXCG'; MNEG='MNEG'; MXEG='MXEG'; MNCA='MNCA'; MXCA='MXCA'
        MNEA='MNEA'; MXEA='MXEA'; MNCT='MNCT'; MXCT='MXCT'; MNET='MNET'; MXET='MXET'
        PMCG='PMCG'; PMEG='PMEG'; TCVA='TCVA'; TCGT='TCGT'; TCLT='TCLT'; BLTH='BLTH'
        MNAI='MNAI'; MXAI='MXAI'; RAEN='RAEN'; RAED='RAED'; CVVA='CVVA'; CVGT='CVGT'
        CVLT='CVLT'; SCRV='SCRV'; DENC='DENC'; DENF='DENF'; INDX='INDX'; VOLU='VOLU'
        CIGT='CIGT'; CILT='CILT'; CIVA='CIVA'; CEGT='CEGT'; CELT='CELT'; CEVA='CEVA'
        MNRE='MNRE'; MXRE='MXRE'; MNRI='MNRI'; MXRI='MXRI'; WLEN='WLEN'; ZTHI='ZTHI'
    #class Performance:
        MTFS='MTFS'; MTFT='MTFT'; MTFA='MTFA'; MTFD='MTFD'; MTFN='MTFN'; MTFX='MTFX'
        MTHA='MTHA'; MTHS='MTHS'; MTHT='MTHT'; MTHN='MTHN'; MTHX='MTHX'; IMSF='IMSF'
        RELI='RELI'; RSCE='RSCE'; RSCH='RSCH'; RSRE='RSRE'; RSRH='RSRH'; RWCE='RWCE'
        RWCH='RWCH'; RWRE='RWRE'; RWRH='RWRH'
    #class Control:
        CONF='CONF'; DMFS='DMFS'; OPGT='OPGT'; OPLT='OPLT'; OSGT='OSGT'; OSLT='OSLT'
        GTCE='GTCE'; GOTO='GOTO'; ENDX='ENDX'; BLNK='BLNK'; USYM='USYM'; ZPLM='ZPLM'
        UDOP='UDOP'; UDOC='UDOC'; OOFF='OOFF'; SUMM='SUMM'; PROD='PROD'; DIVI='DIVI'
        DIVB='DIVB'; SQRT='SQRT'; ABSO='ABSO'; LOGT='LOGT'; LOGE='LOGE'; SINE='SINE'
        COSI='COSI'; TANG='TANG'; ASIN='ASIN'; ACOS='ACOS'; ATAN='ATAN'; EXPD='EXPD'
        MINN='MINN'; MAXX='MAXX'; CONS='CONS'
    #class NonSequential:
        NSDD='NSDD'; NSDC='NSDC'; NSTR='NSTR'; NSST='NSST'; NSDE='NSDE'; NSDP='NSDP'
        NSRD='NSRD'; NSLT='NSLT'; NSTW='NSTW'; NSRW='NSRW'; NPAF='NPAF'; NSRM='NSRM'
    #class Polarization:
        POWR='POWR'; POWP='POWP'; POWF='POWF'; POPD='POPD'
    #class Diffraction:
        DIFF='DIFF'; DLTN='DLTN'; FOUC='FOUC'; POPD='POPD'; PROB='PROB'; STRH='STRH'
        POPI='POPI'; FREZ='FREZ'; ERFP='ERFP'
    #class GlobalCoord:
        GLCA='GLCA'; GLCB='GLCB'; GLCC='GLCC'; GLCX='GLCX'; GLCY='GLCY'; GLCZ='GLCZ'
        GLCR='GLCR'

#=============本来打算构建一个映射词典来简化操作数的参数设置，但由于ZOSAPI的复杂性和多样性，让GPT生成的不准确，暂时先不使用。===========
    # _operand_parameter_maps = {
    #     # 默认映射: 适用于大多数标准像差操作数
    #     'DEFAULT': {'wave': (4, 'IntegerValue'), 'field': (3, 'IntegerValue'), 'samp': (7, 'IntegerValue')},
    #     # 像差类
    #     'SPHA': {'wave': (2, 'IntegerValue')}, 'COMA': {'wave': (2, 'IntegerValue'), 'field': (3, 'IntegerValue')},
    #     'ASTI': {'wave': (2, 'IntegerValue'), 'field': (3, 'IntegerValue')},
    #     'FCUR': {'wave': (2, 'IntegerValue'), 'field': (3, 'IntegerValue')},
    #     'DIST': {'wave': (2, 'IntegerValue'), 'field': (3, 'IntegerValue')},
    #     'AXCL': {'wave1': (2, 'IntegerValue'), 'wave2': (3, 'IntegerValue')},
    #     'LACL': {'wave1': (2, 'IntegerValue'), 'wave2': (3, 'IntegerValue'), 'field': (4, 'IntegerValue')},
    #     'OPD':  {'wave': (2, 'IntegerValue'), 'field': (3, 'IntegerValue'), 'px': (4, 'DoubleValue'), 'py': (5, 'DoubleValue')},
    #     'DIMX': {'field': (2, 'IntegerValue'), 'wave': (3, 'IntegerValue')},
    #     # 几何类
    #     'EFFL': {'wave': (2, 'IntegerValue')}, 'EFLX': {'wave': (2, 'IntegerValue')},
    #     'EFLY': {'wave': (2, 'IntegerValue')}, 'FNUM': {'wave': (2, 'IntegerValue')},
    #     'PIMH': {'wave': (2, 'IntegerValue'), 'field': (3, 'IntegerValue')},
    #     'TOTR': {'surf1': (2, 'IntegerValue'), 'surf2': (3, 'IntegerValue')},
    #     'TTHI': {'surf1': (2, 'IntegerValue'), 'surf2': (3, 'IntegerValue')},
    #     # 光线追迹类
    #     'REAX': {'wave': (2, 'IntegerValue'), 'hx': (3, 'DoubleValue'), 'hy': (4, 'DoubleValue'), 'px': (5, 'DoubleValue'), 'py': (6, 'DoubleValue')},
    #     'REAY': {'wave': (2, 'IntegerValue'), 'hx': (3, 'DoubleValue'), 'hy': (4, 'DoubleValue'), 'px': (5, 'DoubleValue'), 'py': (6, 'DoubleValue')},
    #     'RAID': {'wave': (2, 'IntegerValue'), 'hx': (3, 'DoubleValue'), 'hy': (4, 'DoubleValue'), 'px': (5, 'DoubleValue'), 'py': (6, 'DoubleValue')},
    #     'TRAC': {'surf': (2, 'IntegerValue'), 'wave': (3, 'IntegerValue'), 'field': (4, 'IntegerValue')},
    #     'TRAY': {'surf': (2, 'IntegerValue'), 'wave': (3, 'IntegerValue'), 'field': (4, 'IntegerValue')},
    #     # 约束类
    #     'MNCG': {'surf1': (2, 'IntegerValue'), 'surf2': (3, 'IntegerValue')},
    #     'MXCG': {'surf1': (2, 'IntegerValue'), 'surf2': (3, 'IntegerValue')},
    #     'MNEG': {'surf1': (2, 'IntegerValue'), 'surf2': (3, 'IntegerValue')},
    #     'MXEG': {'surf1': (2, 'IntegerValue'), 'surf2': (3, 'IntegerValue')},
    #     'MNCA': {'surf1': (2, 'IntegerValue'), 'surf2': (3, 'IntegerValue')},
    #     'MXCA': {'surf1': (2, 'IntegerValue'), 'surf2': (3, 'IntegerValue')},
    #     'MNEA': {'surf1': (2, 'IntegerValue'), 'surf2': (3, 'IntegerValue')},
    #     'MXEA': {'surf1': (2, 'IntegerValue'), 'surf2': (3, 'IntegerValue')},
    #     'DSAG': {'surf1': (2, 'IntegerValue'), 'surf2': (3, 'IntegerValue')},
    #     'CVVA': {'surf': (2, 'IntegerValue')},
    #     'PMCG': {'surf': (2, 'IntegerValue')},
    #     'RELI': {'wave': (2, 'IntegerValue'), 'field': (3, 'IntegerValue')},
    #     # MTF类
    #     'MTFS': {'field': (3, 'IntegerValue'), 'wave': (4, 'IntegerValue'), 'freq': (6, 'DoubleValue')},
    #     'MTFT': {'field': (3, 'IntegerValue'), 'wave': (4, 'IntegerValue'), 'freq': (6, 'DoubleValue')},
    #     'MTFA': {'field': (3, 'IntegerValue'), 'wave': (4, 'IntegerValue'), 'freq': (6, 'DoubleValue')},
    #     'MTFD': {'field': (3, 'IntegerValue'), 'wave': (4, 'IntegerValue'), 'freq': (6, 'DoubleValue')},
    # }

    def __init__(self, zos_manager):
        if not zos_manager or not zos_manager.is_connected:
            raise ValueError("需要一个有效的、已连接的 ZOSAPIManager 实例。")
        self.zos_manager = zos_manager
        self.TheSystem = zos_manager.TheSystem
        self.ZOSAPI = zos_manager.ZOSAPI
        self.TheMFE = self.TheSystem.MFE
        self._operand_type_map = self._build_operand_type_map()

    def _build_operand_type_map(self) -> Dict[int, str]:

        type_map = {}
        try:
            operand_enum_type = self.ZOSAPI.Editors.MFE.MeritOperandType
            for name in dir(operand_enum_type):
                if not name.startswith('_'):
                    try:
                        enum_member = getattr(operand_enum_type, name)
                        type_map[int(enum_member)] = name
                    except Exception:
                        continue
            return type_map
        except AttributeError:
            logger.error("无法找到ZOSAPI.Editors.MFE.MeritOperandType枚举。")
            return {}

#=============有映射词典的话可以这样做==================
    # def add_operand(
    #     self,
    #     operand_type: str,
    #     target: float = 0.0,
    #     weight: float = 1.0,
    #     direct_params: Dict[int, Any] = None,
    #     **kwargs
    # ) -> Any:
    #     """
    #     添加一个操作数，同时支持“智能关键字”和“直接参数”两种模式。

    #     Args:
    #         operand_type (str): 操作数类型，如 'TOTR', 'EFFL'。
    #         target (float): 目标值。
    #         weight (float): 权重。
    #         direct_params (Dict[int, Any], optional): 
    #             【直接参数模式】一个字典，用于直接设置单元格。
    #             键是单元格编号(int)，值是要设置的数据(int, float, str)。
    #             示例: {2: 5, 3: 12.345}
    #         **kwargs: 
    #             【智能关键字模式】使用预定义的关键字设置参数。
    #             示例: surf1=1, wave=2
    #     """
    #     new_operand = self.TheMFE.AddOperand()
        
    #     operand_type_enum = getattr(self.ZOSAPI.Editors.MFE.MeritOperandType, operand_type)
    #     new_operand.ChangeType(operand_type_enum)
    #     new_operand.Target = target
    #     new_operand.Weight = weight
        
    #     # --- 1. 处理智能关键字参数 (kwargs) ---
    #     specific_map = self._operand_parameter_maps.get(operand_type, {})
    #     for param_name, value in kwargs.items():
    #         if param_name in specific_map:
    #             cell_index, value_type = specific_map[param_name]
    #             cell = new_operand.GetCellAt(cell_index)
    #             setattr(cell, value_type, value)
    #         else:
    #             logger.warning(f"关键字 '{param_name}' 未在 '{operand_type}' 的智能映射规则中定义，将被忽略。")
        
    #     # --- 2. 处理直接参数设置 (direct_params) ---
    #     if direct_params:
    #         for cell_index, value in direct_params.items():
    #             cell = new_operand.GetCellAt(cell_index)
    #             # 根据值的类型，自动调用正确的API属性
    #             if isinstance(value, int):
    #                 cell.IntegerValue = value
    #             elif isinstance(value, float):
    #                 cell.DoubleValue = value
    #             elif isinstance(value, str):
    #                 cell.StringValue = value
    #             else:
    #                 logger.warning(f"直接参数中单元格 {cell_index} 的值类型未知，无法设置。")
        
    #     logger.info(f"成功添加操作数: {operand_type}")
    #     return new_operand
#=========================================================
    def add_operand(
        self,
        operand_type: str,
        target: float = 0.0,
        weight: float = 1.0,
        params: Dict[int, Any] = None
    ) -> Any:
        """
        添加一个操作数，并根据传入值的Python类型来选择API调用。
        Args:
            operand_type (str): 操作数类型，如 'TOTR', 'EFFL'。
            target (float): 目标值。
            weight (float): 权重。
            params (Dict[int, Any], optional): 
                一个字典，用于直接设置单元格。
                键是单元格编号(int)，值是要设置的数据(int, float)。
                示例: {2: 5, 3: 12.345}
                注意：操作数的第一个参数index从2开始！！！
        """
        new_operand = self.TheMFE.AddOperand()
        operand_type_enum = getattr(self.ZOSAPI.Editors.MFE.MeritOperandType, operand_type)
        new_operand.ChangeType(operand_type_enum)
        new_operand.Target = target
        new_operand.Weight = weight

        if params:
            for cell_index, value in params.items():
                cell = new_operand.GetCellAt(cell_index)

                if isinstance(value, float):
                    cell.DoubleValue = value
                elif isinstance(value, int):
                    cell.IntegerValue = value
                else:
                     logger.warning(f"参数单元格 {cell_index} 的值类型未知 ({type(value)})，无法设置。")
        
        logger.info(f"成功添加操作数: {operand_type}")
        return new_operand
    

    def clear_merit_function(self) -> None:
        try:
            while self.TheMFE.NumberOfOperands > 1:
                self.TheMFE.RemoveOperandAt(2)
            if self.TheMFE.NumberOfOperands == 1:
                op1 = self.TheMFE.GetOperandAt(1)
                op1.ChangeType(self.ZOSAPI.Editors.MFE.MeritOperandType.BLNK)
            elif self.TheMFE.NumberOfOperands == 0:
                self.TheMFE.AddOperand().ChangeType(self.ZOSAPI.Editors.MFE.MeritOperandType.BLNK)
            logger.info("评价函数已清空并重置为单个BLNK操作数。")
        except Exception as e:
            logger.error(f"清空评价函数时出错: {str(e)}")
            raise

    def use_optimization_wizard(
        self,
        wizard_type: str = 'default',
        clear_existing: bool = True,
        weight: float = 1.0,
        rings: int = 2,
        arms: int = 0,
        use_glass_constraints: bool = True,
        glass_min_center: float = 3.0,
        glass_max_center: float = 1000.0,
        glass_min_edge: float = 3.0,
        use_air_constraints: bool = True,
        air_min_center: float = 0.5,
        air_max_center: float = 1000.0,
        air_min_edge: float = 0.5,
        **other_settings
    ) -> None:
        """
        使用功能完备的优化向导自动生成评价函数，拥有清晰的参数定义。

        Args:
            wizard_type (str): 向导类型, 支持 'rms_spot', 'wavefront', 'default'。
            clear_existing (bool): 是否清空现有函数。
            weight (float): 评价函数总体权重。
            rings (int): 高斯求积环数 (2=3环, 3=4环, 4=6环)。
            arms (int): 高斯求积臂数 (0 for auto)。
            use_glass_constraints (bool): 是否启用玻璃厚度约束。
            glass_min_center (float): 最小中心玻璃厚度。
            glass_max_center (float): 最大中心玻璃厚度。
            glass_min_edge (float): 最小边缘玻璃厚度。
            use_air_constraints (bool): 是否启用空气间隔约束。
            air_min_center (float): 最小中心空气间隔。
            air_max_center (float): 最大中心空气间隔。
            air_min_edge (float): 最小边缘空气间隔。
            **other_settings: 其他不常用的设置，如 'add_distortion_constraint'。
        """
        wizard = self.TheMFE.SEQOptimizationWizard
        if clear_existing:
            self.clear_merit_function()

        # --- 设置核心参数 ---
        wizard.OverallWeight = weight
        type_map = {'rms_spot': 1, 'wavefront': 2, 'default': 0}
        wizard.Data = type_map.get(wizard_type.lower(), 0)
        
        # --- 设置高斯求积 ---
        wizard.Ring = rings
        wizard.Arm = arms

        # --- 设置玻璃厚度约束 ---
        wizard.IsGlassUsed = use_glass_constraints
        if wizard.IsGlassUsed:
            wizard.GlassMin = glass_min_center
            wizard.GlassMax = glass_max_center
            wizard.GlassEdge = glass_min_edge

        # --- 设置空气间隔约束 ---
        wizard.IsAirUsed = use_air_constraints
        if wizard.IsAirUsed:
            wizard.AirMin = air_min_center
            wizard.AirMax = air_max_center
            wizard.AirEdge = air_min_edge

        # --- 设置其他不常用的约束 (通过 **other_settings) ---
        if other_settings.get('add_distortion_constraint', False):
            wizard.IsDistortionUsed = True
            wizard.DistortionWeight = other_settings.get('distortion_weight', 1.0)
            
        if other_settings.get('add_axial_color_constraint', False):
            wizard.IsAxialColorUsed = True
            wizard.AxialColorWeight = other_settings.get('axial_color_weight', 1.0)

        # 应用所有设置
        wizard.Apply()
        logger.info(f"已使用 '{wizard_type}' 优化向导生成评价函数。")

    def update(self) -> None:
        try:
            self.TheMFE.CalculateMeritFunction()
        except AttributeError:
            _ = self.TheMFE.NumberOfOperands
    def get_current_merit_value(self) -> float:
        opt_tool = None
        try:
            opt_tool = self.TheSystem.Tools.OpenLocalOptimization()
            merit_value = opt_tool.InitialMeritFunction
            return merit_value
        except Exception as e:
            logger.error(f"获取评价函数值失败: {e}")
            return -1.0
        finally:
            if opt_tool:
                opt_tool.Close()

    def list_operands(self) -> List[Dict[str, Any]]:
        operands_list = []
        try:
            for i in range(self.get_operand_count()):
                operand = self.TheMFE.GetOperandAt(i + 1)
                op_type_int = int(operand.Type)
                op_type_str = self._operand_type_map.get(op_type_int, f"UnknownType_{op_type_int}")
                operands_list.append({
                    'index': i, 'type': op_type_str, 'target': operand.Target,
                    'weight': operand.Weight, 'value': operand.Value
                })
            return operands_list
        except Exception as e:
            logger.error(f"获取操作数列表失败: {str(e)}")
            return []
    def get_operand_count(self) -> int:
        return self.TheMFE.NumberOfOperands
    def delete_operand(self, index: int) -> None:
        if not (0 <= index < self.get_operand_count()):
            raise IndexError(f"无效的操作数索引: {index}")
        if self.get_operand_count() == 1 and self.list_operands()[0]['type'] == 'CONF':
             logger.warning("无法删除最后一个CONF操作数。")
             return
        self.TheMFE.RemoveOperandAt(index + 1)
    def edit_operand(self, index: int, **kwargs) -> bool:
        if not (0 <= index < self.get_operand_count()):
            raise IndexError(f"无效的操作数索引: {index}")
        operand = self.TheMFE.GetOperandAt(index + 1)
        if self.list_operands()[index]['type'] == 'CONF' and ('target' in kwargs or 'weight' in kwargs):
            return False
        if 'target' in kwargs:
            operand.Target = float(kwargs['target'])
        if 'weight' in kwargs:
            operand.Weight = float(kwargs['weight'])
        return True

    def run_local_optimization(self, algorithm: str = 'DampedLeastSquares', cores: int = 20, timeout_seconds: int = 120) -> Dict[str, Any]:
        local_opt = None

        alg_map = {'DampedLeastSquares': self.ZOSAPI.Tools.Optimization.OptimizationAlgorithm.DampedLeastSquares}
        if algorithm not in alg_map:
            raise ValueError(f"不支持的算法: {algorithm}")
        local_opt = self.TheSystem.Tools.OpenLocalOptimization()
        local_opt.Algorithm = alg_map[algorithm]
        local_opt.NumberOfCores = cores
        local_opt.Cycles = self.ZOSAPI.Tools.Optimization.OptimizationCycles.Automatic
        initial_merit = local_opt.InitialMeritFunction
        logger.info(f"开始局部优化... 初始评价函数值: {initial_merit:.6f}")
        local_opt.RunAndWaitWithTimeout(timeout_seconds)
        final_merit = local_opt.CurrentMeritFunction
        iterations = -1
        if hasattr(local_opt, 'NumberOfCyclesRun'):
            iterations = local_opt.NumberOfCyclesRun
        logger.info(f"局部优化完成。最终评价函数值: {final_merit:.6f}")
        
        if local_opt:
            local_opt.Close()
        return {'success': True, 'initial_merit': initial_merit, 'final_merit': final_merit, 'iterations': iterations}


    def run_global_optimization(self, output_folder: str, timeout_seconds: int = 60, cores: int = 20, save_top_n: int = 10) -> Dict[str, Any]:
        """
        运行全局优化, 将所有结果保存在指定的文件夹中，并加载最优解。
        """
        global_opt = None

        import os
        os.makedirs(output_folder, exist_ok=True)

        working_file_path = os.path.join(output_folder, "global_opt_workfile.zos")
        self.TheSystem.SaveAs(working_file_path)
        self.TheSystem.LoadFile(working_file_path, False)

        for f in os.listdir(output_folder):
            if f.startswith("GLOPT_") and f.endswith(".zos"):
                os.remove(os.path.join(output_folder, f))
        # 运行优化
        global_opt = self.TheSystem.Tools.OpenGlobalOptimization()
        global_opt.NumberOfCores = cores
        save_enum = getattr(self.ZOSAPI.Tools.Optimization.OptimizationSaveCount, f"Save_{save_top_n}")
        global_opt.NumberToSave = save_enum

        initial_merit = global_opt.InitialMeritFunction
        logger.info(f"全局优化开始... (目标文件夹: {os.path.basename(output_folder)}, 初始MF: {initial_merit:.6f})")
        global_opt.RunAndWaitWithTimeout(timeout_seconds)

        # 处理结果
        top_results = [m for m in (global_opt.CurrentMeritFunction(i) for i in range(1, save_top_n + 1)) if m > 0]

        global_opt.Cancel(); global_opt.WaitForCompletion(); global_opt.Close(); global_opt = None

        if top_results:
            min_merit_value = min(top_results)
            best_result_index = top_results.index(min_merit_value) + 1
            
            best_file_name = None
            # 构造期望的文件后缀，例如 "_001.zos"
            expected_suffix = f"_{best_result_index:03d}.zos"
            
            # 遍历输出文件夹中的所有文件
            for filename in os.listdir(output_folder):
                # 检查文件是否以 "GLOPT_" 开头并以我们期望的后缀结束
                if filename.startswith("GLOPT_") and filename.endswith(expected_suffix):
                    best_file_name = filename
                    break  # 找到后立即退出循环

            if best_file_name:
                best_file_path = os.path.join(output_folder, best_file_name)
                # 理论上文件应该存在，但再次检查以确保稳健性
                if os.path.exists(best_file_path):
                    self.TheSystem.LoadFile(best_file_path, False)
                    logger.info(f"全局优化完成。最优解(第{best_result_index}个, 文件: {best_file_name})已加载，MF: {min_merit_value:.6f}")
                else:
                    # 这个情况理论上不会发生，因为我们已经从目录中找到了文件名
                    logger.error(f"代码逻辑错误：找到了文件名 {best_file_name} 但文件路径 {best_file_path} 不存在！")
                    self.TheSystem.LoadFile(working_file_path, False)
            else:
                logger.error(f"无法在目录 {output_folder} 中找到与最优结果索引 {best_result_index} 匹配的文件。")
                self.TheSystem.LoadFile(working_file_path, False)

        else:
            logger.warning("全局优化未找到任何有效结果。")

        return {'success': True, 'initial_merit': initial_merit, 'top_results': top_results, 'results_directory': output_folder}

            
    def run_hammer_optimization(self, timeout_seconds: int = 60, cores: int = 20) -> Dict[str, Any]:
        """
        运行锤形优化 (Hammer Optimization)。

        Args:
            timeout_seconds: 优化运行的秒数。
            cores: 使用的核心数。

        Returns:
            一个包含优化结果的字典。
        """
        hammer_opt = None
 
        hammer_opt = self.TheSystem.Tools.OpenHammerOptimization()
        hammer_opt.NumberOfCores = cores
        initial_merit = hammer_opt.InitialMeritFunction
        logger.info(f"开始锤形优化... 初始评价函数值: {initial_merit:.6f}，运行 {timeout_seconds} 秒，使用 {cores} 个核心")

        hammer_opt.RunAndWaitWithTimeout(timeout_seconds)
        final_merit = hammer_opt.CurrentMeritFunction
        logger.info(f"锤形优化完成。最终评价函数值: {final_merit:.6f}")

        if hammer_opt:
            hammer_opt.Cancel()
            hammer_opt.WaitForCompletion()
            hammer_opt.Close()
            logger.info("锤形优化工具已关闭。")

        return {'success': True, 'initial_merit': initial_merit, 'final_merit': final_merit}
    
