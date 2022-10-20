import sys
from pathlib import Path
from AioSpider.template import create_project as cpj
from AioSpider.template import gen_spider as gs


argv = sys.argv
# aioSpider options value [-argv]


# 创建项目 aioSpider createProject project
def create_project(name):

    items = cpj(name)

    for item in items:
        if item['type'] == 'dir' and not item['path'].exists():
            item['path'].mkdir(parents=True, exist_ok=True)

    for item in items:
        if item['type'] == 'file' and not item['path'].exists():
            item['path'].write_text(item['text'], encoding='utf-8')


# 创建爬虫 aioSpider genSpider spider
def gen_spider(args):

    name = args[2]
    if len(args) == 4:
        start_url = args[3]
    else:
        start_url = None

    spider_text = gs(name, start_url)
    path = Path().cwd() / f'spider/{name}.py'
    if not path.exists():
        path.write_text(spider_text, encoding='utf-8')


# 创建爬虫 aioSpider genModel model
def gen_model(args):
    sql = args[2]
    print(sql)


sql = """
CREATE TABLE `mmb_main_essential_information` (
  `ID` int NOT NULL AUTO_INCREMENT,
  `NAME` varchar(100) NOT NULL COMMENT '公司名称',
  `SUOSHUSF` varchar(30) DEFAULT NULL COMMENT '所属省份',
  `SUOSHUCS` varchar(50) DEFAULT NULL COMMENT '所属城市',
  `SUOSHUQX` varchar(50) DEFAULT NULL COMMENT '所属区县',
  `SUOSHUCYL` varchar(80) DEFAULT NULL COMMENT '所属产业链1',
  `SUOSHUHY` varchar(40) DEFAULT NULL COMMENT '所属行业',
  `SUOSHUEJHY` varchar(80) DEFAULT '' COMMENT '所属二级行业1',
  `JINGYINGFW` text COMMENT '经营范围',
  `SUOSHUZBSC` varchar(20) DEFAULT NULL COMMENT '所属资本市场',
  `ZIBENSCDY` int DEFAULT NULL COMMENT '所属资本市场对应（A股拟IPO公司-1，A股公司-2，三板公司-3，四板公司-4，已私募融资公司-5，非挂牌非上市公司-6，海外上市公司-7）',
  `OLDEJHANGYE` varchar(80) DEFAULT NULL,
  `OLDHANGYE` varchar(40) DEFAULT NULL COMMENT '员工人数',
  `YOUXIANDJ` char(4) DEFAULT NULL COMMENT '优先等级',
  `ZHUCEZB` varchar(30) DEFAULT NULL COMMENT '注册资本（万元）',
  `ZHUCEZBINT` double(20,2) DEFAULT NULL COMMENT '注册资本-数字',
  `ZHUCEZT` varchar(50) DEFAULT NULL COMMENT '注册状态',
  `FADINGDBR` varchar(100) DEFAULT NULL COMMENT '法定代表人',
  `CHENGLISJ` varchar(30) DEFAULT NULL COMMENT '成立时间',
  `ZHUCEDZ` varchar(300) DEFAULT NULL COMMENT '注册地址',
  `LEIXING` int DEFAULT NULL COMMENT '(公司类型，1-大陆企业  2-港澳台  3-外资 4-国有)',
  `CREATE_TIME` datetime DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '登记时间',
  `DIANHUA` varchar(60) DEFAULT NULL COMMENT '电话',
  `LIANXIDH` text COMMENT '联系电话',
  `LIANXIYX` varchar(80) DEFAULT NULL COMMENT '联系邮箱',
  `TONGYIXYDM` varchar(50) DEFAULT NULL COMMENT '统一信用代码',
  `NASHUIRSBH` varchar(50) DEFAULT NULL COMMENT '纳税人识别号',
  `GONGSHANGZCH` varchar(30) DEFAULT NULL COMMENT '工商注册号',
  `ZUZHIJGDM` varchar(50) DEFAULT NULL COMMENT '组织机构代码',
  `GONGSILX` varchar(80) DEFAULT NULL COMMENT '公司类型',
  `GONGSIWZ` varchar(300) DEFAULT NULL COMMENT '公司网址',
  `QIYEJJ` text COMMENT '企业简介',
  `FINACELINK` varchar(500) DEFAULT NULL COMMENT '业务亮点拼接',
  `YINGYEQX` varchar(50) DEFAULT NULL COMMENT '营业期限',
  `TONGXINDZ` varchar(300) DEFAULT NULL COMMENT '通信地址',
  `IS_GX` char(6) DEFAULT NULL COMMENT '联系方式数量',
  `IS_BZ` char(1) DEFAULT NULL COMMENT '标准制定c',
  `IS_ZX` char(1) DEFAULT NULL COMMENT '专项证照d',
  `IS_ZF` char(1) DEFAULT NULL COMMENT '政府奖励b',
  `DIANHUAS` varchar(5) DEFAULT NULL COMMENT '1表示已经对接，0表示未对接',
  `TAX` double(20,0) DEFAULT '0' COMMENT '是否失信企业（1是，0否）',
  `RANKWEIGHT` double(20,4) DEFAULT '0.0000' COMMENT '是否A级纳税企业（1是，0否）',
  `ISINVEST` varchar(5) DEFAULT '否' COMMENT '是否有投资信息或购买其他公司股权（是、否）',
  `ISGUARANTY` varchar(5) DEFAULT '否' COMMENT '是否有对外提供担保信息（是、否）',
  `LOCATIONS` varchar(30) DEFAULT NULL COMMENT '经纬度',
  `longitude` double(20,15) DEFAULT NULL,
  `latitude` double(20,15) DEFAULT NULL,
  PRIMARY KEY (`ID`) USING BTREE,
  UNIQUE KEY `name_index` (`NAME`) USING BTREE,
  KEY `sf_index` (`SUOSHUSF`) USING BTREE,
  KEY `RANKWEIGHT` (`RANKWEIGHT`) USING BTREE,
  KEY `erjihy_index` (`SUOSHUEJHY`,`ZIBENSCDY`) USING BTREE,
  KEY `suoshuhy` (`SUOSHUHY`) USING BTREE,
  KEY `zibdy` (`ZIBENSCDY`) USING BTREE,
  KEY `youxiandj` (`YOUXIANDJ`) USING BTREE,
  KEY `leixing` (`LEIXING`,`YOUXIANDJ`,`ZHUCEZBINT`) USING BTREE,
  KEY `locations` (`longitude`,`latitude`) USING BTREE,
  KEY `pz_index` (`ZHUCEZBINT`) USING BTREE,
  KEY `dz_index` (`ZHUCEDZ`) USING BTREE
) ENGINE=MyISAM AUTO_INCREMENT=1263977826 DEFAULT CHARSET=utf8mb3 COMMENT='企业-基本信息' |
"""
argv = ['aioSpider', 'genModel', 'aaa']


if argv[1] == 'createProject':
    create_project(argv[2])

elif argv[1] == 'genSpider':
    gen_spider(argv)

elif argv[1] == 'genModel':
    gen_model(args)
