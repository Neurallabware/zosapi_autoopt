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
    
    def generate_all_layouts(self, output_dir: str, is_nsc: bool = False, 
                           custom_config: Optional[Dict[str, Dict]] = None,
                           preset: str = "standard") -> Dict[str, str]:
        """
        生成所有适用的layout图
        
        Args:
            output_dir: 输出目录
            is_nsc: 是否为NSC系统
            custom_config: 自定义配置字典，格式如：
                {
                    'cross_section': {'number_of_rays': 50, 'y_stretch': 1.5},
                    '3d_viewer': {},
                    'shaded_model': {}
                }
            preset: 预设配置名称 ("draft", "standard", "high_quality", "publication")
                
        Returns:
            Dict[str, str]: 生成的文件路径字典
        """
        output_path = Path(output_dir)
        output_path.mkdir(parents=True, exist_ok=True)
        
        generated_files = {}
        
        # 获取预设配置
        if custom_config is None:
            config = get_preset_config(preset, is_nsc)
        else:
            # 合并预设配置和自定义配置
            config = get_preset_config(preset, is_nsc)
            for layout_type, params in custom_config.items():
                if layout_type in config:
                    config[layout_type].update(params)
                else:
                    config[layout_type] = params
        
        logger.info(f"使用配置预设: {preset}, NSC系统: {is_nsc}")
        logger.info(f"将生成的Layout类型: {list(config.keys())}")
        
        # 生成各种layout
        for layout_type, layout_config in config.items():
            try:
                file_path = str(output_path / f"layout_{layout_type}.png")
                
                success = False
                if layout_type == 'cross_section':
                    success = self.export_cross_section(file_path, **layout_config)
                elif layout_type == '3d_viewer':
                    success = self.export_3d_viewer(file_path, **layout_config)
                elif layout_type == 'shaded_model':
                    success = self.export_shaded_model(file_path, is_nsc=is_nsc, **layout_config)
                elif layout_type == 'nsc_3d_layout' and is_nsc:
                    success = self.export_nsc_3d_layout(file_path, **layout_config)
                
                if success:
                    generated_files[layout_type] = file_path
                    description = LAYOUT_TYPE_DESCRIPTIONS.get(layout_type, layout_type)
                    logger.info(f"✓ {description}: {file_path}")
                else:
                    logger.warning(f"✗ 生成失败: {layout_type}")
                    
            except Exception as e:
                logger.error(f"Failed to generate {layout_type}: {str(e)}")
                continue
        
        logger.info(f"成功生成 {len(generated_files)} 个layout文件，位于: {output_dir}")
        return generated_files
    
    def create_layout_comparison(self, layout_files: Dict[str, str], 
                               save_path: Optional[str] = None) -> plt.Figure:
        """
        创建layout对比图
        
        Args:
            layout_files: layout文件路径字典
            save_path: 保存路径
            
        Returns:
            matplotlib Figure对象
        """
        try:
            from PIL import Image
            
            num_layouts = len(layout_files)
            if num_layouts == 0:
                fig, ax = plt.subplots(figsize=(10, 6))
                ax.text(0.5, 0.5, 'No layout files provided', 
                       ha='center', va='center', transform=ax.transAxes, fontsize=16)
                ax.axis('off')
                return fig
            
            # 计算子图布局
            if num_layouts <= 2:
                rows, cols = 1, num_layouts
                fig_size = (8 * cols, 6)
            elif num_layouts <= 4:
                rows, cols = 2, 2
                fig_size = (12, 10)
            else:
                rows = (num_layouts + 2) // 3
                cols = 3
                fig_size = (15, 5 * rows)
            
            fig, axes = plt.subplots(rows, cols, figsize=fig_size)
            
            # 确保axes是可迭代的
            if rows == 1 and cols == 1:
                axes = [axes]
            elif rows == 1 or cols == 1:
                axes = axes.flatten()
            else:
                axes = axes.flatten()
            
            # 加载并显示每个layout图像
            for idx, (layout_name, image_path) in enumerate(layout_files.items()):
                if idx < len(axes):
                    ax = axes[idx]
                    try:
                        img = Image.open(image_path)
                        ax.imshow(img)
                        ax.set_title(layout_name.replace('_', ' ').title(), fontsize=12)
                        ax.axis('off')
                    except Exception as e:
                        ax.text(0.5, 0.5, f'Failed to load\n{layout_name}', 
                               ha='center', va='center', transform=ax.transAxes)
                        ax.axis('off')
                        logger.error(f"Failed to load layout image {image_path}: {e}")
            
            # 隐藏未使用的子图
            for idx in range(len(layout_files), len(axes)):
                axes[idx].axis('off')
            
            plt.suptitle('System Layout Analysis', fontsize=16)
            plt.tight_layout()
            
            if save_path:
                plt.savefig(save_path, dpi=300, bbox_inches='tight')
                logger.info(f"Layout comparison saved to: {save_path}")
            
            return fig
            
        except Exception as e:
            logger.error(f"Error creating layout comparison: {str(e)}")
            fig, ax = plt.subplots(figsize=(10, 6))
            ax.text(0.5, 0.5, f'Error creating layout comparison:\n{str(e)}', 
                   ha='center', va='center', transform=ax.transAxes, fontsize=12)
            ax.axis('off')
            return fig
    
    def get_available_presets(self, is_nsc: bool = False) -> List[str]:
        """
        获取可用的配置预设列表
        
        Args:
            is_nsc: 是否为NSC系统
            
        Returns:
            可用预设列表
        """
        return get_available_presets(is_nsc)
    
    def get_preset_info(self, preset_name: str, is_nsc: bool = False) -> Dict:
        """
        获取预设配置信息
        
        Args:
            preset_name: 预设名称
            is_nsc: 是否为NSC系统
            
        Returns:
            预设配置字典
        """
        return get_preset_config(preset_name, is_nsc)
    
    def print_available_presets(self, is_nsc: bool = False):
        """
        打印所有可用的预设信息
        
        Args:
            is_nsc: 是否为NSC系统
        """
        presets = self.get_available_presets(is_nsc)
        print(f"可用的Layout配置预设 ({'NSC' if is_nsc else 'Sequential'}系统):")
        print("=" * 50)
        
        for preset in presets:
            config = self.get_preset_info(preset, is_nsc)
            print(f"\n📋 {preset}:")
            
            if 'cross_section' in config:
                cs_config = config['cross_section']
                width = cs_config.get('output_pixel_width', 800)
                height = cs_config.get('output_pixel_height', 600)
                rays = cs_config.get('number_of_rays', 25)
                print(f"  • 截面图: {width}x{height}, {rays}条光线")
            
            layout_types = [lt for lt in config.keys() if lt != 'cross_section']
            if layout_types:
                print(f"  • 其他类型: {', '.join(layout_types)}")
        
        print("\n使用方法:")
        print(f"layout_analyzer.generate_all_layouts('./output', preset='预设名称', is_nsc={is_nsc})")
    
    def quick_export_with_preset(self, output_dir: str, preset: str = "standard", 
                                is_nsc: bool = False) -> Dict[str, str]:
        """
        使用预设快速导出所有Layout
        
        Args:
            output_dir: 输出目录
            preset: 预设名称
            is_nsc: 是否为NSC系统
            
        Returns:
            生成的文件路径字典
        """
        logger.info(f"开始使用预设 '{preset}' 快速导出Layout...")
        
        # 检查预设是否存在
        available_presets = self.get_available_presets(is_nsc)
        if preset not in available_presets:
            logger.warning(f"预设 '{preset}' 不存在，使用 'standard' 预设")
            logger.info(f"可用预设: {', '.join(available_presets)}")
            preset = "standard"
        
        # 生成layout
        return self.generate_all_layouts(output_dir, is_nsc, None, preset)


