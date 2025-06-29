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
