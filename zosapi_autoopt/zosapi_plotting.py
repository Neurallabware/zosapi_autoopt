"""
Zemax OpticStudio Python API 绘图模块
提供光学系统分析图形绘制功能，包括点列图、光线扇形图、MTF曲线等
"""

import matplotlib.pyplot as plt
import numpy as np
import math
from typing import Optional, List, Dict, Union, Any, Tuple
import logging
from pathlib import Path
import os

logger = logging.getLogger(__name__)

# 设置全局绘图样式
plt.rcParams['font.family'] = ['DejaVu Sans', 'Arial', 'sans-serif']
plt.rcParams['axes.unicode_minus'] = False


class ZOSPlotter:
    """
    Zemax OpticStudio 绘图类
    
    提供多种光学系统分析图形的绘制功能:
    - 点列图 (Spot Diagram)
    - 光线扇形图 (Ray Fan)
    - MTF曲线 (Modulation Transfer Function)
    - 场曲和畸变 (Field Curvature and Distortion)
    - 系统综合分析图 (Comprehensive Analysis)
    """
    
    def __init__(self, zos_manager, analyzer=None):
        """
        初始化绘图类
        
        Args:
            zos_manager: ZOSAPIManager实例
            analyzer: ZOSAnalyzer实例（如果为None，则根据需要创建）
        """
        self.zos_manager = zos_manager
        self.ZOSAPI = zos_manager.ZOSAPI
        self.TheSystem = zos_manager.TheSystem
        
        # 如果未提供analyzer，等到需要时再创建
        self._analyzer = analyzer
        
        # 设置颜色和线型
        self.colors = ['b', 'g', 'r', 'c', 'm', 'y', 'k']
        self.linestyles = ['-', '--', '-.', ':']

    @property
    def analyzer(self):
        """获取分析器实例，如果尚未创建则自动创建"""
        if self._analyzer is None:
            from .zosapi_analysis import ZOSAnalyzer
            self._analyzer = ZOSAnalyzer(self.zos_manager)
        return self._analyzer
    
    def _parse_field_selection(self, fields: Union[str, List[int], int] = "all") -> List[int]:
        """
        解析视场选择
        
        Args:
            fields: "all", "single"(第一个视场), 或视场索引列表(0-based)
            
        Returns:
            视场索引列表
        """
        num_fields = self.TheSystem.SystemData.Fields.NumberOfFields
        
        if fields == "all":
            return list(range(num_fields))
        elif fields == "single":
            return [0]  # 第一个视场
        elif isinstance(fields, int):
            return [fields]
        else:
            return fields if isinstance(fields, list) else [fields]
    
    def _parse_wavelength_selection(self, wavelengths: Union[str, List[int], int] = "all") -> List[int]:
        """
        解析波长选择
        
        Args:
            wavelengths: "all", "single"(主波长), 或波长索引列表(0-based)
            
        Returns:
            波长索引列表
        """
        num_wavelengths = self.TheSystem.SystemData.Wavelengths.NumberOfWavelengths
        
        if wavelengths == "all":
            return list(range(num_wavelengths))
        elif wavelengths == "single":
            # 寻找主波长
            primary_wave = 0
            for i in range(1, num_wavelengths + 1):
                if self.TheSystem.SystemData.Wavelengths.GetWavelength(i).IsPrimary:
                    primary_wave = i - 1  # 转换为0-based
                    break
            return [primary_wave]
        elif isinstance(wavelengths, int):
            return [wavelengths]
        else:
            return wavelengths if isinstance(wavelengths, list) else [wavelengths]
    

    def plot_spots(self, 
                 fields: Union[str, List[int], int] = "all", 
                 wavelengths: Union[str, List[int], int] = "all",
                 show_airy_disk: bool = False,
                 max_rays: int = 500,
                 title: Optional[str] = None,
                 save_path: Optional[str] = None) -> plt.Figure:
        """
        绘制点列图(Spot Diagram)
        
        Args:
            fields: "all", "single"(第一个视场), 或视场索引列表(0-based)
            wavelengths: "all", "single"(主波长), 或波长索引列表(0-based)
            show_airy_disk: 是否显示艾里斑
            max_rays: 每个视场的最大光线数量
            title: 图表标题，如果为None则自动生成
            save_path: 保存路径
            
        Returns:
            Figure对象
        """
        # 解析视场和波长选择
        field_indices = self._parse_field_selection(fields)
        wave_indices = self._parse_wavelength_selection(wavelengths)
        
        num_selected_fields = len(field_indices)
        num_selected_waves = len(wave_indices)
        
        # 计算子图布局 - 默认3列，基于视场数量计算行数
        cols = 3
        rows = (num_selected_fields + cols - 1) // cols  # 向上取整
        
        # 创建子图，使用constrained_layout以保持一致的大小
        fig, axes = plt.subplots(rows, cols, figsize=(15, 5 * rows), 
                                constrained_layout=True)
        
        # 确保axes始终是2D数组，以便一致的索引
        if rows == 1 and cols == 1:
            axes = np.array([[axes]])
        elif rows == 1:
            axes = axes.reshape(1, -1)
        elif cols == 1:
            axes = axes.reshape(-1, 1)
        
        # 为每个选定的视场绘图
        for plot_idx, field_idx in enumerate(field_indices):
            row = plot_idx // cols
            col = plot_idx % cols
            ax = axes[row, col]
            
            # 获取视场信息
            field = self.TheSystem.SystemData.Fields.GetField(field_idx + 1)  # Zemax使用1-based索引
            field_y = field.Y
            
            # 绘制每个选定的波长
            for wave_idx in wave_indices:
                spot_data = self.analyzer.analyze_spot_diagram(
                    field_index=field_idx, 
                    wavelength_index=wave_idx, 
                    max_rays=max_rays
                )
                
                # 获取波长信息
                wavelength = self.TheSystem.SystemData.Wavelengths.GetWavelength(wave_idx + 1)
                wave_value = wavelength.Wavelength
                
                color = self.colors[wave_idx % len(self.colors)]
                label = f'λ={wave_value:.3f}nm' if num_selected_waves > 1 else ''
                
                # 使用较大的点大小以提高可见性，特别是对于轴上视场
                point_size = 2 if field_y == 0 else 1
                ax.scatter(spot_data['x_coords'], spot_data['y_coords'], 
                          c=color, alpha=0.7, s=point_size, label=label)
                
                # 如果需要，绘制艾里斑
                if show_airy_disk and 'airy_radius' in spot_data:
                    airy_radius = spot_data['airy_radius']
                    if airy_radius > 0:
                        circle = plt.Circle((0, 0), airy_radius, 
                                           color=color, fill=False, 
                                           linestyle='--', alpha=0.5)
                        ax.add_patch(circle)
            
            ax.set_title(f'Field {field_idx+1}: Y={field_y:.2f}')
            ax.set_xlabel('X (mm)')
            ax.set_ylabel('Y (mm)')
            # 使用aspect='equal'并设置adjustable='datalim'以保持真实形状
            # 同时保持子图大小一致
            ax.set_aspect('equal', adjustable='datalim')
            ax.grid(True, alpha=0.3)
            
            if num_selected_waves > 1:
                ax.legend()
        
        # 隐藏未使用的子图
        for plot_idx in range(num_selected_fields, rows * cols):
            row = plot_idx // cols
            col = plot_idx % cols
            axes[row, col].set_visible(False)
        
        # 基于选择创建标题
        if title is None:
            title_parts = []
            if fields == "all":
                title_parts.append("All Fields")
            elif fields == "single":
                title_parts.append("Single Field")
            else:
                title_parts.append(f"Fields {field_indices}")
                
            if wavelengths == "all":
                title_parts.append("All Wavelengths")
            elif wavelengths == "single":
                title_parts.append("Primary Wavelength")
            else:
                title_parts.append(f"Wavelengths {wave_indices}")
            
            title = f'Spot Diagram - {" & ".join(title_parts)}'
        
        plt.suptitle(title, fontsize=14)
        
        if save_path:
            plt.savefig(save_path, dpi=300, bbox_inches='tight')
            logger.info(f"Multi-field spot diagrams saved to: {save_path}")
        
        return fig


    def plot_rayfan(self, 
                  fields: Union[str, List[int], int] = "all", 
                  wavelengths: Union[str, List[int], int] = "single",
                  num_rays: int = 21,
                  title: Optional[str] = None,
                  save_path: Optional[str] = None) -> plt.Figure:
        """
        绘制光线扇形图(Ray Fan)
        
        Args:
            fields: "all", "single"(第一个视场), 或视场索引列表(0-based)
            wavelengths: "all", "single"(主波长), 或波长索引列表(0-based)
            num_rays: 每个扇形的光线数量
            title: 图表标题，如果为None则自动生成
            save_path: 保存路径
            
        Returns:
            Figure对象
        """
        # 解析视场和波长选择
        field_indices = self._parse_field_selection(fields)
        wave_indices = self._parse_wavelength_selection(wavelengths)
        
        num_selected_fields = len(field_indices)
        num_selected_waves = len(wave_indices)
        
        # 创建子图布局: 2行(X和Y扇形图) x num_fields列
        if num_selected_fields == 1:
            fig, axes = plt.subplots(2, 1, figsize=(8, 10))
            axes = axes.reshape(2, 1)
        else:
            fig, axes = plt.subplots(2, num_selected_fields, figsize=(4*num_selected_fields, 8))
            if axes.ndim == 1:
                axes = axes.reshape(2, 1)
        
        # 为每个选定的视场绘图
        for plot_idx, field_idx in enumerate(field_indices):
            # 获取视场信息
            field = self.TheSystem.SystemData.Fields.GetField(field_idx + 1)
            
            # X扇形子图
            ax_x = axes[0, plot_idx] if num_selected_fields > 1 else axes[0, 0]
            
            # Y扇形子图
            ax_y = axes[1, plot_idx] if num_selected_fields > 1 else axes[1, 0]
            
            # 绘制每个选定的波长
            for wave_plot_idx, wave_idx in enumerate(wave_indices):
                # 获取波长信息
                wavelength = self.TheSystem.SystemData.Wavelengths.GetWavelength(wave_idx + 1)
                wave_value = wavelength.Wavelength
                
                color = self.colors[wave_idx % len(self.colors)]
                linestyle = self.linestyles[wave_plot_idx % len(self.linestyles)]
                
                # X扇形
                ray_fan_x = self.analyzer.analyze_ray_fan(
                    field_index=field_idx, 
                    wavelength_index=wave_idx, 
                    fan_type="X", 
                    num_rays=num_rays
                )
                
                label_x = f'λ={wave_value:.3f}nm' if num_selected_waves > 1 else ''
                ax_x.plot(ray_fan_x['pupil_coords'], ray_fan_x['ray_errors'], 
                         color=color, linestyle=linestyle, linewidth=2, 
                         marker='o', markersize=2, label=label_x)
                
                # Y扇形
                ray_fan_y = self.analyzer.analyze_ray_fan(
                    field_index=field_idx, 
                    wavelength_index=wave_idx, 
                    fan_type="Y", 
                    num_rays=num_rays
                )
                
                label_y = f'λ={wave_value:.3f}nm' if num_selected_waves > 1 else ''
                ax_y.plot(ray_fan_y['pupil_coords'], ray_fan_y['ray_errors'], 
                         color=color, linestyle=linestyle, linewidth=2, 
                         marker='o', markersize=2, label=label_y)
            
            # Format X fan subplot
            ax_x.set_title(f'Field {field_idx+1} (Y={field.Y:.1f}) - X Fan')
            ax_x.set_xlabel('Pupil Coordinate')
            ax_x.set_ylabel('Ray Error (mm)')
            ax_x.grid(True, alpha=0.3)
            ax_x.axhline(y=0, color='black', linestyle='-', alpha=0.5)
            if num_selected_waves > 1:
                ax_x.legend()
            
            # Format Y fan subplot
            ax_y.set_title(f'Field {field_idx+1} (Y={field.Y:.1f}) - Y Fan')
            ax_y.set_xlabel('Pupil Coordinate')
            ax_y.set_ylabel('Ray Error (mm)')
            ax_y.grid(True, alpha=0.3)
            ax_y.axhline(y=0, color='black', linestyle='-', alpha=0.5)
            if num_selected_waves > 1:
                ax_y.legend()
        
        # 基于选择创建标题
        if title is None:
            title_parts = []
            if fields == "all":
                title_parts.append("All Fields")
            elif fields == "single":
                title_parts.append("Single Field")
            else:
                title_parts.append(f"Fields {field_indices}")
                
            if wavelengths == "all":
                title_parts.append("All Wavelengths")
            elif wavelengths == "single":
                title_parts.append("Primary Wavelength")
            else:
                title_parts.append(f"Wavelengths {wave_indices}")
            
            title = f'Ray Fan Analysis - {" & ".join(title_parts)}'
        
        plt.suptitle(title, fontsize=14)
        plt.tight_layout()
        
        if save_path:
            plt.savefig(save_path, dpi=300, bbox_inches='tight')
            logger.info(f"Multi-field ray fan plots saved to: {save_path}")
        
        return fig


    def plot_mtf(self, 
                fields: Union[str, List[int], int] = "all", 
                wavelengths: Union[str, List[int], int] = "all",
                max_frequency: float = 100,
                sample_size: str = "S_256x256",
                title: Optional[str] = None,
                save_path: Optional[str] = None) -> plt.Figure:
        """
        绘制MTF(调制传递函数)曲线
        
        Args:
            fields: "all", "single"(第一个视场), 或视场索引列表(0-based)
            wavelengths: "all", "single"(主波长), 或波长索引列表(0-based)
            max_frequency: 最大空间频率
            sample_size: 采样大小("S_64x64", "S_128x128", "S_256x256", "S_512x512", "S_1024x1024")
            title: 图表标题，如果为None则自动生成
            save_path: 保存路径
            
        Returns:
            Figure对象
        """
        from .zosapi_utils import reshape_zos_data
        
        # 创建FFT MTF分析
        mtf_analysis = self.TheSystem.Analyses.New_FftMtf()
        mtf_settings = mtf_analysis.GetSettings()
        mtf_settings.MaximumFrequency = max_frequency
        
        # 设置采样大小
        sample_size_enum = getattr(self.ZOSAPI.Analysis.SampleSizes, sample_size)
        mtf_settings.SampleSize = sample_size_enum
        
        # 解析视场和波长选择，设置分析配置
        if fields != "all":
            # 如果需要，配置特定视场 - 实现取决于API版本
            pass
        if wavelengths != "all":
            # 如果需要，配置特定波长 - 实现取决于API版本
            pass
        
        # 运行分析
        mtf_analysis.ApplyAndWaitForCompletion()
        mtf_results = mtf_analysis.GetResults()
        
        # 绘制MTF曲线
        plt.figure(figsize=(12, 8))
        legend_labels = []
        
        for seriesNum in range(0, mtf_results.NumberOfDataSeries):
            data = mtf_results.GetDataSeries(seriesNum)
            
            # 获取数据
            xRaw = data.XData.Data
            yRaw = data.YData.Data
            
            x = list(xRaw)
            y = reshape_zos_data(yRaw, yRaw.GetLength(0), yRaw.GetLength(1), True)
            
            # Plot tangential and sagittal MTF
            color = self.colors[seriesNum % len(self.colors)]
            plt.plot(x, y[0], color=color, linewidth=2, linestyle=self.linestyles[0])  # Tangential
            plt.plot(x, y[1], color=color, linewidth=2, linestyle=self.linestyles[1])  # Sagittal
            
            legend_labels.extend([f'Field {seriesNum+1} Tangential', f'Field {seriesNum+1} Sagittal'])
        
        # 基于选择创建标题
        if title is None:
            title_parts = ["MTF Analysis"]
            if fields == "all":
                title_parts.append("All Fields")
            elif fields == "single":
                title_parts.append("Single Field")
            else:
                title_parts.append("Selected Fields")
                
            if wavelengths == "all":
                title_parts.append("All Wavelengths")
            elif wavelengths == "single":
                title_parts.append("Primary Wavelength")
            else:
                title_parts.append("Selected Wavelengths")
            
            title = ' - '.join(title_parts)
        
        plt.title(title)
        plt.xlabel('Spatial Frequency (cycles/mm)')
        plt.ylabel('MTF')
        plt.grid(True, alpha=0.3)
        plt.legend(legend_labels[:min(len(legend_labels), 10)])  # 限制图例条目数
        plt.ylim(0, 1.1)
        plt.tight_layout()
        
        if save_path:
            plt.savefig(save_path, dpi=300, bbox_inches='tight')
            logger.info(f"System MTF plot saved to: {save_path}")
        
        # 关闭分析
        mtf_analysis.Close()
        
        return plt.gcf()


    def plot_field_curvature_distortion(self,
                                   wavelengths: Union[str, List[int], int] = "all",
                                   num_points: int = 50,
                                   title: Optional[str] = None,
                                   save_path: Optional[str] = None) -> plt.Figure:
        """
        绘制场曲和畸变分析图
        
        Args:
            wavelengths: "all", "single"(主波长), 或波长索引列表(0-based)
            num_points: 分析点数量
            title: 图表标题，如果为None则自动生成
            save_path: 保存路径
            
        Returns:
            Figure对象
        """
        # 创建子图
        fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(15, 6))
        
        # 解析波长选择
        wave_indices = self._parse_wavelength_selection(wavelengths)
        
        legend_entries = []
        
        # 遍历所有选定的波长
        for wave_idx, wavelength_index in enumerate(wave_indices):
            # 获取波长信息
            wavelength = self.TheSystem.SystemData.Wavelengths.GetWavelength(wavelength_index + 1)
            wave_value = wavelength.Wavelength
            
            # 为当前波长选择颜色
            color = self.colors[wave_idx % len(self.colors)]
            
            # 分析此波长的场曲和畸变
            distortion_data = self.analyzer.analyze_field_curvature_distortion(
                num_points=num_points, 
                wavelength_index=wavelength_index
            )
            
            # 绘制此波长的场曲
            if distortion_data['field_heights']:
                field_heights = distortion_data['field_heights']
                tangential_fc = distortion_data['tangential_field_curvature']
                sagittal_fc = distortion_data['sagittal_field_curvature']
                
                # Tangential curve (T) - solid line
                if tangential_fc:
                    ax1.plot(tangential_fc, field_heights, color=color, linestyle=self.linestyles[0], linewidth=2, 
                            label=f'{wave_value:.4f}-Tangential')
                    legend_entries.append(f'{wave_value:.4f}-Tangential')
                    
                # Sagittal curve (S) - dashed line
                if sagittal_fc:
                    ax1.plot(sagittal_fc, field_heights, color=color, linestyle=self.linestyles[1], linewidth=2,
                            label=f'{wave_value:.4f}-Sagittal')
                    legend_entries.append(f'{wave_value:.4f}-Sagittal')
                
                # 绘制此波长的畸变
                if distortion_data['distortion_percent']:
                    distortion = distortion_data['distortion_percent']
                    ax2.plot(distortion, field_heights, color=color, linewidth=2,
                            label=f'{wave_value:.4f}')
        
        # Format field curvature subplot
        ax1.set_title('Field Curvature')
        ax1.set_xlabel('Field Curvature (mm)')
        ax1.set_ylabel('Field Height')
        ax1.grid(True, alpha=0.3)
        ax1.axvline(x=0, color='black', linestyle='-', alpha=0.3)  # Zero line is now vertical
        
        if legend_entries:
            ax1.legend()
        else:
            ax1.text(0.5, 0.5, 'No Field Curvature Data', 
                    transform=ax1.transAxes, ha='center', va='center')
        
        # Format distortion subplot
        ax2.set_title('Distortion')
        ax2.set_xlabel('Distortion (%)')
        ax2.set_ylabel('Field Height')
        ax2.grid(True, alpha=0.3)
        ax2.axvline(x=0, color='black', linestyle='-', alpha=0.3)  # Zero line is now vertical
        
        if ax2.get_lines():
            ax2.legend()
        else:
            ax2.text(0.5, 0.5, 'No Distortion Data', 
                    transform=ax2.transAxes, ha='center', va='center')
        
        # Create title based on wavelength selection
        if title is None:
            if wavelengths == "all":
                title = "Field Curvature and Distortion Analysis - All Wavelengths"
            elif wavelengths == "single":
                title = f"Field Curvature and Distortion Analysis - Primary Wavelength"
            else:
                if len(wave_indices) == 1:
                    wavelength = self.TheSystem.SystemData.Wavelengths.GetWavelength(wave_indices[0] + 1)
                    wave_value = wavelength.Wavelength
                    title = f"Field Curvature and Distortion Analysis (λ={wave_value:.4f}nm)"
                else:
                    title = f"Field Curvature and Distortion Analysis - Selected Wavelengths"
        
        plt.suptitle(title, fontsize=14)
        plt.tight_layout()
        
        if save_path:
            plt.savefig(save_path, dpi=300, bbox_inches='tight')
            logger.info(f"Field curvature and distortion plot saved to: {save_path}")
        
        return fig


    def plot_mtf_spot_ranfan(self, 
                       fields: Union[str, List[int], int] = "all", 
                       wavelengths: Union[str, List[int], int] = "all",
                       title: Optional[str] = None,
                       save_path: Optional[str] = None) -> plt.Figure:
        """
        创建包含MTF、点列图和光线扇形图的综合分析图
        
        Args:
            fields: "all", "single"(第一个视场), 或视场索引列表(0-based)
            wavelengths: "all", "single"(主波长), 或波长索引列表(0-based)
            title: 图表标题，如果为None则自动生成
            save_path: 保存路径
            
        Returns:
            Figure对象
        """
        from .zosapi_utils import reshape_zos_data
        
        # 解析视场和波长选择
        field_indices = self._parse_field_selection(fields)
        wave_indices = self._parse_wavelength_selection(wavelengths)
        
        fig = plt.figure(figsize=(16, 12))
        
        # MTF子图（顶部区域）
        ax1 = plt.subplot2grid((3, 3), (0, 0), colspan=3)
        
        # 创建MTF分析
        mtf_analysis = self.TheSystem.Analyses.New_FftMtf()
        mtf_settings = mtf_analysis.GetSettings()
        mtf_settings.MaximumFrequency = 50
        mtf_analysis.ApplyAndWaitForCompletion()
        mtf_results = mtf_analysis.GetResults()
        
        for seriesNum in range(0, min(mtf_results.NumberOfDataSeries, len(self.colors))):
            data = mtf_results.GetDataSeries(seriesNum)
            xRaw = data.XData.Data
            yRaw = data.YData.Data
            x = list(xRaw)
            y = reshape_zos_data(yRaw, yRaw.GetLength(0), yRaw.GetLength(1), True)
            
            ax1.plot(x, y[0], color=self.colors[seriesNum], linewidth=2, label=f'Field {seriesNum+1} T')
            ax1.plot(x, y[1], linestyle='--', color=self.colors[seriesNum], linewidth=2, label=f'Field {seriesNum+1} S')
        
        ax1.set_title('MTF - All Fields')
        ax1.set_xlabel('Spatial Frequency (cycles/mm)')
        ax1.set_ylabel('MTF')
        ax1.grid(True, alpha=0.3)
        ax1.legend(bbox_to_anchor=(1.05, 1), loc='upper left')
        
        mtf_analysis.Close()
        
        # Spot diagram subplots - show multiple wavelengths if selected
        for plot_idx, field_idx in enumerate(field_indices[:3]):  # Limit to 3 fields for layout
            ax = plt.subplot2grid((3, 3), (1, plot_idx))
            
            # Plot selected wavelengths
            for wave_plot_idx, wave_idx in enumerate(wave_indices):
                # Get wavelength information
                spot_data = self.analyzer.analyze_spot_diagram(field_index=field_idx, wavelength_index=wave_idx, max_rays=500)
                
                # Get wavelength information
                wavelength = self.TheSystem.SystemData.Wavelengths.GetWavelength(wave_idx + 1)
                wave_value = wavelength.Wavelength
                
                color = self.colors[wave_idx % len(self.colors)]
                label = f'λ={wave_value:.3f}nm' if len(wave_indices) > 1 else ''
                
                ax.scatter(spot_data['x_coords'], spot_data['y_coords'], 
                          alpha=0.6, s=1, c=color, label=label)
            
            field = self.TheSystem.SystemData.Fields.GetField(field_idx + 1)
            ax.set_title(f'Spot F{field_idx+1}: Y={field.Y:.2f}')
            ax.set_xlabel('X (mm)')
            ax.set_ylabel('Y (mm)')
            ax.set_aspect('equal', adjustable='datalim')
            ax.grid(True, alpha=0.3)
            
            if len(wave_indices) > 1:
                ax.legend()
        
        # Ray fan subplots - show multiple wavelengths if selected
        for plot_idx, field_idx in enumerate(field_indices[:3]):  # Limit to 3 fields for layout
            ax = plt.subplot2grid((3, 3), (2, plot_idx))
            
            # Plot selected wavelengths
            for wave_plot_idx, wave_idx in enumerate(wave_indices):
                ray_fan_data = self.analyzer.analyze_ray_fan(field_index=field_idx, wavelength_index=wave_idx, fan_type="Y", num_rays=21)
                
                # Get wavelength information
                wavelength = self.TheSystem.SystemData.Wavelengths.GetWavelength(wave_idx + 1)
                wave_value = wavelength.Wavelength
                
                color = self.colors[wave_idx % len(self.colors)]
                linestyle = ['-', '--', '-.', ':'][wave_plot_idx % 4]
                label = f'λ={wave_value:.3f}nm' if len(wave_indices) > 1 else ''
                
                ax.plot(ray_fan_data['pupil_coords'], ray_fan_data['ray_errors'], 
                       color=color, linestyle=linestyle, linewidth=2, 
                       marker='o', markersize=2, label=label)
            
            ax.set_title(f'Ray Fan F{field_idx+1}Y')
            ax.set_xlabel('Pupil Coordinate')
            ax.set_ylabel('Ray Error (mm)')
            ax.grid(True, alpha=0.3)
            ax.axhline(y=0, color='black', linestyle='-', alpha=0.5)
            
            if len(wave_indices) > 1:
                ax.legend()
        
        # Create title based on selections
        if title is None:
            title_parts = ["Comprehensive Optical Analysis"]
            if fields == "all":
                title_parts.append("All Fields")
            elif fields == "single":
                title_parts.append("Single Field")
            else:
                title_parts.append("Selected Fields")
                
            if wavelengths == "all":
                title_parts.append("All Wavelengths")
            elif wavelengths == "single":
                title_parts.append("Primary Wavelength")
            else:
                title_parts.append("Selected Wavelengths")
            
            title = ' - '.join(title_parts)
        
        plt.suptitle(title, fontsize=16)
        plt.tight_layout()
        
        if save_path:
            plt.savefig(save_path, dpi=300, bbox_inches='tight')
            logger.info(f"Comprehensive analysis plot saved to: {save_path}")
        
        return fig


    def analyze_and_plot_system(self, 
                         output_dir: str = ".", 
                         fields: Union[str, List[int], int] = "all", 
                         wavelengths: Union[str, List[int], int] = "all",
                         include_layouts: bool = True, 
                         is_nsc: bool = False) -> Dict[str, str]:
        """
        一键分析和绘制系统的所有图表
        
        Args:
            output_dir: 保存图表的目录
            fields: "all", "single"(第一个视场), 或视场索引列表(0-based)
            wavelengths: "all", "single"(主波长), 或波长索引列表(0-based)
            include_layouts: 是否生成系统布局图
            is_nsc: 是否是非序列系统
            
        Returns:
            包含已保存文件路径的字典
        """
        from pathlib import Path
        import os
        
        output_path = Path(output_dir)
        output_path.mkdir(parents=True, exist_ok=True)  # 如果目录不存在则创建
        
        # Clean up any old field curvature and distortion files to prevent confusion
        for old_file in output_path.glob("field_curvature_distortion*.png"):
            try:
                os.remove(old_file)
                logger.info(f"Removed old file: {old_file}")
            except Exception as e:
                logger.warning(f"Failed to remove old file {old_file}: {e}")
        
        saved_files = {}
        
        # 使用指定的视场/波长选择绘制所有分析类型
        try:
            # MTF
            fig = self.plot_mtf(fields=fields, wavelengths=wavelengths, 
                           save_path=str(output_path / "system_mtf.png"))
            plt.close()
            saved_files['mtf'] = str(output_path / "system_mtf.png")
            
            # 点列图
            fig = self.plot_spots(fields=fields, wavelengths=wavelengths,
                             save_path=str(output_path / "multifield_spots.png"))
            plt.close()
            saved_files['spots'] = str(output_path / "multifield_spots.png")
            
            # 光线扇形图
            fig = self.plot_rayfan(fields=fields, wavelengths=wavelengths,
                              save_path=str(output_path / "multifield_rayfan.png"))
            plt.close()
            saved_files['rayfan'] = str(output_path / "multifield_rayfan.png")
            
            # 场曲和畸变
            fig = self.plot_field_curvature_distortion(wavelengths=wavelengths,
                                               save_path=str(output_path / "field_curvature_distortion.png"))
            plt.close()
            saved_files['distortion'] = str(output_path / "field_curvature_distortion.png")
            
            # 综合分析
            fig = self.plot_mtf_spot_ranfan(fields=fields, wavelengths=wavelengths,
                                       save_path=str(output_path / "comprehensive_analysis.png"))
            plt.close()
            saved_files['comprehensive'] = str(output_path / "comprehensive_analysis.png")
            
            logger.info(f"All analysis plots saved to: {output_dir}")
            
        except Exception as e:
            logger.error(f"Error in analyze_and_plot_system: {e}")
        
        return saved_files
