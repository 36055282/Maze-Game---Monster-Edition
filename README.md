迷宫游戏 - 怪物版

一款使用Pygame开发的Python迷宫游戏，包含怪物元素。在单人模式中穿越迷宫、躲避怪物，或在对抗模式中与AI竞赛看谁先到达出口！

功能特点
随机生成的迷宫，含多条路径
支持动态墙壁和出口（GIF动画）
5个游荡的怪物需要躲避
玩家生命值系统（3条命）
受击后获得短暂无敌时间
对抗AI模式（含路径寻找功能）
可自定义游戏图形（玩家、怪物、墙壁、出口等）
键盘操控响应灵敏
运行要求
Python 3.6+
Pygame 2.0+
Pillow (PIL) 8.0+
安装步骤
克隆仓库：
git clone https://github.com/yourusername/maze-game-monster-edition.git
cd maze-game-monster-edition
安装依赖包：
pip install -r requirements.txt
游戏玩法
使用方向键或WASD移动
避开红色怪物
到达绿色出口即获胜
初始3条生命 - 碰到怪物会减少1条生命
受击后获得2秒无敌时间（角色会闪烁红光）
游戏模式
​​单人模式​​：独自挑战迷宫和怪物
​​对抗AI​​：与电脑竞赛看谁先到出口
自定义设置
可通过添加以下图片文件到游戏目录来自定义：

player.png - 玩家角色（推荐15x15像素）
monster.png - 怪物图像（推荐10x10像素）
wall.gif - 动态墙壁（20x20像素）
exit.gif 或 exit.png - 出口图像（20x20像素）
menu_image.png - 菜单背景（推荐200x150像素）
background.png - 游戏背景（800x600像素）
操作控制
​​方向键/WASD​​：移动玩家
​​R键​​：重新开始游戏
​​M键​​：返回主菜单
​​1/2键​​：在菜单中选择游戏模式
开源许可
本项目采用MIT许可证 - 详见LICENSE文件。

requirements.txt
pygame>=2.0.0
Pillow>=8.0.0
可选开发依赖
flake8>=3.8.0
black>=20.8b1# Maze-Game---Monster-Edition
一款基于python设计的开源迷宫小游戏——怪物版
