"""
정렬 알고리즘 시각화 프로그램
Sorting Algorithm Visualizer

기본 정렬: 버블, 선택, 삽입 정렬
고급 정렬: 퀵, 병합, 힙 정렬
"""
import tkinter as tk
from tkinter import ttk, messagebox
import random

from core.controls import ControlPanel, generate_random_data
from visualizers.bar_visualizer import BarVisualizer

# Constants
DEFAULT_DATA_SIZE = 15
QUICK_SORT_MAX_SIZE = 8
MERGE_SORT_MAX_SIZE = 8
HEAP_SORT_MAX_SIZE = 10

# Mode configurations
MODE_CONFIGS = {
    'basic': {
        'title': '기본 정렬 알고리즘',
        'visualizer_class': BarVisualizer,
        'max_size': None,  # No limit
        'has_algorithm_selection': True,
        'module': None
    },
    'quick': {
        'title': '퀵 정렬 (Quick Sort)',
        'visualizer_class': 'QuickSortVisualizer',
        'max_size': QUICK_SORT_MAX_SIZE,
        'has_algorithm_selection': False,
        'module': 'visualizers.quick_visualizer'
    },
    'merge': {
        'title': '병합 정렬 (Merge Sort)',
        'visualizer_class': 'MergeSortVisualizer',
        'max_size': MERGE_SORT_MAX_SIZE,
        'has_algorithm_selection': False,
        'module': 'visualizers.merge_visualizer'
    },
    'heap': {
        'title': '힙 정렬 (Heap Sort)',
        'visualizer_class': 'HeapSortVisualizer',
        'max_size': HEAP_SORT_MAX_SIZE,
        'has_algorithm_selection': False,
        'module': 'visualizers.heap_visualizer'
    }
}


