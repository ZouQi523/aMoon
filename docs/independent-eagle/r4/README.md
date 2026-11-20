# R4：穿服角色通过舱口、登上平台并返舱

本关口通过。范围仅为独立可玩的引导式舱口／平台动作：同一个原游戏着装角色和背包，等待门向内打开、低姿后退出门、转移双脚到旧平台、停在扶栏低姿，再沿原路径返舱并收门。没有接入下梯节奏，没有替换默认入口或 R3。

## 最短试玩

在工程根目录：

```sh
python3 scripts/independent-eagle/build_r4_release.py
python3 -m http.server 8000 --bind 127.0.0.1
```

打开 <http://127.0.0.1:8000/web-release/r4-play/>。点「播放／暂停」或按空格出舱；平台终点自动停，点「反向检查」或按 F 返舱。可在途中暂停／换向，滑条逐姿态检查；切「舱内／舱外／平台／侧剖」。默认完整舱壁，舱内为侧上方第三人称观察机位，非历史眼位认证；剖视仅隐藏显示，不豁免任何碰撞。

未打包的独立入口：<http://127.0.0.1:8000/web-release/independent-egress-r4/>。两个入口使用相同源代码。原 Mac 的回环地址不能在另一台电脑直接使用；私有 Git bundle 在新机器克隆后运行上面两条命令即可。纯试玩只需 Python 与现代 WebGL 浏览器，不需要 Blender、Node 或联网素材。

原默认游戏仍是根目录 `index.html`，原 R3 保留在 `/web-release/independent-egress/`。重新生成 R3 用 `python3 scripts/independent-eagle/build_egress_preview.py`，用于查看旧动作冲突，不是 R4 的默认动作。

## 实际改动

- 原旋转绕脚底，R4 改为骨盆枢轴；明确等待门扫过，再移位、起蹲、收臂与低姿通过。终点保持低姿，避免站直撞上倾斜前壁。
- 增加原控制骨架缺失的有限颈部自由度，最大 0.45 rad（25.8°）。扫描服头部、透明罩、面部和遮阳罩一起抬头；颈部枢轴和权重过渡是游戏近似，不报压力服生物力学认证。
- 原扫描顶点、原角色比例、肢段长度、R2 舱体和真窗孔全部保留。只在 R4 副本克隆并重分配头部权重，原扫描位置数组的 SHA-256 与 R3 逐项一致。12 根控制骨骼（原 11 根加颈部），无肢段伸缩。
- 鞋跟跨 73.5 mm 门槛时分脚抬起再落平台；手目标按真实手套表面与支承面校正，平台末端按原圆管半径拟合，抬手过栏后接触。没有让手套顶点单独移动到目标，也没有只检查 IK 点。
- 保留实体左窗 LPD，40°／50°史料版本差异和既有几何近似不变。未使用受限 STL、A11D 或 NASSP 派生物。

每向实际播放 21.6 秒；参数表的 0–16.2 为姿态相位，界面和短片显示换算后的实际秒数。动作速度已放慢，逐帧顶点位移检查上限为 60 mm / 1⁄30 s，实测最大约 58.1 mm；旧的最短弧手臂翻转已改为完整连续坐标架。