# def plot_rayfan(zos_manager, analyzer, 
#                           fields: str = "all", wavelengths: str = "single",
#                           save_path: Optional[str] = None) -> plt.Figure:
#     """
#     Plot ray fan diagrams for specified fields and wavelengths
    
#     Args:
#         zos_manager: ZOSAPI manager instance
#         analyzer: ZOSAnalyzer instance
#         fields: "all", "single" (first field), or list of field indices (0-based)
#         wavelengths: "all", "single" (primary), or list of wavelength indices (0-based)
#         save_path: Path to save the plot
        
#     Returns:
#         Figure object
#     """
#     system = zos_manager.TheSystem
#     num_fields = system.SystemData.Fields.NumberOfFields
#     num_wavelengths = system.SystemData.Wavelengths.NumberOfWavelengths
    
#     # Parse field selection
#     if fields == "all":
#         field_indices = list(range(num_fields))
#     elif fields == "single":
#         field_indices = [0]  # First field
#     else:
#         field_indices = fields if isinstance(fields, list) else [fields]
    
#     # Parse wavelength selection  
#     if wavelengths == "all":
#         wave_indices = list(range(num_wavelengths))
#     elif wavelengths == "single":
#         # Find primary wavelength
#         primary_wave = 0
#         for i in range(1, num_wavelengths + 1):
#             if system.SystemData.Wavelengths.GetWavelength(i).IsPrimary:
#                 primary_wave = i - 1  # Convert to 0-based
#                 break
#         wave_indices = [primary_wave]
#     else:
#         wave_indices = wavelengths if isinstance(wavelengths, list) else [wavelengths]
    
