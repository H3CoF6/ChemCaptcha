## ChemCaptcha  |  Web版插件化化学验证码

### 项目简介

本项目是**基于python 和 RDKIT ** 实现的供**web使用**的有机化学人机验证码

灵感来源于TG机器人的手性碳验证码，参考项目：[chiral-carbon-captcha](https://github.com/leafLeaf9/chiral-carbon-captcha)
<img src="https://user-images.githubusercontent.com/53334104/207500151-c183e106-31f5-4afc-9276-1ca271477b73.png" alt="img" style="zoom:33%;" />

但是那个项目并不好**直接对接web**，且实现的验证码种类有限，所以产生了本项目

由于本项目的验证码实现**采用了插件化的思想**（plugins），实现了种类繁多的验证码形式，并且可以**无限扩展** !!!

<del>如果您嫌弃普通的验证码难度过低，无法防住人机；或者希望以独特风格的验证码展示您站点的风格</del> 那么： **本项目正是你所需要的！！！**

### 快速部署

> 目前推荐手动部署！！dockerfile写得很烂，预计未来优化，实现TUI部署！！

####  手动部署

1. **文件下载**
   分子式文件下载路径在：https://ftp.ncbi.nlm.nih.gov/pubchem/Compound/CURRENT-Full/SDF

   其中每个文件包含**500k个分子文件**，对于绝大多数情况是远远足够（甚至超标的）
   所以建议解压后**只保留合适数目**的分子文件

2. **配置config**

   config在`bsrc/app/utils/config.py`

   参考注释完成配置（主要是文件路径的问题）

3. **安装python依赖**

   建议使用虚拟环境，Linux建议使用uv包管理

   ```bash
   uv pip install -r requirements.txt
   ```

   后续操作记得使用安装好的虚拟环境！！

4. **数据库初始化**

   > 由于本项目在runtime**只读不写**（目前是这样的），所以采用更轻量的Sqlite作为数据库

   ```bash
   # 启动拆分sdf文件的脚本
   cd bsrc/scripts
   python split_sdf.py -i 输入的SDF文件路径 -o 输出的mol目录
   
   # 启动第二个脚本初始化数据库
   ## 不需要等待第一个脚本跑完，可以直接开跑的
   cd .. 
   python -m scripts.init_sqlite
   ```

   耐心等待跑完，<del>或者随时kill掉！！</del>，因为是实时写库，所以kill掉也算是**初始化成功了**

5. **编译前端**（如果生产环境使用就没必要编译前端了）

   ```bash
   cd fsrc
   npm install
   ## 同样推荐直接pnpm i 
   
   npm run build
   ```

   编译成功得到dist文件夹

   把dist文件夹放到`bsrc/app/`，并重命名为static（将**静态挂载到fastapi**）

6. **启动后端服务**

   ```bash
   python -m app.main
   ```

   即可，默认的服务将在8000端口启动

#### Docker部署

直接使用dockerfile分步构建即可，**但是可能有bug**，因为作者自己也没测试过

> 因为感觉实现非常丑陋，后续优化后会推荐使用docker部署的

### 项目截图

| 前端整体![image-20260201230142723](C:\Users\17078\AppData\Roaming\Typora\typora-user-images\image-20260201230142723.png) |
| ------------------------------------------------------------ |
| **点选验证码**![image-20260201230215264](C:\Users\17078\AppData\Roaming\Typora\typora-user-images\image-20260201230215264.png) |
| **正确答案展示**![image-20260201230239233](C:\Users\17078\AppData\Roaming\Typora\typora-user-images\image-20260201230239233.png) |
| **多种验证码可选（最长碳链）**![image-20260201230313814](C:\Users\17078\AppData\Roaming\Typora\typora-user-images\image-20260201230313814.png) |
| **验证码题库选择**![image-20260201230428179](C:\Users\17078\AppData\Roaming\Typora\typora-user-images\image-20260201230428179.png) |
| **rich输出：初始化脚本**![image-20260201230551021](C:\Users\17078\AppData\Roaming\Typora\typora-user-images\image-20260201230551021.png) |



### 项目说明

1. 本项目有很高的LLM成分，**可能存在大量的bug**，未来作者会慢慢修改，当然也欢迎提issue和PR
2. 本项目不保证验证码的安全性，**更多的是趣味性**，真正的反爬需求请接入正规验证码
3. **提倡适度使用**，不要让化学知识成为非化学领域的一道门槛！！！

