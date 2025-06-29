"""
Zemax OpticStudio Python API 工具函数模块
提供常用的数据处理、转换和辅助功能
Author: Your Name
Date: 2025-06-29
"""

import numpy as np
import pandas as pd
from typing import List, Tuple, Optional, Union, Any
import logging

logger = logging.getLogger(__name__)


def reshape_zos_data(data: Any, x: int, y: int, transpose: bool = False) -> List[List[float]]:
    """
    将 System.Double[,] 转换为 2D 列表用于绘图或后处理
    
    Args:
        data: Zemax 返回的 2D 数组数据
        x: X 维度大小
        y: Y 维度大小
        transpose: 是否转置数据
        
    Returns:
        2D 列表数据
    """
    try:
        # 将 .NET 数组转换为 numpy 数组
        arr = np.array([[data[i, j] for j in range(y)] for i in range(x)])
        
        if transpose:
            arr = arr.T
            
        return arr.tolist()
    
    except Exception as e:
        logger.error(f"数据重塑失败: {str(e)}")
        raise


def zos_array_to_numpy(data: Any, shape: Optional[Tuple[int, int]] = None) -> np.ndarray:
    """
    将 Zemax 数组转换为 numpy 数组
    
    Args:
        data: Zemax 数组数据
        shape: 目标形状 (rows, cols)
        
    Returns:
        numpy 数组
    """
    try:
        if shape is None:
            # 尝试自动检测形状
            if hasattr(data, 'GetLength'):
                rows = data.GetLength(0)
                cols = data.GetLength(1)
            else:
                # 假设是 1D 数组
                return np.array(list(data))
        else:
            rows, cols = shape
        
        # 转换为 numpy 数组
        arr = np.array([[data[i, j] for j in range(cols)] for i in range(rows)])
        return arr
    
    except Exception as e:
        logger.error(f"数组转换失败: {str(e)}")
        raise


def zos_array_to_dataframe(data: Any, 
                          shape: Optional[Tuple[int, int]] = None,
                          columns: Optional[List[str]] = None,
                          index: Optional[List[str]] = None) -> pd.DataFrame:
    """
    将 Zemax 数组转换为 pandas DataFrame
    
    Args:
        data: Zemax 数组数据
        shape: 目标形状 (rows, cols)
        columns: 列名列表
        index: 行索引列表
        
    Returns:
        pandas DataFrame
    """
    try:
        # 先转换为 numpy 数组
        arr = zos_array_to_numpy(data, shape)
        
        # 创建 DataFrame
        df = pd.DataFrame(arr, columns=columns, index=index)
        return df
    
    except Exception as e:
        logger.error(f"DataFrame 转换失败: {str(e)}")
        raise


def extract_zos_vector(vector_data: Any) -> List[float]:
    """
    从 Zemax 向量数据中提取数值列表
    
    Args:
        vector_data: Zemax 向量数据
        
    Returns:
        数值列表
    """
    try:
        if hasattr(vector_data, 'Count'):
            return [vector_data[i] for i in range(vector_data.Count)]
        else:
            return list(vector_data)
    
    except Exception as e:
        logger.error(f"向量提取失败: {str(e)}")
        raise


def create_field_coordinates(field_type: str, 
                           field_values: List[Tuple[float, float]]) -> List[dict]:
    """
    创建视场坐标信息
    
    Args:
        field_type: 视场类型 ("Angle", "ObjectHeight", "ParaxialImageHeight", "RealImageHeight")
        field_values: 视场值列表 [(x1, y1), (x2, y2), ...]
        
    Returns:
        视场信息字典列表
    """
    fields = []
    for i, (x, y) in enumerate(field_values):
        field_info = {
            "index": i + 1,
            "type": field_type,
            "x": x,
            "y": y,
            "weight": 1.0  # 默认权重
        }
        fields.append(field_info)
    
    return fields


