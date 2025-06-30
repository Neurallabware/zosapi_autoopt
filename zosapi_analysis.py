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
            
            # 设置参数 - 完全按照官方例程23的方式
            settings = fan_analysis.GetSettings()
            settings.NumberOfRays = int(num_rays / 2)
            
            # 设置视场和波长 - 使用官方API方法
            settings.Field.SetFieldNumber(zemax_field_idx)
            settings.Wavelength.SetWavelengthNumber(zemax_wave_idx)
            
            # 使用默认设置（官方示例23不设置Sagittal和Tangential）
            # 这样会得到两个数据序列，分别对应两个方向
            
            logger.info(f"Ray Fan analysis: Field {zemax_field_idx}, Wavelength {zemax_wave_idx}, Fan type {fan_type}")
            
            # 运行分析
            fan_analysis.ApplyAndWaitForCompletion()
            
            # 获取结果 - 严格按照例程23的方法
            results = fan_analysis.GetResults()
            
            pupil_coords = []
            ray_errors = []
            
            try:
                # 按照例程23的精确方法提取数据
                if hasattr(results, 'GetDataSeries') and results.NumberOfDataSeries >= 2:
                    
                    # 根据fan_type选择正确的数据序列
                    # 基于测试结果：Series 0通常是Y方向，Series 1通常是X方向
                    if fan_type.upper() == "X":
                        series_idx = 1  # X Fan使用Series 1
                    else:
                        series_idx = 0  # Y Fan使用Series 0
                    
                    data_series = results.GetDataSeries(series_idx)
                    
                    # 完全按照官方示例的方法
                    x_raw = np.asarray(tuple(data_series.XData.Data))
                    y_raw = np.asarray(tuple(data_series.YData.Data))
                    
                    x = x_raw
                    y = y_raw.reshape(data_series.YData.Data.GetLength(0), data_series.YData.Data.GetLength(1))
                    
                    logger.info(f"Ray Fan data: x shape={x.shape}, y shape={y.shape}")
                    logger.info(f"Using series {series_idx} for {fan_type} fan")
                    logger.info(f"Y data range: {np.nanmin(y):.6f} to {np.nanmax(y):.6f}")
                    
                    # 现在提取第一列有效数据
                    pupil_coords = list(x)
                    
                    # 找到第一列有效（非NaN）数据
                    valid_col = None
                    for col in range(y.shape[1]):
                        col_data = y[:, col]
                        if not np.all(np.isnan(col_data)):
                            valid_col = col
                            break
                    
                    if valid_col is not None:
                        ray_errors = list(y[:, valid_col])
                        # 将NaN值替换为0
                        ray_errors = [0.0 if np.isnan(x) else x for x in ray_errors]
                    else:
                        # 如果没有找到有效列，使用指定波长的列并处理NaN
                        wave_col = min(wavelength_index, y.shape[1] - 1)
                        ray_errors = list(y[:, wave_col])
                        ray_errors = [0.0 if np.isnan(x) else x for x in ray_errors]
                    
                    logger.info(f"{fan_type} Fan data range: {min(ray_errors):.6f} to {max(ray_errors):.6f}")
                    
                    # 检查数据是否为零
                    if all(abs(val) < 1e-10 for val in ray_errors):
                        logger.warning(f"{fan_type} Fan data appears to be all zeros for field {zemax_field_idx}")
                    else:
                        logger.info(f"Successfully extracted non-zero {fan_type} fan data")
                    
                    logger.info(f"Extracted {fan_type} fan: {len(pupil_coords)} pupil coords, {len(ray_errors)} ray errors")
                
                else:
                    logger.error(f"Insufficient data series: {results.NumberOfDataSeries if hasattr(results, 'NumberOfDataSeries') else 0} (need at least 2)")
                    pupil_coords = []
                    ray_errors = []
                
                # 验证数据
                if not pupil_coords or not ray_errors:
                    logger.error("Failed to extract real ray fan data from Zemax analysis")
                    pupil_coords = []
                    ray_errors = []
                elif len(pupil_coords) != len(ray_errors):
                    logger.error(f"Mismatched data lengths: {len(pupil_coords)} coords vs {len(ray_errors)} errors")
                    pupil_coords = []
                    ray_errors = []
                else:
                    logger.info(f"Successfully extracted {len(pupil_coords)} ray fan data points for {fan_type} fan")
                    
            except Exception as e:
                logger.error(f"获取光线扇形图数据失败: {str(e)}")
                import traceback
                logger.error(f"Traceback: {traceback.format_exc()}")
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
    
    def analyze_field_curvature_distortion(self, num_points: int = 50, wavelength_index: int = 0) -> Dict[str, Any]:
        """
        分析场曲和畸变
        
        Args:
            num_points: 分析点数
            wavelength_index: 波长索引 (0-based for internal use)
            
        Returns:
            场曲和畸变分析结果
        """
        try:
            # Convert to 1-based for Zemax API
            zemax_wave_idx = wavelength_index + 1
            
            # 创建场曲和畸变分析
            analyses = self.zos.TheSystem.Analyses
            distortion_analysis = analyses.New_Analysis(self.zos.ZOSAPI.Analysis.AnalysisIDM.FieldCurvatureAndDistortion)
            
            # 设置参数
            settings = distortion_analysis.GetSettings()
            try:
                settings.NumberOfPoints = num_points
                # 设置波长
                if hasattr(settings, 'Wavelength'):
                    settings.Wavelength.SetWavelengthNumber(zemax_wave_idx)
                    wavelength = self.zos.TheSystem.SystemData.Wavelengths.GetWavelength(zemax_wave_idx)
                    wavelength_value = wavelength.Wavelength
                    logger.info(f"Field curvature and distortion analysis with {num_points} points, wavelength {zemax_wave_idx} ({wavelength_value:.3f}nm)")
                else:
                    logger.info(f"Field curvature and distortion analysis with {num_points} points (wavelength setting not available)")
            except Exception as e:
                logger.warning(f"Cannot set analysis parameters: {e}, using default settings")
                logger.info(f"Field curvature and distortion analysis (using default settings)")
            
            # 运行分析
            distortion_analysis.ApplyAndWaitForCompletion()
            results = distortion_analysis.GetResults()
            
            field_heights = []
            tangential_field_curvature = []
            sagittal_field_curvature = []
            distortion_percent = []
            
            try:
                # 检查数据结构
                if hasattr(results, 'NumberOfDataSeries') and results.NumberOfDataSeries > 0:
                    logger.info(f"Found {results.NumberOfDataSeries} data series")
                    
                    # Field Curvature and Distortion 分析通常有多个序列，对应不同的波长
                    # 每个序列的Y数据包含5列：[子午场曲, 弧矢场曲, ?, ?, 畸变%]
                    
                    # 找到有效的数据系列
                    for series_idx in range(results.NumberOfDataSeries):
                        try:
                            data_series = results.GetDataSeries(series_idx)
                            
                            # 获取X数据（视场高度）
                            x_raw = data_series.XData.Data
                            x = np.asarray(tuple(x_raw))
                            
                            # 获取Y数据（场曲和畸变）
                            y_raw = data_series.YData.Data
                            y_raw_list = list(y_raw)
                            
                            # 检查Y数据维度
                            y = None
                            try:
                                y_dim0 = y_raw.GetLength(0)
                                y_dim1 = y_raw.GetLength(1)
                                y = np.array(y_raw_list).reshape(y_dim0, y_dim1)
                                logger.info(f"Series {series_idx}: x shape={x.shape}, y shape={y.shape}")
                            except Exception as y_err:
                                logger.warning(f"Cannot reshape Y data: {y_err}")
                                continue
                            
                            logger.info(f"Series {series_idx}: X data range: {x.min():.6f} to {x.max():.6f}")
                            
                            # 检查X数据是否有效
                            x_range_valid = abs(x.max() - x.min()) > 1e-6
                            
                            # 检查Y数据形状是否有效（至少有5列）
                            if y is not None and len(y.shape) > 1 and y.shape[1] >= 5:
                                # 处理X数据全为0的情况
                                if not x_range_valid:
                                    # 尝试使用Y数据的第2列作为视场高度
                                    logger.info("X data range invalid, using Y column 2 for field heights")
                                    field_height_col = 2  # 第2列，索引从0开始
                                    
                                    if field_height_col < y.shape[1]:
                                        x = y[:, field_height_col]
                                        x_range_valid = abs(x.max() - x.min()) > 1e-6
                                        logger.info(f"Using Y column {field_height_col} as field heights: {x.min():.6f} to {x.max():.6f}")
                                
                                # 如果X数据有效（原始有效或使用Y列构造的有效）
                                if x_range_valid:
                                    # 设置视场高度
                                    field_heights = list(x)
                                    
                                    # 提取场曲数据
                                    tangential_fc_raw = y[:, 0]
                                    sagittal_fc_raw = y[:, 1]
                                    tangential_field_curvature = list(tangential_fc_raw)
                                    sagittal_field_curvature = list(sagittal_fc_raw)
                                    
                                    logger.info(f"Tangential FC range: {min(tangential_field_curvature):.6f} to {max(tangential_field_curvature):.6f}")
                                    logger.info(f"Sagittal FC range: {min(sagittal_field_curvature):.6f} to {max(sagittal_field_curvature):.6f}")
                                    
                                    # 提取畸变数据
                                    distortion_raw = y[:, 4]
                                    distortion_percent = list(distortion_raw)
                                    logger.info(f"Distortion range: {min(distortion_percent):.6f} to {max(distortion_percent):.6f}%")
                                    
                                    # 找到有效数据后退出循环
                                    break
                                else:
                                    logger.warning(f"Series {series_idx}: No valid X range found after correction")
                            else:
                                logger.warning(f"Series {series_idx}: Y data shape invalid or insufficient columns")
                                
                        except Exception as e:
                            logger.warning(f"Error processing series {series_idx}: {e}")
                            continue
                
                # 检查是否提取到数据
                if not field_heights:
                    logger.warning("No field curvature/distortion data extracted")
                else:
                    logger.info(f"Final extracted data: {len(field_heights)} field points")
                    if tangential_field_curvature:
                        logger.info(f"Tangential FC: {len(tangential_field_curvature)} points, range: {min(tangential_field_curvature):.6f} to {max(tangential_field_curvature):.6f}")
                    if sagittal_field_curvature:
                        logger.info(f"Sagittal FC: {len(sagittal_field_curvature)} points, range: {min(sagittal_field_curvature):.6f} to {max(sagittal_field_curvature):.6f}")
                    if distortion_percent:
                        logger.info(f"Distortion: {len(distortion_percent)} points, range: {min(distortion_percent):.6f}% to {max(distortion_percent):.6f}%")
                    else:
                        logger.warning("No distortion data available")
                
            except Exception as e:
                logger.error(f"提取场曲畸变数据失败: {str(e)}")
                import traceback
                logger.error(f"详细错误: {traceback.format_exc()}")
                field_heights = []
                tangential_field_curvature = []
                sagittal_field_curvature = []
                distortion_percent = []
            
            result = {
                "field_heights": field_heights,
                "tangential_field_curvature": tangential_field_curvature,
                "sagittal_field_curvature": sagittal_field_curvature,
                "distortion_percent": distortion_percent,
                "num_points": len(field_heights),
                "wavelength_index": wavelength_index
            }
            
            # 添加波长值信息
            try:
                wavelength = self.zos.TheSystem.SystemData.Wavelengths.GetWavelength(zemax_wave_idx)
                result["wavelength_value"] = wavelength.Wavelength
            except Exception as e:
                logger.warning(f"Unable to get wavelength value: {e}")
                result["wavelength_value"] = 0
            
            distortion_analysis.Close()
            return result
            
        except Exception as e:
            logger.error(f"场曲畸变分析失败: {str(e)}")
            raise
    



