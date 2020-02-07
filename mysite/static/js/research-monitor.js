
var test_row = ' ';

function initTable(){
    currentProductsTable = $("#current_products_detail")

    //console.log($("#table_summary"))
    currentProductsTable.on('click-row.bs.table', function (e, row, $element) {
        $($element).siblings().removeClass('warning');
        $($element).addClass('warning');
        $('.success').css("background-color","#ffffff");
    });


    currentProductsTable.on('click-cell.bs.table', function(e, value, row, $element){

        test_row = row + '';
        $("#product_introduction_title").text( test_row +'品种介绍');

        $("#product_introduction").show();
//        $("#current_product_introduction").bootstrapTable('refresh',{url: "../static/tableData/currentProductData/Introduction/" + row + "_introduction.json"});

        $("#net_value_title").text( test_row +'现货价格走势图');
        showNV_Plot(test_row);

        });

    function showNV_Plot(test_row){

    var url_path = "../static/tableData/CommodityPriceData/" + test_row + "_tsdata.json";

    $.getJSON(url_path,function (data) {


       var dataArrays = data;
       var tsdata = dataArrays.ts_data;
       var tsdate = dataArrays.ts_date;
       var alldata = [];
       var timeXaxis = [];


       function toPercent(point){
            var str=Number(point*100).toFixed(3);
            str+="%";
            return str;
        }
       function year_return(tsdata){
           var year_rr = Math.pow((tsdata[tsdata.length-1] / tsdata[0]),(250/tsdata.length)) - 1;
           return toPercent(year_rr.toFixed(2));

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
           return toPercent((max_loss*(-1)).toFixed(2));
       }

       function getWeekReturn(tsdata){

            var price_length = tsdata.length;
            return toPercent(((tsdata[price_length-1] - tsdata[price_length-6]) / tsdata[price_length - 6 ]).toFixed(6));

       }
       function getDayReturn(tsdata){

            var price_length = tsdata.length;
            return toPercent(((tsdata[price_length-1] - tsdata[price_length-2]) / tsdata[price_length - 2 ]).toFixed(6));

       }
       function getMonthReturn(tsdata){

            var price_length = tsdata.length;
            return toPercent(((tsdata[price_length-1] - tsdata[price_length-21]) / tsdata[price_length - 21 ]).toFixed(6));

       }

       var _dayReturn = getDayReturn(tsdata);
       var str_dayReturn = "\t今日涨幅: " + _dayReturn + "\xa0\xa0";
       var _weekReturn = getWeekReturn(tsdata);
       var str_weekReturn = "\t周涨幅: " + _weekReturn + "\xa0\xa0";
       var _monthReturn = getMonthReturn(tsdata);
       var str_monthReturn = "\t月涨幅: " + _monthReturn + "\xa0\xa0";


       var title = {
          text: test_row  + str_dayReturn +  str_weekReturn + str_monthReturn
       };

       for(i=0;i<tsdate.length;i++){
            trading_date = tsdate[i];
            if(i == 0){
                timeXaxis.push('');
            }else{
                timeXaxis.push(trading_date);
            }
        }

       for(i=0;i<tsdate.length;i++){
            nv = tsdata[i];
            trading_date = tsdate[i];
            alldata.push([trading_date,nv]);

//            var someDate = new Date(Date.parse(trading_date));
//            var trading_dates =Date.UTC(someDate.getFullYear(), someDate.getMonth(), someDate.getDate());
//            alldata.push([trading_dates,nv]);

	    }


       var chart = {
          zoomType: 'x'
       };


       var subtitle = {
          text: "Drag the picture to see the details."
       };
       var xAxis = {
//          type: 'datetime',
          minRange: 3, // 10 天
          categories: timeXaxis,
          tickInterval:  1,

//          tickWidth: 100,
//		  gridLineWidth: 1,
		  labels: {
			    align: 'right',
			    autoRotation:[-8],
//				x: -40,
//				y: -30
			},
			// 时间格式化字符
			// 默认会根据当前的刻度间隔取对应的值，即当刻度间隔为一周时，取 week 值

       };
       var yAxis = {
          title: {
             text: 'Price'
          }
       };
       var legend = {
          enabled: false
       };
       var plotOptions = {
          area: {
             fillColor: {
                linearGradient: { x1: 0, y1: 0, x2: 0, y2: 1},
                stops: [
                   [0, Highcharts.getOptions().colors[0]],
                   [1, Highcharts.Color(Highcharts.getOptions().colors[0]).setOpacity(0).get('rgba')]
                ]
             },
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


       var series= [{
          type: 'area',
          name: '价格',
          pointInterval: 1,
//          pointStart: Date.UTC(2019, 7, 1),
          data: alldata
          }
       ];

       var json = {};
       json.chart = chart;
       json.title = title;
       json.subtitle = subtitle;
       json.legend = legend;
       json.xAxis = xAxis;
       json.yAxis = yAxis;
       json.series = series;
       json.plotOptions = plotOptions;
       $('#container').highcharts(json);

     });


}

}

function returnFormater(value){
    var color;
    value = value.toFixed(5);
    if(value > 0){
        color = '#f00000';
    }
    else if(value == 0){
            color = '#8a8c8d';
    }else{
        color = '#237f52';
    }

    var percent_value = value * 100;
    percent_value = percent_value.toFixed(3);

    percent_value = percent_value.toString()+"%";

    return '<div  style="font-weight: bold; color: ' + color + '">'+ percent_value + '</div>';

}

addLoadEvent(initTable);