class SortingVisualizerApp:
    """Main application for sorting algorithm visualization."""
    
    def __init__(self, root: tk.Tk):
        """Initialize the application."""
        self.root = root
        self.root.title("정렬 알고리즘 시각화")
        self.root.geometry("1200x700")
        self.root.configure(bg='#2C3E50')
        
        # Current visualizer mode
        self.current_mode = None
        self.visualizer = None
        self.data = generate_random_data(DEFAULT_DATA_SIZE)
        
        self._create_menu()
        self._create_main_frame()
        self._create_status_bar()
        
        # Initialize with basic sort visualizer
        self._switch_to_mode('basic')
        
    def _create_menu(self):
        """Create the menu bar."""
        menubar = tk.Menu(self.root)
        self.root.config(menu=menubar)
        
        # Algorithm menu
        algo_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="알고리즘", menu=algo_menu)
        
        algo_menu.add_command(label="기본 정렬 (버블, 선택, 삽입)", 
                             command=lambda: self._switch_to_mode('basic'))
        algo_menu.add_separator()
        algo_menu.add_command(label="퀵 정렬", command=lambda: self._switch_to_mode('quick'))
        algo_menu.add_command(label="병합 정렬", command=lambda: self._switch_to_mode('merge'))
        algo_menu.add_command(label="힙 정렬", command=lambda: self._switch_to_mode('heap'))
        
        # Help menu
        help_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="도움말", menu=help_menu)
        help_menu.add_command(label="사용법", command=self._show_help)
        help_menu.add_command(label="정보", command=self._show_about)
        
    def _create_main_frame(self):
        """Create the main content frame."""
        self.main_frame = tk.Frame(self.root, bg='#2C3E50')
        self.main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Title label
        self.title_label = tk.Label(
            self.main_frame,
            text="기본 정렬 알고리즘",
            font=('맑은 고딕', 18, 'bold'),
            bg='#2C3E50', fg='#ECF0F1'
        )
        self.title_label.pack(pady=(0, 10))
        
        # Canvas frame
        self.canvas_frame = tk.Frame(self.main_frame, bg='#34495E', bd=2, relief=tk.SUNKEN)
        self.canvas_frame.pack(fill=tk.BOTH, expand=True)
        
        # Canvas for visualization
        self.canvas = tk.Canvas(
            self.canvas_frame,
            bg='#2C3E50',
            highlightthickness=0
        )
        self.canvas.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # Control panel placeholder
        self.control_frame = tk.Frame(self.main_frame, bg='#2C3E50')
        self.control_frame.pack(fill=tk.X, pady=(10, 0))
        
    def _create_status_bar(self):
        """Create status bar at the bottom."""
        self.status_bar = tk.Label(
            self.root,
            text="준비됨 | 데이터 크기: 15",
            font=('맑은 고딕', 10),
            bg='#1A252F', fg='#BDC3C7',
            anchor=tk.W, padx=10, pady=5
        )
        self.status_bar.pack(fill=tk.X, side=tk.BOTTOM)
        
    def _update_status(self, message: str):
        """Update status bar message."""
        self.status_bar.config(text=message)
        
    def _switch_to_mode(self, mode: str):
        """Switch to a specific sorting visualization mode."""
        if mode not in MODE_CONFIGS:
            return
            
        self._stop_current()
        self.current_mode = mode
        config = MODE_CONFIGS[mode]
        
        self.title_label.config(text=config['title'])
        
        # Clear control frame
        for widget in self.control_frame.winfo_children():
            widget.destroy()
            
        try:
            # Import visualizer class if needed
            if config['module']:
                module = __import__(config['module'], fromlist=[config['visualizer_class']])
                visualizer_class = getattr(module, config['visualizer_class'])
            else:
                visualizer_class = config['visualizer_class']
            
            # Create control panel
            self.controls = ControlPanel(
                self.control_frame,
                on_start=self._start_sort,
                on_stop=self._stop_sort,
                on_reset=self._reset_sort,
                on_step=self._step_sort,
                on_speed_change=self._change_speed,
                on_generate=self._generate_data,
                on_algorithm_change=self._change_algorithm if config['has_algorithm_selection'] else None
            )
            
            # Prepare data
            max_size = config['max_size']
            data_to_use = self.data[:max_size] if max_size else self.data
            
            # Create visualizer
            self.visualizer = visualizer_class(self.canvas, data_to_use)
            self.visualizer.on_complete = self._on_sort_complete
            self.visualizer.draw()
            
            self._update_status(f"{config['title']} | 데이터 크기: {len(data_to_use)}")
            
        except ImportError:
            self._show_not_implemented(config['title'])
            
    def _show_not_implemented(self, name: str):
        """Show placeholder for not yet implemented visualizers."""
        self.canvas.delete("all")
        self.canvas.create_text(
            self.canvas.winfo_width() // 2 or 400,
            self.canvas.winfo_height() // 2 or 250,
            text=f"{name} 시각화\n(구현 예정)",
            font=('맑은 고딕', 24, 'bold'),
            fill='#7F8C8D',
            justify=tk.CENTER
        )
        self._update_status(f"{name} - 아직 구현되지 않았습니다")
        
    def _stop_current(self):
        """Stop current visualizer if running."""
        if self.visualizer:
            self.visualizer.stop()
        
    def _switch_to_heap(self):
        """Switch to heap sort visualization."""
        self._stop_current()
        self.current_mode = 'heap'
        self.title_label.config(text="힙 정렬 (Heap Sort)")
        
        # Clear control frame
        for widget in self.control_frame.winfo_children():
            widget.destroy()
            
        try:
            from visualizers.heap_visualizer import HeapSortVisualizer
            
            self.controls = ControlPanel(
                self.control_frame,
                on_start=self._start_sort,
                on_stop=self._stop_sort,
                on_reset=self._reset_sort,
                on_step=self._step_sort,
                on_speed_change=self._change_speed,
                on_generate=self._generate_data
            )
            
            self.visualizer = HeapSortVisualizer(self.canvas, self.data[:10])  # Limit for visibility
            self.visualizer.on_complete = self._on_sort_complete
            self.visualizer.draw()
        except ImportError:
            self._show_not_implemented("힙 정렬 (Heap Sort)")
            
    def _show_not_implemented(self, name: str):
        """Show placeholder for not yet implemented visualizers."""
        self.canvas.delete("all")
        self.canvas.create_text(
            self.canvas.winfo_width() // 2 or 400,
            self.canvas.winfo_height() // 2 or 250,
            text=f"{name} 시각화\n(구현 예정)",
            font=('맑은 고딕', 24, 'bold'),
            fill='#7F8C8D',
            justify=tk.CENTER
        )
        self._update_status(f"{name} - 아직 구현되지 않았습니다")
        
    def _stop_current(self):
        """Stop current visualizer if running."""
        if self.visualizer:
            self.visualizer.stop()
            
    def _start_sort(self):
        """Start or resume the sorting visualization."""
        if self.visualizer:
            self.visualizer.set_step_mode(self.controls.get_step_mode())
            self.controls.set_running_state(True)
            
            # Check if we can resume from paused state
            if self.visualizer.can_resume():
                self.visualizer.is_paused = False
                self.visualizer.is_running = True
                self._resume_visualization()
                self._update_status(f"재개됨: {MODE_CONFIGS[self.current_mode]['title']}")
            else:
                # Start fresh
                config = MODE_CONFIGS[self.current_mode]
                if config['has_algorithm_selection']:
                    algorithm = self.controls.algorithm_var.get()
                    self.visualizer.sort(algorithm)
                    algo_name = BarVisualizer.ALGORITHM_NAMES.get(algorithm, algorithm)
                    self._update_status(f"실행 중: {algo_name}")
                else:
                    self.visualizer.sort()
                    self._update_status(f"실행 중: {config['title']}")
                    
    def _resume_visualization(self):
        """Resume visualization from paused state."""
        if self.visualizer and self.visualizer._current_generator:
            self.visualizer._run_visualization(self.visualizer._current_generator)
                
    def _stop_sort(self):
        """Pause the sorting visualization (can be resumed)."""
        if self.visualizer:
            self.visualizer.stop()
            self.controls.set_running_state(False)
            self._update_status("일시정지됨 (시작 버튼으로 재개)")
            
    def _reset_sort(self):
        """Reset the visualization."""
        if self.visualizer:
            self.visualizer.reset()
            self.controls.set_running_state(False)
            self._update_status(f"리셋됨 | 데이터 크기: {len(self.visualizer.data)}")
            
    def _step_sort(self):
        """Execute one step in step mode."""
        if self.visualizer:
            self.visualizer.step()
            
    def _change_speed(self, speed: int):
        """Change animation speed."""
        if self.visualizer:
            self.visualizer.set_delay(speed)
            
    def _generate_data(self, size: int):
        """Generate new random data."""
        self.data = generate_random_data(size)
        
        if self.visualizer:
            # Limit data size for advanced visualizers
            config = MODE_CONFIGS[self.current_mode]
            max_size = config['max_size']
            data_to_use = self.data[:max_size] if max_size else self.data
                
            self.visualizer.reset(data_to_use)
            self._update_status(f"새 데이터 생성됨 | 크기: {len(data_to_use)}")
            
    def _change_algorithm(self, algorithm: str):
        """Change the sorting algorithm (basic mode only)."""
        if self.visualizer and self.current_mode == 'basic':
            algo_name = BarVisualizer.ALGORITHM_NAMES.get(algorithm, algorithm)
            self._update_status(f"알고리즘 변경: {algo_name}")
            
    def _on_sort_complete(self):
        """Called when sorting is complete."""
        self.controls.set_running_state(False)
        self._update_status("정렬 완료!")
        
    def _show_help(self):
        """Show help dialog."""
        help_text = """정렬 알고리즘 시각화 사용법

【기본 조작】
▶ 시작: 정렬 시작
⏹ 정지: 정렬 중지
↺ 리셋: 원래 데이터로 복원
→ 스텝: 한 단계씩 진행 (스텝 모드)

【속도 조절】
슬라이더로 애니메이션 속도 조절
(10ms: 빠름, 1000ms: 느림)

【데이터 생성】
크기를 지정하고 '랜덤 생성' 클릭

【알고리즘 선택】
메뉴 > 알고리즘에서 선택
기본 정렬: 버블, 선택, 삽입
고급 정렬: 퀵, 병합, 힙
"""
        messagebox.showinfo("사용법", help_text)
        
    def _show_about(self):
        """Show about dialog."""
        about_text = """정렬 알고리즘 시각화 프로그램

버전: 1.0
Python tkinter 기반

정렬 알고리즘의 동작 원리를
시각적으로 이해할 수 있도록
제작된 교육용 프로그램입니다.
"""
        messagebox.showinfo("정보", about_text)


def main():
    """Main entry point."""
    root = tk.Tk()
    app = SortingVisualizerApp(root)
    root.mainloop()


if __name__ == "__main__":
    main()