#     num_selected_fields = len(field_indices)
#     num_selected_waves = len(wave_indices)
    
#     # Create subplot layout: 2 rows (X and Y fans) x num_fields columns
#     if num_selected_fields == 1:
#         fig, axes = plt.subplots(2, 1, figsize=(8, 10))
#         axes = axes.reshape(2, 1)
#     else:
#         fig, axes = plt.subplots(2, num_selected_fields, figsize=(4*num_selected_fields, 8))
#         if axes.ndim == 1:
#             axes = axes.reshape(2, 1)
    
#     # Colors for different wavelengths
#     colors = ['b', 'g', 'r', 'c', 'm', 'y', 'k']
#     linestyles = ['-', '--']
    
#     # Plot for each selected field
#     for plot_idx, field_idx in enumerate(field_indices):
#         # Get field information
#         field = system.SystemData.Fields.GetField(field_idx + 1)
        
#         # X fan subplot
#         ax_x = axes[0, plot_idx] if num_selected_fields > 1 else axes[0, 0]
        
#         # Y fan subplot  
#         ax_y = axes[1, plot_idx] if num_selected_fields > 1 else axes[1, 0]
        
#         # Plot each selected wavelength
#         for wave_plot_idx, wave_idx in enumerate(wave_indices):
#             # Get wavelength information
#             wavelength = system.SystemData.Wavelengths.GetWavelength(wave_idx + 1)
#             wave_value = wavelength.Wavelength
            
