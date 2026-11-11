# Simulator 动画图册 / Animation gallery

**点击任意封面，进入该动画的独立播放页面。** 无需打开 Jupyter；也可以点击 GIF 文件单独预览或下载。

共 8 个 GIF，覆盖原 Simulator 的 5 类动态展示；多周期磁滞图的四个周期选项分别导出。表格使用静态封面，避免同时加载所有动画。

| 动画 | 单独预览 | GIF 文件 |
|---|---|---|
| [自旋构型、外场与磁滞同步演化](spin_configuration_dynamics.md) | [![自旋构型、外场与磁滞同步演化](previews/spin_configuration_dynamics.png)](spin_configuration_dynamics.md) | [打开 GIF](spin_configuration_dynamics.gif) |
| [温度与阶跃外场响应](temperature_field_response.md) | [![温度与阶跃外场响应](previews/temperature_field_response.png)](temperature_field_response.md) | [打开 GIF](temperature_field_response.gif) |
| [三周期磁滞：P=10](multi_cycle_hysteresis_P10.md) | [![三周期磁滞：P=10](previews/multi_cycle_hysteresis_P10.png)](multi_cycle_hysteresis_P10.md) | [打开 GIF](multi_cycle_hysteresis_P10.gif) |
| [三周期磁滞：P=50](multi_cycle_hysteresis_P50.md) | [![三周期磁滞：P=50](previews/multi_cycle_hysteresis_P50.png)](multi_cycle_hysteresis_P50.md) | [打开 GIF](multi_cycle_hysteresis_P50.gif) |
| [三周期磁滞：P=125](multi_cycle_hysteresis_P125.md) | [![三周期磁滞：P=125](previews/multi_cycle_hysteresis_P125.png)](multi_cycle_hysteresis_P125.md) | [打开 GIF](multi_cycle_hysteresis_P125.gif) |
| [三周期磁滞：P=300](multi_cycle_hysteresis_P300.md) | [![三周期磁滞：P=300](previews/multi_cycle_hysteresis_P300.png)](multi_cycle_hysteresis_P300.md) | [打开 GIF](multi_cycle_hysteresis_P300.gif) |
| [周期扫描：磁滞形状与面积](period_sweep_explorer.md) | [![周期扫描：磁滞形状与面积](previews/period_sweep_explorer.png)](period_sweep_explorer.md) | [打开 GIF](period_sweep_explorer.gif) |
| [多温度比较与周期扫描](multi_temperature_period_explorer.md) | [![多温度比较与周期扫描](previews/multi_temperature_period_explorer.png)](multi_temperature_period_explorer.md) | [打开 GIF](multi_temperature_period_explorer.gif) |

## 导出说明

- 温度响应动画直接提取原 notebook 已保存的图像帧；GIF 调色板和播放间隔会有格式转换带来的差异。
- 其余动画使用原 notebook 中对应的计算与绘图代码重新导出，保留原参数与种子。自旋快照展示也保留原有的记录扩展与一致性检查，未另写 Metropolis 更新算法。
- 播放控件转换为自动循环 GIF；GIF 本身不能保留滑块或复选框。多温度图保留默认全部温度选中的状态，不枚举所有复选框组合。
- 周期扫描图的每一帧代表不同 P，并非同一条轨迹的下一个时间点。
- 原仓库的三个早期 GIF 仍保留在上一级目录；它们是旧版重画的演示，与这里直接依据完整 Simulator 导出的版本分开保存。

## 来源与重现

对应原 notebook 的单元格源代码保存在 [source_cells.json](source_cells.json)，参数、帧数、文件哈希见 [manifest.json](manifest.json)。原 notebook 保持不变。

从仓库根目录运行：

```sh
python tools/export_notebook_gifs.py
```

默认重画七个基于代码的 GIF，并保留已发布的温度响应 GIF。若要重新提取温度响应的原始帧，提供保存了 HTML 动画输出的原 notebook：

```sh
python tools/export_notebook_gifs.py --notebook /path/to/Simulator.ipynb
```

仅用于导出图像；不会触发完整验证网格或修改已有研究结果。
