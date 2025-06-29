"""
Zemax OpticStudio Python API 分析模块
提供各种光学分析功能的封装
Author: allin-love
Date: 2025-06-29
"""

import logging
from typing import Optional, Dict, List, Tuple, Any
import numpy as np
from zosapi_core import ZOSAPIManager
from zosapi_utils import ZOSDataProcessor, zos_array_to_numpy, extract_zos_vector

logger = logging.getLogger(__name__)


class ZOSAnalyzer:
    """Zemax 光学分析器"""
    
    def __init__(self, zos_manager: ZOSAPIManager):
        """
        初始化分析器
        
        Args:
            zos_manager: ZOSAPI 管理器实例
        """
        self.zos = zos_manager
        self.data_processor = ZOSDataProcessor()
        
        if not self.zos.is_connected:
            raise ValueError("ZOSAPI 管理器未连接")
    
    def analyze_spot_diagram(self, field_index: int = 0, wavelength_index: int = 0,
                           surface_index: Optional[int] = None, 
                           max_rays: int = 500) -> Dict[str, Any]:
        """
        分析点列图 (使用批量光线追迹，参考官方例程22)
        
        Args:
            field_index: 视场索引 (0-based for internal use)
            wavelength_index: 波长索引 (0-based for internal use) 
            surface_index: 面索引，None 表示像面
            max_rays: 最大光线数
            
        Returns:
            点列图分析结果
        """
        try:
            try:
                from System import Enum, Int32, Double
            except ImportError:
                # 如果System不可用，回退到标准spot analysis
                return self._fallback_spot_analysis(field_index, wavelength_index, max_rays)
            
            import random
            
            system = self.zos.TheSystem
            fields = system.SystemData.Fields
            wavelengths = system.SystemData.Wavelengths
            
            # Convert to 1-based for Zemax API
            zemax_field_idx = field_index + 1
            zemax_wave_idx = wavelength_index + 1
            
            # 获取视场信息
            field = fields.GetField(zemax_field_idx)
            
            # 确定最大视场值用于归一化
            max_field = 0.0
            for i in range(1, fields.NumberOfFields + 1):
                if abs(fields.GetField(i).Y) > max_field:
                    max_field = abs(fields.GetField(i).Y)
            if max_field == 0:
                max_field = 1.0
            
            # 归一化视场坐标
            hx_norm = field.X / max_field
            hy_norm = field.Y / max_field
            
            # 初始化批量光线追迹
            raytrace = system.Tools.OpenBatchRayTrace()
            nsur = system.LDE.NumberOfSurfaces
            
            # 创建光线数据缓冲区
            normUnPolData = raytrace.CreateNormUnpol(max_rays, self.zos.ZOSAPI.Tools.RayTrace.RaysType.Real, nsur)
            
            # 填充缓冲区：为当前视场和波长添加光线
            normUnPolData.ClearData()
            for i in range(max_rays):
                # 在单位圆内生成随机光瞳坐标
                while True:
                    px = random.random() * 2 - 1
                    py = random.random() * 2 - 1
                    if px*px + py*py <= 1:
                        break
                normUnPolData.AddRay(zemax_wave_idx, hx_norm, hy_norm, px, py, 
                                   Enum.Parse(self.zos.ZOSAPI.Tools.RayTrace.OPDMode, "None"))
            
            # 执行追迹
            raytrace.RunAndWaitForCompletion()
            
            # 读取结果
            normUnPolData.StartReadingResults()
            
            # 为.NET引用传递创建占位符
            sysInt = Int32(1)
            sysDbl = Double(1.0)
            
            x_coords = []
            y_coords = []
            
            # 读取第一条光线
            output = normUnPolData.ReadNextResult(sysInt, sysInt, sysInt, sysDbl, sysDbl, sysDbl, 
                                                sysDbl, sysDbl, sysDbl, sysDbl, sysDbl, sysDbl, sysDbl, sysDbl)
            
            # 循环读取所有光线结果
            while output[0]:  # success flag
                # 检查错误码和渐晕码
                if output[2] == 0 and output[3] == 0:  # 有效光线
                    x_coords.append(output[4])  # 像面X坐标
                    y_coords.append(output[5])  # 像面Y坐标
                
                # 读取下一条光线
                output = normUnPolData.ReadNextResult(sysInt, sysInt, sysInt, sysDbl, sysDbl, sysDbl,
                                                    sysDbl, sysDbl, sysDbl, sysDbl, sysDbl, sysDbl, sysDbl, sysDbl)
            
            # 计算RMS半径
            if x_coords and y_coords:
                x_arr = np.array(x_coords)
                y_arr = np.array(y_coords)
                rms_radius = np.sqrt(np.mean(x_arr**2 + y_arr**2))
            else:
                rms_radius = 0.0
            
            # 清理
            raytrace.Close()
            
            return {
                'x_coords': x_coords,
                'y_coords': y_coords,
                'rms_radius': rms_radius,
                'num_rays': len(x_coords),
                'field_index': field_index,
                'wavelength_index': wavelength_index
            }
            
        except Exception as e:
            logger.error(f"Spot diagram analysis failed: {e}")
            # 不创建仿真数据，明确报告分析失败
            return {
                'x_coords': [],
                'y_coords': [],
                'rms_radius': None,
                'num_rays': 0,
                'field_index': field_index,
                'wavelength_index': wavelength_index,
                'error': f'Batch ray trace failed: {str(e)}'
            }

    def _fallback_spot_analysis(self, field_index: int, wavelength_index: int, max_rays: int) -> Dict[str, Any]:
        """Fallback spot analysis using standard Zemax spot analysis - NO simulation data"""
        try:
            # 使用标准spot analysis - 只获取真实的Zemax数据
            analyses = self.zos.TheSystem.Analyses
            spot_analysis = analyses.New_Analysis(self.zos.ZOSAPI.Analysis.AnalysisIDM.StandardSpot)
            
            settings = spot_analysis.GetSettings()
            settings.Field.SetFieldNumber(field_index + 1)  # Convert to 1-based
            settings.Wavelength.SetWavelengthNumber(wavelength_index + 1)
            settings.RayDensity = 6  # High density for more rays
            
            spot_analysis.ApplyAndWaitForCompletion()
            results = spot_analysis.GetResults()
            
            # 尝试从真实的Zemax结果中提取数据
            try:
                # 获取RMS值 - 这是真实的分析结果
                rms_radius = results.SpotData.GetRMSSpotSizeFor(field_index + 1, wavelength_index + 1)
                
                # 尝试获取真实的光线数据
                # 注意：标准Spot Analysis可能不直接提供光线坐标
                # 我们需要报告这个限制而不是创建假数据
                logger.warning("Standard spot analysis does not provide individual ray coordinates")
                
                # 返回真实的RMS数据，但说明坐标数据不可用
                result = {
                    'x_coords': [],  # 真实分析中不可用
                    'y_coords': [],  # 真实分析中不可用  
                    'rms_radius': rms_radius,  # 真实的RMS值
                    'num_rays': 0,  # 无法获取单独光线
                    'field_index': field_index,
                    'wavelength_index': wavelength_index,
                    'analysis_type': 'standard_spot_rms_only'  # 标记数据类型
                }
                
            except Exception as e:
                logger.error(f"Failed to extract data from Zemax spot analysis: {e}")
                # 连真实数据都无法获取，返回错误信息
                result = {
                    'x_coords': [],
                    'y_coords': [],
                    'rms_radius': None,
                    'num_rays': 0,
                    'field_index': field_index,
                    'wavelength_index': wavelength_index,
                    'error': 'Failed to extract real Zemax data'
                }
            
            spot_analysis.Close()
            return result
            
        except Exception as e:
            logger.error(f"Fallback spot analysis failed: {e}")
            # 完全失败时，明确报告无法获取真实数据
            return {
                'x_coords': [],
                'y_coords': [],
                'rms_radius': None,
                'num_rays': 0,
                'field_index': field_index,
                'wavelength_index': wavelength_index,
                'error': f'Analysis failed: {str(e)}'
            }

    def analyze_wavefront(self, field_index: int = 1, wavelength_index: int = 1,
                         surface_index: Optional[int] = None,
                         sampling: int = 32) -> Dict[str, Any]:
        """
        分析波前 - 使用真实的Zemax波前分析
        
        Args:
            field_index: 视场索引 (1-based)
            wavelength_index: 波长索引 (1-based)
            surface_index: 面索引，None 表示像面
            sampling: 采样点数
            
        Returns:
            波前分析结果
        """
        try:
            # 使用真实的Zemax波前分析
            analyses = self.zos.TheSystem.Analyses
            wf_analysis = analyses.New_Analysis(self.zos.ZOSAPI.Analysis.AnalysisIDM.WavefrontMap)
            
            settings = wf_analysis.GetSettings()
            settings.Field.SetFieldNumber(field_index)
            settings.Wavelength.SetWavelengthNumber(wavelength_index)
            if surface_index is not None:
                settings.Surface = surface_index
            
            wf_analysis.ApplyAndWaitForCompletion()
            results = wf_analysis.GetResults()
            
            # 尝试从真实结果中提取数据
            try:
                # 这里需要根据实际的Zemax API来提取波前数据
                # 注意：不同版本的API可能有不同的方法
                logger.warning("Wavefront data extraction depends on specific Zemax API version")
                
                # 获取基本的波前统计信息
                rms_wfe = None
                pv_wfe = None
                
                # 如果无法提取详细数据，至少报告分析已完成
                result = {
                    "wavefront": None,  # 详细波前数据需要API支持
                    "x_coords": None,
                    "y_coords": None,
                    "mask": None,
                    "rms_wfe": rms_wfe,
                    "pv_wfe": pv_wfe,
                    "shape": (sampling, sampling),
                    "field_index": field_index,
                    "wavelength_index": wavelength_index,
                    "surface_index": surface_index,
                    "sampling": sampling,
                    "analysis_type": "real_zemax_wavefront",
                    "note": "Detailed wavefront data extraction requires specific API support"
                }
                
            except Exception as e:
                logger.error(f"Failed to extract wavefront data: {e}")
                result = {
                    "wavefront": None,
                    "x_coords": None,
                    "y_coords": None,
                    "mask": None,
                    "rms_wfe": None,
                    "pv_wfe": None,
                    "shape": (sampling, sampling),
                    "field_index": field_index,
                    "wavelength_index": wavelength_index,
                    "surface_index": surface_index,
                    "sampling": sampling,
                    "error": f"Failed to extract wavefront data: {str(e)}"
                }
            
            wf_analysis.Close()
            return result
            
        except Exception as e:
            logger.error(f"波前分析失败: {str(e)}")
            # 不创建仿真数据，报告真实的失败
            return {
                "wavefront": None,
                "x_coords": None,
                "y_coords": None,
                "mask": None,
                "rms_wfe": None,
                "pv_wfe": None,
                "shape": (sampling, sampling),
                "field_index": field_index,
                "wavelength_index": wavelength_index,
                "surface_index": surface_index,
                "sampling": sampling,
                "error": f"Wavefront analysis failed: {str(e)}"
            }
    
    def analyze_mtf(self, field_index: int = 0, wavelength_index: int = 0,
                   frequency_type: str = "CyclesPerMM",
                   max_frequency: float = 100.0,
                   num_points: int = 50) -> Dict[str, Any]:
        """
        分析 MTF (基于官方例程4的实现)
        
        Args:
            field_index: 视场索引 (0-based)
            wavelength_index: 波长索引 (0-based)
            frequency_type: 频率类型
            max_frequency: 最大频率
            num_points: 数据点数
            
        Returns:
            MTF 分析结果
        """
        try:
            # 获取分析器 - 严格按照例程4的方法
            analyses = self.zos.TheSystem.Analyses
            mtf_analysis = analyses.New_FftMtf()
            
            # 设置参数 - 完全参考例程4
            settings = mtf_analysis.GetSettings()
            settings.MaximumFrequency = max_frequency
            settings.SampleSize = self.zos.ZOSAPI.Analysis.SampleSizes.S_256x256
            
            # 运行分析
            mtf_analysis.ApplyAndWaitForCompletion()
            
            # 获取结果 - 严格按照例程4的方法
            results = mtf_analysis.GetResults()
            
            frequencies = []
            mtf_sagittal = []
            mtf_tangential = []
            
            try:
                # 按照例程4的方法提取数据：遍历所有数据序列
                for seriesNum in range(0, results.NumberOfDataSeries, 1):
                    data = results.GetDataSeries(seriesNum)
                    
                    # 获取X数据（频率）- 只需要获取一次
                    if not frequencies:
                        x_raw = data.XData.Data
                        frequencies = list(x_raw)
                    
                    # 获取Y数据（MTF值）- 使用例程4的reshape方法
                    y_raw = data.YData.Data
                    
                    # 定义reshape方法（从例程4中提取）
                    def reshape_data(data, x, y, transpose=False):
                        from itertools import islice
                        if type(data) is not list:
                            data = list(data)
                        var_lst = [y] * x
                        it = iter(data)
                        res = [list(islice(it, i)) for i in var_lst]
                        if transpose:
                            return list(map(list, zip(*res)))
                        return res
                    
                    y_reshaped = reshape_data(y_raw, y_raw.GetLength(0), y_raw.GetLength(1), True)
                    
                    # 第一个序列提取弧矢和子午MTF（例程4中y[0]是弧矢，y[1]是子午）
                    if seriesNum == 0:
                        mtf_tangential = y_reshaped[0]  # 第一条线是子午（tangential）
                        mtf_sagittal = y_reshaped[1]    # 第二条线是弧矢（sagittal）
                        break
                
                # 关闭分析
                mtf_analysis.Close()
                
                # 如果无法获取真实数据，报告失败而不是创建仿真数据
                if not frequencies:
                    logger.error("Failed to extract real MTF data from Zemax analysis")
                    frequencies = []
                    mtf_tangential = []
                    mtf_sagittal = []
                
            except Exception as e:
                logger.error(f"获取MTF数据失败: {str(e)}")
                # 不创建仿真数据，返回空结果
                frequencies = []
                mtf_tangential = []
                mtf_sagittal = []
                
                # 尝试关闭分析（如果还未关闭）
                try:
                    mtf_analysis.Close()
                except:
                    pass
                    pass
            
            result = {
                "frequencies": frequencies,
                "mtf_sagittal": mtf_sagittal,
                "mtf_tangential": mtf_tangential,
                "field_index": field_index,
                "wavelength_index": wavelength_index,
                "max_frequency": max_frequency,
                "num_points": len(frequencies)
            }
            
            return result
            
        except Exception as e:
            logger.error(f"MTF 分析失败: {str(e)}")
            raise
    
    def analyze_ray_fan(self, field_index: int = 0, wavelength_index: int = 0,
                       fan_type: str = "Y", num_rays: int = 21) -> Dict[str, Any]:
        """
        分析光线扇形图 (基于官方例程23的实现)
        
        Args:
            field_index: 视场索引 (0-based for internal use)
            wavelength_index: 波长索引 (0-based for internal use)
            fan_type: 扇形类型 ("X", "Y")
            num_rays: 光线数量
            
        Returns:
            光线扇形图分析结果
        """
        try:
            # Convert to 1-based for Zemax API
            zemax_field_idx = field_index + 1
            zemax_wave_idx = wavelength_index + 1
            
            # 获取分析器 - 严格按照例程23的方法
            analyses = self.zos.TheSystem.Analyses
            fan_analysis = analyses.New_Analysis(self.zos.ZOSAPI.Analysis.AnalysisIDM.RayFan)
            
            # 设置参数 - 参考例程23
            settings = fan_analysis.GetSettings()
            settings.NumberOfRays = int(num_rays / 2)  # 例程23中使用max_rays/2
            
            # 设置视场和波长 - 使用官方API方法（例程23中的精确实现）
            settings.Field.SetFieldNumber(zemax_field_idx)
            settings.Wavelength.SetWavelengthNumber(zemax_wave_idx)
            
            # 设置扇形类型（如果API支持）
            try:
                if fan_type.upper() == "X":
                    settings.Type = self.zos.ZOSAPI.Analysis.RayFan.RayFanTypes.X
                else:
                    settings.Type = self.zos.ZOSAPI.Analysis.RayFan.RayFanTypes.Y
            except:
                # 如果不支持设置类型，使用默认值
                pass
            
            # 运行分析
            fan_analysis.ApplyAndWaitForCompletion()
            
            # 获取结果 - 严格按照例程23的方法
            results = fan_analysis.GetResults()
            
            pupil_coords = []
            ray_errors = []
            
            try:
                # 按照例程23的方法提取数据
                # 例程23中使用了特定的数据提取方法
                if hasattr(results, 'GetDataSeries'):
                    # 尝试获取数据序列
                    data_series = results.GetDataSeries(0)  # 获取第一个数据序列
                    
                    # 获取X数据（瞳孔坐标）
                    x_data = data_series.XData.Data
                    pupil_coords = list(x_data)
                    
                    # 获取Y数据（光线误差）
                    y_data = data_series.YData.Data
                    if hasattr(y_data, 'GetLength') and y_data.GetLength(1) > 0:
                        # 多维数据，提取第一列
                        ray_errors = []
                        for i in range(y_data.GetLength(0)):
                            ray_errors.append(y_data[i, 0])
                    else:
                        # 一维数据
                        ray_errors = list(y_data)
                
                elif hasattr(results, 'Data'):
                    # 备用方法：直接从结果数据提取
                    data = results.Data
                    if data is not None:
                        # 尝试从真实数据中提取，不创建仿真数据
                        logger.warning("Cannot extract detailed ray fan data from results.Data")
                
                # 如果无法获取真实数据，报告失败而不是创建仿真数据
                if not pupil_coords:
                    logger.error("Failed to extract real ray fan data from Zemax analysis")
                    pupil_coords = []
                    ray_errors = []
                    
            except Exception as e:
                logger.error(f"获取光线扇形图数据失败: {str(e)}")
                # 不创建仿真数据，返回空结果
                pupil_coords = []
                ray_errors = []
            
            result = {
                "pupil_coords": pupil_coords,
                "ray_errors": ray_errors,
                "field_index": field_index,
                "wavelength_index": wavelength_index,
                "fan_type": fan_type,
                "num_rays": len(pupil_coords)
            }
            
            # 关闭分析
            fan_analysis.Close()
            
            return result
            
        except Exception as e:
            logger.error(f"光线扇形图分析失败: {str(e)}")
            raise
    
    def analyze_field_curvature_distortion(self) -> Dict[str, Any]:
        """
        分析场曲和畸变
        
        Returns:
            场曲和畸变分析结果
        """
        try:
            # 获取分析器
            analyses = self.zos.TheSystem.Analyses
            fc_analysis = analyses.New_Analysis(self.zos.ZOSAPI.Analysis.AnalysisIDM.FieldCurvatureAndDistortion)
            
            fc_analysis.ApplyAndWaitForCompletion()
            
            # 获取结果
            results = fc_analysis.GetResults()
            
            # 提取数据
            field_positions = extract_zos_vector(results.GetXData())
            sagittal_focus = extract_zos_vector(results.GetYData(0))
            tangential_focus = extract_zos_vector(results.GetYData(1))
            distortion = extract_zos_vector(results.GetYData(2))
            
            result = {
                "field_positions": field_positions,
                "sagittal_focus": sagittal_focus,
                "tangential_focus": tangential_focus,
                "distortion": distortion
            }
            
            # 关闭分析
            fc_analysis.Close()
            
            return result
            
        except Exception as e:
            logger.error(f"场曲和畸变分析失败: {str(e)}")
            raise
    
    def analyze_system_performance(self) -> Dict[str, Any]:
        """
        分析系统整体性能
        
        Returns:
            系统性能分析结果
        """
        try:
            # 收集多个分析结果
            performance = {}
            
            # 获取系统基本信息
            performance["system_info"] = self.zos.get_system_info()
            
            # 分析主要视场的点列图
            try:
                spot_results = []
                num_fields = self.zos.TheSystem.SystemData.Fields.NumberOfFields
                for field_idx in range(1, min(num_fields + 1, 4)):  # 最多分析3个视场
                    spot_data = self.analyze_spot_diagram(field_index=field_idx)
                    spot_results.append(spot_data)
                performance["spot_diagrams"] = spot_results
            except Exception as e:
                logger.warning(f"点列图分析失败: {str(e)}")
            
            # 分析 MTF
            try:
                mtf_data = self.analyze_mtf()
                performance["mtf"] = mtf_data
            except Exception as e:
                logger.warning(f"MTF 分析失败: {str(e)}")
            
            # 分析场曲和畸变
            try:
                fc_data = self.analyze_field_curvature_distortion()
                performance["field_curvature_distortion"] = fc_data
            except Exception as e:
                logger.warning(f"场曲和畸变分析失败: {str(e)}")
            
            # 分析波前
            try:
                wf_data = self.analyze_wavefront()
                performance["wavefront"] = wf_data
            except Exception as e:
                logger.warning(f"波前分析失败: {str(e)}")
            
            return performance
            
        except Exception as e:
            logger.error(f"系统性能分析失败: {str(e)}")
            raise
    
    def optimize_system(self, merit_function_type: str = "RMS",
                       max_iterations: int = 100,
                       target_improvement: float = 1e-6) -> Dict[str, Any]:
        """
        优化光学系统
        
        Args:
            merit_function_type: 评价函数类型
            max_iterations: 最大迭代次数
            target_improvement: 目标改善值
            
        Returns:
            优化结果
        """
        try:
            # 获取优化器
            local_optimization = self.zos.TheSystem.Tools.OpenLocalOptimization()
            
            # 设置优化参数
            local_optimization.Algorithm = self.zos.ZOSAPI.Tools.Optimization.OptimizationAlgorithm.DampedLeastSquares
            local_optimization.Cycles = self.zos.ZOSAPI.Tools.Optimization.OptimizationCycles.Automatic
            local_optimization.NumberOfCycles = max_iterations
            
            # 获取初始评价函数值
            initial_merit = local_optimization.InitialMeritFunction
            
            # 运行优化
            opt_result = local_optimization.RunAndWaitForCompletion()
            
            # 获取最终评价函数值
            final_merit = local_optimization.CurrentMeritFunction
            
            # 计算改善
            improvement = (initial_merit - final_merit) / initial_merit if initial_merit != 0 else 0
            
            result = {
                "success": opt_result == self.zos.ZOSAPI.Tools.Optimization.OptimizationReturn.Success,
                "initial_merit": initial_merit,
                "final_merit": final_merit,
                "improvement": improvement,
                "iterations": local_optimization.NumberOfCycles
            }
            
            # 关闭优化器
            local_optimization.Close()
            
            return result
            
        except Exception as e:
            logger.error(f"系统优化失败: {str(e)}")
            raise
    
    def quick_focus(self, surface_index: Optional[int] = None) -> Dict[str, Any]:
        """
        快速聚焦
        
        Args:
            surface_index: 面索引，None 表示像面
            
        Returns:
            聚焦结果
        """
        try:
            # 获取快速聚焦工具
            quick_focus_tool = self.zos.TheSystem.Tools.OpenQuickFocus()
            
            if surface_index is not None:
                quick_focus_tool.Surface = surface_index
            
            # 运行快速聚焦
            quick_focus_tool.RunAndWaitForCompletion()
            
            result = {
                "success": True,
                "surface_index": surface_index or "Image"
            }
            
            # 关闭工具
            quick_focus_tool.Close()
            
            return result
            
        except Exception as e:
            logger.error(f"快速聚焦失败: {str(e)}")
            raise