#             color = colors[wave_idx % len(colors)]
#             linestyle = linestyles[wave_plot_idx % len(linestyles)]
            
#             # X fan
#             ray_fan_x = analyzer.analyze_ray_fan(
#                 field_index=field_idx, 
#                 wavelength_index=wave_idx, 
#                 fan_type="X", 
#                 num_rays=21
#             )
            
#             label_x = f'λ={wave_value:.3f}nm' if num_selected_waves > 1 else ''
#             ax_x.plot(ray_fan_x['pupil_coords'], ray_fan_x['ray_errors'], 
#                      color=color, linestyle=linestyle, linewidth=2, 
#                      marker='o', markersize=2, label=label_x)
            
#             # Y fan
#             ray_fan_y = analyzer.analyze_ray_fan(
#                 field_index=field_idx, 
#                 wavelength_index=wave_idx, 
#                 fan_type="Y", 
#                 num_rays=21
#             )
            
#             label_y = f'λ={wave_value:.3f}nm' if num_selected_waves > 1 else ''
#             ax_y.plot(ray_fan_y['pupil_coords'], ray_fan_y['ray_errors'], 
#                      color=color, linestyle=linestyle, linewidth=2, 
#                      marker='o', markersize=2, label=label_y)
        
#         # Format X fan subplot
#         ax_x.set_title(f'Field {field_idx+1} (Y={field.Y:.1f}) - X Fan')
#         ax_x.set_xlabel('Pupil Coordinate')
#         ax_x.set_ylabel('Ray Error (mm)')
#         ax_x.grid(True, alpha=0.3)
#         ax_x.axhline(y=0, color='black', linestyle='-', alpha=0.5)
#         if num_selected_waves > 1:
#             ax_x.legend()
        
