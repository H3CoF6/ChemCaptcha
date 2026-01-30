## Web Chemistry Captcha  |  插件化的Web化学验证码

> 受到项目[chiral-carbon-captcha](https://github.com/leafLeaf9/chiral-carbon-captcha)的启发，决定造一个**更多种类**的化学验证码
>
> 原项目选择用java造轮子，本项目将使用**python作为后端语言**进行快速开发
>
> 核心思路是将**验证码作为插件**，实现各种不同的验证码的**无限扩展**

---

**.mol文件来源**：https://ftp.ncbi.nlm.nih.gov/pubchem/Compound/CURRENT-Full/SDF/

考虑使用：https://ftp.ncbi.nlm.nih.gov/pubchem/Compound/CURRENT-Full/SDF/Compound_167500001_168000000.sdf.gz

（分子量比较大！！）

预期实现至少以下类型的验证码

- [x] 手性碳
- [x] 芳香环
- [x] 顺反异构
- [ ] 主链
- [ ] 酸碱中心
- [ ] 位阻
- [ ] 氢键供受
- [ ] 共面
- [ ] 共线
- [ ] 共振

---

### 项目施工中，暂无部署和使用文档

未来会加入Dockerfile容器化部署


