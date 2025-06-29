"""
Zemax OpticStudio Python API Plotting Module
Provides plotting functions for various optical analysis results
Author: Your Name
Date: 2025-06-29
"""

import matplotlib.pyplot as plt
import numpy as np
from typing import Optional, Tuple, List, Dict, Any
import logging

logger = logging.getLogger(__name__)

# Setup plotting style - use English fonts
plt.rcParams['font.family'] = ['DejaVu Sans', 'Arial', 'sans-serif']
plt.rcParams['axes.unicode_minus'] = False


class ZOSPlotter:
    """Zemax data plotter"""
    
    def __init__(self, style: str = "default", figsize: Tuple[int, int] = (10, 8)):
        """
        Initialize plotter
        
        Args:
            style: matplotlib style
            figsize: Figure size
        """
        self.style = style
        self.figsize = figsize
        self.setup_style()
    
    def setup_style(self):
        """Setup plotting style"""
        plt.style.use(self.style)
        
        # Custom colors and styles
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
                         title: str = "Spot Diagram", figsize: Optional[Tuple[int, int]] = None,
                         save_path: Optional[str] = None) -> plt.Figure:
        """
        Plot spot diagram
        
        Args:
            x_coords: X coordinates list
            y_coords: Y coordinates list
            title: Plot title
            figsize: Figure size
            save_path: Save path
            
        Returns:
            matplotlib Figure object
        """
        if figsize is None:
            figsize = self.figsize
        
        fig, ax = plt.subplots(figsize=figsize)
        
        # Plot scatter diagram
        scatter = ax.scatter(x_coords, y_coords, alpha=0.6, s=1, c=self.colors['primary'])
        
        # Calculate RMS circle
        x_rms = np.sqrt(np.mean(np.array(x_coords)**2))
        y_rms = np.sqrt(np.mean(np.array(y_coords)**2))
        rms_radius = np.sqrt(x_rms**2 + y_rms**2)
        
        # Draw RMS circle
        circle = plt.Circle((0, 0), rms_radius, fill=False, color=self.colors['danger'], 
                           linestyle='--', label=f'RMS Radius: {rms_radius:.3f}')
        ax.add_patch(circle)
        
        # Set equal aspect ratio
        ax.set_aspect('equal')
        ax.grid(True, alpha=0.3)
        ax.set_xlabel('X (mm)')
        ax.set_ylabel('Y (mm)')
        ax.set_title(title)
        ax.legend()
        
        # Add statistics information
        stats_text = f'Rays: {len(x_coords)}\nRMS Radius: {rms_radius:.6f} mm'
        ax.text(0.02, 0.98, stats_text, transform=ax.transAxes, 
                verticalalignment='top', bbox=dict(boxstyle='round', facecolor='wheat', alpha=0.8))
        
        plt.tight_layout()
        
        if save_path:
            plt.savefig(save_path, dpi=300, bbox_inches='tight')
            logger.info(f"Spot diagram saved to: {save_path}")
        
        return fig
    
    def plot_wavefront(self, wavefront: np.ndarray, x_coords: np.ndarray, y_coords: np.ndarray,
                      mask: Optional[np.ndarray] = None, title: str = "Wavefront Map",
                      colorbar_label: str = "Wavefront Error (waves)", 
                      figsize: Optional[Tuple[int, int]] = None,
                      save_path: Optional[str] = None) -> plt.Figure:
        """
        Plot wavefront map
        
        Args:
            wavefront: Wavefront data
            x_coords: X coordinate grid
            y_coords: Y coordinate grid
            mask: Mask array
            title: Plot title
            colorbar_label: Colorbar label
            figsize: Figure size
            save_path: Save path
            
        Returns:
            matplotlib Figure object
        """
        if figsize is None:
            figsize = self.figsize
        
        fig, ax = plt.subplots(figsize=figsize)
        
        # Apply mask
        if mask is not None:
            plot_data = np.where(mask, wavefront, np.nan)
        else:
            plot_data = wavefront
        
        # Plot wavefront
        im = ax.contourf(x_coords, y_coords, plot_data, levels=50, cmap='RdYlBu_r')
        
        # Add contour lines
        contours = ax.contour(x_coords, y_coords, plot_data, levels=10, colors='black', alpha=0.3, linewidths=0.5)
        
        # Add colorbar
        cbar = plt.colorbar(im, ax=ax, label=colorbar_label)
        
        # Set axes
        ax.set_aspect('equal')
        ax.set_xlabel('Normalized Pupil X')
        ax.set_ylabel('Normalized Pupil Y')
        ax.set_title(title)
        
        # Add statistics information
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
            logger.info(f"Wavefront map saved to: {save_path}")
        
        return fig
    
    def plot_mtf_curve(self, frequencies: List[float], mtf_values: List[float],
                      title: str = "MTF Curve", label: str = "MTF",
                      figsize: Optional[Tuple[int, int]] = None,
                      save_path: Optional[str] = None) -> plt.Figure:
        """
        Plot MTF curve
        
        Args:
            frequencies: Frequency list
            mtf_values: MTF values list
            title: Plot title
            label: Curve label
            figsize: Figure size
            save_path: Save path
            
        Returns:
            matplotlib Figure object
        """
        if figsize is None:
            figsize = self.figsize
        
        fig, ax = plt.subplots(figsize=figsize)
        
        # Plot MTF curve
        ax.plot(frequencies, mtf_values, color=self.colors['primary'], 
                linewidth=2, marker='o', markersize=3, label=label)
        
        # Set axes
        ax.set_xlabel('Spatial Frequency (cycles/mm)')
        ax.set_ylabel('MTF')
        ax.set_title(title)
        ax.grid(True, alpha=0.3)
        ax.legend()
        
        # Set Y-axis range
        ax.set_ylim(0, 1.1)
        
        plt.tight_layout()
        
        if save_path:
            plt.savefig(save_path, dpi=300, bbox_inches='tight')
            logger.info(f"MTF curve saved to: {save_path}")
        
        return fig
    
    def plot_ray_fan(self, field_angles: List[float], ray_errors: List[float],
                    title: str = "Ray Fan", ylabel: str = "Ray Error",
                    figsize: Optional[Tuple[int, int]] = None,
                    save_path: Optional[str] = None) -> plt.Figure:
        """
        Plot ray fan diagram
        
        Args:
            field_angles: Field angle list
            ray_errors: Ray error list
            title: Plot title
            ylabel: Y-axis label
            figsize: Figure size
            save_path: Save path
            
        Returns:
            matplotlib Figure object
        """
        if figsize is None:
            figsize = self.figsize
        
        fig, ax = plt.subplots(figsize=figsize)
        
        # Plot ray fan diagram
        ax.plot(field_angles, ray_errors, color=self.colors['primary'], 
                linewidth=2, marker='o', markersize=3)
        
        # Set axes
        ax.set_xlabel('Field Angle (degrees)')
        ax.set_ylabel(ylabel)
        ax.set_title(title)
        ax.grid(True, alpha=0.3)
        
        # Add zero line
        ax.axhline(y=0, color='black', linestyle='-', alpha=0.5)
        
        plt.tight_layout()
        
        if save_path:
            plt.savefig(save_path, dpi=300, bbox_inches='tight')
            logger.info(f"Ray fan diagram saved to: {save_path}")
        
        return fig
    
    def plot_field_curvature(self, field_positions: List[float], 
                           sagittal_focus: List[float], tangential_focus: List[float],
                           title: str = "Field Curvature", figsize: Optional[Tuple[int, int]] = None,
                           save_path: Optional[str] = None) -> plt.Figure:
        """
        Plot field curvature
        
        Args:
            field_positions: Field positions
            sagittal_focus: Sagittal focus positions
            tangential_focus: Tangential focus positions
            title: Plot title
            figsize: Figure size
            save_path: Save path
            
        Returns:
            matplotlib Figure object
        """
        if figsize is None:
            figsize = self.figsize
        
        fig, ax = plt.subplots(figsize=figsize)
        
        # Plot field curvature
        ax.plot(sagittal_focus, field_positions, color=self.colors['primary'], 
                linewidth=2, marker='o', markersize=4, label='Sagittal')
        ax.plot(tangential_focus, field_positions, color=self.colors['secondary'], 
                linewidth=2, marker='s', markersize=4, label='Tangential')
        
        # Set axes
        ax.set_xlabel('Focus Position Shift (mm)')
        ax.set_ylabel('Field Height')
        ax.set_title(title)
        ax.grid(True, alpha=0.3)
        ax.legend()
        
        # Add zero line
        ax.axvline(x=0, color='black', linestyle='-', alpha=0.5)
        
        plt.tight_layout()
        
        if save_path:
            plt.savefig(save_path, dpi=300, bbox_inches='tight')
            logger.info(f"Field curvature plot saved to: {save_path}")
        
        return fig
    
    def plot_distortion(self, field_positions: List[float], distortion_values: List[float],
                       title: str = "Distortion", figsize: Optional[Tuple[int, int]] = None,
                       save_path: Optional[str] = None) -> plt.Figure:
        """
        Plot distortion diagram
        
        Args:
            field_positions: Field positions
            distortion_values: Distortion values
            title: Plot title
            figsize: Figure size
            save_path: Save path
            
        Returns:
            matplotlib Figure object
        """
        if figsize is None:
            figsize = self.figsize
        
        fig, ax = plt.subplots(figsize=figsize)
        
        # Plot distortion
        ax.plot(field_positions, distortion_values, color=self.colors['primary'], 
                linewidth=2, marker='o', markersize=4)
        
        # Set axes
        ax.set_xlabel('Field Position')
        ax.set_ylabel('Distortion (%)')
        ax.set_title(title)
        ax.grid(True, alpha=0.3)
        
        # Add zero line
        ax.axhline(y=0, color='black', linestyle='-', alpha=0.5)
        
        plt.tight_layout()
        
        if save_path:
            plt.savefig(save_path, dpi=300, bbox_inches='tight')
            logger.info(f"Distortion plot saved to: {save_path}")
        
        return fig
    
    def plot_multiple_curves(self, x_data: List[float], y_data_list: List[List[float]],
                           labels: List[str], title: str = "Multiple Curves",
                           xlabel: str = "X", ylabel: str = "Y",
                           figsize: Optional[Tuple[int, int]] = None,
                           save_path: Optional[str] = None) -> plt.Figure:
        """
        Plot multiple curves
        
        Args:
            x_data: X data
            y_data_list: Y data list
            labels: Curve labels list
            title: Plot title
            xlabel: X-axis label
            ylabel: Y-axis label
            figsize: Figure size
            save_path: Save path
            
        Returns:
            matplotlib Figure object
        """
        if figsize is None:
            figsize = self.figsize
        
        fig, ax = plt.subplots(figsize=figsize)
        
        # Plot multiple curves
        colors = list(self.colors.values())
        for i, (y_data, label) in enumerate(zip(y_data_list, labels)):
            color = colors[i % len(colors)]
            line_style = self.line_styles[i % len(self.line_styles)]
            marker = self.markers[i % len(self.markers)]
            
            ax.plot(x_data, y_data, color=color, linewidth=2, 
                   linestyle=line_style, marker=marker, markersize=4, label=label)
        
        # Set axes
        ax.set_xlabel(xlabel)
        ax.set_ylabel(ylabel)
        ax.set_title(title)
        ax.grid(True, alpha=0.3)
        ax.legend()
        
        plt.tight_layout()
        
        if save_path:
            plt.savefig(save_path, dpi=300, bbox_inches='tight')
            logger.info(f"Multiple curves plot saved to: {save_path}")
        
        return fig
    
    def create_subplot_layout(self, nrows: int, ncols: int, 
                            figsize: Optional[Tuple[int, int]] = None) -> Tuple[plt.Figure, np.ndarray]:
        """
        Create subplot layout
        
        Args:
            nrows: Number of rows
            ncols: Number of columns
            figsize: Figure size
            
        Returns:
            Figure and Axes array
        """
        if figsize is None:
            figsize = (ncols * 5, nrows * 4)
        
        fig, axes = plt.subplots(nrows, ncols, figsize=figsize)
        
        # Ensure axes is an array
        if nrows == 1 and ncols == 1:
            axes = np.array([axes])
        elif nrows == 1 or ncols == 1:
            axes = axes.reshape(-1)
        
        return fig, axes