#         # Format Y fan subplot
#         ax_y.set_title(f'Field {field_idx+1} (Y={field.Y:.1f}) - Y Fan')
#         ax_y.set_xlabel('Pupil Coordinate')
#         ax_y.set_ylabel('Ray Error (mm)')
#         ax_y.grid(True, alpha=0.3)
#         ax_y.axhline(y=0, color='black', linestyle='-', alpha=0.5)
#         if num_selected_waves > 1:
#             ax_y.legend()
    
#     # Create title based on selections
#     title_parts = []
#     if fields == "all":
#         title_parts.append("All Fields")
#     elif fields == "single":
#         title_parts.append("Single Field")
#     else:
#         title_parts.append(f"Fields {field_indices}")
        
#     if wavelengths == "all":
#         title_parts.append("All Wavelengths")
#     elif wavelengths == "single":
#         title_parts.append("Primary Wavelength")
#     else:
#         title_parts.append(f"Wavelengths {wave_indices}")
    
#     plt.suptitle(f'Ray Fan Analysis - {" & ".join(title_parts)}', fontsize=14)
#     plt.tight_layout()
    
#     if save_path:
#         plt.savefig(save_path, dpi=300, bbox_inches='tight')
#         logger.info(f"Multi-field ray fan plots saved to: {save_path}")
    
