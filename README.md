# OpenBCI × BrainFlow 学习计划

基于 **BrainFlow** 官方库和 **BoardShim** API 的系统性脑机接口（BCI）学习教程，无需任何硬件即可开始学习（使用 Synthetic Board 模拟数据）。

## 学习路线图

| Unit | 主题 | 核心知识 | 文件 |
|------|------|----------|------|
| 1 | OpenBCI & BrainFlow 入门 | BCI概念、硬件概览、BrainFlow架构、环境安装 | [unit1_introduction.ipynb](notebooks/unit1_introduction.ipynb) |
| 2 | BoardShim 基础 | 会话管理、合成板、数据获取、通道理解 | [unit2_boardshim_basics.ipynb](notebooks/unit2_boardshim_basics.ipynb) |
| 3 | 数据采集深入 | 板卡类型、CSV回放与流式板、Markers、数据持久化 | [unit3_data_acquisition.ipynb](notebooks/unit3_data_acquisition.ipynb) |
| 4 | 信号处理 API | 滤波、去趋势、小波去噪、滚动平滑 | [unit4_signal_processing.ipynb](notebooks/unit4_signal_processing.ipynb) |
| 5 | 频域分析与特征提取 | PSD、频带功率、统计特征、特征向量构建 | [unit5_frequency_analysis.ipynb](notebooks/unit5_frequency_analysis.ipynb) |
| 6 | ML 集成 | BrainFlow内置ML模型、放松度/专注度/正念度评估 | [unit6_ml_integration.ipynb](notebooks/unit6_ml_integration.ipynb) |
| 7 | 实战项目 | 完整BCI流水线：采集→处理→特征→ML→可视化 | [unit7_capstone_project.ipynb](notebooks/unit7_capstone_project.ipynb) |

## 环境依赖

### 核心依赖（必须安装）

```bash
pip install brainflow numpy
```

### 可视化与数据处理（推荐安装）

```bash
pip install matplotlib pandas
```

### 交互式实时可视化（实战项目使用）

```bash
pip install pyqtgraph PyQt5
```

### 可选依赖（进阶扩展）

```bash
pip install mne scipy scikit-learn
```

## 依赖说明

| 库 | 用途 | 是否必须 |
|----|------|----------|
| `brainflow` | 核心库：数据采集、信号处理、ML模型 | ✅ 必须 |
| `numpy` | 数值计算、数组操作 | ✅ 必须 |
| `matplotlib` | 静态图表绘制 | 🔸 推荐 |
| `pandas` | 数据框操作、CSV读写 | 🔸 推荐 |
| `pyqtgraph` | 高速实时图表 | 🔸 实战项目 |
| `PyQt5` | pyqtgraph 的 Qt 后端 | 🔸 实战项目 |
| `mne` | EEG专业分析（MNE-Python） | 🔹 可选 |
| `scipy` | 科学计算（信号处理补充） | 🔹 可选 |
| `scikit-learn` | 自定义ML模型训练 | 🔹 可选 |

## 快速开始

```bash
# 1. 安装核心依赖
pip install brainflow numpy matplotlib pandas

# 2. 克隆或下载本项目
cd openbci-5

# 3. 启动 Jupyter Notebook
jupyter notebook notebooks/

# 4. 按顺序学习 Unit 1 → Unit 7
```

## 不需要真实硬件

所有 Unit 均使用 BrainFlow 内置的 **Synthetic Board**（合成板）进行演示，生成模拟 EEG 信号。这意味着：

- 🚫 不需要购买 OpenBCI 设备
- 🚫 不需要安装串口驱动
- ✅ 所有代码可直接运行
- ✅ 学习完成后，只需修改 `board_id` 和 `params` 即可切换到真实硬件

## 关键概念速览

### BrainFlow 三大核心模块

```
┌─────────────────────────────────────────────┐
│                  BrainFlow                    │
├─────────────────┬─────────────────┬─────────┤
│   BoardShim     │   DataFilter    │ MLModel │
│   (数据采集)     │   (信号处理)     │ (ML推理) │
├─────────────────┼─────────────────┼─────────┤
│ • 设备连接       │ • 滤波          │ • 放松度  │
│ • 数据流控制     │ • 去噪          │ • 专注度  │
│ • 板卡信息查询   │ • 频域分析       │ • 正念度  │
│ • 数据回放       │ • 特征提取       │ • ONNX    │
└─────────────────┴─────────────────┴─────────┘
```

### BoardShim 统一抽象

BrainFlow 的核心优势：**一套代码适配所有支持的硬件**。切换设备只需修改 `board_id` 和连接参数。

```python
# 合成板（测试用）
board = BoardShim(BoardIds.SYNTHETIC_BOARD, BrainFlowInputParams())

# OpenBCI Cyton（仅需修改两处）
params = BrainFlowInputParams()
params.serial_port = "COM3"
board = BoardShim(BoardIds.CYTON_BOARD, params)

# 其余代码完全相同！
```

## 官方资源

| 资源 | 链接 |
|------|------|
| BrainFlow 官方文档 | https://brainflow.readthedocs.io |
| BrainFlow GitHub | https://github.com/brainflow-dev/brainflow |
| OpenBCI 官方文档 | https://docs.openbci.com |
| BrainFlow Notebooks | https://github.com/brainflow-dev/brainflow/tree/master/docs/notebooks |

## 学习建议

1. **按顺序学习**：每个 Unit 都依赖前面 Unit 的知识
2. **动手运行**：每个代码单元格都设计为可直接执行
3. **修改实验**：尝试修改参数（滤波阶数、窗口大小、频带范围），观察输出变化
4. **最后实战**：Unit 7 会将所有知识串联成一个完整的 BCI 应用
