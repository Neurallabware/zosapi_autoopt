"""
Zemax OpticStudio Python API 绘图模块
提供各种光学分析图表的绘制功能
Author: Your Name
Date: 2025-06-29
"""

import matplotlib.pyplot as plt
import numpy as np
from typing import Optional, Tuple, List, Dict, Any
import logging

logger = logging.getLogger(__name__)

# 设置中文字体支持
plt.rcParams['font.sans-serif'] = ['SimHei', 'DejaVu Sans']
plt.rcParams['axes.unicode_minus'] = False


class ZOSPlotter:
    """Zemax 数据绘图器"""
    
    def __init__(self, style: str = "default", figsize: Tuple[int, int] = (10, 8)):
        """
        初始化绘图器
        
        Args:
            style: matplotlib 样式
            figsize: 图片尺寸
        """
        self.style = style
        self.figsize = figsize
        self.setup_style()
    
    def setup_style(self):
        """设置绘图样式"""
        plt.style.use(self.style)
        
        # 自定义颜色和样式
        self.colors = {
            'primary': '#1f77b4',
            'secondary': '#ff7f0e', 
            'success': '#2ca02c',
            'danger': '#d62728',
            'warning': '#ff9800',
            'info': '#17a2b8'
        }
        
        self.line_styles = ['-', '--', '-.', ':']
        self.markers = ['o', 's', '^', 'v', 'D', 'x', '+']
    
    def plot_spot_diagram(self, x_coords: List[float], y_coords: List[float], 
                         title: str = "点列图", figsize: Optional[Tuple[int, int]] = None,
                         save_path: Optional[str] = None) -> plt.Figure:
        """
        绘制点列图
        
        Args:
            x_coords: X 坐标列表
            y_coords: Y 坐标列表
            title: 图标题
            figsize: 图片尺寸
            save_path: 保存路径
            
        Returns:
            matplotlib Figure 对象
        """
        if figsize is None:
            figsize = self.figsize
        
        fig, ax = plt.subplots(figsize=figsize)
        
        # 绘制散点图
        scatter = ax.scatter(x_coords, y_coords, alpha=0.6, s=1, c=self.colors['primary'])
        
        # 计算 RMS 圆
        x_rms = np.sqrt(np.mean(np.array(x_coords)**2))
        y_rms = np.sqrt(np.mean(np.array(y_coords)**2))
        rms_radius = np.sqrt(x_rms**2 + y_rms**2)
        
        # 绘制 RMS 圆
        circle = plt.Circle((0, 0), rms_radius, fill=False, color=self.colors['danger'], 
                           linestyle='--', label=f'RMS 半径: {rms_radius:.3f}')
        ax.add_patch(circle)
        
        # 设置坐标轴等比例
        ax.set_aspect('equal')
        ax.grid(True, alpha=0.3)
        ax.set_xlabel('X (mm)')
        ax.set_ylabel('Y (mm)')
        ax.set_title(title)
        ax.legend()
        
        # 添加统计信息
        stats_text = f'光线数: {len(x_coords)}\nRMS 半径: {rms_radius:.6f} mm'
        ax.text(0.02, 0.98, stats_text, transform=ax.transAxes, 
                verticalalignment='top', bbox=dict(boxstyle='round', facecolor='wheat', alpha=0.8))
        
        plt.tight_layout()
        
        if save_path:
            plt.savefig(save_path, dpi=300, bbox_inches='tight')
            logger.info(f"点列图已保存到: {save_path}")
        
        return fig
    
    def plot_wavefront(self, wavefront: np.ndarray, x_coords: np.ndarray, y_coords: np.ndarray,
                      mask: Optional[np.ndarray] = None, title: str = "波前图",
                      colorbar_label: str = "波前误差 (waves)", 
                      figsize: Optional[Tuple[int, int]] = None,
                      save_path: Optional[str] = None) -> plt.Figure:
        """
        绘制波前图
        
        Args:
            wavefront: 波前数据
            x_coords: X 坐标网格
            y_coords: Y 坐标网格
            mask: 掩膜数组
            title: 图标题
            colorbar_label: 颜色条标签
            figsize: 图片尺寸
            save_path: 保存路径
            
        Returns:
            matplotlib Figure 对象
        """
        if figsize is None:
            figsize = self.figsize
        
        fig, ax = plt.subplots(figsize=figsize)
        
        # 应用掩膜
        if mask is not None:
            plot_data = np.where(mask, wavefront, np.nan)
        else:
            plot_data = wavefront
        
        # 绘制波前
        im = ax.contourf(x_coords, y_coords, plot_data, levels=50, cmap='RdYlBu_r')
        
        # 添加等高线
        contours = ax.contour(x_coords, y_coords, plot_data, levels=10, colors='black', alpha=0.3, linewidths=0.5)
        
        # 添加颜色条
        cbar = plt.colorbar(im, ax=ax, label=colorbar_label)
        
        # 设置坐标轴
        ax.set_aspect('equal')
        ax.set_xlabel('归一化坐标 X')
        ax.set_ylabel('归一化坐标 Y')
        ax.set_title(title)
        
        # 添加统计信息
        valid_data = plot_data[~np.isnan(plot_data)]
        if len(valid_data) > 0:
            rms_wfe = np.sqrt(np.mean(valid_data**2))
            pv_wfe = np.max(valid_data) - np.min(valid_data)
            stats_text = f'RMS: {rms_wfe:.6f} waves\nPV: {pv_wfe:.6f} waves'
            ax.text(0.02, 0.98, stats_text, transform=ax.transAxes, 
                    verticalalignment='top', bbox=dict(boxstyle='round', facecolor='wheat', alpha=0.8))
        
        plt.tight_layout()
        
        if save_path:
            plt.savefig(save_path, dpi=300, bbox_inches='tight')
            logger.info(f"波前图已保存到: {save_path}")
        
        return fig
    
    def plot_mtf_curve(self, frequencies: List[float], mtf_values: List[float],
                      title: str = "MTF 曲线", label: str = "MTF",
                      figsize: Optional[Tuple[int, int]] = None,
                      save_path: Optional[str] = None) -> plt.Figure:
        """
        绘制 MTF 曲线
        
        Args:
            frequencies: 频率列表
            mtf_values: MTF 值列表
            title: 图标题
            label: 曲线标签
            figsize: 图片尺寸
            save_path: 保存路径
            
        Returns:
            matplotlib Figure 对象
        """
        if figsize is None:
            figsize = self.figsize
        
        fig, ax = plt.subplots(figsize=figsize)
        
        # 绘制 MTF 曲线
        ax.plot(frequencies, mtf_values, color=self.colors['primary'], 
                linewidth=2, marker='o', markersize=3, label=label)
        
        # 设置坐标轴
        ax.set_xlabel('空间频率 (cycles/mm)')
        ax.set_ylabel('MTF')
        ax.set_title(title)
        ax.grid(True, alpha=0.3)
        ax.legend()
        
        # 设置 Y 轴范围
        ax.set_ylim(0, 1.1)
        
        plt.tight_layout()
        
        if save_path:
            plt.savefig(save_path, dpi=300, bbox_inches='tight')
            logger.info(f"MTF 曲线已保存到: {save_path}")
        
        return fig
    
    def plot_ray_fan(self, field_angles: List[float], ray_errors: List[float],
                    title: str = "光线扇形图", ylabel: str = "光线误差",
                    figsize: Optional[Tuple[int, int]] = None,
                    save_path: Optional[str] = None) -> plt.Figure:
        """
        绘制光线扇形图
        
        Args:
            field_angles: 视场角列表
            ray_errors: 光线误差列表
            title: 图标题
            ylabel: Y 轴标签
            figsize: 图片尺寸
            save_path: 保存路径
            
        Returns:
            matplotlib Figure 对象
        """
        if figsize is None:
            figsize = self.figsize
        
        fig, ax = plt.subplots(figsize=figsize)
        
        # 绘制光线扇形图
        ax.plot(field_angles, ray_errors, color=self.colors['primary'], 
                linewidth=2, marker='o', markersize=3)
        
        # 设置坐标轴
        ax.set_xlabel('视场角 (度)')
        ax.set_ylabel(ylabel)
        ax.set_title(title)
        ax.grid(True, alpha=0.3)
        
        # 添加零线
        ax.axhline(y=0, color='black', linestyle='-', alpha=0.5)
        
        plt.tight_layout()
        
        if save_path:
            plt.savefig(save_path, dpi=300, bbox_inches='tight')
            logger.info(f"光线扇形图已保存到: {save_path}")
        
        return fig
    
    def plot_field_curvature(self, field_positions: List[float], 
                           sagittal_focus: List[float], tangential_focus: List[float],
                           title: str = "场曲图", figsize: Optional[Tuple[int, int]] = None,
                           save_path: Optional[str] = None) -> plt.Figure:
        """
        绘制场曲图
        
        Args:
            field_positions: 视场位置
            sagittal_focus: 弧矢焦点位置
            tangential_focus: 子午焦点位置
            title: 图标题
            figsize: 图片尺寸
            save_path: 保存路径
            
        Returns:
            matplotlib Figure 对象
        """
        if figsize is None:
            figsize = self.figsize
        
        fig, ax = plt.subplots(figsize=figsize)
        
        # 绘制场曲
        ax.plot(sagittal_focus, field_positions, color=self.colors['primary'], 
                linewidth=2, marker='o', markersize=4, label='弧矢方向')
        ax.plot(tangential_focus, field_positions, color=self.colors['secondary'], 
                linewidth=2, marker='s', markersize=4, label='子午方向')
        
        # 设置坐标轴
        ax.set_xlabel('焦点位置偏移 (mm)')
        ax.set_ylabel('视场高度')
        ax.set_title(title)
        ax.grid(True, alpha=0.3)
        ax.legend()
        
        # 添加零线
        ax.axvline(x=0, color='black', linestyle='-', alpha=0.5)
        
        plt.tight_layout()
        
        if save_path:
            plt.savefig(save_path, dpi=300, bbox_inches='tight')
            logger.info(f"场曲图已保存到: {save_path}")
        
        return fig
    
    def plot_distortion(self, field_positions: List[float], distortion_values: List[float],
                       title: str = "畸变图", figsize: Optional[Tuple[int, int]] = None,
                       save_path: Optional[str] = None) -> plt.Figure:
        """
        绘制畸变图
        
        Args:
            field_positions: 视场位置
            distortion_values: 畸变值
            title: 图标题
            figsize: 图片尺寸
            save_path: 保存路径
            
        Returns:
            matplotlib Figure 对象
        """
        if figsize is None:
            figsize = self.figsize
        
        fig, ax = plt.subplots(figsize=figsize)
        
        # 绘制畸变
        ax.plot(field_positions, distortion_values, color=self.colors['primary'], 
                linewidth=2, marker='o', markersize=4)
        
        # 设置坐标轴
        ax.set_xlabel('视场位置')
        ax.set_ylabel('畸变 (%)')
        ax.set_title(title)
        ax.grid(True, alpha=0.3)
        
        # 添加零线
        ax.axhline(y=0, color='black', linestyle='-', alpha=0.5)
        
        plt.tight_layout()
        
        if save_path:
            plt.savefig(save_path, dpi=300, bbox_inches='tight')
            logger.info(f"畸变图已保存到: {save_path}")
        
        return fig
    
    def plot_multiple_curves(self, x_data: List[float], y_data_list: List[List[float]],
                           labels: List[str], title: str = "多曲线图",
                           xlabel: str = "X", ylabel: str = "Y",
                           figsize: Optional[Tuple[int, int]] = None,
                           save_path: Optional[str] = None) -> plt.Figure:
        """
        绘制多条曲线
        
        Args:
            x_data: X 数据
            y_data_list: Y 数据列表
            labels: 曲线标签列表
            title: 图标题
            xlabel: X 轴标签
            ylabel: Y 轴标签
            figsize: 图片尺寸
            save_path: 保存路径
            
        Returns:
            matplotlib Figure 对象
        """
        if figsize is None:
            figsize = self.figsize
        
        fig, ax = plt.subplots(figsize=figsize)
        
        # 绘制多条曲线
        colors = list(self.colors.values())
        for i, (y_data, label) in enumerate(zip(y_data_list, labels)):
            color = colors[i % len(colors)]
            line_style = self.line_styles[i % len(self.line_styles)]
            marker = self.markers[i % len(self.markers)]
            
            ax.plot(x_data, y_data, color=color, linewidth=2, 
                   linestyle=line_style, marker=marker, markersize=4, label=label)
        
        # 设置坐标轴
        ax.set_xlabel(xlabel)
        ax.set_ylabel(ylabel)
        ax.set_title(title)
        ax.grid(True, alpha=0.3)
        ax.legend()
        
        plt.tight_layout()
        
        if save_path:
            plt.savefig(save_path, dpi=300, bbox_inches='tight')
            logger.info(f"多曲线图已保存到: {save_path}")
        
        return fig
    
    def create_subplot_layout(self, nrows: int, ncols: int, 
                            figsize: Optional[Tuple[int, int]] = None) -> Tuple[plt.Figure, np.ndarray]:
        """
        创建子图布局
        
        Args:
            nrows: 行数
            ncols: 列数
            figsize: 图片尺寸
            
        Returns:
            Figure 和 Axes 数组
        """
        if figsize is None:
            figsize = (ncols * 5, nrows * 4)
        
        fig, axes = plt.subplots(nrows, ncols, figsize=figsize)
        
        # 确保 axes 是数组
        if nrows == 1 and ncols == 1:
            axes = np.array([axes])
        elif nrows == 1 or ncols == 1:
            axes = axes.reshape(-1)
        
        return fig, axes


# === 便捷绘图函数 ===

def quick_spot_plot(x_coords: List[float], y_coords: List[float], 
                   title: str = "点列图", save_path: Optional[str] = None) -> plt.Figure:
    """快速绘制点列图"""
    plotter = ZOSPlotter()
    return plotter.plot_spot_diagram(x_coords, y_coords, title=title, save_path=save_path)


def quick_wavefront_plot(wavefront: np.ndarray, title: str = "波前图", 
                        save_path: Optional[str] = None) -> plt.Figure:
    """快速绘制波前图"""
    plotter = ZOSPlotter()
    h, w = wavefront.shape
    x = np.linspace(-1, 1, w)
    y = np.linspace(-1, 1, h)
    xx, yy = np.meshgrid(x, y)
    return plotter.plot_wavefront(wavefront, xx, yy, title=title, save_path=save_path)


def quick_mtf_plot(frequencies: List[float], mtf_values: List[float], 
                  title: str = "MTF 曲线", save_path: Optional[str] = None) -> plt.Figure:
    """快速绘制 MTF 曲线"""
    plotter = ZOSPlotter()
    return plotter.plot_mtf_curve(frequencies, mtf_values, title=title, save_path=save_path)