#     return fig


# def plot_mtf(zos_manager, 
#                    fields: str = "all", wavelengths: str = "all",
#                    max_frequency: float = 100,
#                    save_path: Optional[str] = None) -> plt.Figure:
#     """
#     Plot MTF for specified fields and wavelengths using Zemax built-in analysis
    
#     Args:
#         zos_manager: ZOSAPI manager instance
#         fields: "all", "single" (first field), or list of field indices (0-based)
#         wavelengths: "all", "single" (primary), or list of wavelength indices (0-based)
#         max_frequency: Maximum spatial frequency to analyze
#         save_path: Path to save the plot
        
#     Returns:
#         Figure object
#     """
#     from .zosapi_utils import reshape_zos_data
    
#     system = zos_manager.TheSystem
    
#     # Create FFT MTF analysis (following Official Example 4)
#     mtf_analysis = system.Analyses.New_FftMtf()
#     mtf_settings = mtf_analysis.GetSettings()
#     mtf_settings.MaximumFrequency = max_frequency
#     mtf_settings.SampleSize = zos_manager.ZOSAPI.Analysis.SampleSizes.S_256x256
    
#     # Parse field and wavelength selections for analysis configuration
#     if fields != "all":
#         # Configure specific fields if needed - implementation depends on API version
#         pass
#     if wavelengths != "all":
#         # Configure specific wavelengths if needed - implementation depends on API version  
#         pass
    
#     # Run analysis
#     mtf_analysis.ApplyAndWaitForCompletion()
#     mtf_results = mtf_analysis.GetResults()
    
#     # Plot MTF curves
#     plt.figure(figsize=(12, 8))
#     colors = ('b','g','r','c', 'm', 'y', 'k')
#     linestyles = ['-', '--']
#     legend_labels = []
    
#     for seriesNum in range(0, mtf_results.NumberOfDataSeries):
#         data = mtf_results.GetDataSeries(seriesNum)
        
#         # Get data
#         xRaw = data.XData.Data
#         yRaw = data.YData.Data
        
#         x = list(xRaw)
#         y = reshape_zos_data(yRaw, yRaw.GetLength(0), yRaw.GetLength(1), True)
        
#         # Plot tangential and sagittal MTF
#         color = colors[seriesNum % len(colors)]
#         plt.plot(x, y[0], color=color, linewidth=2, linestyle=linestyles[0])  # Tangential
#         plt.plot(x, y[1], color=color, linewidth=2, linestyle=linestyles[1])  # Sagittal
        
#         legend_labels.extend([f'Series {seriesNum+1} Tangential', f'Series {seriesNum+1} Sagittal'])
    
#     # Create title based on selections
#     title_parts = ["MTF Analysis"]
#     if fields == "all":
#         title_parts.append("All Fields")
#     elif fields == "single":
#         title_parts.append("Single Field")
#     else:
#         title_parts.append("Selected Fields")
        
#     if wavelengths == "all":
#         title_parts.append("All Wavelengths")
#     elif wavelengths == "single":
#         title_parts.append("Primary Wavelength")
#     else:
#         title_parts.append("Selected Wavelengths")
    
#     plt.title(' - '.join(title_parts))
#     plt.xlabel('Spatial Frequency (cycles/mm)')
#     plt.ylabel('MTF')
#     plt.grid(True, alpha=0.3)
#     plt.legend(legend_labels[:min(len(legend_labels), 10)])  # Limit legend entries
#     plt.ylim(0, 1.1)
#     plt.tight_layout()
    
#     if save_path:
#         plt.savefig(save_path, dpi=300, bbox_inches='tight')
#         logger.info(f"System MTF plot saved to: {save_path}")
    
#     # Close analysis
#     mtf_analysis.Close()
    
#     return plt.gcf()


# def plot_mtf_spot_ranfan(zos_manager, analyzer, 
#                                fields: str = "all", wavelengths: str = "all",
#                                save_path: Optional[str] = None) -> plt.Figure:
#     """
#     Create a comprehensive analysis plot with MTF, spot diagrams, and ray fans
    
#     Args:
#         zos_manager: ZOSAPI manager instance
#         analyzer: ZOSAnalyzer instance
#         fields: "all", "single" (first field), or list of field indices (0-based)
#         wavelengths: "all", "single" (primary), or list of wavelength indices (0-based)
#         save_path: Path to save the plot
        
#     Returns:
#         Figure object
#     """
#     from .zosapi_utils import reshape_zos_data
    
#     system = zos_manager.TheSystem
#     num_fields = system.SystemData.Fields.NumberOfFields
#     num_wavelengths = system.SystemData.Wavelengths.NumberOfWavelengths
    
#     # Parse field selection
#     if fields == "all":
#         field_indices = list(range(num_fields))
#     elif fields == "single":
#         field_indices = [0]  # First field
#     else:
#         field_indices = fields if isinstance(fields, list) else [fields]
    
#     # Parse wavelength selection  
#     if wavelengths == "all":
#         wave_indices = list(range(num_wavelengths))
#     elif wavelengths == "single":
#         # Find primary wavelength
#         primary_wave = 0
#         for i in range(1, num_wavelengths + 1):
#             if system.SystemData.Wavelengths.GetWavelength(i).IsPrimary:
#                 primary_wave = i - 1  # Convert to 0-based
#                 break
#         wave_indices = [primary_wave]
#     else:
#         wave_indices = wavelengths if isinstance(wavelengths, list) else [wavelengths]
    
#     fig = plt.figure(figsize=(16, 12))
    
#     # MTF subplot (top section)
#     ax1 = plt.subplot2grid((3, 3), (0, 0), colspan=3)
    