动作策略参考 [NASA ALSJ Apollo 11 出舱记录](https://history.nasa.gov/wp-content/uploads/static/history/alsj/a11/a11.step.html)：先定位脚部、跪姿后退、调整背部姿势、避开中段甲板和舱门铰链，并在平台检查返舱。本轮不是飞行实录的精确帧复刻。R2 来源账目继续见 `references/independent-eagle/r2/references-r2.json`。

## 已实际通过的验证

1. **真实网格双向检查**：60 Hz 模拟，每 2 步导出一次，30 Hz 检查；1,322 个姿态全部包含实际变形扫描服、背包／RCU／软管／天线、透明头盔／遮阳罩／面部及两只靴套。56,241 个被索引顶点、57,664 个三角形，对完整 R2 舱体、真实开角门扇、旧平台／扶栏／梯子做 Blender 三角面 BVH 相交，0 个交叉姿态。正负表面夹具通过，不能仅靠包围盒误报。
2. **支承面接触**：查询实际变形表面到实际支承三角面的最近距离，不以目标点替代。全程至少一只靴底距支承面不超过约 6.01 mm；平台终点两只靴底约 6.0 mm，右／左手套到真实扶栏约 4.4／3.7 mm。采用 8 mm 的游戏接触容差，未报告深穿透。手转移阶段允许离开原支点，不宣称双手全程贴住结构。
3. **完整出门**：平台终点整个人物最低 Z 约 1.667 m，超过门槛前沿 Z=1.601 m；两只靴套完整足迹仍在旧平台边界内。不是仅将背包包络点穿过去。
4. **双向一致与可达**：相同时间位置的出／返实际顶点最大差异小于 1 µm；双腿目标最大距离约 0.677 m，小于原 0.740 m 两段骨长；手目标误差为浮点精度，没有借伸缩掩盖不可达。
5. **生产版实际输入**：静态构建 36 个核心资产，实际点击播放／暂停、空格、F 换向、滑条 Home／End、完整出返舱、门打开／关闭均通过，无页面脚本错误。生产版是相对路径的自包含静态目录。
6. **未改区域**：默认 `index.html`、R2 JSON／GLB／Blender、左窗 LPD 生成器、原比较脚本和 R3 源码散列保持。默认发布构建仍 36 个资产，实际点击开始并输入 Space 到 flight，无 R4 钩子。没有改月球车、悬挂、喷尘或仪表。

详见 `verification.json`、`dense/collision-report.json`、`rig-preservation.json`、`production-smoke.json`。最早 M0 是未通过的关键姿态记录；M2 是较疏 173 样本先通过的检查点；最终以上述密测为准。

环境：macOS 26.6.2、Blender 5.1.1、Python 3.9.6、Node 与 Chrome 的实际版本见 `rig-preservation.json`。实际渲染提交的 40 个平台换手姿态 CPU 中位约 6.8 ms、P95 约 8.1 ms；不是 GPU 帧率或移动端认证。

复测命令（先按最短试玩启动服务器）：

```sh
# QA 需 playwright-core；已有依赖时无需再安装。CHROME 可指定浏览器路径。
python3 scripts/independent-eagle/build_egress_preview.py
node scripts/independent-eagle/r4_audit.mjs --dense
blender --background --python scripts/independent-eagle/r4_check.py -- --dense
python3 scripts/independent-eagle/r4_motion.py  # 此项 QA 需 numpy
node scripts/independent-eagle/r4_rig_test.mjs
node scripts/independent-eagle/r4_smoke.mjs
```

完整 QA 的 `.f32`／拓扑与视频帧是本机可重生临时文件，不进交付 Git bundle。生成默认发布页用 `python3 scripts/build_web.py`。

## 交付与边界

手机同机位对照 `Eagle-R4-phone-comparison.png` 和短片 `Eagle-R4-passage-return.mp4` 只含原游戏可分享内容和独立 R2。短片约 28.9 s、1.5×，显示完整出舱／平台／返舱收门；部分镜头明确标注剖视。原 R3 和 R4 的关键帧使用相同舱体局部机位，动作时序不同，未冒充同时间帧。

本轮完成定义是**引导式运动学过门／平台通行**，不是人体受力、手指包握、压力服生物力学或连续碰撞数学证明。起蹲和舱内短挪位仍为程序近似；后舱近似体积、历史精确眼位、LPD 飞行实物版本、移动端性能和完整下梯均未扩展或认证。下一阶段才能据这个已核对接口处理下梯接触节奏。

Git 交付在隔离本地工作树／无父提交的交付分支整理，只复制明确允许分享的源码／模型及小型验证记录；原工作区用户未提交文件、当前分支和暂存区不改；Git 仅新增交付工作树／分支记录。没有推送、部署或合并 main。版本、bundle 哈希和 Library 身份见交付清单。
