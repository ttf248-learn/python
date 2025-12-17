# 需求拆分

1.分析网页数据：https://hk.eastmoney.com/buyback.html?code=00700，编写python代码，抓取所有的公司行动数据
2.设计合理的本地数据存储方式，不依赖三方中间件，通过文件方式存储最好，股票代码不是固定的
3.需要支持不同的股票代码
4.启动的时候能读取本地数据
5.设计 cli 交互模式，支持查看数据汇总，按月、按年汇总回购的金额
6.如果合约已经抓取，下次抓取需要按照日期支持数据更新，每天仅有一次回购，日期作为去重的索引，除了第一次，后续的抓取增量更新即可

需要抓取的数据是这些，你需要自行访问网页，进行分析、提取数据，页面支持翻页，需要自动翻页，获取全部的数据，

1	00700	腾讯控股	105.40万	611.000	599.500	603.358	63593.95万	2025-12-11
2	00700	腾讯控股	106.00万	603.000	595.500	599.539	63551.12万	2025-12-10
3	00700	腾讯控股	105.60万	609.500	596.500	601.956	63566.50万	2025-12-09
4	00700	腾讯控股	104.90万	608.500	604.500	606.101	63579.95万	2025-12-08
5	00700	腾讯控股	104.60万	610.500	605.000	608.025	63599.39万	2025-12-05

## 请求网页收到的应答


<!DOCTYPE html>

<!--published at 12/12/2025 11:23:20 AM by hk.eastmoney.com/buyback PJ 101 Linux .NetCore6.0 23-->
<html>
<head>
    <meta http-equiv="Content-Type" content="text/html; charset=utf-8" />
    <meta http-equiv="X-UA-Compatible" content="IE=edge">
    <title>公司回购 _ 东方财富网</title>
    <meta name="keywords" content="港股资讯、港股吧、港股行情报价、A&#x2B;H股比价表、机构持仓、机构评级、沽空记录、公司回购、新股上市、港股ADR、港股日志" />
    <meta name="description" content="东方财富网港股频道，中国最具人气的港股资讯交流平台，提供最及时的港股市场资讯和行情交易数据，覆盖港股资讯、港股吧、港股行情报价、A&#x2B;H股比价表、机构持仓、机构评级、沽空记录、公司回购、新股上市、港股ADR、港股日志" />
    <meta name="Author" content="东方财富网" />
    <meta name="Copyright" content="东方财富网版权所有" />
    <meta name="referrer" content="always">
    <link rel="shortcut icon" type="image/x-icon" href="/favicon.ico" />
    
    <link rel="stylesheet" href="/emresource/main/css/hk_buyback.css?v=2025.12.12.11">

    <base target="_blank" />
</head>
<body class="stock" style="margin-top:33px">
    <div style="background-color:#fff;width:1000px;margin:0 auto;">
        



<div class="container" id="container">
    <div class="header" id="header">
        

<div class="Navigation">
    <ul><li class='first'><a  target="_blank" href="http://finance.eastmoney.com/" >财经</a></li><li><a  target="_blank" href="http://finance.eastmoney.com/yaowen.html" >焦点</a></li><li><a  target="_blank" href="http://stock.eastmoney.com/" >股票</a></li><li><span class="red"><a  target="_blank" href="http://stock.eastmoney.com/newstock.html" >新股</a></span></li><li><a  target="_blank" href="http://stock.eastmoney.com/gzqh.html" >期指</a></li><li><a  target="_blank" href="http://option.eastmoney.com/" >期权</a></li><li><span class="red"><a  target="_blank" href="http://quote.eastmoney.com/flash/sz300059.html" >行情</a></span></li><li><a  target="_blank" href="http://data.eastmoney.com/" >数据</a></li><li><a  target="_blank" href="http://stock.eastmoney.com/global.html" >全球</a></li><li><a  target="_blank" href="http://stock.eastmoney.com/america.html" >美股</a></li><li><a  target="_blank" href="http://hk.eastmoney.com/" >港股</a></li><li><a  target="_blank" href="http://futures.eastmoney.com/" >期货</a></li><li><a  target="_blank" href="http://forex.eastmoney.com/" >外汇</a></li><li><a  target="_blank" href="http://bank.eastmoney.com/" >银行</a></li><li><a  target="_blank" href="http://www.1234567.com.cn/" >基金</a></li><li><a  target="_blank" href="http://money.eastmoney.com/" >理财</a></li><li><a  target="_blank" href="http://bond.eastmoney.com/" >债券</a></li><li><a  target="_blank" href=" https://roadshow.eastmoney.com/" >直播</a></li><li><span class="red"><a  target="_blank" href="http://guba.eastmoney.com/" >股吧</a></span></li><li><a  target="_blank" href="http://guba.eastmoney.com/jj.html" >基金吧</a></li><li><a  target="_blank" href="http://blog.eastmoney.com/" >博客</a></li><li><span class="red"><a  target="_blank" href="http://caifuhao.eastmoney.com/" >财富号</a></span></li><li><a  target="_blank" href="http://so.eastmoney.com/" >搜索</a></li></ul>
</div>

        <div class="row" style="margin: 10px 0 0 0;">
            <div class="adLeft">
                <iframe class="lyad" width="175" height="90" frameborder="0" scrolling="no" marginwidth="0" marginheight="0" src="//same.eastmoney.com/s?z=eastmoney&c=299&op=1"></iframe>
            </div>
            <div class="adCenter">
                <iframe class="lyad" width="636" height="90" frameborder="0" scrolling="no" marginwidth="0" marginheight="0" src="//same.eastmoney.com/s?z=eastmoney&c=1210&op=1"></iframe>
            </div>
            <div class="adRight">
                <iframe class="lyad" width="175" height="90" frameborder="0" scrolling="no" marginwidth="0" marginheight="0" src="//same.eastmoney.com/s?z=eastmoney&c=300&op=1"></iframe>
            </div>
        </div>



        

<div class="main_frame">

    <div class="logo">
        <a href="http://www.eastmoney.com" target="_blank">
            <img src="/emresource/main/images/logo.gif" alt="东方财富网">
        </a>
        <a href="https://hk.eastmoney.com/" target="_blank">
            港股
        </a>
    </div>

        <div class="category_wrap">
        <div class="category_item">
        <span class="icons icon-market"></span>
        <a href="http://quote.eastmoney.com/center/">行情中心</a>
        </div>
        <div class="category_item">
        <span class="icons icon-pie-chart"></span>
        <a href="http://data.eastmoney.com/center/">数据中心</a>
        </div>
        <div class="category_item">
        <span class="icons icon-mobile"></span>
        <a href="http://wap.eastmoney.com/spread/">手机站</a>
        </div>
        <div class="category_item">
        <span class="icons icon-client"></span>
        <a href="https://acttg.eastmoney.com/pub/pctg_hskh_act_gfcgrj_01_01_01_0">客户端</a>
        </div>
        </div>