# === Convenient plotting functions ===

def quick_spot_plot(x_coords: List[float], y_coords: List[float], 
                   title: str = "Spot Diagram", save_path: Optional[str] = None) -> plt.Figure:
    """Quick spot diagram plot"""
    plotter = ZOSPlotter()
    return plotter.plot_spot_diagram(x_coords, y_coords, title=title, save_path=save_path)


def quick_wavefront_plot(wavefront: np.ndarray, title: str = "Wavefront Map", 
                        save_path: Optional[str] = None) -> plt.Figure:
    """Quick wavefront plot"""
    plotter = ZOSPlotter()
    h, w = wavefront.shape
    x = np.linspace(-1, 1, w)
    y = np.linspace(-1, 1, h)
    xx, yy = np.meshgrid(x, y)
    return plotter.plot_wavefront(wavefront, xx, yy, title=title, save_path=save_path)


def quick_mtf_plot(frequencies: List[float], mtf_values: List[float], 
                  title: str = "MTF Curve", save_path: Optional[str] = None) -> plt.Figure:
    """Quick MTF curve plot"""
    plotter = ZOSPlotter()
    return plotter.plot_mtf_curve(frequencies, mtf_values, title=title, save_path=save_path)

# === Advanced Multi-Field Multi-Wavelength Plotting Functions ===

