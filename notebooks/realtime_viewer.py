# realtime_viewer.py — 独立运行的实时 BCI 可视化脚本
# 用法: python realtime_viewer.py
"""
实时 BCI 信号可视化
使用 pyqtgraph 实现高性能实时渲染

依赖: uv add pyqtgraph pyside6 brainflow numpy
用法: python realtime_viewer.py
"""

import sys
import numpy as np
from collections import deque

from brainflow.board_shim import BoardShim, BrainFlowInputParams, BoardIds
from brainflow.data_filter import DataFilter, FilterTypes, DetrendOperations

import pyqtgraph as pg
from pyqtgraph.Qt import QtWidgets, QtCore


class RealTimeViewer:
    def __init__(self):
        # BrainFlow 设置
        self.board_id = BoardIds.SYNTHETIC_BOARD
        self.descr = BoardShim.get_board_descr(self.board_id)
        self.sampling_rate = self.descr["sampling_rate"] # 250Hz
        self.eeg_channels = self.descr["eeg_channels"]
        self.eeg_names = BoardShim.get_eeg_names(self.board_id)
        # 关闭日志记录
        BoardShim.disable_board_logger()
        
        # 显示参数
        self.display_seconds = 5
        self.display_points = self.display_seconds * self.sampling_rate
        # 5*250 = 1250 点数据
        
        # 数据缓冲(16,1250)
        # 超过长度后会自动丢弃旧数据
        self.buffers = [deque(maxlen=self.display_points) for _ in self.eeg_channels]
        
        # 启动板卡
        params = BrainFlowInputParams()
        self.board = BoardShim(self.board_id, params)
        self.board.prepare_session()
        self.board.start_stream(450000) # 缓冲区可以存下1800ms的数据
        
        # 初始化 GUI
        self._init_gui()
        
    def _init_gui(self):
        # 设置背景为白色
        pg.setConfigOption("background", "w")
        # 设置前景为黑色
        pg.setConfigOption("foreground", "k")
        
        # 创建 Qt 应用实例
        self.app = QtWidgets.QApplication(sys.argv)
        # 创建图形布局窗口，设置标题和大小
        self.win = pg.GraphicsLayoutWidget(title="BCI Real-Time Viewer", size=(1000, 700))
        # 显示窗口
        self.win.show()
        
        # 时域图 - 创建用于显示EEG信号的图表和曲线
        self.plots = []  # 存储每个通道的PlotItem对象
        self.curves = []  # 存储每个通道的PlotDataItem对象（曲线）
        # 为每个EEG通道定义不同的颜色，便于区分
        colors = ["#A54E4E", "#A473B6", "#5B45A4", "#2079D2",
                  "#32B798", "#2FA537", "#9DA52F", "#A53B2F",
                  "#8B4513", "#D2691E", "#FF6347", "#40E0D0",
                  "#EE82EE", "#F5DEB3", "#9ACD32", "#FF69B4"]
        
        # 遍历所有EEG通道，为每个通道创建独立的绘图区域
        for i in range(len(self.eeg_channels)):
            # 在当前窗口位置添加一个新的绘图区域
            p = self.win.addPlot(row=i, col=0)
            # 隐藏左侧Y轴刻度
            p.showAxis("left", True)
            # 禁用左侧Y轴的右键菜单
            p.setMenuEnabled("left", False)
            # 设置Y轴标签为通道名
            axis = p.getAxis("left")
            axis.setLabel(self.eeg_names[i])
            # axis.label.setRotation(45)
            axis.setWidth(20)
            axis.setTicks([])
            # axis.setPen(None)
            # 只在最后一个通道显示底部X轴刻度
            p.showAxis("bottom", i == len(self.eeg_channels) - 1)
            # 禁用底部X轴的右键菜单
            p.setMenuEnabled("bottom", False)
            # 设置X轴范围，显示5秒数据
            # 0-1249点数据，对应5秒时间
            p.setXRange(0, self.display_points)
            # 为第一个通道设置图表标题，包含设备名称和采样率
            if i == 0:
                p.setTitle(f"EEG Signals ({self.descr['name']}, {self.sampling_rate} Hz)")
            # 将绘图对象保存到列表中
            self.plots.append(p)
            
            # 创建画笔，设置曲线颜色和宽度
            pen = pg.mkPen({"color": colors[i], "width": 1})
            # 使用画笔创建曲线对象
            curve = p.plot(pen=pen)
            # 将曲线对象保存到列表中
            self.curves.append(curve)
        
        # 定时器
        self.timer = QtCore.QTimer()
        self.timer.timeout.connect(self._update)
    
        
    def _update(self):
        """定时更新显示"""
        # 从板卡获取当前数据，获取采样率/10个样本（约100ms的数据）
        data = self.board.get_current_board_data(self.sampling_rate // 10)
        
        # 检查是否有新数据
        if data.shape[1] > 0:
            # 遍历所有EEG通道
            for i, ch in enumerate(self.eeg_channels):
                # 复制当前通道的数据，避免修改原始数据
                ch_data = data[ch, :].copy()
                # 简单预处理：去除常数趋势（去直流偏移）
                DataFilter.detrend(ch_data, DetrendOperations.CONSTANT.value)
                # 应用带通滤波器：25.25-49.5 Hz，4阶巴特沃斯滤波器
                # 这可以去除低频漂移和高频噪声，保留主要的EEG信号频段
                DataFilter.perform_bandpass(ch_data, self.sampling_rate,
                                             0.5, 50, 4,
                                             FilterTypes.BUTTERWORTH.value, 0)
                
                # 将处理后的数据点添加到对应通道的缓冲区
                for val in ch_data:
                    self.buffers[i].append(val)
                
                # 更新曲线显示数据
                self.curves[i].setData(list(self.buffers[i]))
    
    def run(self):
        """启动应用"""
        app = QtWidgets.QApplication.instance()
        if app is None:
            raise RuntimeError("QApplication 尚未创建")
        app.aboutToQuit.connect(self.cleanup)
        self.timer.start(100)  # 100ms 更新间隔
        try:
            app.exec()
        finally:
            self.cleanup()


    def cleanup(self):
        """安全释放 BrainFlow 资源"""
        if getattr(self, "_cleaned_up", False):
            return
        self._cleaned_up = True

        # 先停止 Qt 定时器，防止 cleanup 后继续调用 _update
        timer = getattr(self, "timer", None)
        if timer is not None:
            try:
                timer.stop()
            except Exception as e:
                print(f"停止定时器失败: {e}")

        board = getattr(self, "board", None)
        if board is None:
            return
        try:
            if board.is_prepared():
                board.stop_stream()
                board.release_session()
                print("会话已释放")
        except Exception as e:
            print(f"释放会话失败: {e}")
        self.board = None


if __name__ == "__main__":
    viewer = RealTimeViewer()
    viewer.run()