</div>




        <div class="menu">
            <div class="menuTitle">
                <a href="http://hk.eastmoney.com/" target="_blank">港股首页</a>
            </div>
            <div class="mainMenu">
                <ul>
                    <li><a target="_blank" href="http://hk.eastmoney.com/news/cggdd.html">港股导读</a></li>
                    <li><a target="_blank" href="http://hk.eastmoney.com/news/cggyw.html">港股聚焦</a></li>
                    <li><a target="_blank" href="http://hk.eastmoney.com/news/csckx.html">市场快讯</a></li>
                    <li><a target="_blank" href="http://hk.eastmoney.com/news/cahgdt.html">AH股动态</a></li>
                    <li><a target="_blank" href="http://hk.eastmoney.com/news/cgsbd.html">公司报道</a></li>
                    <li><a target="_blank" href="http://stock.eastmoney.com/news/cgsyj.html">公司研究</a></li>
                    <li><a target="_blank" href="http://hk.eastmoney.com/news/cggyj.html">个股研究</a></li>
                    <li><a target="_blank" href="http://hk.eastmoney.com/news/cwozx.html">窝轮资讯</a></li>
                    <li><a target="_blank" href="http://quote.eastmoney.com/center/hkstock.html#_1">港股行情中心</a></li>
                    <li><a target="_blank" href="http://hk.eastmoney.com/notice.html">港股日历</a></li>
                    <li class="nobg"><a target="_blank" href="http://guba.eastmoney.com/hk.html">港股吧</a></li>
                </ul>
            </div>
        </div>
        <div class="subMenu">
            <ul>
                <li class="first" style="_width:80px;"><span style="float:left; ">港股数据</span><b style="float:left;margin-left:6px;"></b></li>
                <li><a href="http://hk.eastmoney.com/notice.html" target="_blank">港股日历</a></li>
                <li><a href="http://hk.eastmoney.com/rating.html" target="_blank">机构评级</a></li>
                <li><a href="http://hk.eastmoney.com/hold.html" target="_blank">机构持仓</a></li>
                <li><a href="http://hk.eastmoney.com/ipolist.html" target="_blank">新股上市</a></li>
                <li><a href="http://hk.eastmoney.com/buyback.html" target="_blank">公司回购</a></li>
                <li><a href="http://hk.eastmoney.com/sellshort.html" target="_blank">沽空记录</a></li>
                <li><a href="http://data.eastmoney.com/notices/gg.html" target="_blank">港股公告</a></li>
                <li><a href="http://quote.eastmoney.com/center/list.html#ah_1" target="_blank">AH比价</a></li>
                <li><a href="http://quote.eastmoney.com/center/adrlist.html#adr_1" target="_blank">ADR</a></li>
            </ul>
        </div>


    </div>
    <div class="main" id="main">


        <div class="row">
            <div class="card">
                <div class="card_header">
                    <div class="card_title">
                        <a target="_blank" href="http://hk.eastmoney.com/buyback.html">公司回购</a>
                    </div>
                    <div class="card_inner">
                        <div class="search">
                            <form target="_self" method="get" class="search_form">
                                <label>按个股查询：</label>
                                <input type="text" id="StockCode" name="code" class="StockCode" autocomplete="off">
                                <input type="submit" class="cxbtn" value="查询">
                            </form>
                        </div>

                        <div class="date">
                            <label class="ml20">按时间查询：</label>
                            <input type="text" onclick="WdatePicker()" id="sdate" class="wdate w90" readonly="">
                            <span>到 </span>
                            <input type="text" onclick="WdatePicker()" id="edate" class="wdate w90" readonly="">
                            <input type="submit" class="cxbtn" id="dateBtn" value="查询">
                        </div>
                    </div>
                    <div class="card_more"><a class="ml10" target="_self" href="http://hk.eastmoney.com/buyback.html" id="wacth_all">查看全部</a></div>
                </div>
                <div class="card_body">
                    <table class="table table_striped center ">
                        <thead>
                            <tr>
                                <td>序号</td>
                                <td>股票代码</td>
                                <td>股票名称</td>
                                <td>回购数量(股)</td>
                                <td>最高回购价</td>
                                <td>最低回购价</td>
                                <td>回购平均价</td>
                                <td>回购总额(港元)</td>
                                <td>日期</td>
                            </tr>
                        </thead>
                        <tbody>

                                    <tr>
                                        <td><span>1</span></td>
                                        <td>
                                            <a target="_blank" href="http://quote.eastmoney.com/hk/00700.html">00700</a>
                                        </td>
                                        <td>
                                            <a target="_blank" href="http://quote.eastmoney.com/hk/00700.html">腾讯控股</a>
                                        </td>
                                        <td><span>105.40万</span></td>
                                        <td><span>611.000</span></td>
                                        <td><span>599.500</span></td>
                                        <td><span>603.358</span></td>
                                        <td><span>63593.95万</span></td>
                                        <td><span>2025-12-11</span></td>
                                    </tr>
                                    <tr>
                                        <td><span>2</span></td>
                                        <td>
                                            <a target="_blank" href="http://quote.eastmoney.com/hk/00700.html">00700</a>
                                        </td>
                                        <td>
                                            <a target="_blank" href="http://quote.eastmoney.com/hk/00700.html">腾讯控股</a>
                                        </td>
                                        <td><span>106.00万</span></td>
                                        <td><span>603.000</span></td>
                                        <td><span>595.500</span></td>
                                        <td><span>599.539</span></td>
                                        <td><span>63551.12万</span></td>
                                        <td><span>2025-12-10</span></td>
                                    </tr>
                                    <tr>
                                        <td><span>3</span></td>
                                        <td>
                                            <a target="_blank" href="http://quote.eastmoney.com/hk/00700.html">00700</a>
                                        </td>
                                        <td>
                                            <a target="_blank" href="http://quote.eastmoney.com/hk/00700.html">腾讯控股</a>
                                        </td>
                                        <td><span>105.60万</span></td>
                                        <td><span>609.500</span></td>
                                        <td><span>596.500</span></td>
                                        <td><span>601.956</span></td>
                                        <td><span>63566.50万</span></td>
                                        <td><span>2025-12-09</span></td>
                                    </tr>
                                    <tr>
                                        <td><span>4</span></td>
                                        <td>
                                            <a target="_blank" href="http://quote.eastmoney.com/hk/00700.html">00700</a>
                                        </td>
                                        <td>
                                            <a target="_blank" href="http://quote.eastmoney.com/hk/00700.html">腾讯控股</a>
                                        </td>
                                        <td><span>104.90万</span></td>
                                        <td><span>608.500</span></td>
                                        <td><span>604.500</span></td>
                                        <td><span>606.101</span></td>
                                        <td><span>63579.95万</span></td>
                                        <td><span>2025-12-08</span></td>
                                    </tr>
                                    <tr>
                                        <td><span>5</span></td>
                                        <td>
                                            <a target="_blank" href="http://quote.eastmoney.com/hk/00700.html">00700</a>
                                        </td>
                                        <td>
                                            <a target="_blank" href="http://quote.eastmoney.com/hk/00700.html">腾讯控股</a>
                                        </td>
                                        <td><span>104.60万</span></td>
                                        <td><span>610.500</span></td>
                                        <td><span>605.000</span></td>
                                        <td><span>608.025</span></td>
                                        <td><span>63599.39万</span></td>
                                        <td><span>2025-12-05</span></td>
                                    </tr>
                                    <tr>
                                        <td><span>6</span></td>
                                        <td>
                                            <a target="_blank" href="http://quote.eastmoney.com/hk/00700.html">00700</a>
                                        </td>
                                        <td>
                                            <a target="_blank" href="http://quote.eastmoney.com/hk/00700.html">腾讯控股</a>
                                        </td>
                                        <td><span>104.40万</span></td>
                                        <td><span>613.000</span></td>
                                        <td><span>605.000</span></td>
                                        <td><span>608.920</span></td>
                                        <td><span>63571.29万</span></td>
                                        <td><span>2025-12-04</span></td>
                                    </tr>
                                    <tr>
                                        <td><span>7</span></td>
                                        <td>
                                            <a target="_blank" href="http://quote.eastmoney.com/hk/00700.html">00700</a>
                                        </td>
                                        <td>
                                            <a target="_blank" href="http://quote.eastmoney.com/hk/00700.html">腾讯控股</a>
                                        </td>
                                        <td><span>104.00万</span></td>
                                        <td><span>616.000</span></td>
                                        <td><span>609.000</span></td>
                                        <td><span>611.178</span></td>
                                        <td><span>63562.47万</span></td>
                                        <td><span>2025-12-03</span></td>
                                    </tr>
                                    <tr>
                                        <td><span>8</span></td>
                                        <td>
                                            <a target="_blank" href="http://quote.eastmoney.com/hk/00700.html">00700</a>
                                        </td>
                                        <td>
                                            <a target="_blank" href="http://quote.eastmoney.com/hk/00700.html">腾讯控股</a>
                                        </td>
                                        <td><span>102.80万</span></td>
                                        <td><span>625.500</span></td>
                                        <td><span>615.500</span></td>
                                        <td><span>618.595</span></td>
                                        <td><span>63591.56万</span></td>
                                        <td><span>2025-12-02</span></td>
                                    </tr>
                                    <tr>
                                        <td><span>9</span></td>
                                        <td>
                                            <a target="_blank" href="http://quote.eastmoney.com/hk/00700.html">00700</a>
                                        </td>
                                        <td>
                                            <a target="_blank" href="http://quote.eastmoney.com/hk/00700.html">腾讯控股</a>
                                        </td>
                                        <td><span>102.90万</span></td>
                                        <td><span>623.000</span></td>
                                        <td><span>613.000</span></td>
                                        <td><span>618.010</span></td>
                                        <td><span>63593.24万</span></td>
                                        <td><span>2025-12-01</span></td>
                                    </tr>
                                    <tr>
                                        <td><span>10</span></td>
                                        <td>
                                            <a target="_blank" href="http://quote.eastmoney.com/hk/00700.html">00700</a>
                                        </td>
                                        <td>
                                            <a target="_blank" href="http://quote.eastmoney.com/hk/00700.html">腾讯控股</a>
                                        </td>
                                        <td><span>103.90万</span></td>
                                        <td><span>616.500</span></td>
                                        <td><span>609.000</span></td>
                                        <td><span>611.751</span></td>
                                        <td><span>63560.93万</span></td>
                                        <td><span>2025-11-28</span></td>
                                    </tr>
                                    <tr>
                                        <td><span>11</span></td>
                                        <td>
                                            <a target="_blank" href="http://quote.eastmoney.com/hk/00700.html">00700</a>
                                        </td>
                                        <td>
                                            <a target="_blank" href="http://quote.eastmoney.com/hk/00700.html">腾讯控股</a>
                                        </td>
                                        <td><span>103.60万</span></td>
                                        <td><span>620.000</span></td>
                                        <td><span>609.000</span></td>
                                        <td><span>613.594</span></td>
                                        <td><span>63568.33万</span></td>
                                        <td><span>2025-11-27</span></td>
                                    </tr>
                                    <tr>
                                        <td><span>12</span></td>
                                        <td>
                                            <a target="_blank" href="http://quote.eastmoney.com/hk/00700.html">00700</a>
                                        </td>
                                        <td>
                                            <a target="_blank" href="http://quote.eastmoney.com/hk/00700.html">腾讯控股</a>
                                        </td>
                                        <td><span>102.20万</span></td>
                                        <td><span>629.000</span></td>
                                        <td><span>618.500</span></td>
                                        <td><span>621.976</span></td>
                                        <td><span>63565.95万</span></td>
                                        <td><span>2025-11-26</span></td>
                                    </tr>
                                    <tr>
                                        <td><span>13</span></td>
                                        <td>
                                            <a target="_blank" href="http://quote.eastmoney.com/hk/00700.html">00700</a>
                                        </td>
                                        <td>
                                            <a target="_blank" href="http://quote.eastmoney.com/hk/00700.html">腾讯控股</a>
                                        </td>
                                        <td><span>101.40万</span></td>
                                        <td><span>634.500</span></td>
                                        <td><span>620.500</span></td>
                                        <td><span>626.771</span></td>
                                        <td><span>63554.55万</span></td>
                                        <td><span>2025-11-25</span></td>
                                    </tr>
                                    <tr>
                                        <td><span>14</span></td>
                                        <td>
                                            <a target="_blank" href="http://quote.eastmoney.com/hk/00700.html">00700</a>
                                        </td>
                                        <td>
                                            <a target="_blank" href="http://quote.eastmoney.com/hk/00700.html">腾讯控股</a>
                                        </td>
                                        <td><span>102.20万</span></td>
                                        <td><span>626.500</span></td>
                                        <td><span>613.500</span></td>
                                        <td><span>622.010</span></td>
                                        <td><span>63569.40万</span></td>
                                        <td><span>2025-11-24</span></td>
                                    </tr>
                                    <tr>
                                        <td><span>15</span></td>
                                        <td>
                                            <a target="_blank" href="http://quote.eastmoney.com/hk/00700.html">00700</a>
                                        </td>
                                        <td>
                                            <a target="_blank" href="http://quote.eastmoney.com/hk/00700.html">腾讯控股</a>
                                        </td>
                                        <td><span>104.20万</span></td>
                                        <td><span>614.500</span></td>
                                        <td><span>606.500</span></td>
                                        <td><span>610.233</span></td>
                                        <td><span>63586.24万</span></td>
                                        <td><span>2025-11-21</span></td>
                                    </tr>
                                    <tr>
                                        <td><span>16</span></td>
                                        <td>
                                            <a target="_blank" href="http://quote.eastmoney.com/hk/00700.html">00700</a>
                                        </td>
                                        <td>
                                            <a target="_blank" href="http://quote.eastmoney.com/hk/00700.html">腾讯控股</a>
                                        </td>
                                        <td><span>102.60万</span></td>
                                        <td><span>628.500</span></td>
                                        <td><span>616.000</span></td>
                                        <td><span>619.873</span></td>
                                        <td><span>63598.96万</span></td>
                                        <td><span>2025-11-20</span></td>
                                    </tr>
                                    <tr>
                                        <td><span>17</span></td>
                                        <td>
                                            <a target="_blank" href="http://quote.eastmoney.com/hk/00700.html">00700</a>
                                        </td>
                                        <td>
                                            <a target="_blank" href="http://quote.eastmoney.com/hk/00700.html">腾讯控股</a>
                                        </td>
                                        <td><span>101.80万</span></td>
                                        <td><span>630.500</span></td>
                                        <td><span>619.500</span></td>
                                        <td><span>624.266</span></td>
                                        <td><span>63550.29万</span></td>
                                        <td><span>2025-11-19</span></td>
                                    </tr>
                                    <tr>
                                        <td><span>18</span></td>
                                        <td>
                                            <a target="_blank" href="http://quote.eastmoney.com/hk/00700.html">00700</a>
                                        </td>
                                        <td>
                                            <a target="_blank" href="http://quote.eastmoney.com/hk/00700.html">腾讯控股</a>
                                        </td>
                                        <td><span>101.30万</span></td>
                                        <td><span>640.500</span></td>
                                        <td><span>620.500</span></td>
                                        <td><span>627.445</span></td>
                                        <td><span>63560.20万</span></td>
                                        <td><span>2025-11-18</span></td>
                                    </tr>
                                    <tr>
                                        <td><span>19</span></td>
                                        <td>
                                            <a target="_blank" href="http://quote.eastmoney.com/hk/00700.html">00700</a>
                                        </td>
                                        <td>
                                            <a target="_blank" href="http://quote.eastmoney.com/hk/00700.html">腾讯控股</a>
                                        </td>
                                        <td><span>83.90万</span></td>
                                        <td><span>669.000</span></td>
                                        <td><span>648.000</span></td>
                                        <td><span>655.986</span></td>
                                        <td><span>55037.22万</span></td>
                                        <td><span>2025-10-10</span></td>
                                    </tr>
                                    <tr>
                                        <td><span>20</span></td>
                                        <td>
                                            <a target="_blank" href="http://quote.eastmoney.com/hk/00700.html">00700</a>
                                        </td>
                                        <td>
                                            <a target="_blank" href="http://quote.eastmoney.com/hk/00700.html">腾讯控股</a>
                                        </td>
                                        <td><span>81.60万</span></td>
                                        <td><span>680.500</span></td>
                                        <td><span>666.000</span></td>
                                        <td><span>674.739</span></td>
                                        <td><span>55058.73万</span></td>
                                        <td><span>2025-10-09</span></td>
                                    </tr>
                                    <tr>
                                        <td><span>21</span></td>
                                        <td>
                                            <a target="_blank" href="http://quote.eastmoney.com/hk/00700.html">00700</a>
                                        </td>
                                        <td>
                                            <a target="_blank" href="http://quote.eastmoney.com/hk/00700.html">腾讯控股</a>
                                        </td>
                                        <td><span>81.70万</span></td>
                                        <td><span>680.000</span></td>
                                        <td><span>669.500</span></td>
                                        <td><span>674.405</span></td>
                                        <td><span>55098.91万</span></td>
                                        <td><span>2025-10-08</span></td>
                                    </tr>
                                    <tr>
                                        <td><span>22</span></td>
                                        <td>
                                            <a target="_blank" href="http://quote.eastmoney.com/hk/00700.html">00700</a>
                                        </td>
                                        <td>
                                            <a target="_blank" href="http://quote.eastmoney.com/hk/00700.html">腾讯控股</a>
                                        </td>
                                        <td><span>81.50万</span></td>
                                        <td><span>682.000</span></td>
                                        <td><span>670.500</span></td>
                                        <td><span>675.267</span></td>
                                        <td><span>55034.27万</span></td>
                                        <td><span>2025-10-06</span></td>
                                    </tr>
                                    <tr>
                                        <td><span>23</span></td>
                                        <td>
                                            <a target="_blank" href="http://quote.eastmoney.com/hk/00700.html">00700</a>
                                        </td>
                                        <td>
                                            <a target="_blank" href="http://quote.eastmoney.com/hk/00700.html">腾讯控股</a>
                                        </td>
                                        <td><span>81.70万</span></td>
                                        <td><span>680.000</span></td>
                                        <td><span>670.500</span></td>
                                        <td><span>673.696</span></td>
                                        <td><span>55040.94万</span></td>
                                        <td><span>2025-10-03</span></td>
                                    </tr>
                                    <tr>
                                        <td><span>24</span></td>
                                        <td>
                                            <a target="_blank" href="http://quote.eastmoney.com/hk/00700.html">00700</a>
                                        </td>
                                        <td>
                                            <a target="_blank" href="http://quote.eastmoney.com/hk/00700.html">腾讯控股</a>
                                        </td>
                                        <td><span>81.20万</span></td>
                                        <td><span>683.000</span></td>
                                        <td><span>666.000</span></td>
                                        <td><span>677.704</span></td>
                                        <td><span>55029.53万</span></td>
                                        <td><span>2025-10-02</span></td>
                                    </tr>
                                    <tr>
                                        <td><span>25</span></td>
                                        <td>
                                            <a target="_blank" href="http://quote.eastmoney.com/hk/00700.html">00700</a>
                                        </td>
                                        <td>
                                            <a target="_blank" href="http://quote.eastmoney.com/hk/00700.html">腾讯控股</a>
                                        </td>
                                        <td><span>83.20万</span></td>
                                        <td><span>666.500</span></td>
                                        <td><span>657.500</span></td>
                                        <td><span>662.212</span></td>
                                        <td><span>55096.02万</span></td>
                                        <td><span>2025-09-30</span></td>
                                    </tr>
                                    <tr>
                                        <td><span>26</span></td>
                                        <td>
                                            <a target="_blank" href="http://quote.eastmoney.com/hk/00700.html">00700</a>
                                        </td>
                                        <td>
                                            <a target="_blank" href="http://quote.eastmoney.com/hk/00700.html">腾讯控股</a>
                                        </td>
                                        <td><span>83.70万</span></td>
                                        <td><span>664.000</span></td>
                                        <td><span>648.000</span></td>
                                        <td><span>657.968</span></td>
                                        <td><span>55071.89万</span></td>
                                        <td><span>2025-09-29</span></td>
                                    </tr>
                                    <tr>
                                        <td><span>27</span></td>
                                        <td>
                                            <a target="_blank" href="http://quote.eastmoney.com/hk/00700.html">00700</a>
                                        </td>
                                        <td>
                                            <a target="_blank" href="http://quote.eastmoney.com/hk/00700.html">腾讯控股</a>
                                        </td>
                                        <td><span>85.00万</span></td>
                                        <td><span>652.500</span></td>
                                        <td><span>640.000</span></td>
                                        <td><span>647.437</span></td>
                                        <td><span>55032.18万</span></td>
                                        <td><span>2025-09-26</span></td>
                                    </tr>
                                    <tr>
                                        <td><span>28</span></td>
                                        <td>
                                            <a target="_blank" href="http://quote.eastmoney.com/hk/00700.html">00700</a>
                                        </td>
                                        <td>
                                            <a target="_blank" href="http://quote.eastmoney.com/hk/00700.html">腾讯控股</a>
                                        </td>
                                        <td><span>84.40万</span></td>
                                        <td><span>658.500</span></td>
                                        <td><span>644.000</span></td>
                                        <td><span>652.015</span></td>
                                        <td><span>55030.08万</span></td>
                                        <td><span>2025-09-25</span></td>
                                    </tr>
                                    <tr>
                                        <td><span>29</span></td>
                                        <td>
                                            <a target="_blank" href="http://quote.eastmoney.com/hk/00700.html">00700</a>
                                        </td>
                                        <td>
                                            <a target="_blank" href="http://quote.eastmoney.com/hk/00700.html">腾讯控股</a>
                                        </td>
                                        <td><span>85.80万</span></td>
                                        <td><span>650.500</span></td>
                                        <td><span>628.500</span></td>
                                        <td><span>641.649</span></td>
                                        <td><span>55053.52万</span></td>
                                        <td><span>2025-09-24</span></td>
                                    </tr>
                                    <tr>
                                        <td><span>30</span></td>
                                        <td>
                                            <a target="_blank" href="http://quote.eastmoney.com/hk/00700.html">00700</a>
                                        </td>
                                        <td>
                                            <a target="_blank" href="http://quote.eastmoney.com/hk/00700.html">腾讯控股</a>
                                        </td>
                                        <td><span>86.70万</span></td>
                                        <td><span>643.000</span></td>
                                        <td><span>627.000</span></td>
                                        <td><span>634.802</span></td>
                                        <td><span>55037.30万</span></td>
                                        <td><span>2025-09-23</span></td>
                                    </tr>
                                    <tr>
                                        <td><span>31</span></td>
                                        <td>
                                            <a target="_blank" href="http://quote.eastmoney.com/hk/00700.html">00700</a>
                                        </td>
                                        <td>
                                            <a target="_blank" href="http://quote.eastmoney.com/hk/00700.html">腾讯控股</a>
                                        </td>
                                        <td><span>86.20万</span></td>
                                        <td><span>643.000</span></td>
                                        <td><span>635.000</span></td>
                                        <td><span>638.517</span></td>
                                        <td><span>55040.13万</span></td>
                                        <td><span>2025-09-22</span></td>
                                    </tr>
                                    <tr>
                                        <td><span>32</span></td>
                                        <td>
                                            <a target="_blank" href="http://quote.eastmoney.com/hk/00700.html">00700</a>
                                        </td>
                                        <td>
                                            <a target="_blank" href="http://quote.eastmoney.com/hk/00700.html">腾讯控股</a>
                                        </td>
                                        <td><span>85.70万</span></td>
                                        <td><span>647.000</span></td>
                                        <td><span>638.500</span></td>
                                        <td><span>642.691</span></td>
                                        <td><span>55078.61万</span></td>
                                        <td><span>2025-09-19</span></td>
                                    </tr>
                                    <tr>
                                        <td><span>33</span></td>
                                        <td>
                                            <a target="_blank" href="http://quote.eastmoney.com/hk/00700.html">00700</a>
                                        </td>
                                        <td>
                                            <a target="_blank" href="http://quote.eastmoney.com/hk/00700.html">腾讯控股</a>
                                        </td>
                                        <td><span>84.80万</span></td>
                                        <td><span>664.000</span></td>
                                        <td><span>636.000</span></td>
                                        <td><span>648.975</span></td>
                                        <td><span>55033.11万</span></td>
                                        <td><span>2025-09-18</span></td>
                                    </tr>
                                    <tr>
                                        <td><span>34</span></td>
                                        <td>
                                            <a target="_blank" href="http://quote.eastmoney.com/hk/00700.html">00700</a>
                                        </td>
                                        <td>
                                            <a target="_blank" href="http://quote.eastmoney.com/hk/00700.html">腾讯控股</a>
                                        </td>
                                        <td><span>83.90万</span></td>
                                        <td><span>663.500</span></td>
                                        <td><span>645.500</span></td>
                                        <td><span>656.593</span></td>
                                        <td><span>55088.19万</span></td>
                                        <td><span>2025-09-17</span></td>
                                    </tr>
                                    <tr>
                                        <td><span>35</span></td>
                                        <td>
                                            <a target="_blank" href="http://quote.eastmoney.com/hk/00700.html">00700</a>
                                        </td>
                                        <td>
                                            <a target="_blank" href="http://quote.eastmoney.com/hk/00700.html">腾讯控股</a>
                                        </td>
                                        <td><span>85.30万</span></td>
                                        <td><span>649.000</span></td>
                                        <td><span>641.000</span></td>
                                        <td><span>645.462</span></td>
                                        <td><span>55057.88万</span></td>
                                        <td><span>2025-09-16</span></td>
                                    </tr>
                                    <tr>
                                        <td><span>36</span></td>
                                        <td>
                                            <a target="_blank" href="http://quote.eastmoney.com/hk/00700.html">00700</a>
                                        </td>
                                        <td>
                                            <a target="_blank" href="http://quote.eastmoney.com/hk/00700.html">腾讯控股</a>
                                        </td>
                                        <td><span>85.60万</span></td>
                                        <td><span>648.000</span></td>
                                        <td><span>637.500</span></td>
                                        <td><span>643.552</span></td>
                                        <td><span>55088.04万</span></td>
                                        <td><span>2025-09-15</span></td>
                                    </tr>
                                    <tr>
                                        <td><span>37</span></td>
                                        <td>
                                            <a target="_blank" href="http://quote.eastmoney.com/hk/00700.html">00700</a>
                                        </td>
                                        <td>
                                            <a target="_blank" href="http://quote.eastmoney.com/hk/00700.html">腾讯控股</a>
                                        </td>
                                        <td><span>85.20万</span></td>
                                        <td><span>649.000</span></td>
                                        <td><span>642.000</span></td>
                                        <td><span>646.052</span></td>
                                        <td><span>55043.65万</span></td>
                                        <td><span>2025-09-12</span></td>
                                    </tr>
                                    <tr>
                                        <td><span>38</span></td>
                                        <td>
                                            <a target="_blank" href="http://quote.eastmoney.com/hk/00700.html">00700</a>
                                        </td>
                                        <td>
                                            <a target="_blank" href="http://quote.eastmoney.com/hk/00700.html">腾讯控股</a>
                                        </td>
                                        <td><span>87.40万</span></td>
                                        <td><span>633.000</span></td>
                                        <td><span>624.000</span></td>
                                        <td><span>629.840</span></td>
                                        <td><span>55048.01万</span></td>
                                        <td><span>2025-09-11</span></td>
                                    </tr>
                                    <tr>
                                        <td><span>39</span></td>
                                        <td>
                                            <a target="_blank" href="http://quote.eastmoney.com/hk/00700.html">00700</a>
                                        </td>
                                        <td>
                                            <a target="_blank" href="http://quote.eastmoney.com/hk/00700.html">腾讯控股</a>
                                        </td>
                                        <td><span>86.60万</span></td>
                                        <td><span>638.500</span></td>
                                        <td><span>628.500</span></td>
                                        <td><span>635.590</span></td>
                                        <td><span>55042.11万</span></td>
                                        <td><span>2025-09-10</span></td>
                                    </tr>
                                    <tr>
                                        <td><span>40</span></td>
                                        <td>
                                            <a target="_blank" href="http://quote.eastmoney.com/hk/00700.html">00700</a>
                                        </td>
                                        <td>
                                            <a target="_blank" href="http://quote.eastmoney.com/hk/00700.html">腾讯控股</a>
                                        </td>
                                        <td><span>88.30万</span></td>
                                        <td><span>627.500</span></td>
                                        <td><span>619.000</span></td>
                                        <td><span>624.000</span></td>
                                        <td><span>55099.18万</span></td>
                                        <td><span>2025-09-09</span></td>
                                    </tr>
                                    <tr>
                                        <td><span>41</span></td>
                                        <td>
                                            <a target="_blank" href="http://quote.eastmoney.com/hk/00700.html">00700</a>
                                        </td>
                                        <td>
                                            <a target="_blank" href="http://quote.eastmoney.com/hk/00700.html">腾讯控股</a>
                                        </td>
                                        <td><span>89.70万</span></td>
                                        <td><span>618.500</span></td>
                                        <td><span>605.500</span></td>
                                        <td><span>613.738</span></td>
                                        <td><span>55052.28万</span></td>
                                        <td><span>2025-09-08</span></td>
                                    </tr>
                                    <tr>
                                        <td><span>42</span></td>
                                        <td>
                                            <a target="_blank" href="http://quote.eastmoney.com/hk/00700.html">00700</a>
                                        </td>
                                        <td>
                                            <a target="_blank" href="http://quote.eastmoney.com/hk/00700.html">腾讯控股</a>
                                        </td>
                                        <td><span>91.30万</span></td>
                                        <td><span>608.500</span></td>
                                        <td><span>597.000</span></td>
                                        <td><span>603.245</span></td>
                                        <td><span>55076.23万</span></td>
                                        <td><span>2025-09-05</span></td>
                                    </tr>
                                    <tr>
                                        <td><span>43</span></td>
                                        <td>
                                            <a target="_blank" href="http://quote.eastmoney.com/hk/00700.html">00700</a>
                                        </td>
                                        <td>
                                            <a target="_blank" href="http://quote.eastmoney.com/hk/00700.html">腾讯控股</a>
                                        </td>
                                        <td><span>92.50万</span></td>
                                        <td><span>605.000</span></td>
                                        <td><span>591.000</span></td>
                                        <td><span>595.226</span></td>
                                        <td><span>55058.44万</span></td>
                                        <td><span>2025-09-04</span></td>
                                    </tr>
                                    <tr>
                                        <td><span>44</span></td>
                                        <td>
                                            <a target="_blank" href="http://quote.eastmoney.com/hk/00700.html">00700</a>
                                        </td>
                                        <td>
                                            <a target="_blank" href="http://quote.eastmoney.com/hk/00700.html">腾讯控股</a>
                                        </td>
                                        <td><span>91.60万</span></td>
                                        <td><span>612.500</span></td>
                                        <td><span>596.500</span></td>
                                        <td><span>601.217</span></td>
                                        <td><span>55071.50万</span></td>
                                        <td><span>2025-09-03</span></td>
                                    </tr>
                                    <tr>
                                        <td><span>45</span></td>
                                        <td>
                                            <a target="_blank" href="http://quote.eastmoney.com/hk/00700.html">00700</a>
                                        </td>
                                        <td>
                                            <a target="_blank" href="http://quote.eastmoney.com/hk/00700.html">腾讯控股</a>
                                        </td>
                                        <td><span>91.30万</span></td>
                                        <td><span>608.000</span></td>
                                        <td><span>599.500</span></td>
                                        <td><span>602.798</span></td>
                                        <td><span>55035.42万</span></td>
                                        <td><span>2025-09-02</span></td>
                                    </tr>
                                    <tr>
                                        <td><span>46</span></td>
                                        <td>
                                            <a target="_blank" href="http://quote.eastmoney.com/hk/00700.html">00700</a>
                                        </td>
                                        <td>
                                            <a target="_blank" href="http://quote.eastmoney.com/hk/00700.html">腾讯控股</a>
                                        </td>
                                        <td><span>91.00万</span></td>
                                        <td><span>609.500</span></td>
                                        <td><span>601.500</span></td>
                                        <td><span>604.919</span></td>
                                        <td><span>55047.65万</span></td>
                                        <td><span>2025-09-01</span></td>
                                    </tr>
                                    <tr>
                                        <td><span>47</span></td>
                                        <td>
                                            <a target="_blank" href="http://quote.eastmoney.com/hk/00700.html">00700</a>
                                        </td>
                                        <td>
                                            <a target="_blank" href="http://quote.eastmoney.com/hk/00700.html">腾讯控股</a>
                                        </td>
                                        <td><span>91.90万</span></td>
                                        <td><span>605.000</span></td>
                                        <td><span>594.500</span></td>
                                        <td><span>598.803</span></td>
                                        <td><span>55030.00万</span></td>
                                        <td><span>2025-08-29</span></td>
                                    </tr>
                                    <tr>
                                        <td><span>48</span></td>
                                        <td>
                                            <a target="_blank" href="http://quote.eastmoney.com/hk/00700.html">00700</a>
                                        </td>
                                        <td>
                                            <a target="_blank" href="http://quote.eastmoney.com/hk/00700.html">腾讯控股</a>
                                        </td>
                                        <td><span>92.70万</span></td>
                                        <td><span>598.500</span></td>
                                        <td><span>590.500</span></td>
                                        <td><span>594.229</span></td>
                                        <td><span>55084.98万</span></td>
                                        <td><span>2025-08-28</span></td>
                                    </tr>
                                    <tr>
                                        <td><span>49</span></td>
                                        <td>
                                            <a target="_blank" href="http://quote.eastmoney.com/hk/00700.html">00700</a>
                                        </td>
                                        <td>
                                            <a target="_blank" href="http://quote.eastmoney.com/hk/00700.html">腾讯控股</a>
                                        </td>
                                        <td><span>90.90万</span></td>
                                        <td><span>614.500</span></td>
                                        <td><span>596.000</span></td>
                                        <td><span>605.375</span></td>
                                        <td><span>55028.60万</span></td>
                                        <td><span>2025-08-27</span></td>
                                    </tr>
                                    <tr>
                                        <td><span>50</span></td>
                                        <td>
                                            <a target="_blank" href="http://quote.eastmoney.com/hk/00700.html">00700</a>
                                        </td>
                                        <td>
                                            <a target="_blank" href="http://quote.eastmoney.com/hk/00700.html">腾讯控股</a>
                                        </td>
                                        <td><span>89.90万</span></td>
                                        <td><span>617.500</span></td>
                                        <td><span>609.500</span></td>
                                        <td><span>612.698</span></td>
                                        <td><span>55081.51万</span></td>
                                        <td><span>2025-08-26</span></td>
                                    </tr>
                        </tbody>
                    </table>
                </div>
            </div>

            

