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
        内置的、扁平化的评价函数操作数常量库。
        所有操作数都在顶层，方便直接调用。
        调用示例: mf_editor.add_operand(Op.EFFL)
        """
        # ------------------- 控制与数学运算 (Control & Math) -------------------
        CONF='CONF'; DMFS='DMFS'; OPGT='OPGT'; OPLT='OPLT'; OSGT='OSGT'; OSLT='OSLT'
        GTCE='GTCE'; GOTO='GOTO'; ENDX='ENDX'; BLNK='BLNK'; USYM='USYM'; ZPLM='ZPLM'
        UDOP='UDOP'; UDOC='UDOC'; OOFF='OOFF'; SUMM='SUMM'; PROD='PROD'; DIVI='DIVI'
        DIVB='DIVB'; SQRT='SQRT'; ABSO='ABSO'; LOGT='LOGT'; LOGE='LOGE'; SINE='SINE'
        COSI='COSI'; TANG='TANG'; ASIN='ASIN'; ACOS='ACOS'; ATAN='ATAN'; EXPP='EXPD'
        MINN='MINN'; MAXX='MAXX'; CONS='CONS'

        # ------------------- 像差与波前 (Aberration & Wavefront) -------------------
        SPHA='SPHA'; COMA='COMA'; ASTI='ASTI'; FCUR='FCUR'; DIST='DIST'; AXCL='AXCL'
        LACL='LACL'; LATC='LATC'; PTUX='PTUX'; PTUY='PTUY'; PSUX='PSUX'; PSUY='PSUY'
        OPD='OPD'; OPDM='OPDM'; OPDX='OPDX'; WAVE='WAVE'; ZERN='ZERN'; SPHD='SPHD'
        SPHS='SPHS'

        # ------------------- 几何与一阶参数 (Geometric & First-Order) -------------------
        EFFL='EFFL'; EFLX='EFLX'; EFLY='EFLY'; EFLA='EFLA'; FNUM='FNUM'; EFNO='EFNO'
        ISFN='ISFN'; TOTR='TOTR'; TTHI='TTHI'; PLEN='PLEN'; PIMH='PIMH'; STHI='STHI'
        ENPP='ENPP'; EXPP='EXPP'; EPDI='EPDI'; CARD='CARD'; PMAG='PMAG'; AMAG='AMAG'

        # ------------------- 约束 (Constraints) -------------------
        MNCG='MNCG'; MXCG='MXCG'; MNEG='MNEG'; MXEG='MXEG'; MNCA='MNCA'; MXCA='MXCA'
        MNEA='MNEA'; MXEA='MXEA'; MNCT='MNCT'; MXCT='MXCT'; MNET='MNET'; MXET='MXET'
        PMCG='PMCG'; PMEG='PMEG'; TCVA='TCVA'; TCGT='TCGT'; TCLT='TCLT'; BLTH='BLTH'
        MNAI='MNAI'; MXAI='MXAI'; RAEN='RAEN'; RAED='RAED'; CVVA='CVVA'; CVGT='CVGT'
        CVLT='CVLT'; SCRV='SCRV'; DENC='DENC'; DENF='DENF'; INDX='INDX'; VOLU='VOLU'
        CIGT='CIGT'; CILT='CILT'; CIVA='CIVA'; CEGT='CEGT'; CELT='CELT'; CEVA='CEVA'
        DSAG='DSAG'

        # ------------------- 光线追迹 (Ray Tracing) -------------------
        REAX='REAX'; REAY='REAY'; REAZ='REAZ'; REAR='REAR'; RAGX='RAGX'; RAGY='RAGY'
        RAGZ='RAGZ'; REAA='REAA'; REAB='REAB'; REAC='REAC'; RAID='RAID'; RAIN='RAIN'
        TRAC='TRAC'; NORX='NORX'; NORY='NORY'; NORZ='NORZ'

        # ------------------- MTF与性能分析 (MTF & Performance) -------------------
        MTFS='MTFS'; MTFT='MTFT'; MTFA='MTFA'; MTFD='MTFD'; MTFN='MTFN'; MTFX='MTFX'
        MTHA='MTHA'; MTHS='MTHS'; MTHT='MTHT'; MTHN='MTHN'; MTHX='MTHX'
        IMSF='IMSF'

        # ------------------- 非序列 (Non-Sequential) -------------------
        NSDD='NSDD'; NSDC='NSDC'; NSTR='NSTR'; NSST='NSST'; NSDE='NSDE'; NSDP='NSDP'
        NSRD='NSRD'; NSLT='NSLT'; NSTW='NSTW'; NSRW='NSRW'; NPAF='NPAF'
    # --- 智能参数映射字典 ---
    _operand_parameter_maps = {
        # '操作数类型': {'参数名': (单元格索引, 值类型), ...}
        
        # 默认映射: 适用于大多数标准像差操作数
        'DEFAULT': {
            'wave': (4, 'IntegerValue'), 'field': (3, 'IntegerValue'), 'samp': (7, 'IntegerValue'),
        },

        # --- 特定操作数的专属映射 ---
        
        # 几何与一阶参数
        'EFFL': { 'wave': (2, 'IntegerValue') },
        'EFLX': { 'wave': (2, 'IntegerValue') },
        'EFLY': { 'wave': (2, 'IntegerValue') },
        'FNUM': { 'wave': (2, 'IntegerValue') },
        'PIMH': { 'wave': (2, 'IntegerValue'), 'field': (3, 'IntegerValue') },
        'TOTR': { 'surf1': (2, 'IntegerValue'), 'surf2': (3, 'IntegerValue') },
        
        # 光线追迹
        'TRAC': { 'surf': (2, 'IntegerValue'), 'wave': (3, 'IntegerValue'), 'field': (4, 'IntegerValue')},
        'REAX': { 'wave': (2, 'IntegerValue'), 'hx': (3, 'DoubleValue'), 'hy': (4, 'DoubleValue'), 'px': (5, 'DoubleValue'), 'py': (6, 'DoubleValue')},
        'REAY': { 'wave': (2, 'IntegerValue'), 'hx': (3, 'DoubleValue'), 'hy': (4, 'DoubleValue'), 'px': (5, 'DoubleValue'), 'py': (6, 'DoubleValue')},
        'RAID': { 'wave': (2, 'IntegerValue'), 'hx': (3, 'DoubleValue'), 'hy': (4, 'DoubleValue'), 'px': (5, 'DoubleValue'), 'py': (6, 'DoubleValue')},
        
        # 约束类
        'MNCG': { 'surf1': (2, 'IntegerValue'), 'surf2': (3, 'IntegerValue') },
        'MXCG': { 'surf1': (2, 'IntegerValue'), 'surf2': (3, 'IntegerValue') },
        'MNEG': { 'surf1': (2, 'IntegerValue'), 'surf2': (3, 'IntegerValue') },
        'MXEG': { 'surf1': (2, 'IntegerValue'), 'surf2': (3, 'IntegerValue') },
        'MNCA': { 'surf1': (2, 'IntegerValue'), 'surf2': (3, 'IntegerValue') },
        'MXCA': { 'surf1': (2, 'IntegerValue'), 'surf2': (3, 'IntegerValue') },
        'MNEA': { 'surf1': (2, 'IntegerValue'), 'surf2': (3, 'IntegerValue') },
        'MXEA': { 'surf1': (2, 'IntegerValue'), 'surf2': (3, 'IntegerValue') },
        'DSAG': { 'surf1': (2, 'IntegerValue'), 'surf2': (3, 'IntegerValue') },
        'CVVA': { 'surf': (2, 'IntegerValue') },
        'PMCG': { 'surf': (2, 'IntegerValue') },
        'PMEG': { 'surf': (2, 'IntegerValue') },
        
        # MTF
        'MTFS': { 'field': (3, 'IntegerValue'), 'wave': (4, 'IntegerValue'), 'freq': (6, 'DoubleValue')},
        'MTFT': { 'field': (3, 'IntegerValue'), 'wave': (4, 'IntegerValue'), 'freq': (6, 'DoubleValue')},
        'MTFA': { 'field': (3, 'IntegerValue'), 'wave': (4, 'IntegerValue'), 'freq': (6, 'DoubleValue')},
    }

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

    def add_operand(self, operand_type: str, target: float = 0.0, weight: float = 1.0, **kwargs) -> Any:
        try:
            new_operand = self.TheMFE.AddOperand()
            operand_type_enum = getattr(self.ZOSAPI.Editors.MFE.MeritOperandType, operand_type)
            new_operand.ChangeType(operand_type_enum)
            new_operand.Target = target
            new_operand.Weight = weight
            
            # --- 智能参数映射逻辑 ---
            specific_map = self._operand_parameter_maps.get(operand_type, self._operand_parameter_maps['DEFAULT'])
            
            for param_name, value in kwargs.items():
                if param_name in specific_map:
                    cell_index, value_type = specific_map[param_name]
                    cell = new_operand.GetCellAt(cell_index)
                    setattr(cell, value_type, value)
                else:
                    logger.warning(f"参数 '{param_name}' 在操作数 '{operand_type}' 的映射规则中未定义，将被忽略。")
            
            logger.info(f"成功添加操作数: {operand_type}")
            return new_operand
        except Exception as e:
            logger.error(f"添加操作数 '{operand_type}' 失败: {str(e)}")
            raise
    

    def clear_merit_function(self) -> None:
        try:
            while self.TheMFE.NumberOfOperands > 1:
                self.TheMFE.RemoveOperandAt(2)
            if self.TheMFE.NumberOfOperands == 1:
                op1 = self.TheMFE.GetOperandAt(1)
                op1.ChangeType(self.ZOSAPI.Editors.MFE.MeritOperandType.CONF)
            elif self.TheMFE.NumberOfOperands == 0:
                self.TheMFE.AddOperand().ChangeType(self.ZOSAPI.Editors.MFE.MeritOperandType.CONF)
            logger.info("评价函数已清空并重置为单个CONF操作数。")
        except Exception as e:
            logger.error(f"清空评价函数时出错: {str(e)}")
            raise
    # def use_optimization_wizard(self, wizard_type: str = 'default', **settings) -> None:
    #     try:
    #         wizard = self.TheMFE.SEQOptimizationWizard
    #         if settings.get('clear_existing', True):
    #             self.clear_merit_function()
    #         wizard.OverallWeight = settings.get('weight', 1.0)
    #         type_map = {'rms_spot': 1, 'wavefront': 2, 'default': 0}
    #         wizard.Data = type_map.get(wizard_type.lower(), 0)
    #         wizard.Apply()
    #         logger.info(f"已使用 '{wizard_type}' 优化向导生成评价函数。")
    #     except Exception as e:
    #         logger.error(f"使用优化向导失败: {str(e)}")
    #         raise
    def use_optimization_wizard(self, wizard_type: str = 'default', **settings) -> None:
        """
        使用功能完备的优化向导自动生成评价函数。

        Args:
            wizard_type: 向导类型，支持 'rms_spot', 'wavefront', 'default'。
            **settings: 详尽的向导设置参数，例如:
                - 'clear_existing': (bool) 是否清空现有函数，默认True。
                - 'weight': (float) 总体权重，默认1.0。
                
                # --- 高斯求积设置 ---
                - 'rings': (int) 高斯求积环数 (2=3环, 3=4环, 4=6环), 默认2。
                - 'arms': (int) 高斯求积臂数, 默认0 (自动)。

                # --- 边界约束 ---
                - 'use_glass_constraints': (bool) 是否使用玻璃厚度约束, 默认True。
                - 'glass_min_center': (float) 最小中心厚度, 默认3.0。
                - 'glass_max_center': (float) 最大中心厚度, 默认1000.0。
                - 'glass_min_edge': (float) 最小边缘厚度, 默认3.0。
                - 'use_air_constraints': (bool) 是否使用空气间隔约束, 默认True。
                - 'air_min_center': (float) 最小中心间隔, 默认0.5。
                - 'air_max_center': (float) 最大中心间隔, 默认1000.0。
                - 'air_min_edge': (float) 最小边缘间隔, 默认0.5。
                
                # --- 其他约束 ---
                - 'add_distortion_constraint': (bool) 是否添加畸变约束, 默认True。
                - 'distortion_weight': (float) 畸变权重, 默认1.0。
                - 'add_axial_color_constraint': (bool) 是否添加轴向色差约束, 默认True。
                - 'axial_color_weight': (float) 轴向色差权重, 默认1.0。
        """
        try:
            wizard = self.TheMFE.SEQOptimizationWizard
            if settings.get('clear_existing', True):
                self.clear_merit_function()

            # --- 设置核心参数 ---
            wizard.OverallWeight = settings.get('weight', 1.0)
            type_map = {'rms_spot': 1, 'wavefront': 2, 'default': 0}
            wizard.Data = type_map.get(wizard_type.lower(), 0)
            
            # --- 设置高斯求积 ---
            wizard.Ring = settings.get('rings', 2) # 2 corresponds to 3 rings in the GUI
            wizard.Arm = settings.get('arms', 0)

            # --- 设置玻璃厚度约束 ---
            wizard.IsGlassUsed = settings.get('use_glass_constraints', True)
            if wizard.IsGlassUsed:
                wizard.GlassMin = settings.get('glass_min_center', 0.3)
                wizard.GlassMax = settings.get('glass_max_center', 1000.0)
                wizard.GlassEdge = settings.get('glass_min_edge', 0.3)

            # --- 设置空气间隔约束 ---
            wizard.IsAirUsed = settings.get('use_air_constraints', True)
            if wizard.IsAirUsed:
                wizard.AirMin = settings.get('air_min_center', 0.5)
                wizard.AirMax = settings.get('air_max_center', 1000.0)
                wizard.AirEdge = settings.get('air_min_edge', 0.5)

            # --- 设置其他约束 ---
            wizard.IsDistortionUsed = settings.get('add_distortion_constraint', False)
            if wizard.IsDistortionUsed:
                wizard.DistortionWeight = settings.get('distortion_weight', 1.0)
                
            wizard.IsAxialColorUsed = settings.get('add_axial_color_constraint', False)
            if wizard.IsAxialColorUsed:
                wizard.AxialColorWeight = settings.get('axial_color_weight', 1.0)

            # 应用所有设置
            wizard.Apply()
            logger.info(f"已使用功能完备的 '{wizard_type}' 优化向导生成评价函数。")
        except Exception as e:
            logger.error(f"使用优化向导失败: {str(e)}")
            raise
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
            best_file_name = f"GLOPT_0000_{best_result_index:03d}.zos"
            best_file_path = os.path.join(output_folder, best_file_name)

            if os.path.exists(best_file_path):
                self.TheSystem.LoadFile(best_file_path, False)
                logger.info(f"全局优化完成。最优解(第{best_result_index}个)已加载，MF: {min_merit_value:.6f}")
            else:
                logger.error(f"最优结果文件 {best_file_path} 未找到！")
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
    