def create_wavelength_info(wavelengths: List[float], weights: Optional[List[float]] = None) -> List[dict]:
    """
    创建波长信息
    
    Args:
        wavelengths: 波长列表 (微米)
        weights: 权重列表
        
    Returns:
        波长信息字典列表
    """
    if weights is None:
        weights = [1.0] * len(wavelengths)
    
    wavelength_info = []
    for i, (wl, weight) in enumerate(zip(wavelengths, weights)):
        wl_info = {
            "index": i + 1,
            "wavelength": wl,
            "weight": weight
        }
        wavelength_info.append(wl_info)
    
    return wavelength_info


def degrees_to_radians(degrees: float) -> float:
    """角度转弧度"""
    return degrees * np.pi / 180.0


def radians_to_degrees(radians: float) -> float:
    """弧度转角度"""
    return radians * 180.0 / np.pi


def microns_to_mm(microns: float) -> float:
    """微米转毫米"""
    return microns / 1000.0


def mm_to_microns(mm: float) -> float:
    """毫米转微米"""
    return mm * 1000.0


def calculate_rms_error(data: np.ndarray) -> float:
    """
    计算 RMS 误差
    
    Args:
        data: 数据数组
        
    Returns:
        RMS 值
    """
    return np.sqrt(np.mean(data**2))


def calculate_pv_error(data: np.ndarray) -> float:
    """
    计算 Peak-to-Valley 误差
    
    Args:
        data: 数据数组
        
    Returns:
        PV 值
    """
    return np.max(data) - np.min(data)


def remove_piston_tilt(data: np.ndarray, x_coords: np.ndarray, y_coords: np.ndarray) -> np.ndarray:
    """
    移除数据中的倾斜和平移
    
    Args:
        data: 原始数据
        x_coords: X 坐标
        y_coords: Y 坐标
        
    Returns:
        移除倾斜和平移后的数据
    """
    try:
        # 构建系数矩阵 [1, x, y]
        valid_mask = ~np.isnan(data.flatten())
        A = np.column_stack([
            np.ones(x_coords.flatten()[valid_mask].shape),
            x_coords.flatten()[valid_mask],
            y_coords.flatten()[valid_mask]
        ])
        
        # 最小二乘拟合
        coeffs, _, _, _ = np.linalg.lstsq(A, data.flatten()[valid_mask], rcond=None)
        
        # 计算拟合平面
        fitted_plane = (coeffs[0] + 
                       coeffs[1] * x_coords + 
                       coeffs[2] * y_coords)
        
        # 移除拟合平面
        corrected_data = data - fitted_plane
        
        return corrected_data
    
    except Exception as e:
        logger.error(f"移除倾斜和平移失败: {str(e)}")
        return data


