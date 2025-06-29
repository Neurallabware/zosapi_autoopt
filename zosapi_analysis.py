"""
Zemax OpticStudio Python API 分析模块
提供各种光学分析功能的封装
Author: Your Name
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
    
    def analyze_spot_diagram(self, field_index: int = 1, wavelength_index: int = 1,
                           surface_index: Optional[int] = None, 
                           ray_density: int = 3) -> Dict[str, Any]:
        """
        分析点列图
        
        Args:
            field_index: 视场索引 (1-based)
            wavelength_index: 波长索引 (1-based) 
            surface_index: 面索引，None 表示像面
            ray_density: 光线密度 (1-8)
            
        Returns:
            点列图分析结果
        """
        try:
            # 获取分析器
            analyses = self.zos.TheSystem.Analyses
            spot_analysis = analyses.New_Analysis(self.zos.ZOSAPI.Analysis.AnalysisIDM.StandardSpotDiagram)
            
            # 设置参数
            settings = spot_analysis.GetSettings()
            settings.Field.SetFieldNumber(field_index)
            settings.Wavelength.SetWavelengthNumber(wavelength_index)
            
            if surface_index is not None:
                settings.Surface.SetSurfaceNumber(surface_index)
            
            # 设置光线密度
            settings.RayDensity = ray_density
            spot_analysis.ApplyAndWaitForCompletion()
            
            # 获取结果
            results = spot_analysis.GetResults()
            
            # 提取数据
            x_data = extract_zos_vector(results.GetXData())
            y_data = extract_zos_vector(results.GetYData())
            
            # 处理数据
            processed_data = self.data_processor.process_spot_diagram_data(results)
            
            # 添加额外信息
            processed_data.update({
                "field_index": field_index,
                "wavelength_index": wavelength_index,
                "surface_index": surface_index,
                "ray_density": ray_density
            })
            
            # 关闭分析
            spot_analysis.Close()
            
            return processed_data
            
        except Exception as e:
            logger.error(f"点列图分析失败: {str(e)}")
            raise
    
    def analyze_wavefront(self, field_index: int = 1, wavelength_index: int = 1,
                         surface_index: Optional[int] = None,
                         sampling: int = 32) -> Dict[str, Any]:
        """
        分析波前
        
        Args:
            field_index: 视场索引 (1-based)
            wavelength_index: 波长索引 (1-based)
            surface_index: 面索引，None 表示像面
            sampling: 采样点数
            
        Returns:
            波前分析结果
        """
        try:
            # 获取分析器
            analyses = self.zos.TheSystem.Analyses
            wf_analysis = analyses.New_Analysis(self.zos.ZOSAPI.Analysis.AnalysisIDM.WavefrontMap)
            
            # 设置参数
            settings = wf_analysis.GetSettings()
            settings.Field.SetFieldNumber(field_index)
            settings.Wavelength.SetWavelengthNumber(wavelength_index)
            
            if surface_index is not None:
                settings.Surface.SetSurfaceNumber(surface_index)
            
            # 设置采样
            settings.SampleSize = sampling
            wf_analysis.ApplyAndWaitForCompletion()
            
            # 获取结果
            results = wf_analysis.GetResults()
            
            # 提取波前数据
            shape = (sampling, sampling)
            wavefront_data = results.GetDataGrid()
            
            # 处理数据
            processed_data = self.data_processor.process_wavefront_data(wavefront_data, shape)
            
            # 添加额外信息
            processed_data.update({
                "field_index": field_index,
                "wavelength_index": wavelength_index,
                "surface_index": surface_index,
                "sampling": sampling
            })
            
            # 关闭分析
            wf_analysis.Close()
            
            return processed_data
            
        except Exception as e:
            logger.error(f"波前分析失败: {str(e)}")
            raise
    
    def analyze_mtf(self, field_index: int = 1, wavelength_index: int = 1,
                   frequency_type: str = "CyclesPerMM",
                   max_frequency: float = 100.0,
                   num_points: int = 50) -> Dict[str, Any]:
        """
        分析 MTF
        
        Args:
            field_index: 视场索引 (1-based)
            wavelength_index: 波长索引 (1-based)
            frequency_type: 频率类型
            max_frequency: 最大频率
            num_points: 数据点数
            
        Returns:
            MTF 分析结果
        """
        try:
            # 获取分析器
            analyses = self.zos.TheSystem.Analyses
            mtf_analysis = analyses.New_Analysis(self.zos.ZOSAPI.Analysis.AnalysisIDM.FftMtf)
            
            # 设置参数
            settings = mtf_analysis.GetSettings()
            settings.Field.SetFieldNumber(field_index)
            settings.Wavelength.SetWavelengthNumber(wavelength_index)
            
            # 设置频率
            settings.MaximumFrequency = max_frequency
            settings.NumberOfDataPoints = num_points
            
            mtf_analysis.ApplyAndWaitForCompletion()
            
            # 获取结果
            results = mtf_analysis.GetResults()
            
            # 提取数据
            frequencies = extract_zos_vector(results.GetXData())
            mtf_sagittal = extract_zos_vector(results.GetYData(0))  # 弧矢方向
            mtf_tangential = extract_zos_vector(results.GetYData(1))  # 子午方向
            
            result = {
                "frequencies": frequencies,
                "mtf_sagittal": mtf_sagittal,
                "mtf_tangential": mtf_tangential,
                "field_index": field_index,
                "wavelength_index": wavelength_index,
                "max_frequency": max_frequency,
                "num_points": num_points
            }
            
            # 关闭分析
            mtf_analysis.Close()
            
            return result
            
        except Exception as e:
            logger.error(f"MTF 分析失败: {str(e)}")
            raise
    
    def analyze_ray_fan(self, field_index: int = 1, wavelength_index: int = 1,
                       fan_type: str = "Y") -> Dict[str, Any]:
        """
        分析光线扇形图
        
        Args:
            field_index: 视场索引 (1-based)
            wavelength_index: 波长索引 (1-based)
            fan_type: 扇形类型 ("X", "Y")
            
        Returns:
            光线扇形图分析结果
        """
        try:
            # 获取分析器
            analyses = self.zos.TheSystem.Analyses
            fan_analysis = analyses.New_Analysis(self.zos.ZOSAPI.Analysis.AnalysisIDM.RayFan)
            
            # 设置参数
            settings = fan_analysis.GetSettings()
            settings.Field.SetFieldNumber(field_index)
            settings.Wavelength.SetWavelengthNumber(wavelength_index)
            
            # 设置扇形类型
            if fan_type.upper() == "X":
                settings.Type = self.zos.ZOSAPI.Analysis.RayFan.RayFanTypes.X
            else:
                settings.Type = self.zos.ZOSAPI.Analysis.RayFan.RayFanTypes.Y
            
            fan_analysis.ApplyAndWaitForCompletion()
            
            # 获取结果
            results = fan_analysis.GetResults()
            
            # 提取数据
            pupil_coords = extract_zos_vector(results.GetXData())
            ray_errors = extract_zos_vector(results.GetYData())
            
            result = {
                "pupil_coords": pupil_coords,
                "ray_errors": ray_errors,
                "field_index": field_index,
                "wavelength_index": wavelength_index,
                "fan_type": fan_type
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
            final_merit = local_optimization.FinalMeritFunction
            
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
            focus_result = quick_focus_tool.RunAndWaitForCompletion()
            
            result = {
                "success": focus_result == self.zos.ZOSAPI.Tools.General.QuickFocusReturn.Success,
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