def plot_multifield_spots(zos_manager, analyzer, save_path: Optional[str] = None) -> plt.Figure:
    """
    Plot spot diagrams for all fields and wavelengths
    
    Args:
        zos_manager: ZOSAPI manager instance
        analyzer: ZOSAnalyzer instance
        save_path: Path to save the plot
        
    Returns:
        Figure object
    """
    system = zos_manager.TheSystem
    num_fields = system.SystemData.Fields.NumberOfFields
    num_wavelengths = system.SystemData.Wavelengths.NumberOfWavelengths
    
    # Calculate subplot layout
    import math
    n_cols = min(3, num_fields)
    n_rows = math.ceil(num_fields / n_cols)
    
    fig, axes = plt.subplots(n_rows, n_cols, figsize=(4*n_cols, 4*n_rows))
    
    # Handle axes to ensure it's always a list
    if num_fields == 1:
        axes = [axes]
    elif n_rows == 1 and n_cols > 1:
        axes = list(axes)
    elif n_rows > 1 and n_cols == 1:
        axes = list(axes)
    else:
        axes = axes.flatten()
    
    # Plot for each field
    colors = ['b', 'g', 'r', 'c', 'm', 'y', 'k']
    for field_idx in range(num_fields):
        ax = axes[field_idx]
        
        # Get field information
        field = system.SystemData.Fields.GetField(field_idx + 1)
        field_y = field.Y
        
        # Plot each wavelength
        for wave_idx in range(min(num_wavelengths, len(colors))):
            spot_data = analyzer.analyze_spot_diagram(
                field_index=field_idx, 
                wavelength_index=wave_idx, 
                ray_density=3
            )
            
            ax.scatter(spot_data['x_coords'], spot_data['y_coords'], 
                      c=colors[wave_idx], alpha=0.6, s=1, 
                      label=f'λ{wave_idx+1}' if num_wavelengths > 1 else '')
        
        ax.set_title(f'Field {field_idx+1}: Y={field_y:.2f}')
        ax.set_xlabel('X (mm)')
        ax.set_ylabel('Y (mm)')
        ax.set_aspect('equal')
        ax.grid(True, alpha=0.3)
        if num_wavelengths > 1:
            ax.legend()
    
    # Hide extra subplots
    if len(axes) > num_fields:
        for i in range(num_fields, len(axes)):
            axes[i].set_visible(False)
    
    plt.suptitle('Spot Diagrams - All Fields', fontsize=14)
    plt.tight_layout()
    
    if save_path:
        plt.savefig(save_path, dpi=300, bbox_inches='tight')
        logger.info(f"Multi-field spot diagrams saved to: {save_path}")
    
    return fig