# # === 便捷函数 ===

# def generate_system_layouts_enhanced(zos_manager, output_dir: str = ".", 
#                                    is_nsc: bool = False,
#                                    layout_config: Optional[Dict] = None,
#                                    preset: str = "standard") -> Dict[str, str]:
#     """
#     增强版系统layout生成函数
    
#     Args:
#         zos_manager: ZOSAPI管理器
#         output_dir: 输出目录
#         is_nsc: 是否为NSC系统
#         layout_config: layout配置字典（会覆盖预设中的相应部分）
#         preset: 预设名称 ("draft", "standard", "high_quality", "publication")
        
#     Returns:
#         生成的文件路径字典
#     """
#     analyzer = ZOSLayoutAnalyzer(zos_manager)
#     return analyzer.generate_all_layouts(output_dir, is_nsc, layout_config, preset)


# def create_comprehensive_layout_analysis(zos_manager, output_dir: str = ".",
#                                         is_nsc: bool = False,
#                                         layout_config: Optional[Dict] = None,
#                                         preset: str = "standard") -> Dict[str, str]:
#     """
#     创建全面的layout分析，包括单独文件和对比图
    
#     Args:
#         zos_manager: ZOSAPI管理器
#         output_dir: 输出目录
#         is_nsc: 是否为NSC系统
#         layout_config: layout配置字典（会覆盖预设中的相应部分）
#         preset: 预设名称 ("draft", "standard", "high_quality", "publication")
        