#     # Create MTF analysis
#     mtf_analysis = system.Analyses.New_FftMtf()
#     mtf_settings = mtf_analysis.GetSettings()
#     mtf_settings.MaximumFrequency = 50
#     mtf_analysis.ApplyAndWaitForCompletion()
#     mtf_results = mtf_analysis.GetResults()
    
#     colors = ('b','g','r','c', 'm', 'y', 'k')
#     for seriesNum in range(0, min(mtf_results.NumberOfDataSeries, len(colors))):
#         data = mtf_results.GetDataSeries(seriesNum)
#         xRaw = data.XData.Data
#         yRaw = data.YData.Data
#         x = list(xRaw)
#         y = reshape_zos_data(yRaw, yRaw.GetLength(0), yRaw.GetLength(1), True)
        
#         ax1.plot(x, y[0], color=colors[seriesNum], linewidth=2, label=f'Field {seriesNum+1} T')
#         ax1.plot(x, y[1], linestyle='--', color=colors[seriesNum], linewidth=2, label=f'Field {seriesNum+1} S')
    
#     ax1.set_title('MTF - 全部视场')
#     ax1.set_xlabel('空间频率 (周期/mm)')
#     ax1.set_ylabel('MTF')
#     ax1.grid(True, alpha=0.3)
#     ax1.legend(bbox_to_anchor=(1.05, 1), loc='upper left')
    
#     mtf_analysis.Close()
    
#     # 点列图子图 - 显示多个波长（如果已选择）
#     for plot_idx, field_idx in enumerate(field_indices[:3]):  # 限制为3个视场用于布局
#         ax = plt.subplot2grid((3, 3), (1, plot_idx))
        
#         # 绘制选定的波长
#         for wave_plot_idx, wave_idx in enumerate(wave_indices):
#             spot_data = analyzer.analyze_spot_diagram(field_index=field_idx, wavelength_index=wave_idx, max_rays=500)
            
#             # 获取波长信息
#             wavelength = system.SystemData.Wavelengths.GetWavelength(wave_idx + 1)
#             wave_value = wavelength.Wavelength
            
#             color = colors[wave_idx % len(colors)]
#             label = f'λ={wave_value:.3f}nm' if len(wave_indices) > 1 else ''
            
#             ax.scatter(spot_data['x_coords'], spot_data['y_coords'], 
#                       alpha=0.6, s=1, c=color, label=label)
        
#         field = system.SystemData.Fields.GetField(field_idx + 1)
#         ax.set_title(f'点列图 F{field_idx+1}: Y={field.Y:.2f}')
#         ax.set_xlabel('X (mm)')
#         ax.set_ylabel('Y (mm)')
#         ax.set_aspect('equal', adjustable='datalim')
#         ax.grid(True, alpha=0.3)
        
#         if len(wave_indices) > 1:
#             ax.legend()
    
#     # 光线扇形图子图 - 显示多个波长（如果已选择）
#     for plot_idx, field_idx in enumerate(field_indices[:3]):  # 限制为3个视场用于布局
#         ax = plt.subplot2grid((3, 3), (2, plot_idx))
        
#         # 绘制选定的波长
#         for wave_plot_idx, wave_idx in enumerate(wave_indices):
#             ray_fan_data = analyzer.analyze_ray_fan(field_index=field_idx, wavelength_index=wave_idx, fan_type="Y", num_rays=21)
            
#             # 获取波长信息
#             wavelength = system.SystemData.Wavelengths.GetWavelength(wave_idx + 1)
#             wave_value = wavelength.Wavelength
            
#             color = colors[wave_idx % len(colors)]
#             linestyle = ['-', '--', '-.', ':'][wave_plot_idx % 4]
#             label = f'λ={wave_value:.3f}nm' if len(wave_indices) > 1 else ''
            
#             ax.plot(ray_fan_data['pupil_coords'], ray_fan_data['ray_errors'], 
#                    color=color, linestyle=linestyle, linewidth=2, 
#                    marker='o', markersize=2, label=label)
        
#         ax.set_title(f'光线扇形图 F{field_idx+1}Y')
#         ax.set_xlabel('瞳坐标')
#         ax.set_ylabel('光线像差 (mm)')
#         ax.grid(True, alpha=0.3)
#         ax.axhline(y=0, color='black', linestyle='-', alpha=0.5)
        
#         if len(wave_indices) > 1:
#             ax.legend()
    
#     # 基于选择创建标题
#     if title is None:
#         title_parts = ["综合光学分析"]
#         if fields == "all":
#             title_parts.append("全部视场")
#         elif fields == "single":
#             title_parts.append("单视场")
#         else:
#             title_parts.append("选定视场")
            
#         if wavelengths == "all":
#             title_parts.append("全部波长")
#         elif wavelengths == "single":
#             title_parts.append("主波长")
#         else:
#             title_parts.append("选定波长")
        
#         title = ' - '.join(title_parts)
    
#     plt.suptitle(title, fontsize=16)
#     plt.tight_layout()
    
#     if save_path:
#         plt.savefig(save_path, dpi=300, bbox_inches='tight')
#         logger.info(f"综合分析图已保存至: {save_path}")
    
#     return fig


# def plot_field_curvature_distortion(zos_manager, analyzer,
#                                    wavelengths: Union[str, List[int], int] = "all",
#                                    save_path: Optional[str] = None) -> plt.Figure:
#     """
#     Plot field curvature and distortion analysis for multiple wavelengths
    
#     Args:
#         zos_manager: ZOSAPI manager instance
#         analyzer: ZOSAnalyzer instance
#         wavelengths: "all", "single" (primary), or list of wavelength indices (0-based)
#         save_path: Path to save the plot
        
#     Returns:
#         Figure object
#     """
#     # Create subplots
#     fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(15, 6))
    
#     system = zos_manager.TheSystem
#     num_wavelengths = system.SystemData.Wavelengths.NumberOfWavelengths
    
#     # Parse wavelength selection  
#     if wavelengths == "all":
#         wave_indices = list(range(num_wavelengths))
#     elif wavelengths == "single":
#         # Find primary wavelength
#         primary_wave = 0
#         for i in range(1, num_wavelengths + 1):
#             if system.SystemData.Wavelengths.GetWavelength(i).IsPrimary:
#                 primary_wave = i - 1  # Convert to 0-based
#                 break
#         wave_indices = [primary_wave]
#     else:
#         if isinstance(wavelengths, int):
#             wave_indices = [wavelengths]
#         else:
#             wave_indices = wavelengths if isinstance(wavelengths, list) else [wavelengths]
    
#     # Colors for different wavelengths - Zemax风格色彩
#     colors = ('b', 'g', 'r', 'c', 'm', 'y', 'k')
#     linestyles = ['-', '--']  # 实线用于切向(T)，虚线用于弧矢(S)
    
#     legend_entries = []
    
#     # 遍历所有选定的波长
#     for wave_idx, wavelength_index in enumerate(wave_indices):
#         # Get wavelength information
#         wavelength = system.SystemData.Wavelengths.GetWavelength(wavelength_index + 1)
#         wave_value = wavelength.Wavelength
        