class BatchAnalyzer:
    """批量分析器"""
    
    def __init__(self, zos_manager: ZOSAPIManager):
        """
        初始化批量分析器
        
        Args:
            zos_manager: ZOSAPI 管理器实例
        """
        self.zos = zos_manager
        self.analyzer = ZOSAnalyzer(zos_manager)
    
    def analyze_all_fields_spots(self, wavelength_index: int = 1) -> List[Dict[str, Any]]:
        """
        分析所有视场的点列图
        
        Args:
            wavelength_index: 波长索引
            
        Returns:
            所有视场的点列图分析结果列表
        """
        results = []
        num_fields = self.zos.TheSystem.SystemData.Fields.NumberOfFields
        
        for field_idx in range(1, num_fields + 1):
            try:
                spot_data = self.analyzer.analyze_spot_diagram(
                    field_index=field_idx, 
                    wavelength_index=wavelength_index
                )
                results.append(spot_data)
            except Exception as e:
                logger.error(f"视场 {field_idx} 点列图分析失败: {str(e)}")
        
        return results
    
    def analyze_all_wavelengths_mtf(self, field_index: int = 1) -> List[Dict[str, Any]]:
        """
        分析所有波长的 MTF
        
        Args:
            field_index: 视场索引
            
        Returns:
            所有波长的 MTF 分析结果列表
        """
        results = []
        num_wavelengths = self.zos.TheSystem.SystemData.Wavelengths.NumberOfWavelengths
        
        for wl_idx in range(1, num_wavelengths + 1):
            try:
                mtf_data = self.analyzer.analyze_mtf(
                    field_index=field_index,
                    wavelength_index=wl_idx
                )
                results.append(mtf_data)
            except Exception as e:
                logger.error(f"波长 {wl_idx} MTF 分析失败: {str(e)}")
        
        return results


# === 便捷函数 ===

def quick_spot_analysis(zos_manager: ZOSAPIManager, field_index: int = 1) -> Dict[str, Any]:
    """快速点列图分析"""
    analyzer = ZOSAnalyzer(zos_manager)
    return analyzer.analyze_spot_diagram(field_index=field_index)


def quick_mtf_analysis(zos_manager: ZOSAPIManager, field_index: int = 1) -> Dict[str, Any]:
    """快速 MTF 分析"""
    analyzer = ZOSAnalyzer(zos_manager)
    return analyzer.analyze_mtf(field_index=field_index)


def quick_system_optimization(zos_manager: ZOSAPIManager) -> Dict[str, Any]:
    """快速系统优化"""
    analyzer = ZOSAnalyzer(zos_manager)
    return analyzer.optimize_system()
