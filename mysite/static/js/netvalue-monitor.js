
var test_row = ' ';


function initTable(){

    simulateStockTable = $("#simulate_stock_strategy")
    simulateFutureTable = $("#simulate_future_strategy")
    simulateOptionTable = $("#simulate_option_strategy")


    realStockTable = $("#real_stock_strategy")
    accountTable = $("#account_name_summary")

    //console.log($("#table_summary"))
    accountTable.on('click-row.bs.table', function (e, row, $element) {
        $($element).siblings().removeClass('warning');
        $($element).addClass('warning');
        $('.success').css("background-color","#ffffff");
    });
    realStockTable.on('click-row.bs.table', function (e, row, $element) {
        $($element).siblings().removeClass('warning');
        $($element).addClass('warning');
        $('.success').css("background-color","#ffffff");
    });
    simulateOptionTable.on('click-row.bs.table', function (e, row, $element) {
        $($element).siblings().removeClass('warning');
        $($element).addClass('warning');
        $('.success').css("background-color","#ffffff");
    });
    simulateStockTable.on('click-row.bs.table', function (e, row, $element) {
        $($element).siblings().removeClass('warning');
        $($element).addClass('warning');
        $('.success').css("background-color","#ffffff");
    });
    simulateFutureTable.on('click-row.bs.table', function (e, row, $element) {
        $($element).siblings().removeClass('warning');
        $($element).addClass('warning');
        $('.success').css("background-color","#ffffff");
    });
    accountTable.on('click-cell.bs.table', function(e, value, row, $element){
        test_row = row + '';
        $("#net_value_title").text( test_row +'策略净值图');

        $("#net_value_panel").show();
        $("#net_detail").bootstrapTable('refresh',{url: "../static/tableData/HistoryNetValue/" + row + "_nv_detail.json"});
        showNV_Plot(test_row);

        });
    simulateStockTable.on('click-cell.bs.table', function(e, value, row, $element){
        test_row = row + '';
        $("#net_value_title").text( test_row +'策略净值图');
        $("#net_value_panel").show();
        $("#net_detail").bootstrapTable('refresh',{url: "../static/tableData/HistoryNetValue/" + row + "_nv_detail.json"});
        showNV_Plot(test_row);

        });
    simulateFutureTable.on('click-cell.bs.table', function(e, value, row, $element){
        test_row = row + '';
        $("#net_value_title").text( test_row +'策略净值图');
        $("#net_value_panel").show();
        $("#net_detail").bootstrapTable('refresh',{url: "../static/tableData/HistoryNetValue/" + row + "_nv_detail.json"});
        showNV_Plot(test_row);

        });
    simulateOptionTable.on('click-cell.bs.table', function(e, value, row, $element){
        test_row = row + '';
        $("#net_value_title").text( test_row +'策略净值图');
        $("#net_value_panel").show();
        $("#net_detail").bootstrapTable('refresh',{url: "../static/tableData/HistoryNetValue/" + row + "_nv_detail.json"});
        showNV_Plot(test_row);

        });
    realStockTable.on('click-cell.bs.table', function(e, value, row, $element){
        //alert( "Value: " + row);
        // load detail table according to sector name
        //$("#test_div").text(row)
        test_row = row + '';
//        $("#net_value_title").text( test_row +'策略净值图');
        $("#net_value_title").text( '另类投资产品净值图');

        $("#net_value_panel").show();
        $("#net_detail").bootstrapTable('refresh',{url: "../static/tableData/HistoryNetValue/" + row + "_nv_detail.json"});
        showNV_Plot(test_row);
    });

    function showNV_Plot(test_row){

    var index_url_path = "../static/tableData/HistoryNetValue/shanghai_tsdata.json";
    var hushen300_url_path = "../static/tableData/HistoryNetValue/hushen300_tsdata.json";
    var cyb_url_path = "../static/tableData/HistoryNetValue/cyb_tsdata.json";

    var shanghai_index = [];
    $.getJSON(index_url_path,function (index_data) {

       var dataArrays = index_data;
       var tsdata = dataArrays.ts_index;
       var tsdate = dataArrays.ts_date;
//       var tsIndex = dataArrays.ts_index;

       for(i=0;i<tsdate.length;i++){
            nv = tsdata[i];
            trading_date = tsdate[i];
            shanghai_index.push([trading_date,nv]);
	    }

	  });

    var hushen300_index = [];
    $.getJSON(hushen300_url_path,function (index_data) {

       var dataArrays = index_data;
       var tsdata = dataArrays.ts_index;
       var tsdate = dataArrays.ts_date;
//       var tsIndex = dataArrays.ts_index;

       for(i=0;i<tsdate.length;i++){
            nv = tsdata[i];
            trading_date = tsdate[i];
            hushen300_index.push([trading_date,nv]);
	    }

	  });

    var cyb_index = [];
    $.getJSON(cyb_url_path,function (index_data) {

       var dataArrays = index_data;
       var tsdata = dataArrays.ts_index;
       var tsdate = dataArrays.ts_date;
//       var tsIndex = dataArrays.ts_index;

       for(i=0;i<tsdate.length;i++){
            nv = tsdata[i];
            trading_date = tsdate[i];
            cyb_index.push([trading_date,nv]);
	    }

	  });

    var url_path = "../static/tableData/HistoryNetValue/" + test_row + "_tsdata.json";

    $.getJSON(url_path,function (data) {

       var dataArrays = data;
       var tsdata = dataArrays.ts_data;
       var tsdate = dataArrays.ts_date;
       var tsCap = dataArrays.ts_capital;
       var current_amount = dataArrays.amount;

	   var startDate = tsdate[0];
	   var endDate = tsdate[tsdate.length-1];


       var origin_strategy_data = new Array();
       var completion_strategy_data= [];
       var shanghai_index_selected = [];
       var hushen300_index_selected = [];
       var cyb_index_selected = [];
       var timeXaxis = [];
       var first_shanghai_index;


       for(i=0;i<tsdate.length;i++){
            nv = tsdata[i];
            trading_date = tsdate[i];
            origin_strategy_data[trading_date] = nv;
	    }
//	    console.log("初始策略净值信息")
//        console.log(origin_strategy_data)

//	   根据策略净值数据与指数数据，补全缺失的策略净值
       for(i=0;i<shanghai_index.length;i++){
            if(shanghai_index[i][0] >= startDate && shanghai_index[0] <= endDate){
                if(shanghai_index[i][0] == startDate ){
                    first_shanghai_index = shanghai_index[i][1];
                }
                shanghai_index_selected.push([shanghai_index[i][0],shanghai_index[i][1] / first_shanghai_index]);
                if(shanghai_index[i][0] == endDate ){
                    break;
                }
            }
       }
       for(i=0;i<hushen300_index.length;i++){
            if(hushen300_index[i][0] >= startDate && hushen300_index[0] <= endDate){
                if(hushen300_index[i][0] == startDate ){
                    first_hushen300_index = hushen300_index[i][1];
                }
                hushen300_index_selected.push([hushen300_index[i][0], hushen300_index[i][1] / first_hushen300_index]);
                if(hushen300_index[i][0] == endDate ){
                    break;
                }
            }
       }
       for(i=0;i<cyb_index.length;i++){
            if(cyb_index[i][0] >= startDate && cyb_index[0] <= endDate){
                if(cyb_index[i][0] == startDate ){
                    first_cyb_index = cyb_index[i][1];
                }
                cyb_index_selected.push([cyb_index[i][0], cyb_index[i][1] / first_cyb_index]);
                if(cyb_index[i][0] == endDate ){
                    break;
                }
            }
       }

//       console.log("筛选之后的创业板指数：");
//       console.log(cyb_index_selected);

//       补全策略数据缺失的时间
       for(i=0;i<shanghai_index_selected.length;i++){
            var trading_date = shanghai_index_selected[i][0];           // 今天交易日期
            if(i!=0){
                var last_trading_date = shanghai_index_selected[i-1][0];
            }else{
                var last_trading_date = shanghai_index_selected[i][0];
            }

            if(Object.keys(origin_strategy_data).includes(trading_date)){
                completion_strategy_data.push([shanghai_index_selected[i][0],origin_strategy_data[trading_date]]);
            }else{
                origin_strategy_data[trading_date] = origin_strategy_data[last_trading_date]
                completion_strategy_data.push([trading_date,origin_strategy_data[last_trading_date]])
            }
       }


//    var timestamp = new Date(date).getTime();
//    console.log(timestamp);

        var completion_strategy_timestamp = [];
        var shanghai_index_timestamp = [];
        var hushen300_index_timestamp = [];
        var cyb_index_timestamp = [];

        for(i=0;i<completion_strategy_data.length;i++){
            var trading_date = shanghai_index_selected[i][0];           // 今天交易日期
            var timestamp = new Date(trading_date).getTime();
            completion_strategy_timestamp.push([timestamp,completion_strategy_data[i][1]]);
            shanghai_index_timestamp.push([timestamp,shanghai_index_selected[i][1]]);
            hushen300_index_timestamp.push([timestamp,hushen300_index_selected[i][1]]);
            cyb_index_timestamp.push([timestamp,cyb_index_selected[i][1]]);

        }




       var chart = {
          zoomType: 'x'
       };


       function sharpRatio(tsdata){
           var sum = 0;
           var length = tsdata.length;
           var r_length = length-1;

           var temp = new Array(r_length);

           for (var j = 0; j < r_length; j++){
               var return_rate = (tsdata[j+1] - tsdata[j]) / tsdata[j];
               temp[j] = return_rate;

           }
           for (var i = 0; i < temp.length; i++){
               sum += temp[i];
           }
           var avg = sum/temp.length;
           var deviation = 0;

           for(var i=0;i<temp.length;i++){
               deviation += Math.pow(temp[i] - avg , 2) / r_length;
           }
           std = Math.sqrt(deviation)
           return (((avg-0.02/365)/std)*Math.sqrt(250)).toFixed(2);
       };
       function toPercent(point){
            var str=Number(point*100).toFixed(2);
            str+="%";
            return str;
        }
       function year_return(tsdata){
           var year_rr = Math.pow((tsdata[tsdata.length-1] / tsdata[0]),(250/tsdata.length)) - 1;
           return toPercent(year_rr.toFixed(3));

       }
       function maxLoss(tsdata){
           var max_loss = 0;
           var exist_max = tsdata[0];
           var change = 0;
           for(var i=1; i <tsdata.length; i++){

               change = (tsdata[i] - exist_max) /exist_max;
               if (change < max_loss){
                   max_loss = change;
               }
               if (tsdata[i] >= exist_max){
                   exist_max = tsdata[i];
               }
           }
           return toPercent((max_loss*(-1)).toFixed(5));
       }

       var NetValue = tsdata[tsdata.length-1].toFixed(4);
       var strng_netValue = "净值:" + NetValue + "\xa0\xa0";

       var initialCapital = (current_amount / 10000).toFixed(2);
       var string_initCap = "份额:" + initialCapital + "万\xa0\xa0";
       var sr = sharpRatio(tsdata);
       var string_sr = "SharpRatio:" + sr + "\xa0\xa0";
       var year_rr = year_return(tsdata);
       var string_yrr = "\tYearReturn:" + year_rr + "\xa0\xa0";
       var max_loss = maxLoss(tsdata);
       var str_max_l = "\tMaxLoss:" + max_loss + "\xa0\xa0";

       var title = {
          text: strng_netValue + string_yrr + string_sr +  str_max_l
//          text: strng_netValue + string_yrr + string_sr +  str_max_l  +  string_initCap

       };


       var yAxis =
       {
          style: {
             color: '#4572A7'
          },
          title:{
             text: '   '
          },
          labels: {
            formatter: function () {
                return (this.value > 0 ? ' + ' : '') + this.value + '%';
            }
          }
       };

       var credits =  {
            enabled:false
        };

       var plotOptions = {

          line: {
             compare: 'percent',
             color: 'red',
             marker: {
                radius: 2
             },
             lineWidth: 1,
             states: {
                hover: {
                   lineWidth: 1
                }
             },
             threshold: null
          }
       };

       var legend = {
			align: 'center',
			verticalAlign: 'bottom',
			x: 0,
			y: 0,
			enabled: true
		};


       var series= [{
          color: '#D1283B',
          name: '策略净值',
//          pointStart: Date.UTC(2019, 7, 1),
          data: completion_strategy_timestamp,
          tooltip: {
              valueDecimals: 3
          }

          },{
          name: '上证指数',
//          name: '沪深300',

          color: '#2AA6AC',
//          pointStart: Date.UTC(2019, 7, 1),
          data: shanghai_index_timestamp,
          tooltip: {
              valueDecimals: 3
          }

          }
          ,{
//          name: '上证指数',
          name: '沪深300',

          color: 'green',
//          pointStart: Date.UTC(2019, 7, 1),
          data: hushen300_index_timestamp,
          tooltip: {
              valueDecimals: 3
          }

          }
//          ,{
////          name: '上证指数',
//          name: '创业板指',
//
//          color: 'orange',
////          pointStart: Date.UTC(2019, 7, 1),
//          data: cyb_index_timestamp,
//          tooltip: {
//              valueDecimals: 3
//          }
//
//          }


       ];

//       console.log(completion_strategy_data);

       var json = {};
       json.chart = chart;
       json.title = title;
//       json.subtitle = subtitle;
        json.credits = credits;
       json.legend = legend;

       json.yAxis = yAxis;
       json.series = series;
       json.plotOptions = plotOptions;
       $('#container').highcharts('stockChart',json);

     });

}
}


addLoadEvent(initTable);