#     Returns:
#         生成的文件路径字典
#     """
#     analyzer = ZOSLayoutAnalyzer(zos_manager)
    
#     # 生成所有layout文件
#     layout_files = analyzer.generate_all_layouts(output_dir, is_nsc, layout_config, preset)
    
#     # 创建对比图
#     if layout_files:
#         comparison_path = str(Path(output_dir) / "layout_comparison.png")
#         fig = analyzer.create_layout_comparison(layout_files, comparison_path)
#         plt.close(fig)
#         layout_files['comparison'] = comparison_path
    
#     return layout_files


# def quick_layout_export(zos_manager, output_dir: str = ".", 
#                        preset: str = "standard", is_nsc: bool = False) -> Dict[str, str]:
#     """
#     快速Layout导出 - 最简单的使用方式
    
#     Args:
#         zos_manager: ZOSAPI管理器
#         output_dir: 输出目录
#         preset: 预设名称
#         is_nsc: 是否为NSC系统
        
#     Returns:
#         生成的文件路径字典
#     """
#     analyzer = ZOSLayoutAnalyzer(zos_manager)
#     return analyzer.quick_export_with_preset(output_dir, preset, is_nsc)


# def print_layout_presets(is_nsc: bool = False):
#     """
#     打印所有可用的Layout预设信息
    
#     Args:
#         is_nsc: 是否为NSC系统
#     """
#     # 创建一个临时的分析器实例来访问预设信息
#     print(f"Layout配置预设信息 ({'NSC' if is_nsc else 'Sequential'}系统):")
#     print("=" * 60)
    
#     presets = get_available_presets(is_nsc)
    
#     for preset in presets:
#         config = get_preset_config(preset, is_nsc)
#         print(f"\n📋 {preset.upper()}:")
        
#         if 'cross_section' in config:
#             cs_config = config['cross_section']
#             width = cs_config.get('output_pixel_width', 800)
#             height = cs_config.get('output_pixel_height', 600)
#             rays = cs_config.get('number_of_rays', 25)
#             y_stretch = cs_config.get('y_stretch', 1.0)
#             color_by = cs_config.get('color_rays_by', 'None')
#             print(f"  📐 截面图: {width}×{height}px, {rays}条光线, Y拉伸:{y_stretch}")
#             if color_by != 'None':
#                 print(f"     颜色编码: {color_by}")
        
#         layout_types = [lt for lt in config.keys() if lt != 'cross_section']
#         if layout_types:
#             type_descriptions = [LAYOUT_TYPE_DESCRIPTIONS.get(lt, lt) for lt in layout_types]
#             print(f"  🎯 其他类型: {', '.join(type_descriptions)}")
    
#     print(f"\n💡 使用示例:")
#     print(f"   quick_layout_export(zos_manager, './output', preset='high_quality', is_nsc={is_nsc})")
#     print(f"   create_comprehensive_layout_analysis(zos_manager, './output', preset='publication')")


# # 向后兼容的别名
# generate_system_layouts = generate_system_layouts_enhanced