<div class="pagerbox" id="pagination">
    <div class="pager" style="overflow:visible;">
        <!-- 如果页数大于6 -->
            <!-- 生成页数选项卡 -->
            <!-- 如果是首页不显示<上一页> -->
            <!-- 如果当前页与首页间距超过3则用...代替中间页 -->
            <!-- 普通情况当前标签左右各两个标签 -->
            <!-- 当前标签 -->
            <span>1 </span>
            <!-- 当前标签右侧部分 -->
                        <a href="buyback_2.html?code=00700&amp;sdate=&amp;edate=" target="_self">2 </a>
                        <a href="buyback_3.html?code=00700&amp;sdate=&amp;edate=" target="_self">3 </a>
                        <a href="buyback_4.html?code=00700&amp;sdate=&amp;edate=" target="_self">4 </a>
                        <a href="buyback_5.html?code=00700&amp;sdate=&amp;edate=" target="_self">5 </a>
                    <!-- 普通情况 -->
                <!-- 右侧标签不足两个情况 -->
            <!-- 如果当前标签右侧标签超过三个由...代替 -->
                <span style="border: 1px solid #C8D8F2;background: #fff;color: #3669ba;">...</span>
            <!-- 如果是最后一页则不显示下一页 -->
                <a href="buyback_14.html?code=00700&amp;sdate=&amp;edate=" target="_self">14 </a>
                <a href="buyback_2.html?code=00700&amp;sdate=&amp;edate=" target="_self">下一页</a>
            <!-- 如果页数小于6则全部展示，没有下一页和上一页标签 -->
    </div>