#         # 为当前波长选择颜色
#         color = colors[wave_idx % len(colors)]
        
#         # Analyze field curvature and distortion for this wavelength
#         distortion_data = analyzer.analyze_field_curvature_distortion(num_points=50, wavelength_index=wavelength_index)
        
#         # Plot field curvature for this wavelength
#         if distortion_data['field_heights']:
#             field_heights = distortion_data['field_heights']
#             tangential_fc = distortion_data['tangential_field_curvature']
#             sagittal_fc = distortion_data['sagittal_field_curvature']
            
#             # 切向曲线 (T) - 实线 - 注意X、Y轴交换
#             if tangential_fc:
#                 ax1.plot(tangential_fc, field_heights, color=color, linestyle=linestyles[0], linewidth=2, 
#                         label=f'{wave_value:.4f}-Tangential')
#                 legend_entries.append(f'{wave_value:.4f}-Tangential')
                
#             # 弧矢曲线 (S) - 虚线 - 注意X、Y轴交换
#             if sagittal_fc:
#                 ax1.plot(sagittal_fc, field_heights, color=color, linestyle=linestyles[1], linewidth=2,
#                         label=f'{wave_value:.4f}-Sagittal')
#                 legend_entries.append(f'{wave_value:.4f}-Sagittal')
        
#         # Plot distortion for this wavelength
#         if distortion_data['distortion_percent']:
#             distortion = distortion_data['distortion_percent']
#             ax2.plot(distortion, field_heights, color=color, linewidth=2,
#                     label=f'{wave_value:.4f}')
    
#     # Format field curvature subplot - 交换X、Y轴标签
#     ax1.set_title('Field Curvature')
#     ax1.set_xlabel('Field Curvature (mm)')
#     ax1.set_ylabel('Field Height')
#     ax1.grid(True, alpha=0.3)
#     ax1.axvline(x=0, color='black', linestyle='-', alpha=0.3)  # 零线现在是垂直的
    
#     if legend_entries:
#         ax1.legend()
#     else:
#         ax1.text(0.5, 0.5, 'No Field Curvature Data', 
#                 transform=ax1.transAxes, ha='center', va='center')
    
#     # Format distortion subplot - 交换X、Y轴标签
#     ax2.set_title('Distortion')
#     ax2.set_xlabel('Distortion (%)')
#     ax2.set_ylabel('Field Height')
#     ax2.grid(True, alpha=0.3)
#     ax2.axvline(x=0, color='black', linestyle='-', alpha=0.3)  # 零线现在是垂直的
    
#     if ax2.get_lines():
#         ax2.legend()
#     else:
#         ax2.text(0.5, 0.5, 'No Distortion Data', 
#                 transform=ax2.transAxes, ha='center', va='center')
    
#     # Create title based on wavelength selection
#     if wavelengths == "all":
#         title = "Field Curvature and Distortion Analysis - All Wavelengths"
#     elif wavelengths == "single":
#         title = f"Field Curvature and Distortion Analysis - Primary Wavelength"
#     else:
#         if len(wave_indices) == 1:
#             wavelength = system.SystemData.Wavelengths.GetWavelength(wave_indices[0] + 1)
#             wave_value = wavelength.Wavelength
#             title = f"Field Curvature and Distortion Analysis (λ={wave_value:.4f}nm)"
#         else:
#             title = f"Field Curvature and Distortion Analysis - Selected Wavelengths"
    
#     plt.suptitle(title, fontsize=14)
#     plt.tight_layout()
    
#     if save_path:
#         plt.savefig(save_path, dpi=300, bbox_inches='tight')
#         logger.info(f"Field curvature and distortion plot saved to: {save_path}")
    
#     return fig





# # === Super convenient one-liner functions ===

# def analyze_and_plot_system(zos_manager, output_dir: str = ".", 
#                            fields: str = "all", wavelengths: str = "all",
#                            include_layouts: bool = True, is_nsc: bool = False) -> Dict[str, str]:
#     """
#     One-liner function to analyze and plot everything for a loaded system
    
#     Args:
#         zos_manager: ZOSAPI manager instance
#         output_dir: Directory to save plots
#         fields: "all", "single" (first field), or list of field indices (0-based)
#         wavelengths: "all", "single" (primary), or list of wavelength indices (0-based)
#         include_layouts: Whether to generate system layout plots
#         is_nsc: Whether this is an NSC (Non-Sequential Components) system
        
#     Returns:
#         Dictionary with saved file paths
#     """
#     from pathlib import Path
#     from .zosapi_analysis import ZOSAnalyzer
#     import os
    
#     output_path = Path(output_dir)
#     output_path.mkdir(parents=True, exist_ok=True)  # Create directory if it doesn't exist
    
#     # 清理可能存在的旧场曲和畸变文件，防止混淆
#     for old_file in output_path.glob("field_curvature_distortion*.png"):
#         try:
#             os.remove(old_file)
#             logger.info(f"Removed old file: {old_file}")
#         except Exception as e:
#             logger.warning(f"Failed to remove old file {old_file}: {e}")
    
#     analyzer = ZOSAnalyzer(zos_manager)
    
#     saved_files = {}
    
#     # Plot all analysis types with specified field/wavelength selections
#     try:
#         # MTF
#         fig = plot_mtf(zos_manager, fields=fields, wavelengths=wavelengths, 
#                              save_path=str(output_path / "system_mtf.png"))
#         plt.close()
#         saved_files['mtf'] = str(output_path / "system_mtf.png")
        
#         # Spot diagrams
#         fig = plot_spots(zos_manager, analyzer, fields=fields, wavelengths=wavelengths,
#                                    save_path=str(output_path / "multifield_spots.png"))
#         plt.close()
#         saved_files['spots'] = str(output_path / "multifield_spots.png")
        
#         # Ray fans
#         fig = plot_rayfan(zos_manager, analyzer, fields=fields, wavelengths=wavelengths,
#                                     save_path=str(output_path / "multifield_rayfan.png"))
#         plt.close()
#         saved_files['rayfan'] = str(output_path / "multifield_rayfan.png")
        
#         # Field curvature and distortion
#         # 场曲和畸变分析 - 使用所有选定的波长
#         fig = plot_field_curvature_distortion(zos_manager, analyzer,
#                                              wavelengths=wavelengths,
#                                              save_path=str(output_path / "field_curvature_distortion.png"))
#         plt.close()
#         saved_files['distortion'] = str(output_path / "field_curvature_distortion.png")
        
#         # Comprehensive
#         fig = plot_mtf_spot_ranfan(zos_manager, analyzer, fields=fields, wavelengths=wavelengths,
#                                          save_path=str(output_path / "comprehensive_analysis.png"))
#         plt.close()
#         saved_files['comprehensive'] = str(output_path / "comprehensive_analysis.png")
        
#         logger.info(f"All analysis plots saved to: {output_dir}")
        
#     except Exception as e:
#         logger.error(f"Error in analyze_and_plot_system: {e}")
    
#     return saved_files