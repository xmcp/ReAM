# ReAM
基于 Python 的键盘记录器。

分为被控端（`Rem`）控制端（`Ram`）两部分。

`Rem` 经过 `cxfreeze` 打包后可以隐蔽地启动、记录相关数据并尝试连接由配置文件指定的 `Ram`。

`Ram` 可以收集多个被控端的数据。

`Rem` 支持 Python 2 和 Python 3，但推荐使用 Python 2，因为 `pyHook` 的 Python 3 fork 安装不太方便，而且 Python 2 的脚本打包之后体积更小。

`Ram` 只支持 Python 3。

预期中的功能列表：

- 离线记录、查看数据；
- 窗口截图；
- 被控端配置文件；
- 主控端保存记录到文件。

## 截图

**v1.0** 实现了截图功能
![v1.0_1](https://cloud.githubusercontent.com/assets/6646473/16311962/30685064-39a5-11e6-9e6a-c5a6e913aed5.png)
![v1.0_2](https://cloud.githubusercontent.com/assets/6646473/16311882/d9761d72-39a4-11e6-90d3-c3655e05fe5d.png)

**v0.5**
![v0.5_1](https://cloud.githubusercontent.com/assets/6646473/16302387/6c90017c-397d-11e6-97d5-89ecd0151076.png)

## R.M.T! R.M.T! R.M.T!
![rmt](https://cloud.githubusercontent.com/assets/6646473/16269759/2dc64044-38c6-11e6-89d4-d7e737f9c941.png)