</div>


            <div class="pagerbox">数据来源：<a target="_blank" href="http://choice.eastmoney.com/Product/index.html?adid=953" style="text-decoration: underline;">东方财富Choice数据</a></div>
        </div>



    </div>

</div>



    </div>
    <!-- footer-2016 -->
<style>
    .footer2016 ul {list-style: none;margin: 0;padding: 0;}
    .footer2016 a:hover{color:#ff4901 !important;text-decoration: underline !important;}
    .footer2016 .icon, .footer2016 .navlist li a {display: inline-block;}
    .footer2016 .icon {background-image: url(//g1.dfcfw.com/g4/202005/20200513165332.png);background-repeat: no-repeat;}
    .footer2016 {margin: 0 auto;clear: both;width: 1000px;line-height: 1.1;_line-height: 1.2;font-family: simsun;font-size: 12px;border-top: 2px solid #2F5895;}
    .footer2016 .footertg {background-color: #F3F3F3;float: left;width: 100%;padding: 12px 0 0;height: 140px;}
    .footer2016 .footertg a:link, .footer2016 .footertg a:visited {color: #676767;text-decoration: none;}
    .footer2016 .qr {float: left;width: 80px;height: 140px;line-height: 150%;padding: 0 10px 0 8px;}
    .footer2016 .qr .t {font-weight: 700;font-size: 14px;padding-bottom: 10px;}
    .footer2016 .icon_qrem80, .footer2016 .icon_qrjj80 {background-image: url(//g1.dfcfw.com/g2/201607/20160728133707.png);width: 80px;height: 80px;}
    .footer2016 .icon_qrem80 {background-position: 0 -330px;}
    .footer2016 .icon_emwxqr, .footer2016 .icon_jjwxqr {background-image: url(//g1.dfcfw.com/g2/201607/20160728133707.png);width: 86px;height: 106px;}
    .footer2016 .icon_emwxqr {background-position: -90px 0;}
    .footer2016 .ftglist ul li.qrli {position: relative;}
    .footer2016 .ftglist ul li.qrli:hover .icon_qr, .footer2016 .scl-news .name a {display: block;}
    .footer2016 .icon_emwxqr, .footer2016 .icon_jjwxqr {display: none;position: absolute;left: 0;top: 24px;}
    .footer2016 .ftglist {float: left;height: 140px;padding: 0px 10px;}
    .footer2016 .ftglistt {font-size: 14px;font-weight: 700;line-height: 130%;padding-bottom: 6px;text-align: left;}
    .footer2016 .ftglist ul li {padding: 5px 0;color: #676767;text-align: left;}
    .footer2016 .icon_wb {background-position: -24px 0;width: 14px;height: 12px;}
    .footer2016 .icon_wx {background-position: 0 0;width: 14px;height: 11px;}
    .footer2016 .icon_note {background-position: -47px 0;width: 13px;height: 11px;}
    .footer2016 .ftglist .icon {vertical-align: -1px;margin-right: 2px;}
    .footer2016 .footertg a:link, .footer2016 .footertg a:visited {color: #676767;text-decoration: none;}
    .footer2016 .qrl {border-left: 1px solid #ddd;margin-left: 10px;padding-left: 20px;}
    .footer2016 .icon_qrjj80 {background-position: -90px -330px;}
    .footer2016 .footercr {clear: both;text-align: center;line-height: 26px;font-size: 12px;width:1000px;margin: 0 auto;height:26px;overflow:hidden;}
    .footer2016 .icon_icp {background-position: -24px -21px;width: 15px;height: 17px;}
    .footer2016 .footercr .icon {vertical-align: -3px;margin-right: 2px;}
    .footer2016 .icon_pol {background-position: 0 -22px;width: 18px;height: 20px;}
    .footer2016 .footerlinks {background-color: #2F5895;height: 30px;text-align: center;line-height: 30px;}
    .footer2016 .footerlinks a:link, .footer2016 .footerlinks a:visited, .footer2016 .footerlinks a:hover {color: #fff !important;text-decoration: none;margin: 0 14px;}
    .footer2016 .footerbz {text-align: center;padding: 12px 0;}
    .footer2016 .footerbz a {margin: 0 4px;}
    .footer2016 .footer-police {background-position: 0 -112px;width: 110px;height: 40px;}
    .footer2016 .footer-zx110 {background-position: -120px -113px;width: 110px;height: 40px;}
    .footer2016 .footer-shjubao {background-position: 0 -172px;width: 110px;height: 40px;}
    .footer2016 .footer-cxzx {background-position: -120px -174px;width: 40px;height: 40px;}
    .footer2016 .footer-shgs {background-position: -180px -174px;width: 47px;height: 40px;}
    .footer2016 .footer-12377 {background-position: 0 -54px;width: 186px;height: 40px;}
    .footer2016 .footer-yhjb {background-position: 0 -229px;width: 123px;height: 40px;}
    .footer2016 .footer-qrlast {width: 90px;}
    .footer2016 .footer-icon-qihuoqr { background: url(https://g1.dfcfw.com/g4/202303/20230324150231.png);width: 80px;height: 80px;display: inline-block;background-repeat: no-repeat;vertical-align: -5px;}
</style>

<div class="footer2016">
    <div class="footertg">
        <div class="qr">
            <div class="t"><a href="http://acttg.eastmoney.com/pub/web_dfcfsy_dbtg_wzl_01_01_01_1" style="color:#000" target="_blank">东方财富</a></div>
            <a href="http://acttg.eastmoney.com/pub/web_app_dcsy_2wm_01_01_01_0" target="_blank"><em class="icon icon_qrem80"></em></a><br />扫一扫下载APP
        </div>

        <div class="ftglist">
            <div class="ftglistt">东方财富产品</div>
            <ul>
                <li><a href="https://acttg.eastmoney.com/pub/pctg_hskh_act_dfcfwmfb_01_01_01_0" target="_blank">东方财富免费版</a></li>
                <li><a href="https://acttg.eastmoney.com/pub/pctg_hskh_act_dfcfwl2_01_01_01_0" target="_blank">东方财富Level-2</a></li>
                <li><a href="https://www.dfcfw.com/CLB/" target="_blank">东方财富策略版</a></li>
                <li><a href="https://acttg.eastmoney.com/pub/web_dfcfsy_wzl_bottom_02_02_04_1" target="_blank">妙想投研助理</a></li>
                <li><a href="https://choice.eastmoney.com/terminal?adid=web_choice_dcsy_website_02_01_01_0" target="_blank">Choice金融终端</a></li>
            </ul>
        </div>
        <div class="ftglist">
            <div class="ftglistt">证券交易</div>
            <ul>
                <li><a href="https://acttg.eastmoney.com/pub/web_kh_dcsy_dbtkwzl_01_01_01_0" target="_blank">东方财富证券开户</a></li>
                <li><a href="https://jywg.18.cn/Trade/Buy" target="_blank">东方财富在线交易</a></li>
				<li><a href="https://acttg.eastmoney.com/pub/pctg_hskh_act_dfcfzqjy_01_01_01_0"  target="_blank">东方财富证券交易</a></li>
            </ul>
        </div>
        <div class="ftglist">
            <div class="ftglistt">关注东方财富</div>
            <ul>
                <li><a href="http://weibo.com/dfcfw" target="_blank"><em class="icon icon_wb"></em>东方财富网微博</a></li>
                <li class="qrli"><a href="javascript:;" target="_self"><em class="icon icon_wx"></em>东方财富网微信</a><em class="icon icon_qr icon_emwxqr"></em></li>
                <li><a href="http://corp.eastmoney.com/Lianxi_liuyan.asp" target="_blank"><em class="icon icon_note"></em>意见与建议</a></li>
            </ul>
        </div>
        <div class="qr qrl">
            <div class="t"><a href="http://acttg.eastmoney.com/pub/web_ttjjsy_dbtg_wzl_01_01_01_1" style="color:#000" target="_blank">天天基金</a></div>
            <a href="http://js1.eastmoney.com/tg.aspx?ID=4672" target="_blank"><em class="icon icon_qrjj80"></em></a><br />扫一扫下载APP
        </div>
        <div class="ftglist">
            <div class="ftglistt">基金交易</div>
            <ul>
                <li><a href="https://trade6.1234567.com.cn/reg/step1" target="_blank">基金开户</a></li>
                <li><a href="https://trade.1234567.com.cn/login" target="_blank">基金交易</a></li>
                <li><a href="http://huoqibao.1234567.com.cn/" target="_blank">活期宝</a></li>
                <li><a href="http://fund.eastmoney.com/trade/default.html" target="_blank">基金产品</a></li>
                <li><a href="http://fund.eastmoney.com/gslc/" target="_blank">稳健理财</a></li>
            </ul>
        </div>
        <div class="ftglist">
            <div class="ftglistt">关注天天基金</div>
            <ul>
                <li><a href="http://weibo.com/ttfund" target="_blank"><em class="icon icon_wb"></em>天天基金网微博</a></li>
                <li class="qrli"><a href="javascript:;" target="_self"><em class="icon icon_wx"></em>天天基金网微信<em class="icon icon_qr icon_jjwxqr"></em></a></li>
            </ul>
        </div>
        <div class="qr qrl footer-qrlast">
            <div class="t"><a href="https://qs.dfcfw.com/1605" style="color:#000" target="_blank">东方财富期货</a></div>
            <a href="http://acttg.eastmoney.com/pub/web_kh_dcsy_dibudfcfqh_01_01_01_1" target="_blank"><em class="footer-icon-qihuoqr"></em></a><br>扫一扫下载APP
        </div>
        <div class="ftglist">
            <div class="ftglistt">期货交易</div>
            <ul>
                <li><a href="https://qs.dfcfw.com/1606" target="_blank">期货手机开户</a></li>
                <li><a href="https://qs.dfcfw.com/1607" target="_blank">期货电脑开户</a></li>
                <li><a href="https://qs.dfcfw.com/1608" target="_blank">期货官方网站</a></li>
            </ul>
        </div>
    </div>
        <div class="footercr" style="padding-top:8px;">信息网络传播视听节目许可证：0908328号 经营证券期货业务许可证编号：913101046312860336 违法和不良信息举报:021-61278686 举报邮箱：<a target="_self" href="mailto:jubao@eastmoney.com">jubao@eastmoney.com</a></div>
        <div class="footercr" style="padding-bottom:8px;">
            <em class="icon icon_icp"></em>沪ICP证:沪B2-20070217 <a target="_blank" rel="nofollow" href="https://beian.miit.gov.cn/" style="color: #3F3F3F;text-decoration:none;">网站备案号:沪ICP备05006054号-11 </a> <a target="_blank" rel="nofollow" href="http://www.beian.gov.cn/portal/registerSystemInfo?recordcode=31010402000120" target="_blank" style="color: #3F3F3F;text-decoration:none;"><em class="icon icon_pol"></em>沪公网安备 31010402000120号</a> 版权所有:东方财富网 <span class="yjyfk">意见与建议:4000300059/952500</span>
        </div>
    <div class="footerlinks">
			<a href="http://about.eastmoney.com" target="_blank" rel="nofollow">关于我们</a>
            <a href="https://about.eastmoney.com/about/sdindex" target="_blank" rel="nofollow">可持续发展</a>
			<a href="http://emhd2.eastmoney.com/market" target="_blank" rel="nofollow">广告服务</a>
			<a href="http://about.eastmoney.com/home/contact" target="_blank" rel="nofollow">联系我们</a>
			<a href="https://zhaopin.eastmoney.com/" target="_blank" rel="nofollow">诚聘英才</a>
			<a href="http://about.eastmoney.com/home/legal" target="_blank" rel="nofollow">法律声明</a>
            <a href="http://about.eastmoney.com/home/conceal" target="_blank" rel="nofollow">隐私保护</a>
			<a href="http://about.eastmoney.com/home/parper" target="_blank" rel="nofollow">征稿启事</a>
			<a href="http://about.eastmoney.com/home/links" target="_blank" rel="nofollow">友情链接</a>
    </div>
    <div class="footerbz">
        <img src="//g1.dfcfw.com/g3/201905/20190531140719.png" title="亲爱的市民朋友，上海警方反诈劝阻电
话“962110”系专门针对避免您财产被
骗受损而设，请您一旦收到来电，立即
接听。" style="vertical-align: bottom;">
        <span class="icon footer-police" title="上海网警网络110" style="position: relative; margin: 0 4px;"></span>
        <span class="icon footer-zx110" title="网络社会征信网" style="position: relative;margin: 0 4px;"></span>
        <a rel="nofollow" href="http://www.shjbzx.cn/" class="icon footer-shjubao" title="上海违法和违规信息举报中心" target="_blank"></a>
        <a rel="nofollow" href="http://www.12377.cn" class="icon footer-12377" title="中国互联网违法和不良信息举报中心" target="_blank"></a>
	</div>
</div>

<script>
    if(document.all && !window.XMLHttpRequest){
        $(".qrli").hover(function(){
            $(".icon_qr",this).show();
        },function(){
            $(".icon_qr",this).hide();
        });
    }
</script>
</body>
</html>
<script src="//emres.dfcfw.com/public/js/websitecommand.js" charset="utf-8"></script>
<script src="//emres.dfcfw.com/common/js/jquery.1.8.3.min.js"></script>
<script src="//emcharts.dfcfw.com/suggest/stocksuggest2017.min.js" charset="utf-8"></script>

    <script src="//emres.dfcfw.com/common/My97DatePickerV2/WdatePicker.js"></script>
    <script>
        function getQueryString(name) {
            var reg = new RegExp("(^|&)" + name + "=([^&]*)(&|$)", "i");
            var r = window.location.search.substr(1).match(reg);
            if (r != null) return unescape(r[2]); return null;
        }

        function inquiry(code) {
            if ($('#StockCode').val()) {
                code = $('#StockCode').val()
            } else {
                code = code || '';
            }
            var sdate = $('#sdate').val() || '';
            var edate = $('#edate').val() || '';
            var url = "/buyback.html?code=" + code + "&sdate=" + sdate + "&edate=" + edate;
            window.open(url, "_self");
            return false;
        }




        var newsuggest = new suggest2017({ //新建实例
            inputid: 'StockCode', //参数部分
            placeholder: '输代码、名称或简拼',
            showblank: false,
            modules: ["stock"],
            filter: {
                securitytype: '6,19'
            },
            offset: {
                left: -170,
                top: 0
            },
            onConfirmStock: function (result) {
                var code = result.stock.Code;
                $('#StockCode').val(code)
                inquiry(code)
                return false;
            },
            onSubmit: function (result) {
                var code = result.key;

                inquiry(code)
                return false;
            }
        })

        $(function () {
            $("#dateBtn").click(function () {
                inquiry();
            })

            $('#StockCode').val(getQueryString('code') || '');
            $('#sdate').val(getQueryString('sdate') || '');
            $('#edate').val(getQueryString('edate') || '');
        })
    </script>

<script src="//emres.dfcfw.com/public/js/topnav.js"></script>

<script src="//emcharts.dfcfw.com/newsts/newsts.min.js" charset="utf-8"></script>
<script src="//emcharts.dfcfw.com/pr3/prod/personalrecommend3.min.js"></script>
<script src="//emcharts.dfcfw.com/emsider/prod/emsider.min.js"></script>
    <script>EMSider();</script>

<script src="//emcharts.dfcfw.com/usercollect/usercollect.min.js"></script>
    <script>
    var emtj_isUpload = 1;
    var emtj_pageId = 112102302944;
    var emtj_logSet = "1111111111";
    var emtj_sampleRate = 1;
    </script>
<script src="https://bdstatics.eastmoney.com/web/prd/jump_tracker.js" charset="utf-8"></script>
<script type="text/javascript" src="//emcharts.dfcfw.com/websitepagefilter/websitepagefilter.js" charset="utf-8"></script>