def circular_mask(shape: Tuple[int, int], center: Optional[Tuple[int, int]] = None, 
                 radius: Optional[float] = None) -> np.ndarray:
    """
    创建圆形掩膜
    
    Args:
        shape: 数组形状 (height, width)
        center: 圆心坐标 (y, x)，默认为中心
        radius: 半径，默认为最小维度的一半
        
    Returns:
        布尔掩膜数组
    """
    h, w = shape
    if center is None:
        center = (h // 2, w // 2)
    if radius is None:
        radius = min(h, w) // 2
    
    cy, cx = center
    y, x = np.ogrid[:h, :w]
    mask = (x - cx)**2 + (y - cy)**2 <= radius**2
    
    return mask


def normalize_data(data: np.ndarray, method: str = "minmax") -> np.ndarray:
    """
    数据归一化
    
    Args:
        data: 原始数据
        method: 归一化方法 ("minmax", "zscore", "rms")
        
    Returns:
        归一化后的数据
    """
    if method == "minmax":
        data_min = np.nanmin(data)
        data_max = np.nanmax(data)
        return (data - data_min) / (data_max - data_min)
    
    elif method == "zscore":
        mean = np.nanmean(data)
        std = np.nanstd(data)
        return (data - mean) / std
    
    elif method == "rms":
        rms = np.sqrt(np.nanmean(data**2))
        return data / rms
    
    else:
        raise ValueError(f"未知的归一化方法: {method}")


def interpolate_missing_data(data: np.ndarray, method: str = "linear") -> np.ndarray:
    """
    插值填充缺失数据
    
    Args:
        data: 包含 NaN 的数据
        method: 插值方法
        
    Returns:
        填充后的数据
    """
    try:
        from scipy.interpolate import griddata
        
        # 获取有效数据点
        valid_mask = ~np.isnan(data)
        if not np.any(valid_mask):
            return data
        
        # 创建坐标网格
        h, w = data.shape
        x = np.arange(w)
        y = np.arange(h)
        xx, yy = np.meshgrid(x, y)
        
        # 有效点的坐标和值
        valid_points = np.column_stack([xx[valid_mask], yy[valid_mask]])
        valid_values = data[valid_mask]
        
        # 所有点的坐标
        all_points = np.column_stack([xx.ravel(), yy.ravel()])
        
        # 插值
        interpolated = griddata(valid_points, valid_values, all_points, 
                              method=method, fill_value=np.nan)
        
        return interpolated.reshape(data.shape)
    
    except ImportError:
        logger.warning("scipy 未安装，跳过插值")
        return data
    except Exception as e:
        logger.error(f"插值失败: {str(e)}")
        return data


class ZOSDataProcessor:
    """Zemax 数据处理器类"""
    
    def __init__(self):
        self.processed_data = {}
    
    def process_spot_diagram_data(self, spot_data: Any) -> dict:
        """
        处理点列图数据
        
        Args:
            spot_data: Zemax 点列图数据
            
        Returns:
            处理后的数据字典
        """
        try:
            # 提取光线坐标
            x_coords = extract_zos_vector(spot_data.GetXData())
            y_coords = extract_zos_vector(spot_data.GetYData())
            
            # 计算 RMS 半径
            rms_radius = np.sqrt(np.mean(np.array(x_coords)**2 + np.array(y_coords)**2))
            
            # 计算几何半径
            geo_radius = np.max(np.sqrt(np.array(x_coords)**2 + np.array(y_coords)**2))
            
            result = {
                "x_coords": x_coords,
                "y_coords": y_coords,
                "rms_radius": rms_radius,
                "geometric_radius": geo_radius,
                "ray_count": len(x_coords)
            }
            
            return result
        
        except Exception as e:
            logger.error(f"点列图数据处理失败: {str(e)}")
            raise
    
    def process_wavefront_data(self, wavefront_data: Any, shape: Tuple[int, int]) -> dict:
        """
        处理波前数据
        
        Args:
            wavefront_data: Zemax 波前数据
            shape: 数据形状
            
        Returns:
            处理后的数据字典
        """
        try:
            # 转换为 numpy 数组
            wf_array = zos_array_to_numpy(wavefront_data, shape)
            
            # 创建坐标网格
            h, w = shape
            x = np.linspace(-1, 1, w)
            y = np.linspace(-1, 1, h)
            xx, yy = np.meshgrid(x, y)
            
            # 创建圆形掩膜
            mask = circular_mask(shape)
            
            # 应用掩膜
            masked_wf = np.where(mask, wf_array, np.nan)
            
            # 移除倾斜和平移
            corrected_wf = remove_piston_tilt(masked_wf, xx, yy)
            
            # 计算统计量
            valid_data = corrected_wf[~np.isnan(corrected_wf)]
            rms_wfe = calculate_rms_error(valid_data)
            pv_wfe = calculate_pv_error(valid_data)
            
            result = {
                "wavefront": corrected_wf,
                "x_coords": xx,
                "y_coords": yy,
                "mask": mask,
                "rms_wfe": rms_wfe,
                "pv_wfe": pv_wfe,
                "shape": shape
            }
            
            return result
        
        except Exception as e:
            logger.error(f"波前数据处理失败: {str(e)}")
            raise