def plot_multifield_rayfan(zos_manager, analyzer, save_path: Optional[str] = None) -> plt.Figure:
    """
    Plot ray fan diagrams for all fields
    
    Args:
        zos_manager: ZOSAPI manager instance
        analyzer: ZOSAnalyzer instance
        save_path: Path to save the plot
        
    Returns:
        Figure object
    """
    system = zos_manager.TheSystem
    num_fields = system.SystemData.Fields.NumberOfFields
    
    if num_fields == 1:
        fig, axes = plt.subplots(2, 1, figsize=(8, 10))
        axes = axes.reshape(2, 1)
    else:
        fig, axes = plt.subplots(2, num_fields, figsize=(4*num_fields, 8))
        if axes.ndim == 1:
            axes = axes.reshape(2, 1)
    
    # Plot for each field
    for field_idx in range(num_fields):
        # Get field information
        field = system.SystemData.Fields.GetField(field_idx + 1)
        
        # X fan
        ax_x = axes[0, field_idx] if num_fields > 1 else axes[0, 0]
        ray_fan_x = analyzer.analyze_ray_fan(
            field_index=field_idx, 
            wavelength_index=0, 
            fan_type="X", 
            num_rays=21
        )
        
        ax_x.plot(ray_fan_x['pupil_coords'], ray_fan_x['ray_errors'], 
                 'b-', linewidth=2, marker='o', markersize=2)
        ax_x.set_title(f'Field {field_idx+1} (Y={field.Y:.1f}) - X Fan')
        ax_x.set_xlabel('Pupil Coordinate')
        ax_x.set_ylabel('Ray Error (mm)')
        ax_x.grid(True, alpha=0.3)
        ax_x.axhline(y=0, color='black', linestyle='-', alpha=0.5)
        
        # Y fan
        ax_y = axes[1, field_idx] if num_fields > 1 else axes[1, 0]
        ray_fan_y = analyzer.analyze_ray_fan(
            field_index=field_idx, 
            wavelength_index=0, 
            fan_type="Y", 
            num_rays=21
        )
        
        ax_y.plot(ray_fan_y['pupil_coords'], ray_fan_y['ray_errors'], 
                 'r-', linewidth=2, marker='o', markersize=2)
        ax_y.set_title(f'Field {field_idx+1} (Y={field.Y:.1f}) - Y Fan')
        ax_y.set_xlabel('Pupil Coordinate')
        ax_y.set_ylabel('Ray Error (mm)')
        ax_y.grid(True, alpha=0.3)
        ax_y.axhline(y=0, color='black', linestyle='-', alpha=0.5)
    
    plt.suptitle('Ray Fan Analysis - All Fields', fontsize=14)
    plt.tight_layout()
    
    if save_path:
        plt.savefig(save_path, dpi=300, bbox_inches='tight')
        logger.info(f"Multi-field ray fan plots saved to: {save_path}")
    
    return fig


