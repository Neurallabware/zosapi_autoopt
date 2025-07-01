"""
Zemax OpticStudio Layout 分析模块
提供统一的光学系统Layout绘制和导出功能
Author: allin-love
Date: 2025-07-01
"""

import os
import logging
from typing import Optional, Dict, List, Union, Any
from pathlib import Path
import matplotlib.pyplot as plt

LAYOUT_TYPE_DESCRIPTIONS = {
        "cross_section": "系统截面图",
        "3d_viewer": "3D视图", 
        "shaded_model": "着色模型"
    }

logger = logging.getLogger(__name__)


class ZOSLayoutAnalyzer:
    """
    Zemax 光学系统Layout分析器
    提供2D/3D系统布局图的生成和导出功能
    """
    
    def __init__(self, zos_manager):
        """
        初始化Layout分析器
        
        Args:
            zos_manager: ZOSAPI管理器实例
        """
        self.zos_manager = zos_manager
        self.system = zos_manager.TheSystem
        self.layouts_interface = self.system.Tools.Layouts

    def _prepare_save_path(self, save_path: str) -> str:
        """
        预处理保存路径，确保路径有效且可写
        
        Args:
            save_path: 原始保存路径
            
        Returns:
            处理后的保存路径，失败时返回None
        """
        try:
            import tempfile
            
            path_obj = Path(save_path)
            
            # 确保路径是绝对路径
            if not path_obj.is_absolute():
                path_obj = Path.cwd() / path_obj
            
            # 确保目录存在
            path_obj.parent.mkdir(parents=True, exist_ok=True)
            
            # 检查目录权限
            if not os.access(path_obj.parent, os.W_OK):
                logger.warning(f"Directory not writable: {path_obj.parent}")
                # 使用临时目录
                temp_path = Path(tempfile.gettempdir()) / path_obj.name
                logger.info(f"Using temporary directory: {temp_path}")
                path_obj = temp_path
                path_obj.parent.mkdir(parents=True, exist_ok=True)
            
            # 确保文件扩展名为PNG
            if not path_obj.suffix.lower() == '.png':
                path_obj = path_obj.with_suffix('.png')
            
            # 如果文件已存在，删除它
            if path_obj.exists():
                try:
                    path_obj.unlink()
                except:
                    pass
            
            return str(path_obj)
            
        except Exception as e:
            logger.error(f"Path preparation failed: {e}")
            return None

    def export_cross_section(self, save_path: str, **config) -> bool:
        """
        导出截面图 (Cross Section Layout)
        
        Args:
            save_path: 保存路径
            **config: 配置选项
                - output_pixel_width: int (图像宽度，默认1920)
                - output_pixel_height: int (图像高度，默认1080) 
                - start_surface: int (起始面，默认-1)
                - end_surface: int (结束面，默认最后一面-1)
                - number_of_rays: int (光线数量，默认7)
                - y_stretch: float (Y轴拉伸比例，默认1.0)
                - fletch_rays: bool (是否显示羽毛状光线，默认False)
                - wavelength: int (波长索引，-1表示所有波长，默认-1)
                - field: int (视场索引，-1表示所有视场，默认-1)
                - configuration: int (配置索引，默认-1)
                - color_rays_by: str (光线颜色分类方式: 'Wavelength', 'Fields', 'Waves')
                - upper_pupil: float (上光瞳，默认1.0)
                - lower_pupil: float (下光瞳，默认-1.0)
                - marginal_and_chief_ray_only: bool (仅主边缘光线，默认False)
                - delete_vignetted: bool (删除渐晕光线，默认False)
                - surface_line_thickness: str (表面线厚度: 'Thinnest', 'Thin', 'Standard', 'Thick', 'Thickest')
                - rays_line_thickness: str (光线线厚度: 'Thinnest', 'Thin', 'Standard', 'Thick', 'Thickest')
                - save_image_as_file: bool (是否保存为文件，默认True)
                
        Returns:
            bool: 导出是否成功
        """

        # 预处理保存路径
        save_path = self._prepare_save_path(save_path)
        if not save_path:
            logger.error("Save path preparation failed")
            return False
        
        # 创建CrossSectionExport对象
        cross_export = self.layouts_interface.OpenCrossSectionExport()
        
        if cross_export is None:
            logger.error("Failed to create CrossSectionExport object")
            return False
        
        # === 左侧面板设置 ===
        # 表面范围设置
        cross_export.StartSurface = config.get('start_surface', -1)
        num_surfaces = self.system.LDE.NumberOfSurfaces
        cross_export.EndSurface = config.get('end_surface', num_surfaces - 1)
        
        # 光线设置
        cross_export.NumberOfRays = config.get('number_of_rays', 7)
        cross_export.YStretch = config.get('y_stretch', 1.0)
        cross_export.FletchRays = config.get('fletch_rays', False)
        
        # === 右侧面板设置 ===
        # 分析参数（-1表示所有）
        cross_export.Wavelength = config.get('wavelength', -1)  # -1 = all wavelengths
        cross_export.Field = config.get('field', -1)  # -1 = all fields
        
        # 光线颜色分类设置
        color_option = config.get('color_rays_by', 'fields')
        try:
            ZOSAPI = self.zos_manager.ZOSAPI
            if color_option.lower() in ['wavelength', 'waves']:
                cross_export.ColorRaysBy = ZOSAPI.Tools.Layouts.ColorRaysByCrossSectionOptions.Wavelength
            elif color_option.lower() == 'fields':
                cross_export.ColorRaysBy = ZOSAPI.Tools.Layouts.ColorRaysByCrossSectionOptions.Fields
            else:
                # 默认使用波长
                cross_export.ColorRaysBy = ZOSAPI.Tools.Layouts.ColorRaysByCrossSectionOptions.Wavelength
        except Exception as e:
            logger.warning(f"Could not set color rays by option: {e}")
        
        # 光瞳范围设置
        cross_export.UpperPupil = config.get('upper_pupil', 1.0)
        cross_export.LowerPupil = config.get('lower_pupil', -1.0)
        
        # 光线过滤选项
        cross_export.DeleteVignetted = config.get('delete_vignetted', False)
        cross_export.MarginalAndChiefRayOnly = config.get('marginal_and_chief_ray_only', False)
        
        # === 线条厚度设置 ===
        try:
            ZOSAPI = self.zos_manager.ZOSAPI
            # 表面线厚度
            surface_thickness = config.get('surface_line_thickness', 'Standard')
            if surface_thickness == 'Thinnest':
                cross_export.SurfaceLineThickness = ZOSAPI.Tools.Layouts.LineThicknessOptions.Thinnest
            elif surface_thickness == 'Thin':
                cross_export.SurfaceLineThickness = ZOSAPI.Tools.Layouts.LineThicknessOptions.Thin
            elif surface_thickness == 'Standard':
                cross_export.SurfaceLineThickness = ZOSAPI.Tools.Layouts.LineThicknessOptions.Standard
            elif surface_thickness == 'Thick':
                cross_export.SurfaceLineThickness = ZOSAPI.Tools.Layouts.LineThicknessOptions.Thick
            elif surface_thickness == 'Thickest':
                cross_export.SurfaceLineThickness = ZOSAPI.Tools.Layouts.LineThicknessOptions.Thickest
            
            # 光线线厚度
            rays_thickness = config.get('rays_line_thickness', 'Standard')
            if rays_thickness == 'Thinnest':
                cross_export.RaysLineThickness = ZOSAPI.Tools.Layouts.LineThicknessOptions.Thinnest
            elif rays_thickness == 'Thin':
                cross_export.RaysLineThickness = ZOSAPI.Tools.Layouts.LineThicknessOptions.Thin
            elif rays_thickness == 'Standard':
                cross_export.RaysLineThickness = ZOSAPI.Tools.Layouts.LineThicknessOptions.Standard
            elif rays_thickness == 'Thick':
                cross_export.RaysLineThickness = ZOSAPI.Tools.Layouts.LineThicknessOptions.Thick
            elif rays_thickness == 'Thickest':
                cross_export.RaysLineThickness = ZOSAPI.Tools.Layouts.LineThicknessOptions.Thickest
        except Exception as e:
            logger.warning(f"Could not set line thickness options: {e}")
        
        # === 输出设置 ===
        cross_export.SaveImageAsFile = config.get('save_image_as_file', True)
        cross_export.OutputFileName = save_path
        cross_export.OutputPixelWidth = config.get('output_pixel_width', 1920)
        cross_export.OutputPixelHeight = config.get('output_pixel_height', 1080)
        
        logger.info(f"CrossSection设置: 表面{cross_export.StartSurface}-{cross_export.EndSurface}, "
                   f"光线数{cross_export.NumberOfRays}, 尺寸{cross_export.OutputPixelWidth}x{cross_export.OutputPixelHeight}")
        
        # 执行导出
        if cross_export.SaveImageAsFile:
            cross_export.Run()
    
    def export_3d_viewer(self, save_path: str, **config) -> bool:
        """
        导出3D Viewer布局图
        
        Args:
            save_path: 保存路径
            **config: 配置选项
            
        Returns:
            bool: 导出是否成功
        """
        try:
            # 预处理保存路径
            save_path = self._prepare_save_path(save_path)
            if not save_path:
                logger.error("Save path preparation failed")
                return False
                
            viewer_export = self.layouts_interface.Open3DViewerExport()
            
            if viewer_export is None:
                logger.error("Failed to create 3DViewerExport object")
                return False
            
            # 设置输出路径
            viewer_export.OutputFileName = save_path
            viewer_export.SaveImageAsFile = True
            
            # 执行导出
            viewer_export.Run()
            status = viewer_export.WaitWithTimeout(30.0)
            
            # 检查导出状态和文件
            if status == self.zos_manager.ZOSAPI.Tools.RunStatus.Completed:
                if Path(save_path).exists() and Path(save_path).stat().st_size > 0:
                    logger.info(f"3D viewer layout exported to: {save_path}")
                    return True
                else:
                    logger.error(f"3D viewer export completed but file invalid: {save_path}")
                    return False
            else:
                logger.error(f"3D viewer export failed with status: {status}")
                return False
                
        except Exception as e:
            logger.error(f"Error exporting 3D viewer layout: {str(e)}")
            return False
    
    def export_shaded_model(self, save_path: str, is_nsc: bool = False, **config) -> bool:
        """
        导出3D着色模型
        
        Args:
            save_path: 保存路径
            is_nsc: 是否为NSC系统
            **config: 配置选项
            
        Returns:
            bool: 导出是否成功
        """
        try:
            # 预处理保存路径
            save_path = self._prepare_save_path(save_path)
            if not save_path:
                logger.error("Save path preparation failed")
                return False
                
            if is_nsc:
                shaded_export = self.layouts_interface.OpenNSCShadedModelExport()
            else:
                shaded_export = self.layouts_interface.OpenShadedModelExport()
            
            if shaded_export is None:
                logger.error("Failed to create ShadedModelExport object")
                return False
            
            # 设置输出路径
            shaded_export.OutputFileName = save_path
            shaded_export.SaveImageAsFile = True
            
            # 执行导出
            shaded_export.Run()
            status = shaded_export.WaitWithTimeout(30.0)
            
            # 检查导出状态和文件
            if status == self.zos_manager.ZOSAPI.Tools.RunStatus.Completed:
                if Path(save_path).exists() and Path(save_path).stat().st_size > 0:
                    logger.info(f"Shaded model layout exported to: {save_path}")
                    return True
                else:
                    logger.error(f"Shaded model export completed but file invalid: {save_path}")
                    return False
            else:
                logger.error(f"Shaded model export failed with status: {status}")
                return False
                
        except Exception as e:
            logger.error(f"Error exporting shaded model layout: {str(e)}")
            return False
    
    def export_nsc_3d_layout(self, save_path: str, **config) -> bool:
        """
        导出NSC 3D Layout (仅适用于NSC系统)
        
        Args:
            save_path: 保存路径
            **config: 配置选项
            
        Returns:
            bool: 导出是否成功
        """
        try:
            nsc_layout_export = self.layouts_interface.OpenNSC3DLayoutExport()
            
            if nsc_layout_export is None:
                logger.error("Failed to create NSC3DLayoutExport object")
                return False
            
            # 设置输出路径
            nsc_layout_export.OutputFileName = save_path
            nsc_layout_export.SaveImageAsFile = True
            
            # 执行导出
            nsc_layout_export.Run()
            status = nsc_layout_export.WaitWithTimeout(60.0)
            
            if status == self.zos_manager.ZOSAPI.Tools.RunStatus.Completed:
                logger.info(f"NSC 3D layout exported to: {save_path}")
                return True
            else:
                logger.error(f"NSC 3D layout export failed with status: {status}")
                return False
                
        except Exception as e:
            logger.error(f"Error exporting NSC 3D layout: {str(e)}")
            return False
    