class BatchAnalyzer:
    """
    批量分析类，用于处理多个光学系统或配置的分析
    """
    
    def __init__(self, zos_manager):
        """
        初始化批量分析器
        
        Args:
            zos_manager: ZOSAPI管理器实例
        """
        import matplotlib.pyplot as plt
        self.zos_manager = zos_manager
        self.analyzer = ZOSAnalyzer(zos_manager)
        self.results = {}
        self.plt = plt
        
    def analyze_multiple_files(self, file_paths: List[str], 
                              analysis_types: List[str] = None,
                              output_dir: str = "batch_output") -> Dict:
        """
        批量分析多个光学文件
        
        Args:
            file_paths: 光学文件路径列表
            analysis_types: 分析类型列表 ['spot', 'rayfan', 'mtf', 'distortion']
            output_dir: 输出目录
            
        Returns:
            分析结果字典
        """
        from pathlib import Path
        import os
        
        if analysis_types is None:
            analysis_types = ['spot', 'rayfan', 'mtf']
            
        output_path = Path(output_dir)
        output_path.mkdir(parents=True, exist_ok=True)
        
        batch_results = {}
        
        for file_path in file_paths:
            try:
                file_name = Path(file_path).stem
                logger.info(f"分析文件: {file_name}")
                
                # 打开文件
                self.zos_manager.open_file(file_path)
                
                # 创建文件专用输出目录
                file_output_dir = output_path / file_name
                file_output_dir.mkdir(exist_ok=True)
                
                file_results = {}
                
                # 执行指定的分析
                if 'spot' in analysis_types:
                    try:
                        from zosapi_plotting import plot_spots
                        fig = plot_spots(
                            self.zos_manager, self.analyzer,
                            fields="all", wavelengths="all",
                            save_path=str(file_output_dir / "spots.png")
                        )
                        self.plt.close(fig)
                        file_results['spot'] = str(file_output_dir / "spots.png")
                    except Exception as e:
                        logger.error(f"点列图分析失败 {file_name}: {e}")
                        
                if 'rayfan' in analysis_types:
                    try:
                        from zosapi_plotting import plot_rayfan
                        fig = plot_rayfan(
                            self.zos_manager, self.analyzer,
                            fields="all", wavelengths="single",
                            save_path=str(file_output_dir / "rayfan.png")
                        )
                        self.plt.close(fig)
                        file_results['rayfan'] = str(file_output_dir / "rayfan.png")
                    except Exception as e:
                        logger.error(f"Ray Fan分析失败 {file_name}: {e}")
                        
                if 'mtf' in analysis_types:
                    try:
                        from zosapi_plotting import plot_mtf
                        fig = plot_mtf(
                            self.zos_manager,
                            fields="all", wavelengths="all",
                            save_path=str(file_output_dir / "mtf.png")
                        )
                        self.plt.close(fig)
                        file_results['mtf'] = str(file_output_dir / "mtf.png")
                    except Exception as e:
                        logger.error(f"MTF分析失败 {file_name}: {e}")
                        
                if 'distortion' in analysis_types:
                    try:
                        from zosapi_plotting import plot_field_curvature_distortion
                        fig = plot_field_curvature_distortion(
                            self.zos_manager, self.analyzer,
                            save_path=str(file_output_dir / "distortion.png")
                        )
                        self.plt.close(fig)
                        file_results['distortion'] = str(file_output_dir / "distortion.png")
                    except Exception as e:
                        logger.error(f"畸变分析失败 {file_name}: {e}")
                
                batch_results[file_name] = file_results
                logger.info(f"完成文件分析: {file_name}")
                
            except Exception as e:
                logger.error(f"处理文件失败 {file_path}: {e}")
                batch_results[Path(file_path).stem] = {"error": str(e)}
        
        # 生成批量分析报告
        self._generate_batch_report(batch_results, output_path)
        
        return batch_results
    
    def analyze_configuration_sweep(self, config_parameter: str, 
                                   values: List[float],
                                   analysis_types: List[str] = None,
                                   output_dir: str = "config_sweep") -> Dict:
        """
        参数扫描分析
        
        Args:
            config_parameter: 配置参数名称
            values: 参数值列表
            analysis_types: 分析类型列表
            output_dir: 输出目录
            
        Returns:
            扫描分析结果
        """
        from pathlib import Path
        
        if analysis_types is None:
            analysis_types = ['spot', 'rayfan']
            
        output_path = Path(output_dir)
        output_path.mkdir(parents=True, exist_ok=True)
        
        sweep_results = {}
        
        for i, value in enumerate(values):
            try:
                logger.info(f"分析配置 {config_parameter}={value}")
                
                # 这里需要根据具体参数修改系统配置
                # 示例：修改焦距或其他参数
                # self._modify_system_parameter(config_parameter, value)
                
                config_name = f"{config_parameter}_{value:.3f}"
                config_output_dir = output_path / config_name
                config_output_dir.mkdir(exist_ok=True)
                
                config_results = {}
                
                # 执行分析
                if 'spot' in analysis_types:
                    spot_data = self.analyzer.analyze_spot_diagram(field_index=0, wavelength_index=0)
                    config_results['rms_size'] = spot_data.get('rms_size', None)
                    
                if 'rayfan' in analysis_types:
                    rayfan_data = self.analyzer.analyze_ray_fan(field_index=0, wavelength_index=0)
                    config_results['max_ray_error'] = max(abs(min(rayfan_data['ray_errors'])), 
                                                         abs(max(rayfan_data['ray_errors'])))
                
                sweep_results[config_name] = config_results
                
            except Exception as e:
                logger.error(f"配置分析失败 {config_parameter}={value}: {e}")
                sweep_results[f"{config_parameter}_{value:.3f}"] = {"error": str(e)}
        
        return sweep_results
    
    def _generate_batch_report(self, batch_results: Dict, output_path):
        """
        生成批量分析报告
        
        Args:
            batch_results: 批量分析结果
            output_path: 输出路径
        """
        from pathlib import Path
        report_path = Path(output_path) / "batch_analysis_report.txt"
        
        with open(report_path, 'w', encoding='utf-8') as f:
            f.write("ZOSAPI 批量分析报告\n")
            f.write("=" * 50 + "\n\n")
            
            for file_name, results in batch_results.items():
                f.write(f"文件: {file_name}\n")
                f.write("-" * 30 + "\n")
                
                if "error" in results:
                    f.write(f"错误: {results['error']}\n")
                else:
                    for analysis_type, result_path in results.items():
                        f.write(f"{analysis_type}: {result_path}\n")
                
                f.write("\n")
        
        logger.info(f"批量分析报告已保存: {report_path}")
    
    def compare_systems(self, system_files: List[str], 
                       analysis_type: str = "spot",
                       output_dir: str = "comparison") -> Dict:
        """
        比较多个光学系统的性能
        
        Args:
            system_files: 系统文件列表
            analysis_type: 比较的分析类型
            output_dir: 输出目录
            
        Returns:
            比较结果
        """
        from pathlib import Path
        import matplotlib.pyplot as plt
        
        output_path = Path(output_dir)
        output_path.mkdir(parents=True, exist_ok=True)
        
        comparison_results = {}
        
        # 收集所有系统的数据
        all_data = {}
        
        for file_path in system_files:
            try:
                file_name = Path(file_path).stem
                self.zos_manager.open_file(file_path)
                
                if analysis_type == "spot":
                    spot_data = self.analyzer.analyze_spot_diagram(field_index=0, wavelength_index=0)
                    all_data[file_name] = {
                        'rms_size': spot_data.get('rms_size', 0),
                        'geo_size': spot_data.get('geo_size', 0)
                    }
                elif analysis_type == "rayfan":
                    rayfan_data = self.analyzer.analyze_ray_fan(field_index=0, wavelength_index=0)
                    max_error = max(abs(min(rayfan_data['ray_errors'])), 
                                  abs(max(rayfan_data['ray_errors'])))
                    all_data[file_name] = {'max_ray_error': max_error}
                    
            except Exception as e:
                logger.error(f"比较分析失败 {file_path}: {e}")
                all_data[Path(file_path).stem] = {"error": str(e)}
        
        # 创建比较图表
        if analysis_type == "spot" and all_data:
            fig, (ax1, ax2) = self.plt.subplots(1, 2, figsize=(12, 5))
            
            systems = list(all_data.keys())
            rms_sizes = [all_data[sys].get('rms_size', 0) for sys in systems]
            geo_sizes = [all_data[sys].get('geo_size', 0) for sys in systems]
            
            ax1.bar(systems, rms_sizes)
            ax1.set_title('RMS Spot Size Comparison')
            ax1.set_ylabel('RMS Size (mm)')
            ax1.tick_params(axis='x', rotation=45)
            
            ax2.bar(systems, geo_sizes)
            ax2.set_title('Geometric Spot Size Comparison')
            ax2.set_ylabel('Geometric Size (mm)')
            ax2.tick_params(axis='x', rotation=45)
            
            self.plt.tight_layout()
            self.plt.savefig(output_path / "system_comparison.png", dpi=300, bbox_inches='tight')
            self.plt.close()
            
            comparison_results['plot'] = str(output_path / "system_comparison.png")
        
        comparison_results['data'] = all_data
        return comparison_results