def plot_system_mtf(zos_manager, save_path: Optional[str] = None) -> plt.Figure:
    """
    Plot MTF for all fields and wavelengths using Zemax built-in analysis
    
    Args:
        zos_manager: ZOSAPI manager instance
        save_path: Path to save the plot
        
    Returns:
        Figure object
    """
    from zosapi_utils import reshape_zos_data
    
    system = zos_manager.TheSystem
    
    # Create FFT MTF analysis (following Official Example 4)
    mtf_analysis = system.Analyses.New_FftMtf()
    mtf_settings = mtf_analysis.GetSettings()
    mtf_settings.MaximumFrequency = 100
    mtf_settings.SampleSize = zos_manager.ZOSAPI.Analysis.SampleSizes.S_256x256
    
    # Run analysis
    mtf_analysis.ApplyAndWaitForCompletion()
    mtf_results = mtf_analysis.GetResults()
    
    # Plot MTF curves
    plt.figure(figsize=(12, 8))
    colors = ('b','g','r','c', 'm', 'y', 'k')
    legend_labels = []
    
    for seriesNum in range(0, mtf_results.NumberOfDataSeries):
        data = mtf_results.GetDataSeries(seriesNum)
        
        # Get data
        xRaw = data.XData.Data
        yRaw = data.YData.Data
        
        x = list(xRaw)
        y = reshape_zos_data(yRaw, yRaw.GetLength(0), yRaw.GetLength(1), True)
        
        # Plot tangential and sagittal MTF
        color = colors[seriesNum % len(colors)]
        plt.plot(x, y[0], color=color, linewidth=2, linestyle='-')
        plt.plot(x, y[1], color=color, linewidth=2, linestyle='--')
        
        legend_labels.extend([f'Series {seriesNum+1} Tangential', f'Series {seriesNum+1} Sagittal'])
    
    plt.title('MTF Analysis - All Fields and Wavelengths')
    plt.xlabel('Spatial Frequency (cycles/mm)')
    plt.ylabel('MTF')
    plt.grid(True, alpha=0.3)
    plt.legend(legend_labels[:min(len(legend_labels), 10)])  # Limit legend entries
    plt.ylim(0, 1.1)
    plt.tight_layout()
    
    if save_path:
        plt.savefig(save_path, dpi=300, bbox_inches='tight')
        logger.info(f"System MTF plot saved to: {save_path}")
    
    # Close analysis
    mtf_analysis.Close()
    
    return plt.gcf()


def plot_comprehensive_analysis(zos_manager, analyzer, save_path: Optional[str] = None) -> plt.Figure:
    """
    Create a comprehensive analysis plot with MTF, spot diagrams, and ray fans
    
    Args:
        zos_manager: ZOSAPI manager instance
        analyzer: ZOSAnalyzer instance
        save_path: Path to save the plot
        
    Returns:
        Figure object
    """
    from zosapi_utils import reshape_zos_data
    
    system = zos_manager.TheSystem
    num_fields = system.SystemData.Fields.NumberOfFields
    
    fig = plt.figure(figsize=(16, 12))
    
    # MTF subplot (top section)
    ax1 = plt.subplot2grid((3, 3), (0, 0), colspan=3)
    
    # Create MTF analysis
    mtf_analysis = system.Analyses.New_FftMtf()
    mtf_settings = mtf_analysis.GetSettings()
    mtf_settings.MaximumFrequency = 50
    mtf_analysis.ApplyAndWaitForCompletion()
    mtf_results = mtf_analysis.GetResults()
    
    colors = ('b','g','r','c', 'm', 'y', 'k')
    for seriesNum in range(0, min(mtf_results.NumberOfDataSeries, len(colors))):
        data = mtf_results.GetDataSeries(seriesNum)
        xRaw = data.XData.Data
        yRaw = data.YData.Data
        x = list(xRaw)
        y = reshape_zos_data(yRaw, yRaw.GetLength(0), yRaw.GetLength(1), True)
        
        ax1.plot(x, y[0], color=colors[seriesNum], linewidth=2, label=f'Field {seriesNum+1} T')
        ax1.plot(x, y[1], linestyle='--', color=colors[seriesNum], linewidth=2, label=f'Field {seriesNum+1} S')
    
    ax1.set_title('MTF - All Fields')
    ax1.set_xlabel('Spatial Frequency (cycles/mm)')
    ax1.set_ylabel('MTF')
    ax1.grid(True, alpha=0.3)
    ax1.legend(bbox_to_anchor=(1.05, 1), loc='upper left')
    
    mtf_analysis.Close()
    
    # Spot diagram subplots
    for field_idx in range(min(3, num_fields)):
        ax = plt.subplot2grid((3, 3), (1, field_idx))
        
        spot_data = analyzer.analyze_spot_diagram(field_index=field_idx, wavelength_index=0, ray_density=3)
        ax.scatter(spot_data['x_coords'], spot_data['y_coords'], alpha=0.6, s=1, c='blue')
        
        field = system.SystemData.Fields.GetField(field_idx + 1)
        ax.set_title(f'Spot F{field_idx+1}: Y={field.Y:.2f}')
        ax.set_xlabel('X (mm)')
        ax.set_ylabel('Y (mm)')
        ax.set_aspect('equal')
        ax.grid(True, alpha=0.3)
    
    # Ray fan subplots
    for field_idx in range(min(3, num_fields)):
        ax = plt.subplot2grid((3, 3), (2, field_idx))
        
        ray_fan_data = analyzer.analyze_ray_fan(field_index=field_idx, wavelength_index=0, fan_type="Y", num_rays=21)
        ax.plot(ray_fan_data['pupil_coords'], ray_fan_data['ray_errors'], 'g-', linewidth=2, marker='o', markersize=2)
        
        ax.set_title(f'Ray Fan F{field_idx+1}')
        ax.set_xlabel('Pupil Coordinate')
        ax.set_ylabel('Ray Error (mm)')
        ax.grid(True, alpha=0.3)
        ax.axhline(y=0, color='black', linestyle='-', alpha=0.5)
    
    plt.suptitle('Comprehensive Optical Analysis', fontsize=16)
    plt.tight_layout()
    
    if save_path:
        plt.savefig(save_path, dpi=300, bbox_inches='tight')
        logger.info(f"Comprehensive analysis plot saved to: {save_path}")
    
    return fig


# === Super convenient one-liner functions ===

def analyze_and_plot_system(zos_manager, output_dir: str = ".") -> Dict[str, str]:
    """
    One-liner function to analyze and plot everything for a loaded system
    
    Args:
        zos_manager: ZOSAPI manager instance
        output_dir: Directory to save plots
        
    Returns:
        Dictionary with saved file paths
    """
    from pathlib import Path
    from zosapi_analysis import ZOSAnalyzer
    
    output_path = Path(output_dir)
    analyzer = ZOSAnalyzer(zos_manager)
    
    saved_files = {}
    
    # Plot all analysis types
    try:
        # MTF
        fig = plot_system_mtf(zos_manager, str(output_path / "system_mtf.png"))
        plt.close()
        saved_files['mtf'] = str(output_path / "system_mtf.png")
        
        # Spot diagrams
        fig = plot_multifield_spots(zos_manager, analyzer, str(output_path / "multifield_spots.png"))
        plt.close()
        saved_files['spots'] = str(output_path / "multifield_spots.png")
        
        # Ray fans
        fig = plot_multifield_rayfan(zos_manager, analyzer, str(output_path / "multifield_rayfan.png"))
        plt.close()
        saved_files['rayfan'] = str(output_path / "multifield_rayfan.png")
        
        # Comprehensive
        fig = plot_comprehensive_analysis(zos_manager, analyzer, str(output_path / "comprehensive_analysis.png"))
        plt.close()
        saved_files['comprehensive'] = str(output_path / "comprehensive_analysis.png")
        
        logger.info(f"All analysis plots saved to: {output_dir}")
        
    except Exception as e:
        logger.error(f"Error in analyze_and_plot_system: {e}")
    
    return saved_files
